# Skill 路由速查

> 日常一眼查。重决策 / 多步流程走 `ai-coding-guide` skill。
> **头注 2026-08-19**：本文件只做速查，现行路由以 `ai-coding-guide` 与其 `references/routing.md` 为准；条件路径以当前会话可用清单和 `settings.json` 为准，不把历史插件当作已安装能力。

## 任务 → Skill

| 你要做 | 用哪个 | 备注 |
|--------|--------|------|
| 需求模糊，要澄清 | `mattpocock-skills:grilling` / `grill-me`（条件） | 单环澄清；`grill-me` 需用户手动调用 |
| 大功能 / 跨会话 / 多 Agent | `ai-coding-guide` | 进入需求→设计→实现→审查→测试→总结状态机 |
| 已有需求文档，要落地 | `ai-coding-guide` | 先核验需求、范围和验收，再按复杂度执行 |
| 写测试驱动 | `mattpocock-skills:tdd`（条件）/ `code-change-workflow` | 红→绿→重构；不替代最终验证 |
| 调 bug | `mattpocock-skills:diagnosing-bugs`（条件）/ `code-change-workflow` | 先复现，再查根因和所有调用方 |
| 改完自验 | 内置 `run` 或项目 test/lint/build/check | 有运行时表面优先跑真实流程，并保存命令与结果 |
| 审 PR / 代码 | 内置 `code-review` | AI 代码至少一次独立轻量复核；高风险再叠加 `security-review` |
| 安全审查 | 内置 `security-review` | auth / 权限 / DB / 架构 / 外部 IO 等高风险场景 |
| 快速小改 | 直接最小改动；`ponytail`（条件） | 跨模块或超过 3 文件重新分诊 |
| 学新代码库 | `lean-ctx` / `gitnexus-exploring` | 先结构，后调用链和影响范围 |
| 前端视觉 | `ai-coding-guide` 前端视觉子路径 | 先定方向，再实现和验证；不指向已归档 frontend-guide |
| 路由/Skill 维护 | `guide-skill-auditor` | 行为变化再叠加对应审查/评估流程 |
| 循环 / 定时 | 内置 `/loop` | 省略间隔时按任务变化自定步调 |

## 原则

- **先澄清后设计**：需求模糊先澄清；目标明确但任务大，进入 `ai-coding-guide` 状态机；小改不套重流程
- **按复杂度加流程**：单环问题只用单环 Skill；跨会话、多 Agent、高风险才增加状态机、隔离和恢复检查
- **验证不是结论**：审查负责找错，真实命令或运行时流程负责证明行为；AI 代码不因改动小而跳过独立轻量复核
- **YAGNI**：能删 / 能复用 / 能不写 → 不写；没有观测落点的组织指标不写成硬门禁

## 何时不用 skill

- 单文件 bug、机械重命名、纯格式 → 直接改
- 纯问答、查资料 → 直接答
