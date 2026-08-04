import sys, json

# learning_nudge — Stop hook. Counts substantive tasks (code-file edits, per
# edited_tracker's edited_state.json) across sessions; every N fires a one-line
# learning-first v2.2 reminder, then resets. Reminder-only: never blocks.
# Pattern mirrors verify_gate.py (load/save state, stop_hook_active guard,
# fail-silent on any error). State lives in its own file, NOT edited_state —
# edited_state is per-session and would reset the counter every new session.

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

EDITED = "C:/Users/zys31/.claude/hooks/edited_state.json"
STATE = "C:/Users/zys31/.claude/hooks/learning_state.json"
N = 8

CODE_EXT = (".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go",
            ".rs", ".java", ".kt", ".kts", ".c", ".cc", ".cpp", ".cxx", ".h",
            ".hh", ".hpp", ".hxx", ".cs", ".rb", ".php", ".swift", ".m", ".mm",
            ".scala", ".sc", ".vue", ".svelte", ".ex", ".exs", ".dart", ".lua",
            ".clj", ".cljs", ".cljc", ".hs", ".ml", ".mli", ".fs", ".fsx",
            ".nim", ".zig", ".v", ".sv", ".jl", ".pl", ".pm", ".r", ".R")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f)
    except Exception:
        pass


try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

# Never re-fire inside a stop-hook continuation (prevents stop-loop).
if data.get("stop_hook_active"):
    sys.exit(0)

sid = data.get("session_id", "unknown")

# A "substantive task" this turn = edited_tracker saw >=1 CODE file edited this
# session. Read its per-session state; only count code edits, skip docs/config.
edited = read_json(EDITED)
if not edited or edited.get("session_id") != sid:
    sys.exit(0)  # no edit activity this session
code_paths = [p for p in edited.get("paths", []) if p.lower().endswith(CODE_EXT)]
if not code_paths:
    sys.exit(0)  # only docs/config/memory touched — not a substantive coding task

# Count this session once. Guard against double-counting if Stop fires again in
# the same session before a new edit session begins: count distinct session ids.
st = read_json(STATE) or {"count": 0, "counted_sessions": []}
counted = st.get("counted_sessions", [])
if sid in counted:
    sys.exit(0)  # already counted this session's substantive work

st["count"] = int(st.get("count", 0)) + 1
counted.append(sid)
st["counted_sessions"] = counted[-50:]  # keep bounded
save(STATE, st)

if st["count"] < N:
    sys.exit(0)

# Threshold hit: remind once, reset counter.
st["count"] = 0
save(STATE, st)

msg = (
    f"learning-first v2.2: 已 {N} 个实质编码任务。\n"
    "  挑最近一个 AI 帮做的,闭卷重做一遍(不看 transcript/笔记)——卡住=没真学会。\n"
    "  也可现在说『skip』跳过本次。每月闭卷重做见 cron 提醒。"
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": msg,
    }
}, ensure_ascii=False))
sys.exit(0)
