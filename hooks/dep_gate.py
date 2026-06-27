import sys, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ADD_PATTERNS = [
    (re.compile(r"\bpip3?\s+install\b(?!\s+-e\b)(?![^|&;]*\s-r\s)"), "pip install"),
    (re.compile(r"\bpipx\s+install\b"), "pipx install"),
    (re.compile(r"\buv\s+(?:add|pip\s+install)\b"), "uv add"),
    (re.compile(r"\bpoetry\s+add\b"), "poetry add"),
    (re.compile(r"\bnpm\s+install\b(?!\s*-g\b)(?![^|&;]*--no-save)(?![^|&;]*--package-lock)(?!\s*\.?\s*$)"), "npm install <pkg>"),
    (re.compile(r"\bnpm\s+i\s+\S"), "npm i <pkg>"),
    (re.compile(r"\bnpx\s+create-"), "npx create-* (脚手架,装大量依赖)"),
    (re.compile(r"\byarn\s+add\b"), "yarn add"),
    (re.compile(r"\bpnpm\s+add\b"), "pnpm add"),
    (re.compile(r"\bbun\s+add\b"), "bun add"),
    (re.compile(r"\bcargo\s+add\b"), "cargo add"),
    (re.compile(r"\bgo\s+get\b"), "go get"),
    (re.compile(r"\bgem\s+install\b"), "gem install"),
    (re.compile(r"\bbundle\s+add\b"), "bundle add"),
    (re.compile(r"\bcomposer\s+(?:require|create-project)\b"), "composer require"),
    (re.compile(r"\bdotnet\s+add\s+package\b"), "dotnet add package"),
    (re.compile(r"\bapk\s+add\b|\bapt(?:-get)?\s+install\b|\byum\s+install\b|\bdnf\s+install\b|\bpacman\s+-S\b|\bbrew\s+install\b"), "系统包管理器 install"),
]

def deny(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": msg}}, ensure_ascii=False))
    sys.exit(0)

try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

if not data.get("tool_input", {}).get("command"):
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
hits = [name for rx, name in ADD_PATTERNS if rx.search(cmd)]
if not hits:
    sys.exit(0)

deny(f"dep_gate: 命令疑似新增依赖 -> {', '.join(hits[:3])}.\n  命令: {cmd[:100]}\n  CLAUDE.md §1.1 / §6: 新增依赖=技术栈/攻击面变更,属「须确认」级.\n  -> 动手前向用户确认: 包名+版本+来源可信度.\n  -> 本地 -e ./path 开发装、lock 重建等不新增外部攻击面的可放过.")
sys.exit(0)