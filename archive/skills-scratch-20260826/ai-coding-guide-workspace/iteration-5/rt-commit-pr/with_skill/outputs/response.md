域归属：编码（提交/收尾）  
ai-coding-guide 在当前会话：YES

| 项 | 路由契约 |
|---|---|
| **分类** | 提交/收尾 |
| **主路径** | 手动 git 提交流程：`git status --short` → `git diff --cached --stat` → 用户确认 → `commit` → `push` → 创建 PR |
| **组合** | 无（条件路径 `ocr review` 不在当前会话可用清单中） |
| **闸门** | 提交确认：涉及 commit / push / PR 等不可逆外发操作，必须先展示改动范围、目标分支与 diff 统计，得到用户明确确认后才执行 |
| **下一步** | 等用户确认提交范围、commit message 与目标分支后再动手；不擅自 commit 或 push |

理由：请求明确为代码改动后的提交与 PR，命中 routing.md Step 1「提交/收尾」分类；按 Step 0.6 风险矩阵属不可逆/外发操作，必须保留人工确认闸门。
