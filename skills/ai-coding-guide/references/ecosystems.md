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
- 审查反馈不能说"你说得对"→ 这是 CLAUDE.md 显式禁止的

### agent-skills（作者：Addy Osmani）

哲学：SDLC 全生命周期闭环，spec→ship 流水线

20+ 主题 skill 覆盖完整 SDLC：spec-driven-development / planning-and-task-breakdown / code-review-and-quality / test-driven-development / shipping-and-launch / code-simplification / performance-optimization 等。核心设计：

| 特征 | 举例 |
|------|------|
| skill 长名 | spec-driven-development、planning-and-task-breakdown、test-driven-development、code-review-and-quality、shipping-and-launch |
| 主题 skill | 每个主题有长名 skill（如 spec-driven-development 对应 spec 阶段）|
| 独有亮点 | interview-me、idea-refine、doubt-driven-development、source-driven-development、context-engineering |
| 闭环 | spec→plan→build→test→review→ship 一条龙 |

触发机制：调 skill（用 skill 长名）。⚠ Claude Code 侧装为顶层独立 skill（无 namespace，散落在 ~/.claude/skills/），无 slash 命令——用 skill 长名调用，勿用斜杠命令。

设计取舍：
- 闭环完整但与 SP 大量功能重叠（TDD/review/plan/spec 各 2-3 套实现）
- 若串行跑 spec-driven-development → planning-and-task-breakdown 全流程，**违反用户 CLAUDE.md §1.2/§1.3 的 commit-per-change + 人工确认线**——慎用，建议分步调用单 skill
- 风格偏叙述流程，与 SP 的指令式风格混用易输出漂移

定位：参考实现 + 独有亮点吸收。同领域执行优先 SP。

### mattpocock/skills（作者：Matt Pocock）

哲学：小而锐的单用途 skill，显式调用为主

28 个 skill 分 5 类（engineering / productivity / misc / in-progress / personal），用户级安装（`~/.claude/skills/`，无 namespace，可原地编辑）。核心设计：

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
- `grill-me/grill-with-docs` — 对抗式访谈压测计划
- `caveman` — 全文 caveman 模式压缩
- `design-an-interface` — 并行多 agent 出 N 套接口设计对比

设计取舍：
- 单用途小 skill → 组合灵活但需手动串
- 显式调用为主 → 不抢触发，低噪音，但新人记不住命令
- 个人/教育风格（Matt Pocock TS 背景）→ writing/teaching 类强，企业工程不如 SP
- 同领域重叠：tdd≈SP test-driven-development；review≈SP requesting-code-review。重叠时优先 SP（流程纪律）

定位：写作/教学/单用途工具的主力。工程流程当 SP 的补充。

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

### Claude Code 插件系统（plugin cache + enabledPlugins）

哲学：Claude Code 通过 `~/.claude/plugins/cache/<plugin-name>/<plugin-name>/<version>/` 加载插件，`~/.claude/settings.json` 的 `enabledPlugins` 字段控制启用

插件类型：
- **namespace 插件**：`<plugin>:` 前缀调用（superpowers / ecc / ponytail / caveman / understand-anything / karpathy-skills / claude-md-management / commit-commands / code-review / open-code-review / feature-dev / frontend-design / skill-creator / claude-code-setup / example-skills）
- **MCP 服务插件**：通过 MCP 协议暴露工具（context7 / playwright / chrome-devtools / github / lean-ctx / gitnexus / douyin / headroom）
- **顶层 skill**：直接装在 `~/.claude/skills/` 无 namespace（agent-skills / mattpocock / 大量用户自装中文 skill）

管理：编辑 `~/.claude/settings.json` 的 `enabledPlugins` 字段，或用 Claude Code 的 `/plugin` 交互命令。cache 目录即权限源——文件夹在 = 插件可被启用。

### ECC（最大生态，v2.0.0）

哲学：全栈框架 + 工作流编排，覆盖 14+ 语言/框架的 build/review/test + 安全 + 工作流 + agent 编排

271 skill + 92 command + 67 agent 全载于 `~/.claude/plugins/cache/ecc/ecc/2.0.0/`。核心覆盖：

| 类别 | 代表 skill / command |
|------|---------------------|
| 框架 build/review/test（14 语言） | `ecc:cpp-build` / `:cpp-review` / `:cpp-test` / `:rust-*` / `:go-*` / `:kotlin-*` / `:flutter-*` / `:react-build` / `:react-review` / `:react-test` / `:vue-review` / `:fastapi-review` / `:python-review` / `:django-review` 等 |
| 安全 | `ecc:security-scan` / `ecc:security-review`（skill）+ 框架专属 `django-security` / `springboot-security` / `laravel-security` / `quarkus-security` / `defi-amm-security` / `llm-trading-agent-security` |
| 前端 | `ecc:multi-frontend` / `frontend-patterns` / `frontend-a11y` / `frontend-design` / `liquid-glass-design` / `react-patterns` / `react-performance` / `vue-patterns` / `angular-developer` / `nextjs-turbopack` / `vite-patterns` / `nuxt4-patterns` |
| 后端框架 | `django-patterns` / `fastapi-patterns` / `springboot-*` / `quarkus-*` / `nestjs-patterns` / `laravel-*` / `dotnet-patterns` / `golang-patterns` / `python-patterns` / `mysql-patterns` / `postgres-patterns` / `redis-patterns` / `prisma-patterns` / `jpa-patterns` / `kubernetes-patterns` / `docker-patterns` |
| 移动端 | `swift-*`（swiftui / actor-persistence / concurrency-6-2 / protocol-di-testing）/ `kotlin-coroutines-flows` / `kotlin-exposed-patterns` / `kotlin-ktor-patterns` / `compose-multiplatform-patterns` / `flutter-dart-code-review` / `harmonyos-app-resolver` |
| 工作流编排 | `ecc:santa-loop`（adversarial 双审，两独立 reviewer 须都 approve）/ `ecc:gan-build` / `:gan-design`（generator-evaluator）/ `ecc:orch-build-mvp` / `:orch-add-feature` / `:orch-change-feature` / `:orch-fix-defect` / `:orch-refine-code` / `ecc:multi-plan` / `:multi-execute` / `:multi-frontend` / `:multi-backend` / `:multi-workflow` / `ecc:loop-start` / `:loop-status` |
| 代码质量 | `ecc:code-review` / `:refactor-clean` / `:prune` / `:test-coverage` / `:quality-gate` / `:production-audit` / `:safety-guard` |
| 计划/蓝图 | `ecc:plan` / `:blueprint` / `:plan-prd` / `:plan-orchestrate` / `:checkpoint` / `:aside` |
| agent 编排 | 67 个 framework 专属 agent（`ecc:python-reviewer` / `:react-reviewer` / `:rust-reviewer` / `:security-reviewer` / `:architect` / `:planner` / `:code-explorer` 等）|
| 成本/会话 | `ecc:cost-report` / `:sessions` / `:resume-session` / `:save-session` / `:project-init` / `:projects` / `:harness-audit` |

定位：当前环境**最大生态**。安全审查主力是 `ecc:security-scan` + santa-loop（对抗双审）；前端开发主力是 `ecc:react-*` + `multi-frontend`；多语言团队项目几乎全靠 ECC。codex-security（Codex 独有的 10 skill 全管线）和 build-web-apps（6 skill 全链路）在 Claude Code 不存在，功能由 ECC 子集覆盖。

### gitnexus（代码库知识图谱 + 控制流/数据流/taint）

哲学：代码库 → 可查询知识图谱 + 控制流图（CFG）/ 程序依赖图（PDG，含 CDG 控制依赖 + RD 数据依赖边）/ taint source→sink 追踪

`gitnexus` MCP 暴露 17 工具 + 9 顶层 skill（gitnexus-cli / -debugging / -exploring / -guide / -impact-analysis / -pdg-query / -pr-review / -refactoring / -taint-analysis）。

| 工具 | 作用 |
|------|------|
| `query` / `cypher` | 图查询（节点/边/路径）|
| `impact` / `api_impact` | 改动 blast radius（哪些调用方会受影响）|
| `trace` | 追踪函数调用链 |
| `route_map` | 端点 → 处理器路由图 |
| `pdg_query` | 控制依赖 / 数据依赖边查询（CDG / REACHING_DEF）|
| `explain` / `context` | 自然语言解释代码片段 / 上下文注入 |
| `check` / `detect_changes` / `shape_check` / `tool_map` | 健康检查 / 变更检测 / 形状校验 / 工具映射 |
| `rename` / `group_sync` / `group_list` / `list_repos` | 安全重命名 / 仓库组同步 |

> ℹ️ **MCP 工具无 `taint-analysis`**——source→sink 污染传播在 **skill 层**（顶层 `gitnexus-taint-analysis` skill），不在 `gitnexus` MCP。同款 skill 还有 `gitnexus-pr-review` / `gitnexus-refactoring` / `gitnexus-impact-analysis` / `gitnexus-pdg-query` / `gitnexus-debugging` / `gitnexus-exploring` / `gitnexus-cli` / `gitnexus-guide`。

定位：与 understand-anything 同属代码库理解层，但**实时查询**强于 understand-anything 的「先 build 全量 graph」。安全审查（taint skill）、重构（impact/rename）、PR review（gitnexus-pr-review skill）独有价值。Claude Code 当前最完整的代码图谱 + 程序分析能力。

### caveman（压缩模式，hook 驱动）

哲学：drop 冗余（冠词/虚词/客套），保留全部技术实质，省 ~75% token

`caveman:` 插件 7 skill（caveman / cavecrew / caveman-commit / caveman-compress / caveman-help / caveman-review / caveman-stats）+ SessionStart hook 自动激活。`caveman:cavecrew` 派子代理（builder / investigator / reviewer）输出 caveman 压缩格式。

定位：与 ponytail 配套的「沟通压缩」层。教程编写/学习材料默认不用 caveman（用户 memory 已声明——见 `~/.claude/projects/*/memory/tutorial-content-no-caveman.md`）。Level 切换：`/caveman lite|full|ultra|wenyan`。

### commit-commands（git 工作流插件）

哲学：git commit/push/PR 一键化，减少手动错误

3 skill：
| skill | 作用 |
|-------|------|
| `commit-commands:commit` | 智能 commit message（conventional commits）|
| `commit-commands:commit-push-pr` | 一键 commit + push + 开 PR |
| `commit-commands:clean_gone` | 清理本地已删远程分支的引用 |

定位：日常 git 工作流最快捷径。高风险操作（force-push / reset --hard）已由 hooks 拦（见 CLAUDE.md §5）。

### claude-md-management（CLAUDE.md 维护插件）

哲学：CLAUDE.md 是项目记忆，需审计 + session 学习回写

2 skill：
| skill | 作用 |
|-------|------|
| `claude-md-management:claude-md-improver` | 审计 CLAUDE.md 质量（冲突/冗余/含糊/不可执行规则），输出报告 + 改进 |
| `claude-md-management:revise-claude-md` | 把当前 session 的学习回写到 CLAUDE.md |

定位：CLAUDE.md 维护主力。配合顶层 `claude-md-audit` skill（独立审计）形成三件套。

### code-review / open-code-review（代码审查插件）

哲学：本地 diff / PR 多轴结构化审查

| skill | 作用 |
|-------|------|
| `code-review:code-review` | 本地 diff 多轴审查（effort low/medium/high，可 --fix 自动应用，--comment 发 PR 评论）|
| `open-code-review:review` / `:open-code-review` | 走阿里巴巴 `ocr` CLI，行级评论 + 可自动 apply fix |

定位：SP requesting-code-review（流程纪律）的补充——结构化深度审查。open-code-review 适合 PR 远程审查；code-review 适合本地 diff。

### feature-dev（特性开发插件）

哲学：架构蓝图 + 执行路径追踪 + reviewer，特性开发三件套

1 命令（`feature-dev`）+ 3 agent（code-architect / code-explorer / code-reviewer）：
| entry | 类型 | 作用 |
|-------|------|------|
| `feature-dev:code-architect` | agent | 分析现有 codebase 模式，输出实施蓝图（文件/接口/数据流/build order）|
| `feature-dev:code-explorer` | agent | 追执行路径，映射架构层，文档化依赖 |
| `feature-dev:code-reviewer` | agent | confidence-based 过滤的高优先 issue 审查 |
| `feature-dev:feature-dev` | command | 总入口 |

定位：与 SP brainstorming + writing-plans 重叠但角度不同——feature-dev 偏「分析现有 codebase 出蓝图」，SP 偏「设计先行 + 任务拆分」。新功能开发可二选一或互补。

### frontend-design（反 slop 前端设计）

哲学：反 AI 生成模板味，真实设计系统 + audit-first + 严格 pre-flight check

`frontend-design:frontend-design` + `example-skills:frontend-design`（同源）。涵盖落地页 / 作品集 / 重设计。

定位：建新前端应用的设计层主力。配合 ECC `react-*` / `multi-frontend` 实施层。build-web-apps:frontend-app-builder（Codex 独有）的 Claude Code 替代。

### skill-creator（skill 生成与优化）

哲学：从 git history 抽模式生成 SKILL.md，或对现有 skill 跑 9 维 rubric 自优化

| 入口 | 作用 |
|------|------|
| `skill-creator:skill-creator` / `example-skills:skill-creator` | 本地 git history 抽模式生成 SKILL.md（GitHub App 的本地版）|
| 顶层 `darwin-skill` | 9 维 rubric（结构 + 效果 + 元黑名单）+ hill-climbing + 独立 judge agent 盲评 + 测试 prompt 验证 |
| 顶层 `darwin-weekly-audit` | 周期体检，跑 darwin Phase 0.5（设计测试 prompt）+ Phase 1（基线分），只出报告不自动优化 |

定位：skill 元开发。darwin-skill 是 skill 生态的「自我进化」入口。

### claude-code-setup（hook / automation 推荐）

哲学：扫 transcript 找重复模式，推荐可自动化的 hook

`claude-code-setup:claude-automation-recommender` 单 skill。

定位：hook 配置主力。配合 `update-config` skill（顶层）+ 直接编辑 `~/.claude/settings.json`。

### example-skills（Anthropic 官方 17 示例 skill，umbrella：anthropic-agent-skills/example-skills/）

哲学：官方 skill 写法范例 + 即用工具 + Office 文档处理

17 skill：algorithmic-art / brand-guidelines / canvas-design / claude-api / doc-coauthoring / docx / frontend-design / internal-comms / mcp-builder / pdf / pptx / skill-creator / slack-gif-creator / theme-factory / web-artifacts-builder / webapp-testing / xlsx。

定位：学习 skill 写法的范例 + mcp-builder（构建 MCP server）/ web-artifacts-builder（生成 web artifact）有即用价值。

### last30days（跨平台趋势研究）

哲学：抓最近 30 天真实人声，非训练数据回忆

`last30days` 顶层 skill v3.7.0。覆盖 Reddit / X / YouTube / TikTok / Hacker News / Polymarket / GitHub / web。

定位：用户/市场调研。与 `agent-reach`（17 平台 CLI/MCP/curl 互动）互补——last30days 偏只读研究，agent-reach 偏互动。

### github（GitHub MCP，60+ 工具）

哲学：通过 `plugin:github:github` MCP 暴露完整 GitHub 操作

替代 Codex 时代的 github 插件 skill 集。MCP 工具覆盖：
- PR：`create_pull_request` / `update_pull_request` / `merge_pull_request` / `get_*` / `list_pull_requests`
- Issue：`create_issue` / `update_issue` / `list_issues` / `add_issue_comment`
- Branch / commit / tag / release：`create_branch` / `list_commits` / `get_commit` / `list_tags` / `create_release`
- Code search：`search_code` / `search_commits` / `search_issues` / `search_pull_requests` / `search_repositories` / `search_users`
- 协作：`assign_copilot_to_issue` / `request_copilot_review` / `create_pull_request_with_copilot`

定位：GitHub 集成主力。token 通过 Claude Code 的 MCP OAuth 流配置；不可用时降级 `gh` CLI。

### ponytail（作者：Dietrich Gebert）

哲学：lazy senior dev mode，强制最简方案

v4.8.3。hooks 驱动（`ponytail/hooks/claude-codex-hooks.json`），在工具执行前拦截，强制 YAGNI / stdlib first / 不加未请求的抽象。

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

### 开发一个功能（Superpowers 主力）

| 阶段 | Superpowers | 补充生态 |
|------|------------|---------|
| 设计 | brainstorming（自动触发）。问需求→出设计文档→签审。HARD-GATE：没设计就不能写代码 | agent-skills idea-refine（发散收敛）、mattpocock design-an-interface（多方案对比）、`feature-dev:code-architect`（分析现有 codebase 出蓝图）|
| 计划 | writing-plans（自动触发）。假设执行者是"没上下文+品味差的新人"，每步 2-5 分钟。每个任务包含完整文件路径和代码 | agent-skills planning-and-task-breakdown（轻量拆任务）、mattpocock to-prd（出 PRD）、`ecc:plan` / `:blueprint`（ECC 工作流版）|
| 实现 | subagent-driven-development（自动触发）。每个任务：派 agent → spec 审查 → 代码质量审查 → 通过才提交。或 executing-plans（人工场景）| ponytail（最简实现）、agent-skills planning-and-task-breakdown（分步，见 §人工确认线）、`ecc:multi-execute` / `:orch-build-mvp`（并行/编排）|
| 审查 | requesting-code-review → 派审查 subagent。receiving-code-review → 质疑式消化反馈（禁止说"你说得对"）| `code-review:code-review`（多轴）/ `open-code-review:review`（行级 `ocr` CLI）/ `ecc:security-scan`（安全）/ `ecc:santa-loop`（高风险对抗双审）/ `gitnexus:impact` + `:taint-analysis`（图谱安全审查）|
| 验证 | verification-before-completion（铁律：证据驱动）。必须有当轮运行的命令输出，不能依赖"应该可以"| `ecc:<lang>-test`（react/vue/flutter/rust/go 等，框架专属）/ `ecc:test-coverage` |
| 收尾 | finishing-a-development-branch → 显示 4 个选项（合并/PR/保留/丢弃）| `commit-commands:commit-push-pr`（一键三连，最快）|

### 诊断问题

| 场景 | 工具 | 说明 |
|------|------|------|
| 系统化找根因 | SP systematic-debugging + `gitnexus:trace` / `:explain`（图谱辅助定位）| 4 阶段：调查→复现→检查变更→多组件边界加诊断 |
| 构建/类型错误 | 项目构建纪律（CLAUDE.md §1.4）+ `ecc:<lang>-build`（cpp/rust/go/kotlin/flutter/gradle 等框架专属）| tsc --noEmit / go build 等本地编译先行 |
| 性能分析 | mattpocock zoom-out（模块地图）/ `ecc:react-performance` / `performance-optimization` skill | 无单一专门 skill，组合使用 |

### 自动化/循环

| 场景 | 方式 |
|------|------|
| 定时轮询 | `/loop 5m <prompt>` skill（Claude Code 内置）|
| 自定步持续 | `/loop <prompt>`（omit interval 让模型自配速）|
| 受管循环 | 无独立生态——`/loop` + 手动 max-runs/max-duration 硬限制 |

### 学习积累

Claude Code 侧可手写 memory（CLAUDE.md §7 防错闭环，路径 `~/.claude/projects/*/memory/`）；代码库学习走 understand-anything / gitnexus / mattpocock teach。

---

## 配合模式与重叠区处理

各入口已编码在主文件 Step 2 决策路径中，每分类含推荐选项和 fallback。不一致时以主文件 Step 2 为准。

**已有明确需求/PRD →** 决策流走"有需求文档"分类，引导至 SP writing-plans，不走 brainstorming。HARD-GATE 由"用户已确认"替代设计文档。

**多生态分工原则：** SP（流程纪律）/ ECC（框架 + 安全 + 工作流编排）/ gitnexus + understand-anything（代码库理解）/ context7（文档查询）/ lean-ctx + headroom（上下文压缩）/ caveman + ponytail（沟通/代码风格 hook）。agent-skills 和 mattpocock 的通用流程类与 SP 重复，只留独有亮点。

### 重叠区处理（多生态共存，每个域 2-4 套实现）

| 重叠区 | 各生态实现 | 推荐主力（冗余策略） |
|--------|-----------|---------------------|
| TDD | SP test-driven-development（纪律）／ agent-skills test-driven-development ／ mattpocock tdd ／ `ecc:tdd-workflow` | **SP（纪律）**。agent-skills/mattpocock/ECC 与 SP 重复，按项目偏好二选一 |
| 审查 | SP requesting/receiving-code-review（自检）／ agent-skills code-review-and-quality ／ mattpocock review ／ `code-review:code-review`（多轴）／ `open-code-review:review`（`ocr` CLI）／ `ecc:code-review` ／ `ecc:santa-loop`（对抗双审）| **SP（日常自检）→ `code-review:code-review`（结构）→ `ecc:security-scan`（安全）→ `ecc:santa-loop`（高风险对抗）** |
| 调试 | SP systematic-debugging（4 阶段根因）／ agent-skills debugging-and-error-recovery ／ `gitnexus:trace` / `:explain`（图谱辅助）| **SP（最系统化）+ gitnexus（图谱定位）**。debugging-and-error-recovery 为子集 |
| 计划 | SP brainstorming + writing-plans（设计先行 HARD-GATE）／ agent-skills planning-and-task-breakdown + spec-driven-development ／ mattpocock to-prd + design-an-interface + prototype ／ `feature-dev:code-architect` ／ `ecc:plan` / `:blueprint` | **SP（设计先行）+ mattpocock design-an-interface（多方案对比，独有）+ feature-dev:code-architect（分析现有 codebase）** |
| 验证 | SP verification-before-completion（证据铁律）／ agent-skills shipping-and-launch ／ `ecc:<lang>-test`（react/vue/flutter/rust/go 等）／ `ecc:test-coverage` | **SP（每步）+ ECC 框架专属 test（合并前）** |
| 安全 | `ecc:security-scan` + `:security-review`（主力）／ `ecc:santa-loop`（对抗双审）／ `gitnexus-taint-analysis` skill（source→sink 污染流）／ agent-skills security-and-hardening（通用加固）／ 顶层 `security-and-hardening` skill | **ECC security-scan（主力）+ santa-loop（高风险）+ gitnexus-taint-analysis skill（污染流）**。codex-security 10-skill 全管线在 Claude Code 不存在 |
| 代码库理解 | gitnexus（MCP 实时图查询 + PDG/taint）／ understand-anything（8 skill 知识图谱 + tour）／ mattpocock zoom-out + improve-codebase-architecture | **gitnexus（实时查询/重构/taint）+ understand-anything（新项目深度 onboarding/tour）**。mattpocock 偏轻量摘要 |
| 前端开发 | ECC `react-*` / `vue-*` / `multi-frontend` / `frontend-design` / `frontend-patterns` / `frontend-a11y` ／ `frontend-design:frontend-design`（反 slop）／ `example-skills:web-artifacts-builder` ／ agent-skills frontend-ui-engineering | **ECC 前端全家桶（建新 + 优化）+ frontend-design:frontend-design（设计层反 slop）**。build-web-apps 6-skill 全链路在 Claude Code 不存在 |
| 上下文压缩 | lean-ctx + headroom（MCP 三层栈，已配）／ caveman + handoff（沟通压缩层）| **lean-ctx + headroom（MCP 层，自动）+ caveman（沟通压缩，hook）**。层级不同不冲突 |
| OpenAI 应用开发 | ECC `agent-payment-x402`（仅此一项）／ `claude-api` skill（Anthropic 侧参考）| **Claude Code 侧无 OpenAI 全套**——openai-developers 5-skill 在 Claude Code 不存在。需 OpenAI SDK 工作时手写或参考 claude-api skill 跨生态类比 |

**冗余处理原则：** 核心开发流程（TDD/审查/调试/计划/验证）每域有 2-4 套实现。不全部触发——按"SP 管流程纪律 + ECC 管框架/安全/工作流 + gitnexus/understand-anything 管代码库理解 + context7 管文档查询 + lean-ctx/headroom 管上下文"分工。agent-skills 和 mattpocock 的通用流程类与 SP 重复，只留独有亮点（agent-skills 留 interview-me / idea-refine / doubt-driven-development / source-driven-development；mattpocock 留 teach / zoom-out / writing-* / grill-* / design-an-interface）。

---

## MCP 依赖与降级

下列生态依赖 MCP 服务或外部运行时，不可用时需降级：

| 生态 | 依赖 | 不可用时降级 |
|------|------|-------------|
| headroom | headroom MCP 服务运行 | 退到 lean-ctx 本地压缩（无 hash 取回，纯压）；或 `ctx_compose` |
| understand-anything | 首次 build graph 需 AST 解析 | 大仓库超时 → 缩范围（子目录）或退到 gitnexus（实时子图查询）/ mattpocock zoom-out 轻量摘要 |
| gitnexus | gitnexus MCP + 已 build 的代码图谱 | 退到 understand-anything（重新 build）/ mattpocock zoom-out（无图）|
| context7 | context7 MCP 服务（Claude Code 已配双实例 `a1b2c3d4-context7-mcp-001` + `plugin:context7:context7`，Upstash 跨平台 MCP） | 退到直接查官方文档 / WebSearch |
| playwright | playwright MCP + 浏览器（双实例 `b2c3d4e5-playwright-mcp-002` + `plugin:playwright:playwright`）| 退到手动测试 / curl 验证 API |
| chrome-devtools | `plugin:ecc:chrome-devtools` MCP + Chromium | 退到 playwright MCP / 手动测试 |
| github | `plugin:github:github` MCP + token（MCP OAuth 流配置）| 退到 `gh` CLI |
| lean-ctx | `lean-ctx` MCP 服务运行 | 退到原生 Read/Grep/Shell/Glob（无压缩，token 消耗增加）|
| douyin | `douyin` MCP | 无降级（视频提取专用，缺失则跳过该场景）|
| ECC 框架 build/review/test | 无外部依赖（命令/skill 内部）| 命令本身不可用 → 退到 SP 同名 skill + 项目构建命令 |
| agent-skills 全流程串行 | 无外部依赖，但语义上绕过人工确认线 | 用户 CLAUDE.md §1.2/§1.3 已声明 commit 前展示 diff —— 分步调单 skill，或走 SP writing-plans → executing-plans |

## 推荐性质声明

本指南所有生态对比、决策速查、选型速判的推荐均为**基于生态设计哲学的推理**（如"SP 管流程纪律"、"ECC 管框架/安全"），非 benchmark 实测数据。重叠区优先级（如"审查 SP 日常自检 + `code-review:code-review` 结构 + ECC 安全 + santa-loop 对抗"）是经验判断，未做 with-skill vs baseline 对照实验。重要决策建议结合具体项目实测。

平台差异声明：本指南针对 **Claude Code** 环境（`~/.claude/`、CLAUDE.md、settings.json、`/plugin` 系统）。Codex 副本（`~/.codex/`、AGENTS.md、config.toml、`codex plugin` 命令、codex-security/build-web-apps/openai-developers 三个 marketplace 插件）是独立维护的另一份指南，路径与可用生态不同，不混淆。
