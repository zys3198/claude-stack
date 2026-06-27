import sys, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

LOG = "C:/Users/zys31/.claude/hooks/debug.log"
try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception as e:
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"--- ERROR parse: {e}\n--- RAW_DUMP[{len(_raw)}]: {_raw[:800]!r}\n")
    except Exception:
        pass
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
if not ti.get("command"):
    sys.exit(0)

cmd = ti.get("command", "")
try:
    with open(LOG, "a", encoding="utf-8") as _f:
        _f.write(f"--- heartbeat | tool={data.get('tool_name')} cmd={cmd[:120]}\n")
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

if re.search(r'git\s+commit\b', cmd):
    deny("CLAUDE.md §1.3: commit 前先向用户展示 git diff --cached --stat,等确认。")
elif re.search(r'git\s+push\b', cmd):
    deny("CLAUDE.md §1.3: push 前确认分支/远端,展示待 push commits 给用户确认。")
elif re.search(r'git\s+(?:checkout\s+-b|switch\s+-c)\b', cmd):
    deny("CLAUDE.md §1.1: 新建分支前确认 git status 干净(无未提交改动)。")

sys.exit(0)