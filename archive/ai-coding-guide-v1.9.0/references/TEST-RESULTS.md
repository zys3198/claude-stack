# ai-coding-guide 测试记录

本文件记录维护 `ai-coding-guide` 时的最小 RED/GREEN 证据。完整自动评测未跑时，标 `dry_run`，不把结果当 dim8 full_test。

## 2026-07-20 · dry_run

| Prompt | RED：无/旧路由失败 | GREEN：当前路由期望 | 结果 |
|---|---|---|---|
| #4 高风险 auth review | 旧路径把高风险审查写成 `security-and-hardening` + `superpowers:requesting-code-review`，容易只给加固建议，不实际审当前 diff/文件。 | `code-review`/语言 reviewer 审代码 + `security-review`；需要加固方案再叠 `security-and-hardening`；不调用 `verify`。 | pass（文档路由已改） |
| #13 React build 报错 | 旧路径直接派 `ecc:react-build-resolver` agent，忽略可用 slash command，成本更高且入口错层。 | 优先 `ecc:react-build` slash command；不可用才派 `ecc:react-build-resolver`；都无则回构建原文。 | pass（文档路由已改） |
| #11 提交/PR | 旧路径容易把 `commit-push-pr` 当普通提交入口，弱化 push/PR 不可逆确认。 | 单提交走 `commit-commands:commit`；`commit-commands:commit-push-pr` 标明自动 push + 开 PR，跑前确认；长分支走 `superpowers:finishing-a-development-branch`。 | pass（文档路由已改） |

## 下次 full_test 要求

- 用 fresh subagent 跑上表 3 个 prompt：一组不带 skill（baseline），一组带当前 `SKILL.md`。
- 记录原始输出摘要和是否命中 expected。
- full_test 未完成前，Darwin dim8 只能标 `dry_run`。
