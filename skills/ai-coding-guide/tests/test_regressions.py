import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_stage_prompt import build_prompt  # noqa: E402
from inspect_context import discover  # noqa: E402
from rule_registry import stage_rule  # noqa: E402
from validate_artifacts import sections, validate_file  # noqa: E402
from validate_plan import validate_execution_plan  # noqa: E402
from agent_registry import STAGE_EXECUTION, STAGE_ROLES  # noqa: E402
from template_registry import required_artifacts  # noqa: E402


def run_script(name, *args, check=True):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        text=True,
        capture_output=True,
        check=check,
        env=environment,
    )


class MarkdownRegressionTests(unittest.TestCase):
    def test_code_comment_is_not_a_heading(self):
        text = """## 验证与验收

```bash
# 编译
go build ./...
```

## 风险、恢复与回滚
无
"""
        items = dict(sections(text))
        self.assertIn("go build ./...", items["验证与验收"])
        self.assertNotIn("编译", items)

    def test_plan_with_commented_shell_commands_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "execution-plan.md"
            path.write_text(
                """# 执行计划
## 目标与完成定义
完成可观察功能。
## 上下文与范围
修改 `src/app.py`。
## 执行任务
### 任务 T1：实现功能
- 状态：`pending`
- 目标文件：`src/app.py`
## 验证与验收
```bash
# 运行测试
python3 -m unittest
```
## 风险、恢复与回滚
可回滚。
## 进度
- [ ] T1
## 决策记录
- 使用现有接口。
""",
                encoding="utf-8",
            )
            errors, metrics = validate_execution_plan(path, require_pending=True)
            self.assertEqual([], errors)
            self.assertEqual(1, metrics["pending"])

    def test_plan_error_names_file_and_section(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "execution-plan.md"
            path.write_text("# 执行计划\n## 验证与验收\n无命令\n", encoding="utf-8")
            errors, _ = validate_execution_plan(path, require_pending=True)
            self.assertTrue(
                any("02-design/execution-plan.md: 验证与验收" in error for error in errors),
                errors,
            )

    def test_required_report_heading_cannot_be_omitted(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "test-report.md"
            report.write_text(
                "# 测试报告\n\n## 测试范围\n范围充分。\n\n"
                "## 测试命令\n`python3 -m unittest`\n\n"
                "## 测试结果\n通过。\n\n## 未运行项与剩余风险\n无。\n",
                encoding="utf-8",
            )
            errors = validate_file(report, "04-test/test-report.md")
            self.assertTrue(
                any("缺少必要章节：风险与覆盖矩阵" in error for error in errors),
                errors,
            )

    def test_project_without_e2e_can_use_existing_test_layers(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "test-report.md"
            report.write_text(
                "# 测试报告\n\n## 测试范围\n接口变更。\n\n"
                "## 项目测试能力\n现有 `tests/unit` 和 `pytest`，没有 E2E 框架。\n\n"
                "## 风险与覆盖矩阵\n逻辑 | unit | `pytest` | 通过\n\n"
                "## 测试命令\n`pytest`\n\n## 测试结果\n通过。\n\n"
                "## 未运行项与剩余风险\n无。\n",
                encoding="utf-8",
            )
            errors = validate_file(report, "04-test/test-report.md")
            self.assertEqual([], errors)

    def test_api_change_report_requires_fixed_generated_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "artifacts/task/03-code/change-report.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                "# 变更报告\n\n## 变更摘要\n新增批量创建接口。\n\n"
                "## 修改文件\n`src/api.py`。\n\n## 验证结果\n接口测试通过。\n\n"
                "## 计划偏差\n无。\n\n## API 接口文档\n已生成：`03-code/api-docs.md`\n\n"
                "## 剩余风险\n无。\n",
                encoding="utf-8",
            )
            errors = validate_file(report, "03-code/change-report.md")
            self.assertTrue(any("接口文档不存在或为空" in error for error in errors), errors)

            document = root / "artifacts/task/03-code/api-docs.md"
            document.write_text(
                "# Batch API\n\n## 变更概览\n新增接口。\n\n## 通用约定\nJSON。\n\n"
                "## 接口\n### POST /batch\n请求、响应、权限、错误和兼容性均已记录。\n",
                encoding="utf-8",
            )
            self.assertEqual([], validate_file(report, "03-code/change-report.md"))

    def test_generated_fallback_api_document_must_be_filled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "artifacts/task/03-code/change-report.md"
            document = root / "artifacts/task/03-code/api-docs.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                "# 变更报告\n\n## 变更摘要\n新增接口。\n\n## 修改文件\n`api.py`。\n\n"
                "## 验证结果\n通过。\n\n## 计划偏差\n无。\n\n"
                "## API 接口文档\n已生成：`03-code/api-docs.md`\n\n## 剩余风险\n无。\n",
                encoding="utf-8",
            )
            shutil.copyfile(SKILL_ROOT / "templates/api-docs.md", document)
            errors = validate_file(report, "03-code/change-report.md")
            self.assertTrue(any("模板占位项" in error for error in errors), errors)
            document.write_text(
                "# API 接口文档\n\n## 变更概览\n新增批量接口。\n\n"
                "## 通用约定\nJSON 和 Bearer 认证。\n\n## 接口\n"
                "### POST /batch\n请求、响应、权限、错误和兼容性均已记录。\n",
                encoding="utf-8",
            )
            self.assertEqual([], validate_file(report, "03-code/change-report.md"))


class ContextAndPromptTests(unittest.TestCase):
    def test_every_stage_has_nonempty_stage_rules(self):
        for stage in STAGE_ROLES:
            self.assertTrue(stage_rule(stage).strip(), stage)

    def test_context_discovers_project_rules_and_nested_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("rules", encoding="utf-8")
            (root / "backend").mkdir()
            (root / "backend/go.mod").write_text("module example", encoding="utf-8")
            (root / "node_modules/pkg").mkdir(parents=True)
            (root / "node_modules/pkg/package.json").write_text("{}", encoding="utf-8")
            self.assertEqual(["backend/go.mod"], discover(root, ("go.mod", "package.json")))
            output = json.loads(run_script("inspect_context.py", root).stdout)
            self.assertEqual(["AGENTS.md"], output["instructions"])

    def test_design_prompt_requires_agent_self_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("project rules", encoding="utf-8")
            artifacts = root / "artifacts/task"
            artifacts.mkdir(parents=True)
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["REQUIREMENT", "DESIGN"],
                "stages": {
                    "REQUIREMENT": {"artifacts": ["01-requirement/requirement-report.md"]},
                    "DESIGN": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "DESIGN", "设计功能", [])
            self.assertIn("validate_plan.py", prompt)
            self.assertIn("--require-pending", prompt)
            self.assertIn("由当前执行者修改产物并重试", prompt)
            self.assertIn("AGENTS.md", prompt)
            self.assertNotIn("## 用户目标", prompt)
            self.assertNotIn("设计功能", prompt)

    def test_prompt_embeds_only_selected_upstream_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts/task"
            report = artifacts / "01-requirement/requirement-report.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                "# 需求报告\n\n## 目标与背景\n不应进入交接的长背景 TOKEN_NOISE。\n\n"
                "## 范围\n批量创建接口。\n\n## 排除项\n无。\n\n"
                "## 决策与理由\n保持兼容。\n\n## 验收标准\n事务失败全部回滚。\n\n"
                "## 假设与证据\n`api.py`。\n\n## 未决问题\n无。\n",
                encoding="utf-8",
            )
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["REQUIREMENT", "DESIGN"],
                "stages": {
                    "REQUIREMENT": {"artifacts": ["01-requirement/requirement-report.md"]},
                    "DESIGN": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "DESIGN", "原始需求不应重复", [])
            self.assertIn("## 精简上游交接", prompt)
            self.assertIn("事务失败全部回滚", prompt)
            self.assertNotIn("TOKEN_NOISE", prompt)
            self.assertIn("仅在精简交接不足时读取", prompt)

    def test_prompt_injects_stage_and_detected_profile_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "backend").mkdir()
            (root / "backend/go.mod").write_text("module example", encoding="utf-8")
            (root / "backend/handler.go").write_text("package backend", encoding="utf-8")
            (root / "backend/migrations").mkdir()
            (root / "backend/migrations/001.sql").write_text("SELECT 1", encoding="utf-8")
            artifacts = root / "artifacts/task"
            requirement = artifacts / "01-requirement/requirement-report.md"
            requirement.parent.mkdir(parents=True)
            requirement.write_text("需要修改后端数据库事务，入口为 `handler.go`。", encoding="utf-8")
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["REQUIREMENT", "DESIGN"],
                "stages": {
                    "REQUIREMENT": {"artifacts": ["01-requirement/requirement-report.md"]},
                    "DESIGN": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "DESIGN", "设计数据变更", [])
            self.assertIn("## 当前阶段规则", prompt)
            self.assertIn("按“需求报告 → 项目规则", prompt)
            self.assertIn("规则 ID：`backend`", prompt)
            self.assertIn("规则 ID：`golang`", prompt)
            self.assertIn("规则 ID：`sql`", prompt)
            self.assertIn("选择依据：", prompt)
            self.assertIn("03-code/api-docs.md", prompt)

    def test_explicit_profile_handles_ambiguous_project(self):
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
            prompt = build_prompt(state, "DESIGN", "", [], ["frontend"])
            self.assertIn("规则 ID：`frontend`", prompt)
            self.assertIn("选择依据：explicit", prompt)

    def test_review_prompt_contains_severity_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts/task"
            artifacts.mkdir(parents=True)
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["DESIGN", "IMPLEMENT", "REVIEW"],
                "stages": {
                    "DESIGN": {"artifacts": ["02-design/execution-plan.md"]},
                    "IMPLEMENT": {"artifacts": ["03-code/change-report.md"]},
                    "REVIEW": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "REVIEW", "审查实现", [])
            self.assertIn("P0 为安全漏洞", prompt)
            self.assertIn("存在 P0/P1 时结论必须为不通过", prompt)
            self.assertIn("只审查不修改代码", prompt)

    def test_test_prompt_uses_existing_layers_and_allows_only_test_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts/task"
            artifacts.mkdir(parents=True)
            state = {
                "project_root": str(root),
                "artifacts_dir": str(artifacts),
                "requires_design_artifacts": False,
                "route": ["REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST"],
                "stages": {
                    "REQUIREMENT": {"artifacts": []},
                    "DESIGN": {"artifacts": []},
                    "IMPLEMENT": {"artifacts": []},
                    "REVIEW": {"artifacts": []},
                    "TEST": {"prepared_at": "now", "artifacts": []},
                },
            }
            prompt = build_prompt(state, "TEST", "验证批量接口", [])
            self.assertIn("写入级别：`test-write`", prompt)
            self.assertIn("不得修改生产代码", prompt)
            self.assertIn("仓库已有 E2E", prompt)
            self.assertIn("仓库没有 E2E 时不强制创建", prompt)


class LifecycleTests(unittest.TestCase):
    def test_prepare_can_emit_prompt_in_one_cli_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = Path(run_script(
                "workflow_state.py", "init", "--project-root", root,
                "--slug", "one-call", "--size", "small", "--mode", "auto",
                "--execution-mode", "single-context", "--coordinator-id", "main",
            ).stdout.strip())
            result = run_script(
                "workflow_state.py", "prepare", "--state", state_path,
                "--stage", "SOLO", "--emit-prompt", "--request", "修复边界行为",
            )
            self.assertIn("# DevFlow 阶段任务：SOLO", result.stdout)
            self.assertIn("修复边界行为", result.stdout)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIsNotNone(state["stages"]["SOLO"]["prepared_at"])


    def fill_stage_artifacts(self, state_path, stage):
        state = json.loads(state_path.read_text(encoding="utf-8"))
        artifact_root = Path(state["artifacts_dir"])
        for relative in required_artifacts(stage, False):
            path = artifact_root / relative
            text = path.read_text(encoding="utf-8")
            replacements = {
                "{{说明当前实现、关键模块、仓库相对路径、约束和非目标}}": "当前实现位于 `src/app.py`，仅修改该文件。",
                "{{动作导向的任务名}}": "实现目标行为",
                "{{无，或任务 ID}}": "无",
                "{{仓库相对路径}}": "src/app.py",
                "{{工作目录}}": ".",
                "{{项目原生验证命令}}": "python3 -m unittest",
                "{{明确写“通过”或“不通过”；只有无阻断问题时才能写“通过”}}": "通过，无阻断问题。",
                "{{无接口变动时写“无接口变动”；有新增、修改或删除时生成文档并写“已生成：`03-code/api-docs.md`”}}": "无接口变动",
                "{{无接口变动时写“无接口变动”；有新增、修改或删除时生成文档并写“已生成：`01-solo/api-docs.md`”}}": "无接口变动",
                "{{列出仓库实际已有的测试层级及证据路径/配置/命令；若已有 E2E，明确其覆盖边界；若没有，不要为流程强行引入新框架}}": "现有 `devflow/tests` 与 `python3 -m unittest`；没有浏览器 E2E 框架。",
                "{{逐项记录“验收标准或风险 | 项目已有的合适测试层级 | 用例或命令 | 结果”；项目已有 E2E 且本次行为属于其覆盖边界时，必须包含相应 E2E 用例}}": "核心逻辑 | unit | `python3 -m unittest` | 通过",
            }
            for source, target in replacements.items():
                text = text.replace(source, target)
            text = re.sub(r"\{\{[^{}]+\}\}", "已根据当前证据完成并验证。", text)
            path.write_text(text, encoding="utf-8")

    def test_coordinator_stages_and_executor_type_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = Path(
                run_script(
                    "workflow_state.py", "init", "--project-root", root,
                    "--slug", "guard", "--size", "medium", "--mode", "auto",
                    "--execution-mode", "isolated", "--host-adapter", "claude",
                    "--coordinator-id", "main-1",
                ).stdout.strip()
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(3, state["execution_policy_version"])
            self.assertEqual("spawn", state["executor_topology"])
            self.assertIsNone(state["run_id"])
            self.assertIsNone(state.get("team_name"))
            for stage_name in ("REQUIREMENT", "SUMMARY"):
                stage = state["stages"][stage_name]
                self.assertEqual("coordinator", stage["executor_type"])
                self.assertEqual("main-1", stage["executor_id"])

            state["stages"]["REQUIREMENT"].update(
                status="completed", artifacts=["01-requirement/requirement-report.md"]
            )
            state.update(current_stage="REQUIREMENT", next_stage="DESIGN")
            state_path.write_text(json.dumps(state), encoding="utf-8")
            run_script("workflow_state.py", "prepare", "--state", state_path, "--stage", "DESIGN")

            rejected = run_script(
                "workflow_state.py", "assign", "--state", state_path, "--stage", "DESIGN",
                "--role", "devflow-architect", "--executor-type", "architect",
                "--executor-id", "agent-1", "--dispatch-tool", "agent",
                "--team-name", state["team_name"], check=False,
            )
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("executor type must be devflow-stage-executor", rejected.stderr)

            run_script(
                "workflow_state.py", "assign", "--state", state_path, "--stage", "DESIGN",
                "--role", "devflow-architect", "--executor-type", "devflow-stage-executor",
                "--executor-id", "agent-2", "--dispatch-tool", "agent",
            )
            resume = json.loads(run_script("workflow_state.py", "resume", "--state", state_path).stdout)
            self.assertEqual("start-assigned", resume["action"])
            self.assertEqual("devflow-stage-executor", resume["executor_type"])
            self.assertEqual("spawn", resume["executor_topology"])
            self.assertIsNone(resume.get("team_name"))

    def test_medium_lifecycle_conditionally_skips_knowledge_without_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = Path(
                run_script(
                    "workflow_state.py", "init", "--project-root", root,
                    "--slug", "full-run", "--size", "medium", "--mode", "auto",
                    "--execution-mode", "isolated", "--host-adapter", "claude",
                    "--coordinator-id", "main-1",
                ).stdout.strip()
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            for index, stage in enumerate(state["route"]):
                if stage == "KNOWLEDGE":
                    resume = json.loads(run_script(
                        "workflow_state.py", "resume", "--state", state_path
                    ).stdout)
                    self.assertEqual("assess-knowledge", resume["action"])
                    run_script(
                        "workflow_state.py", "decide-knowledge", "--state", state_path,
                        "--decision", "skip", "--reason",
                        "只有常规变更和测试结果，没有新增可复用约束",
                    )
                    continue
                run_script("workflow_state.py", "prepare", "--state", state_path, "--stage", stage)
                if STAGE_EXECUTION[stage] == "agent":
                    run_script(
                        "workflow_state.py", "assign", "--state", state_path, "--stage", stage,
                        "--role", STAGE_ROLES[stage], "--executor-type", "devflow-stage-executor",
                        "--executor-id", f"agent-{index}", "--dispatch-tool", "agent",
                    )
                run_script("workflow_state.py", "start", "--state", state_path, "--stage", stage)
                self.fill_stage_artifacts(state_path, stage)
                run_script(
                    "workflow_state.py", "finish", "--state", state_path,
                    "--stage", stage, "--result", "completed",
                )
                if stage == "REQUIREMENT":
                    run_script(
                        "workflow_state.py", "approve", "--state", state_path,
                        "--stage", "REQUIREMENT", "--user-confirmed",
                    )
            run_script("workflow_state.py", "validate", "--state", state_path)
            resume = json.loads(run_script("workflow_state.py", "resume", "--state", state_path).stdout)
            self.assertEqual("completed", resume["action"])
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("KNOWLEDGE", state["route"])
            self.assertEqual("skipped", state["stages"]["KNOWLEDGE"]["status"])
            self.assertEqual("skip", state["stages"]["KNOWLEDGE"]["decision"])
            self.assertEqual("main-1", state["stages"]["SUMMARY"]["executor_id"])
            self.assertEqual("coordinator", state["stages"]["SUMMARY"]["executor_type"])

    def test_large_keeps_knowledge_and_legacy_medium_route_remains_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            large_path = Path(run_script(
                "workflow_state.py", "init", "--project-root", root,
                "--slug", "large-run", "--size", "large", "--mode", "auto",
                "--execution-mode", "isolated", "--host-adapter", "claude",
                "--coordinator-id", "main",
            ).stdout.strip())
            large = json.loads(large_path.read_text(encoding="utf-8"))
            self.assertIn("KNOWLEDGE", large["route"])

            medium_path = Path(run_script(
                "workflow_state.py", "init", "--project-root", root,
                "--slug", "legacy-medium", "--size", "medium", "--mode", "auto",
                "--execution-mode", "isolated", "--host-adapter", "claude",
                "--coordinator-id", "main",
            ).stdout.strip())
            medium = json.loads(medium_path.read_text(encoding="utf-8"))
            medium["route"] = [
                "REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST", "SUMMARY",
            ]
            medium["stages"]["KNOWLEDGE"]["status"] = "skipped"
            medium_path.write_text(json.dumps(medium), encoding="utf-8")
            run_script("workflow_state.py", "validate", "--state", medium_path)

    def test_valuable_medium_knowledge_candidate_enables_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = Path(run_script(
                "workflow_state.py", "init", "--project-root", root,
                "--slug", "knowledge-run", "--size", "medium", "--mode", "auto",
                "--execution-mode", "single-context",
                "--fallback-reason", "test fixture has no agent host",
                "--coordinator-id", "main",
            ).stdout.strip())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            for stage in ("REQUIREMENT", "DESIGN", "IMPLEMENT", "REVIEW", "TEST"):
                state["stages"][stage]["status"] = "completed"
            state.update(current_stage="TEST", next_stage="KNOWLEDGE")
            state_path.write_text(json.dumps(state), encoding="utf-8")

            rejected = run_script(
                "workflow_state.py", "prepare", "--state", state_path,
                "--stage", "KNOWLEDGE", check=False,
            )
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("decide whether to run optional stage", rejected.stderr)
            run_script(
                "workflow_state.py", "decide-knowledge", "--state", state_path,
                "--decision", "run", "--reason",
                "review found a reusable transaction rollback invariant in src/store.py",
            )
            run_script(
                "workflow_state.py", "prepare", "--state", state_path,
                "--stage", "KNOWLEDGE",
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual("run", state["stages"]["KNOWLEDGE"]["decision"])
            self.assertIsNotNone(state["stages"]["KNOWLEDGE"]["prepared_at"])





    def test_requirement_confirmation_is_mandatory_in_auto_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = Path(
                run_script(
                    "workflow_state.py", "init", "--project-root", root,
                    "--slug", "requirement-gate", "--size", "medium", "--mode", "auto",
                    "--execution-mode", "isolated", "--host-adapter", "claude",
                    "--coordinator-id", "main-1",
                ).stdout.strip()
            )
            run_script(
                "workflow_state.py", "prepare", "--state", state_path,
                "--stage", "REQUIREMENT",
            )
            run_script(
                "workflow_state.py", "start", "--state", state_path,
                "--stage", "REQUIREMENT",
            )
            self.fill_stage_artifacts(state_path, "REQUIREMENT")
            run_script(
                "workflow_state.py", "finish", "--state", state_path,
                "--stage", "REQUIREMENT", "--result", "completed",
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual("awaiting_approval", state["status"])
            self.assertEqual("REQUIREMENT", state["awaiting_approval"])
            self.assertEqual("DESIGN", state["next_stage"])

            premature = run_script(
                "workflow_state.py", "prepare", "--state", state_path,
                "--stage", "DESIGN", check=False,
            )
            self.assertNotEqual(0, premature.returncode)
            self.assertIn("approval required for REQUIREMENT", premature.stderr)
            unconfirmed = run_script(
                "workflow_state.py", "approve", "--state", state_path,
                "--stage", "REQUIREMENT", check=False,
            )
            self.assertNotEqual(0, unconfirmed.returncode)
            self.assertIn("requires explicit user confirmation", unconfirmed.stderr)

            resume = json.loads(run_script("workflow_state.py", "resume", "--state", state_path).stdout)
            self.assertEqual("approve", resume["action"])
            self.assertTrue(resume["requires_user_confirmation"])
            self.assertTrue(resume["artifact"].endswith("01-requirement/requirement-report.md"))
            self.assertIn("--user-confirmed", resume["command"])

            run_script(
                "workflow_state.py", "approve", "--state", state_path,
                "--stage", "REQUIREMENT", "--user-confirmed",
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual("in_progress", state["status"])
            self.assertIsNone(state["awaiting_approval"])



if __name__ == "__main__":
    unittest.main()
