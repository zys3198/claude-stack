域归属：编码（PRD 落地 = 有需求文档的交付型任务）  
ai-coding-guide 在当前会话：YES

| 项 | 路由契约 |
|---|---|
| **分类** | 有需求文档（PRD 已就绪，进入落地规划） |
| **主路径** | 手动拆 4-6 个实现切片 + 输出 `PLAN.md` |
| **组合** | `superpowers:writing-plans`（辅助计划拆解，当前会话可用）；`to-issues` / `to-prd`（可选，若需同步生成任务/需求项） |
| **闸门** | `PLAN.md` 计划确认门禁——用户明确确认后方可进入实现；若升档 medium/large，REQUIREMENT 用户确认门禁不可跳过 |
| **下一步** | 先定位 PRD 文件并跑 `inspect_context.py` 拿项目证据，再按 PRD 拆切片写 `PLAN.md`，等用户确认后实现 |

**需补齐的 1 个关键缺口**：PRD 文件路径在哪里？以及规模预期是 small / medium / large 哪个档位（不说会被自判 small）。
