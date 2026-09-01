按 `ai-coding-guide` 分诊完成，输出路由契约：

| 项 | 内容 |
|---|---|
| 分类 | 理解代码 |
| 主路径 | `lean-ctx` |
| 组合 | `lean-ctx` → `gitnexus-exploring` |
| 闸门 | 无 |
| 下一步 | 直接执行 |

**为什么这样组合**：先用 `lean-ctx` 定位 auth 模块的入口、核心类型和接口实现，再用 `gitnexus-exploring` 查 `login` 的调用链与影响范围；两者互补，不需要用户二选一。
