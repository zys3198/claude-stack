import sys, json, time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch", "update", "str_replace_based_edit_tool", "file_edit")

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

event = data.get("hook_event_name", "")
sid = data.get("session_id", "unknown")
tool = data.get("tool_name", "")
ti = data.get("tool_input", {}) or {}
path = ti.get("file_path") or ti.get("notebook_path") or ""

if event == "SessionStart":
    save(new_state(sid))
    sys.exit(0)

if event == "PreToolUse" and tool in EDIT_TOOLS:
    # Claude Pre 支持 additionalContext 软提醒(Codex 失效那处,这里恢复)。
    st = load(sid)
    preview = set(st.get("paths", []))
    if path:
        preview.add(path)
    if len(preview) >= 3:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": f"edited_tracker: 本次改动累计 {len(preview)} 文件(>=3)。CLAUDE.md §1.1 改动确认线:跨多目录/>=3 文件先 1-2 行说明改哪些+目标,确认再动手。"}}, ensure_ascii=False))
    sys.exit(0)

if event == "PostToolUse" and tool in EDIT_TOOLS:
    st = load(sid)
    now = time.time()
    if path:
        if path not in st["paths"]:
            st["paths"].append(path)
        st["edits_per_path"][path] = st["edits_per_path"].get(path, 0) + 1
        st["last_edit_ts"] = now
        st["stop_blocks"] = 0
        save(st)
    sys.exit(0)

sys.exit(0)