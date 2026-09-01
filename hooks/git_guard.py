import sys, json, os, re, shlex, hashlib

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
    "push": re.compile(r'(?:推送|\bpush\b)', re.IGNORECASE),
    "branch": re.compile(r'(?:分支|\bbranch\b)', re.IGNORECASE),
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
    "commit": re.compile(r'\bgit\s+commit\b', re.IGNORECASE),
    "push": re.compile(r'\bgit\s+push\b', re.IGNORECASE),
    "branch": re.compile(r'\bgit\s+(?:checkout\s+-b|switch\s+-c)\b', re.IGNORECASE),
}

# pi explicitApproval 语义（2026-08-28 自 pi safety-net guards.js 移植）：
# 疑问句/查询式指令不放行；确认词表命中即授权；操作意图（提交/推送 等动词）
# 单独出现也视为用户明确指令授权，不需要确认词。
_QUESTION_RE = re.compile(
    r'(?:？|\?|吗|怎么|为什么|能不能|可否|是否有|看看|检查|查一下|告诉我|怎么操作)',
    re.IGNORECASE,
)
_INTENT_RE = {
    "commit": re.compile(r'(?:提交|\bcommit\b)', re.IGNORECASE),
    "push": re.compile(r'(?:推送|推上去|推一下|发布|\bpush\b)', re.IGNORECASE),
    "branch": re.compile(r'(?:分支|\bbranch\b)', re.IGNORECASE),
}
def count_guarded_operations(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return sum(len(pattern.findall(command)) for pattern in _GUARDED_COMMAND_RE.values())

    count = 0
    for index, token in enumerate(tokens[:-1]):
        if token.lower() != "git":
            continue
        operation = tokens[index + 1].lower()
        if operation in ("commit", "push"):
            count += 1
        elif operation in ("checkout", "switch") and index + 2 < len(tokens):
            if tokens[index + 2].lower() in ("-b", "-c"):
                count += 1
    return count

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


def user_confirmed(data, operation):
    """pi explicitApproval 语义：否定 → 确认词 → 疑问句 → 操作意图。

    空文本/否定意图/疑问查询 → False；确认词表命中 → True；
    指令含操作动词（提交/推送）且无疑问 → True。
    """
    text = _latest_user_prompt(data.get("transcript_path", "")).strip()
    if not text:
        return False
    if _NEGATIVE_OPERATION_RE[operation].search(text):
        return False
    if _CONFIRM_RE.search(text) and _OPERATION_RE[operation].search(text):
        return True
    if _QUESTION_RE.search(text):
        return False
    return bool(_INTENT_RE[operation].search(text))


BLOCK = [
    (r'git\s+reset\s+--hard', 'git reset --hard'),
    (r'git\s+branch\s+-D\b', 'git branch -D (强制删分支)'),
    (r'git\s+push\s+(?:-f\b|--force\b)', 'git push --force'),
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

guarded_operation_count = count_guarded_operations(cmd)
if guarded_operation_count > 1:
    deny("git_guard BLOCKED: 一条命令包含多个受保护 Git 操作，请拆分命令并分别确认。")

if re.search(r'git\s+commit\b', cmd):
    if user_confirmed(data, "commit"):
        sys.exit(0)  # 用户已显式确认 -> 放行 commit
    deny("CLAUDE.md §1.3: commit 需用户显式确认(回复「确认提交」/confirm commit)。建议先展示 git diff --cached --stat。")
elif re.search(r'git\s+push\b', cmd):
    if user_confirmed(data, "push"):
        sys.exit(0)  # 用户已显式确认 -> 放行 push
    deny("CLAUDE.md §1.3: push 前确认分支/远端,展示待 push commits 给用户确认。")
elif re.search(r'git\s+(?:checkout\s+-b|switch\s+-c)\b', cmd):
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
        ("提交全部 5 组", "commit", True, "操作指令放行"),
        ("先别提交", "commit", False, "否定意图拦"),
        ("怎么提交？", "commit", False, "疑问句拦"),
        ("推上去吧", "push", True, "推送口语放行"),
        ("推送发布到远端", "push", True, "推送动词放行"),
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