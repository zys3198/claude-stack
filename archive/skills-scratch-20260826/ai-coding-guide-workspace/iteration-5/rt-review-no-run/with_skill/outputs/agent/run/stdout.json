按 `ai-coding-guide` 分诊结果：

**分类：** 审查代码（当前 diff）  
**主路径：** `code-review`（内置命令，审当前 diff）  
**组合：** `security-review`（auth 高风险）+ Code Reviewer agent 双审  
**闸门：** review + security-review；不运行程序（已按用户要求排除 verify/run）  
**下一步：** 直接执行（auth 变更优先启 `security-review`，再叠 `code-review` / Code Reviewer agent）
