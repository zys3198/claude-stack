域归属：编码（提交/收尾）/ ai-coding-guide 已加载 / 留在本路由

| 项 | 路由契约 |
|---|---|
| **分类** | 提交/收尾（Step 1 明确命中「帮我提交」「发个 PR」） |
| **主路径** | 手动 git 流程：`status` → `diff --stat` → `add` → `commit` → `push` → `create_pull_request` |
| **组合** | 无；PR 描述若缺模板，可条件叠加 `ocr review` 审 diff，非必须 |
| **闸门** | **提交确认**（不可逆/外发）：必须先展示 `git status --short` + `git diff --cached --stat`，逐项确认后方可执行 commit / push / create PR |
| **下一步** | 先收 3 个缺口：1) 提交范围（全部改动还是部分文件）；2) 目标分支；3) PR 标题/描述；确认后展示 diff 等待用户点头发 commit |

> 注：按 CLAUDE.md §1.3，commit、push、PR 均属必须确认项，不得自主执行。
