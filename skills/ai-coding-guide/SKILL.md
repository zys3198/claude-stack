---
name: ai-coding-guide
description: Use when the user asks which skill/tool/ecosystem to use in Claude Code, how installed plugins/skills differ or compare, starts any coding task needing routing, or needs structured, resumable, multi-stage delivery (or to resume an existing workflow). 本 skill 是 Claude Code 编码域总入口路由器，负责编码任务与前端视觉请求的开工分诊和路径选择。中文触发：用哪个工具、X和Y区别/冲突吗、该用什么、怎么配合、哪个更好、刚装了X插件、X不能用了、重任务跨会话/分阶段交付、继续之前的任务、断点续跑、这篇文章/做法能不能优化进路由；页面/界面/UI/落地页/登录页的视觉方向与实现也走本路由（前端视觉子路径）。不用于：中文技术文章写改审（走 article-writing-guide）、学习调研（走 learning-guide）。<!-- v2.3.0 -->
---

# ai-coding-guide（编码域总入口系统）

## 编码路由（分诊层）

本系统同时承担编码域路由。**先读 [references/routing.md](references/routing.md) 分诊**：非交付型任务（工具选型/调试/理解代码/澄清/学习陪跑等）按其中分类路径执行，不进状态机；交付型任务（要写代码并交付可验收结果）由 routing.md Step 0.4 定档——1-2 步单文件机械改保留精简路径，其他非机械代码变更默认先走 Matt `/grill-with-docs`，命中升档信号或用户明说规模时才进入下方「必须执行」状态机；前端视觉任务读 [references/frontend-visual.md](references/frontend-visual.md)。

### Matt skill 调用提示

命中 Matt 路径时，路由输出必须同时给出具体 skill 和手动命令（例如 `/diagnosing-bugs`），不能只写“使用 Matt”。按插件 v1.2.3 的 invocation 分类处理：

- **user-invoked**：`ask-matt`、`grill-with-docs`、`triage`、`improve-codebase-architecture`、`setup-matt-pocock-skills`、`to-spec`、`to-tickets`、`implement`、`wayfinder`、`grill-me`、`handoff`、`teach`、`to-questionnaire`、`wait-what`。必须提醒用户手动调用并等待，不得假装自动执行。
- **model-invoked**：`prototype`、`diagnosing-bugs`、`research`、`tdd`、`domain-modeling`、`codebase-design`、`code-review`、`resolving-merge-conflicts`、`wizard`、`grilling`、`writing-for-agents`。模型可按任务自动调用；路由仍必须显示对应手动命令，用户明确想自己调用时才等待。
- user-invoked skill 可以驱动 model-invoked skill，但不能自动调用另一个 user-invoked skill；本路由不把一串 Matt skill 静默展开。主流程由用户逐个手动推进：`/grill-with-docs` → `/to-spec` →（跨会话/并行/多人/需显式阻塞时 `/to-tickets`）→ `/implement`。各入口内部可按规则驱动 model-invoked skill；`implement` 在预先约定的 seam 按需驱动 `/tdd`，提交前必须完成 `/code-review`。
- `implement` 的原始 skill 要求 commit；本地规则优先，commit 前仍必须展示范围和 `git diff --cached --stat`，得到用户确认后才能提交。

## 必须执行

1. 将用户当前目录设为 `PROJECT_ROOT`，不向父目录寻找或自动切换项目。先读取宿主项目指令，再运行 `python3 <SKILL_ROOT>/scripts/inspect_context.py .` 发现实际项目约定。
2. 开始任何阶段前读取 [通用核心原则](rules/principles.md) 和当前 adapter 补充规则 [rules/core.md](rules/core.md)。`rules/` 不会被宿主自动加载；`build_stage_prompt.py` 按 [rules/manifest.json](rules/manifest.json) 确定性注入通用原则、adapter 补充规则、当前阶段规则，以及由项目证据命中的专项规则。
3. 完整流程读取 [references/workflow-contract.md](references/workflow-contract.md)。medium/large 额外读取 [references/agent-execution.md](references/agent-execution.md) 和 [references/runtime-core.md](references/runtime-core.md)，并且只加载一个匹配的 `adapters/` 实现。
4. 每阶段优先用 `workflow_state.py prepare ... --emit-prompt` 一次完成模板准备和提示生成，再执行 `start → finish`；仅对已经 prepare 的恢复状态单独调用 `build_stage_prompt.py`。REQUIREMENT 和 SUMMARY 由协调者在当前上下文执行，不创建阶段 Agent；isolated 模式的其他 route 阶段在 prompt 后、start 前增加 `spawn → assign`。只有宿主真实返回 executor ID 后才能 `assign`，并登记 adapter 要求的 `executor_type`。
5. REQUIREMENT 按 [references/clarify-requirements.md](references/clarify-requirements.md) 完成证据分析、用户交互和需求报告。报告通过内容校验后必须向用户展示摘要并等待明确确认；只有确认后才能执行 `approve --stage REQUIREMENT --user-confirmed` 并进入 DESIGN。DESIGN 及后续 isolated 阶段只读取清单允许的上游产物和当前必要证据，协调者不得代写。

脚本仅依赖 Python 3.8+ 标准库。Python 不可用时读取 [references/manual-runtime.md](references/manual-runtime.md) 执行等价门禁，不得跳过。

## 按需读取

- 前端、后端、Go、SQL 和设计稿专项规则由阶段 Prompt 自动选择；分类不明确但用户或项目已确认时，用 `build_stage_prompt.py --profile <id>` 显式追加。
- 审查、测试和知识沉淀规则按阶段自动注入，唯一事实源：[rules/stages/review.md](rules/stages/review.md)、[rules/stages/test.md](rules/stages/test.md)、[rules/stages/knowledge.md](rules/stages/knowledge.md)；专项叠加由 [rules/manifest.json](rules/manifest.json) 选择。
- 用户明确要求预览或部署：[references/preview-deploy.md](references/preview-deploy.md)

无法分类时先检查项目证据；不要为了“可能相关”注入全部专项规则。混合项目可以组合多个 profile。

## 不可绕过

- `agents/manifest.json` 内联逻辑角色元数据、职责和上游阶段；`templates/manifest.json` 内联产物语义并映射模板文件和路径；`config/runtime-contract.json` 与 `config/runtime-manifest.json` 定义生命周期和 Claude 能力；`config/tools-contract.json` 定义中立工具契约。adapter 只映射少量宿主执行器，不复制逻辑角色清单。
- `prepare` 只生成缺失模板并记录基线，不覆盖已有产物。阶段执行者填写模板并删除所有 `{{...}}`；不要为标题措辞或排版反复返工。
- medium/large 的 REQUIREMENT 和 SUMMARY 由协调者执行；DESIGN、IMPLEMENT、REVIEW、TEST 分别使用独立 Agent。KNOWLEDGE 是条件阶段：有新增可复用知识才创建 Agent，否则用 `decide-knowledge --decision skip --reason ...` 留下依据并跳过；不得按 size 一刀切。宿主确实不支持时才允许带具体原因的 `single-context` 降级。
- REQUIREMENT 的用户确认门禁在 `auto` 和 `manual` 模式下都不可跳过；没有用户明确确认时不得创建 DESIGN 执行者。
- 保护用户已有改动，不自动 stash、commit、push、部署或执行其他未授权外部写操作。
- 只依据真实命令、观察和产物宣布完成，明确区分 passed、failed、blocked、not-run。
