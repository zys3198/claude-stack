**域归属：** 编码域 / 提交收尾流程  
**ai-coding-guide 在当前会话：** YES  

路由契约如下：

| 项 | 内容 |
|---|---|
| **分类** | 提交/收尾（已产生代码改动，先横切收尾验证再过 git 提交流程） |
| **主路径** | 手动 git 流程：`git status --short` → `git diff --stat` → 用户确认 → `commit` → `push` → `create_pull_request` |
| **组合** | 横切收尾验证（跑 `build / test / lint` 或 `run` 驱动真实流程）+ GitHub MCP `create_pull_request`（条件路径，当前会话可用） |
| **闸门** | 不可逆/外发操作（commit / push / PR）必须先展示改动范围与 diff，取得用户明确确认后方可执行；若改完尚未验证，先补验证 |
| **下一步** | 展示 `git status --short` 与 `git diff --stat`，等待用户确认提交范围和目标分支后再执行 commit / push / PR |
