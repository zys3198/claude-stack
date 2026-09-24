---
name: instruction-engineering
description: 建立或审查项目的 AI 指令资产（CLAUDE.md / AGENTS.md / SKILL.md），只出草稿与 diff，不改项目文件。
disable-model-invocation: true
---
# Instruction Engineering — 项目指令资产

本 Skill 只有两种模式：建立项目 AI 上下文，或审查已有指令设计；两者都先定范围，只交草稿、报告或最小 diff，不直接修改项目文件。

## 第一部分：建立项目 AI 上下文

### 目标与输入

解决老项目中「引用存在但运行不明」导致的误判，至少核对四类上下文：业务与协作历史、需求/技术文档位置、真实运行链路（活代码与死代码）、架构与技术债务。新旧项目都适用；若同一需求在干净小项目也失败，先排除模型和任务描述问题。

### 产物

输出到 `docs/ai-context/`，由用户审阅后自行落地：`CLAUDE.md` 壳、`AGENTS.md` 源、`analysis-report.md` 报告，以及按需生成的 `modules/<module>-AGENTS.md`。

### 最短路线

1. **摸底**：读目录树、语言/框架、构建配置、README，以及已有 `CLAUDE.md`、`AGENTS.md`、`.claude/rules/`；四类上下文逐项记录证据，查不到标「未验证」。
2. **模块切分**：列核心模块与依赖关系。
3. **真实链路**：找入口、路由和构建产物，区分真实运行与仅有引用的代码。
4. **提炼**：整理业务背景、架构、规范和三方对接。
5. **强约束问答**：向负责人确认运行真相、债务和文档位置；找不到负责人也继续产出，但所有缺口标「未验证」。
6. **产出**：完成报告和适用的根/模块草稿；问答推翻模块或链路结论时回到对应步骤修正。

### 完成条件

四类上下文各有证据，或明确写出未验证及缺口；报告、根草稿和适用模块说明均列出；不覆盖已有文件，不把推断写成事实；只完成上下文产出，不做代码重构、项目落地或运行生效。

## 债务观察清单（分析报告 §5 用，只报告不改）

逐项报告证据：死代码（引用不等于运行）、为幻想未来增加的过度设计、半成品改造尾巴、近义命名/结构混淆、文档与真实运行脱节。

## 文件策略与维护规则

- `AGENTS.md` 是内容源，`CLAUDE.md` 只用 `@AGENTS.md` 导入并补 Claude Code 特有内容；不双写、不用 symlink。
- 根文件只留路径与 1–2 句摘要；真正非有不可的内容限于项目说明、非默认包管理器、非标准构建/类型检查命令。根入口预算 ≤120 行。
- 全局规则、项目事实、术语/领域模型、ADR、任务状态、Skill 流程、hook/CI/测试和 memory 分层归置；可复用结论就近落盘并更新根索引，索引过期主动修正。
- 完整重构路线（删死代码、做减法、定规范、自动化测试、债务常态化）见 [references/refactor-roadmap.md](references/refactor-roadmap.md)，超出本 Skill 边界；模板见 [references/templates/AGENTS-template.md](references/templates/AGENTS-template.md)、[references/templates/CLAUDE-shell-template.md](references/templates/CLAUDE-shell-template.md)、[references/templates/analysis-report-template.md](references/templates/analysis-report-template.md)。

## 第二部分：审查指令设计

### 范围与停止线

只读取用户明确纳入的自建 `SKILL.md`、`CLAUDE.md`、`AGENTS.md`；不读取或审查 `references/`、`scripts/`、插件 payload、外部 Skill 或其他文件，来源不明标「不确定」。只出审查报告和 diff，不执行 Edit、Write、移动、删除、提交或推送。

### 最短审查路线

1. **定靶**：列文件路径、归属、目的、允许范围；每个文件标记已审查、未读取、读取失败或不在范围。
2. **九项检查**：逐文件输出 `PASS / FAIL / 不确定`、位置、原文、影响和证据，检查触发边界、重复/冲突、资料读取、等待边界、完成标准、留存依据、常驻划分、逐句剪除和时效核对。
3. **证据分级**：`[源码]`、`[执行记录]`、`[官方原则]`、`[规则推测]`、`[未知]` 分开标；静态文字不能冒充运行行为。
4. **输出最小 diff**：每条 FAIL 写位置、最小摘录、场景、证据类型、影响、diff 和保留约束；全部通过时写「无须修改」。

九项检查的操作标准，以及六条冲突判据（两个负担、信息层级、正面陈述、锚定词、context pointer、归置相邻）见 [references/review-basis.md](references/review-basis.md)。判断常驻还是按需时，优先保留安全、权限、业务和验收门禁；只在当前分支会改变判断/执行/验收的资料才读取。

### 不得削弱的约束

不得删除或改成模型自行决定：生产生效、不可恢复删除、对外发送/发布、密钥/迁移/生产脚本、技术栈/数据结构/关键业务分支/权限判定确认；子代理启动前展示实际模型、provider、route、effort、并发和隔离并等待确认；代码或业务任务的真实运行、验收、失败修复、重新验证、独立复核、多来源核验、实验授权、用户确认、数据保留和审计记录。

### 审查完成条件

所有范围内文件都有结论；建议含原文、场景、最小 diff、证据类型和保留约束；不同证据等级不混写；未执行内容标 `unknown`、`not-run` 或「未验证」；末尾给一个最小下一步或明确「无需修改」。
