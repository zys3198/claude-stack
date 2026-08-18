# ai-coding-guide 命令

调用 `ai-coding-guide` Skill，一切以其「必须执行」与「不可绕过」为准；门禁、生命周期与角色边界不复述——唯一事实源：SKILL.md、[references/workflow-contract.md](../references/workflow-contract.md)、[references/agent-execution.md](../references/agent-execution.md)。

恢复任务：用户输入 `/ai-coding-guide resume <slug>` 或「继续之前的任务」→ 运行 `resume --project-root . --slug <slug>`；状态文件不存在时立即停止恢复并报告，要求重新提交原需求。
