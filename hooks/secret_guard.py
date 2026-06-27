import sys, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SECRET_FILES = re.compile(
    r"(?i)(^|[/\\\s])(?:\.env(?:\.[\w-]+)?|id_rsa|id_dsa|id_ecdsa|id_ed25519|"
    r"\.npmrc|\.pypirc|\.netrc|\.pgpass|\.my\.cnf|"
    r"\.aws[/\\]credentials|\.aws[/\\]config|credentials\.json|serviceaccount\.json|"
    r"htpasswd|\.htpasswd|shadow)\b"
)

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
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

event = data.get("hook_event_name", "")

if not data.get("tool_input", {}).get("command"):
    sys.exit(0)

if event == "PreToolUse":
    cmd = data.get("tool_input", {}).get("command", "")
    m = SECRET_FILES.search(cmd)
    if m:
        msg = ("secret_guard BLOCKED: 命令疑似读取机密文件 (" + m.group(0) + "). "
               "CLAUDE.md §1.3: 机密文件(.env/key/credentials/id_rsa/...)不应进 AI 上下文。"
               "改读 .env.example / 文档, 或由用户手动 cat 确认, 或显式声明授权。")
        deny(msg)
    sys.exit(0)

if event == "PostToolUse":
    resp = data.get("tool_response", {}) or {}
    out = (resp.get("stdout") or "") + "\n" + (resp.get("stderr") or "")
    if not out:
        sys.exit(0)
    hits = []
    for rx, name in SECRET_PATTERNS:
        m = rx.search(out)
        if m:
            preview = m.group(0)[:8] + "..." + m.group(0)[-3:]
            hits.append(f"{name} ({preview})")
    if hits:
        post_warn(
            "secret_guard 警告: Bash 输出含疑似密钥 -> "
            + "; ".join(hits[:3])
            + "。机密已进 AI 上下文,后续勿外发/勿写入提交。建议轮换该密钥。"
        )
    sys.exit(0)

sys.exit(0)