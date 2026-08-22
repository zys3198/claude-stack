import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_CONFIG_PATH = SKILL_ROOT / "config" / "workflow.json"


def load_workflow_contract() -> dict:
    if not WORKFLOW_CONFIG_PATH.is_file():
        raise FileNotFoundError(f"缺少工作流配置源: {WORKFLOW_CONFIG_PATH}")
    config = json.loads(WORKFLOW_CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or "version" not in config:
        raise ValueError(f"工作流配置不是有效契约: {WORKFLOW_CONFIG_PATH}")
    return config
