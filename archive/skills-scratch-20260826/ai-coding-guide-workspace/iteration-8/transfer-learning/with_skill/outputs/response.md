域归属：学习（目标是“吃透”技术并准备讲解，不是编码交付产物）  
ai-coding-guide 在当前会话？ YES  
转介：命中 routing.md 域边界“学习/调研/吃透/做教程 → learning-guide”，不进 Step 1 编码分类。

**路由契约（五项）**

| 项 | 判断 |
|---|---|
| 分类 | 学习/技术吃透（给自己学会 → 能讲清楚） |
| 主路径 | `learning-guide` |
| 组合 | 无；`ai-coding-guide` 仅承担本次路由判断，不进入编码执行 |
| 闸门 | 无（学习路径的验收与进度闸门由 `learning-guide` 内部定义） |
| 下一步 | 调用 `learning-guide`，由它处理“两周内掌握 transformer 并能对外讲解”的学习计划 |

说明：本次请求不是写代码，因此不进 ai-coding-guide 的交付状态机；按 routing.md 第 18 行，学习任务直接交 `learning-guide`。
