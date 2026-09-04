import sys, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SECRET_FILES = re.compile(
    r"(?i)(^|[/\\\s])(?:\.env(?!\.(?:example|sample|template)(?:\b|$))(?:\.[\w-]+)?|id_rsa|id_dsa|id_ecdsa|id_ed25519|"
    r"\.npmrc|\.pypirc|\.netrc|\.pgpass|\.my\.cnf|"
    r"\.aws[/\\]credentials|\.aws[/\\]config|\.git-credentials|credentials\.json|serviceaccount\.json|"
    r"htpasswd|\.htpasswd|shadow)\b"
)
SECRET_GLOBS = re.compile(r"(?i)(^|[/\\\s])\.\[[eE]\][nN][vV](?:\b|$)")
MCP_FILE_TOOLS = {
    "mcp__lean-ctx__ctx_read", "mcp__lean-ctx__ctx_glob",
    "mcp__lean-ctx__ctx_tree", "mcp__lean-ctx__ctx_search",
}
READ_TOOLS = {
    "Read", "read", "ReadFile", "read_file", "View", "view",
    "Grep", "grep", "Search", "search", "ListFiles", "list_files",
    "ListDirectory", "list_directory", "Glob", "glob",
}

SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9_\-]{16,}"), "OpenAI sk- key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS AKIA key"),
    (re.compile(r"ghp_[a-zA-Z0-9]{30,}"), "GitHub PAT (ghp_)"),
    (re.compile(r"gho_[a-zA-Z0-9]{30,}"), "GitHub OAuth (gho_)"),
    (re.compile(r"github_pat_[a-zA-Z0-9_]{30,}"), "GitHub fine-grained PAT"),
    (re.compile(r"xox[bpoa]-[a-zA-Z0-9\-]{10,}"), "Slack token (xox)"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "Google API key (AIza)"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "PEM private key block"),
    (re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}"), "Google OAuth (ya29.)"),
]


# Pre 拦截: Claude PreToolUse permissionDecision=deny。Post 告警: hookSpecificOutput.additionalContext。
def deny(msg):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        }
    }, ensure_ascii=False))
    sys.exit(0)

def post_warn(msg):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }, ensure_ascii=False))
    sys.exit(0)

try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    if _i < 0:
        raise ValueError("hook input has no JSON object")
    data = json.loads(_raw[_i:])
except Exception:
    if re.search(r'"hook_event_name"\s*:\s*"PostToolUse"', _raw):
        sys.exit(0)
    deny("secret_guard BLOCKED: Hook 输入无效，无法确认命令或路径是否含机密。")

if not isinstance(data, dict):
    deny("secret_guard BLOCKED: Hook 输入结构无效，无法确认命令或路径是否含机密。")

event = data.get("hook_event_name", "")
tool = data.get("tool_name", "")
tool_input = data.get("tool_input", {}) or {}

if event == "PreToolUse" and tool in MCP_FILE_TOOLS:
    for key in ("path", "file_path", "pattern", "query"):
        value = tool_input.get(key, "")
        if isinstance(value, str):
            m = SECRET_FILES.search(value) or SECRET_GLOBS.search(value)
            if m:
                deny(
                    "secret_guard BLOCKED: MCP 文件查询疑似触及机密路径 ("
                    + m.group(0)
                    + "). 请改读 .env.example 或脱敏材料。"
                )

if event == "PreToolUse" and tool in READ_TOOLS:
    for key in ("file_path", "path", "pattern"):
        value = tool_input.get(key, "")
        if isinstance(value, str):
            m = SECRET_FILES.search(value) or SECRET_GLOBS.search(value)
            if m:
                deny(
                    "secret_guard BLOCKED: 文件查询疑似读取机密路径 ("
                    + m.group(0)
                    + "). CLAUDE.md §1.3: 机密文件不应进 AI 上下文。"
                    "改读 .env.example / 文档, 或提供脱敏内容。"
                )
    sys.exit(0)

if not data.get("tool_input", {}).get("command"):
    sys.exit(0)

if event == "PreToolUse":
    cmd = data.get("tool_input", {}).get("command", "")
    m = SECRET_FILES.search(cmd) or SECRET_GLOBS.search(cmd)
    if m:
        msg = ("secret_guard BLOCKED: 命令疑似读取机密文件 (" + m.group(0) + "). "
               "CLAUDE.md §1.3: 机密文件(.env/key/credentials/id_rsa/...)不应进 AI 上下文。"
               "改读 .env.example / 文档, 或由用户手动 cat 确认, 或显式声明授权。")
        deny(msg)
    sys.exit(0)

if event == "PostToolUse":
    resp = data.get("tool_response")
    if isinstance(resp, str):
        out = resp
    elif isinstance(resp, dict):
        out = (resp.get("stdout") or "") + "\n" + (resp.get("stderr") or "")
    else:
        out = ""
    if not out:
        sys.exit(0)
    hits = []
    for rx, name in SECRET_PATTERNS:
        if rx.search(out):
            hits.append(name)
    if hits:
        post_warn(
            "secret_guard 警告: Bash 输出含疑似密钥类型 -> "
            + "; ".join(hits[:3])
            + "。机密已进 AI 上下文,后续勿外发/勿写入提交。建议轮换该密钥。"
        )
    sys.exit(0)

sys.exit(0)