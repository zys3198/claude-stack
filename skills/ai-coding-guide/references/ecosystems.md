# 生态详情参考

本文件是 `ai-coding-guide` 主文件的渐进式披露详情。主文件触发时只加载速查表；用户选"看详情 / B 选项"或分类为"了解指南"时，Read 本文件展开。

主文件路径：`SKILL.md`（同目录）

---

## 认识各生态

### Superpowers（作者：Jesse Vincent / obra）

哲学：完整开发方法论，流水线驱动

≈14 个技能构成一条从 idea 到合并的完整 pipeline。技能自动触发（检测到上下文就激活）。核心设计：

| 铁律 | 来源 | 内容 |
|------|------|------|
| 设计先行 | brainstorming HARD-GATE | 未经设计讨论，不得写任何代码 |
| TDD | test-driven-development | 没有先看到测试失败，就不能写实现代码 |
| 证据驱动 | verification-before-completion | 没有当轮运行的验证输出，就不能声称完成 |

触发机制：你说话 → using-superpowers 评估是否有 1% 匹配 → 自动加载匹配 skill → 按 checklist 执行。不需要你记命令。

设计取舍：
- 强制流程（HARD-GATE）→ 可靠但有时啰嗦
- 假设执行者是"热情但品味差的初级工程师"→ 极度详细的任务拆分
- "NO 生产代码 WITHOUT 失败测试"→ 删掉没测试就写的代码
- 审查反馈不能说"你说得对"→ 这是 AGENTS.md 显式禁止的

### agent-skills（作者：Addy Osmani）

哲学：SDLC 全生命周期闭环，spec→ship 流水线

20+ 主题 skill 覆盖完整 SDLC：spec-driven-development / planning-and-task-breakdown / code-review-and-quality / test-driven-development / shipping-and-launch / code-simplification / performance-optimization 等。核心设计：

| 特征 | 举例 |
|------|------|
| skill 长名 | spec-driven-development、planning-and-task-breakdown、test-driven-development、code-review-and-quality、shipping-and-launch |
| 主题 skill | 每个主题有长名 skill（如 spec-driven-development 对应 spec 阶段）|
| 独有亮点 | interview-me、idea-refine、doubt-driven-development、source-driven-development、context-engineering |
| 闭环 | spec→plan→build→test→review→ship 一条龙 |

触发机制：调 skill（用 skill 长名）。⚠ Codex 侧经 skill-installer 装为独立 skill（无 namespace，散落在 ~/.codex/skills/），slash 命令（/build /spec 等）未安装——用 skill 长名调用，勿用斜杠命令。

设计取舍：
- 闭环完整但与 SP 大量功能重叠（TDD/review/plan/spec 各 2-3 套实现）
- 若串行跑 spec-driven-development → planning-and-task-breakdown 全流程，**违反用户 AGENTS.md §1.2/§1.3 的 commit-per-change + 人工确认线**——慎用，建议分步调用单 skill
- 风格偏叙述流程，与 SP 的指令式风格混用易输出漂移

定位：参考实现 + 独有亮点吸收。同领域执行优先 SP。

### mattpocock/skills（作者：Matt Pocock）

哲学：小而锐的单用途 skill，显式调用为主

28 个 skill 分 5 类（engineering / productivity / misc / in-progress / personal），用户级安装（`~/.codex/skills/ 或 ~/.agents/skills/，无 namespace，可原地编辑）。核心设计：

| 类别 | 代表 skill |
|------|-----------|
| 工程 | tdd、improve-codebase-architecture、zoom-out、prototype、design-an-interface、to-prd、to-issues、triage、request-refactor-plan |
| 写作 | edit-article、writing-beats、writing-fragments、writing-shape |
| 元/教学 | teach、write-a-skill、handoff、grill-me、grill-with-docs |
| 工具链 | git-guardrails-claude-code、setup-pre-commit、migrate-to-shoehorn、scaffold-exercises、obsidian-vault |
| 压缩 | caveman（token 减 75%） |

触发机制：多数 `disable-model-invocation: true`——**不自动触发，显式 `/skill-name` 才跑**。少数（tdd、review）按 description 匹配自动触发。

独有亮点（SP/agent-skills 无对应）：
- `teach` — 结构化教学工作区（MISSION.md + lessons/ + learning-records/ + reference/），zone of proximal development，多 session 状态化
- `zoom-out` — 上调抽象层给模块地图（vs understand-anything 全量扫，更轻）
- `writing-beats/fragments/shape` — narrative 文章塑形三件套
- `grill-me/grill-with-docs` — 轻量需求澄清与对抗式访谈；重点不是产长文档，而是逐问逐答、让用户快速拍板
- `caveman` — 全文 caveman 模式压缩
- `design-an-interface` — 并行多 agent 出 N 套接口设计对比

设计取舍：
- 单用途小 skill → 组合灵活但需手动串
- 显式调用为主 → 不抢触发，低噪音，但新人记不住命令
- 个人/教育风格（Matt Pocock TS 背景）→ writing/teaching 类强，企业工程不如 SP
- 同领域重叠：tdd≈SP test-driven-development；review≈SP requesting-code-review。重叠时优先 SP（流程纪律）

定位：写作/教学/单用途工具的主力。`grill-me` 负责轻量澄清，工程重流程仍由 SP 兜底。

### Trellis（外部 CLI，Mindfold）

哲学：把执行期约束从聊天上下文里抽出来，放进结构化任务树

它不是 skill 生态，而是外部 CLI。本指南建议主要用于**长会话执行期**：给任务、验收标准、层级关系一个持久真相源，减少模型随着对话变长而跑偏。前期需求澄清走 `grill-me`，不靠 Trellis。

| 特征 | 价值 |
|------|------|
| 任务树 | 把大任务拆成可持续引用的节点，而不是散在聊天记录里 |
| 验收标准 | 每个任务可带明确 done 条件，减少“差不多完成”的漂移 |
| 长任务治理 | 适合 30-60 分钟以上、跨多阶段执行 |

设计取舍：
- 比单纯聊天更稳，但前置成本更高
- 适合“计划已定、进入执行期”的任务，不适合替代轻量需求澄清
- 本指南不默认假设已安装；只有用户明确提到，或确实遇到长会话跑偏问题时才推荐

定位：执行期结构化治理层。前期澄清优先 `grill-me`，重流程设计优先 SP，长任务执行期再考虑 Trellis。

### understand-anything（作者：Egonex-AI，原创建者 Lum1104）

哲学：代码库 → 可查询知识图谱

8 个 skill（understand / understand-chat / dashboard / diff / domain / explain / knowledge / onboard）+ 子 agent（architecture-analyzer / file-analyzer / domain-analyzer / tour-builder / graph-reviewer 等）。核心：全仓库 AST + 语义分析产出 `graph.json`（文件节点 + 调用/依赖边），可可视化、查询、生成学习 tour。

| 特征 | 价值 |
|------|------|
| 知识图谱 | 跨文件依赖/调用关系结构化，区别于摘要式 onboarding |
| tour-builder | 自动生成 5-15 步代码库学习路径 |
| diff 模式 | 改动影响图谱节点，blast radius 可视化 |
| dashboard | 浏览器看 graph |

触发：`/understand` 显式启动 build；后续 `/understand-chat` 基于已建 graph 问答。

定位：新项目上手 / 大型重构影响分析 / 团队 onboarding。与 mattpocock `zoom-out` 互补——zoom-out 偏摘要速览，understand-anything 偏深度结构化。首次 build graph 大仓库耗时，值得。

### headroom（作者：headroomlabs-ai）

哲学：上下文压缩 MCP 服务

MCP 工具：`headroom_compress`（长内容 → 压缩文本 + hash）/ `headroom_retrieve`（按 hash 取回原文）/ `headroom_stats`（压缩统计）。配合你 AGENTS.md §11 三层栈：`lean-ctx hook → Headroom MCP → lean-ctx MCP → LLM`。

| 特征 | 价值 |
|------|------|
| 有损压缩 + hash 取回 | 压中间结果省 token，需要细节再 retrieve |
| 统计 | 看本会话压缩次数 / 省 token / 成本 |

定位：长会话/大仓库上下文管理。与 lean-ctx（本地代码压缩）分层互补——lean-ctx 压代码/命令输出，headroom 压任意长文本。MCP 服务需运行。

### Codex marketplace 插件（openai-curated 等三源）

哲学：Codex 官方插件市场托管的 skill 集 + MCP 服务，通过 codex plugin 命令管理

三个 marketplace 源：
- openai-primary-runtime：documents / spreadsheets / presentations（Office 文档处理）
- openai-bundled：browser / computer-use（浏览器和桌面自动化）
- openai-curated：最大的源，含 codex-security / build-web-apps / openai-developers / github / figma / notion / playwright / supabase / stripe 等 40+ 插件

管理命令：codex plugin list（查可用）/ codex plugin add <name>@<marketplace>（装）/ codex plugin marketplace add <owner>/<repo>（加第三方源）

### codex-security（openai-curated 插件）

哲学：安全扫描全管线，从发现到验证到修复的闭环

10 个 skill 构成完整安全审查链路：

| skill | 作用 |
|-------|------|
| security-scan | repository 全量或 scoped-path 扫描 |
| deep-security-scan | 多 pass 独立发现 + 语义合并 + 验证（最彻底）|
| security-diff-scan | PR / commit / branch diff 的安全审查 |
| threat-model | 创建/更新/持久化仓库威胁模型 |
| finding-discovery | 发现候选安全发现 |
| validation | 判定候选发现是否有效 |
| attack-path-analysis | 从 source 到 sink 追踪 + 校准 severity |
| fix-finding | 修复并验证已确认的安全发现 |
| track-findings | 把已验证发现登记到 Linear/Jira/GitHub issue/安全公告 |
| triage-finding | 导入外部扫描器/报告，做仓库影响 triage |

定位：当前环境**最完整的安全审查链路**。codex-security 是全管线（发现→验证→修复→追踪）；agent-skills security-and-hardening 补通用加固。日常用 codex-security:security-diff-scan（PR 审查）。

### build-web-apps（openai-curated 插件）

哲学：前端开发全链路，从设计概念到可运行代码

6 个 skill：

| skill | 作用 |
|-------|------|
| frontend-app-builder | 从 image-generated 概念设计到实现，section-specific references |
| react-best-practices | React/Next.js 性能优化指南（Vercel Engineering）|
| shadcn | shadcn/ui 组件管理——加/搜/修/组合 |
| stripe-best-practices | Stripe 集成——Checkout/PaymentIntents/Connect/billing |
| supabase-postgres-best-practices | Postgres 查询/schema/配置优化 |
| frontend-testing-debugging | 前端 dev server / UI 回归 / 交互 bug / 响应式布局 QA |

定位：前端开发主力。build-web-apps 偏工程实践（best practices + 测试 + 修复），react-best-practices / shadcn / stripe / supabase 全链路。建新应用用 frontend-app-builder，优化现有用 react-best-practices / frontend-testing-debugging。

### openai-developers（openai-curated 插件）

哲学：OpenAI 官方应用开发 skill 集，覆盖 API key 管理到部署

5 个 skill：

| skill | 作用 |
|-------|------|
| agents-sdk | 构建/运行/部署/评估 Agents SDK 应用 |
| build-chatgpt-app | 构建/重构 ChatGPT Apps SDK（MCP server + widget UI）|
| chatgpt-app-submission | 生成 submission.json + 审查清单 |
| openai-api-troubleshooting | 分类 API 请求失败原因 + 路由修复 |
| platform-api-key | API key 安全管理（inspect/ask reuse-vs-new/never expose）|

定位：OpenAI 应用开发唯一选择，无其他生态重叠。platform-api-key 是所有 OpenAI API 工作的**前置门**（先确认 key 可用再继续）。

### github（openai-curated 插件）

哲学：GitHub PR / issue / CI 工作流 skill 集，配 GitHub MCP

4 个 skill：

| skill | 作用 |
|-------|------|
| github | 仓库 / PR / issue 总览与 triage 入口 |
| gh-address-comments | 审查 PR 未解决 review 线程，实现选定的修复 |
| gh-fix-ci | 调试修复 GitHub Actions 失败的 PR check |
| yeet | 本地改动 → commit → push → 开 draft PR 的工作流 |

定位：GitHub 集成主力。配 github MCP（token 需配，降级走 `gh` CLI）。CI 修复走 gh-fix-ci，发 PR 走 yeet（轻量）或 SP finishing-a-development-branch（要选合并/PR/保留/丢弃）。

### ponytail（作者：Dietrich Gebert）

哲学：lazy senior dev mode，强制最简方案

v4.7.0。hooks 驱动（`ponytail/hooks/claude-codex-hooks.json`），在工具执行前拦截，强制 YAGNI / stdlib first / 不加未请求的抽象。

| 铁律 | 内容 |
|------|------|
| YAGNI | 不加未请求的功能/抽象 |
| stdlib first | 优先标准库，不引外部依赖 |
| 最短路径 | 能 3 行解决不写 30 行 |

定位：快速改动 / 原型 / bug 修复的主力。与 SP 设计先行有冲突——SP 要完整流程（brainstorming→plan→TDD），ponytail 要最简实现。**裁决**：用户要"快速改/简单修"走 ponytail；要"新功能/完整开发"走 SP。

### claude-api（anthropic-agent-skills）

哲学：Claude API/SDK 文档 skill

构建 LLM 应用时参考 Claude API 文档。与 openai-developers 互补——openai-developers 管 OpenAI 生态，claude-api 管 Anthropic 生态。

定位：使用 Claude API 时的文档参考。无 slash，skill 按需加载。

---

## 多生态流程对比

### 开发一个功能（先分清澄清层 / 设计层 / 执行层）

| 阶段 | 主力 | 补充生态 |
|------|------|---------|
| 轻量澄清 | `grill-me`。逐问逐答，帮用户快速拍板；适合需求模糊、但不想先读长 brainstorm 文档 | agent-skills interview-me / idea-refine |
| 设计 | brainstorming（自动触发）。问需求→出设计文档→签审。HARD-GATE：没设计就不能写代码 | mattpocock design-an-interface（多方案对比） |
| 计划 | writing-plans（自动触发）。假设执行者是"没上下文+品味差的新人"，每步 2-5 分钟。每个任务包含完整文件路径和代码 | agent-skills planning-and-task-breakdown（轻量拆任务）、mattpocock to-prd（出 PRD） |
| 执行治理 | Trellis（若已安装）。长会话/多阶段任务用任务树持续约束；不是默认前置层 | TaskCreate / TaskUpdate（内置轻量替代） |
| 实现 | subagent-driven-development（自动触发）。每个任务：派 agent → spec 审查 → 代码质量审查 → 通过才提交。或 executing-plans（人工场景） | ponytail（最简实现）、agent-skills planning-and-task-breakdown（分步，见 §人工确认线） |
| 审查 | requesting-code-review → 派审查 subagent。receiving-code-review → 质疑式消化反馈（禁止说"你说得对"） | codex-security:security-diff-scan（安全）→ deep-security-scan（高风险多 pass） |
| 验证 | verification-before-completion（铁律：证据驱动）。必须有当轮运行的命令输出，不能依赖"应该可以" | build-web-apps:frontend-testing-debugging（前端合并前） |
| 收尾 | finishing-a-development-branch → 显示 4 个选项（合并/PR/保留/丢弃） | 无 |

### 诊断问题

| 场景 | 工具 | 说明 |
|------|------|------|
| 系统化找根因 | SP systematic-debugging | 4 阶段：调查→复现→检查变更→多组件边界加诊断 |
| 构建/类型错误 | 项目构建纪律（AGENTS.md §1.4）+ build-web-apps:frontend-testing-debugging（前端）| tsc --noEmit / go build 等本地编译先行 |
| 性能分析 | mattpocock zoom-out（模块地图）/ build-web-apps:react-best-practices | 无单一专门 skill，组合使用 |

### 自动化/循环

| 场景 | 方式 |
|------|------|
| 定时轮询 | 内置 /loop 5m <prompt> |
| 条件驱动持续运行 | 内置 /goal <condition>（小模型每轮评估，达标自动停）|

### 学习积累

无专门生态。Codex 侧可手写 memory（AGENTS.md §8 防错闭环）；代码库学习走 understand-anything / mattpocock teach。

---

## 配合模式与重叠区处理

各入口已编码在主文件 Step 2 决策路径中，每分类含推荐选项和 fallback。不一致时以主文件 Step 2 为准。

**已有明确需求/PRD →** 决策流走"有需求文档"分类，引导至 SP writing-plans，不走 brainstorming。HARD-GATE 由"用户已确认"替代设计文档。

**多生态分工原则：** `grill-me`（轻量澄清）/ SP（流程纪律）/ Trellis（长任务执行治理）/ codex-security（安全）/ build-web-apps（前端）/ understand-anything + CodeGraph（代码库理解）。agent-skills 和 mattpocock 的通用流程类与 SP 重复，只留独有亮点。

### 重叠区处理（多生态共存，每个域 2-4 套实现）

| 重叠区 | 各生态实现 | 推荐主力（冗余策略） |
|--------|-----------|---------------------|
| TDD | SP test-driven-development（纪律）／ agent-skills test-driven-development ／ mattpocock tdd | **SP（纪律）**。agent-skills/mattpocock 与 SP 重复，按项目偏好二选一 |
| 审查 | SP requesting/receiving-code-review（自检）／ agent-skills code-review-and-quality ／ mattpocock review ／ codex-security security-diff-scan（安全）| **SP（日常自检）→ codex-security（安全）→ codex-security deep-security-scan（高风险多 pass）** |
| 调试 | SP systematic-debugging（4 阶段根因）／ agent-skills debugging-and-error-recovery | **SP（最系统化）**。debugging-and-error-recovery 为子集 |
| 计划 | SP brainstorming + writing-plans（设计先行 HARD-GATE）／ agent-skills planning-and-task-breakdown + spec-driven-development ／ mattpocock to-prd + design-an-interface + prototype | **需求模糊先 `grill-me`；需求清楚走 SP writing-plans；想轻量拆任务用 planning-and-task-breakdown** |
| 执行治理 | Trellis（执行期任务树治理，外部 CLI，不默认假设已装） ／ TaskCreate + TaskUpdate（内置） | **计划已定 + 长会话/多阶段才上 Trellis；未装回落 TaskCreate** |
| 验证 | SP verification-before-completion（证据铁律）／ agent-skills shipping-and-launch ／ build-web-apps:frontend-testing-debugging（前端）| **SP（每步）+ build-web-apps（前端合并前）** |
| 执行放权 | dangerously-skip-permissions（风险开关，不属某一生态） | **默认不用**。仅在需求非常清楚、计划扎实、用户显式接受风险时讨论 |
| 安全 | codex-security（10 skill 全管线）／ agent-skills security-and-hardening | **codex-security（主力，管线最完整）+ agent-skills security-and-hardening（通用加固）** |
| 代码库理解 | understand-anything（8 skill 知识图谱）／ CodeGraph MCP ／ mattpocock zoom-out + improve-codebase-architecture | **CodeGraph（日常结构查询）+ understand-anything（新项目深度 onboarding）**。mattpocock 偏轻量摘要 |
| 前端开发 | build-web-apps（6 skill 工程实践）／ agent-skills frontend-ui-engineering | **build-web-apps（建新应用 + 优化现有）** |
| 上下文压缩 | lean-ctx + headroom（MCP 三层栈，已配）／ mattpocock caveman + handoff | **lean-ctx + headroom（MCP 层，自动）**。mattpocock 是 skill 指令层建议，层级不同不冲突 |

**冗余处理原则：** 核心开发流程（TDD/审查/调试/计划/验证）每域有 2-4 套实现。不全部触发——按"`grill-me` 管轻量澄清 + SP 管流程纪律 + Trellis 管长任务执行治理 + codex-security 管安全 + build-web-apps 管前端 + understand-anything/CodeGraph 管代码库理解"分工。agent-skills 和 mattpocock 的通用流程类与 SP 重复，只留独有亮点（agent-skills 留 interview-me / idea-refine / doubt-driven-development；mattpocock 留 teach / zoom-out / writing-* / grill-* / design-an-interface）。

---

## MCP 依赖与降级

下列生态依赖 MCP 服务或外部运行时，不可用时需降级：

| 生态 | 依赖 | 不可用时降级 |
|------|------|-------------|
| headroom | headroom MCP 服务运行 | 退到 lean-ctx 本地压缩（无 hash 取回，纯压）；或 ctx_compress |
| understand-anything | 首次 build graph 需 AST 解析 | 大仓库超时 → 缩范围（子目录）或退到 mattpocock zoom-out 轻量摘要 |
| context7 | context7 MCP 服务（config.toml 已配 `a1b2c3d4-context7-mcp-001`，Upstash 跨平台 MCP） | 退到直接查官方文档 / 搜索引擎 |

| playwright | playwright MCP + 浏览器 | 退到手动测试 / curl 验证 API |
| github | github MCP + token | 退到 `gh` CLI |
| agent-skills 全流程串行 | 无外部依赖，但语义上绕过人工确认线 | 用户 AGENTS.md §1.2/§1.3 已声明 commit 前展示 diff —— 分步调单 skill，或走 SP writing-plans → executing-plans |

## 推荐性质声明

本指南所有生态对比、决策速查、选型速判的推荐均为**基于生态设计哲学的推理**（如"SP 管流程纪律"），非 benchmark 实测数据。重叠区优先级（如"审查 SP 日常自检 + codex-security 深度"）是经验判断，未做 with-skill vs baseline 对照实验。重要决策建议结合具体项目实测。
