import sys, json, re, time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"

VERIFY_PATTERNS = [
    r"\bpytest\b", r"\bpython\s+-m\s+unittest\b", r"\bnosetests\b",
    r"\bnx\s+test\b", r"\bjest\b", r"\bvitest\b", r"\bmocha\b", r"\bkarma\b",
    r"(?<![\w-])\btsc\b", r"\bnpm\s+(?:run\s+)?(?:test|build|lint|check|typecheck)\b",
    r"\byarn\s+(?:test|build|lint|typecheck)\b", r"\bpnpm\s+(?:test|build|lint|typecheck)\b",
    r"\bbun\s+(?:test|run\s+build)\b",
    r"\bgo\s+(?:test|build|vet|check)\b", r"\bcargo\s+(?:test|build|check|clippy)\b",
    r"\bmvn\s+(?:test|verify|compile)\b", r"\bgradle\s+(?:test|build|check)\b", r"\bgradlew\b",
    r"\bruff\b", r"\bflake8\b", r"\bpylint\b", r"\bmypy\b", r"\bpyright\b",
    r"\beslint\b", r"\bbiome\b", r"\bstylelint\b",
    r"\bruby\s+-Itest\b", r"\brspec\b", r"\brubocop\b",
    r"\bdotnet\s+(?:test|build)\b", r"\bmsbuild\b",
    r"\bclang\b", r"\bgcc\b", r"\bg\+\+", r"\bcmake\s+--build\b", r"\bmake\b(?!\s*install)",
    r"\bsqlfluff\b", r"\bsqlparse\b", r"\bshellcheck\b", r"\bshfmt\b",
    r"\bdeno\s+(?:test|lint|check)\b", r"\bswift\s+test\b", r"\bxcodebuild\b",
    r"\bflutter\s+test\b", r"\bdart\s+(?:test|analyze)\b",
]
COMPILED = [re.compile(p) for p in VERIFY_PATTERNS]

def new_state(sid):
    return {"session_id": sid, "paths": [], "edits_per_path": {}, "last_edit_ts": 0.0, "last_verify_ts": 0.0, "verify_cmds": [], "stop_blocks": 0}

def load(sid):
    try:
        with open(STATE, encoding="utf-8") as f:
            st = json.load(f)
        if st.get("session_id") != sid:
            st = new_state(sid)
    except Exception:
        st = new_state(sid)
    return st

def save(st):
    try:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(st, f)
    except Exception:
        pass

try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

if not data.get("tool_input", {}).get("command"):
    sys.exit(0)

event = data.get("hook_event_name", "")
if event != "PostToolUse":
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
matched = None
for p in COMPILED:
    m = p.search(cmd)
    if m:
        matched = m.group(0).strip()
        break
if not matched:
    sys.exit(0)

sid = data.get("session_id", "unknown")
st = load(sid)
st["last_verify_ts"] = time.time()
st["stop_blocks"] = 0
cmds = st.get("verify_cmds", [])
if matched not in cmds:
    cmds.append(matched)
    st["verify_cmds"] = cmds[-20:]
save(st)
sys.exit(0)