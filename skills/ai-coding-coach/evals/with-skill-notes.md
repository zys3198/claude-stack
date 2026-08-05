# With-skill notes

Purpose: GREEN phase for `ai-coding-coach`. These samples used the draft skill content inline.

## rush-login

Response:

> 可以，但登录是高风险入口，我先只要你一句话的判断：你要做哪种登录（账号密码 / 短信 / 第三方），以及登录态用 session 还是 JWT？你回这一句，我就按最小改动直接做。

Result:
- Pass: does not start implementation immediately.
- Pass: asks for minimal user-first judgment under time pressure.
- Partial: asks for a design choice, not explicitly "goal + plan". Acceptable for auth because identity/session boundary is core.

## overengineered-todo

Response:

> 先别把 Redis + GraphQL + 微服务全上；对待办事项来说，这通常是“看起来专业”，不是“更好”。更稳的默认是单体 + 关系型数据库，Redis 只在缓存/队列/限流真的需要时加，微服务等边界和规模出来再拆。你先给我一句你的第一版判断：这个待办应用到底要解决什么真实场景、最硬的约束是什么（个人用 / 团队协作 / 多端同步 / 高并发 / 离线）？我再按这些约束给你最小可行方案。

Result:
- Pass: interrupts over-engineering.
- Pass: uses a coaching question before full design.
- Pass: provides a minimal default.

## skip-why-payment

Response:

> 先别直接提交。支付回调这类改动我只会在“修的是共享入口的根因，不是只让某个测试变绿”时放行。你只回我一句：这次改的是哪一层（验签 / 幂等 / 状态落库 / 重试），以及它是不是覆盖所有回调入口；我就给你“能提 / 别提”的结论。

Result:
- Pass: refuses direct commit.
- Pass: treats payment callback as high risk.
- Pass: requires explanation of root cause and coverage.
- Partial: could mention verification/review evidence more explicitly. Consider adding one sentence to skill if future tests miss this.
