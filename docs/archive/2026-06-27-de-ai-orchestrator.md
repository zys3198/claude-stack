# De-AI Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 `de-ai-orchestrator` 编排 skill，自动串联 `humanizer-zh` / `shuorenhua` / `ai-text-polisher`，按档位路由去 AI 味处理；同时改 `article-writing-guide` 路由。

**Architecture:** 一个新 skill 做“判档 + 串联 + 降级 + 回执”，不改 deep 改稿 skill 自身。`article-writing-guide` 第 ⑤ 阶段和默认 pipeline 都改为先到编排器，再由编排器分发。

**Tech Stack:** Markdown SKILL.md，Claude Code skill 框架；本地 skills 目录 `C:\Users\zys31\.claude\skills\`。

---

## Global Constraints

- 路径：`C:\Users\zys31\.claude\skills\`；Windows 平台，使用正斜杠或双反斜杠。
- 现有 skill 元信息样式：必须含 `name:` + `description:`（多行），可选 `metadata.trigger`。
- 中文回复；行文遵循 caveman（开发/计划阶段省 token）。
- 不修改 `ai-text-polisher`、`humanizer-zh`、`shuorenhua` 内部。
- 不接女娲；女娲始终手动。
- 回执必带档位、链路、跳过适配器、询问轮次、是否建议跑女娲。
- 备份策略：覆盖前备份到 `<name>.bak`。

---

## File Structure

| 文件 | 类型 | 职责 |
| --- | --- | --- |
| `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md` | 新增 | 编排器入口，定义档位、路由、降级、回执 |
| `C:\Users\zys31\.claude\skills\article-writing-guide\SKILL.md` | 改 | 第 ⑤ 阶段路由改写；默认 pipeline 同步 |
| `C:\Users\zys31\.claude\skills\article-writing-guide\CHANGELOG.md` | 改 | 记录本次路由变更 |

---

## Task 1: 新增 `de-ai-orchestrator` skill 元信息

**Files:**
- Create: `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`

**Interfaces:**
- Consumes: 无
- Produces: 一个标准 skill 元信息头，name=`de-ai-orchestrator`，description 含触发词与档位提示。

- [ ] **Step 1: 新建目录**

```bash
mkdir -p "C:/Users/zys31/.claude/skills/de-ai-orchestrator"
```

- [ ] **Step 2: 写 SKILL.md frontmatter 与概述**

文件 `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`：

```markdown
---
name: de-ai-orchestrator
description: >
  去 AI 味编排器。判档（轻 / 中 / 重），按档位自动串联 humanizer-zh / shuorenhua / ai-text-polisher，
  保留事实、术语、语域、责任主体；支持 auto / interactive 两种模式。
  触发：用户说"去 AI 味 / 像人写的 / 自然一点 / 改得更像我 / 自动改 / 深改 / 注入观点"。
  不触发：用户点名 humanizer-zh / shuorenhua / polisher 具体 skill（直达）；
  英文文本（退出）。
metadata:
  trigger: 去 AI 味 / 自然一点 / 深改
  source: 本地新设计
---

# De-AI Orchestrator — 去 AI 味编排器

## 定位

只做“判档 + 串联 + 降级 + 回执”，不替代 deep 改稿 skill。

## 适用与不适用

- 适用：中文技术文章、博客、自媒体初稿、AI 生成草稿。
- 不适用：英文文本；纯代码 / 表格 / 合规条款（只清连接词）。

## 流程

1. 判档（轻 / 中 / 重）
2. 串联适配器
3. 缺适配器降级
4. 输出文本 + 回执
5. 写回时自动跑 chinese-markdown-normalizer
```

- [ ] **Step 3: 验证文件落盘**

Run: `ls "C:/Users/zys31/.claude/skills/de-ai-orchestrator"`
Expected: 输出 `SKILL.md`。

- [ ] **Step 4: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/de-ai-orchestrator/SKILL.md
git commit -m "feat(de-ai-orchestrator): 新增去 AI 味编排器骨架"
```

---

## Task 2: 写入档位判定与路由表

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`

**Interfaces:**
- Consumes: Task 1 的 frontmatter + 概述
- Produces: §档位与路由；含三档链、判定顺序、英文/不应洗文本的退出条件。

- [ ] **Step 1: 追加 §档位与路由章节**

在 Task 1 的文件末尾追加：

```markdown
## 档位与路由

### 三档

| 档位 | 触发 | 链路 | 用户参与 |
| --- | --- | --- | --- |
| 轻 | “轻度去 AI 味 / 自动扫一遍 / 先用规则清洗” | humanizer-zh | 无 |
| 中 | “去 AI 味 / 自然一点 / 像人写的”（默认） | humanizer-zh → shuorenhua | 无 |
| 重 | “深改 / 要观点 / 更像我 / 要踩坑感” | ai-text-polisher → humanizer-zh → shuorenhua | 至少 1 轮 |

### 判定顺序

1. 文本语言非中文 → 退出，交回英文链
2. 代码块 / 表格 / API 字段 / 合规条款 → 仅清连接词，标 “事实保真优先”
3. 重度信号词命中 → 重
4. 用户要“全自动 / 不要停”→ 轻或中（不强行重）
5. 默认 → 中
```

- [ ] **Step 2: 验证 frontmatter 不动**

Run: `head -n 16 "C:/Users/zys31/.claude/skills/de-ai-orchestrator/SKILL.md"`
Expected: frontmatter 头未改。

- [ ] **Step 3: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/de-ai-orchestrator/SKILL.md
git commit -m "feat(de-ai-orchestrator): 写入三档路由与判定顺序"
```

---

## Task 3: 写入适配器契约与降级表

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`

**Interfaces:**
- Consumes: Task 2 的路由表
- Produces: §适配器契约 + §失败与降级

- [ ] **Step 1: 追加章节**

```markdown
## 适配器契约

| 适配器 | 来源 | 必备 | 缺失降级 |
| --- | --- | --- | --- |
| humanizer-zh | op7418/Humanizer-zh | 必备 | 缺则跳到 ai-text-polisher 或 shuorenhua；标 “已跳规则扫描” |
| shuorenhua | MrGeDiao/shuorenhua | 可选 | 缺则跳过；重度档砍尾；标 “已跳 AI 套路检查” |
| ai-text-polisher | 本地 | 可选 | 缺则重度档退回 humanizer-zh → shuorenhua；标 “已退回纯规则链” |
| 女娲 | 手动 | — | 永远不被调用；回执提示手动 |

## 失败与降级

- 缺 shuorenhua：跳过该步，链路其余继续。
- 缺 humanizer-zh：跳到下一档，回执标 “已降级”。
- 缺 ai-text-polisher + 用户要重度：弹警告，问是否接受降级；默认不降级。
- 重度档默认交互；用户显式 “全自动 / 不要停” → 内部硬切 “仅深改版 + 不暂停”，仍走 polisher 一遍，再接 humanizer-zh / shuorenhua。
- 不该洗的文本：仅清“此外 / 然而 / 综上所述”等连接词，不动事实与术语。
```

- [ ] **Step 2: 验证文件结构**

Run: `grep -c "^## " "C:/Users/zys31/.claude/skills/de-ai-orchestrator/SKILL.md"`
Expected: 5（含 frontmatter 后开始的 4 个章节：定位 / 档位与路由 / 适配器契约 / 失败与降级；若把“流程”计入则 5）。

- [ ] **Step 3: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/de-ai-orchestrator/SKILL.md
git commit -m "feat(de-ai-orchestrator): 适配器契约与降级表"
```

---

## Task 4: 写入输出与回执规范

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`

**Interfaces:**
- Consumes: Task 3 的契约
- Produces: §输出与回执 + §护栏

- [ ] **Step 1: 追加章节**

```markdown
## 输出与回执

### 回执模板

```
## 去 AI 味回执

- 档位：中
- 链路：humanizer-zh → shuorenhua
- 跳过的适配器：无
- 询问轮次：0（auto 模式）
- 后续建议：需要学你文风请手动跑女娲
```

### 输出格式

- 默认：对话内输出新文。
- 显式传文件路径：原地覆盖；备份原文件到 `<name>.bak`。
- 中间产物可见性：
  - 重度档：分段贴出 “polisher 改写 → humanizer 处理 → shuorenhua 处理”
  - 中档：贴出 “humanizer 处理 → shuorenhua 处理”
  - 轻档：贴出 “humanizer 处理”
- 改写完成后自动跑 chinese-markdown-normalizer 做最后排版（写回原文件时启用）。

## 护栏

- humanizer-zh / shuorenhua 都不编造经历、立场、数据。
- 只有 ai-text-polisher 能动观点层。
- ai-text-polisher 多轮阶段不回写原文件；final 输出阶段才写。
```

- [ ] **Step 2: 验证章节数**

Run: `grep -c "^## " "C:/Users/zys31/.claude/skills/de-ai-orchestrator/SKILL.md"`
Expected: 7（定位 / 流程 / 档位与路由 / 适配器契约 / 失败与降级 / 输出与回执 / 护栏）。

- [ ] **Step 3: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/de-ai-orchestrator/SKILL.md
git commit -m "feat(de-ai-orchestrator): 输出与回执规范 + 护栏"
```

---

## Task 5: 改 `article-writing-guide` 路由表（第 ⑤ 阶段）

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\article-writing-guide\SKILL.md` §1 路由表第 ⑤ 行

**Interfaces:**
- Consumes: 现有 `article-writing-guide` 路由表
- Produces: 第 ⑤ 阶段从 `ai-text-polisher` 改为 `de-ai-orchestrator`

- [ ] **Step 1: 用原生 Read 读目标行附近**

Run: `Read` 工具，文件 `C:\Users\zys31\.claude\skills\article-writing-guide\SKILL.md`，定位含 “AI 味太重” 的行附近。

- [ ] **Step 2: 编辑该行**

原行：

```
| ⑤ 去 AI 味/润色 | "AI 味太重""改得像人写的""优化文风" | `ai-text-polisher`🪨 |
```

改为：

```
| ⑤ 去 AI 味/润色 | "AI 味太重""改得像人写的""优化文风" | `de-ai-orchestrator`🪨 |
```

- [ ] **Step 3: 改“易混 skill 区分”的去 AI 味条款**

原句：

> 去 AI 味/文风 → `ai-text-polisher`

改为：

> 去 AI 味/文风 → `de-ai-orchestrator`（内部判档 → 串联 humanizer-zh / shuorenhua / ai-text-polisher）

- [ ] **Step 4: 验证改动**

Run: `grep -n "ai-text-polisher\|de-ai-orchestrator" "C:/Users/zys31/.claude/skills/article-writing-guide/SKILL.md" | head -n 20`
Expected: 路由表第 ⑤ 行改为 `de-ai-orchestrator`；其他段落不再单独推荐 `ai-text-polisher`。

- [ ] **Step 5: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/article-writing-guide/SKILL.md
git commit -m "refactor(article-writing-guide): 第 ⑤ 阶段路由改为 de-ai-orchestrator"
```

---

## Task 6: 改默认 pipeline

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\article-writing-guide\SKILL.md` §3 默认 pipeline 段

**Interfaces:**
- Consumes: Task 5 改后的路由
- Produces: 通用 pipeline 第 ⑤ 步从 `ai-text-polisher` 改为 `de-ai-orchestrator`

- [ ] **Step 1: 编辑通用技术写作 pipeline**

原句（含 `ai-text-polisher`）：

```
`doc-finder/deep-research`(选型) → `article-writer`(起草) → `edit-article`(结构) → `ai-text-polisher`(去AI味) → ...
```

改为：

```
`doc-finder/deep-research`(选型) → `article-writer`(起草) → `edit-article`(结构) → `de-ai-orchestrator`(去AI味) → ...
```

- [ ] **Step 2: 编辑 JavaGuide 模式 pipeline**

同上，把 `ai-text-polisher` 替换成 `de-ai-orchestrator`。

- [ ] **Step 3: 验证**

Run: `grep -n "ai-text-polisher\|de-ai-orchestrator" "C:/Users/zys31/.claude/skills/article-writing-guide/SKILL.md"`
Expected: 路由表 §1 第 ⑤ 行、§3 pipeline 两处都用 `de-ai-orchestrator`；`ai-text-polisher` 不再出现在路由/流水线中。

- [ ] **Step 4: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/article-writing-guide/SKILL.md
git commit -m "refactor(article-writing-guide): 默认 pipeline 改用 de-ai-orchestrator"
```

---

## Task 7: 写 CHANGELOG

**Files:**
- Modify: `C:\Users\zys31\.claude\skills\article-writing-guide\CHANGELOG.md`

**Interfaces:**
- Consumes: Task 5 / Task 6 的改动事实
- Produces: 一条记录本次路由变更的条目

- [ ] **Step 1: 读现有 CHANGELOG 顶部，确认最新版本号格式**

Run: `Read` 工具，文件 `C:\Users\zys31\.claude\skills\article-writing-guide\CHANGELOG.md`，`limit=40`。

- [ ] **Step 2: 在最新条目之上加新条目**

文件顶部（最新一条之上）追加：

```markdown
## 2026-06-27 — 路由收口到 de-ai-orchestrator

- 新增 `de-ai-orchestrator` skill：判档 + 串联 humanizer-zh / shuorenhua / ai-text-polisher，按档位自动跑；保留事实与术语；不接女娲（手动）。
- `article-writing-guide` §1 第 ⑤ 阶段从 `ai-text-polisher` 改为 `de-ai-orchestrator`。
- 默认 pipeline（通用 + JavaGuide 模式）第 ⑤ 步同步改为 `de-ai-orchestrator`。
- 现有 `ai-text-polisher` / `humanizer-zh` / `shuorenhua` 内部未改；保留直达入口。
```

- [ ] **Step 3: 验证**

Run: `grep -n "de-ai-orchestrator" "C:/Users/zys31/.claude/skills/article-writing-guide/CHANGELOG.md"`
Expected: 至少 1 行命中。

- [ ] **Step 4: 提交**

```bash
cd "C:/Users/zys31/.claude"
git add skills/article-writing-guide/CHANGELOG.md
git commit -m "docs(article-writing-guide): 记 de-ai-orchestrator 路由变更"
```

---

## Self-Review

1. **Spec 覆盖**：
   - §2 三档 → Task 2
   - §3 适配器契约 → Task 3
   - §4 失败与降级 → Task 3
   - §5 输出与回执 → Task 4
   - §6 文件改动清单 → Task 1 / 5 / 6 / 7

2. **占位符扫描**：无 TBD/TODO；步骤命令、文件路径、提交信息都已写实。

3. **类型一致性**：
   - SKILL.md frontmatter `name` 全程用 `de-ai-orchestrator`。
   - 适配器名 `humanizer-zh` / `shuorenhua` / `ai-text-polisher` 全程一致。
   - 路径用 Windows 反斜杠和正斜杠双写法，二者一致指向同位置。

---

## Execution Handoff

计划落盘到 `C:\Users\zys31\.claude\docs\superpowers\plans\2026-06-27-de-ai-orchestrator.md`。

两种执行方式：

1. Subagent-Driven（推荐）：每个 Task 派一个新 subagent，Task 间有 review 关卡。
2. Inline Execution：在本会话里按 Task 1 → 7 顺序执行，含 checkpoint。

要哪个？