# Skill Benchmark: code-change-workflow

**Date**: 2026-08-17T03:27:39Z
**Evals**: 调试-修根因检查调用方, 改前-反查真需求 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 25% ± 25% |

## Per-Case Results

### 调试-修根因检查调用方 (with_skill)

- **Pass Rate**: 50% (1/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[根因]} | ✅ | output satisfies all contains checks (all:[根因]) |
| output_contains.all: missing [调用方] | ❌ | output does not contain required keywords: [调用方] |

### 改前-反查真需求 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [为什么] | ❌ | output does not contain required keywords: [为什么] |

