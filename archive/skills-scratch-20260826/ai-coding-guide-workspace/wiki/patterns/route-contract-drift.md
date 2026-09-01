# 多任务路由契约标签回退

- id: `route-contract-drift`
- kind: `regression`
- updated: `2026-08-31T06:44:22Z`

## Summary
iteration-4、iteration-5、iteration-8 出现路由类别、组合工具、固定字段或规模口令缺失；部分响应判断方向正确，但输出没有稳定保留入口契约中的精确标签。

## Root cause
关键约束主要埋在 references/routing.md，SKILL.md 入口没有重复最小强制集；变体请求下，模型容易用泛化分类替代标准分类，或省略 gitnexus-exploring、guide-skill-auditor、eval、small/medium/large 等可验收标签。

## Recommendation
在 SKILL.md 入口增加稳定性硬约束：路由输出保留固定字段并使用 routing.md 原分类名；调用链优先 gitnexus-exploring；guide maintenance 主路径 guide-skill-auditor 且行为变化先补 eval；交付状态机明确 small/medium/large 口令提醒。候选必须经过多任务 target、guardrail、holdout 验证。

## Evidence
- [Raw trace](../../raw/traces/iteration-4.json)
- [Raw trace](../../raw/traces/iteration-5.json)
- [Raw trace](../../raw/traces/iteration-8.json)

---

## Maintainer update 2026-08-31T09:43:02Z

# 多任务路由契约标签回退

- id: `route-contract-drift`
- kind: `regression`
- updated: `2026-08-31T09:43:02Z`

## Summary
历史 Trace 曾出现分类、组合工具或固定字段不稳定；本次真实全局 active smoke test 覆盖日常结构、调用链、结构加调用链三种请求，3/3 通过，确认 v2.4.0 当前路由契约行为稳定。

## Root cause
关键路由约束曾主要埋在 references/routing.md，入口 Skill 缺少最小强制集；v2.4.0 已将标准分类、固定输出字段和 lean-ctx → gitnexus-exploring 顺序提升到入口约束。

## Recommendation
继续保留固定路由契约和代码理解工具顺序；后续路由行为变化先补可验证 eval，再进入 propose/gate。将真实 active smoke test 作为回归证据，不把 --bare 未加载 Skill 的结果计入模型失败。

## Evidence
- [Raw trace](../../raw/traces/iteration-11.json)
