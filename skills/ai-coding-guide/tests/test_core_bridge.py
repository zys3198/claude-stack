import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_stage_prompt import build_prompt  # noqa: E402
import rule_sources  # noqa: E402


class CoreBridgeTests(unittest.TestCase):
    def test_stage_prompt_includes_core_and_adapter_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts/task"
            artifacts.mkdir(parents=True)
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["REQUIREMENT", "DESIGN"],
                "stages": {
                    "REQUIREMENT": {"artifacts": []},
                    "DESIGN": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "DESIGN", "", [])
            self.assertIn("## 通用核心原则", prompt)
            self.assertIn("## DevFlow adapter 补充规则", prompt)
            self.assertIn("证据优先", prompt)
            self.assertIn("职责隔离", prompt)

    def test_helper_prompt_includes_core_and_adapter_rules(self):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "build_helper_prompt.py"),
                "--role",
                "devflow-code-explorer",
                "--purpose",
                "核对规则",
            ],
            capture_output=True,
            text=True,
            check=True,
            env=environment,
        )
        self.assertIn("## 通用核心原则", result.stdout)
        self.assertIn("## DevFlow adapter 补充规则", result.stdout)
        self.assertIn("证据优先", result.stdout)
        self.assertIn("职责隔离", result.stdout)

    def test_missing_rule_source_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing-principles.md"
            with patch.object(rule_sources, "CORE_RULES_PATH", missing):
                with self.assertRaisesRegex(FileNotFoundError, "缺少规则源"):
                    rule_sources.load_rule_blocks()


if __name__ == "__main__":
    unittest.main()
