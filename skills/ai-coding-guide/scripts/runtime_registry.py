#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Optional


SKILL_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = SKILL_ROOT / "config" / "runtime-contract.json"
ADAPTERS_PATH = SKILL_ROOT / "config" / "runtime-manifest.json"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"缺少 runtime source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _string_set(values, label: str, allow_empty: bool = False) -> set:
    if (
        not isinstance(values, list)
        or (not allow_empty and not values)
        or not all(isinstance(value, str) and value for value in values)
        or len(values) != len(set(values))
    ):
        raise ValueError(f"{label} 无效")
    return set(values)


def _validate_runtime_contract(data: dict) -> dict:
    fields = {
        "version",
        "lifecycle",
        "access_levels",
        "execution_modes",
        "capabilities",
        "adapter_rules",
    }
    if not isinstance(data, dict) or set(data) != fields or data.get("version") != "1.0":
        raise ValueError("runtime contract 不完整、字段无效或版本不支持")
    lifecycle = data["lifecycle"]
    lifecycle_fields = {"required_operations", "optional_operations", "executor_id"}
    if not isinstance(lifecycle, dict) or set(lifecycle) != lifecycle_fields:
        raise ValueError("runtime lifecycle contract 无效")
    required_operations = _string_set(
        lifecycle["required_operations"], "runtime required lifecycle operations"
    )
    optional_operations = _string_set(
        lifecycle["optional_operations"],
        "runtime optional lifecycle operations",
        allow_empty=True,
    )
    if required_operations & optional_operations or lifecycle["executor_id"] != "host-issued":
        raise ValueError("runtime lifecycle operations 无效")
    for key in ("access_levels", "execution_modes", "capabilities"):
        _string_set(data[key], f"runtime contract {key}")
    _string_set(data["adapter_rules"], "runtime contract adapter_rules")
    return data


def load_runtime_contract(path: Optional[Path] = None) -> dict:
    source = path if path is not None else CONTRACT_PATH
    return _validate_runtime_contract(_load_json(source))


def _validate_runtime_source(data: dict, runtime_id: str, modes: set) -> None:
    if not isinstance(data, dict) or data.get("id") != runtime_id:
        raise ValueError(f"runtime adapter source ID 不一致: {runtime_id}")
    if data.get("version") != "1.0":
        raise ValueError(f"runtime adapter source 不完整: {runtime_id}")
    if "isolated" not in modes:
        return
    required = {
        "dispatch_tool",
        "topology",
        "stage_executor",
        "research_executor",
        "required_tools",
    }
    if not required.issubset(data) or not all(
        isinstance(data[key], str) and data[key]
        for key in required - {"required_tools"}
    ):
        raise ValueError(f"runtime adapter source 不完整: {runtime_id}")
    if data["topology"] not in {"spawn", "team"}:
        raise ValueError(f"runtime adapter source 拓扑无效: {runtime_id}")
    _string_set(data["required_tools"], f"runtime adapter source required_tools: {runtime_id}")


def load_runtime_adapters(
    contract: Optional[dict] = None,
    path: Optional[Path] = None,
) -> Dict[str, dict]:
    catalog_path = (path if path is not None else ADAPTERS_PATH).resolve()
    data = _load_json(catalog_path)
    catalog_fields = {"version", "source", "runtimes"}
    if (
        not isinstance(data, dict)
        or set(data) != catalog_fields
        or data.get("version") != "1.0"
        or data.get("source") != "runtime-contract.json"
    ):
        raise ValueError("runtime adapter catalog 不完整或字段无效")
    declared_contract = load_runtime_contract((catalog_path.parent / data["source"]).resolve())
    if contract is None:
        contract = declared_contract
    else:
        contract = _validate_runtime_contract(contract)
        if contract != declared_contract:
            raise ValueError("runtime adapter catalog contract 与声明 source 不一致")
    runtimes = data.get("runtimes")
    if not isinstance(runtimes, list) or not runtimes:
        raise ValueError("runtime adapter catalog 必须是非空数组")

    root = catalog_path.parent.parent.parent.resolve()
    required_operations = set(contract["lifecycle"]["required_operations"])
    all_operations = required_operations | set(contract["lifecycle"]["optional_operations"])
    contract_access = set(contract["access_levels"])
    contract_modes = set(contract["execution_modes"])
    contract_capabilities = set(contract["capabilities"])
    runtime_fields = {"id", "status", "source", "package", "verified_on", "capabilities"}
    capability_fields = {
        "lifecycle_operations",
        "unsupported_operations",
        "access_levels",
        "execution_modes",
        "features",
    }
    result = {}
    for runtime in runtimes:
        if (
            not isinstance(runtime, dict)
            or not {"id", "status", "capabilities"}.issubset(runtime)
            or set(runtime) - runtime_fields
        ):
            raise ValueError("runtime adapter 定义或字段无效")
        runtime_id = runtime["id"]
        if not isinstance(runtime_id, str) or not runtime_id or runtime_id in result:
            raise ValueError(f"runtime adapter ID 无效或重复: {runtime_id}")
        status = runtime["status"]
        if status not in {"operational", "described-only"}:
            raise ValueError(f"runtime adapter 状态无效: {runtime_id}")
        if "verified_on" in runtime and not (
            isinstance(runtime["verified_on"], str) and runtime["verified_on"]
        ):
            raise ValueError(f"runtime adapter verified_on 无效: {runtime_id}")
        capabilities = runtime["capabilities"]
        if not isinstance(capabilities, dict) or set(capabilities) != capability_fields:
            raise ValueError(f"runtime adapter capabilities 字段无效: {runtime_id}")
        operations = _string_set(
            capabilities["lifecycle_operations"],
            f"runtime adapter lifecycle_operations: {runtime_id}",
            allow_empty=True,
        )
        unsupported = _string_set(
            capabilities["unsupported_operations"],
            f"runtime adapter unsupported_operations: {runtime_id}",
            allow_empty=True,
        )
        access = _string_set(capabilities["access_levels"], f"runtime adapter access_levels: {runtime_id}")
        modes = _string_set(capabilities["execution_modes"], f"runtime adapter execution_modes: {runtime_id}")
        features = _string_set(
            capabilities["features"],
            f"runtime adapter features: {runtime_id}",
            allow_empty=True,
        )
        if not operations.issubset(all_operations) or not unsupported.issubset(all_operations):
            raise ValueError(f"runtime adapter 声明未知生命周期操作: {runtime_id}")
        if operations & unsupported:
            raise ValueError(f"runtime adapter 同时支持和拒绝同一操作: {runtime_id}")
        if operations | unsupported != all_operations:
            raise ValueError(f"runtime adapter 生命周期操作未完整覆盖: {runtime_id}")
        if not access.issubset(contract_access) or not modes.issubset(contract_modes):
            raise ValueError(f"runtime adapter 声明未知访问级别或执行模式: {runtime_id}")
        if not features.issubset(contract_capabilities):
            raise ValueError(f"runtime adapter 声明未知能力: {runtime_id}")

        source = runtime.get("source")
        if source is not None and not (isinstance(source, str) and source):
            raise ValueError(f"runtime adapter source 无效: {runtime_id}")
        if status == "operational":
            if source is None:
                raise ValueError(f"operational runtime 缺少 source: {runtime_id}")
            if "isolated" in modes and not required_operations.issubset(operations):
                raise ValueError(f"operational isolated runtime 缺少必需生命周期: {runtime_id}")
        if source is not None:
            source_path = (catalog_path.parent / source).resolve()
            if root not in source_path.parents or not source_path.is_file():
                raise ValueError(f"runtime adapter source 缺失或越界: {runtime_id}")
            _validate_runtime_source(_load_json(source_path), runtime_id, modes)

        package = runtime.get("package")
        if package is not None:
            package_fields = {"name", "version", "bin"}
            if (
                not isinstance(package, dict)
                or set(package) != package_fields
                or not all(isinstance(package[key], str) and package[key] for key in package_fields)
            ):
                raise ValueError(f"runtime adapter package 无效: {runtime_id}")
        if runtime_id == "pi" and package is None:
            raise ValueError("pi runtime 缺少 package 事实")
        result[runtime_id] = runtime
    return result


RUNTIME_CONTRACT = load_runtime_contract()
RUNTIME_ADAPTERS = load_runtime_adapters(RUNTIME_CONTRACT)
