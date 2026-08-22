#!/usr/bin/env python3
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SKILL_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import memory_registry  # noqa: E402
import runtime_registry  # noqa: E402


class MemoryBridgeTests(unittest.TestCase):
    def test_contract_defines_entry_index_and_relations(self):
        contract = memory_registry.MEMORY_CONTRACT
        self.assertEqual(set(contract), {"version", "entry", "index", "relations"})
        self.assertEqual(set(contract["entry"]["metadata_types"]), {"user", "feedback", "project", "reference"})
        self.assertEqual(contract["entry"]["body_format"], "markdown")
        self.assertEqual(contract["entry"]["link_syntax"], "[[name]]")
        self.assertEqual(contract["index"]["pointer_format"], "markdown-link")
        self.assertEqual(contract["relations"]["unresolved_action"], "report")

    def test_local_adapter_binds_claude_storage(self):
        self.assertEqual(set(memory_registry.MEMORY_ADAPTERS), {"claude"})
        claude = memory_registry.MEMORY_ADAPTERS["claude"]
        self.assertEqual(claude["entry_storage"]["kind"], "markdown-files")
        self.assertEqual(claude["index_storage"]["kind"], "markdown-file")
        self.assertEqual(claude["index_storage"]["path_binding"], "MEMORY.md")

    def _assert_contract_rejected(self, contract, message):
        with self.assertRaisesRegex(ValueError, message):
            memory_registry._validate_memory_contract(contract)

    def _assert_adapter_rejected(self, adapter, message="memory adapter"):
        with self.assertRaisesRegex(ValueError, message):
            memory_registry._validate_memory_adapter(
                adapter, memory_registry.MEMORY_CONTRACT, "claude"
            )

    def test_contract_rejects_unknown_field(self):
        contract = copy.deepcopy(memory_registry.MEMORY_CONTRACT)
        contract["unexpected"] = True
        self._assert_contract_rejected(contract, "字段无效")

    def test_contract_rejects_duplicate_type(self):
        contract = copy.deepcopy(memory_registry.MEMORY_CONTRACT)
        contract["entry"]["metadata_types"].append("user")
        self._assert_contract_rejected(contract, "type.*重复")

    def test_contract_rejects_unknown_type(self):
        contract = copy.deepcopy(memory_registry.MEMORY_CONTRACT)
        contract["entry"]["metadata_types"].append("chat")
        self._assert_contract_rejected(contract, "type.*未知")

    def test_contract_rejects_malformed_relations(self):
        contract = copy.deepcopy(memory_registry.MEMORY_CONTRACT)
        contract["relations"] = [[]]
        self._assert_contract_rejected(contract, "relations")

    def test_adapter_rejects_malformed_kind(self):
        adapter = copy.deepcopy(memory_registry.MEMORY_ADAPTERS["claude"])
        adapter["entry_storage"]["kind"] = []
        self._assert_adapter_rejected(adapter, "entry_storage")

    def test_adapter_rejects_malformed_status(self):
        adapter = copy.deepcopy(memory_registry.MEMORY_ADAPTERS["claude"])
        adapter["status"] = []
        self._assert_adapter_rejected(adapter, "status")

    def test_adapter_rejects_unknown_field(self):
        adapter = copy.deepcopy(memory_registry.MEMORY_ADAPTERS["claude"])
        adapter["unexpected"] = True
        self._assert_adapter_rejected(adapter, "字段无效")

    def test_adapter_rejects_source_id_mismatch(self):
        adapter = copy.deepcopy(memory_registry.MEMORY_ADAPTERS["claude"])
        adapter["id"] = "other"
        self._assert_adapter_rejected(adapter, "ID 不一致")

    def test_adapter_rejects_unknown_storage_kind(self):
        adapter = copy.deepcopy(memory_registry.MEMORY_ADAPTERS["claude"])
        adapter["entry_storage"]["kind"] = "unknown"
        self._assert_adapter_rejected(adapter, "entry_storage")

    def _write_catalog(self, root, status="operational", source="../adapters/claude/manifest.json"):
        config = root / "config"
        adapters = root / "adapters"
        config.mkdir(parents=True)
        (adapters / "claude").mkdir(parents=True)
        shutil.copy2(
            SKILL_ROOT / "config/runtime-contract.json",
            config / "runtime-contract.json",
        )
        shutil.copy2(
            SKILL_ROOT / "adapters/claude/manifest.json",
            adapters / "claude/manifest.json",
        )
        shutil.copy2(
            SKILL_ROOT / "adapters/claude/memory.json",
            adapters / "claude/memory.json",
        )
        catalog = {
            "version": "1.0",
            "source": "runtime-contract.json",
            "runtimes": [
                {
                    "id": "claude",
                    "status": status,
                    "source": source,
                    "capabilities": copy.deepcopy(
                        runtime_registry.RUNTIME_ADAPTERS["claude"]["capabilities"]
                    ),
                }
            ],
        }
        catalog_path = config / "runtime-manifest.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        return catalog_path, adapters / "claude/memory.json"

    def test_loader_loads_local_memory_source(self):
        adapters = memory_registry.load_memory_adapters()
        self.assertEqual(set(adapters), {"claude"})
        self.assertEqual(adapters["claude"]["status"], "operational")

    def test_loader_rejects_missing_sibling_source(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path, memory_path = self._write_catalog(Path(directory) / "stack")
            memory_path.unlink()
            with self.assertRaisesRegex(ValueError, "memory adapter source 缺失"):
                memory_registry.load_memory_adapters(path=catalog_path)

    def test_loader_rejects_runtime_status_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path, _ = self._write_catalog(Path(directory) / "stack", status="described-only")
            with self.assertRaisesRegex(ValueError, "status 与 runtime"):
                memory_registry.load_memory_adapters(path=catalog_path)

    def test_loader_rejects_runtime_source_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path, _ = self._write_catalog(
                Path(directory) / "stack", source="../../../outside/manifest.json"
            )
            with self.assertRaisesRegex(ValueError, "source 缺失或越界"):
                memory_registry.load_memory_adapters(path=catalog_path)


if __name__ == "__main__":
    unittest.main()
