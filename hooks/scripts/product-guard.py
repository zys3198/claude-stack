# 产物守卫：PreToolUse 阶段拦截绕过约定位置的工作树创建。
# 规则依据见 ~/.claude/CLAUDE.md 第 8 节「工作树」。
#
# 只拦一类可以客观判定的行为：git worktree add 的目标路径不在当前仓库
# .claude/worktrees/ 下，或工作树名是 hash。不做主观推测，其余一律放行。
# 判定方式是把命令拆成词、取出真正的目标路径再规范化比对，
# 不用「命令里是否出现某个子串」来判断。
# 异常写入 product-guard.log，不阻塞工具调用。

import json
import os
import re
import shlex
import subprocess
import sys
import time

CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
LOGFILE = os.path.join(CLAUDE, "product-guard.log")

WORKTREE_DIR = os.path.join(".claude", "worktrees")
HASH_WORD = re.compile(r"[0-9a-f]{16,}")
AGENT_HASH = re.compile(r"^(worktree-)?agent-[0-9a-f]{6,}")
# git worktree add 中会吃掉下一个词的选项，取目标路径时要跳过它们的值
OPTS_WITH_VALUE = {"-b", "-B", "--branch", "--reason", "--track", "--lock"}
GIT_TIMEOUT = 10


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
    except OSError:
        pass


def norm(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=False))


def repo_root(cwd):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return r.stdout.strip()


def add_target(command):
    # 返回 git worktree add 的目标路径；命令里没有这个动作时返回 None；
    # 拆不出目标时返回空串。
    try:
        tokens = shlex.split(command.replace("\\", "/"))
    except ValueError:
        return ""
    for i, token in enumerate(tokens):
        if token != "worktree" or i + 1 >= len(tokens) or tokens[i + 1] != "add":
            continue
        j = i + 2
        while j < len(tokens) and tokens[j].startswith("-"):
            j += 2 if tokens[j] in OPTS_WITH_VALUE else 1
        return tokens[j] if j < len(tokens) else ""
    return None


def check_name(name):
    name = name.strip().rstrip("/\\")
    if not name:
        return
    if AGENT_HASH.match(name) or HASH_WORD.search(name):
        deny(
            f"工作树名 {name!r} 是 hash，无法辨认任务。"
            "改成任务语义名字，kebab-case，2～4 个词，例如 eam-qr-code。"
        )


def check_worktree_add(command, cwd):
    target = add_target(command)
    if target is None:
        return
    if not target:
        deny(
            "无法从命令中判定 git worktree add 的目标路径。"
            "改写成单一形式：git worktree add .claude/worktrees/<任务名>。"
        )
        return
    root = repo_root(cwd)
    if not root:
        deny(
            "无法确定当前仓库根目录，不能判定工作树位置是否合规。"
            "请先切到目标仓库目录再执行，或改用在会话里调用 EnterWorktree。"
        )
        return
    want = os.path.join(root, WORKTREE_DIR)
    resolved = norm(os.path.join(cwd, target))
    if not resolved.startswith(norm(want) + os.sep):
        deny(
            f"工作树只能建在当前仓库的 .claude/worktrees/<任务名> 下，"
            f"不允许建到别的位置（{target} 解析为 {resolved}）。"
            "改用在会话里调用 EnterWorktree，或写成 "
            "git worktree add .claude/worktrees/<任务名>。"
        )
        return
    check_name(os.path.basename(resolved))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        sys.exit(0)
    if not isinstance(payload, dict):
        sys.exit(0)
    ti = payload.get("tool_input")
    if not isinstance(ti, dict):
        ti = {}
    tool = payload.get("tool_name") or ""
    cwd = payload.get("cwd") or os.getcwd()
    try:
        if tool == "EnterWorktree":
            check_name(ti.get("name") or "")
        else:
            check_worktree_add(ti.get("command") or "", cwd)
    except Exception as exc:
        import traceback
        log(f"check failed: {exc}\n{traceback.format_exc()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
