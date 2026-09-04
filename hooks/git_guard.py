import sys, json, os, re, shlex, hashlib, subprocess

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

LOG = os.environ.get("CLAUDE_GIT_GUARD_LOG", "C:/Users/zys31/.claude/hooks/debug.log")
SELF_TEST = "--self-test" in sys.argv
_raw = ""
try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception as e:
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            fingerprint = hashlib.sha256(_raw.encode("utf-8")).hexdigest()[:16]
            f.write(
                f"--- ERROR parse: {type(e).__name__} "
                f"raw_sha256={fingerprint} raw_len={len(_raw)}\n"
            )
    except Exception:
        pass
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
if not ti.get("command"):
    if SELF_TEST:
        ti = {"command": "git status --self-test"}
    else:
        sys.exit(0)

cmd = ti.get("command", "")
try:
    with open(LOG, "a", encoding="utf-8") as _f:
        fingerprint = hashlib.sha256(cmd.encode("utf-8")).hexdigest()[:16]
        _f.write(
            f"--- heartbeat | tool={data.get('tool_name')} "
            f"cmd_sha256={fingerprint} cmd_len={len(cmd)}\n"
        )
except Exception:
    pass

# Claude Code PreToolUse 契约:permissionDecision=deny 拦下,permissionDecisionReason 展示给模型。
# 无命中=静默 allow(stdout 空 + exit 0)。
def deny(msg):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        }
    }, ensure_ascii=False))
    sys.exit(0)

# --- explicit user confirmation gate for `git commit` ---
# PreToolUse gives transcript_path -> session JSONL. If the latest genuine
# user prompt carries an affirmative token, treat §1.3's confirm requirement
# as satisfied and let the assistant's `git commit` through (no `!` needed).
_CONFIRM_RE = re.compile(
    r'(确认|批准|授权|同意|允许|可以|confirm|go\s+ahead|proceed)',
    re.IGNORECASE,
)
_OPERATION_RE = {
    "commit": re.compile(r'(?:提交|\bcommit\b)', re.IGNORECASE),
    "push": re.compile(r'(?:推送|推上去|推一下|\bpush\b)', re.IGNORECASE),
    "branch": re.compile(
        r'\bgit\s+(?:branch|checkout\s+-[bB]|switch\s+(?:-[cC]|--(?:create|force-create)))\b'
        r'|(?:新建|创建|建立|切换(?:到)?|create|new|switch(?:\s+to)?|checkout\s+-b|switch\s+(?:-c|--create|--force-create))'
        r'[^。！？；，,;:\n]{0,12}(?:分支|\bbranch\b)'
        r'|(?:分支|\bbranch\b)[^。！？；，,;:\n]{0,12}(?:新建|创建|建立|切换|create|new|switch)',
        re.IGNORECASE,
    ),
}
_NEGATIVE_OPERATION_RE = {
    "commit": re.compile(
        r'(?:不|不要|无需|禁止|拒绝|别|勿|等一下|先别|先不)[^。！？；，,;:\n]{0,8}(?:提交|\bcommit\b)'
        r'|\b(?:do\s+not|don\'t|never|not|no|avoid)\b[^\n,.;:!?]{0,20}\bcommit\b',
        re.IGNORECASE,
    ),
    "push": re.compile(
        r'(?:不|不要|无需|禁止|拒绝|别|勿)[^。！？；，,;:\n]{0,8}(?:推送|\bpush\b)'
        r'|\b(?:do\s+not|don\'t|never|not|no|avoid)\b[^\n,.;:!?]{0,20}\bpush\b',
        re.IGNORECASE,
    ),
    "branch": re.compile(
        r'(?:不|不要|无需|禁止|拒绝|别|勿)[^。！？；，,;:\n]{0,8}(?:分支|\bbranch\b)'
        r'|\b(?:do\s+not|don\'t|never|not|no|avoid)\b[^\n,.;:!?]{0,20}\bbranch\b',
        re.IGNORECASE,
    ),
}
_GUARDED_COMMAND_RE = {
    "commit": re.compile(r'\b(?:git\s+commit|git-commit(?:\.exe)?)\b', re.IGNORECASE),
    "push": re.compile(r'\b(?:git\s+push|git-push(?:\.exe)?)\b', re.IGNORECASE),
    "branch": re.compile(r'\b(?:git\s+(?:checkout\s+-[bB]|switch\s+(?:-[cC]|--(?:create|force-create)))|git-(?:checkout|switch)(?:\.exe)?\s+(?:-[bB]|-[cC]|--(?:create|force-create)))\b', re.IGNORECASE),
}

_QUESTION_RE = re.compile(
    r'(?:？|\?|吗|是否|怎么|为什么|能不能|可否)',
    re.IGNORECASE,
)
_QUERY_OPERATION_RE = re.compile(
    r'(?:看看|检查|查一下|告诉我|怎么操作)[^。！？；，,;:\n]{0,12}'
    r'(?:提交|\bcommit\b|推送|推上去|推一下|\bpush\b|新建|创建|建立|切换|分支|\bbranch\b)',
    re.IGNORECASE,
)
_CONDITIONAL_OPERATION_RE = re.compile(
    r'(?:未经|未(?:经)?|尚未|无需|不需要|不用|没有|没)[^。！？；，,;:\n]{0,12}'
    r'(?:确认|批准|授权|同意)[^。！？；，,;:\n]{0,8}'
    r'(?:就|便|再)?[^。！？；，,;:\n]{0,8}'
    r'(?:提交|\bcommit\b|推送|\bpush\b|新建|创建|建立|分支|\bbranch\b)'
    r'|(?:确认|批准|授权|同意)[^。！？；，,;:\n]{0,8}(?:后|之后|以后)[^。！？；，,;:\n]{0,8}'
    r'(?:提交|\bcommit\b|推送|\bpush\b|新建|创建|建立|分支|\bbranch\b)'
    r'|(?:only|just)\s+(?:commit|push|create|switch)\b[^\n,.;:!?]{0,30}'
    r'\b(?:after|if|when|once|until)\b[^\n,.;:!?]{0,20}'
    r'\b(?:confirm|approval|authorize|permission)\b'
    r'|\b(?:commit|push|create|switch)\b[^\n,.;:!?]{0,30}'
    r'\b(?:after|if|when|once|until)\b[^\n,.;:!?]{0,20}'
    r'\b(?:confirm|approval|authorize|permission)\b'
    r'|\b(?:commit|push|create|switch)\b[^\n,.;:!?]{0,20}'
    r'\bwithout\b[^\n,.;:!?]{0,20}'
    r'\b(?:confirm|confirmation|approval|authorize|authorization|permission)\b'
    r'|\b(?:without|unless)\b[^\n,.;:!?]{0,20}'
    r'\b(?:confirm|confirmation|approval|authorize|authorization|permission)\b[^\n,.;:!?]{0,20}'
    r'\b(?:commit|push|create|switch)\b',
    re.IGNORECASE,
)
# Parse protected Git operations after global options, including `-C` and
# `--no-pager`, so one shell command cannot hide an extra operation.
def _git_subcommand(tokens, git_index):
    index = git_index + 1
    while index < len(tokens):
        token = tokens[index]
        if token in {";", "|", "&", "&&", "||"}:
            return None
        if token in {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}:
            index += 2
            continue
        if token.startswith(("--git-dir=", "--work-tree=", "--namespace=", "--super-prefix=", "--config-env=")):
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token.lower(), index
    return None


def _git_aliases(tokens, git_index):
    aliases = {}
    index = git_index + 1
    while index < len(tokens):
        token = tokens[index]
        if token in {";", "|", "&", "&&", "||"}:
            break
        if token in {"-c", "--config-env"} and index + 1 < len(tokens):
            value = tokens[index + 1]
            if token == "-c" and value.lower().startswith("alias.") and "=" in value:
                name, expansion = value[6:].split("=", 1)
                aliases[name.lower()] = expansion
            index += 2
            continue
        if token.startswith("--config-env="):
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return aliases


def _configured_git_aliases():
    try:
        result = subprocess.run(
            ["git", "config", "--get-regexp", r"^alias\."],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=0.5,
            check=False,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    aliases = {}
    for line in result.stdout.splitlines():
        match = re.match(r"(\S+)\s+(.+)$", line)
        if match and match.group(1).lower().startswith("alias."):
            aliases[match.group(1)[6:].lower()] = match.group(2).strip()
    return aliases


def _balanced_body(command, start):
    depth = 1
    body_start = start + (2 if command.startswith("$(", start) else 1)
    index = body_start
    quote = ""
    while index < len(command):
        char = command[index]
        if quote == "'":
            if char == "'":
                quote = ""
            index += 1
            continue
        if quote == '"':
            if char == "\\":
                index += 2
                continue
            if char == '"':
                quote = ""
            index += 1
            continue
        if char == "\\":
            index += 2
            continue
        if char in "'\"":
            quote = char
        elif command.startswith("$(", index):
            depth += 1
            index += 2
            continue
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return command[body_start:index], index + 1
        index += 1
    return None, len(command)


def _backtick_body(command, start):
    index = start + 1
    while index < len(command):
        if command[index] == "\\":
            index += 2
            continue
        if command[index] == "`":
            return command[start + 1:index], index + 1
        index += 1
    return None, len(command)


def _nested_command_bodies(command):
    patterns = (
        re.compile(r"\b(?:sh|bash|zsh|dash|ksh)(?:\.exe)?\s+(?:-[^\s]*c[^\s]*|--command)\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL),
        re.compile(r"\bcmd(?:\.exe)?\s+/c\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL),
        re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\s+(?:-[^\s]*c[^\s]*|--command)\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL),
    )
    bodies = [match.group(2) for pattern in patterns for match in pattern.finditer(command)]
    index = 0
    quote = ""
    while index < len(command):
        char = command[index]
        if quote == "'":
            if char == "'":
                quote = ""
            index += 1
            continue
        if quote == '"':
            if char == "\\":
                index += 2
                continue
            if char == '"':
                quote = ""
                index += 1
                continue
            if command.startswith("$(", index):
                body, index = _balanced_body(command, index)
                if body is not None:
                    bodies.append(body)
                continue
            if char == "`":
                body, index = _backtick_body(command, index)
                if body is not None:
                    bodies.append(body)
                continue
            index += 1
            continue
        if char in "'\"":
            quote = char
            index += 1
            continue
        if command.startswith("$(", index) or char == "(":
            body, index = _balanced_body(command, index)
            if body is not None:
                bodies.append(body)
            continue
        if char == "`":
            body, index = _backtick_body(command, index)
            if body is not None:
                bodies.append(body)
            continue
        index += 1
    return bodies


def _has_short_option(args, options):
    return any(
        token.startswith("-") and not token.startswith("--") and any(char in token[1:] for char in options)
        for token in args
    )


def _is_branch_creation(tokens, subcommand, subcommand_index):
    args = []
    for token in tokens[subcommand_index + 1:]:
        if token in {";", "|", "&", "&&", "||"}:
            break
        args.append(token.lower())

    if not args:
        return False
    if subcommand in {"checkout", "switch"}:
        if "--orphan" in args:
            return True
        if subcommand == "switch" and any(arg in {"--create", "--force-create"} for arg in args):
            return True
        return _has_short_option(args, "bB" if subcommand == "checkout" else "cC")

    if any(arg in {"-c", "-C", "-m", "-M", "-f", "--copy", "--move", "--force", "--track", "--no-track"} for arg in args):
        return True
    query_flags = {
        "--all", "--remotes", "-a", "-r",
        "--contains", "--no-contains", "--merged", "--no-merged", "--points-at",
        "--format", "--sort", "--column", "--color", "--omit-empty",
        "--show-current", "--verbose", "-v", "-vv",
    }
    if any(arg in query_flags or any(arg.startswith(flag + "=") for flag in query_flags if flag.startswith("--")) for arg in args):
        return False
    if "-l" in args or "--list" in args:
        return False
    return any(not arg.startswith("-") for arg in args)


def _command_basename(token):
    executable = re.sub(r"^.*[/\\\\]", "", token).lower()
    return re.sub(r"\.(?:exe|cmd|bat|ps1)$", "", executable)


_COMMAND_WRAPPERS = {"env", "sudo", "command"}
_SHELL_WRAPPERS = {"sh", "bash", "zsh", "dash", "ksh", "cmd", "powershell", "pwsh"}
_SHELL_COMMAND_FLAGS = {"-c", "--command", "/c", "-command"}


def _is_command_position(tokens, index):
    start = index
    while start and tokens[start - 1] not in {";", "|", "&", "&&", "||"}:
        start -= 1
    if index == start:
        return True
    wrapper = _command_basename(tokens[start])
    if wrapper in _COMMAND_WRAPPERS:
        return True
    if wrapper in _SHELL_WRAPPERS:
        for flag_index in range(start + 1, index):
            if tokens[flag_index].lower() in _SHELL_COMMAND_FLAGS:
                return index == flag_index + 1
    return False


def find_guarded_operations(command, _seen=None):
    raw = str(command or "")
    seen = _seen if _seen is not None else set()
    if not raw or raw in seen:
        return []
    seen.add(raw)

    try:
        lex_raw = re.sub(
            r"(?i)(?<![\w.-])(?:\.[/\\\\]|[A-Za-z]:[/\\\\][^\s;&|()]+[/\\\\])git\.ps1\b",
            "git.ps1",
            raw,
        )
        lexer = shlex.shlex(lex_raw, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        operations = [operation for operation, pattern in _GUARDED_COMMAND_RE.items() if pattern.search(raw)]
    else:
        operations = []
        for index, token in enumerate(tokens):
            executable = _command_basename(token)
            if not _is_command_position(tokens, index):
                continue
            if executable == "eval":
                body = " ".join(tokens[index + 1:])
                operations.extend(find_guarded_operations(body, seen))
                continue
            if executable.startswith("git-") and executable[4:] in {"commit", "push", "branch", "checkout", "switch"}:
                helper = executable[4:]
                if helper in {"commit", "push"}:
                    operations.append(helper)
                elif helper in {"checkout", "switch", "branch"} and _is_branch_creation(tokens, helper, index):
                    operations.append("branch")
                continue
            if executable != "git":
                continue
            subcommand = _git_subcommand(tokens, index)
            if not subcommand:
                continue
            operation, subcommand_index = subcommand
            if operation in {"commit", "push"}:
                operations.append(operation)
            elif operation in {"checkout", "switch", "branch"} and _is_branch_creation(tokens, operation, subcommand_index):
                operations.append("branch")
            else:
                aliases = _git_aliases(tokens, index)
                aliases.update(_configured_git_aliases())
                if operation not in aliases:
                    continue
                expansion = aliases[operation].strip()
                if expansion.startswith("!"):
                    expansion = expansion[1:].lstrip()
                else:
                    expansion = f"git {expansion}"
                args = tokens[subcommand_index + 1:]
                if args:
                    expansion += " " + " ".join(shlex.quote(arg) for arg in args)
                operations.extend(find_guarded_operations(expansion, seen))

    for body in _nested_command_bodies(raw):
        operations.extend(find_guarded_operations(body, seen))
    seen.remove(raw)
    return operations


def count_guarded_operations(command):
    return len(find_guarded_operations(command))

_NOISE_MARKERS = ("Stop hook feedback", "bash-input", "bash-stdout", "bash-stderr",
                  "system-reminder", "local-command", "UserPromptSubmit hook",
                  "PostToolUse", "PreToolUse")


def _latest_user_prompt(transcript_path):
    """Text of the most recent *genuine* user prompt in the session
    transcript, skipping hook feedback and `!`-command echoes."""
    if not transcript_path:
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-400:]
    except Exception:
        return ""
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("type") != "user":
            continue
        msg = entry.get("message", {}) or {}
        content = msg.get("content")
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = "\n".join(b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
        else:
            text = ""
        text = text.strip()
        if not text or any(m in text for m in _NOISE_MARKERS):
            continue
        return text
    return ""


def operation_text(text, operation):
    clauses = [clause.strip() for clause in re.split(r'[。！？；，,;:\n]', text)]
    selected = []
    for index, clause in enumerate(clauses):
        if not clause or not _OPERATION_RE[operation].search(clause):
            continue
        if index and re.search(
            r'(未经|未(?:经)?|尚未|没有|没|without|unless|only|just|after|if|when|once|until)',
            clauses[index - 1],
            re.IGNORECASE,
        ):
            selected.append(clauses[index - 1])
        selected.append(clause)
    return " ".join(dict.fromkeys(selected)) if selected else text


def user_confirmed(data, operation):
    """显式确认语义：否定 → 疑问句 → 确认词 → 操作意图。

    空文本/否定意图/疑问查询/裸操作指令 → False；确认词表命中 → True；
    必须同时包含确认词与对应操作词才放行。
    """
    text = _latest_user_prompt(data.get("transcript_path", "")).strip()
    if not text:
        return False
    text = operation_text(text, operation)
    if _NEGATIVE_OPERATION_RE[operation].search(text):
        return False
    if _CONDITIONAL_OPERATION_RE.search(text):
        return False
    if _QUESTION_RE.search(text) or _QUERY_OPERATION_RE.search(text):
        return False
    if _CONFIRM_RE.search(text) and _OPERATION_RE[operation].search(text):
        return True
    return False


BLOCK = [
    (r'git\s+reset\s+--hard', 'git reset --hard'),
    (r'(?:git\s+branch|git-branch(?:\.exe)?)\s+-D\b', 'git branch -D (强制删分支)'),
    (r'(?:git\s+push|git-push(?:\.exe)?)\s+(?:-f\b|--force\b)', 'git push --force'),
    (r'git\s+clean\s+-[a-z]*f', 'git clean -f'),
    (r'\brm\s+-rf?\b', 'rm -rf'),
    (r'--no-verify', '--no-verify (绕过 hook)'),
    (r'--no-gpg-sign', '--no-gpg-sign (绕过签名)'),
    (r'-c\s+commit\.gpgsign=false', '禁用 gpg 签名'),
    (r'DROP\s+(?:TABLE|DATABASE)\b', 'SQL DROP (删表/库)'),
    (r'(?:curl|wget)[^|]*\|\s*(?:sh|bash)\b', 'curl/wget 管道执行远程脚本'),
    (r'chmod\s+-R\s+777\b', 'chmod -R 777 (全权限)'),
    (r'\bnpm\s+publish\b', 'npm publish (发布)'),
    (r'>\s*/dev/sd[a-z]', '写块设备 /dev/sdX'),
]
for pat, name in BLOCK:
    if re.search(pat, cmd):
        msg = (f"git_guard BLOCKED: {name}\n"
               f"CLAUDE.md §1.3 人工确认线:破坏性/绕过操作需用户显式确认。")
        deny(msg)

guarded_operations = find_guarded_operations(cmd)
if len(guarded_operations) > 1:
    deny("git_guard BLOCKED: 一条命令包含多个受保护 Git 操作，请拆分命令并分别确认。")

if guarded_operations:
    operation = guarded_operations[0]
    if operation == "commit":
        if user_confirmed(data, "commit"):
            sys.exit(0)  # 用户已显式确认 -> 放行 commit
        deny("CLAUDE.md §1.3: commit 需用户显式确认(回复「确认提交」/confirm commit)。建议先展示 git diff --cached --stat。")
    elif operation == "push":
        if user_confirmed(data, "push"):
            sys.exit(0)  # 用户已显式确认 -> 放行 push
        deny("CLAUDE.md §1.3: push 前确认分支/远端,展示待 push commits 给用户确认。")
    elif operation == "branch":
        if user_confirmed(data, "branch"):
            sys.exit(0)  # 用户已确认 -> 放行新建分支
        deny("CLAUDE.md §1.1: 新建分支前确认 git status 干净(回复「确认创建分支」/confirm branch)。")

if not SELF_TEST:
    sys.exit(0)


if SELF_TEST:
    # 自检：pi safety-net guards.js 同款断言（2026-08-28 移植时保留）
    import tempfile

    def _mk_transcript(texts):
        f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        for t in texts:
            f.write(json.dumps({"type": "user", "message": {"content": t}}) + "\n")
        f.close()
        return f.name

    def _check(data, op, expected, label):
        got = user_confirmed(data, op)
        assert got is expected, f"FAIL {label}: got={got}, expect={expected}"
        print(f"  ok {label}")

    print("git_guard user_confirmed self-test:")
    cases = [
        ("确认提交全部 5 组", "commit", True, "确认词放行"),
        ("提交全部 5 组", "commit", False, "裸提交指令拦"),
        ("先别提交", "commit", False, "否定意图拦"),
        ("怎么提交？", "commit", False, "疑问句拦"),
        ("是否确认提交？", "commit", False, "确认疑问句拦"),
        ("确认提交，提交后帮我检查状态", "commit", True, "后续查询不否定确认"),
        ("确认后提交", "commit", False, "条件确认不放行"),
        ("only commit after I confirm", "commit", False, "英文条件确认不放行"),
        ("推上去吧", "push", False, "裸推送指令拦"),
        ("推送发布到远端", "push", False, "裸推送动词拦"),
        ("确认发布文档", "push", False, "发布非推送拦"),
        ("确认查看分支", "branch", False, "查看分支不授权创建"),
        ("确认创建分支", "branch", True, "创建分支放行"),
        ("没有确认就提交", "commit", False, "没有确认条件拦"),
        ("未经确认，确认提交", "commit", False, "独立否定分句拦"),
        ("commit without confirmation", "commit", False, "without 条件拦"),
        ("确认提交，之后是否需要推送", "commit", True, "跨操作疑问不影响提交"),
        ("确认提交，之后是否需要推送", "push", False, "跨操作疑问拦推送"),
        ("confirm git branch feature", "branch", True, "英文 git 分支确认放行"),
        ("确认 git checkout -b feature", "branch", True, "中文 git 分支确认放行"),
        ("看看提交历史", "commit", False, "查询意图拦(看看)"),
        ("帮我检查一下状态", "commit", False, "查询意图拦(检查)"),
    ]
    for text, op, expect, label in cases:
        path = _mk_transcript([text])
        try:
            _check({"transcript_path": path}, op, expect, label)
        finally:
            os.unlink(path)
    print("  all ok")

    print("git_guard operation parser self-test:")
    operation_cases = [
        ("git commit -m x", ["commit"], "direct commit"),
        ("git -C repo commit -m x", ["commit"], "-C commit"),
        ("git --no-pager push origin main", ["push"], "--no-pager push"),
        ("git -C repo commit -m x && git push origin main", ["commit", "push"], "mixed operations"),
        ("sh -c 'git commit -m x'", ["commit"], "sh wrapper commit"),
        ("cmd /c git commit -m x", ["commit"], "cmd unquoted wrapper commit"),
        ("powershell -c git push origin main", ["push"], "powershell unquoted wrapper push"),
        ("(git commit)", ["commit"], "subshell commit"),
        ("$(git commit $(printf x))", ["commit"], "nested command substitution commit"),
        ("echo '$(git commit)'", [], "single quoted substitution is inert"),
        ("sh -c 'git commit' && sh -c 'git commit'", ["commit", "commit"], "duplicate nested commits"),
        (r".\git.ps1 commit -m x", ["commit"], "git.ps1 commit"),
        ("git branch --contains main", [], "branch contains query"),
        ("git branch --merged main", [], "branch merged query"),
        ("$(git push origin main)", ["push"], "command substitution push"),
        ("git.exe -C repo commit -m x", ["commit"], "git.exe commit"),
        ("git.cmd commit -m x", ["commit"], "git.cmd commit"),
        ("git branch feature", ["branch"], "branch create"),
        ("git checkout --quiet -b feature", ["branch"], "checkout option order"),
        ("git checkout -B feature", ["branch"], "checkout force branch"),
        ("git switch -C feature", ["branch"], "switch force branch"),
        ("git -c alias.ci=commit ci", ["commit"], "explicit commit alias"),
        ("git -c alias.p=push p origin main", ["push"], "explicit push alias with args"),
        ("git -c alias.co=checkout co -b feature", ["branch"], "explicit branch alias with args"),
        ("git branch --list feature", [], "branch listing"),
        ("git branch --all feature", [], "branch all query"),
        ("git branch --remotes feature", [], "branch remotes query"),
        ("git switch --create feature", ["branch"], "switch create branch"),
        ("git switch --force-create feature", ["branch"], "switch force-create branch"),
        ("eval 'git commit -m x'", ["commit"], "eval commit"),
        ("echo git commit", [], "echo git inert"),
        ("git-commit.exe -m x", ["commit"], "git-commit helper"),
        ("git-push.exe origin main", ["push"], "git-push helper"),
        ("git-branch.exe --all feature", [], "git-branch helper query"),
        ("git status", [], "unprotected status"),
    ]
    for command, expected, label in operation_cases:
        got = find_guarded_operations(command)
        assert got == expected, f"FAIL {label}: got={got}, expect={expected}"
        print(f"  ok {label}")
    print("  all ok")