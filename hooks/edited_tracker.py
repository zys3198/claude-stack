import sys, json, time, os, hashlib, subprocess, re

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


def prune_old_states(sid, keep=3):
    # SessionStart 时清理历史会话 state 快照，只留最近 keep 份防堆积。
    if STATE_OVERRIDE:
        return
    try:
        d = os.path.dirname(DEFAULT_STATE)
        mine = os.path.basename(state_path(sid))
        files = [f for f in os.listdir(d) if f.startswith("edited_state.json.") and f.endswith(".json")]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)), reverse=True)
        for f in files[keep:]:
            if f != mine:
                try:
                    os.remove(os.path.join(d, f))
                except OSError:
                    pass
    except OSError:
        pass


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


def normalize_path(path, root=""):
    path = str(path).strip()
    if not path:
        return ""
    if root and not os.path.isabs(path):
        path = os.path.join(root, path)
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


def patch_paths(patch):
    if not isinstance(patch, str):
        return []
    paths = []
    for line in patch.splitlines():
        match = re.match(r"\*\*\* (?:Update|Add|Delete) File:\s*(.+?)\s*$", line)
        if match:
            paths.append(match.group(1))
            continue
        if line.startswith(("+++ ", "--- ")):
            path = line[4:].split("\t", 1)[0].strip()
            if path != "/dev/null":
                paths.append(path[2:] if path[:2] in {"a/", "b/"} else path)
    return paths


def edit_paths(tool, tool_input, root=""):
    if tool == "MultiEdit":
        raw_paths = [
            edit.get("file_path")
            for edit in tool_input.get("edits", [])
            if isinstance(edit, dict) and edit.get("file_path")
        ]
    elif tool == "apply_patch":
        raw_paths = patch_paths(tool_input.get("patch") or tool_input.get("input") or "")
    else:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        raw_paths = [path] if path else []
    paths = [normalize_path(path, root) for path in raw_paths]
    return list(dict.fromkeys(path for path in paths if path))


def new_state(sid, project_root="", baseline=None):
    baseline = dict(baseline or {})
    return {"session_id": sid, "project_root": project_root, "baseline_code_hashes": baseline, "verified_code_hashes": dict(baseline), "paths": [], "edits_per_path": {}, "last_edit_ts": 0.0, "last_verify_ts": 0.0, "verify_cmds": [], "stop_blocks": 0, "code_pending": []}


def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            st = json.load(f)
        if not isinstance(st, dict) or st.get("session_id") != sid:
            return None
    except FileNotFoundError:
        return new_state(sid)
    except Exception:
        return None
    return st


def save(st):
    path = state_path(st.get("session_id", "unknown"))
    lock_path = f"{path}.lock"
    deadline = time.monotonic() + 1.0
    locked = False
    temp_path = f"{path}.{os.getpid()}.{time.time_ns()}.tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        while time.monotonic() < deadline:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                locked = True
                break
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(lock_path) > 10:
                        os.unlink(lock_path)
                        continue
                except OSError:
                    continue
                time.sleep(0.02)
        if not locked:
            return

        disk = {}
        try:
            with open(path, encoding="utf-8") as f:
                candidate = json.load(f)
            if isinstance(candidate, dict) and candidate.get("session_id") == st.get("session_id"):
                disk = candidate
        except Exception:
            pass
        merged = {**disk, **st}
        for key in ("paths", "code_pending", "verify_cmds"):
            values = list(disk.get(key, [])) if isinstance(disk.get(key), list) else []
            for value in st.get(key, []):
                if value not in values:
                    values.append(value)
            merged[key] = values
        edits = dict(disk.get("edits_per_path", {})) if isinstance(disk.get("edits_per_path"), dict) else {}
        if isinstance(st.get("edits_per_path"), dict):
            for key, value in st["edits_per_path"].items():
                edits[key] = max(int(edits.get(key, 0)), int(value))
        merged["edits_per_path"] = edits
        for key in ("last_edit_ts", "last_verify_ts"):
            merged[key] = max(float(disk.get(key, 0)), float(st.get(key, 0)))
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(merged, f)
        os.replace(temp_path, path)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    finally:
        if locked:
            try:
                os.unlink(lock_path)
            except OSError:
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
project_root = data.get("cwd") or ti.get("cwd") or os.getcwd()
paths = edit_paths(tool, ti, project_root)

if event == "SessionStart":
    state_file = state_path(sid)
    st = load(sid) if os.path.exists(state_file) else None
    if st is None or st.get("session_id") != sid or not st.get("project_root"):
        baseline = changed_code_hashes(project_root)
        st = new_state(sid, project_root, baseline)
        save(st)
    else:
        st["project_root"] = st.get("project_root") or project_root
        save(st)
    prune_old_states(sid)
    sys.exit(0)

if event == "PreToolUse" and tool in EDIT_TOOLS:
    # Claude Pre 支持 additionalContext 软提醒(Codex 失效那处,这里恢复)。
    st = load(sid)
    if st is None:
        sys.exit(0)
    preview = set(st.get("paths", []))
    preview.update(paths)
    directories = {os.path.dirname(path) for path in preview}
    if len(preview) >= 3 or len(directories) >= 2:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": f"edited_tracker: 本次改动累计 {len(preview)} 文件，涉及 {len(directories)} 个目录。CLAUDE.md §1.1 改动确认线:跨多目录或 >=3 文件先 1-2 行说明改哪些+目标,确认再动手。"}}, ensure_ascii=False))
    sys.exit(0)

if event == "PostToolUse" and tool in EDIT_TOOLS:
    st = load(sid)
    if st is None:
        sys.exit(0)
    if not st.get("project_root"):
        st["project_root"] = project_root
    now = time.time()
    if paths:
        for path in paths:
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