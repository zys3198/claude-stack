import copy
import json
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

import install_adapter  # noqa: E402
import runtime_registry  # noqa: E402


class RuntimeBridgeTests(unittest.TestCase):
    def test_contract_declares_neutral_lifecycle(self):
        contract = runtime_registry.RUNTIME_CONTRACT
        self.assertEqual(
            contract["lifecycle"]["required_operations"],
            ["spawn", "send", "wait", "close"],
        )
        self.assertEqual(contract["lifecycle"]["optional_operations"], ["spawn_helper"])
        self.assertEqual(contract["lifecycle"]["executor_id"], "host-issued")
        self.assertEqual(set(contract["access_levels"]), {"read", "report", "write", "test-write"})
        serialized = json.dumps(contract, ensure_ascii=False)
        for tool_name in ("Agent", "Read", "Glob", "Grep"):
            self.assertNotIn(tool_name, serialized)

    def test_catalog_maps_local_claude_runtime(self):
        runtimes = runtime_registry.RUNTIME_ADAPTERS
        self.assertEqual(set(runtimes), {"claude"})
        self.assertEqual(runtimes["claude"]["status"], "operational")
        self.assertEqual(
            runtimes["claude"]["source"],
            "../adapters/claude/manifest.json",
        )

    def test_catalog_keeps_host_tool_names_out(self):
        serialized = json.dumps(runtime_registry.RUNTIME_ADAPTERS, ensure_ascii=False)
        for tool_name in ("Agent", "Read", "Glob", "Grep"):
            self.assertNotIn(tool_name, serialized)

    def _assert_contract_rejected(self, contract):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "runtime contract|lifecycle"):
                runtime_registry.load_runtime_contract(path)

    def test_contract_rejects_unknown_or_malformed_fields(self):
        cases = {}
        unknown_field = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        unknown_field["dispatch_tool"] = "Agent"
        cases["unknown field"] = unknown_field
        numeric_operation = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        numeric_operation["lifecycle"]["required_operations"] = [1]
        cases["numeric operation"] = numeric_operation
        nested_operation = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        nested_operation["lifecycle"]["optional_operations"] = [["spawn_helper"]]
        cases["nested operation"] = nested_operation
        duplicate_operation = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        duplicate_operation["lifecycle"]["required_operations"] = ["spawn", "spawn"]
        cases["duplicate operation"] = duplicate_operation
        empty_operation = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        empty_operation["lifecycle"]["optional_operations"] = [""]
        cases["empty operation"] = empty_operation

        for name, contract in cases.items():
            with self.subTest(name=name):
                self._assert_contract_rejected(contract)

    def test_missing_contract_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing-contract.json"
            with patch.object(runtime_registry, "CONTRACT_PATH", missing):
                with self.assertRaisesRegex(FileNotFoundError, "缺少 runtime source"):
                    runtime_registry.load_runtime_contract()

    def _write_catalog(self, directory, catalog, contract=None, sources=None):
        root = Path(directory) / "stack"
        config = root / "config"
        config.mkdir(parents=True)
        contract_path = config / "runtime-contract.json"
        contract_path.write_text(
            json.dumps(contract if contract is not None else runtime_registry.RUNTIME_CONTRACT),
            encoding="utf-8",
        )
        path = config / "runtime-manifest.json"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        for runtime_id, source_data in (sources or {}).items():
            runtime = next(item for item in catalog["runtimes"] if item["id"] == runtime_id)
            source_path = (path.parent / runtime["source"]).resolve()
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(json.dumps(source_data), encoding="utf-8")
        return root, path

    def _assert_catalog_rejected(self, catalog, message, contract=None, sources=None):
        with tempfile.TemporaryDirectory() as directory:
            _, path = self._write_catalog(directory, catalog, contract=contract, sources=sources)
            with self.assertRaisesRegex(ValueError, message):
                runtime_registry.load_runtime_adapters(contract, path)

    def _claude_source(self):
        path = SKILL_ROOT / "adapters/claude/manifest.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_unknown_lifecycle_operation_is_rejected(self):
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [
                {
                    "id": "claude",
                    "status": "described-only",
                    "capabilities": {
                        "lifecycle_operations": [],
                        "access_levels": ["read"],
                        "execution_modes": ["single-context"],
                        "features": [],
                        "unsupported_operations": ["not-an-operation"],
                    },
                }
            ],
        }
        self._assert_catalog_rejected(catalog, "未知生命周期操作")

    def test_supported_and_unsupported_operation_conflict_is_rejected(self):
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [
                {
                    "id": "claude",
                    "status": "described-only",
                    "capabilities": {
                        "lifecycle_operations": ["spawn"],
                        "access_levels": ["read"],
                        "execution_modes": ["single-context"],
                        "features": [],
                        "unsupported_operations": ["spawn"],
                    },
                }
            ],
        }
        self._assert_catalog_rejected(catalog, "同时支持和拒绝")

    def test_catalog_rejects_malformed_capabilities_and_host_fields(self):
        cases = {}
        malformed = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        malformed["capabilities"]["unsupported_operations"] = []
        cases["missing operation coverage"] = malformed
        host_field = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        host_field["dispatch_tool"] = "Agent"
        cases["host field"] = host_field
        for name, runtime in cases.items():
            catalog = {
                "version": "1.0",
                "source": "runtime-contract.json",
                "runtimes": [runtime],
            }
            with self.subTest(name=name):
                self._assert_catalog_rejected(catalog, "runtime adapter|字段")

    def test_operational_isolated_adapter_requires_lifecycle_and_complete_source(self):
        missing_operations = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        missing_operations["capabilities"]["lifecycle_operations"] = []
        missing_operations["capabilities"]["unsupported_operations"] = [
            "spawn", "send", "wait", "close", "spawn_helper"
        ]
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [missing_operations],
        }
        self._assert_catalog_rejected(
            catalog,
            "必需生命周期",
            sources={"claude": self._claude_source()},
        )

        incomplete_source = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        catalog["runtimes"] = [incomplete_source]
        self._assert_catalog_rejected(
            catalog,
            "source 不完整",
            sources={"claude": {"id": "claude", "version": "1.0"}},
        )

    def test_isolated_source_rejects_unknown_topology(self):
        source = self._claude_source()
        source["topology"] = "unknown"
        runtime = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [runtime],
        }
        self._assert_catalog_rejected(
            catalog,
            "source.*拓扑",
            sources={"claude": source},
        )

    def test_catalog_contract_must_match_declared_source(self):
        contract = copy.deepcopy(runtime_registry.RUNTIME_CONTRACT)
        contract["capabilities"].append("custom-host-capability")
        runtime = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        runtime["capabilities"]["features"] = ["custom-host-capability"]
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [runtime],
        }
        with tempfile.TemporaryDirectory() as directory:
            _, path = self._write_catalog(directory, catalog)
            with self.assertRaisesRegex(ValueError, "contract.*不一致"):
                runtime_registry.load_runtime_adapters(contract, path)

    def test_explicit_catalog_path_controls_source_resolution(self):
        runtime = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        runtime["source"] = "claude.json"
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [runtime],
        }
        with tempfile.TemporaryDirectory() as directory:
            _, path = self._write_catalog(
                directory,
                catalog,
                sources={"claude": self._claude_source()},
            )
            runtimes = runtime_registry.load_runtime_adapters(
                runtime_registry.RUNTIME_CONTRACT,
                path,
            )
            self.assertEqual(set(runtimes), {"claude"})

    def test_missing_or_out_of_root_source_is_rejected(self):
        runtime = copy.deepcopy(runtime_registry.RUNTIME_ADAPTERS["claude"])
        runtime["source"] = "../../../outside/claude.json"
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [runtime],
        }
        self._assert_catalog_rejected(
            catalog,
            "source 缺失或越界",
            sources={"claude": self._claude_source()},
        )

    def test_copy_install_copies_local_skill_without_runtime_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "project"
            project_root.mkdir()
            env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
            install = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "install_adapter.py"),
                    "--adapter", "claude",
                    "--project-root", str(project_root),
                    "--copy-skills",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            copied_skill = project_root / ".claude/skills/ai-coding-guide"
            self.assertTrue((copied_skill / "config/runtime-manifest.json").is_file())
            self.assertFalse((project_root / ".claude/universal-agent-stack").exists())

    def test_cross_drive_link_failure_falls_back_to_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(Path, "symlink_to", side_effect=OSError("links disabled")),
                patch.object(install_adapter.os.path, "relpath", side_effect=ValueError("cross-drive")),
            ):
                results = install_adapter.install_skills(
                    "claude", root / ".claude", root / ".claude/skills",
                    ["ai-coding-guide"], refresh=False, copy_skills=False,
                )
            self.assertIn("ai-coding-guide=copied", results)
            self.assertFalse((root / ".claude/universal-agent-stack").exists())


if __name__ == "__main__":
    unittest.main()
