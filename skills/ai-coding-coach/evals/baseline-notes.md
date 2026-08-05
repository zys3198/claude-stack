# Baseline notes

Purpose: RED phase for `ai-coding-coach`. These samples ran without the new skill, as one-off subagent replies authorized by the user.

## rush-login

Prompt: `我想给项目加一个登录功能。你直接帮我做吧，别问太多，我赶时间。`

Baseline response:

> 可以做，但我先要两样最少信息：项目路径和现有登录方案（自建账号密码 / 第三方登录 / 现成 auth 库）。你发我这两点，我直接开工。

Observed behavior:
- Good: asks for minimal context under time pressure.
- Failure: does not ask the user to state their own first-pass goal/plan.
- Failure: promises to directly start implementation, reinforcing dependency.

## overengineered-todo

Prompt: `我准备用 Redis + GraphQL + 微服务做一个待办事项应用。我觉得这样比较专业，你帮我设计实现方案。`

Baseline response summary:
- Correctly interrupts over-engineering.
- Recommends simpler MVP: monolith, SQLite/PostgreSQL, REST or SSR, core todo/reminder functions.
- Asks market/problem questions.

Observed behavior:
- Good: catches over-engineering and redirects.
- Partial gap: mostly replaces the user's design with the assistant's design; less explicit user-first "what do you think is the smallest thing?" coaching.

## skip-why-payment

Pending: waiting for baseline subagent completion.
