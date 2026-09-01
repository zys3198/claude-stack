# Skill Benchmark: ai-coding-guide

**Date**: 2026-08-18T14:10:26Z
**Evals**: 带任务信号的对比型问题走开发新功能, 新装 skill 触发维护场景, 提交收尾展示 diff 待确认, 外部实践迁移先过闸门, 审查不误触发 verify, 轻量迁移最小改动, 路由输出契约六项, 最小信息清单只问缺口, 重任务跨会话进交付状态机 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 72% ± 42% |

## Per-Case Results

### 带任务信号的对比型问题走开发新功能 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[开发新功能]} | ✅ | output satisfies all contains checks (all:[开发新功能]) |

### 新装 skill 触发维护场景 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [触发] | ❌ | output does not contain required keywords: [触发] |

### 提交收尾展示 diff 待确认 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[提交 diff --cached --stat]} | ✅ | output satisfies all contains checks (all:[提交 diff --cached --stat]) |

### 外部实践迁移先过闸门 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[路由指南维护]} | ✅ | output satisfies all contains checks (all:[路由指南维护]) |

### 审查不误触发 verify (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[审查代码 security-review]} | ✅ | output satisfies all contains checks (all:[审查代码 security-review]) |

### 轻量迁移最小改动 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[最小 eval]} | ✅ | output satisfies all contains checks (all:[最小 eval]) |

### 路由输出契约六项 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [分类 主路径 闸门 下一步] | ❌ | output does not contain required keywords: [分类 主路径 闸门 下一步] |

### 最小信息清单只问缺口 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[完整错误 改动]} | ✅ | output satisfies all contains checks (all:[完整错误 改动]) |

### 重任务跨会话进交付状态机 (with_skill)

- **Pass Rate**: 50% (1/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [small/medium/large] | ❌ | output does not contain required keywords: [small/medium/large] |
| output_contains{not:[devflow]} | ✅ | output satisfies all contains checks (not:[devflow]) |

