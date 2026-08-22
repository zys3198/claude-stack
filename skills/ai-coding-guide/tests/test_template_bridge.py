import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import template_registry  # noqa: E402


class TemplateBridgeTests(unittest.TestCase):
    def test_loader_preserves_public_artifact_contract(self):
        self.assertEqual(len(template_registry.MANIFEST["artifacts"]), 11)
        self.assertEqual(len(template_registry.MANIFEST["blueprints"]), 3)
        self.assertEqual(len(template_registry.MANIFEST["system_templates"]), 1)
        self.assertEqual(
            list(template_registry.ARTIFACTS),
            [
                "01-solo/solo-report.md",
                "01-requirement/requirement-report.md",
                "02-design/tech-design.md",
                "02-design/execution-plan.md",
                "02-design/design-context/overview.md",
                "02-design/design-context/components.md",
                "03-code/change-report.md",
                "03-code/review-report.md",
                "04-test/test-report.md",
                "05-knowledge/knowledge-report.md",
                "workflow-summary.md",
            ],
        )
        self.assertEqual(
            template_registry.ARTIFACTS["02-design/design-context/overview.md"]["condition"],
            "requires_design_artifacts",
        )
        self.assertEqual(
            template_registry.SYSTEM_TEMPLATES["workflow-state"]["template_version"],
            "2.0",
        )

    def test_local_manifest_separates_semantics_and_adapter_fields(self):
        manifest = json.loads(
            (SKILL_ROOT / "templates/manifest.json").read_text(encoding="utf-8")
        )
        self.assertTrue(all("path" not in item and "template" not in item for item in manifest["artifacts"]))
        self.assertTrue(all("target_pattern" not in item and "template" not in item for item in manifest["blueprints"]))
        self.assertTrue(all("template" not in item for item in manifest["system_templates"]))
        self.assertNotIn("source", manifest)

    def test_missing_local_semantics_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
            with patch.object(template_registry, "MANIFEST_PATH", manifest_path):
                with self.assertRaisesRegex(ValueError, "逻辑产物清单"):
                    template_registry.load_manifest()

    def test_adapter_cannot_override_local_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "artifacts": [
                            {
                                "id": "solo-report",
                                "stage": "SOLO",
                                "template_version": "1.0",
                                "content_concepts": ["变更"],
                            }
                        ],
                        "artifact_adapters": [
                            {
                                "id": "solo-report",
                                "path": "01-solo/solo-report.md",
                                "template": "solo-report.md",
                                "stage": "REVIEW",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(template_registry, "MANIFEST_PATH", manifest_path):
                with self.assertRaisesRegex(ValueError, "映射字段无效"):
                    template_registry.load_manifest()


if __name__ == "__main__":
    unittest.main()
