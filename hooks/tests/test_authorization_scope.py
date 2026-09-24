import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "authorization_scope.py"
spec = importlib.util.spec_from_file_location("authorization_scope", MODULE)
auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth)


SCOPE = {
    "targets": ["deploy-nginx-1"],
    "operation_family": "docker-exclusive",
    "impact_ceiling": 3,
    "critical_params": {"verb": "restart"},
}


with tempfile.TemporaryDirectory() as temp:
    auth.STATE_DIR = Path(temp)
    auth.LOCK = auth.STATE_DIR / ".lock"
    session = "session-test"
    auth.set_active_task(session, "task-one")
    grant_id = auth.grant(session, "task-one", SCOPE)
    assert grant_id.startswith("g-"), grant_id
    assert auth.match(session, SCOPE)["matched"] is True
    assert auth.match(session, {**SCOPE, "impact_ceiling": 2})["matched"] is True
    assert auth.match(session, {**SCOPE, "targets": ["deploy-nginx-2"]})["matched"] is False
    assert auth.match(session, {**SCOPE, "impact_ceiling": 4})["matched"] is False
    assert auth.revoke(session, grant_id=grant_id) == 1
    assert auth.match(session, SCOPE)["matched"] is False

    auth.grant(session, "task-one", SCOPE)
    auth.set_active_task(session, "task-two")
    assert auth.match(session, SCOPE)["matched"] is False
    auth.cleanup(session)
    assert auth.match(session, SCOPE)["matched"] is False

    path = auth._state_path(session)
    path.write_text("{broken", encoding="utf-8")
    result = auth.match(session, SCOPE)
    assert result["matched"] is False
    assert result["state_error"]

for bad in (
    {"command": "git push"},
    {"token": "secret"},
):
    try:
        auth.normalize_critical_params(bad)
    except auth.AuthorizationError:
        pass
    else:
        raise AssertionError(f"敏感字段未拒绝: {bad}")

print("PASS authorization scope")
