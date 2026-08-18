import sys, json

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"

MAX_BLOCKS = 3

def load(sid):
    try:
        with open(STATE, encoding="utf-8") as f:
            st = json.load(f)
        if st.get("session_id") != sid:
            return None
        return st
    except Exception:
        return None

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

sid = data.get("session_id", "unknown")
st = load(sid)
if st is None:
    sys.exit(0)

paths = st.get("paths", [])
# code_pending 由 edited_tracker 维护（仅代码文件）；缺省视为空——历史 paths 里的旧代码文件不回溯追究
code_paths = st.get("code_pending", [])
if not code_paths:
    sys.exit(0)

last_edit = float(st.get("last_edit_ts", 0))
last_verify = float(st.get("last_verify_ts", 0))
if last_verify >= last_edit:
    # 验证已覆盖全部改动：清空代码监视，防 markdown 编辑重新武装门禁
    st["code_pending"] = []
    st["stop_blocks"] = 0
    save(st)
    sys.exit(0)

if data.get("stop_hook_active"):
    sys.exit(0)

blocks = int(st.get("stop_blocks", 0)) + 1
st["stop_blocks"] = blocks
save(st)

verify_cmds = st.get("verify_cmds", [])
hint = "、".join(verify_cmds[-5:]) if verify_cmds else "无"

if blocks >= MAX_BLOCKS:
    auto_reason = (f"verify_gate AUTO-RELEASE ({blocks}/{MAX_BLOCKS}): 防死循环放行。代码改动未跑验证，但已达拦截上限。\n  改动文件({len(code_paths)}): {', '.join(code_paths[:5])}\n  最近验证命令: {hint}\n  -> 建议下次改动后主动跑验证。")
    st["code_pending"] = []
    st["stop_blocks"] = 0
    save(st)
    print(json.dumps({"decision": "approve", "reason": auto_reason}, ensure_ascii=False))
    sys.exit(0)

reason = (f"verify_gate BLOCKED ({blocks}/{MAX_BLOCKS}): 检测到代码改动但未跑验证就收工。\n  改动文件({len(code_paths)}): {', '.join(code_paths[:5])}\n  CLAUDE.md §1.3: 改动后跑 lint + test + 编译(tsc/go build/pytest...).\n  最近验证命令: {hint}\n  -> 跑验证命令, 或纯结构改动跑任一相关命令记录后即可收工.\n  -> 第 {MAX_BLOCKS} 次拦截后自动放行(防死循环).")
print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
sys.exit(2)