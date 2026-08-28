---
name: cold-skills-index
description: >-
  冷技能索引。本地冷技能已打 disable-model-invocation 不占系统提示，需要时用
  Skill 工具按 name 显式调用。列出全部冷技能名称与用途（分类 + 深冻层）。
---

# 冷技能索引

冷技能不出现在自动可用列表，但可用 Skill 工具显式调用（传 name）。
冷/深冻分级思路移植自 pi 三阶技能治理（2026-08-28）：热 = 正常注入系统提示；
冷 = disable-model-invocation 不进系统提示，靠本索引按需发现；深冻 = 长期不用/重复能力，
无索引入口，仅 `/skill:<name>` 或 grep MANIFEST 可达，正常任务禁止主动用。

## 本地冷技能（~/.claude/skills/，disable-model-invocation: true）

### 讲解/教学

| name | 用途 |
|------|------|
| eli5 | 把概念讲给外行听 |
| lesson-svg-diagram | 课程 HTML 内联 SVG 配图 |

### 浏览器/工具

| name | 用途 |
|------|------|
| kimi-webbridge | 本地 WebSocket 控制真实浏览器（127.0.0.1:10086） |

## 已启用但低频插件（settings.json enabledPlugins=true，实测 2026-08-28 全 true）

> 更正 2026-08-28：本节原标「已禁插件」，实测 settings.json enabledPlugins 无 false 项
> （officecli/ppt-master/taste-skill/frontend-design 均 true）——插件实际全部启用中。
> 需要真「冷」时手动改 settings.json 对应项为 false，或用 `/plugin disable <name>`。

### 办公/文档

| 插件 | 用途 | 使用证据 |
|------|------|---------|
| officecli | Office 文档 CLI | 0 用/738 会话 |
| ppt-master | SVG→PPTX 生成 | 0 用/742 会话 |

### 设计/前端

| 插件 | 用途 | 使用证据 |
|------|------|---------|
| taste-skill | 图片生成风格 | 4 用/725 会话 |
| frontend-design | 前端设计 | 0 用/54 会话 |

## 深冻层（无索引入口，仅显式调用）

当前无深冻项。进入条件：冷技能/插件连续跨越多轮审计（skill-trimmer / cold-skills-index）
仍 0 使用，且存在等价替代 → 记入 `installing/` 台账后下沉至此。
深冻项不在此索引列条目（保持索引只放"可能有用"的冷项）。

## 转热 / 转深冻方法

- 冷技能转热：删 SKILL.md frontmatter 的 `disable-model-invocation: true` 行
- 插件转热：settings.json `enabledPlugins` 对应项改 true
- 转深冻：先在 `installing/` 台账记一笔（来源/日期/下沉理由），再在本索引移除条目
