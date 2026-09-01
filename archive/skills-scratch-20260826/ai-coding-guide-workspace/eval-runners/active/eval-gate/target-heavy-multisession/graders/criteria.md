---
type: llm
weight: 1
---

只有当最后回答明确进入交付状态机，并在下一步或规模判定中明确给出 `small`、`medium`、`large` 至少一个口令选项或说明默认自判 `small` 时才通过。不得把请求路由成已移除的 `devflow`。只做路由判断。
