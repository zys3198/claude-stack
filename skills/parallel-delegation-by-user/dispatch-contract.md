# Dispatch contract

## Split gate

子任务同时满足以下条件才适合并行：

- 输入和读取范围清楚；
- 不依赖其他子任务的中间结果；
- 输出可以单独验收；
- 可指定文件、目录、符号或资料边界；
- 并行收益大于协调成本。

主代理保留需求澄清、架构、跨任务取舍、强耦合修改、最终整合和最终答复。单文件机械修改或用户要求单代理时不派发。

## Handoff

每个 worker 使用最小契约：

```text
Task: <唯一子任务>
Scope: <允许读取和修改的范围>
Inputs: <已知上下文、文件、约束>
Output: <必须返回的结果>
Acceptance: <主代理可执行的验收条件>
Boundaries: <禁止修改、禁止外部操作、禁止继续委派>
Isolation: <read-only | isolated-write | disjoint-write>
```

派发前由主代理确认总目标、不变约束、子任务边界、依赖关系、写入冲突、验收条件和宿主限制。不会实质改变目标、安全边界或验收条件的普通信息缺口采用合理假设继续；关键缺口才阻塞并提问。不要用“看看这个项目”替代契约。

## Scheduling

- 无中间结果依赖、读取范围不重叠且宿主明确支持并发：并行。
- 写入范围不重叠且宿主明确支持：可并行；共享文件、生成物或状态：顺序或隔离。
- 后一项依赖前一项验收：分阶段调度。
- 无法证明独立或并行收益不足：留在主代理或顺序执行。

## Worker result

worker 必须返回实际证据，不只返回“完成”：

```text
Status: completed | blocked | failed
Result: <实际结果>
Files inspected: <实际检查文件>
Files changed: <实际修改文件，无则写 none>
Checks: <实际运行的检查及结果>
Blockers: <阻塞，无则写 none>
Risks: <剩余风险，无则写 none>
Runtime: <宿主实际暴露的 provider/route/worker/model/effort/concurrency/isolation；无法确认的值写 unverified>
```

worker 不创建下级 worker，不执行破坏性或外部写操作，不提交或推送，不把未验证推测写成事实。发现范围、权限或运行时能力不满足时停止并报告。
