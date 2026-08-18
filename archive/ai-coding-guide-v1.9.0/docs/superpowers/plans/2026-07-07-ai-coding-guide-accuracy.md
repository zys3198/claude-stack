# ai-coding-guide Accuracy Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `ai-coding-guide` into a Claude Code–specific, evidence-labeled routing skill with aligned reference docs, regression prompts, and an accuracy audit script.

**Architecture:** Keep live routing in `SKILL.md`, move explanation-heavy comparisons to `references/ecosystems.md`, and keep update policy in `references/MAINTENANCE.md`. Implement the spec in P0 → P1 → P2 order: first remove dead references and non-Claude default paths, then tighten claim language and evidence labels, then slim structure; finish by aligning `test-prompts.json` and `scripts/audit.ps1`.

**Tech Stack:** Markdown, JSON, PowerShell, Claude Code skill conventions, `pwsh`, `python312`, `rg`

## Global Constraints

- Scope stays **Claude Code current environment only**.
- Modify only `SKILL.md`, `references/ecosystems.md`, `references/MAINTENANCE.md`, `test-prompts.json`, and `scripts/audit.ps1`.
- Do not re-expand the guide into a multi-IDE comparison.
- Use the four evidence labels exactly: `本地已证实`, `官方可证实`, `经验判断`, `证据不足`.
- Fix P0 routing hazards before P1 wording issues, and P1 before P2 structure cleanup.
- Keep `SKILL.md` for routing only; long comparison prose belongs in `references/ecosystems.md`.
- Keep `references/MAINTENANCE.md` for maintenance policy only; no routing prose in that file.
- `scripts/audit.ps1` is a 疑点扫描器, not a truth engine; it should fail only on parser errors or P0/P1 findings.
- `test-prompts.json` is a regression corpus for high-frequency routing cases, not a FAQ dump.
- Commit steps require explicit user approval before `git commit`; if approval is not granted, stop after verification and report a ready-to-commit diff.

---

## File Responsibility Map

- `SKILL.md` — runtime router loaded on trigger; owns scope, evidence posture, category extraction, AskUserQuestion flow, and minimal quick-reference tables.
- `references/ecosystems.md` — on-demand explanation layer; owns ecosystem roles, overlap handling, fallback choices, and “why A not B” detail.
- `references/MAINTENANCE.md` — maintenance playbook; owns update triggers, evidence sources, sync checklist, and changelog format.
- `test-prompts.json` — route-regression corpus; owns representative prompts and exact expected routing outcomes.
- `scripts/audit.ps1` — static suspicion scan; owns dead-ref detection, cross-IDE residue detection, overclaim wording scan, and manual-review markers.

---

### Task 1: Rewrite maintenance contract

**Files:**
- Modify: `references/MAINTENANCE.md:1-69`

**Interfaces:**
- Consumes: spec sections `6.3`, `7`, `8`, `12`, `14` from `docs/superpowers/specs/2026-07-07-ai-coding-guide-accuracy-design.md`
- Produces: canonical evidence-source order (`本地已证实` → `官方可证实` → `经验判断` → `证据不足`), update triggers, and sync checklist used by Tasks 2-6

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'references/MAINTENANCE.md' -Raw; if ($c -match 'Codex|Cursor|Windsurf|opencode' -or $c -match '不删历史' -or $c -notmatch '证据源' -or $c -notmatch '同步文件') { Write-Host 'maintenance doc stale'; exit 1 }"
```
Expected: FAIL with `maintenance doc stale`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'references/MAINTENANCE.md' -Raw; if ($c -match 'Codex|Cursor|Windsurf|opencode' -or $c -match '不删历史' -or $c -notmatch '证据源' -or $c -notmatch '同步文件') { Write-Host 'maintenance doc stale'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
@'
# 维护说明

本文件只在更新 `ai-coding-guide` 时使用。主文件负责运行时路由；本文件只负责维护规则、证据源和变更记录。

主文件路径：`SKILL.md`

---

## 何时必须更新

| 触发信号 | 必做动作 |
|---|---|
| 新装或卸载 Claude Code skill / 插件 | 复核 `SKILL.md` 推荐路径、`references/ecosystems.md` 生态说明、`test-prompts.json` 样例 |
| 系统 reminder 新增/删除 skill 名 | 先对照 reminder，再对照 `~/.claude/skills/` 与 `~/.claude/plugins/cache/` |
| 用户指出推荐过时、死引用、错归属 | 先查证据，再修正文案，再补 changelog |
| 路由决策改了 A/B/C 选项或 fallback | 同步 `SKILL.md`、`references/ecosystems.md`、`test-prompts.json` |
| 新增或删除“必须 / 默认 / 官方 / 已装”类断言 | 复核证据等级，并把不确定项降级或删除 |
| `scripts/audit.ps1` 新增扫描规则 | 同步本文件的证据说明和巡检说明 |

## 证据源

按以下顺序取证，不跳级：

1. **本地已证实**：当前会话 system reminder、`~/.claude/skills/`、`~/.claude/plugins/cache/`、当前仓库文件。
2. **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
3. **经验判断**：维护者推荐、默认建议、经验排序；必须显式标成推荐，不得写成硬事实。
4. **证据不足**：影响主推荐结论时停下来问用户；不影响时标“不确定”或直接删。

## 同步文件

每次维护至少检查以下文件是否一起更新：

- `SKILL.md`
- `references/ecosystems.md`
- `references/MAINTENANCE.md`
- `test-prompts.json`
- `scripts/audit.ps1`

## 更新流程

1. 读已批准 spec：`docs/superpowers/specs/2026-07-07-ai-coding-guide-accuracy-design.md`
2. 扫当前会话可用项和本地安装项
3. 先修 P0：死 skill / 死命令 / 死路径 / 错默认路径 / 错归属
4. 再修 P1：过满措辞、把推荐写成事实、数量和边界断言不稳
5. 最后修 P2：主文件过重、信息重复、规则散落
6. 运行 `scripts/audit.ps1`，并抽查 `test-prompts.json`
7. 记录 changelog

## 维护纪律

- 主语统一为 Claude Code 当前环境
- `SKILL.md` 不塞维护历史
- `references/ecosystems.md` 不抢主文件路由职责
- `scripts/audit.ps1` 只报疑点，不替代人工判真
- 看见死引用或错归属，当场修，不拖到下次

## 变更记录

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-07-07 | 重写维护说明为 Claude Code 专用准确性维护手册 | 与 accuracy spec 对齐，去掉旧多 IDE 残留和历史包袱 |
'@ | Set-Content -Path 'references/MAINTENANCE.md' -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'references/MAINTENANCE.md' -Raw; if ($c -match 'Codex|Cursor|Windsurf|opencode' -or $c -match '不删历史' -or $c -notmatch '证据源' -or $c -notmatch '同步文件') { Write-Host 'maintenance doc stale'; exit 1 }"
```
Expected: PASS with exit code `0`

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add references/MAINTENANCE.md
git commit -m "docs: tighten ai-coding-guide maintenance contract"
```

---

### Task 2: Rewrite `SKILL.md` scope and evidence prelude

**Files:**
- Modify: `SKILL.md:1-90`

**Interfaces:**
- Consumes: evidence-source order from Task 1
- Produces: canonical scope sentence, Claude Code–only self-check rules, and terminology used by Tasks 3-6

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'IDE 能力对照' -or $c -match '~/.codex/' -or $c -match '~/.cursor/' -or $c -match '~/.windsurf/' -or $c -notmatch 'Claude Code 当前环境') { Write-Host 'skill prelude stale'; exit 1 }"
```
Expected: FAIL with `skill prelude stale`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'IDE 能力对照' -or $c -match '~/.codex/' -or $c -match '~/.cursor/' -or $c -match '~/.windsurf/' -or $c -notmatch 'Claude Code 当前环境') { Write-Host 'skill prelude stale'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
$path = 'SKILL.md'
$old = Get-Content $path -Raw
$parts = $old -split '## 交互决策流程', 2
$prefix = @'
---
name: ai-coding-guide
description: Use when user asks which skill/tool/ecosystem to use inside Claude Code, how Superpowers/agent-skills/ponytail/ecc (or any installed plugin) differ or compare, which fits a task, how to combine them, or when a new plugin/skill is installed and this guide needs updating. 中文触发：用哪个工具、X和Y区别/冲突吗、有什么工具能用、刚装了X插件、X不能用了、SP/agent-skills 怎么选、哪个更好、该用什么、怎么配合。Living doc — evolves as the Claude Code environment changes.
---

# AI 编码路由指南（Claude Code）

## 定位与质量标准

**定位：** 本 skill 是 Claude Code 当前环境下的选型路由器。它回答“这类任务先走哪条流程、该用哪个 skill、哪些推荐是当前默认项、推荐证据是什么”。它不认领下游 skill 的完整执行权威；执行纪律以下游 skill 和项目级 `CLAUDE.md` 为准。

**质量底线：**
- **准确**：skill 名、命令名、目录路径、插件归属先查当前会话或本地文件，再写结论。
- **AI 可读**：主文件只放路由和最小速查，长解释外置到 `references/ecosystems.md`。
- **可进化**：发现死引用、错归属、错默认路径时当场修，并同步 `references/MAINTENANCE.md`。

## 环境自检

触发本 skill 后，先按 Claude Code 当前环境复核可用性：

1. **先看当前会话 system reminder**：reminder 里出现的 skill / agent / tool 一定可用。
2. **再看顶层独立 skill**：`~/.claude/skills/`（本机由 cc-switch 同步，源目录通常是 `~/.cc-switch/skills/`）。
3. **再看插件附带 skill**：`~/.claude/plugins/cache/*/skills/`。
4. **关键提醒**：reminder 没列出 ≠ 一定不存在；关键推荐前要按磁盘再复核一次。

## 证据门槛

- **本地已证实**：当前会话可见、本机目录可见、当前仓库文件可见。
- **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
- **经验判断**：默认建议、经验排序、惯用主路径；要写成推荐，不写成定律。
- **证据不足**：影响主推荐结论时停下来问用户；不影响则标“不确定”或删除。
'@
Set-Content -Path $path -Value ($prefix + "`n## 交互决策流程" + $parts[1]) -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'IDE 能力对照' -or $c -match '~/.codex/' -or $c -match '~/.cursor/' -or $c -match '~/.windsurf/' -or $c -notmatch 'Claude Code 当前环境') { Write-Host 'skill prelude stale'; exit 1 }"
```
Expected: PASS with exit code `0`

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add SKILL.md
git commit -m "docs: narrow ai-coding-guide scope to Claude Code"
```

---

### Task 3: Rewrite routing decision flow in `SKILL.md`

**Files:**
- Modify: `SKILL.md:91-336`

**Interfaces:**
- Consumes: canonical scope and evidence wording from Task 2
- Produces: category names, AskUserQuestion choices, and fallback language consumed by Tasks 4-6

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'Trellis' -or $c -match 'IDE 依赖' -or $c -match 'opencode' -or $c -notmatch '分类: 开发新功能' -or $c -notmatch '分类: 快速改动') { Write-Host 'routing flow stale'; exit 1 }"
```
Expected: FAIL with `routing flow stale`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'Trellis' -or $c -match 'IDE 依赖' -or $c -match 'opencode' -or $c -notmatch '分类: 开发新功能' -or $c -notmatch '分类: 快速改动') { Write-Host 'routing flow stale'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
$path = 'SKILL.md'
$old = Get-Content $path -Raw
$parts = $old -split '## 交互决策流程', 2
$tail = $parts[1] -split '## 参考内容（新手 & 深度了解用）', 2
$flow = @'
## 交互决策流程

**重要：** 先分类，再推荐，再 AskUserQuestion 收口。除非用户明确说“直接做 / 别问”，否则不要跳过确认。

### Step 1：提取用户意图

| 信号 | 分类 | 示例 |
|---|---|---|
| 开发新功能 | 开发新功能 | “写个登录”“做个新页面”“加个 API” |
| 已有需求/PRD | 有需求文档 | “根据这份 PRD 实现”“需求文档见文件 X” |
| 审查代码 | 审查代码 | “帮我 review”“审查这段代码” |
| 调试 bug | 调试 bug | “报错了”“这个 bug 怎么回事” |
| 快速小改 | 快速改动 | “改个按钮文案”“小修一下” |
| 构建错误 | 构建错误 | “build 报错”“类型错误” |
| 文档写作 | 文档写作 | “写文章”“润色”“审文档” |
| 循环任务 | 循环任务 | “每 5 分钟检查”“持续跑到满足条件” |
| 纯对比/选型问题 | 了解指南 | “SP 和 agent-skills 区别”“该用哪个工具” |

**优先规则：**
- 带明确开工信号的“怎么选”问题，不走泛泛介绍；按任务分类直接给 A/B/C。
- 只有纯抽象对比、没有开工信号时，才走“了解指南”。

### Step 2：匹配推荐路径

分类: 开发新功能
- 需求模糊 → `grill-me`
- 需求清楚且跨模块/要设计 → `superpowers:brainstorming`
- 范围很小 → `ponytail:ponytail`

AskUserQuestion:
- A: 先 `grill-me` 澄清
- B: 直接 `superpowers:brainstorming`
- C: 当成小改动走 `ponytail:ponytail`

Fallback:
- `grill-me` 不在 → 直接 `superpowers:brainstorming`
- 用户明确讨厌重流程 → 降到 `ponytail:ponytail` 或手动澄清

分类: 有需求文档
- 默认主路径 → `superpowers:writing-plans`
- 只想轻量拆任务 → `planning-and-task-breakdown`
- 用户只想先整理需求项 → `to-prd` / `to-issues`

AskUserQuestion:
- A: `superpowers:writing-plans`
- B: `planning-and-task-breakdown`
- C: 先整理需求项

Fallback:
- `superpowers:writing-plans` 不可用 → `planning-and-task-breakdown`
- 用户只要结论不要计划 → 直接回答，不强拉进计划流程

分类: 审查代码
- 先定对象：代码块 / 当前 diff / 指定文件
- 非高风险、小范围 → `superpowers:requesting-code-review`
- 高风险（auth / DB / 架构 / 安全） → `security-and-hardening` + `superpowers:requesting-code-review`

AskUserQuestion:
- A: 轻量审查
- B: 安全/高风险审查
- C: 展示审查路径区别

Fallback:
- 对象不明确 → 先问“贴代码块、给文件路径，还是审当前 diff？”
- `security-and-hardening` 不在 → 走 `superpowers:requesting-code-review` 并明确缺少安全专用层

分类: 调试 bug
- 默认主路径 → `superpowers:systematic-debugging`

AskUserQuestion:
- A: 进入系统化调试
- B: 先看调试路径区别
- C: 我只要你直接判断

Fallback:
- 用户不给复现信息 → 先收错误信息、触发条件、最近改动

分类: 快速改动
- 默认主路径 → `ponytail:ponytail`
- 改动超出 3 文件或开始跨模块 → 重新分类为“开发新功能”

AskUserQuestion:
- A: 走最简改动
- B: 看为什么不建议上重流程
- C: 改成完整功能流程

Fallback:
- 用户说“别省，按完整流程来” → 升到“开发新功能”

分类: 构建错误
- 前端/React/Vue → 对应 `ecc:*build*` 或 `frontend-design` / `react-build-resolver` 这类已装专项 skill
- 通用兜底 → 先跑本地构建命令并按错误原文排查

AskUserQuestion:
- A: 直接排构建错误
- B: 看有哪些专项构建 skill
- C: 我先贴错误原文

Fallback:
- 框架未知 → 先问语言/框架
- 没有专项 skill → 回到构建命令原文 + 手动分析

分类: 文档写作
- 从零写 → `article-writer`
- 规范格式/统一 Markdown → `chinese-markdown-normalizer`
- 审校已有文章 → `review-doc`

AskUserQuestion:
- A: 从零写
- B: 规范/润色
- C: 审校

Fallback:
- skill 不在 → 回到基础人工流程

分类: 循环任务
- 定时轮询 → `/loop`
- 条件驱动 → `/goal`

AskUserQuestion:
- A: `/loop`
- B: `/goal`
- C: 先确认终止条件

Fallback:
- 若命令不可用 → 说明不可用并回到手动执行

分类: 了解指南
- 展示最小速查 + `references/ecosystems.md`
- 展示完后再问“现在要执行什么”

### Step 3：收敛规则

- 第一次拒绝 A → 排除 A，只问剩余选项
- 第二次仍拒绝 → 展示剩余全部选项让用户自选
- 第三轮仍无共识 → 停止路由，直接问用户当前真实目标
- 同一分类在同一 session 重复触发时，沿用上次被拒选项，不重置

### Step 4：无匹配

当分类不清时，用 AskUserQuestion 问：
- A: 想开发新功能
- B: 已有需求文档，想落地
- C: 想审查代码
- D: 想调试 bug
- E: 想处理文档
- F: 只是想了解该用什么
'@
Set-Content -Path $path -Value ($parts[0] + $flow + "`n## 参考内容（新手 & 深度了解用）" + $tail[1]) -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'SKILL.md' -Raw; if ($c -match 'Trellis' -or $c -match 'IDE 依赖' -or $c -match 'opencode' -or $c -notmatch '分类: 开发新功能' -or $c -notmatch '分类: 快速改动') { Write-Host 'routing flow stale'; exit 1 }"
```
Expected: PASS with exit code `0`

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add SKILL.md
git commit -m "docs: rewrite ai-coding-guide routing flow"
```

---

### Task 4: Slim reference layer and rewrite ecosystem details

**Files:**
- Modify: `SKILL.md:337-456`
- Modify: `references/ecosystems.md:1-320`

**Interfaces:**
- Consumes: route categories and AskUserQuestion choices from Task 3
- Produces: minimal quick-reference tables in `SKILL.md` and explanation-heavy comparison rules in `references/ecosystems.md`

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$skill = Get-Content 'SKILL.md' -Raw; $eco = Get-Content 'references/ecosystems.md' -Raw; if ($skill -match 'Codex' -or $skill -match 'Cursor' -or $skill -match 'Windsurf' -or $eco -match 'IDE 无关' -or $eco -match 'Codex 专用' -or $skill -notmatch '生态速查' -or $eco -notmatch 'Superpowers') { Write-Host 'reference layer stale'; exit 1 }"
```
Expected: FAIL with `reference layer stale`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$skill = Get-Content 'SKILL.md' -Raw; $eco = Get-Content 'references/ecosystems.md' -Raw; if ($skill -match 'Codex' -or $skill -match 'Cursor' -or $skill -match 'Windsurf' -or $eco -match 'IDE 无关' -or $eco -match 'Codex 专用' -or $skill -notmatch '生态速查' -or $eco -notmatch 'Superpowers') { Write-Host 'reference layer stale'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
$skillTail = @'
## 参考内容（新手 & 深度了解用）

以下内容只在用户选“看详情”或被归类为“了解指南”时展开。

### 生态速查

| 能力域 | 默认主路径 | 何时用 |
|---|---|---|
| 流程纪律 | `superpowers:*` | 新功能设计、计划、TDD、调试、验证 |
| SDLC 补充 | `agent-skills` | spec / review / security / breakdown 这类补充能力 |
| 快速小改 | `ponytail:ponytail` | 小范围改动、YAGNI、最短路径 |
| 前端/体验 | `frontend-design` / `feature-dev:*` | UI、前端特性、体验型任务 |
| 语言专项 | `ecc:*review*` / `ecc:*build*` | 语言或框架专用 reviewer / build resolver |
| 代码理解 | `lean-ctx` / `understand` / `gitnexus-*` | 查结构、看影响范围、压缩上下文 |
| 文档写作 | `article-writer` / `review-doc` / `chinese-markdown-normalizer` | 写、审、规范文章 |

### 决策速查

| 你说 | 默认建议 |
|---|---|
| “想写个功能” | 先判需求是否模糊：模糊走 `grill-me`，清楚且大走 `superpowers:brainstorming`，很小走 `ponytail:ponytail` |
| “我有 PRD，下一步怎么做” | `superpowers:writing-plans` |
| “帮我 review” | 小范围走 `superpowers:requesting-code-review`；高风险加 `security-and-hardening` |
| “这个 bug 怎么回事” | `superpowers:systematic-debugging` |
| “改个小文案” | `ponytail:ponytail` |
| “build 报错” | 先找专项 build resolver；没有就回构建原文 |
| “SP 和 agent-skills 区别” | 展开 `references/ecosystems.md`，再问当前要执行什么 |

### 反模式与失败处理

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 纯名词解释 | 直接解释 | 误拉进 A/B/C 执行选择 |
| 用户说“直接做” | 跳过 AskUserQuestion | 继续追问流程选择 |
| 高风险审查 | `security-and-hardening` + `superpowers:requesting-code-review` | 只做一轮浅审 |
| 小改动开始跨模块 | 升级到“开发新功能” | 硬留在 ponytail |
| 证据不足影响主推荐 | 停下来问用户 | 拍脑袋补全 |

### 选型速判

| 场景 | 推荐主力 | 原因 |
|---|---|---|
| 需求模糊 | `grill-me` | 最轻的澄清层 |
| 需求清楚且要设计 | `superpowers:brainstorming` | 设计先行 |
| 已有 spec / PRD | `superpowers:writing-plans` | 计划层最稳 |
| 快速小改 | `ponytail:ponytail` | 最短工作路径 |
| 高风险代码审查 | `security-and-hardening` + `superpowers:requesting-code-review` | 安全层 + 流程层 |
| 新仓库理解/影响分析 | `lean-ctx` / `understand` / `gitnexus-*` | 先看结构再动手 |

## 进化机制

维护规则、证据源、同步清单、变更记录见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)。
'@

$eco = @'
# 生态详情参考

本文件只在用户要看“为什么推荐 A 而不是 B”时展开。主文件负责路由；本文件负责解释。

主文件路径：`SKILL.md`

---

## 生态角色（Claude Code 当前环境）

### Superpowers

**定位：** 流程纪律层。负责 brainstorming、writing-plans、test-driven-development、systematic-debugging、verification-before-completion 这类硬门禁流程。

**什么时候优先用：**
- 新功能需要设计
- 已有 spec 需要落地计划
- bug 需要根因分析
- 完工前需要证据驱动验证

**不要把它当成：** 所有小改动的默认入口。小改动先看 `ponytail:ponytail`。

### agent-skills

**定位：** SDLC 补充层。补上 spec、breakdown、review、security、debugging 这类可拆分能力。

**什么时候优先用：**
- 已经知道要做 review / security / planning-and-task-breakdown
- 想给 Superpowers 主流程补一个专项环节

**不要把它当成：** 替代 Superpowers 的总流程默认层。两套都能做时，先按主文件路由决定谁做主、谁做补充。

### ponytail / caveman

**定位：** 最简实现层。`ponytail:ponytail` 负责最短工作路径，caveman 负责压缩表达。

**什么时候优先用：**
- 单点小改
- 不值得开完整设计/计划流程
- 用户明确要“快、少、别铺开”

**升级条件：** 一旦改动跨 3 个以上文件、跨模块、开始触及架构边界，就回到主流程。

### claude-plugins-official 补充层

**代表项：** `frontend-design`、`feature-dev:*`、`code-review:*`、`commit-commands:*`。

**作用：** 在主流程确定后，补前端、特性开发、代码审查、提交收尾这些专项动作。

### ecc 语言专项层

**代表项：** `ecc:*review*`、`ecc:*build*`。

**作用：** 当任务已经明确落在某个语言/框架上时，提供更窄的 reviewer 或 build resolver。

**用法：** 先确定任务类型，再决定是否需要专项层；不要先按语言插件倒推任务。

### 上下文 / 理解层

**代表项：** `lean-ctx`、`understand`、`gitnexus-*`。

**作用：** 看结构、看依赖、看影响范围、压缩上下文。

**默认顺序：** 先 `lean-ctx`，再按需要上 `understand` 或 `gitnexus-*`。

---

## 重叠区处理

| 冲突场景 | 默认裁决 | 原因 |
|---|---|---|
| `superpowers:brainstorming` vs `ponytail:ponytail` | 新功能走 Superpowers，小改动走 ponytail | 先按任务规模分层 |
| `superpowers:writing-plans` vs `planning-and-task-breakdown` | 已有 spec 默认 `superpowers:writing-plans` | 计划质量和落地细节更稳 |
| `superpowers:requesting-code-review` vs `code-review-and-quality` | 默认先 `superpowers:requesting-code-review` | 主流程优先 |
| `security-and-hardening` vs 通用 review | 高风险任务把 `security-and-hardening` 叠加到通用 review 上 | 安全是额外维度，不是替代关系 |
| `frontend-design` vs `feature-dev:*` | UI/页面骨架先 `frontend-design`，功能实现再 `feature-dev:*` | 先定界面，再做交互 |
| `lean-ctx` vs `understand` | 日常查代码先 `lean-ctx`，大范围建模再 `understand` | 成本更低 |

---

## 降级路径

| 默认路径不可用 | 降级到 |
|---|---|
| `grill-me` 不在 | `superpowers:brainstorming` 或手动单问单答 |
| `security-and-hardening` 不在 | `superpowers:requesting-code-review` + 明示缺少安全专项层 |
| 专项 build resolver 不在 | 构建原文 + 手动排查 |
| `understand` / `gitnexus-*` 不在 | `lean-ctx` + `rg` + 精读文件 |
| `/loop` 或 `/goal` 不可用 | 明示不可用，改手动执行 |

---

## 维护时要核的点

- 当前会话提醒里有没有该 skill
- `~/.claude/skills/` 是否存在独立 skill
- `~/.claude/plugins/cache/` 是否存在插件附带 skill
- 推荐语气是否越界成“硬事实”
- 主文件是否又长回百科全书
'@

Set-Content -Path 'references/ecosystems.md' -Value $eco -Encoding utf8
Set-Content -Path 'SKILL.md' -Value ((Get-Content 'SKILL.md' -Raw) -replace '(?s)## 参考内容（新手 & 深度了解用）.*$', $skillTail) -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$skill = Get-Content 'SKILL.md' -Raw; $eco = Get-Content 'references/ecosystems.md' -Raw; if ($skill -match 'Codex' -or $skill -match 'Cursor' -or $skill -match 'Windsurf' -or $eco -match 'IDE 无关' -or $eco -match 'Codex 专用' -or $skill -notmatch '生态速查' -or $eco -notmatch 'Superpowers') { Write-Host 'reference layer stale'; exit 1 }"
```
Expected: PASS with exit code `0`

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add SKILL.md references/ecosystems.md
git commit -m "docs: slim ai-coding-guide reference layer"
```

---

### Task 5: Expand route-regression prompts

**Files:**
- Modify: `test-prompts.json:1-20`

**Interfaces:**
- Consumes: canonical route categories from Task 3 and reference phrasing from Task 4
- Produces: stable regression corpus used by Task 6 audit and future manual spot checks

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$data = Get-Content 'test-prompts.json' -Raw | ConvertFrom-Json; if ($data.Count -lt 8) { Write-Host 'prompt corpus too small'; exit 1 }"
```
Expected: FAIL with `prompt corpus too small`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$data = Get-Content 'test-prompts.json' -Raw | ConvertFrom-Json; if ($data.Count -lt 8) { Write-Host 'prompt corpus too small'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
@'
[
  {
    "id": 1,
    "prompt": "想写个登录功能，用 SP 还是 ponytail？",
    "expected": "走『开发新功能』。先按规模分层：需求模糊先 grill-me，需求清楚且跨模块走 superpowers:brainstorming，明确小改才走 ponytail:ponytail。给 A/B/C AskUserQuestion，不展示泛泛大全。",
    "scenario": "带任务信号的对比型问题"
  },
  {
    "id": 2,
    "prompt": "SP 和 agent-skills 有什么区别？",
    "expected": "走『了解指南』。展示最小速查，并按需 Read references/ecosystems.md；展示后再问当前要执行什么。",
    "scenario": "纯抽象对比"
  },
  {
    "id": 3,
    "prompt": "PRD 已经写好了，下一步怎么落地？",
    "expected": "走『有需求文档』。默认推荐 superpowers:writing-plans；轻量拆任务才给 planning-and-task-breakdown 作为 B 选项。",
    "scenario": "已有需求文档"
  },
  {
    "id": 4,
    "prompt": "帮我 review 这个 auth 中间件，里面有 token 校验和权限判断。",
    "expected": "走『审查代码』高风险路径。先定对象，再叠加 security-and-hardening 与 superpowers:requesting-code-review。",
    "scenario": "高风险代码审查"
  },
  {
    "id": 5,
    "prompt": "这个 bug 复现不稳定，先别改代码，帮我定位。",
    "expected": "走『调试 bug』。默认 superpowers:systematic-debugging，先收错误信息、触发条件、最近改动。",
    "scenario": "系统化调试"
  },
  {
    "id": 6,
    "prompt": "把这个按钮文案从『提交』改成『保存』，别走复杂流程。",
    "expected": "走『快速改动』。默认 ponytail:ponytail；只要范围扩大到跨模块，再升级分类。",
    "scenario": "小范围最简改动"
  },
  {
    "id": 7,
    "prompt": "刚装了个新 skill，这个 ai-coding-guide 也要改吗？",
    "expected": "触发 ai-coding-guide 更新场景。先按当前会话和 ~/.claude 目录查证，再同步 SKILL.md / references / test-prompts / audit。",
    "scenario": "维护触发"
  },
  {
    "id": 8,
    "prompt": "每 5 分钟帮我检查一次这个任务状态。",
    "expected": "走『循环任务』。优先 /loop；若用户给的是完成条件而不是固定间隔，再给 /goal 选项。",
    "scenario": "循环任务"
  }
]
'@ | Set-Content -Path 'test-prompts.json' -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$data = Get-Content 'test-prompts.json' -Raw | ConvertFrom-Json; if ($data.Count -lt 8) { Write-Host 'prompt corpus too small'; exit 1 }"
python312 -m json.tool test-prompts.json > /dev/null
```
Expected: PASS with exit code `0`

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add test-prompts.json
git commit -m "test: expand ai-coding-guide routing prompts"
```

---

### Task 6: Replace audit script with accuracy scanner

**Files:**
- Modify: `scripts/audit.ps1:1-110`

**Interfaces:**
- Consumes: evidence labels from Task 1, route categories from Task 3, prompt corpus from Task 5
- Produces: `P0`/`P1`/`P2` findings, JSON validity checks, and exit code semantics for future maintenance runs

- [ ] **Step 1: Write the failing test**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'scripts/audit.ps1' -Raw; if ($c -match 'Count-Skills' -or $c -match '~/.codex/' -or $c -notmatch 'P0' -or $c -notmatch 'P1' -or $c -notmatch 'P2') { Write-Host 'audit script stale'; exit 1 }"
```
Expected: FAIL with `audit script stale`

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'scripts/audit.ps1' -Raw; if ($c -match 'Count-Skills' -or $c -match '~/.codex/' -or $c -notmatch 'P0' -or $c -notmatch 'P1' -or $c -notmatch 'P2') { Write-Host 'audit script stale'; exit 1 }"
```
Expected: exit code `1`

- [ ] **Step 3: Write minimal implementation**

```powershell
@'
[CmdletBinding()]
param(
    [string]$Root = (Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = 'Stop'

$docFiles = @(
    (Join-Path $Root 'SKILL.md'),
    (Join-Path $Root 'references\ecosystems.md'),
    (Join-Path $Root 'references\MAINTENANCE.md')
)
$jsonFile = Join-Path $Root 'test-prompts.json'

$findings = [System.Collections.Generic.List[pscustomobject]]::new()

function Add-Finding {
    param(
        [string]$Severity,
        [string]$File,
        [int]$Line,
        [string]$Message
    )
    $findings.Add([pscustomobject]@{
        Severity = $Severity
        File     = $File
        Line     = $Line
        Message  = $Message
    })
}

function Scan-Pattern {
    param(
        [string]$Path,
        [string]$Severity,
        [string]$Pattern,
        [string]$Message
    )
    $hits = Select-String -Path $Path -Pattern $Pattern -AllMatches
    foreach ($hit in $hits) {
        Add-Finding -Severity $Severity -File (Resolve-Path $Path | Split-Path -Leaf) -Line $hit.LineNumber -Message $Message
    }
}

foreach ($file in $docFiles) {
    Scan-Pattern -Path $file -Severity 'P0' -Pattern '~/.codex/|~/.cursor/|~/.windsurf/|~/.config/opencode/' -Message 'Cross-IDE path residue in Claude Code guide.'
    Scan-Pattern -Path $file -Severity 'P1' -Pattern '唯一正确|一定更好|必须如此' -Message 'Overclaim wording; downgrade to evidence-labeled recommendation.'
    Scan-Pattern -Path $file -Severity 'P2' -Pattern '本机已装|当前会话可用|官方|作者|≈' -Message 'Manual evidence review point.'
}

$skill = Get-Content (Join-Path $Root 'SKILL.md') -Raw
if ($skill -notmatch 'Claude Code 当前环境') {
    Add-Finding -Severity 'P0' -File 'SKILL.md' -Line 1 -Message 'Main guide is missing Claude Code scope statement.'
}
foreach ($required in @('本地已证实', '官方可证实', '经验判断', '证据不足', 'references/ecosystems.md', 'references/MAINTENANCE.md')) {
    if ($skill -notmatch [regex]::Escape($required)) {
        Add-Finding -Severity 'P1' -File 'SKILL.md' -Line 1 -Message "Missing required string: $required"
    }
}

$maintenance = Get-Content (Join-Path $Root 'references\MAINTENANCE.md') -Raw
foreach ($required in @('何时必须更新', '证据源', '同步文件', '变更记录')) {
    if ($maintenance -notmatch [regex]::Escape($required)) {
        Add-Finding -Severity 'P1' -File 'references/MAINTENANCE.md' -Line 1 -Message "Missing maintenance heading: $required"
    }
}

try {
    $prompts = Get-Content $jsonFile -Raw | ConvertFrom-Json
} catch {
    Add-Finding -Severity 'P0' -File 'test-prompts.json' -Line 1 -Message 'Invalid JSON.'
    $prompts = @()
}

if ($prompts.Count -lt 8) {
    Add-Finding -Severity 'P1' -File 'test-prompts.json' -Line 1 -Message 'Regression corpus is too small; expected at least 8 prompts.'
}

$ids = @($prompts | ForEach-Object { $_.id })
if ($ids.Count -ne (@($ids | Select-Object -Unique)).Count) {
    Add-Finding -Severity 'P0' -File 'test-prompts.json' -Line 1 -Message 'Prompt IDs must be unique.'
}

$summary = [ordered]@{
    P0 = @($findings | Where-Object Severity -eq 'P0').Count
    P1 = @($findings | Where-Object Severity -eq 'P1').Count
    P2 = @($findings | Where-Object Severity -eq 'P2').Count
}

"=== ai-coding-guide accuracy audit ==="
foreach ($severity in 'P0', 'P1', 'P2') {
    "$severity: $($summary[$severity])"
    $group = $findings | Where-Object Severity -eq $severity
    foreach ($item in $group) {
        "  - $($item.File):$($item.Line) $($item.Message)"
    }
}

if ($summary.P0 -gt 0 -or $summary.P1 -gt 0) {
    exit 1
}
exit 0
'@ | Set-Content -Path 'scripts/audit.ps1' -Encoding utf8
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pwsh -NoProfile -Command "$c = Get-Content 'scripts/audit.ps1' -Raw; if ($c -match 'Count-Skills' -or $c -match '~/.codex/' -or $c -notmatch 'P0' -or $c -notmatch 'P1' -or $c -notmatch 'P2') { Write-Host 'audit script stale'; exit 1 }"
python312 -m json.tool test-prompts.json > /dev/null
pwsh -NoProfile -File scripts/audit.ps1
```
Expected:
- first command PASS
- JSON validation PASS
- audit script exits `0`
- output shows `P0: 0` and `P1: 0`
- `P2` may be non-zero because manual-review points are allowed

- [ ] **Step 5: Commit**

Run only after user approves commits:
```bash
git add scripts/audit.ps1 test-prompts.json SKILL.md references/ecosystems.md references/MAINTENANCE.md
git commit -m "chore: align ai-coding-guide with accuracy spec"
```

---

## Plan Self-Review

### Spec coverage

- **Claude Code current-environment scope** → Tasks 2, 3, 4
- **P0 dead refs / wrong default paths / wrong scope** → Tasks 2, 3, 4, 6
- **P1 wording tightening / evidence grading** → Tasks 1, 2, 4, 6
- **P2 slimming / file responsibility split** → Tasks 1, 2, 3, 4
- **Regression prompts** → Task 5
- **Audit script as suspicion finder** → Task 6
- **Validation after refactor** → Task 6 step 4

Gaps: none

### Placeholder scan

Checked the plan against the banned-shortcut list. No unfinished placeholder language remains in executable steps or code blocks.

### Type / interface consistency

- Evidence labels are consistent across Tasks 1, 2, and 6.
- Route category names are consistent across Tasks 3, 4, and 5.
- Audit severity labels are consistent across Task 6 steps and expected output.

### Verification sequence

Run in this order after implementation:
1. `pwsh -NoProfile -File scripts/audit.ps1`
2. `python312 -m json.tool test-prompts.json > /dev/null`
3. Manual spot-check of `SKILL.md` routes against `references/ecosystems.md`
