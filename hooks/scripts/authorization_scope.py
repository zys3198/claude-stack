import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
STATE_DIR = CLAUDE / "authorization"
LOCK = STATE_DIR / ".lock"
SCHEMA_VERSION = 1
LOCK_WAIT_SECONDS = 2.0
LOCK_STALE_SECONDS = 30.0
MAX_TARGETS = 128
MAX_GRANTS = 128
MAX_TEXT = 512
MAX_TASK = 256
MAX_PARAMS = 32


class AuthorizationError(Exception):
    pass


class StateError(AuthorizationError):
    pass


def _text(value, name, limit=MAX_TEXT):
    if not isinstance(value, str):
        raise AuthorizationError(f"{name} 必须是字符串")
    value = value.strip()
    if not value or len(value) > limit:
        raise AuthorizationError(f"{name} 为空或过长")
    if any(ord(char) < 32 for char in value):
        raise AuthorizationError(f"{name} 含控制字符")
    return value


def normalize_session_id(value):
    return _text(value, "session_id")


def normalize_task_id(value):
    return _text(value, "task_id", MAX_TASK)


def normalize_operation_family(value):
    value = _text(value, "operation_family", 128).casefold()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._:-]{0,127}", value):
        raise AuthorizationError("operation_family 格式无效")
    return value


def normalize_target(value):
    value = _text(value, "target")
    return value.replace("\\", "/").casefold()


def normalize_targets(value):
    if not isinstance(value, list) or not value or len(value) > MAX_TARGETS:
        raise AuthorizationError("targets 必须是非空数组")
    targets = {normalize_target(item) for item in value}
    if len(targets) != len(value):
        raise AuthorizationError("targets 含重复项")
    return sorted(targets)


def _safe_param(value, name):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        return _text(value, name)
    if isinstance(value, list) and len(value) <= MAX_TARGETS:
        return [_safe_param(item, name) for item in value]
    raise AuthorizationError(f"{name} 只能保存标量或标量数组")


def normalize_critical_params(value):
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > MAX_PARAMS:
        raise AuthorizationError("critical_params 必须是对象")
    result = {}
    for key, item in value.items():
        key = _text(key, "critical_param_name", 128).casefold()
        if any(word in key for word in ("command", "token", "secret", "password", "api_key", "credential")):
            raise AuthorizationError("critical_params 不得保存命令或凭据字段")
        result[key] = _safe_param(item, f"critical_params.{key}")
    return {key: result[key] for key in sorted(result)}


def normalize_scope(scope):
    if not isinstance(scope, dict):
        raise AuthorizationError("scope 必须是对象")
    allowed = {"targets", "operation_family", "impact_ceiling", "critical_params"}
    unknown = set(scope) - allowed
    if unknown:
        raise AuthorizationError(f"scope 含未知字段: {', '.join(sorted(unknown))}")
    impact = scope.get("impact_ceiling")
    if not isinstance(impact, int) or isinstance(impact, bool) or not 0 <= impact <= 4:
        raise AuthorizationError("impact_ceiling 必须是 0 到 4 的整数")
    return {
        "targets": normalize_targets(scope.get("targets")),
        "operation_family": normalize_operation_family(scope.get("operation_family")),
        "impact_ceiling": impact,
        "critical_params": normalize_critical_params(scope.get("critical_params")),
    }


def _state_path(session_id):
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return STATE_DIR / f"{digest}.json"


def _empty_state(session_id):
    return {
        "version": SCHEMA_VERSION,
        "session_id": session_id,
        "active_task_id": None,
        "updated_at": time.time(),
        "grants": [],
    }


def _validate_state(data, session_id):
    if not isinstance(data, dict):
        raise StateError("授权状态顶层结构无效")
    required = {"version", "session_id", "active_task_id", "updated_at", "grants"}
    if set(data) != required:
        raise StateError("授权状态字段无效")
    if data["version"] != SCHEMA_VERSION:
        raise StateError("授权状态版本不受支持")
    if normalize_session_id(data["session_id"]) != session_id:
        raise StateError("授权状态 session_id 不匹配")
    active = data["active_task_id"]
    if active is not None:
        active = normalize_task_id(active)
    if not isinstance(data["updated_at"], (int, float)):
        raise StateError("授权状态时间无效")
    grants = data["grants"]
    if not isinstance(grants, list) or len(grants) > MAX_GRANTS:
        raise StateError("授权状态 grants 无效")
    checked = []
    ids = set()
    for grant in grants:
        if not isinstance(grant, dict) or set(grant) != {"grant_id", "task_id", "scope", "granted_at"}:
            raise StateError("授权记录字段无效")
        grant_id = _text(grant["grant_id"], "grant_id", 128)
        if grant_id in ids:
            raise StateError("授权记录 grant_id 重复")
        ids.add(grant_id)
        task_id = normalize_task_id(grant["task_id"])
        if not isinstance(grant["granted_at"], (int, float)):
            raise StateError("授权记录时间无效")
        checked.append({
            "grant_id": grant_id,
            "task_id": task_id,
            "scope": normalize_scope(grant["scope"]),
            "granted_at": grant["granted_at"],
        })
    return {
        "version": SCHEMA_VERSION,
        "session_id": session_id,
        "active_task_id": active,
        "updated_at": data["updated_at"],
        "grants": checked,
    }


def load_state(session_id):
    session_id = normalize_session_id(session_id)
    path = _state_path(session_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise StateError(f"授权状态不可读取: {exc}") from exc
    return _validate_state(data, session_id)


def _lock_acquire():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()}-{os.urandom(8).hex()}"
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, token.encode("ascii"))
            finally:
                os.close(fd)
            return token
        except FileExistsError:
            try:
                age = time.time() - LOCK.stat().st_mtime
                if age > LOCK_STALE_SECONDS or age < -LOCK_STALE_SECONDS:
                    LOCK.unlink()
                    continue
            except OSError:
                pass
        except OSError as exc:
            raise AuthorizationError(f"授权状态锁不可用: {exc}") from exc
        if time.monotonic() >= deadline:
            raise AuthorizationError("授权状态锁等待超时")
        time.sleep(0.02)


def _lock_release(token):
    try:
        if LOCK.read_text(encoding="ascii").strip() == token:
            LOCK.unlink()
    except OSError:
        pass


def _atomic_write(path, data):
    temp = path.with_name(f".{path.name}.{os.getpid()}.{os.urandom(4).hex()}.tmp")
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except OSError as exc:
        try:
            temp.unlink()
        except OSError:
            pass
        raise AuthorizationError(f"授权状态写入失败: {exc}") from exc


def _mutate(session_id, callback):
    session_id = normalize_session_id(session_id)
    token = _lock_acquire()
    try:
        state = load_state(session_id) or _empty_state(session_id)
        state = callback(state)
        state["updated_at"] = time.time()
        state = _validate_state(state, session_id)
        _atomic_write(_state_path(session_id), state)
        return state
    finally:
        _lock_release(token)


def set_active_task(session_id, task_id):
    task_id = normalize_task_id(task_id)

    def update(state):
        if state["active_task_id"] != task_id:
            state["active_task_id"] = task_id
            state["grants"] = []
        return state

    return _mutate(session_id, update)


def _grant_id():
    return f"g-{int(time.time() * 1000)}-{os.urandom(6).hex()}"


def grant(session_id, task_id, scope):
    task_id = normalize_task_id(task_id)
    scope = normalize_scope(scope)

    def update(state):
        if state["active_task_id"] != task_id:
            raise AuthorizationError("task_id 不是当前 active task；先切换任务")
        for item in state["grants"]:
            if item["task_id"] == task_id and item["scope"] == scope:
                return state
        if len(state["grants"]) >= MAX_GRANTS:
            raise AuthorizationError("授权记录已达到上限")
        state["grants"].append({
            "grant_id": _grant_id(),
            "task_id": task_id,
            "scope": scope,
            "granted_at": time.time(),
        })
        return state

    state = _mutate(session_id, update)
    for item in reversed(state["grants"]):
        if item["task_id"] == task_id and item["scope"] == scope:
            return item["grant_id"]
    raise AuthorizationError("授权记录写入后无法读回")


def revoke(session_id, grant_id=None, task_id=None):
    if grant_id is not None:
        grant_id = _text(grant_id, "grant_id", 128)
    if task_id is not None:
        task_id = normalize_task_id(task_id)

    revoked = 0

    def update(state):
        nonlocal revoked
        before = len(state["grants"])
        state["grants"] = [
            item for item in state["grants"]
            if not (
                (grant_id is None or item["grant_id"] == grant_id)
                and (task_id is None or item["task_id"] == task_id)
            )
        ]
        revoked = before - len(state["grants"])
        return state

    _mutate(session_id, update)
    return revoked


def cleanup(session_id):
    session_id = normalize_session_id(session_id)

    def update(state):
        state["active_task_id"] = None
        state["grants"] = []
        return state

    _mutate(session_id, update)
    return True


def match(session_id, request_scope):
    try:
        session_id = normalize_session_id(session_id)
        request_scope = normalize_scope(request_scope)
        state = load_state(session_id)
    except AuthorizationError as exc:
        return {"matched": False, "state_error": str(exc)}
    if state is None or not state["active_task_id"]:
        return {"matched": False, "state_error": None}
    for item in state["grants"]:
        if item["task_id"] != state["active_task_id"]:
            continue
        granted = item["scope"]
        if granted["targets"] != request_scope["targets"]:
            continue
        if granted["operation_family"] != request_scope["operation_family"]:
            continue
        if granted["critical_params"] != request_scope["critical_params"]:
            continue
        if granted["impact_ceiling"] < request_scope["impact_ceiling"]:
            continue
        return {"matched": True, "state_error": None, "grant_id": item["grant_id"]}
    return {"matched": False, "state_error": None}


def _scope_from_json(raw):
    try:
        return json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise AuthorizationError(f"scope JSON 无效: {exc}") from exc


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="管理当前 Claude 会话的精确授权范围")
    sub = parser.add_subparsers(dest="action", required=True)

    task = sub.add_parser("set-task")
    task.add_argument("--session-id", required=True)
    task.add_argument("--task-id", required=True)

    add = sub.add_parser("grant")
    add.add_argument("--session-id", required=True)
    add.add_argument("--task-id", required=True)
    add.add_argument("--scope-json", required=True)

    remove = sub.add_parser("revoke")
    remove.add_argument("--session-id", required=True)
    remove.add_argument("--grant-id")
    remove.add_argument("--task-id")

    clear = sub.add_parser("cleanup")
    clear.add_argument("--session-id", required=True)

    probe = sub.add_parser("match")
    probe.add_argument("--session-id", required=True)
    probe.add_argument("--scope-json", required=True)

    args = parser.parse_args(argv)
    try:
        if args.action == "set-task":
            state = set_active_task(args.session_id, args.task_id)
            print(json.dumps({"active_task_id": state["active_task_id"]}, ensure_ascii=False))
        elif args.action == "grant":
            grant_id = grant(args.session_id, args.task_id, _scope_from_json(args.scope_json))
            print(json.dumps({"grant_id": grant_id}, ensure_ascii=False))
        elif args.action == "revoke":
            print(json.dumps({"revoked": revoke(args.session_id, args.grant_id, args.task_id)}))
        elif args.action == "cleanup":
            cleanup(args.session_id)
            print(json.dumps({"cleaned": True}))
        else:
            print(json.dumps(match(args.session_id, _scope_from_json(args.scope_json)), ensure_ascii=False))
        return 0
    except AuthorizationError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
