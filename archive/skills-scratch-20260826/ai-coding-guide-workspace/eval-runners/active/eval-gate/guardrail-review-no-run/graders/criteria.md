---
type: llm
weight: 1
---

只有当最后回答归类为审查代码，包含 `security-review`，并尊重“不要运行程序”而不把 verify 作为下一步时才通过。只做路由判断。
