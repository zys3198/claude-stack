域归属：编码域（审查/优化 guide skill 属于 ai-coding-guide 覆盖的「路由指南维护」分类）  
ai-coding-guide 在当前会话？ YES  
若域归属非编码 → 不适用

---

**分类：** 路由指南维护  
**主路径：** `guide-skill-auditor`（已安装在 `~/.claude/skills/guide-skill-auditor`）  
**组合：** 无  
**闸门：** 按 `guide-skill-auditor` 内置的 skill 审查清单执行；若涉及行为/结构变更，补充 `darwin-skill` 或最小改后补 eval 用例  
**下一步：** 直接执行 `guide-skill-auditor`，目标为 `learning-guide` skill，只做审查判断不自动改文件
