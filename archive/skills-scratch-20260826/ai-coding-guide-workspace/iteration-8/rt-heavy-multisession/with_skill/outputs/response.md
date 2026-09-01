## 开工路由判断（ai-coding-guide）

**分类：** 开发新功能 — 重任务 / 跨会话交付（命中 Step 0.4 升档信号：用户明说「比较大」「跨几个会话」）

**主路径：** `ai-coding-guide` 交付状态机  
`REQUIREMENT → DESIGN → IMPLEMENT → REVIEW → TEST → SUMMARY`，状态写入 `workflow-state.json` 实现断点续跑。

**组合：**  
- 核心：`workflow_state.py prepare/start/finish` 阶段管理  
- 复杂/高风险改造：`code-change-workflow`（改前/改中/改后清单 + Verify 分级）  
- 条件路径：`superpowers:writing-plans`（计划探索）、`superpowers:verification-before-completion`（收尾验证）——当前会话可调用时才启用

**闸门：**  
- **硬门**：REQUIREMENT 阶段必须完成证据分析、产出需求报告并向用户展示摘要，等待明确确认后才能 `approve --stage REQUIREMENT --user-confirmed` 进入 DESIGN。  
- **阶段门**：每阶段先 `prepare --emit-prompt` → 再 `start → finish`；DESIGN/IMPLEMENT/REVIEW/TEST 各自独立 Agent。  
- **收尾门**：产生产品代码改动后进横切收尾验证（build / lint / test / run 真实流程），不凭"应该没问题"交付。

**下一步：**  
用户已暗示 large 规模，下一步是确认 **现在是否启动交付状态机进入 REQUIREMENT 阶段**；若确认，先跑 `python3 <SKILL_ROOT>/scripts/inspect_context.py .` 收集项目证据，再开始需求澄清。
