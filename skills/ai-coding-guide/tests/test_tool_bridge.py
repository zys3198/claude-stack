import copy
import json
import re
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import tool_registry  # noqa: E402


class ToolBridgeTests(unittest.TestCase):
    def test_contract_is_neutral_and_covers_roles(self):
        contract = tool_registry.TOOL_CONTRACT
        self.assertEqual(
            {tool["id"] for tool in contract["tools"]},
            {"read", "search", "write", "execute", "dispatch"},
        )
        self.assertEqual(
            {item["role"] for item in contract["role_requirements"]},
            tool_registry.ROLE_IDS,
        )
        serialized = json.dumps(contract, ensure_ascii=False)
        for host_name in tool_registry.HOST_TOOL_NAMES:
            if host_name not in tool_registry.NEUTRAL_TOOL_IDS:
                self.assertIsNone(
                    re.search(
                        rf"(?<![A-Za-z0-9_]){re.escape(host_name)}(?![A-Za-z0-9_])",
                        serialized,
                    )
                )

    def test_local_adapter_binds_claude_tools(self):
        self.assertEqual(set(tool_registry.TOOL_ADAPTERS), {"claude"})
        self.assertEqual(
            tool_registry.TOOL_ADAPTERS["claude"]["tool_bindings"]["dispatch"],
            ["Agent"],
        )
        self.assertEqual(tool_registry.TOOL_ADAPTERS["claude"]["unsupported_capabilities"], [])

    def _assert_contract_rejected(self, contract, message):
        with self.assertRaisesRegex(ValueError, message):
            tool_registry._validate_tool_contract(contract)

    def _assert_adapter_rejected(self, adapter, message="tool adapter"):
        with self.assertRaisesRegex(ValueError, message):
            tool_registry._validate_tool_adapter(
                adapter, tool_registry.TOOL_CONTRACT, "claude"
            )

    def test_contract_rejects_host_tool_name(self):
        contract = copy.deepcopy(tool_registry.TOOL_CONTRACT)
        contract["tools"][0]["description"] = "grep"
        self._assert_contract_rejected(contract, "宿主工具名")

    def test_contract_rejects_duplicate_tool(self):
        contract = copy.deepcopy(tool_registry.TOOL_CONTRACT)
        contract["tools"].append(copy.deepcopy(contract["tools"][0]))
        self._assert_contract_rejected(contract, "ID.*重复")

    def test_contract_rejects_unknown_role_requirement(self):
        contract = copy.deepcopy(tool_registry.TOOL_CONTRACT)
        contract["role_requirements"][0]["required"] = ["missing"]
        self._assert_contract_rejected(contract, "引用未知工具")

    def test_contract_rejects_incomplete_role_coverage(self):
        contract = copy.deepcopy(tool_registry.TOOL_CONTRACT)
        contract["role_requirements"].pop()
        self._assert_contract_rejected(contract, "未完整覆盖角色")

    def test_adapter_rejects_unknown_field(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["unexpected"] = True
        self._assert_adapter_rejected(adapter, "未知字段")

    def test_adapter_rejects_unknown_host_binding(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["tool_bindings"]["read"] = ["DefinitelyNotAHostTool"]
        self._assert_adapter_rejected(adapter, "未声明宿主工具")

    def test_adapter_rejects_unmapped_capability(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["tool_bindings"].pop("search")
        self._assert_adapter_rejected(adapter, "tool_bindings 未完整覆盖")

    def test_adapter_rejects_supported_and_unsupported_capability(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["unsupported_capabilities"] = ["dispatch"]
        adapter["tool_bindings"]["dispatch"] = ["Agent"]
        self._assert_adapter_rejected(adapter, "同时支持和拒绝")

    def test_adapter_rejects_missing_required_binding(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["tool_bindings"]["read"] = []
        self._assert_adapter_rejected(adapter, "缺少 required capability binding")

    def test_adapter_rejects_unknown_fallback(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        adapter["fallbacks"] = [{"rule_id": "unknown", "reason": "invalid"}]
        self._assert_adapter_rejected(adapter, "fallback rule 未知")

    def test_adapter_rejects_duplicate_fallback(self):
        adapter = copy.deepcopy(tool_registry.TOOL_ADAPTERS["claude"])
        fallback = {"rule_id": "isolated-to-single-context", "reason": "fallback"}
        adapter["fallbacks"] = [fallback, copy.deepcopy(fallback)]
        self._assert_adapter_rejected(adapter, "fallback rule 未知或重复")


if __name__ == "__main__":
    unittest.main()
