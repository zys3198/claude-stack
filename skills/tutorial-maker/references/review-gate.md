# 自审门（sub-agent teach-back 验证）

静态 Markdown 没有 live 读者。自审门用**独立 sub-agent 模拟 from-zero 读者**做 teach-back，判定来自外部信号，杜绝作者/AI 自评自卷。这是本 skill 与"裸生成 markdown"的本质区别。

## 触发

每课生成后、标 `done` 前必跑。`/tutorial <topic> review <N>` 可重跑。

## 怎么跑

用 Agent 工具派一个 sub-agent（general-purpose），给它且仅给：

- 本课 markdown **全文**
- 前序课的 **objective**（不给讲解全文，避免污染）
- `glossary.md` 当前内容
- 本课的 objective

**关键约束**：模拟读者只读这些，不读作者脑里的隐性知识、不读 sources.md 原始材料。这逼出"作者有但没写进课里"的缺口——教程最常见的失败模式。

## sub-agent 指令模板

```
你是一个 from-zero 学习者，只读过下面这份课 + 它前序课的 objective + glossary。你没看过作者的其他笔记或原始材料。

任务：
1. 可达性：仅凭给定内容，你能否达到本课 objective？哪一句让你卡住（用了没定义的概念 / 跳了步骤 / 前置没交代）？引用原句。
2. teach-back：回答 objective 派生的问题。如 objective="能说出所有权解决的3个问题"，你就写出3个。答案必须只来自课内，不能猜。
3. 练习可解性：做"你来试"的题。每题答案能否从课内推出？有没有歧义（两种合理解读）？答案是否一题一折叠（不是合并到一个 `<details>`）？
4. concrete-first：课是否先上具体例子再抽象？
5. jargon 卫生：每个术语要么课内定义、要么链 glossary？
6. common_mistakes 覆盖：curriculum.yaml 声明的 `common_mistakes` 是否在课内「常见错误」节真覆盖（不是只列错误，而是讲了"为什么错 + 正解"）？

输出 JSON：
{
  "reachable": true|false,
  "teachback_pass": true|false,
  "exercise_solvable": true|false,
  "exercise_one_per_fold": true|false,
  "concrete_first": true|false,
  "jargon_clean": true|false,
  "common_mistakes_addressed": true|false,
  "blockers": [{"check": "<检查名>", "quote": "<课内原句>", "fix": "<具体修复>"}]
}
```

## MUST / SHOULD 门规则

| 级别 | 检查 |
|------|------|
| MUST | reachable / teachback_pass / exercise_solvable / exercise_one_per_fold / common_mistakes_addressed |
| SHOULD | concrete_first / jargon_clean |

- 任一 **MUST = false** → 课 status 留 `blocked`，不标 `done`，进 `progress.md` 自审未过清单 + blockers。
- SHOULD = false → 警告，不阻塞。
- 报告落 `.tutorial-maker/reviews/NN-<slug>.md`：逐项 PASS/FAIL + 证据（模拟读者原话）+ 修复建议。
- 作者可 `/tutorial <topic> regen <N>`（按 blockers 重生成，存 `.old`）或手改后 `/tutorial <topic> review <N>` 重跑。

## 顽固点

regen 2 次仍 MUST 不过 → 标顽固点，建议作者手介入，**不死磕**（认知科学：间隔练习 > 集中死磕）。顽固点留在 progress.md，不阻塞其他课生成。
