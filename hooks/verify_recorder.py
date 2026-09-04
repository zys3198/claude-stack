import sys, json, re, time, os, hashlib

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"
STATE_OVERRIDE = os.environ.get("CLAUDE_HOOK_STATE")

VERIFY_PATTERNS = [
    r"\bpytest\b", r"\bpython\S*\s+-m\s+unittest\b", r"\bnosetests\b",
    r"\bpy_compile\b", r"\bpython\S*\s+-m\s+py_compile\b",
    r"\bnx\s+test\b", r"\bjest\b", r"\bvitest\b", r"\bmocha\b", r"\bkarma\b",
    r"(?<![\w-])\btsc\b", r"\bnpm\s+(?:run\s+)?(?:test|build|lint|check|typecheck)\b",
    r"\byarn\s+(?:test|build|lint|typecheck)\b", r"\bpnpm\s+(?:test|build|lint|typecheck)\b",
    r"\bbun\s+(?:test|run\s+build)\b",
    r"\bnode\s+(?:--check|--test)\b",
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
OUTPUT_PREFIX = re.compile(r"^\s*(?:echo|printf|print|write-output|write-host)\b", re.IGNORECASE)
SEARCH_PREFIX = re.compile(r"^\s*(?:grep|rg|ripgrep|findstr|select-string)\b", re.IGNORECASE)
INLINE_PREFIX = re.compile(r"^\s*(?:python\S*|py|ruby|powershell|pwsh|node)\s+-(?:c|e|command)\b", re.IGNORECASE)
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\r?\n")


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
        import subprocess
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
        if path.lower().endswith((".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".kts", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".cs", ".rb", ".php", ".swift", ".m", ".mm", ".scala", ".sc", ".vue", ".svelte", ".ex", ".exs", ".dart", ".lua", ".clj", ".cljs", ".cljc", ".hs", ".ml", ".mli", ".fs", ".fsx", ".nim", ".zig", ".v", ".sv", ".jl", ".pl", ".pm", ".r", ".R")):
            paths[path] = file_hash(os.path.join(root, path))
    return paths


def strip_shell_comment(segment):
    quote = ""
    index = 0
    while index < len(segment):
        char = segment[index]
        if quote == "'":
            if char == "'":
                quote = ""
            index += 1
            continue
        if quote == '"':
            if char == "\\":
                index += 2
                continue
            if char == '"':
                quote = ""
            index += 1
            continue
        if char in "'\"":
            quote = char
        elif char in "\\`":
            index += 2
            continue
        elif char == "#":
            return segment[:index]
        index += 1
    return segment


def find_match(command):
    for segment in SEGMENT_SPLIT.split(command):
        segment = strip_shell_comment(segment)
        stripped = segment.strip()
        if not stripped or OUTPUT_PREFIX.match(stripped) or SEARCH_PREFIX.match(stripped):
            continue
        if INLINE_PREFIX.match(stripped):
            continue
        for pattern in COMPILED:
            match = pattern.search(segment)
            if match:
                return match.group(0).strip().replace("\"", "").replace("'", "")
    return None

def new_state(sid):
    return {"session_id": sid, "paths": [], "edits_per_path": {}, "last_edit_ts": 0.0, "last_verify_ts": 0.0, "verify_cmds": [], "stop_blocks": 0, "code_pending": []}

def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            st = json.load(f)
        if st.get("session_id") != sid:
            return None
    except FileNotFoundError:
        st = new_state(sid)
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
            merged[key] = values[-20:] if key == "verify_cmds" else values
        for key in ("last_edit_ts", "last_verify_ts"):
            merged[key] = max(float(disk.get(key, 0)), float(st.get(key, 0)))
        edits = dict(disk.get("edits_per_path", {})) if isinstance(disk.get("edits_per_path"), dict) else {}
        if isinstance(st.get("edits_per_path"), dict):
            for key, value in st["edits_per_path"].items():
                edits[key] = max(int(edits.get(key, 0)), int(value))
        merged["edits_per_path"] = edits
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

def succeeded(data):
    response = data.get("tool_response")
    if not isinstance(response, dict):
        return False
    if response.get("interrupted") is True:
        return False
    exit_code = response.get("exit_code", response.get("exitCode"))
    if exit_code is not None:
        return exit_code in (0, "0")
    if "success" in response:
        return response["success"] is True
    if "is_error" in response:
        return response["is_error"] is False
    return (
        response.get("interrupted") is False
        and isinstance(response.get("stdout"), str)
        and response.get("stderr") == ""
    )

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
matched = find_match(cmd)
if not matched:
    sys.exit(0)

if not succeeded(data):
    sys.exit(0)

sid = data.get("session_id", "unknown")
st = load(sid)
if st is None:
    sys.exit(0)
st["last_verify_ts"] = time.time()
st["stop_blocks"] = 0
root = data.get("cwd") or data.get("tool_input", {}).get("cwd") or st.get("project_root")
if root:
    verified = changed_code_hashes(root)
    if verified:
        st["verified_code_hashes"] = verified
cmds = st.get("verify_cmds", [])
if matched not in cmds:
    cmds.append(matched)
    st["verify_cmds"] = cmds[-20:]
save(st)
sys.exit(0)