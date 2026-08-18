# 编码路由 stopgap（待 Phase 2 重设计）

来源：ai-coding-guide v1.9.0（已归档 `~/.claude/archive/ai-coding-guide-v1.9.0/`，完整分类树、生态详情、test-prompts、维护纪律均在归档内）。本文件只保 Phase 1→2 过渡期最常用的分诊信号；Phase 2 将把完整路由树并入本系统并重写本文件。

## 先分诊：任务是不是交付型？

- **交付型**（要写代码并交付可验收结果）→ 走 `SKILL.md`「必须执行」状态机。口令必须明说规模 small/medium/large，不说会被自判 small。
- **非交付型** → 按下表分诊，不进状态机。

## 非交付型分诊表

| 信号 | 去向 |
|---|---|
| 工具/插件选型、X 和 Y 区别、刚装了 X、怎么配合 | 查归档 guide 的 `references/ecosystems.md` 给主路径+条件路径；不自检就推荐不存在的工具 = 最严重路由失败 |
| 调试 bug、构建错误 | `superpowers:systematic-debugging`（条件路径）；手动：复现 → 定位 → 最小修复 → 验证；复杂走 `code-change-workflow` §2 |
| 理解代码、谁调用了 Y | `lean-ctx` 读结构；调用链/影响面 → `gitnexus-*` |
| 需求不清、没思路、判级 | `expose-unknowns`；深度采访 → `superpowers:brainstorming`（条件路径） |
| 提交前检查、轻量 review | 内置 `code-review`；高风险叠加安全审查 |
| 学习陪跑（我先想/你纠偏） | `ai-coding-coach`；说话层归属 → `learning-personas` |
| 前端视觉（页面/UI/动画） | `hallmark`（新页面）/ `impeccable`（提质）/ `emil-design-eng`（动画） |
| 普通小改、机械任务 | 直接最小实现 + 必要验证，纪律见 `code-change-workflow` |

## 闸门底线（任何路径都守）

- 中高风险改动：失败测试或最小复现 → 实现 → 相关 test/build → 必要 review。
- 不可逆/外发（commit / push / 删除 / 密钥 / DB 写）：先展示范围或 diff，用户确认后执行。
- 插件 skill（`superpowers:*` / `mattpocock-skills:*` 等）是条件路径：当前会话可调用清单出现才走；matt 系为 user-invoked，模型调不到时提醒用户手动启用。
