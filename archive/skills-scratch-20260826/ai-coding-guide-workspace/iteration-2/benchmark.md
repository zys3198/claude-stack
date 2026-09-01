# Skill Benchmark: ai-coding-guide

**Date**: 2026-08-17T03:13:42Z
**Evals**: 域边界转介-学习调研, 域边界转介-文章审校, 前端视觉-落地页留本路由, 前端视觉-方向未定先问, 指南维护-审计 router guide, 学习陪跑-你练模式, 判级-暴露未知路由, 重构-不推荐已移除工具 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |

## Per-Case Results

### 域边界转介-学习调研 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[learning-guide]} | ✅ | output satisfies all contains checks (all:[learning-guide]) |

### 域边界转介-文章审校 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[article-writing-guide]} | ✅ | output satisfies all contains checks (all:[article-writing-guide]) |

### 前端视觉-落地页留本路由 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[hallmark]} | ✅ | output satisfies all contains checks (all:[hallmark]) |
| output_contains{not:[design-an-interface]} | ✅ | output satisfies all contains checks (not:[design-an-interface]) |

### 前端视觉-方向未定先问 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[方向]} | ✅ | output satisfies all contains checks (all:[方向]) |
| output_contains{not:[design-an-interface]} | ✅ | output satisfies all contains checks (not:[design-an-interface]) |

### 指南维护-审计 router guide (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[guide-skill-auditor]} | ✅ | output satisfies all contains checks (all:[guide-skill-auditor]) |

### 学习陪跑-你练模式 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[ai-coding-coach]} | ✅ | output satisfies all contains checks (all:[ai-coding-coach]) |

### 判级-暴露未知路由 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[expose-unknowns]} | ✅ | output satisfies all contains checks (all:[expose-unknowns]) |

### 重构-不推荐已移除工具 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[重构]} | ✅ | output satisfies all contains checks (all:[重构]) |
| output_contains{not:[simplify]} | ✅ | output satisfies all contains checks (not:[simplify]) |

