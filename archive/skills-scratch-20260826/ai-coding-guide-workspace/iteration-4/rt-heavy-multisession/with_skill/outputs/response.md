**域归属：** 编码域 —— 大型代码改造、跨会话交付管理。  
**ai-coding-guide 在当前会话：** YES

---

**分类 / 主路径 / 组合 / 闸门 / 下一步**

| 项 | 路由契约 |
|---|---|
| **分类** | 交付型任务 —— 重任务 / 跨会话交付（`开发新功能` Step 0.4 进状态机档） |
| **主路径** | `ai-coding-guide` 交付状态机：澄清(REQUIREMENT) → 设计(DESIGN) → 实现(IMPLEMENT) → 审查(REVIEW) → 测试(TEST) → 总结(SUMMARY)；状态由 `workflow-state.json` 持久化，支持跨会话断点续跑 |
| **组合** | `superpowers:writing-plans`（条件路径，当前会话可用则用于拆阶段计划）+ `code-change-workflow`（复杂/高风险改动用改前/改中/改后清单）+ `superpowers:verification-before-completion`（条件路径，收尾验证） |
| **闸门** | 1) REQUIREMENT 阶段必须输出需求摘要并等待用户明确确认，未确认不得进入 DESIGN；2) 跨会话依赖 `workflow-state.json` 作为唯一状态源，每阶段 start/finish 必须登记；3) 涉及架构/权限/DB/安全等高风险域须先设计确认；4) 任何不可逆操作（commit/push/删除/迁移/外部发布）须先展示范围并单独确认 |
| **下一步** | 在当前项目目录执行 `python3 C:\Users\zys31\.claude\skills\ai-coding-guide\scripts\inspect_context.py .` 收集项目证据，然后进入 REQUIREMENT 阶段：用 `workflow_state.py prepare REQUIREMENT --emit-prompt` 生成阶段提示并开始需求澄清 |

**说明：** 用户已明说“跨几个会话”，属于 Step 0.4 升档信号，不进精简路径，必须走完整交付状态机以保证可断点续跑和阶段验收。
