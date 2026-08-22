#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Optional

from runtime_registry import load_runtime_adapters


SKILL_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = SKILL_ROOT / "config" / "memory-contract.json"
ADAPTERS_PATH = SKILL_ROOT / "config" / "runtime-manifest.json"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"缺少 memory source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(values, label: str, allow_empty: bool = False) -> set:
    if (
        not isinstance(values, list)
        or (not allow_empty and not values)
        or not all(isinstance(value, str) and value for value in values)
    ):
        raise ValueError(f"{label} 无效")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} 重复")
    return set(values)


def _validate_memory_contract(data: dict) -> dict:
    fields = {"version", "entry", "index", "relations"}
    if not isinstance(data, dict) or set(data) != fields or data.get("version") != "1.0":
        raise ValueError("memory contract 字段无效或版本不支持")

    entry = data["entry"]
    entry_fields = {
        "frontmatter_required",
        "metadata_required",
        "metadata_types",
        "body_format",
        "link_syntax",
    }
    if not isinstance(entry, dict) or set(entry) != entry_fields:
        raise ValueError("memory entry contract 字段无效")
    if _strings(entry["frontmatter_required"], "memory entry frontmatter") != {
        "name",
        "description",
        "metadata",
    }:
        raise ValueError("memory entry frontmatter 字段不完整")
    if _strings(entry["metadata_required"], "memory entry metadata") != {"type"}:
        raise ValueError("memory entry metadata 字段不完整")
    metadata_types = _strings(entry["metadata_types"], "memory entry metadata type")
    allowed_types = {"user", "feedback", "project", "reference"}
    if not metadata_types.issubset(allowed_types):
        raise ValueError("memory entry metadata type 未知")
    if metadata_types != allowed_types:
        raise ValueError("memory entry metadata type 不完整")
    if entry["body_format"] != "markdown" or entry["link_syntax"] != "[[name]]":
        raise ValueError("memory entry body 或 link contract 无效")

    index = data["index"]
    index_fields = {"required", "pointer_format", "pointer_fields", "max_lines"}
    if not isinstance(index, dict) or set(index) != index_fields:
        raise ValueError("memory index contract 字段无效")
    if index["required"] is not True or index["pointer_format"] != "markdown-link":
        raise ValueError("memory index contract 无效")
    if _strings(index["pointer_fields"], "memory index pointer") != {
        "title",
        "path",
        "hook",
    }:
        raise ValueError("memory index pointer 字段不完整")
    if (
        not isinstance(index["max_lines"], int)
        or isinstance(index["max_lines"], bool)
        or index["max_lines"] <= 0
    ):
        raise ValueError("memory index max_lines 无效")

    relations = data["relations"]
    if not isinstance(relations, dict) or set(relations) != {
        "link_syntax",
        "target",
        "unresolved_action",
    }:
        raise ValueError("memory relations contract 字段无效")
    if relations != {
        "link_syntax": "[[name]]",
        "target": "entry-name",
        "unresolved_action": "report",
    }:
        raise ValueError("memory relations contract 无效")
    return data


def _validate_storage(data: dict, fields: set, kinds: set, label: str) -> dict:
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError(f"memory adapter {label} 字段无效")
    if not isinstance(data["kind"], str) or data["kind"] not in kinds:
        raise ValueError(f"memory adapter {label} kind 无效")
    if not isinstance(data["path_binding"], str) or not data["path_binding"]:
        raise ValueError(f"memory adapter {label} path_binding 无效")
    return data


def _validate_memory_adapter(
    data: dict,
    contract: dict,
    runtime_id: str,
    runtime_status: Optional[str] = None,
) -> dict:
    _validate_memory_contract(contract)
    fields = {
        "version",
        "id",
        "status",
        "entry_storage",
        "index_storage",
        "session_storage",
    }
    if not isinstance(data, dict) or set(data) != fields or data.get("version") != "1.0":
        raise ValueError(f"memory adapter 字段无效: {runtime_id}")
    if data["id"] != runtime_id:
        raise ValueError(f"memory adapter ID 不一致: {runtime_id}")
    if not isinstance(data["status"], str) or data["status"] not in {
        "operational",
        "described-only",
    }:
        raise ValueError(f"memory adapter status 无效: {runtime_id}")
    if runtime_status is not None and data["status"] != runtime_status:
        raise ValueError(f"memory adapter status 与 runtime 不一致: {runtime_id}")
    entry_storage = _validate_storage(
        data["entry_storage"],
        {"kind", "path_binding", "file_pattern"},
        {"markdown-files", "session-jsonl"},
        "entry_storage",
    )
    if entry_storage["file_pattern"] is not None and not (
        isinstance(entry_storage["file_pattern"], str) and entry_storage["file_pattern"]
    ):
        raise ValueError(f"memory adapter entry_storage file_pattern 无效: {runtime_id}")
    index_storage = _validate_storage(
        data["index_storage"],
        {"kind", "path_binding"},
        {"markdown-file", "session-tree"},
        "index_storage",
    )
    session_storage = _validate_storage(
        data["session_storage"],
        {"kind", "path_binding"},
        {"host-managed", "jsonl-tree"},
        "session_storage",
    )
    if data["status"] == "described-only" and any(
        storage["path_binding"] != "host-defined"
        for storage in (entry_storage, index_storage, session_storage)
    ):
        raise ValueError(f"described-only memory adapter 必须使用 host-defined path: {runtime_id}")
    return data


def load_memory_contract(path: Optional[Path] = None) -> dict:
    source = path if path is not None else CONTRACT_PATH
    return _validate_memory_contract(_load_json(source))


def load_memory_adapters(
    contract: Optional[dict] = None,
    path: Optional[Path] = None,
) -> Dict[str, dict]:
    catalog_path = (path if path is not None else ADAPTERS_PATH).resolve()
    contract = load_memory_contract() if contract is None else _validate_memory_contract(contract)
    runtimes = load_runtime_adapters(path=catalog_path)
    root = catalog_path.parent.parent.parent.resolve()
    result = {}
    for runtime_id, runtime in runtimes.items():
        source = runtime.get("source")
        if not isinstance(source, str) or not source:
            raise ValueError(f"runtime adapter 缺少 memory source 基准: {runtime_id}")
        source_path = (catalog_path.parent / source).resolve()
        memory_path = source_path.with_name("memory.json")
        if root not in memory_path.parents or not memory_path.is_file():
            raise ValueError(f"memory adapter source 缺失或越界: {runtime_id}")
        result[runtime_id] = _validate_memory_adapter(
            _load_json(memory_path),
            contract,
            runtime_id,
            runtime.get("status"),
        )
    return result


MEMORY_CONTRACT = load_memory_contract()
MEMORY_ADAPTERS = load_memory_adapters(MEMORY_CONTRACT)
