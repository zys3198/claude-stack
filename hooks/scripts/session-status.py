# 会话与产物总览，供 /dev-status 使用，跨项目通用。
# 用法：session-status.py [仓库路径]      默认取当前目录
#
# 只读。信息全部来自 git、claude agents --json 与会话卫生表，不做任何修改。

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
HYGIENE = CLAUDE / "session-hygiene.json"
HANDOFF = CLAUDE / "session-handoff.jsonl"
HANDOFF_DIR = CLAUDE / "session-handoff.d"
WORKTREE_MARK = os.path.join(".claude", "worktrees")
AGENTS_TIMEOUT = 20
GIT_TIMEOUT = 20
NOTE_WIDTH = 26


def git(args, cwd):
    try:
        r = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return r.returncode, r.stdout or ""


def norm(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def main_root(cwd):
    # 主检出的根目录。从链接工作树里调用时 --show-toplevel 返回工作树自身，
    # 统一取主检出根，工作树分类与四类分组才有同一个参照物。
    rc, out = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    common = out.strip().rstrip("/\\")
    if rc == 0 and os.path.basename(common) == ".git":
        return os.path.dirname(common)
    rc, out = git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0 or not out.strip():
        return None
    return out.strip()


def worktree_prefix(repo):
    return norm(os.path.join(repo, WORKTREE_MARK)) + os.sep


def short(path, root):
    p = norm(path)
    r = norm(root)
    if p == r:
        return "主检出"
    if p.startswith(r + os.sep):
        return os.path.relpath(path, root)
    return path


def active_sessions():
    # 枚举失败时返回 None，由调用方显式标注降级，不伪装成「没有会话」。
    try:
        r = subprocess.run(
            ["claude", "agents", "--json"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=AGENTS_TIMEOUT,
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
    rows = [d for d in rows if isinstance(d, dict) and d.get("cwd")]
    rows.sort(key=lambda d: d.get("startedAt", 0))
    return rows


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


def ignored_count(path):
    # 被 .gitignore 覆盖的内容不计入 git status --porcelain，
    # 但会随工作树目录一起被删除，所以单列出来给用户看。
    rc, out = git(["status", "--porcelain", "--ignored"], path)
    if rc != 0:
        return None
    return sum(1 for line in out.splitlines() if line.startswith("!!"))


def stash_rows(repo):
    rc, out = git(["stash", "list", "--format=%gd|%ct|%gs"], repo)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) < 3 or not parts[1].isdigit():
            continue
        rows.append({"ref": parts[0], "ts": int(parts[1]), "subject": parts[2]})
    return rows


def containers():
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    rows = []
    for line in (r.stdout or "").splitlines():
        parts = line.split("|", 1)
        if len(parts) == 2:
            rows.append((parts[0], parts[1]))
    return sorted(rows)


def port_owners(ports):
    # Windows 专用：netstat -ano -p TCP。其他平台返回空，端口段显示为无占用者。
    try:
        r = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=25,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    if r.returncode != 0:
        return {}
    wanted = {str(p) for p in ports}
    found = {}
    for line in (r.stdout or "").splitlines():
        cols = line.split()
        if len(cols) < 5 or cols[0].upper() != "TCP":
            continue
        local = cols[1]
        if ":" not in local:
            continue
        port = local.rsplit(":", 1)[1]
        if port in wanted and cols[3].upper() == "LISTENING":
            found.setdefault(int(port), cols[4])
    return found


def orphan_dirs(repo):
    base = Path(repo) / ".claude" / "worktrees"
    if not base.is_dir():
        return []
    known = {norm(t["path"]) for t in list_worktrees(repo)}
    rc, out = git(["branch", "--list", "--format=%(refname:short)"], repo)
    branches = set(out.split()) if rc == 0 else set()
    rows = []
    for entry in sorted(base.iterdir()):
        # junction 与符号链接都不是工作树副本，跟着进去会看到别人的内容
        if os.path.islink(entry) or os.path.isjunction(entry) or not entry.is_dir():
            continue
        if norm(str(entry)) in known:
            continue
        same = [b for b in (entry.name, f"worktree-{entry.name}") if b in branches]
        rows.append({"name": entry.name, "branches": same})
    return rows


def root_scatter(repo):
    rc, out = git(["status", "--porcelain"], repo)
    if rc != 0:
        return None
    rows = []
    for line in out.splitlines():
        if len(line) < 4 or " -> " in line:
            continue
        path = line[3:].strip().strip('"')
        if "/" in path or "\\" in path:
            continue
        rows.append(f"{line[:2]} {path}")
    return rows


def handoff_rows():
    # 主文件与溢出文件一起读。收尾记录拿不到锁时会改写独占命名的溢出文件，
    # 那些记录要等下一次裁剪才并回主文件。
    paths = [HANDOFF] if HANDOFF.is_file() else []
    if HANDOFF_DIR.is_dir():
        paths.extend(sorted(p for p in HANDOFF_DIR.iterdir() if p.is_file()))
    rows = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    rows.sort(key=lambda r: r.get("ts") if isinstance(r.get("ts"), (int, float)) else 0)
    return rows


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    target = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else os.getcwd()
    repo = main_root(target)
    if not repo:
        print(f"不是 git 仓库：{target}")
        return
    rc, out = git(["rev-parse", "--abbrev-ref", "HEAD"], repo)
    branch = out.strip() if rc == 0 else "?"
    stamp = time.strftime("%Y-%m-%d %H:%M")
    print(f"仓库 {repo}")
    print(f"分支 {branch}    检查时间 {stamp}")

    sessions = active_sessions()
    degraded = sessions is None
    if degraded:
        sessions = []
    print()
    if degraded:
        print("活跃会话 枚举失败（claude agents --json 不可用）")
        print("  工作树占用判定不可靠，本节与「可清理」分组仅供参考，不要据此删除")
    else:
        print(f"活跃会话 {len(sessions)} 个")
        for s in sessions:
            ts = time.strftime("%m-%d %H:%M", time.localtime(s.get("startedAt", 0) / 1000))
            where = short(s["cwd"], repo) if norm(s["cwd"]).startswith(norm(repo)) else s["cwd"]
            print(f"  pid {s.get('pid'):<7} {s.get('kind', ''):<11} {s.get('status', ''):<7} "
                  f"{ts}  {where}")

    prefix = worktree_prefix(repo)
    trees = list_worktrees(repo)
    others = [t for t in trees if norm(t["path"]) != norm(repo)]
    print()
    print(f"工作树 {len(others)} 个")
    buckets = {"在用": [], "有改动": [], "可清理": [], "游离": []}
    for t in others:
        path = t["path"]
        holder = None
        for s in sessions:
            c = norm(s["cwd"])
            if c == norm(path) or c.startswith(norm(path) + os.sep):
                holder = s
                break
        n = change_count(path)
        label = os.path.basename(path.rstrip("/\\"))
        br = t["branch"] or ("(detached)" if t["detached"] else "?")
        note = f"{n} 处改动" if isinstance(n, int) and n else "干净"
        inside = norm(path).startswith(prefix)
        if holder:
            buckets["在用"].append(f"  pid {holder.get('pid'):<7} {label:<38} {note:<{NOTE_WIDTH}} [{br}]")
        elif not isinstance(n, int):
            buckets["游离"].append(f"  {'':<11} {label:<38} 无法读取{'':<{NOTE_WIDTH - 8}} [{br}]")
        elif n:
            buckets["有改动"].append(f"  {'':<11} {label:<38} {note:<{NOTE_WIDTH}} [{br}]")
        elif inside:
            ig = ignored_count(path)
            if ig:
                note = f"干净，另有 {ig} 项被忽略内容"
            buckets["可清理"].append(f"  {'':<11} {label:<38} {note:<{NOTE_WIDTH}} [{br}]")
        else:
            buckets["游离"].append(f"  {'':<11} {label:<38} {note:<{NOTE_WIDTH}} [{br}]")
    for name in ("在用", "有改动", "可清理", "游离"):
        rows = buckets[name]
        if not rows:
            continue
        print(f"  [{name}] {len(rows)}")
        for r in rows:
            print(r)
    if buckets["可清理"]:
        print("  可清理只表示 git 未登记改动；标出被忽略内容的项，删除会一并删掉那些文件")

    orphans = orphan_dirs(repo)
    if orphans:
        print(f"  [孤儿目录] {len(orphans)}   git 已不再注册，改动不在任何分支上")
        for o in orphans[:10]:
            keep = ("分支 " + ", ".join(o["branches"])) if o["branches"] else "无同名分支，内容只在此目录"
            print(f"  {'':<11} {o['name']:<34} {keep}")
        if len(orphans) > 10:
            print(f"  ...另有 {len(orphans) - 10} 个")

    stash = stash_rows(repo)
    if stash:
        oldest = int((time.time() - min(s["ts"] for s in stash)) / 86400)
        print()
        print(f"stash {len(stash)} 条，最老 {oldest} 天")
        for s in stash[:5]:
            ts = time.strftime("%m-%d %H:%M", time.localtime(s["ts"]))
            print(f"  {s['ref']:<11} {ts}  {s['subject'][:70]}")
        if len(stash) > 5:
            print(f"  ...另有 {len(stash) - 5} 条")

    dirty = change_count(repo)
    print()
    print(f"主检出未提交改动 {dirty if dirty is not None else '?'} 处")

    scatter = root_scatter(repo)
    if scatter is None:
        print("仓库根状态读取失败")
    elif scatter:
        print(f"仓库根散落 {len(scatter)} 项（规则：仓库根不新建任何文件或目录）")
        for row in scatter[:10]:
            print(f"  {row}")
        if len(scatter) > 10:
            print(f"  ...另有 {len(scatter) - 10} 项")

    recent = [
        r for r in handoff_rows()
        if r.get("dirty") and r.get("repo") and r.get("cwd")
        and norm(r["repo"]) == norm(repo)
    ]
    if recent:
        # 时间戳只认数值。收尾记录可能被手工编辑，缺字段或写错类型时
        # 计数照常、明细跳过，避免整个状态汇总崩掉
        dated = [r for r in recent if isinstance(r.get("ts"), (int, float))]
        print(f"上次会话留下的未提交改动 {len(recent)} 条")
        for r in dated[-3:]:
            ts = time.strftime("%m-%d %H:%M", time.localtime(r["ts"]))
            print(f"  {ts}  {os.path.basename(r['cwd'].rstrip('/\\'))}  {r['dirty']} 处")

    hygiene = {}
    if HYGIENE.is_file():
        try:
            hygiene = json.loads(HYGIENE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            hygiene = {}
    ports = [p["port"] for p in hygiene.get("ports", []) if isinstance(p.get("port"), int)]
    owners = port_owners(ports) if ports else {}
    if hygiene.get("ports"):
        print()
        print("登记端口")
        for p in hygiene["ports"]:
            port = p.get("port")
            who = owners.get(port)
            state = f"占用 pid {who}" if who else "空闲"
            print(f"  {port:<6} {state:<16} {p.get('label', '')}")

    rowser = containers()
    if rowser:
        print()
        print(f"容器 {len(rowser)} 个")
        for name, status in rowser:
            print(f"  {name:<28} {status}")


if __name__ == "__main__":
    main()
