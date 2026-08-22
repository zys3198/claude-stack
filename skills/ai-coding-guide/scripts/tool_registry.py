#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Dict, Optional

from agent_registry import MANIFEST as AGENT_MANIFEST
from runtime_registry import load_runtime_adapters


SKILL_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = SKILL_ROOT / "config" / "tools-contract.json"
ADAPTERS_PATH = SKILL_ROOT / "config" / "runtime-manifest.json"
HOST_TOOL_NAMES = (
    "Agent",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
    "read",
    "grep",
    "find",
    "ls",
    "write",
    "edit",
    "bash",
)
ROLE_IDS = {role["id"] for role in AGENT_MANIFEST["roles"]}
NEUTRAL_TOOL_IDS = {"read", "search", "write", "execute", "dispatch"}


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"缺少 tool source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(values, label: str, allow_empty: bool = False) -> set:
    if (
        not isinstance(values, list)
        or (not allow_empty and not values)
        or not all(isinstance(value, str) and value for value in values)
        or len(values) != len(set(values))
    ):
        raise ValueError(f"{label} 无效")
    return set(values)


def _validate_tool_contract(data: dict) -> dict:
    fields = {"version", "tools", "role_requirements", "unsupported_rules", "fallbacks"}
    if not isinstance(data, dict) or set(data) != fields or data.get("version") != "1.0":
        raise ValueError("tool contract 不完整、字段无效或版本不支持")
    serialized = json.dumps(data, ensure_ascii=False)
    if any(
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])",
            serialized,
        )
        for name in HOST_TOOL_NAMES
        if name not in NEUTRAL_TOOL_IDS
    ):
        raise ValueError("tool contract 包含宿主工具名")

    tools = data["tools"]
    if not isinstance(tools, list) or not tools:
        raise ValueError("tool contract tools 必须是非空数组")
    tool_ids = set()
    for tool in tools:
        if not isinstance(tool, dict) or set(tool) != {"id", "description", "binding_required"}:
            raise ValueError("tool contract tool 定义无效")
        tool_id = tool["id"]
        if not isinstance(tool_id, str) or not tool_id or tool_id in tool_ids:
            raise ValueError(f"tool contract tool ID 无效或重复: {tool_id}")
        if not isinstance(tool["description"], str) or not tool["description"]:
            raise ValueError(f"tool contract tool description 无效: {tool_id}")
        if not isinstance(tool["binding_required"], bool):
            raise ValueError(f"tool contract binding_required 无效: {tool_id}")
        tool_ids.add(tool_id)

    requirements = data["role_requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("tool contract role_requirements 必须是非空数组")
    requirement_roles = set()
    for requirement in requirements:
        required_fields = {"role", "required", "optional"}
        if not isinstance(requirement, dict) or set(requirement) != required_fields:
            raise ValueError("tool contract role requirement 定义无效")
        role = requirement["role"]
        if role not in ROLE_IDS or role in requirement_roles:
            raise ValueError(f"tool contract role 无效或重复: {role}")
        required = _strings(requirement["required"], f"tool contract required: {role}")
        optional = _strings(
            requirement["optional"], f"tool contract optional: {role}", allow_empty=True
        )
        if not required.issubset(tool_ids) or not optional.issubset(tool_ids):
            raise ValueError(f"tool contract role 引用未知工具: {role}")
        if required & optional:
            raise ValueError(f"tool contract role 同时声明 required/optional: {role}")
        requirement_roles.add(role)
    if requirement_roles != ROLE_IDS:
        raise ValueError("tool contract role_requirements 未完整覆盖角色")

    rules = data["unsupported_rules"]
    if not isinstance(rules, list) or not rules:
        raise ValueError("tool contract unsupported_rules 必须是非空数组")
    rule_ids = set()
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {"id", "when", "action"}:
            raise ValueError("tool contract unsupported rule 定义无效")
        rule_id = rule["id"]
        if not isinstance(rule_id, str) or not rule_id or rule_id in rule_ids:
            raise ValueError(f"tool contract unsupported rule ID 无效或重复: {rule_id}")
        if not isinstance(rule["when"], str) or not rule["when"]:
            raise ValueError(f"tool contract unsupported rule when 无效: {rule_id}")
        if rule["action"] not in {"reject", "report", "fallback"}:
            raise ValueError(f"tool contract unsupported rule action 无效: {rule_id}")
        rule_ids.add(rule_id)

    fallbacks = data["fallbacks"]
    if not isinstance(fallbacks, list) or not fallbacks:
        raise ValueError("tool contract fallbacks 必须是非空数组")
    fallback_ids = set()
    for fallback in fallbacks:
        fields = {"id", "from_mode", "to_mode", "when", "reason"}
        if not isinstance(fallback, dict) or set(fallback) != fields:
            raise ValueError("tool contract fallback 定义无效")
        fallback_id = fallback["id"]
        if not isinstance(fallback_id, str) or not fallback_id or fallback_id in fallback_ids:
            raise ValueError(f"tool contract fallback ID 无效或重复: {fallback_id}")
        if fallback["from_mode"] not in {"isolated", "single-context"}:
            raise ValueError(f"tool contract fallback from_mode 无效: {fallback_id}")
        if fallback["to_mode"] not in {"isolated", "single-context"}:
            raise ValueError(f"tool contract fallback to_mode 无效: {fallback_id}")
        if fallback["from_mode"] == fallback["to_mode"]:
            raise ValueError(f"tool contract fallback 模式未变化: {fallback_id}")
        if not all(isinstance(fallback[key], str) and fallback[key] for key in ("when", "reason")):
            raise ValueError(f"tool contract fallback 文本无效: {fallback_id}")
        fallback_ids.add(fallback_id)
    return data


def load_tool_contract(path: Optional[Path] = None) -> dict:
    source = path if path is not None else CONTRACT_PATH
    return _validate_tool_contract(_load_json(source))


def _validate_tool_adapter(data: dict, contract: dict, runtime_id: str) -> dict:
    required_fields = {
        "version",
        "id",
        "host_tool_names",
        "tool_bindings",
        "unsupported_capabilities",
        "fallbacks",
    }
    optional_fields = {
        "compatibility",
        "dispatch_tool",
        "topology",
        "stage_executor",
        "research_executor",
        "required_tools",
        "installation",
        "host_agents",
    }
    if (
        not isinstance(data, dict)
        or not required_fields.issubset(data)
        or set(data) - required_fields - optional_fields
        or data.get("version") != "1.0"
    ):
        raise ValueError(f"tool adapter source 不完整、字段无效或包含未知字段: {runtime_id}")
    if data["id"] != runtime_id:
        raise ValueError(f"tool adapter source ID 不一致: {runtime_id}")
    host_tool_names = _strings(
        data["host_tool_names"], f"tool adapter host_tool_names: {runtime_id}"
    )
    tool_ids = {tool["id"] for tool in contract["tools"]}
    bindings = data["tool_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != tool_ids:
        raise ValueError(f"tool adapter tool_bindings 未完整覆盖: {runtime_id}")
    unsupported = _strings(
        data["unsupported_capabilities"],
        f"tool adapter unsupported_capabilities: {runtime_id}",
        allow_empty=True,
    )
    if not unsupported.issubset(tool_ids):
        raise ValueError(f"tool adapter 声明未知 unsupported capability: {runtime_id}")
    binding_required = {
        tool["id"] for tool in contract["tools"] if tool["binding_required"]
    }
    for tool_id, values in bindings.items():
        bound = _strings(values, f"tool adapter binding: {runtime_id}/{tool_id}", allow_empty=True)
        if not bound.issubset(host_tool_names):
            raise ValueError(f"tool adapter binding 未声明宿主工具: {runtime_id}/{tool_id}")
        if tool_id in unsupported and bound:
            raise ValueError(f"tool adapter 同时支持和拒绝 capability: {runtime_id}/{tool_id}")
        if tool_id in binding_required and tool_id not in unsupported and not bound:
            raise ValueError(f"tool adapter 缺少 required capability binding: {runtime_id}/{tool_id}")

    fallback_ids = {fallback["id"] for fallback in contract["fallbacks"]}
    fallbacks = data["fallbacks"]
    if not isinstance(fallbacks, list):
        raise ValueError(f"tool adapter fallbacks 无效: {runtime_id}")
    seen = set()
    for fallback in fallbacks:
        if not isinstance(fallback, dict) or set(fallback) != {"rule_id", "reason"}:
            raise ValueError(f"tool adapter fallback 定义无效: {runtime_id}")
        rule_id = fallback["rule_id"]
        if rule_id not in fallback_ids or rule_id in seen:
            raise ValueError(f"tool adapter fallback rule 未知或重复: {runtime_id}/{rule_id}")
        if not isinstance(fallback["reason"], str) or not fallback["reason"]:
            raise ValueError(f"tool adapter fallback reason 无效: {runtime_id}/{rule_id}")
        seen.add(rule_id)
    return data


def load_tool_adapters(
    contract: Optional[dict] = None,
    path: Optional[Path] = None,
) -> Dict[str, dict]:
    catalog_path = (path if path is not None else ADAPTERS_PATH).resolve()
    contract = load_tool_contract() if contract is None else _validate_tool_contract(contract)
    runtimes = load_runtime_adapters(path=catalog_path)
    root = catalog_path.parent.parent.parent.resolve()
    result = {}
    for runtime_id, runtime in runtimes.items():
        source = runtime.get("source")
        if not isinstance(source, str) or not source:
            raise ValueError(f"runtime adapter 缺少 tool source: {runtime_id}")
        source_path = (catalog_path.parent / source).resolve()
        if root not in source_path.parents or not source_path.is_file():
            raise ValueError(f"tool adapter source 缺失或越界: {runtime_id}")
        result[runtime_id] = _validate_tool_adapter(
            _load_json(source_path), contract, runtime_id
        )
    return result


TOOL_CONTRACT = load_tool_contract()
TOOL_ADAPTERS = load_tool_adapters(TOOL_CONTRACT)
