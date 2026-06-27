import sys, json

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STATE = "C:/Users/zys31/.claude/hooks/turn_state.json"
THRESHOLD = 20

try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

sid = data.get("session_id", "unknown")
try:
    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
except Exception:
    st = {"session_id": None, "count": 0}

if st.get("session_id") != sid:
    st = {"session_id": sid, "count": 0}

st["count"] += 1
try:
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f)
except Exception:
    pass

if st["count"] >= THRESHOLD:
    msg = (f"CLAUDE.md §7: 当前会话第 {st['count']} 轮(>= {THRESHOLD}),上下文可能饱和。建议 /compact 压缩。")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}}, ensure_ascii=False))
sys.exit(0)