# Changelog

本文件从 2026-09-12 起记；此前无版本惯例，历史变更只追溯安装台账。

## 1.1.0 — 2026-09-12

来源实验：`C:\ZYS\Code\lab-area\exp\2026-09-11-claude-workflow-harness\`，经 skill-auditor 静态审计与 better-harness 0.7.0-alpha1 证据审计后同步。

- §1.1 新增「Context→追问→执行环」：非平凡任务先读最小上下文，目标/约束/验收缺失先问 1-3 个反向问题；明确机械改动不反问。
- §1.1 新增「Prompt → Context → Harness」分层：三者缺一时标缺口，不靠模型猜。
- §1.1 新增「角色边界」：AI 负责整理/初稿/疑点/检查，人负责目标/边界/取舍/最终结论。
- §1.1 新增「确认前先完成可授权准备」：只读调查先行，写入与不可逆动作留在确认后。
- §1.3 交付规则加证据回执：结果、改动范围、验证证据、未完成项/风险。
- §1.5 规范驱动产物改为宿主解耦：以项目实际 workflow contract/规格/状态机为准，不硬编码路径。
- §3 Agent 切片改为宿主实际执行计划/合同优先，移除固定 `02-design/execution-plan.md`。
- §3 新增 Harness 审计触发：改 Skill/规则/Hook 或出现返工、验证遗漏、规则冲突时显式运行 `/better-harness`。
- §3 Hook 规则改为宿主解耦：以 `settings.json` 实际挂载的 PreToolUse hooks 为准，移除固定 Claude/pi 路径。
- 新增 `CHANGELOG.md`、`references/MAINTENANCE.md`；evals 从 2 个 case 补到 5 个，model 字段更新为 `claude-haiku-4-5`。

验证：新 CLI 显式 `/code-change-workflow` 可加载全部新规则（证据见实验目录 `VERIFICATION.md`）。未验证：自然语言自动触发（headless `-p` 会话不注入 skill 清单）、eval runner（`claude plugin eval` 被组织 early-access gate 拦截）。

## evals 迁移到官方 runner 布局 — 2026-09-12（资产更新，不 bump skill 版本：SKILL.md 正文零改动）

- CLI 2.1.269 实测 eval 组织门已开放；旧 `evals/eval.yaml + cases/*.yaml`（v1alpha1）布局 runner 发现数为 0，从未真跑过。
- 5 个 case 全量迁移为 `evals/<case>/case.yaml`（schema_version "1.0"）；判词从 `output_contains` 改为确定性 `regex` grader（pattern 贴 SKILL.md 原词）；bug-fix、delivery-evidence 用 `scaffold_script` 在沙箱 cwd 落 fixture（`add_dirs` 只授读权限、不复制文件，已二进制+沙箱实证）。
- 旧布局存档于实验目录 `evals-legacy-archive/` 后删除；最终全量 5/5 绿（258s、$0.17），research-no-route 另跑 3/3 稳；证据见实验目录 `eval-runner-evidence/`。
- 附带证据：全部 eval trace 中子会话第一个工具调用均为 Skill code-change-workflow，自然语言自动触发在 eval 载体下已验证（headless `-p` 不注入清单的结论仅限该载体）。

## 1.0.0 — 2026-07-29（追认）

- 由全局 `CLAUDE.md` 瘦身迁出（台账事件 `claude-md-slimming-20260729`）：原 §1.1-1.4 / §2 / §3 / §4 成为改前/改中/改后清单、AI 代码审查方法论、调试工作流、Agent 调度、止血回退。
- 2026-07-29 至 2026-09-11 之间的具体演进 unknown：无版本字段、无变更记录，安装台账只有出处登记，不补编。
