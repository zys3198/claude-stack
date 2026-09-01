## learning-guide 开工路由判断

**触发门禁（先行）：**
- learning-guide 相关？ **NO** —— 「学完的笔记」表明学习已完成，任务是把既有笔记转成公众号文章，属于**知识输出**，不在学习输入域。
- 目标 skill 在当前会话？ `article-writing-guide` **YES**（已装、会话可用）。
- 门禁结论：不进学习域路由表，转写作域。

**路由契约：**

| 项 | 判断 |
|---|---|
| **分类** | 写作任务（知识输出），非学习任务；学习环节已闭环 |
| **主路径** | `article-writing-guide`（写作域路由器），进入其开工路由（问询 → 边学边写/改写路径 §3） |
| **组合** | 无叠加。learning-guide 的「学了要写文 → 串行」规则**不触发**——学习已完成，无需先走 `deep-learn`/`tutorial-maker` 等学习域流程，直接串行交接给写作域，不并联 |
| **闸门** | learning-guide 触发门禁 = NO；已满足放行条件：`article-writing-guide` 在会话可用清单中，可直接认领 |
| **下一步** | 调用 `article-writing-guide` skill，由其完成写作域开工路由（先确认公众号文章的定位/读者/长度/风格，再定改写方案） |

**一句话**：这篇笔记已学完，路由到此为止，剩下的交给写作域——直接转 `article-writing-guide`。

需要我现在调用 `article-writing-guide` 进入写作路由吗？
