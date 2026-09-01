按 `ai-coding-guide` 路由逻辑，该问题本身属于元配置咨询，不走编码交付状态机。

**分类**：Skill 治理 / 元配置澄清（非交付型，不进编码状态机）  
**主路径**：当前上下文直接判断与回答，不触发 `REQUIREMENT → DESIGN → IMPLEMENT` 流程  
**组合**：无需独立 Agent 或 adapter，单上下文完成  
**闸门**：需确认新装 skill 的「触发域」与「功能边界」——是否介入编码域任务  
**下一步**：请告诉我新 skill 的**名称**和**用途**；若它处理的是编码/前端/调试/代码审查等任务，才需要评估是否要在 `ai-coding-guide/references/routing.md` 中增加引用或路由条目。
