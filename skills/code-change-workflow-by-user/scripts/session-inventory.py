# 本机会话清点：一眼看清现在有哪些活还在飞、本机在跑什么、哪些东西还没提交。
# 依赖 psutil（进程与端口枚举，跨平台）。
import argparse
import json
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

import psutil

sys.stdout.reconfigure(encoding="utf-8")

CONFIG_PATH = Path.home() / ".claude" / "session-hygiene.json"


def git(repo, *args):
    # 只读查询，失败时返回空，由调用方按空值处理。
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def lines(text):
    return [line for line in text.splitlines() if line.strip()]


def display_width(text):
    # 中文和全角符号占两格，按字符数补空格会错位。
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def pad(text, target):
    return text + " " * max(1, target - display_width(text))


def repo_root(start):
    root = git(start, "rev-parse", "--show-toplevel")
    return Path(root) if root else None


def load_config():
    # 端口和容器是本机资源，配置跟着机器走，不放进任何仓库。
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def section(title):
    print()
    print(f"── {title} " + "─" * max(0, 60 - len(title)))


def show_repo(root):
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    dirty = lines(git(root, "status", "--short"))
    section("主检出")
    print(f"  {root}")
    print(f"  分支 {branch}    未提交改动 {len(dirty)} 处")


def parse_worktrees(root):
    entries = []
    current = {}
    for line in lines(git(root, "worktree", "list", "--porcelain")):
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": Path(line[len("worktree "):])}
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):].replace("refs/heads/", "")
        elif line == "detached":
            current["branch"] = "(detached)"
    if current:
        entries.append(current)
    return entries


def show_worktrees(root):
    entries = parse_worktrees(root)
    section(f"工作树 {len(entries)} 个")
    for entry in entries:
        path = entry["path"]
        branch = entry.get("branch", "?")
        if path == root:
            print(f"  {pad('主检出', 20)}{pad(branch, 42)}{path}")
            continue
        dirty = len(lines(git(path, "status", "--short")))
        unpushed = len(lines(git(path, "log", "--oneline", "HEAD", "--not", "--remotes")))
        flag = "干净" if dirty == 0 and unpushed == 0 else f"未提交 {dirty} / 未推送 {unpushed}"
        print(f"  {pad(flag, 20)}{pad(branch, 42)}{path}")


def listening_ports():
    table = {}
    for conn in psutil.net_connections(kind="tcp"):
        if conn.status != psutil.CONN_LISTEN or conn.laddr is None:
            continue
        table.setdefault(conn.laddr.port, conn.pid)
    return table


def process_label(pid):
    if pid is None:
        return "属主未知"
    try:
        process = psutil.Process(pid)
        cwd = process.cwd()
    except psutil.Error:
        return f"pid {pid}"
    return f"pid {pid}  {process.name()}  cwd={cwd}"


def show_ports(config):
    ports = config.get("ports", [])
    if not ports:
        return
    listening = listening_ports()
    section("端口")
    for item in ports:
        port = item["port"]
        label = item.get("label", "")
        owner = listening.get(port)
        state = "空闲" if owner is None else "占用"
        print(f"  {port:<6} {state:<4} {label}")
        if owner is not None:
            print(f"         {process_label(owner)}")


def show_exclusive(config):
    items = config.get("exclusive", [])
    if not items:
        return
    section("独占操作")
    names = docker_container_names()
    if names is None:
        print("  docker 不可用，无法确认容器状态")
        return
    for item in items:
        name = item["container"]
        label = item.get("label", "")
        state = "运行中" if name in names else "未运行"
        print(f"  {name:<24} {state:<6} {label}")


def docker_container_names():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return set(lines(result.stdout)) if result.returncode == 0 else None


def show_loose(root):
    stats = {}
    for line in lines(git(root, "count-objects", "-v")):
        key, _, value = line.partition(":")
        stats[key.strip()] = value.strip()
    pack_dir = Path(git(root, "rev-parse", "--git-common-dir"))
    if not pack_dir.is_absolute():
        pack_dir = root / pack_dir
    pack_dir = pack_dir / "objects" / "pack"
    stamps = [path.stat().st_mtime for path in pack_dir.glob("*")] if pack_dir.exists() else []
    last_pack = time.strftime("%Y-%m-%d %H:%M", time.localtime(max(stamps))) if stamps else "从未打包"

    section("找回窗口")
    print(f"  未打包对象 {stats.get('count', '?')} 个    最近打包 {last_pack}")
    print(f"  git add 过的内容已进对象库，工作区文件被删也能捞回；没 add 的改动只存在于文件里，删了就没了")


def show_stashes_and_branches(root):
    stashes = lines(git(root, "stash", "list"))
    section("其他")
    print(f"  stash {len(stashes)} 条")
    for line in stashes:
        print(f"         {line}")
    loose = []
    for ref in lines(git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")):
        if not git(root, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{ref}"):
            count = git(root, "rev-list", "--count", ref, "--not", "--remotes")
            loose.append(f"{ref}（未推送提交 {count or 0}）")
    print(f"  无远端分支 {len(loose)} 条")
    for item in loose:
        print(f"         {item}")


def main():
    parser = argparse.ArgumentParser(description="清点本机在跑的资源和未收尾的工作")
    parser.add_argument("path", nargs="?", default=".", help="仓库内任意路径")
    args = parser.parse_args()

    root = repo_root(args.path)
    if root is None:
        print(f"{args.path} 不在 Git 仓库里")
        return 1

    config = load_config()
    show_repo(root)
    show_worktrees(root)
    show_ports(config)
    show_exclusive(config)
    show_stashes_and_branches(root)
    show_loose(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
