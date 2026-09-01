按 `ai-coding-guide` 分诊结果如下：

| 项 | 判断 |
|---|---|
| **分类** | 开发新功能 · Step 0.4 进交付状态机档（用户已明示「改造任务比较大」「跨几个会话」） |
| **主路径** | `ai-coding-guide` 完整交付状态机：REQUIREMENT → DESIGN → IMPLEMENT → REVIEW → TEST → [KNOWLEDGE] → SUMMARY，状态由 `<SKILL_ROOT>/scripts/workflow_state.py` 写入 `artifacts/<task-slug>/workflow-state.json`，跨会话断点续跑 |
| **组合** | `superpowers:writing-plans`（条件路径，当前会话可用则走）辅助切分阶段；`code-change-workflow` 管理改前/改中/改后清单；改动完成后走横切收尾验证 |
| **闸门** | 1. REQUIREMENT 必须输出需求报告并由用户明确确认后才能进 DESIGN；2. DESIGN 方案、影响文件、风险、回滚、验证命令明确；3. REVIEW 阻断问题为零；4. TEST 失败/阻塞/未运行分明；5. 外部写操作（commit/push/删文件）逐项确认 |
| **下一步** | 请先定两个事：① 任务 slug（用于 `artifacts/<slug>/`）；② 规模口令 `medium` 或 `large`（跨会话改造默认不低于 medium）。确认后即可执行 `workflow_state.py init --slug <slug> --size <medium|large>` 启动状态机。 |
