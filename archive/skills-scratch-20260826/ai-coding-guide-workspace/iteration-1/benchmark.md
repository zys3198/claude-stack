# Skill Benchmark: ai-coding-guide

**Date**: 2026-08-17T03:09:25Z
**Evals**: 域边界转介-学习调研, 域边界转介-文章审校, 前端视觉-落地页留本路由, 前端视觉-方向未定先问, 指南维护-审计 router guide, 学习陪跑-你练模式, 判级-暴露未知路由, 重构-不推荐已移除工具 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 25% ± 35% |

## Per-Case Results

### 域边界转介-学习调研 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [learning-guide] | ❌ | output does not contain required keywords: [learning-guide] |

### 域边界转介-文章审校 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [article-writing-guide] | ❌ | output does not contain required keywords: [article-writing-guide] |

### 前端视觉-落地页留本路由 (with_skill)

- **Pass Rate**: 50% (1/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [hallmark] | ❌ | output does not contain required keywords: [hallmark] |
| output_contains{not:[design-an-interface]} | ✅ | output satisfies all contains checks (not:[design-an-interface]) |

### 前端视觉-方向未定先问 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[方向]} | ✅ | output satisfies all contains checks (all:[方向]) |
| output_contains{not:[design-an-interface]} | ✅ | output satisfies all contains checks (not:[design-an-interface]) |

### 指南维护-审计 router guide (with_skill)

- **Pass Rate**: 0% (0/0)

### 学习陪跑-你练模式 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [ai-coding-coach] | ❌ | output does not contain required keywords: [ai-coding-coach] |

### 判级-暴露未知路由 (with_skill)

- **Pass Rate**: 0% (0/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [expose-unknowns] | ❌ | output does not contain required keywords: [expose-unknowns] |

### 重构-不推荐已移除工具 (with_skill)

- **Pass Rate**: 50% (1/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains.all: missing [重构] | ❌ | output does not contain required keywords: [重构] |
| output_contains{not:[simplify]} | ✅ | output satisfies all contains checks (not:[simplify]) |

