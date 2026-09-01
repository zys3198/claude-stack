**触发门禁**：article-writing-guide 相关？YES —— 写作域「审校」请求，命中 §1 阶段⑧。目标 skill 存在性：`multi-review-pipeline` 在本会话 available skills 列表 ✓。

---

**① 分类**
审校（阶段⑧）· 多维度并行审稿 · **报告型**（只出报告不改）

**② 主路径**
`multi-review-pipeline` —— 命中 §7 示例「先出审校报告我看看，别改」→ **停在报告阶段**，不进入批量改稿环

**③ 组合**
无下游执行步骤（本次只出报告）。报告交付后若你要求按修订清单改稿，才串 `edit-article`（结构）→ `human-writing`（文风）→ 可选 `chinese-markdown-normalizer`（排版）；本次不预执行

**④ 闸门**
- **只读不改**：审稿报告不改稿、不落盘、不动原文件
- **CHECKPOINT 已确认**：你已明确「只出报告不改」→ 范围=单点报告，不跑全链路
- 报告内的确定性论断（React 渲染机制、API 行为）受证据门槛约束：源码/官方文档优先，标的 `needs evidence` 处不得装成事实

**⑤ 下一步**
执行 `multi-review-pipeline` 审校这篇 React 渲染优化文章，产出多维度并行审稿报告（并行审 → 修订清单，停在此处），等你确认后再决定是否批量改。需要你提供文章路径或内容。
