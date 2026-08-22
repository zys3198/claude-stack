import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import workflow_sources  # noqa: E402


class WorkflowBridgeTests(unittest.TestCase):
    def test_contract_preserves_current_workflow_semantics(self):
        contract = workflow_sources.load_workflow_contract()
        self.assertEqual(
            contract,
            {
                "version": "2.0",
                "max_stage_failures": 2,
                "max_batch_tasks": 3,
                "required_approval_gates": ["REQUIREMENT"],
                "manual_gates": ["DESIGN", "REVIEW", "TEST"],
                "optional_stages": ["KNOWLEDGE"],
                "routes": {
                    "small": ["SOLO", "SUMMARY"],
                    "medium": ["REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST", "KNOWLEDGE", "SUMMARY"],
                    "large": ["REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST", "KNOWLEDGE", "SUMMARY"],
                },
                "compatible_routes": {
                    "medium": [["REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST", "SUMMARY"]]
                },
            },
        )

    def test_runtime_config_owns_contract(self):
        config = json.loads((SKILL_ROOT / "config/workflow.json").read_text(encoding="utf-8"))
        self.assertEqual(config["version"], "2.0")
        self.assertNotIn("source", config)

    def test_runtime_scripts_do_not_read_legacy_workflow_config(self):
        for name in ("workflow_state.py", "validate_config.py", "validate_artifacts.py"):
            source = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertNotIn('config/workflow.json', source)
            self.assertIn("load_workflow_contract", source)

    def test_missing_workflow_config_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "workflow.json"
            with patch.object(workflow_sources, "WORKFLOW_CONFIG_PATH", config_path):
                with self.assertRaisesRegex(FileNotFoundError, "缺少工作流配置源"):
                    workflow_sources.load_workflow_contract()


if __name__ == "__main__":
    unittest.main()
