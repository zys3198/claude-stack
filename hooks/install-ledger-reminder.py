import sys, json, re, os
from datetime import datetime

# PostToolUse hook: 检测安装/卸载类 shell 命令 → 追加 auto-log.jsonl 兜底记录 +
# additionalContext 提醒模型按 CLAUDE.md §7 在 ~/.claude/installing/ 正式登记。
# 非安装命令毫秒级退出。

LOG = os.path.join(os.path.expanduser("~"), ".claude", "installing", "auto-log.jsonl")

PATTERNS = re.compile(
    r"(?:^|[;&|]\s*|\n)\s*(?:sudo\s+)?"
    r"(?:claude\s+(?:plugin|mcp)\s+(?:install|uninstall|remove|add|update)"
    r"|npx\s+skills\s+add"
    r"|npm\s+(?:i|install)\s+(?:-g|--global)"
    r"|pnpm\s+add\s+-g|yarn\s+global\s+add|bun\s+add\s+-g"
    r"|pipx?\s+(?:install|uninstall)"
    r"|uv\s+(?:tool\s+)?(?:pip\s+)?install"
    r"|cargo\s+(?:install|uninstall)"
    r"|winget\s+(?:install|uninstall)"
    r"|scoop\s+(?:install|uninstall)"
    r"|gem\s+install|composer\s+(?:global\s+)?require|dotnet\s+tool\s+(?:install|uninstall))"
    r"\b"
)
SECRET_ARGS = re.compile(
    r"(?i)(--?(?:token|password|passwd|secret|api[-_]?key|access[-_]?token|private[-_]?key))"
    r"(?:=|\s+)(?:\"[^\"]*\"|'[^']*'|[^\s;&|]+)"
)
SECRET_ASSIGNMENTS = re.compile(
    r"(?i)\b([A-Z][A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API[_-]?KEY|PRIVATE[_-]?KEY))=([^\s;&|]+)"
)
AUTH_URL = re.compile(r"(?i)(https?://)[^/\s:@]+:[^@\s]+@")


def redact_command(command):
    command = AUTH_URL.sub(r"\1<redacted>@", command)
    command = SECRET_ARGS.sub(r"\1=<redacted>", command)
    return SECRET_ASSIGNMENTS.sub(r"\1=<redacted>", command)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    i = raw.find("{")
    data = json.loads(raw[i:]) if i >= 0 else {}
except Exception:
    sys.exit(0)

if data.get("hook_event_name") != "PostToolUse":
    sys.exit(0)
cmd = ((data.get("tool_input", {}) or {}).get("command") or "").strip()
if not cmd or not PATTERNS.search(cmd):
    sys.exit(0)

entry = json.dumps({
    "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
    "session_id": data.get("session_id", ""),
    "cmd": redact_command(cmd)[:500],
    "cwd": (data.get("cwd") or "")[:200],
}, ensure_ascii=False)
try:
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
except Exception:
    pass

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "install-ledger: 检测到安装/卸载命令，已记 auto-log.jsonl。请本轮按 CLAUDE.md §7 在 ~/.claude/installing/ 对应台账（skill-install/mcp-install/tool-install/custom-setup.md）正式登记：来源、日期、命令原文、位置、依赖、备注；目标是仅凭台账可原样恢复。",
    }
}, ensure_ascii=False))
sys.exit(0)
