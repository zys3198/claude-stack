# Skill Benchmark: ai-coding-guide

**Date**: 2026-08-18T14:20:01Z
**Evals**: 新装 skill 触发维护场景, 路由输出契约六项, 重任务跨会话进交付状态机 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |

## Per-Case Results

### 新装 skill 触发维护场景 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[路由指南维护]} | ✅ | output satisfies all contains checks (all:[路由指南维护]) |

### 路由输出契约六项 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[分类 主路径 闸门 下一步]} | ✅ | output satisfies all contains checks (all:[分类 主路径 闸门 下一步]) |

### 重任务跨会话进交付状态机 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[状态机 口令]} | ✅ | output satisfies all contains checks (all:[状态机 口令]) |
| output_contains{not:[devflow]} | ✅ | output satisfies all contains checks (not:[devflow]) |

