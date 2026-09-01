按 `ai-coding-guide` 分诊：

- **域归属：** 编码（改造任务涉及代码交付）
- **`ai-coding-guide` 在当前会话：** YES

**路由契约（只做判断，不执行）：**

| 项 | 内容 |
|---|---|
| **分类** | 开发新功能 — 重任务 / 跨会话交付（命中 Step 1「大任务/跨会话/断点续跑」信号） |
| **主路径** | `ai-coding-guide` 交付状态机：澄清 REQUIREMENT → 设计 DESIGN → 实现 IMPLEMENT → 审查 REVIEW → 测试 TEST → 总结 SUMMARY，脚本写 `workflow-state.json` 断点续跑 |
| **组合** | `superpowers:writing-plans`（拆阶段计划）+ `code-change-workflow`（改前/改中/改后清单与 Verify 分级） |
| **闸门** | REQUIREMENT 用户确认门禁不可跳过；DESIGN 方案确认；每阶段产物校验；横切收尾验证（build/test/真实流程）；提交/删除/外部写操作单独确认 |
| **下一步** | 确认两件事后启动 REQUIREMENT：1）是否现在就开始；2）规模口令选 `medium` 还是 `large`（用户未明说时默认自判 `small`，但「跨会话改造」建议显式定档） |

未启动前，不读取项目文件，不跑 `inspect_context.py`。
