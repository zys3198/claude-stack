域归属：编码（审查/优化 skill 文件）/ ai-coding-guide 已加载 / 留在本路由

| 契约项 | 内容 |
|---|---|
| 分类 | 路由指南维护（审查/优化 guide skill） |
| 主路径 | `guide-skill-auditor` |
| 组合 | 若审查发现路由逻辑/触发词/行为变化 → 叠 `darwin-skill` 做 skill 演化；纯小修则补 eval 用例 |
| 闸门 | review（skill 行为影响后续路由，改前需确认范围；不自动 commit/push） |
| 下一步 | 路由判断完成；用户确认后进入 `guide-skill-auditor` 审查 `~/.claude/skills/learning-guide`，再决定小修还是演化 |
