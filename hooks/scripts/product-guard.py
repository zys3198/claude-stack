# 产物守卫：PreToolUse 阶段拦截绕过约定位置或违反命名要求的工作树创建。
# 规则依据见 ~/.claude/CLAUDE.md 第 8 节「工作树」。
#
# 只拦可以客观判定的行为：git worktree add 的目标路径不在当前仓库
# .claude/worktrees/ 下，或工作树名不合规。不做主观推测，其余一律放行。
# 判定方式是把命令拆成词、取出每一处 git worktree add 的真正目标路径再规范化比对，
# 不用「命令里是否出现某个子串」来判断。
#
# 已知覆盖不到的情形：把命令再包一层解释器（bash -c "..." 、python -c "os.system(...)"）
# 之后，顶层拆词看不到 worktree add，会放行。这类写法需要刻意规避，
# 本守卫定位是防止误建，不作为安全边界。
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
# git worktree add 中会吃掉下一个词的选项。依据 git 2.54 的用法行：
# [-b | -B] <new-branch> 与 [--lock [--reason <string>]]，其余选项都不带值。
OPTS_WITH_VALUE = {"-b", "-B", "--reason"}
# 工作树名要求：kebab-case，禁用 hash、纯日期与保留名。依据 CLAUDE.md 第 8 节。
NAME_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_RESERVED = {"tmp", "test"}
NAME_RESERVED_PREFIX = ("agent-", "worktree-")
DATE_ONLY = re.compile(r"^(?:\d{8}|\d{4}-?\d{2}-?\d{2})$")
GIT_TIMEOUT = 10


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
    except OSError:
        pass


def norm(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


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


def main_root(cwd):
    # 主检出的根目录。链接工作树里 --show-toplevel 返回工作树自身，
    # 用 --git-common-dir 的上一级取主检出；取不到时退回 --show-toplevel。
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return repo_root(cwd)
    common = (r.stdout or "").strip().rstrip("/\\")
    if r.returncode == 0 and os.path.basename(common) == ".git":
        return os.path.dirname(common)
    return repo_root(cwd)


def is_control(token):
    # shell 控制符与重定向。出现在目标位置说明命令还有后续子句，
    # 不能再把它当成工作树路径（例如 git worktree add -h 2>&1 | head）。
    if token in {"|", "||", "&&", ";", "&", "|&"}:
        return True
    return bool(re.match(r"^\d*[<>]", token))


def is_git_token(token):
    # 命令名按最后一段判定，覆盖 git、git.exe 与绝对路径形式的 git。
    # 只做精确名字比对，不用子串，避免把 gitk、git-lfs 之类也算进来。
    return os.path.basename(token.replace("\\", "/")).lower() in {"git", "git.exe"}


def split_tokens(command):
    # 反斜杠写法统一成斜杠后再拆词；引号不闭合时返回 None 表示无法判定。
    try:
        return shlex.split(command.replace("\\", "/"))
    except ValueError:
        return None


def leading_cd(tokens, cwd):
    # 命令以 cd <目录> 开头时，后续 git 命令在该目录下执行。
    if not tokens or tokens[0] != "cd":
        return cwd
    candidate = None
    for token in tokens[1:]:
        if is_control(token):
            break
        candidate = token
    if not candidate:
        return cwd
    resolved = norm(os.path.join(cwd, candidate))
    return resolved if os.path.isdir(resolved) else cwd


def git_invocation(tokens, i, cwd):
    # tokens[i] 是 "git"，返回该次调用实际作用的目录与子命令起始下标。
    j = i + 1
    while j < len(tokens) and tokens[j].startswith("-"):
        if tokens[j] == "-C" and j + 1 < len(tokens):
            candidate = norm(os.path.join(cwd, tokens[j + 1]))
            if os.path.isdir(candidate):
                cwd = candidate
            j += 2
            continue
        j += 1
    return cwd, j


def worktree_adds(command, cwd):
    # 返回命令里每一处 git worktree add 的 (目标路径, 该次 git 调用目录)。
    # 没有这个动作时返回空列表；命令无法拆词时返回 None。
    tokens = split_tokens(command)
    if tokens is None:
        return None
    base = leading_cd(tokens, cwd)
    found = []
    i = 0
    while i < len(tokens):
        if not is_git_token(tokens[i]):
            i += 1
            continue
        git_dir, j = git_invocation(tokens, i, base)
        if j + 1 < len(tokens) and tokens[j] == "worktree" and tokens[j + 1] == "add":
            k = j + 2
            while k < len(tokens) and tokens[k].startswith("-") and not is_control(tokens[k]):
                k += 2 if tokens[k] in OPTS_WITH_VALUE else 1
            target = "" if k >= len(tokens) or is_control(tokens[k]) else tokens[k]
            found.append((target, git_dir))
            i = k
            continue
        i = j
    return found


def name_reason(name):
    name = name.strip().rstrip("/\\")
    if not name:
        return None
    if AGENT_HASH.match(name) or HASH_WORD.search(name) or DATE_ONLY.match(name):
        return (
            f"工作树名 {name!r} 是 hash 或纯日期，无法辨认任务。"
            "改成任务语义名字，kebab-case，例如 eam-qr-code。"
        )
    if name.lower() in NAME_RESERVED or name.startswith(NAME_RESERVED_PREFIX):
        return (
            f"工作树名 {name!r} 在禁用名单里（禁止 {', '.join(sorted(NAME_RESERVED))}、"
            f"{'、'.join(NAME_RESERVED_PREFIX)}开头）。"
            "改成任务语义名字，kebab-case，例如 eam-qr-code。"
        )
    if not NAME_OK.match(name):
        return (
            f"工作树名 {name!r} 不是 kebab-case，只能用小写字母、数字和连字符。"
            "例如 eam-qr-code。"
        )
    return None


def location_reason(target, git_dir):
    if not target:
        return (
            "无法从命令中判定 git worktree add 的目标路径。"
            "改写成单一形式：git worktree add .claude/worktrees/<任务名>。"
        )
    root = main_root(git_dir)
    if not root:
        return (
            "无法确定当前仓库根目录，不能判定工作树位置是否合规。"
            "请先切到目标仓库目录再执行，或改用在会话里调用 EnterWorktree。"
        )
    want = norm(os.path.join(root, WORKTREE_DIR))
    joined = os.path.normpath(os.path.join(git_dir, target))
    resolved = norm(joined)
    if not resolved.startswith(want + os.sep):
        return (
            "工作树只能建在当前仓库的 .claude/worktrees/<任务名> 下，"
            f"不允许建到别的位置（{target} 解析为 {resolved}）。"
            "改用在会话里调用 EnterWorktree，或写成 "
            "git worktree add .claude/worktrees/<任务名>。"
        )
    # 名字取用户写下的原样，不做 normcase，否则大写会被折成小写而绕过格式校验
    return name_reason(os.path.basename(joined))


def check_worktree_add(command, cwd):
    if not isinstance(command, str):
        # 命令不是字符串时拆不了词。记一条日志后放行，不做猜测。
        log(f"skip check: command 不是字符串（{type(command).__name__}）")
        return
    found = worktree_adds(command, cwd)
    if found is None:
        deny(
            "无法从命令中判定 git worktree add 的目标路径（引号不闭合）。"
            "改写成单一形式：git worktree add .claude/worktrees/<任务名>。"
        )
        return
    for target, git_dir in found:
        reason = location_reason(target, git_dir)
        if reason:
            deny(reason)
            return


def enter_path_reason(path, cwd):
    resolved = norm(path if os.path.isabs(path) else os.path.join(cwd, path))
    root = main_root(resolved)
    if not root:
        return (
            f"EnterWorktree 的 path（{path}）不是可用的工作树目录。"
            "改用 name 参数，在 .claude/worktrees/<任务名> 下新建一个。"
        )
    want = norm(os.path.join(root, WORKTREE_DIR))
    if not resolved.startswith(want + os.sep):
        return (
            "EnterWorktree 只能进入当前仓库 .claude/worktrees/<任务名> 下的工作树，"
            f"不允许进入别的位置（{path} 解析为 {resolved}）。"
        )
    return None


def check_enter_worktree(tool_input, cwd):
    # name 与 path 同时给出时两个都要校验，只报第一条命中的原因。
    # 只看 name 就返回的话，越界的 path 会被漏掉。
    name = tool_input.get("name")
    reason = name_reason(name) if name else None
    path = tool_input.get("path")
    if not reason and path:
        reason = enter_path_reason(path, cwd)
    if reason:
        deny(reason)


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
            check_enter_worktree(ti, cwd)
        else:
            check_worktree_add(ti.get("command") or "", cwd)
    except Exception as exc:
        import traceback
        log(f"check failed: {exc}\n{traceback.format_exc()}")
    sys.exit(0)


if __name__ == "__main__":
    main()
