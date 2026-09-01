## 开工路由判断

| 项 | 路由契约 |
|---|---|
| **分类** | 路由指南维护（Step 1 信号：「补个触发词进 ai-coding-guide」） |
| **主路径** | `guide-skill-auditor` |
| **组合** | 定位触发词来源文章 → 在 `ai-coding-guide` description 或 `references/routing.md` Step 1 信号表补 1 处 → 必要时补 1 个 eval 用例 |
| **闸门** | 改前展示目标文件与具体插入行；确认触发词来源与插入位置；最小改动 diff 自检 |
| **下一步** | 先确认「这篇文章」是哪篇（请给路径/链接/原文）以及要补的触发词原文，再执行 |

**为什么不是其他路径：** 这是 guide skill 自身的小修，不是用户项目代码交付，不走交付状态机；命中「改 guide 触发词/描述/路由文本」分类，所以主路径用 `guide-skill-auditor` 而不是 `darwin-skill`（后者用于行为变化/较大改造）。
