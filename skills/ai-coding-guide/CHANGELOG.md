# Changelog

本文件记录 ai-coding-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

详细维护规则与变更证据见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md) 的变更记录表（2026-07-22 之前的历史改动以该表为准）。

## [v1.5.0] - 2026-08-13

### Changed（guide-router 重建：吸收前端域 + 插件路径降级）

- **前端视觉任务改由本 guide 接管**：域边界删除「前端视觉 → frontend-guide」转介，新增 Step 1「前端视觉」分类 + Step 2 前端视觉子路径（阶段先于风格：方向未定先人工方向选择 → `hallmark` / `impeccable`；动画走 `emil-design-eng` 系；组件库优先项目现有依赖）。依据：交接文档 P0 错配——旧 frontend-guide 把「定方向」默认路由到 `design-an-interface`（实测其 description 为模块 API/interface 设计，非 UI）；`frontend-design:frontend-design` 候选第一跳测试 FAIL（当前会话 `Unknown skill`、settings.json 无 enabledPlugins），按计划回退为人工方向选择 + 已验证 fallback。
- **插件条目全部降为条件路径**：`superpowers:*` / `ecc:*` / `ponytail:*` / `commit-commands:*` / `understand-anything:*` / `ocr review` 不再作为默认主路径；新增「路径角色标记」定义直达/条件路径，判定依据 = 当前会话可调用清单。依据：RED-03——本会话系统提示无任何插件条目，旧正文把插件写死为默认 = 伪装直达。
- **按全库审计（2026-08-13）删/改路由引用**：删除 `simplify`、`request-refactor-plan`、`review`、`review-doc`、`security-and-hardening` 的路由引用（审计建议档「移除+改路由」，skill 本体移动待用户逐项拍板后执行）；`security-review` 改内置命令；`planning-and-task-breakdown` 引用已不存在（v1.4.3 删）。
- **新增 A4 两裁决**：教程裁决（给自己学会 → learning-guide；对外发布 → article-writing-guide）；Step 4 无匹配改按最终交付物四问收口，独立工具请求直接执行不制造第四 router。
- **新增角色分层（A2 本域项）**：`gitnexus-guide`（参考层）、`animation-vocabulary`（词汇参考层）不作为用户第一跳。
- **Step 0.7 新增「多会话工作」缺口行**：跨会话任务问交接物/断点续跑方式（ask-matt 可迁移思想之单/多会话区分）。

### Fixed（活跃漂移文件点名修复）

- `references/cheatsheet.md`：`grill-me`（已撤销）默认行改 `expose-unknowns` 判级；`review` / `security-and-hardening` 行删；九查 → 十查；`research`（已撤销）→ `agent-reach`；插件行全部加条件路径标注。
- `references/ecosystems.md`：Matt Pocock 代表项清理已撤销目标（grill-me/triage/tdd/setup-matt-pocock-skills）；新增 frontend-design 候选测试 FAIL 实测状态；`understand` 裸名改 `understand-anything:understand`（条件路径）；ponytail/caveman 按 A3 分流表述。
- `test-prompts.json`：id 4/10/11/12/13/14/16/17/20/23/29 同步新路由（内置 security-review、手动默认、十查）；新增 #30（登录页方向未定不得进 design-an-interface）、#31（点名插件不可用走 fallback）、#32（三域外独立工具直接执行）、#33（教程归属裁决）。

### Rationale

- 依据：2026-08-13 交接文档 RED 基线（RED-01 前端 P0 错配 / RED-03 插件伪装直达 / RED-04 三域外无收口 / RED-05 单多会话区分）+ 96 项全库审计报告（skill-trimmer-workspace/audit-report-draft.md）。
- 未动：触发门禁、开工问询、风险矩阵、收敛规则、学习型开发/判级/知识收尾/循环/调研分类主体——无缺陷暴露。

## [v1.4.5] - 2026-08-13

### Fixed

- Step 1「开发新功能」行示例删「做个新页面」撞词，改内联负向：含『页面/界面/UI/落地页/登录页』且要视觉产出 → frontend-guide（#5 撞词行内联负向）。
- `grill-me` / `improve-codebase-architecture` 已移 `_weak-model-backup` → 改手动/fallback 注（开发新功能、判级/暴露未知、重构/简化 3 分类）。
- `understand` 裸名改 `understand-anything:understand`（理解代码 3 处）；编码域调研行 `research`（存证调研）→ `agent-reach`。
- `test-prompts.json` #26 expected 同步。

### Rationale

- guide-skill-auditor 组合审查（2026-08-13）：#5 撞词行无内联负向 + #6 死引用（grill-me / improve-codebase-architecture 移备份磁盘实证；understand/research 前缀或备份）。
- 未动：Step 2 各分类主路径、Step 0.5-0.8、风险矩阵、触发门禁——无缺陷暴露。

## [v1.4.4] - 2026-07-31

### Fixed

- description 补 what 句「本 skill 是 Claude Code 编码域开工路由器」--对齐 guide-skill-auditor 十查 #1（router 型必须声明分发角色；frontend/learning 已有，本域缺失）。
- `security-review` 裸名改 `ecc:security-review`（Step 2 审查代码分类高风险行），与同文件 `ecc:python-review`/`ecc:react-build` 前缀一致。

### Rationale

- guide-skill-auditor 组合审查（2026-07-31）发现 #1 FAIL：description 缺 what，agent 对路由分发职责的理解被削弱。依据 router-guide-skill-quality-bar 第 2 条（router 型必须含「我是 X 域路由器」what）。
- security-review 属 ecc marketplaces skill，调用前缀统一防裸名找不到。

## [v1.4.3] - 2026-07-29

### Fixed

- 删除 `planning-and-task-breakdown` 的 3 处路由引用（「有需求文档」分类的轻量拆任务路径、AskUserQuestion B 选项、SP:writing-plans fallback）——该 skill 已按 skill-trimmer 精简移入 `_weak-model-backup/`（D 类+C2，与 SP:writing-plans 重复），fallback 改为 CLAUDE.md §3 手动拆切片 + PLAN.md。

### Rationale

- 2026-07-28 skill-trimmer 全库精简判定（Carl 四删五留 + 本机三决议），用户逐项拍板后执行；guide-skill-auditor 验证无死引用。

## [v1.4.2] - 2026-07-25

### Fixed

- 开工问询与 Step 0.7 背景去重：开工问询第 2 条加「Step 0.7 已覆盖的缺口不重复问」；Step 0.7 头部加「开工问询已问过的背景不重复收」。
- 模式默认从「默认推荐 coach」改「按任务类型推荐」（coach/pair/driver 各有适用场景，见开工问询第 1 条）；Step 0.8 同步删「默认 coach」。

### Rationale

- 2026-07-25 评审中风险：开工问询触发条件是「需求模糊/缺背景」，一刀切默认 coach 在明确交付/机械任务上虚晃；开工问询与 Step 0.7 都问背景存在重复问窗口。

## [v1.4.1] - 2026-07-25

### Fixed

- 开工问询标题摘「grill-me 式」字样（死引用）：grill-me 本体是逐题压问，开工问询是一次性模式问询，引用名不符。改中性名「路由入口」。
- Step 0.8 收敛：coach/pair/driver 定为**路由词汇**，不再内嵌执行定义；进 `ai-coding-coach` 后协作行为以该 skill 为准（partner-coach/coach/engineer），ai-coding-coach 侧加「Mode vocabulary (router handoff)」映射段。
- learning-guide 裁决规则 3 第 4 点删除「编码任务开工判级 → ai-coding-guide」半句：判级/暴露未知不分域统一 → `expose-unknowns`，编码判级不再在学习域 guide 里被裁决归属。

### Rationale

- 2026-07-25 评审发现 v1.4.0 落地三处硬伤：(1)「grill-me 式」引用与实际问询强度不符；(2) Step 0.8 与 ai-coding-coach 双重定义模式；(3) 判级归属按域切开属绕路，`expose-unknowns` 本就处理判级方法。三处均为 routing-layer 冲突，非行为变更。

## [v1.4.0] - 2026-07-25

### Added

- 新增「开工问询（grill-me 式，路由入口）」段：触发门禁后、分类前，逐个问模式（coach/pair/driver，默认 coach）+ 背景，把 v2.2 learning-first 从全局软声明变成 guide 硬触发。
- Step 0.5 路由输出契约 5 行 -> 6 行，加「参与度」行。
- Step 0.8 学习陪跑模式从「学习型开发分类专属」提升为「所有分类路由出口默认卡」，默认 coach。

### Rationale

- v2.2 原写的 `/output-styles` -> Learning 模式经实测本机不存在（无命令/配置/文件），v2.2 一直零落地机制。改由 4 guide 开工问询承担落地。
- 用户要求（2026-07-25）：「在 AI 时代通过指挥 AI 执行任务提升自己，增加协作参与感，不是 AI 全做完」。
- 与决策点先问分工：开工问询管 why（背景）+ how（模式）；决策点先问管 which（方向）。不重叠。

## [v1.3.2] - 2026-07-23

### Added

- 「优先规则」新增**混合意图裁决（tie-breaker）**：单一请求跨多域时按「最终交付物/目标」定归属（代码+写作看交付物、修bug+求理解看目标、做页面+写代码看有无视觉产出），判不出按 Step 4 问。
- 「优先规则」新增**决策点先问（默认问、可直接做）**：方向/方案/栈选型等多走向决策点先给 2-3 选项问用户，不让下游 skill 自行推断；用户说「直接做/你定」则跳过走默认。

### Fixed

- 修死引用 `verify`：Step 2 横切收尾（原 :155）与 `references/cheatsheet.md` 中裸名 `verify` 实为不存在的 skill，改为「`run` 驱动真实流程验证 + `superpowers:verification-before-completion` 组织证据」。

### Rationale

- tie-breaker 依据：guide-skill-auditor 动态基线（2026-07-23）发现「代码+写作」「修bug+求理解」混合意图无归属裁决，子代理实测有摇摆空间。
- 决策点先问依据：用户明确反对「让下游 skill 自己拍脑袋定方向」（2026-07-23），对齐 CLAUDE.md「反查真需求」「grill-me 压清」既有规则；强度取「默认问、可直接做」对齐本 guide「默认值先于菜单」。
- verify 死引用依据：guide-health-checker（2026-07-23）实测磁盘+会话无裸名 `verify` skill。

## [v1.3.1] - 2026-07-22

### Added

- 「路由指南维护」分类新增子路径：审查/优化/新建任一 router 型 guide skill → `guide-skill-auditor`（Step 1 信号行 + Step 2 分类块 + 决策速查各 1 处）。
- `test-prompts.json` 新增 #29（审查 learning-guide → guide-skill-auditor）。

### Rationale

- 新 skill `guide-skill-auditor` 落成（v1.0.0），把四域 v1.3.0 改造方法论固化为九查清单 + 基线测试 + 分级修复流程；本分类接线让它可被「审查 guide」类请求路由到。
- TDD 证据：RED 裸审子代理对预埋 9 缺陷样本仅自发发现 4/9 项（漏 description 流程摘要、范畴词兜底行、防漂移门禁等结构性检查），GREEN 带 skill 后 9/9 全识别。

## [v1.3.0] - 2026-07-22

### Added

- description 加「不用于」清单（含"页面/界面/UI/落地页/登录页"的视觉任务走 frontend-guide、中文技术文章写改审走 article-writing-guide、学习调研走 learning-guide）+ 版本戳 `<!-- v1.3.0 -->`。
- 新增「域边界」段：显式枚举三类转介（前端视觉 / 写作 / 学习）+ 反例（纯后端 API、CLI、构建/调试/审查/提交留在本域），不用「其他/等」范畴词（依据：Superpowers issue #1301 范畴词禁令被放大解释）。
- 新增「触发门禁」3 行：Step 1 分类前输出域归属 + 存在性 + 非编码域转介（依据：社区实测无门禁 skill 触发率 0-20%，forced-eval 模式可达 84%）。
- 质量底线新增「默认值先于菜单」：AskUserQuestion 收敛为仅路径选择改变成本/风险/产物且无法判断时使用（依据：Anthropic 官方 defaults-not-menus 指导）。
- 文末加 HTML 注释路由表门禁：删除 Step 1 信号表 / Step 2 分类路径前必须引用真实误路由事故或官方变更证据（防无证据漂移）。
- `test-prompts.json` 新增 #27（落地页+写码 → 转介 frontend-guide）、#28（吃透 transformer → 转介 learning-guide）域边界回归用例。

### Rationale

- 2026-07-22 RED 基线（子代理无正文加载）：「登录页极简风」「落地页+写码」视觉请求第一跳全被本 guide 抢走——本 guide 在全局 CLAUDE.md §1.0 的优先级导致抢单。修复手段：本 description 加「不用于」清单 + frontend-guide 侧加「视觉优先」条款，双保险。GREEN 验证已确认子代理读到 v1.3.0 description 后对落地页请求判本 guide 为 NO。
- Step 1/Step 2 路由表本身本轮未动——基线测试未暴露分类缺陷，避免无证据漂移。
