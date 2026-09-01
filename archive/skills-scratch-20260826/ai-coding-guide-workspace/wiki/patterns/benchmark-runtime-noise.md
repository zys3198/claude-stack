# 评估执行错误污染 Skill 信号

- id: `benchmark-runtime-noise`
- kind: `evaluation`
- updated: `2026-08-31T06:44:22Z`

## Summary
iteration-1 的 maintenance-audit、iteration-7 多个用例、iteration-9 因 runner/context deadline 或 Windows bash target 失败，未产生可评分 Skill 输出。

## Root cause
评估执行环境或超时失败与路由行为失败混入同一 benchmark 结果，导致 pass rate 不能单独代表 Skill 质量。

## Recommendation
评分时将 ERROR/context timeout 与模型输出 FAIL 分层；修复 runner 后再把对应用例纳入 gate，不能用执行错误证明候选改进。

## Evidence
- [Raw trace](../../raw/traces/iteration-1.json)
- [Raw trace](../../raw/traces/iteration-7.json)
- [Raw trace](../../raw/traces/iteration-9.json)
