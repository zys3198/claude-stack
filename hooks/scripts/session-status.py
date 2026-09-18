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
WORKTREE_MARK = os.path.join(".claude", "worktrees")
AGENTS_TIMEOUT = 20
GIT_TIMEOUT = 20


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
    return os.path.normcase(os.path.abspath(path))


def short(path, root):
    p = os.path.normcase(os.path.abspath(path))
    r = os.path.normcase(os.path.abspath(root))
    if p == r:
        return "主检出"
    if p.startswith(r + os.sep):
        return os.path.relpath(path, root)
    return path


def active_sessions():
    try:
        r = subprocess.run(
            ["claude", "agents", "--json"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=AGENTS_TIMEOUT,
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
        if len(cols) < 4 or cols[0].upper() != "TCP":
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
        if not entry.is_dir() or norm(str(entry)) in known:
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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    target = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else os.getcwd()
    rc, out = git(["rev-parse", "--show-toplevel"], target)
    if rc != 0 or not out.strip():
        print(f"不是 git 仓库：{target}")
        return
    repo = out.strip()
    rc, out = git(["rev-parse", "--abbrev-ref", "HEAD"], repo)
    branch = out.strip() if rc == 0 else "?"
    stamp = time.strftime("%Y-%m-%d %H:%M")
    print(f"仓库 {repo}")
    print(f"分支 {branch}    检查时间 {stamp}")

    sessions = active_sessions()
    print()
    print(f"活跃会话 {len(sessions)} 个")
    for s in sessions:
        ts = time.strftime("%m-%d %H:%M", time.localtime(s.get("startedAt", 0) / 1000))
        where = short(s["cwd"], repo) if norm(s["cwd"]).startswith(norm(repo)) else s["cwd"]
        print(f"  pid {s.get('pid'):<7} {s.get('kind', ''):<11} {s.get('status', ''):<7} "
              f"{ts}  {where}")

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
        inside = WORKTREE_MARK.replace("/", os.sep) in norm(path)
        if holder:
            buckets["在用"].append(f"  pid {holder.get('pid'):<7} {label:<38} {note:<10} [{br}]")
        elif not isinstance(n, int):
            buckets["游离"].append(f"  {'':<11} {label:<38} 无法读取   [{br}]")
        elif n:
            buckets["有改动"].append(f"  {'':<11} {label:<38} {note:<10} [{br}]")
        elif inside:
            buckets["可清理"].append(f"  {'':<11} {label:<38} {note:<10} [{br}]")
        else:
            buckets["游离"].append(f"  {'':<11} {label:<38} {note:<10} [{br}]")
    for name in ("在用", "有改动", "可清理", "游离"):
        rows = buckets[name]
        if not rows:
            continue
        print(f"  [{name}] {len(rows)}")
        for r in rows:
            print(r)

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

    if HANDOFF.is_file():
        recent = []
        for line in HANDOFF.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("dirty") and r.get("repo") and norm(r["repo"]) == norm(repo):
                recent.append(r)
        if recent:
            print(f"上次会话留下的未提交改动 {len(recent)} 条")
            for r in recent[-3:]:
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
