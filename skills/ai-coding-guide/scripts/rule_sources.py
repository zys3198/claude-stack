from pathlib import Path
from typing import List, Tuple


SKILL_ROOT = Path(__file__).resolve().parent.parent
CORE_RULES_PATH = SKILL_ROOT / "rules" / "principles.md"
ADAPTER_RULES_PATH = SKILL_ROOT / "rules" / "core.md"


def load_rule_blocks() -> List[Tuple[str, str]]:
    paths = (
        ("通用核心原则", CORE_RULES_PATH),
        ("DevFlow adapter 补充规则", ADAPTER_RULES_PATH),
    )
    missing = [str(path) for _, path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("缺少规则源：" + ", ".join(missing))
    return [(title, path.read_text(encoding="utf-8").strip()) for title, path in paths]
