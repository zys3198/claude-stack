# Skill Benchmark: ai-coding-guide

**Date**: 2026-08-18T14:25:28Z
**Evals**: 判级-暴露未知路由, 前端视觉-落地页留本路由, 前端视觉-方向未定先问, 指南维护-审计 router guide, 学习陪跑-你练模式, 重构-不推荐已移除工具, 域边界转介-文章审校, 域边界转介-学习调研, 带任务信号的对比型问题走开发新功能, 纯抽象对比走了解指南, 已有需求文档走有需求文档分类, 高风险代码审查双审, 系统化调试先复现定位, 小范围最简改动不弹菜单, 新装 skill 触发维护场景, 循环任务走 /loop, 理解代码组合路径不二选一, 提交收尾展示 diff 待确认, 横切验证后再进提交, 构建错误按原文排查, 外部实践迁移先过闸门, 用户说直接处理就不弹菜单, 审查不误触发 verify, 轻量迁移最小改动, 禁止破坏性清理, 直接执行跳过询问, 定位校准开工路由为主, 路由输出契约六项, 风险闸门矩阵高风险判定, 最小信息清单只问缺口, 点名插件可用则直走, 三域外独立工具直接执行, 教程归属裁决给自己学会, 重任务跨会话进交付状态机 (1 runs each per configuration)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 15% ± 35% |

## Per-Case Results

### 判级-暴露未知路由 (with_skill)

- **Pass Rate**: 100% (1/1)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[expose-unknowns]} | ✅ | output satisfies all contains checks (all:[expose-unknowns]) |

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

- **Pass Rate**: 0% (0/0)

### 重构-不推荐已移除工具 (with_skill)

- **Pass Rate**: 100% (2/2)

| Expectation | Result | Evidence |
|-------------|--------|----------|
| output_contains{all:[重构]} | ✅ | output satisfies all contains checks (all:[重构]) |
| output_contains{not:[simplify]} | ✅ | output satisfies all contains checks (not:[simplify]) |

### 域边界转介-文章审校 (with_skill)

- **Pass Rate**: 0% (0/0)

### 域边界转介-学习调研 (with_skill)

- **Pass Rate**: 0% (0/0)

### 带任务信号的对比型问题走开发新功能 (with_skill)

- **Pass Rate**: 0% (0/0)

### 纯抽象对比走了解指南 (with_skill)

- **Pass Rate**: 0% (0/0)

### 已有需求文档走有需求文档分类 (with_skill)

- **Pass Rate**: 0% (0/0)

### 高风险代码审查双审 (with_skill)

- **Pass Rate**: 0% (0/0)

### 系统化调试先复现定位 (with_skill)

- **Pass Rate**: 0% (0/0)

### 小范围最简改动不弹菜单 (with_skill)

- **Pass Rate**: 0% (0/0)

### 新装 skill 触发维护场景 (with_skill)

- **Pass Rate**: 0% (0/0)

### 循环任务走 /loop (with_skill)

- **Pass Rate**: 0% (0/0)

### 理解代码组合路径不二选一 (with_skill)

- **Pass Rate**: 0% (0/0)

### 提交收尾展示 diff 待确认 (with_skill)

- **Pass Rate**: 0% (0/0)

### 横切验证后再进提交 (with_skill)

- **Pass Rate**: 0% (0/0)

### 构建错误按原文排查 (with_skill)

- **Pass Rate**: 0% (0/0)

### 外部实践迁移先过闸门 (with_skill)

- **Pass Rate**: 0% (0/0)

### 用户说直接处理就不弹菜单 (with_skill)

- **Pass Rate**: 0% (0/0)

### 审查不误触发 verify (with_skill)

- **Pass Rate**: 0% (0/0)

### 轻量迁移最小改动 (with_skill)

- **Pass Rate**: 0% (0/0)

### 禁止破坏性清理 (with_skill)

- **Pass Rate**: 0% (0/0)

### 直接执行跳过询问 (with_skill)

- **Pass Rate**: 0% (0/0)

### 定位校准开工路由为主 (with_skill)

- **Pass Rate**: 0% (0/0)

### 路由输出契约六项 (with_skill)

- **Pass Rate**: 0% (0/0)

### 风险闸门矩阵高风险判定 (with_skill)

- **Pass Rate**: 0% (0/0)

### 最小信息清单只问缺口 (with_skill)

- **Pass Rate**: 0% (0/0)

### 点名插件可用则直走 (with_skill)

- **Pass Rate**: 0% (0/0)

### 三域外独立工具直接执行 (with_skill)

- **Pass Rate**: 0% (0/0)

### 教程归属裁决给自己学会 (with_skill)

- **Pass Rate**: 0% (0/0)

### 重任务跨会话进交付状态机 (with_skill)

- **Pass Rate**: 0% (0/0)

