# 会话生命周期守卫，SessionStart 与 SessionEnd 共用，跨项目通用。
# 用法：session-guard.py start   /   session-guard.py end   （事件负载从 stdin 读入）
#
# 只做两件事：会话开始时报告卫生状况，会话结束时记录收尾状态。
# 不删除任何东西——清理一律走 /dev-clean，由用户逐条确认。
#
# 设计约束：
#   - 非 git 目录静默退出，不产生任何输出
#   - 状态读取失败时如实报告，不当作干净
#   - 只报告当前仓库的事，不引用别的仓库的遗留
#   - 收尾记录文件既会被追加也会被裁剪，两条写入路径都持有同一把锁，
#     裁剪时在锁内重新读取，避免读到旧快照再整份写回而丢掉并发追加的记录
#   - 锁文件里写持有者令牌，释放时比对一致才删除：锁被判定陈旧并由别的进程
#     接管重建之后，原持有者不能再删掉接管者的锁
#   - 锁等待超时不影响会话：追加改写独占命名的溢出文件，裁剪直接跳过。
#     同一文件并发追加在 Windows 上会互相覆盖（实测丢 8% 以上），
#     独占命名让两个降级进程不会写到同一处
#   - 异常写入 session-guard.log，绝不阻塞会话启动或结束

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
HANDOFF = CLAUDE / "session-handoff.jsonl"
HANDOFF_DIR = CLAUDE / "session-handoff.d"
LOCK = CLAUDE / "session-handoff.lock"
LOGFILE = CLAUDE / "session-guard.log"

HANDOFF_KEEP_DAYS = 7
LOCK_WAIT_SECONDS = 2.0
LOCK_STALE_SECONDS = 30.0
AGENTS_TIMEOUT = 20
GIT_TIMEOUT = 20


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
    except OSError:
        pass


def lock_acquire():
    # 拿到锁时返回持有者令牌，没拿到返回 None。
    # 令牌写进锁文件，lock_release 据此判断锁还是不是自己的。
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    token = f"{os.getpid()}-{os.urandom(6).hex()}"
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(LOCK)
                # age 为负数说明锁文件的修改时间在将来，这种锁不会被正常持有者
                # 释放，按陈旧处理，否则裁剪与追加会永久卡住
                if age > LOCK_STALE_SECONDS or age < -LOCK_STALE_SECONDS:
                    os.remove(LOCK)
                    continue
            except OSError:
                pass
        except OSError as exc:
            log(f"lock acquire failed: {exc}")
            return None
        else:
            written = False
            try:
                os.write(fd, token.encode("ascii"))
                written = True
            except OSError as exc:
                log(f"lock write failed: {exc}")
            finally:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if not written:
                # 锁文件已经建出来了，不删掉会留下一个没人释放的锁
                try:
                    os.remove(LOCK)
                except OSError:
                    pass
                return None
            return token
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.02)


def lock_release(token):
    # 只在自己的令牌还在锁文件里时才删除。锁超过陈旧阈值后会被别的进程接管
    # 并重建，那时文件里是对方的令牌，删掉会让两个进程同时进入临界区。
    if not token:
        return
    try:
        if LOCK.read_text(encoding="ascii", errors="replace").strip() != token:
            return
        os.remove(LOCK)
    except OSError:
        pass


def git(args, cwd):
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"git {' '.join(args)} 执行失败：{exc}")
        return 1, ""
    return r.returncode, r.stdout or ""


def norm(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def repo_root(cwd):
    rc, out = git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0 or not out.strip():
        return None
    return out.strip()


def main_root(cwd):
    # 主检出的根目录。链接工作树里 --show-toplevel 返回工作树自身，
    # 用 --git-common-dir 的上一级取主检出，收尾记录的 repo 字段据此对齐。
    rc, out = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    common = out.strip().rstrip("/\\")
    if rc == 0 and os.path.basename(common) == ".git":
        return os.path.dirname(common)
    return repo_root(cwd)


def is_linked_worktree(cwd):
    rc, out = git(["rev-parse", "--git-dir"], cwd)
    if rc != 0:
        return False
    return "worktrees" in out.replace("\\", "/")


def active_sessions():
    # 枚举失败时返回 None，由调用方显式报告降级。
    # 返回空列表会被当成「没有会话在跑」，把正在被别的会话使用的工作树
    # 报成无会话占用。
    try:
        r = subprocess.run(
            ["claude", "agents", "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=AGENTS_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    try:
        rows = json.loads(r.stdout or "[]")
    except ValueError:
        return None
    if not isinstance(rows, list):
        return None
    out = []
    for d in rows:
        if isinstance(d, dict) and d.get("cwd"):
            out.append({
                "pid": d.get("pid"),
                "session_id": d.get("sessionId"),
                "cwd": d["cwd"],
                "status": d.get("status", ""),
                "kind": d.get("kind", ""),
                "started_at": d.get("startedAt", 0),
            })
    return out


def list_worktrees(repo):
    rc, out = git(["worktree", "list", "--porcelain"], repo)
    if rc != 0:
        return []
    trees = []
    cur = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                trees.append(cur)
            cur = {"path": line[len("worktree "):], "branch": None, "detached": False}
        elif cur is None:
            continue
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].replace("refs/heads/", "")
        elif line.startswith("detached"):
            cur["detached"] = True
    if cur:
        trees.append(cur)
    return trees


def change_count(path):
    rc, out = git(["status", "--porcelain"], path)
    if rc != 0:
        return None
    return sum(1 for line in out.splitlines() if line.strip())


def session_owns(path, sessions, self_id):
    target = norm(path)
    for s in sessions:
        if self_id and s.get("session_id") == self_id:
            continue
        cwd = s.get("cwd")
        if not cwd:
            continue
        c = norm(cwd)
        if c == target or c.startswith(target + os.sep):
            return True
    return False


def read_jsonl(path):
    rows = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def overflow_files():
    if not HANDOFF_DIR.is_dir():
        return []
    return sorted(p for p in HANDOFF_DIR.iterdir() if p.is_file())


def handoff_records():
    # 主文件与溢出文件都要读。降级追加的记录先落在溢出文件里，
    # 等下一次裁剪时并回主文件。
    rows = read_jsonl(HANDOFF) if HANDOFF.is_file() else []
    for path in overflow_files():
        rows.extend(read_jsonl(path))
    rows.sort(key=lambda r: r.get("ts") if isinstance(r.get("ts"), (int, float)) else 0)
    return rows


def append_record(record):
    # 先走锁；拿不到锁时写独占命名的溢出文件。
    # 同一文件并发追加在 Windows 上会互相覆盖，共用文件名的写法不行，
    # 独占命名让两个降级进程各写各的。
    token = lock_acquire()
    if token:
        try:
            with open(HANDOFF, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            return True
        except OSError as exc:
            log(f"append handoff failed: {exc}")
            return False
        finally:
            lock_release(token)
    log("append handoff to overflow: 锁等待超时")
    try:
        HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
        name = f"{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}-{os.urandom(4).hex()}.jsonl"
        (HANDOFF_DIR / name).write_text(
            json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
        return True
    except OSError as exc:
        log(f"append handoff overflow failed: {exc}")
        return False


def prune_handoff():
    # 与 handle_end 的追加共用一把锁，并在锁内重新读取，
    # 避免用读取过的旧快照整份写回而丢掉这段时间里追加的记录。
    # 溢出文件里的记录在这一步并回主文件。
    if not HANDOFF.is_file() and not HANDOFF_DIR.is_dir():
        return
    token = lock_acquire()
    if not token:
        log("prune handoff skipped: 锁等待超时")
        return
    try:
        rows = handoff_records()
        cutoff = time.time() - HANDOFF_KEEP_DAYS * 86400
        kept = []
        dropped = 0
        for r in rows:
            fresh = isinstance(r.get("ts"), (int, float)) and r["ts"] >= cutoff
            if fresh:
                kept.append(r)
                continue
            dropped += 1
            if isinstance(r.get("dirty"), int) and r["dirty"] > 0:
                log(f"prune handoff 丢弃过期记录：{r.get('cwd')} dirty={r['dirty']}")
        overflow = overflow_files()
        if not dropped and not overflow:
            return
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept)
        HANDOFF.write_text(text, encoding="utf-8")
        for path in overflow:
            try:
                path.unlink()
            except OSError:
                pass
    except OSError as exc:
        log(f"prune handoff failed: {exc}")
    finally:
        lock_release(token)


def emit(event, context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": context,
        },
    }, ensure_ascii=False))


def handle_start(payload):
    cwd = payload.get("cwd") or os.getcwd()
    self_id = payload.get("session_id")
    root = main_root(cwd)
    if not root:
        return
    if norm(root) == norm(CLAUDE):
        return

    sessions = active_sessions()
    degraded = sessions is None
    if degraded:
        sessions = []
    parts = []
    if degraded:
        parts.append("活跃会话枚举失败，工作树占用判定不可靠")

    dirty = change_count(root)
    if dirty is None:
        parts.append("主检出状态读取失败")
    elif dirty:
        parts.append(f"主检出 {dirty} 处未提交改动")

    loose = 0
    unreadable = 0
    detached = 0
    for tree in list_worktrees(root):
        path = tree["path"]
        if norm(path) == norm(root):
            continue
        if tree["detached"]:
            detached += 1
        # 枚举失败时无从判断工作树有没有会话在用，跳过散落统计，
        # 否则会把正在被别的会话使用的工作树报成无会话占用
        if degraded or session_owns(path, sessions, self_id):
            continue
        n = change_count(path)
        if n is None:
            unreadable += 1
        elif n:
            loose += 1

    if loose:
        parts.append(f"{loose} 个无会话占用的工作树留有未提交改动")
    if unreadable:
        parts.append(f"{unreadable} 个工作树状态读取失败")
    if detached:
        parts.append(f"{detached} 个工作树处于 detached HEAD")

    pending = [
        r for r in handoff_records()
        if isinstance(r.get("dirty"), int) and r["dirty"] > 0
        and r.get("repo") and norm(r["repo"]) == norm(root)
    ]
    if pending:
        latest = pending[-1]
        where = os.path.basename(str(latest.get("cwd", "")).rstrip("/\\")) or "上次会话"
        parts.append(f"上次会话在 {where} 留有 {latest['dirty']} 处改动")

    prune_handoff()

    same_here = sum(
        1 for s in sessions
        if s.get("session_id") != self_id and norm(s.get("cwd") or "") == norm(cwd)
    )
    hint = ""
    if same_here >= 1 and not is_linked_worktree(cwd):
        hint = (
            f" 当前目录另有 {same_here} 个会话在用，"
            "改动代码前先调用 EnterWorktree 迁移到独立工作树，避免互相覆盖。"
        )

    if not parts and not hint:
        return
    body = "；".join(parts)
    text = f"会话卫生：{body}。" if body else ""
    text += hint
    if not text:
        return
    emit("SessionStart", text)


def handle_end(payload):
    cwd = payload.get("cwd") or os.getcwd()
    root = main_root(cwd)
    if not root:
        return
    if norm(root) == norm(CLAUDE):
        return
    rc, out = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    branch = out.strip() if rc == 0 else ""
    dirty = change_count(cwd)
    record = {
        "ts": time.time(),
        "session_id": payload.get("session_id"),
        "reason": payload.get("reason", ""),
        "cwd": cwd,
        "repo": root,
        "branch": branch,
        "worktree": is_linked_worktree(cwd),
        "dirty": dirty,
    }
    if not append_record(record):
        return

    where = os.path.basename(cwd.rstrip("/\\")) if record["worktree"] else "主检出"
    if dirty:
        msg = (
            f"会话结束：{where} 留有 {dirty} 处未提交改动"
            f"（分支 {branch or 'detached'}）。改动会保留，下次会话开始时提示。"
        )
    elif record["worktree"]:
        msg = f"会话结束：工作树 {where} 干净，可用 /dev-clean 清理。"
    else:
        return
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    try:
        if event == "start":
            handle_start(payload)
        elif event == "end":
            handle_end(payload)
    except Exception as exc:
        import traceback
        log(f"{event} failed: {exc}\n{traceback.format_exc()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
