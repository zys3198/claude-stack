# §3 Agent 调度

本节只补充编码任务在 Plan 后的切片、验证和 hooks 衔接；一般委派的独立性、worker 范围、模型/provider/route/effort、并发、隔离、授权、失败处理和主代理复核按 `parallel-delegation` 执行。Plan 触发条件见 `SKILL.md §1.1`。

- **Tracer bullet**：每片竖切穿过全部受影响层（schema→服务→最小呈现），自带阻塞边；切片后先与用户核对粒度和依赖。项目已有 workflow contract、规格或状态机时沿用其字段、契约和验证命令；没有时记录最小计划。正式工单提示用户运行 `/to-tickets`；Plan 审批通过后执行。
- 依赖任务串行；独立写任务按 `parallel-delegation` 的隔离规则后才并行。
- **Verify 分级**（按风险，不按文件数）：
  - 低（机械/重命名/格式）→ 一次独立轻量 reviewer + 项目已有的最小相关检查；不启动多 Agent 对抗审查。
  - 中（功能改动）→ 单 reviewer agent。
  - 高（auth/DB schema/架构/安全敏感）→ 三 agent adversarial（找问题/求证/反驳），2/3 通过；涉及安全边界时追加已证实的 `security-review`。
- 每片完成时必须拿得出外部可观察现象（界面、API 响应或命令输出）；只能汇报「某层写完」算横切，打回重切。全部切片完成后跑集成测试。
- 小改动（如 DTO 字段）不启动多 Agent，仍按低风险 Verify 做一次独立轻量复核；沟通和验收成本高于修改本身时不扩展并行规模。
- **实际护栏**：危险命令是否被拦截，看 `settings.json` 实际挂载的 hooks；没有挂载时按 `CLAUDE.md §1.3` 的人工确认线执行。长链编排（>3 agent）使用已有执行计划或 workflow contract 并设步数上限；进入循环或并行前先单跑一轮同类任务，核对路由、权限、输入契约和产物格式。
