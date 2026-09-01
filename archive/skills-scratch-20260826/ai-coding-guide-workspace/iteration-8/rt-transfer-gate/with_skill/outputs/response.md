**域归属：** 编码域 / ai-coding-guide 路由指南维护 —— 请求是把外部 AI 编码实践吸收进本路由，命中 routing.md Step 1「外部 AI 编码实践」→「路由指南维护」。  
**ai-coding-guide 在当前会话？** YES（已加载）。  

---

| 项 | 路由契约 |
|---|---|
| **分类** | 路由指南维护 |
| **主路径** | `guide-skill-auditor` |
| **组合** | `references/ecosystems.md`（§轻量迁移闸门 / §重机制黑名单）+ 条件 `darwin-skill`（若评估后发现需改行为/结构时启用） |
| **闸门** | 不自动修改 ai-coding-guide 文件；先由 `guide-skill-auditor` 给出「可吸收 / 应拒绝 / 需改造」结论，并补 eval 用例；涉及重机制（project_wiki 三级库、TECH_SPEC 模板、红线机制完整流水线）时只吸收轻量路由规则，不承接项目级流水线 |
| **下一步** | 调用 `guide-skill-auditor`，把文章要点（project_wiki / TECH_SPEC / 红线机制）作为输入，让它按 ecosystems.md 迁移闸门输出评估结论与建议改动清单 |
