#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from typing import Dict, List


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = SKILL_ROOT / "templates"
MANIFEST_PATH = TEMPLATE_ROOT / "manifest.json"


def _merge_items(core_items, adapter_items, core_fields, adapter_fields, label, required=True):
    if not isinstance(core_items, list) or (required and not core_items):
        raise ValueError(f"逻辑{label}清单必须是非空数组")
    if not isinstance(adapter_items, list) or (required and not adapter_items):
        raise ValueError(f"模板 adapter {label}映射必须是非空数组")
    core_by_id = {}
    for item in core_items:
        if not isinstance(item, dict) or not core_fields.issubset(item):
            raise ValueError(f"逻辑{label}清单存在不完整定义")
        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"逻辑{label} ID 无效")
        if item_id in core_by_id:
            raise ValueError(f"逻辑{label} ID 重复: {item_id}")
        core_by_id[item_id] = item
    adapter_by_id = {}
    for item in adapter_items:
        if (
            not isinstance(item, dict)
            or not adapter_fields.issubset(item)
            or set(item) - adapter_fields
        ):
            raise ValueError(f"模板 adapter {label}映射字段无效")
        item_id = item["id"]
        if not all(isinstance(item[field], str) and item[field] for field in adapter_fields):
            raise ValueError(f"模板 adapter {label}映射值无效: {item_id}")
        if item_id in adapter_by_id:
            raise ValueError(f"模板 adapter {label} ID 重复: {item_id}")
        adapter_by_id[item_id] = {field: item[field] for field in adapter_fields - {"id"}}
    if set(core_by_id) != set(adapter_by_id):
        raise ValueError(f"逻辑{label}与 adapter 映射不一致")
    return [{**item, **adapter_by_id[item["id"]]} for item in core_items]


def load_manifest() -> dict:
    adapter = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if adapter.get("version") != "1.0":
        raise ValueError(f"不支持的模板 adapter 清单版本: {adapter.get('version')}")
    core = adapter
    if not isinstance(core.get("version"), str) or not core["version"]:
        raise ValueError("逻辑产物清单缺少 version")
    artifacts = _merge_items(
        core.get("artifacts"),
        adapter.get("artifact_adapters"),
        {"id", "stage", "template_version", "content_concepts"},
        {"id", "path", "template"},
        "产物",
    )
    blueprints = _merge_items(
        core.get("blueprints", []),
        adapter.get("blueprint_adapters", []),
        {"id", "template_version"},
        {"id", "target_pattern", "template"},
        "蓝图",
        required=False,
    )
    system_templates = _merge_items(
        core.get("system_templates", []),
        adapter.get("system_template_adapters", []),
        {"id", "template_version"},
        {"id", "template"},
        "系统模板",
        required=False,
    )
    seen = set()
    for item in artifacts:
        relative = item["path"]
        if relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError(f"模板清单包含不安全或重复路径: {relative}")
        seen.add(relative)
        template = TEMPLATE_ROOT / item["template"]
        if not template.is_file():
            raise ValueError(f"模板文件不存在: {item['template']}")
        if item.get("condition") not in {None, "requires_design_artifacts"}:
            raise ValueError(f"模板清单包含不支持的条件: {item.get('condition')}")
    for blueprint in blueprints:
        if not (TEMPLATE_ROOT / blueprint["template"]).is_file():
            raise ValueError(f"蓝图模板不存在: {blueprint['template']}")
    for template in system_templates:
        if not (TEMPLATE_ROOT / template["template"]).is_file():
            raise ValueError(f"系统模板不存在: {template['template']}")
    return {
        "version": core["version"],
        "artifacts": [{key: value for key, value in item.items() if key != "id"} for item in artifacts],
        "blueprints": blueprints,
        "system_templates": system_templates,
    }


MANIFEST = load_manifest()
ARTIFACTS: Dict[str, dict] = {item["path"]: item for item in MANIFEST["artifacts"]}
SYSTEM_TEMPLATES = {item["id"]: item for item in MANIFEST.get("system_templates", [])}


def required_artifacts(stage: str, include_design_context: bool = False) -> List[str]:
    result = []
    for item in MANIFEST["artifacts"]:
        if item["stage"] != stage:
            continue
        if item.get("condition") == "requires_design_artifacts" and not include_design_context:
            continue
        result.append(item["path"])
    return result


def materialize_stage(stage: str, artifact_root: Path, include_design_context: bool = False) -> List[str]:
    created = []
    for relative in required_artifacts(stage, include_design_context):
        spec = ARTIFACTS[relative]
        destination = artifact_root / relative
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TEMPLATE_ROOT / spec["template"], destination)
        created.append(relative)
    return created


def system_template(template_id: str) -> Path:
    return TEMPLATE_ROOT / SYSTEM_TEMPLATES[template_id]["template"]
