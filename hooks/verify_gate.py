import sys, json, os, hashlib, subprocess, time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_STATE = "C:/Users/zys31/.claude/hooks/edited_state.json"
STATE_OVERRIDE = os.environ.get("CLAUDE_HOOK_STATE")
MAX_BLOCKS = 3
CODE_EXT = (".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".kts", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".cs", ".rb", ".php", ".swift", ".m", ".mm", ".scala", ".sc", ".vue", ".svelte", ".ex", ".exs", ".dart", ".lua", ".clj", ".cljs", ".cljc", ".hs", ".ml", ".mli", ".fs", ".fsx", ".nim", ".zig", ".v", ".sv", ".jl", ".pl", ".pm", ".r", ".R")


def state_path(sid):
    if STATE_OVERRIDE:
        return STATE_OVERRIDE
    token = hashlib.sha256(sid.encode("utf-8")).hexdigest()[:16]
    return f"{DEFAULT_STATE}.{token}.json"


def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            st = json.load(f)
    except FileNotFoundError:
        return None, "missing"
    except Exception:
        return None, "invalid"
    if not isinstance(st, dict):
        return None, "invalid"
    if st.get("session_id") != sid:
        return None, "session_mismatch"
    return st, None


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
        verified = dict(disk.get("verified_code_hashes", {})) if isinstance(disk.get("verified_code_hashes"), dict) else {}
        if isinstance(st.get("verified_code_hashes"), dict):
            verified.update(st["verified_code_hashes"])
        merged["verified_code_hashes"] = verified
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


def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def changed_code_hashes(root):
    if not root:
        return None
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
        return None
    if result.returncode != 0:
        return None
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
            digest = file_hash(os.path.join(root, path))
            if digest is not None:
                paths[path] = digest
    return paths


def refresh_code_pending(st, data):
    tool_input = data.get("tool_input") or {}
    root = st.get("project_root") or data.get("cwd") or tool_input.get("cwd")
    verified = st.get("verified_code_hashes")
    if not root or not isinstance(verified, dict):
        return False
    current = changed_code_hashes(root)
    if current is None:
        return False
    pending = st.setdefault("code_pending", [])
    if not current:
        return True
    discovered = False
    for path, digest in current.items():
        if path not in verified or verified[path] != digest:
            if path not in pending:
                pending.append(path)
                discovered = True
    if discovered:
        st["last_edit_ts"] = time.time()
    return True


try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    if _i < 0:
        raise ValueError("hook input has no JSON object")
    data = json.loads(_raw[_i:])
    if not isinstance(data, dict):
        raise ValueError("hook input is not an object")
except Exception:
    reason = "verify_gate BLOCKED: Hook 输入无效，无法确认 session 或工作区状态，拒绝 fail-open。"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(2)

sid = data.get("session_id", "unknown")
st, state_error = load(sid)
if state_error == "invalid":
    reason = "verify_gate BLOCKED: 状态文件损坏，拒绝 fail-open；请重新启动当前 session 以建立隔离状态。"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(2)
if state_error == "session_mismatch":
    reason = "verify_gate BLOCKED: 状态文件属于其他 session，拒绝 fail-open；请重新启动当前 session 以建立隔离状态。"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(2)
if st is None:
    sys.exit(0)

if not refresh_code_pending(st, data):
    reason = "verify_gate BLOCKED: 无法确认 Git 工作区状态，拒绝 fail-open；请检查项目路径、Git 可用性或超时设置后重试。"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(2)
code_paths = st.get("code_pending", [])
if not code_paths:
    save(st)
    sys.exit(0)

last_edit = float(st.get("last_edit_ts", 0))
last_verify = float(st.get("last_verify_ts", 0))
if last_verify >= last_edit:
    st["code_pending"] = []
    st["stop_blocks"] = 0
    save(st)
    sys.exit(0)

blocks = int(st.get("stop_blocks", 0)) + 1
if blocks > MAX_BLOCKS:
    st["stop_blocks"] = MAX_BLOCKS
    save(st)
    reason = "verify_gate BLOCKED: 检测到代码改动但未跑成功验证，请先执行验证命令并确认退出成功。"
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(2)

st["stop_blocks"] = blocks
save(st)

verify_cmds = st.get("verify_cmds", [])
hint = "、".join(verify_cmds[-5:]) if verify_cmds else "无"
warning = (f"verify_gate WARNING ({blocks}/{MAX_BLOCKS}+): 检测到代码改动但未跑成功验证。\n  改动文件({len(code_paths)}): {', '.join(code_paths[:5])}\n  CLAUDE.md §1.3: 改动后跑 lint + test + 编译(tsc/go build/pytest...).\n  最近成功验证命令: {hint}\n  -> 建议跑验证命令并确认退出成功。")
print(warning, file=sys.stderr)
sys.exit(0)
