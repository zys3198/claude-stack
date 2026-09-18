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
#   - 异常写入 session-guard.log，绝不阻塞会话启动或结束

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
HANDOFF = CLAUDE / "session-handoff.jsonl"
LOGFILE = CLAUDE / "session-guard.log"

HANDOFF_KEEP_DAYS = 7
AGENTS_TIMEOUT = 20
GIT_TIMEOUT = 20


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
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
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return r.returncode, r.stdout or ""


def norm(path):
    return os.path.normcase(os.path.abspath(path))


def repo_root(cwd):
    rc, out = git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0 or not out.strip():
        return None
    return out.strip()


def is_linked_worktree(cwd):
    rc, out = git(["rev-parse", "--git-dir"], cwd)
    if rc != 0:
        return False
    return "worktrees" in out.replace("\\", "/")


def active_sessions():
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
        return []
    if r.returncode != 0:
        return []
    try:
        rows = json.loads(r.stdout or "[]")
    except ValueError:
        return []
    if not isinstance(rows, list):
        return []
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
        if self_id and s["session_id"] == self_id:
            continue
        c = norm(s["cwd"])
        if c == target or c.startswith(target + os.sep):
            return True
    return False


def handoff_records():
    if not HANDOFF.is_file():
        return []
    rows = []
    for line in HANDOFF.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def prune_handoff(rows):
    cutoff = time.time() - HANDOFF_KEEP_DAYS * 86400
    kept = [r for r in rows if isinstance(r.get("ts"), (int, float)) and r["ts"] >= cutoff]
    try:
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept)
        HANDOFF.write_text(text, encoding="utf-8")
    except OSError as exc:
        log(f"prune handoff failed: {exc}")


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
    root = repo_root(cwd)
    if not root:
        return
    if norm(root) == norm(CLAUDE):
        return

    sessions = active_sessions()
    parts = []

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
        if session_owns(path, sessions, self_id):
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

    prune_handoff(handoff_records())

    same_here = sum(
        1 for s in sessions
        if s["session_id"] != self_id and norm(s["cwd"]) == norm(cwd)
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
    root = repo_root(cwd)
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
    try:
        with open(HANDOFF, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        log(f"append handoff failed: {exc}")
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
