import sys, json, time, os, hashlib, subprocess

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"
STATE_OVERRIDE = os.environ.get("CLAUDE_HOOK_STATE")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch", "update", "str_replace_based_edit_tool", "file_edit")
CODE_EXT = (".py",".pyi",".ts",".tsx",".js",".jsx",".mjs",".cjs",".go",".rs",".java",".kt",".kts",".c",".cc",".cpp",".cxx",".h",".hh",".hpp",".hxx",".cs",".rb",".php",".swift",".m",".mm",".scala",".sc",".vue",".svelte",".ex",".exs",".dart",".lua",".clj",".cljs",".cljc",".hs",".ml",".mli",".fs",".fsx",".nim",".zig",".v",".sv",".jl",".pl",".pm",".r",".R")


def state_path(sid):
    if STATE_OVERRIDE:
        return STATE_OVERRIDE
    token = hashlib.sha256(sid.encode("utf-8")).hexdigest()[:16]
    return f"{DEFAULT_STATE}.{token}.json"


def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def changed_code_hashes(root):
    if not root:
        return {}
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if result.returncode != 0:
        return {}
    paths = {}
    parts = result.stdout.split(b"\0")
    index = 0
    while index < len(parts):
        record = parts[index]
        index += 1
        if len(record) < 4:
            continue
        status = record[:2].decode("ascii", "replace")
        path = record[3:].decode("utf-8", "replace")
        if "R" in status or "C" in status:
            if index < len(parts):
                path = parts[index].decode("utf-8", "replace")
                index += 1
        if path.lower().endswith(CODE_EXT):
            paths[path] = file_hash(os.path.join(root, path))
    return paths


def new_state(sid, project_root="", baseline=None):
    baseline = dict(baseline or {})
    return {"session_id": sid, "project_root": project_root, "baseline_code_hashes": baseline, "verified_code_hashes": dict(baseline), "paths": [], "edits_per_path": {}, "last_edit_ts": 0.0, "last_verify_ts": 0.0, "verify_cmds": [], "stop_blocks": 0, "code_pending": []}


def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            st = json.load(f)
        if st.get("session_id") != sid:
            return None
    except FileNotFoundError:
        return new_state(sid)
    except Exception:
        return new_state(sid)
    return st


def save(st):
    try:
        with open(state_path(st.get("session_id", "unknown")), "w", encoding="utf-8") as f:
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
project_root = data.get("cwd") or ti.get("cwd") or os.getcwd()

if event == "SessionStart":
    baseline = changed_code_hashes(project_root)
    save(new_state(sid, project_root, baseline))
    sys.exit(0)

if event == "PreToolUse" and tool in EDIT_TOOLS:
    # Claude Pre 支持 additionalContext 软提醒(Codex 失效那处,这里恢复)。
    st = load(sid)
    if st is None:
        sys.exit(0)
    preview = set(st.get("paths", []))
    if path:
        preview.add(path)
    if len(preview) >= 3:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": f"edited_tracker: 本次改动累计 {len(preview)} 文件(>=3)。CLAUDE.md §1.1 改动确认线:跨多目录/>=3 文件先 1-2 行说明改哪些+目标,确认再动手。"}}, ensure_ascii=False))
    sys.exit(0)

if event == "PostToolUse" and tool in EDIT_TOOLS:
    st = load(sid)
    if st is None:
        sys.exit(0)
    if not st.get("project_root"):
        st["project_root"] = project_root
    now = time.time()
    if path:
        if path not in st["paths"]:
            st["paths"].append(path)
        st["edits_per_path"][path] = st["edits_per_path"].get(path, 0) + 1
        if path.lower().endswith(CODE_EXT) and path not in st.setdefault("code_pending", []):
            st["code_pending"].append(path)
        st["last_edit_ts"] = now
        st["stop_blocks"] = 0
        save(st)
    sys.exit(0)

sys.exit(0)