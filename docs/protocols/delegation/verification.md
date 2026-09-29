# Verification and final report

## Main-agent acceptance

所有已派发 worker 返回后，主代理逐项执行：

1. 检查 `Status`；只有 `completed` 进入完成候选。
2. 对照 handoff 的 `Scope` 和 `Acceptance` 检查实际结果。
3. 检查实际 diff、文件范围、依赖变化和测试或检查输出。
4. 拒绝越界、缺证据、只交计划或未满足验收的结果。
5. 按依赖顺序整合隔离 worktree 或不重叠修改。
6. 运行整体检查，确认组合结果仍满足总目标。
7. 最终答复区分已验证、未验证、阻塞、失败和未运行。

## Proportional checks

- 低风险只读或小改动：运行直接相关的最小检查。
- 常规多文件编码、测试或文档：运行受影响路径的测试、类型检查或 lint。
- 数据库迁移、权限、安全、生产链路或其他高风险改动：保留所有必要的专项验证和确认门禁，不因“按比例”省略关键检查。
- 检查通过且没有新改动、失败或未解决问题时停止；出现这些情况再扩大检查范围。

## Final report

```text
Goal: <总目标>
Workers: <实际派发及各自状态>
Scheduling: <并行或顺序，以及原因>
Runtime: <实际验证的 provider/route/worker/model/effort/concurrency/isolation；未知值写 unverified>
Checks: <worker 检查 + 主代理整体检查>
Integration: <整合结果>
Remaining risks: <剩余风险，无则写 none>
```

不要把计划、默认配置或 worker 自报状态写成已完成证据。
