# Skill Benchmark: guide-skill-auditor

**Date**: 2026-08-17T03:22:46Z
**Evals**: 命中-审查 router guide 路由质量, 命中-兄弟域抢单排查, 不命中-执行型 skill 润色, 不命中-工具选型问题, 命中-description 范畴词检查 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 60% ± 49% |

## Per-Case Results

### 命中-审查 router guide 路由质量 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[十查]} | ✅ | output satisfies all contains checks (all:[十查]) |

### 命中-兄弟域抢单排查 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[基线]} | ✅ | output satisfies all contains checks (all:[基线]) |

### 不命中-执行型 skill 润色 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.not: "十查" | ❌ | output contains forbidden keyword "十查" |

### 不命中-工具选型问题 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [ai-coding-guide] | ❌ | output does not contain required keywords: [ai-coding-guide] |

### 命中-description 范畴词检查 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[范畴词]} | ✅ | output satisfies all contains checks (all:[范畴词]) |

