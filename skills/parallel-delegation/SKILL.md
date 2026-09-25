---
name: parallel-delegation
description: 规划边界清楚、可独立验收的单个或并行子代理任务；涉及模型、effort、并发或隔离时先走确认门禁。
compatibility: 需要宿主提供 agent/subagent 调度能力；模型、effort、并发和隔离能力以运行时实际暴露为准。
disable-model-invocation: true
---

# Model-agnostic parallel delegation

## Route

1. 先判断子任务是否独立、边界是否清楚、结果是否可单独验收，以及收益是否超过成本。收益有两笔：并行省下的时间，以及主代理窗口省下的上下文；成本是钱照付，加上协调与验收开销。需要跟主代理已有上下文一起权衡的决策不委派：worker 看不到主代理的窗口，做出来的取舍缺前提。
2. 按主会话减少的中间材料评估上下文收益。要求 worker 返回短摘要、证据路径、未决项和状态，不把原始搜索结果、完整工具输出或重复背景带回主会话；摘要仍不足以验收时，宁可保留必要证据，不为节省上下文删掉验证依据。
3. 准备派发时读取 [`references/dispatch-contract.md`](references/dispatch-contract.md)。
4. 批量并行（≥2 个 worker）前先派一个 worker 单跑同类任务，核对路由、权限、输入契约和产物格式；单跑未验证可靠不得放并行，首次暴露的通常是脚本和配置问题（参数传错、prompt 漏条件、权限少一项）。
5. 涉及模型、effort、并发、隔离能力或失败处理时读取 [`references/runtime-and-failure.md`](references/runtime-and-failure.md)，并按下面的 Configuration gate 取得确认。
6. 整合前读取 [`references/verification.md`](references/verification.md)，按风险完成主代理复核和最终报告。

## Keep in main agent

需求理解、整体架构、跨任务取舍、强耦合修改、权限与安全判断、外部或不可逆动作、最终整合、最终答复。

## Boundaries

- worker 只能执行收到的唯一子目标，不重定义总目标、不扩大范围、不创建下级 worker。
- 只读任务可在不重叠范围且宿主明确支持并发时并行；写任务必须使用宿主提供的隔离，或明确不重叠文件范围。共享文件、生成物或状态存在冲突风险时顺序执行。
- 生产操作、外部发送、删除、迁移和权限变化遵守宿主确认门禁，不能用并行绕过。
- 子代理默认无主会话授权；只有主模型明确传递当前 `session_id`、`task_id`、精确目标集合、操作族、影响上限和关键参数时，才可在该范围内工作。子代理不得扩大范围、跨会话复用或自行登记更高影响授权。
- worker 返回“完成”不等于验收完成；主代理必须检查实际结果、diff、文件范围和检查输出。
- 任务书里必须写明工作区未提交改动基线：写之前跑 `git status --short` 实测，把已有 `M`/`??` 清单写进「现状」节。回退用文件副本（拷贝到专用 bak 目录），**禁用 `git checkout` 回退**——跨批次长流程里工作区会累积上一批成果，git 回退的粒度是文件不是 hunk，会把它们一起抹掉。验收判定「改动文件 ⊆ 已知名单」，不是「工作区干净」。
- 只交计划不算完成。blocked/failed 不算完成；不得把推测、默认路由或未观测的模型写成事实。

## Configuration gate

每次启动子代理前，先向用户明确展示：拟选模型（可见时写实际名称）、provider、route、effort、并发数和隔离方式；判断配置是否合理，说明原因、影响和备选方案；取得确认后再启动——**常规单个委派不豁免这道确认**。宿主未暴露的值写 `unverified`；同一配置、或没有可选配置而仅用已确认宿主默认值时，不重复询问。

运行时允许时，低风险且边界清楚的任务优先使用较低 effort；跨文件推理、高风险或复杂取舍再提升。任意模型均可参与，只要宿主实际暴露对应调度、隔离和验证能力；不写死字段名。

任务完成后只报告实际派发、实际路由、实际检查、整合结果和剩余风险。

## 维护条款

**分界。** 会变的（Route、Keep in main agent、Boundaries、Configuration gate）整体重写。只增的：本文件没有——判据的依据留在 `references/` 与 `evals/` 里，正文不留历史。

删除判据与整理触发点各协议通用，见 `~/.claude/docs/protocols-index.md` 的「维护条款」。
