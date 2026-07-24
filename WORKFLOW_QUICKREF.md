# Skill 路由速查

> 日常一眼查。重决策 / 多步流程走 `ai-coding-guide` skill。

## 任务 → Skill

| 你要做 | 用哪个 | 备注 |
|--------|--------|------|
| 需求模糊，要澄清 | Matt `grill-me` | 逐问逐答，比 brainstorming 轻 |
| 大功能 / 架构设计 | SP `brainstorming` | HARD-GATE，没设计不让写码 |
| 落地拆任务 | SP `writing-plans` | 已有需求时 |
| 轻量拆任务 | agent-skills `planning-and-task-breakdown` | 不想进 SP 重流程 |
| 写测试驱动 | SP `test-driven-development` | |
| 调 bug | SP `systematic-debugging` | 4 阶段根因 |
| 改完自验 | SP `verification-before-completion` | |
| 审 PR / 代码 | SP `requesting-code-review` | 日常自检 |
| 安全审查 | codex-security `security-diff-scan` | auth / DB / 架构 |
| 快速小改 | ponytail（常驻 active） | YAGNI / stdlib first |
| 学新代码库 | understand-anything / Matt `zoom-out` | 深 vs 浅 |
| 前端开发 | build-web-apps `frontend-app-builder` | |
| 循环 / 定时 | 内置 `/loop` `/goal` | |

## 原则

- **先澄清后设计**：需求模糊 → grill-me；清楚但大 → brainstorming；小改 → 直接 ponytail
- **不并发触发**：SP 流程先行（设计 / 调试 / 验证），审查后置
- **YAGNI**：ponytail 常驻，能删 / 能复用 / 能不写 → 不写
- **跳过 ECC**：一人公司画像，60+ agent 太重（见 memory `skill-ecosystem-choice-2026-07`）

## 何时不用 skill

- 单文件 bug、机械重命名、纯格式 → 直接改
- 纯问答、查资料 → 直接答
