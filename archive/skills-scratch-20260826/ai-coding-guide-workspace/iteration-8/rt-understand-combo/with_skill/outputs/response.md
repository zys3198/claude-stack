根据 `ai-coding-guide` 分诊，输出路由契约如下：

| 项 | 契约 |
|---|---|
| **分类** | 非交付型 / 代码理解 + 调用链路澄清 |
| **主路径** | `lean-ctx` 探索路径：`ctx_compose` 先定位 auth 模块入口 → `ctx_search(action=symbol)` 查 `login` 定义 → `ctx_callgraph` 查调用方；必要时 `ctx_read(mode=signatures/full)` 读关键文件 |
| **组合** | 本任务不启用多 Agent 工作流；单上下文内用 lean-ctx 工具链完成（可选项：若项目规模大或跨多目录，再触发 `Explore` agent 做只读扫描） |
| **闸门** | 无人工确认线（只读查询，不写文件、不改代码、不执行不可逆操作） |
| **下一步** | 运行 `ctx_compose` / `ctx_search` 开始定位 auth 模块与 `login` 调用方，然后向用户汇报结构 |

路由判断完成，是否开始执行搜索？
