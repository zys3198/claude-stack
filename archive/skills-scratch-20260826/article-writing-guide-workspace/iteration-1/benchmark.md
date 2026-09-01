# Skill Benchmark: article-writing-guide

**Date**: 2026-08-17T03:17:58Z
**Evals**: 审校-非后端文体走批量管线, 语言适配-英文文章, 存在性校验-已删 skill 重定向, 系列教程-对外发布, 教程裁决-给自己学会, 去 AI 味-human-writing, 兄弟域转介-前端视觉, 三域外-直接执行独立工具 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |

## Per-Case Results

### 审校-非后端文体走批量管线 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[multi-review-pipeline]} | ✅ | output satisfies all contains checks (all:[multi-review-pipeline]) |

### 语言适配-英文文章 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[article-writer]} | ✅ | output satisfies all contains checks (all:[article-writer]) |

### 存在性校验-已删 skill 重定向 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[article-writer]} | ✅ | output satisfies all contains checks (all:[article-writer]) |

### 系列教程-对外发布 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[tutorial-maker]} | ✅ | output satisfies all contains checks (all:[tutorial-maker]) |

### 教程裁决-给自己学会 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[learning-guide]} | ✅ | output satisfies all contains checks (all:[learning-guide]) |

### 去 AI 味-human-writing (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[human-writing]} | ✅ | output satisfies all contains checks (all:[human-writing]) |

### 兄弟域转介-前端视觉 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[ai-coding-guide]} | ✅ | output satisfies all contains checks (all:[ai-coding-guide]) |

### 三域外-直接执行独立工具 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{not:[article-writer]} | ✅ | output satisfies all contains checks (not:[article-writer]) |
| output_contains{not:[tutorial-maker]} | ✅ | output satisfies all contains checks (not:[tutorial-maker]) |

