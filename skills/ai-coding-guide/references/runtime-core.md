# Runtime core

保持流程语义与宿主无关，把 Agent 生命周期委托给选定的宿主适配器。Claude 本地运行时事实源是 [`config/runtime-contract.json`](../config/runtime-contract.json)，能力映射见 [`config/runtime-manifest.json`](../config/runtime-manifest.json)。

## 生命周期

隔离运行时必须提供：

1. `spawn(role, prompt) -> executor_id`：创建真实、全新的 Agent，并返回宿主签发的标识。
2. `send(executor_id, message)`：在不更换 Agent 身份的前提下发送补充输入。
3. `wait(executor_id)`：等待完成或结构化交接。
4. `close(executor_id)`：阶段不再需要重试时释放 Agent。
5. `spawn_helper(role, bounded_prompt) -> executor_id`：创建只读代码检索或知识检索助手；这是可选生命周期操作。

不得用自造标签代替宿主返回的 ID。协调者可以调用状态脚本、向用户提问、校验产物和派发任务，但不得生成隔离阶段的产物。

## 适配器职责

- adapter 将中立生命周期映射到宿主 API，并声明不支持的操作。
- 宿主工具名、权限字段、安装路径和资源加载格式留在 adapter。
- 一个 isolated 流程只能选择一个 adapter；除非 adapter 明确提供桥接，不得混用项目原生流程与本状态机。
- 没有受支持的生命周期 API 时，先记录 `fallback_reason`，之后才能使用 `single-context`。
