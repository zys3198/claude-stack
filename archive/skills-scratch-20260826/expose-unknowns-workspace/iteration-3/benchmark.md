# Skill Benchmark: expose-unknowns

**Date**: 2026-08-21T03:26:33Z
**Evals**: 判级-未知的未知先扫盲, 判级-已知的未知主动抛问, 判级-已知的已知直接开工 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |

## Per-Case Results

### 判级-未知的未知先扫盲 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[未知的未知]} | ✅ | output satisfies all contains checks (all:[未知的未知]) |

### 判级-已知的未知主动抛问 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[已知的未知]} | ✅ | output satisfies all contains checks (all:[已知的未知]) |

### 判级-已知的已知直接开工 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[已知的已知]} | ✅ | output satisfies all contains checks (all:[已知的已知]) |

