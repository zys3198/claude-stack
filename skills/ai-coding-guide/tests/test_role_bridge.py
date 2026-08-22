import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS))

import agent_registry  # noqa: E402


class RoleBridgeTests(unittest.TestCase):
    def test_loader_merges_local_metadata_and_adapter_fields(self):
        roles = {role["id"]: role for role in agent_registry.MANIFEST["roles"]}
        self.assertEqual(len(roles), 10)
        self.assertEqual(roles["devflow-architect"]["stage"], "DESIGN")
        self.assertEqual(roles["devflow-architect"]["access"], "report")
        self.assertEqual(
            roles["devflow-architect"]["input_artifacts"],
            ["01-requirement/requirement-report.md"],
        )
        self.assertEqual(roles["devflow-architect"]["file"], "devflow-architect.md")
        self.assertEqual(roles["devflow-code-explorer"]["kind"], "helper")
        self.assertEqual(roles["devflow-code-explorer"]["access"], "read")

    def test_local_manifest_separates_semantics_and_adapter_fields(self):
        manifest = json.loads(
            (SKILL_ROOT / "agents/manifest.json").read_text(encoding="utf-8")
        )
        self.assertTrue(all("file" not in role for role in manifest["roles"]))
        self.assertTrue(all("input_artifacts" not in role for role in manifest["roles"]))
        self.assertTrue(all("access" in role for role in manifest["roles"]))
        self.assertNotIn("source", manifest)

    def test_missing_roles_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
            with patch.object(agent_registry, "MANIFEST_PATH", manifest_path):
                with self.assertRaisesRegex(ValueError, "逻辑角色清单 roles"):
                    agent_registry.load_manifest()

    def test_adapter_cannot_override_local_role_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "roles": [
                            {
                                "id": "devflow-architect",
                                "kind": "stage",
                                "stage": "DESIGN",
                                "description": "设计",
                                "access": "report",
                                "input_stages": [],
                                "workspace_evidence": [],
                                "execution": "agent",
                            }
                        ],
                        "role_adapters": [
                            {
                                "id": "devflow-architect",
                                "file": "devflow-architect.md",
                                "access": "write",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(agent_registry, "MANIFEST_PATH", manifest_path):
                with self.assertRaisesRegex(ValueError, "字段无效"):
                    agent_registry.load_manifest()


if __name__ == "__main__":
    unittest.main()
