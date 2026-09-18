# 产物守卫：PreToolUse 阶段拦截绕过约定位置的工作树创建。
# 规则依据见 ~/.claude/CLAUDE.md 第 8 节「工作树」。
#
# 只拦两类可以客观判定的行为：工作树的创建位置或名字不合规。
#   - git worktree add 的目标不在当前仓库 .claude/worktrees/ 下
#   - 工作树名是 hash（含 EnterWorktree 工具传入的 name）
# 不做主观推测，其余一律放行。命令先剥掉引号内内容再判断，
# 避免命令里只是提到那串字就被拦。异常写入 product-guard.log，不阻塞工具调用。

import json
import os
import re
import sys
import time

CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
LOGFILE = os.path.join(CLAUDE, "product-guard.log")

WORKTREE_ADD = re.compile(r"worktree\s+add\b")
WORKTREE_PATH = re.compile(r"\.claude[\\/]worktrees[\\/]([^\s'\"]+)")
HASH_WORD = re.compile(r"[0-9a-f]{16,}")
AGENT_HASH = re.compile(r"^(worktree-)?agent-[0-9a-f]{6,}")


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
    except OSError:
        pass


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=False))


def unquoted(command):
    return re.sub(r"'[^']*'|\"[^\"]*\"", " ", command)


def check_worktree_add(command):
    if not WORKTREE_ADD.search(unquoted(command)):
        return
    flat = command.replace("\\", "/")
    if ".claude/worktrees/" not in flat:
        deny(
            "工作树只能建在当前仓库的 .claude/worktrees/<任务名> 下，"
            "不允许建到仓库外或别的位置。"
            "改用在会话里调用 EnterWorktree，或写成 "
            "git worktree add .claude/worktrees/<任务名>。"
        )
        return
    for name in WORKTREE_PATH.findall(flat):
        check_name(name)


def check_name(name):
    name = name.strip().rstrip("/\\")
    if not name:
        return
    if AGENT_HASH.match(name) or HASH_WORD.search(name):
        deny(
            f"工作树名 {name!r} 是 hash，无法辨认任务。"
            "改成任务语义名字，kebab-case，2～4 个词，例如 eam-qr-code。"
        )


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
    try:
        if tool == "EnterWorktree":
            check_name(ti.get("name") or "")
        else:
            check_worktree_add(ti.get("command") or "")
    except Exception as exc:
        import traceback
        log(f"check failed: {exc}\n{traceback.format_exc()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
