按 `ai-coding-guide` 路由分诊，输出如下：

**分类**：非交付型任务 / 工具与流程澄清  
**主路径**：不进入 `ai-coding-guide` 状态机，走「澄清 → 确认信息 → 给出判断」  
**组合**：单轮上下文直接回答，无需 Agent 编排，无需读写项目代码  
**闸门**：缺少关键信息——新装 skill 的**名称**与**用途**，无法判断是否需要 `ai-coding-guide` 显式引用  
**下一步**：请用户补充新 skill 名称和作用，再判断 `ai-coding-guide` 的 `references/routing.md` 或规则清单是否需要同步更新
