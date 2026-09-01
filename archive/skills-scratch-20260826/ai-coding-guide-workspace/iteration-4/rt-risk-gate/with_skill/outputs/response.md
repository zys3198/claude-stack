域归属：编码（改 auth 权限 + 数据库迁移）  
ai-coding-guide 已在本会话加载：YES

| 项 | 路由契约 |
|---|---|
| **分类** | 开发新功能 / 高风险改动（命中 auth + DB 迁移两个高风险域） |
| **主路径** | 交付状态机 medium/large：REQUIREMENT → DESIGN → IMPLEMENT → REVIEW → TEST → SUMMARY，禁止单 Agent 直接改 |
| **组合** | 独立阶段 Agent（DESIGN/IMPLEMENT/REVIEW/TEST 分离）+ `security-review` 专项 + `verification-before-completion` 生效验证 + 迁移回滚方案审查 |
| **闸门** | REQUIREMENT 用户确认门禁（不可跳过）、设计/角色矩阵书面依据、权限变更安全审查、迁移脚本 review + 备份回滚方案、提交前 `git diff --cached --stat` 确认 |
| **下一步** | 当前不能直接让 agent 改；先由你确认：1）改哪些角色/权限点、2）迁移范围与回滚方案、3）项目角色矩阵/设计文档依据，再进入 REQUIREMENT 阶段 |

**一句话结论**：这是高风险的权限+数据迁移组合，必须走完整交付状态机并由你逐项确认后，才能分阶段交给独立 Agent 执行。
