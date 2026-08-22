#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, List


SKILL_ROOT = Path(__file__).resolve().parent.parent
AGENT_ROOT = SKILL_ROOT / "agents"
MANIFEST_PATH = AGENT_ROOT / "manifest.json"


def load_manifest() -> dict:
    adapter = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if adapter.get("version") != "1.0":
        raise ValueError(f"不支持的 Agent adapter 清单版本: {adapter.get('version')}")
    core = adapter
    if not isinstance(core.get("version"), str) or not core["version"]:
        raise ValueError("逻辑角色清单缺少 version")
    roles = core.get("roles")
    adapters = adapter.get("role_adapters")
    if not isinstance(roles, list) or not roles:
        raise ValueError("逻辑角色清单 roles 必须是非空数组")
    if not isinstance(adapters, list) or not adapters:
        raise ValueError("Agent adapter 清单 role_adapters 必须是非空数组")
    adapter_by_id = {}
    allowed_adapter_fields = {"id", "file", "input_artifacts"}
    for item in adapters:
        if (
            not isinstance(item, dict)
            or not {"id", "file"}.issubset(item)
            or set(item) - allowed_adapter_fields
        ):
            raise ValueError("Agent adapter 清单正文映射字段无效")
        if item["id"] in adapter_by_id:
            raise ValueError(f"Agent adapter ID 重复: {item['id']}")
        if "input_artifacts" in item and not isinstance(item["input_artifacts"], list):
            raise ValueError(f"Agent adapter 产物输入无效: {item['id']}")
        adapter_by_id[item["id"]] = {
            "id": item["id"],
            "file": item["file"],
            **({"input_artifacts": item["input_artifacts"]} if "input_artifacts" in item else {}),
        }
    role_ids = {role.get("id") for role in roles if isinstance(role, dict)}
    if len(role_ids) != len(roles) or None in role_ids:
        raise ValueError("逻辑角色 ID 缺失或重复")
    if role_ids != set(adapter_by_id):
        raise ValueError("逻辑角色与 adapter 正文映射不一致")
    merged_roles = [{**role, **adapter_by_id[role["id"]]} for role in roles]

    ids = set()
    stages = set()
    for role in merged_roles:
        required = {"id", "kind", "file", "description", "access"}
        if not required.issubset(role):
            raise ValueError("Agent 清单存在不完整的角色定义")
        role_id = role["id"]
        if role_id in ids:
            raise ValueError(f"Agent ID 重复: {role_id}")
        ids.add(role_id)
        if role["kind"] not in {"stage", "helper"}:
            raise ValueError(f"Agent 类型无效: {role_id}")
        if role["access"] not in {"read", "report", "write", "test-write"}:
            raise ValueError(f"Agent access 无效: {role_id}")
        if role["kind"] == "stage":
            stage = role.get("stage")
            if not stage or stage in stages:
                raise ValueError(f"阶段缺失或重复: {stage}")
            stages.add(stage)
            if not isinstance(role.get("input_stages"), list) or not isinstance(
                role.get("workspace_evidence"), list
            ):
                raise ValueError(f"阶段角色缺少输入定义: {role_id}")
            if not isinstance(role.get("input_artifacts"), list):
                raise ValueError(f"阶段角色缺少精确产物输入定义: {role_id}")
            if role.get("execution", "agent") not in {"agent", "coordinator"}:
                raise ValueError(f"阶段 execution 无效: {role_id}")
        body = AGENT_ROOT / role["file"]
        if not body.is_file() or not body.read_text(encoding="utf-8").strip():
            raise ValueError(f"Agent 正文不存在或为空: {role['file']}")
    return {"version": core["version"], "roles": merged_roles}


MANIFEST = load_manifest()
ROLES: Dict[str, dict] = {item["id"]: item for item in MANIFEST["roles"]}
STAGE_ROLES: Dict[str, str] = {
    item["stage"]: item["id"] for item in MANIFEST["roles"] if item["kind"] == "stage"
}
STAGE_EXECUTION: Dict[str, str] = {
    item["stage"]: item.get("execution", "agent")
    for item in MANIFEST["roles"]
    if item["kind"] == "stage"
}
HELPER_ROLES = {item["id"] for item in MANIFEST["roles"] if item["kind"] == "helper"}


def role_body(role_id: str) -> str:
    role = ROLES[role_id]
    return (AGENT_ROOT / role["file"]).read_text(encoding="utf-8").strip()


def roles() -> List[dict]:
    return list(MANIFEST["roles"])
