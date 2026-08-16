# Changelog

本文件记录 ai-coding-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

详细维护规则与变更证据见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md) 的变更记录表（2026-07-22 之前的历史改动以该表为准）。

## [v1.8.0] - 2026-08-16

### Changed（参与度词汇统一：集中化 + 引用）
- 开工问询「模式」三选（coach/pair/driver）替换为「归属问（你练/我讲/我动手）+ 说话层」。
- 说话层 persona 定义集中到 `learning-personas`，本 guide 只引用不重复展开（渐进式披露）；Step 0.8 表同步换归属词。
- references/classification-details.md、test-prompts.json 同步换词。
- description 增补「协作参与度/说话层统一走 learning-personas」。

## [v1.7.0] - 2026-08-14

### Added

- **`references/classification-details.md`（新建）**：Step 2 低频 10 分类完整细节（学习型开发 / 判级/暴露未知 / 有需求文档 / 文档写作 / 路由指南维护 / 提交/收尾 / 知识收尾 / 循环任务 / 了解指南 / 编码域调研），每分类含默认路径 / AskUserQuestion / Fallback，文件头带分类索引表。
- **`references/frontend-visual.md`（新建）**：前端视觉 5 分支完整细节（方向未定 / 提质 / 实现 / 动画 / 特殊产物 / 风格叠加）+ 负边界 + 组合顺序 + 验证 + AskUserQuestion / Fallback。

### Changed

- **主文件渐进披露重构（481 → 362 行）**：Step 2 由「18 个分类全部内联」改为「7 个高频分类内联 + 前端视觉决策骨架一行索引 + 低频 10 分类索引表」。低频索引表每行给**一句话主路径 + 条件路径/Fallback 概要 + 「命中即读 references/classification-details.md」提示**，防 references 不自动加载导致路由残缺。

### Rationale

- 依据：渐进披露原则——主文件只放基本通用规则约定 + 真实索引路由，长细节下放 references（SKILL.md 质量底线「AI 可读」已有此约定，本轮执行到位）。references 不自动加载，故索引行必须保留一句话主路径（不读 references 也能正确路由）并显式提示命中即读。
- **高频分类刻意内联**：路由判定核心不外置——开发新功能 / 理解代码 / 审查代码 / 调试 bug / 重构/简化 / 快速改动 / 构建错误是最高频编码任务，内联保证路由骨架自包含。
- **未做进一步格式压缩**（Step 0.4/0.7 表、高频分类 AskUserQuestion 保持完整）：用户确认 5 文件范围（SKILL.md + 2 新建 references + MAINTENANCE.md + CHANGELOG.md）；主文件 362 行高于预估 210，原因=保留核心规则与高频分类内联。是否继续压缩由用户后续拍板。
- 死引用检查：`grep -oE 'references/[a-z-]+\.md' SKILL.md | sort -u` vs 实际目录文件，diff 为空（无死引用）。

## [v1.6.0] - 2026-08-14

### Added

- **Step 0.4 新增流程深度裁决（全套 / 拆单 / 最小三档）**：先按任务复杂度 + 代码熟悉度定流程深度再选 skill——复杂项目/陌生代码库/高风险改动/跨模块设计走全套（`superpowers:*` 完整链：澄清 → 设计 → 计划 → 执行 → 审查 → 验证）；任务需要某一环走拆单（`mattpocock-skills:grilling` / `diagnosing-bugs` / `tdd` / `code-review`）；单点/机械走直接最小（`ponytail:ponytail` 条件路径）。复杂度无法判断才问一句任务规模。
- **mattpocock-skills 轻量工具箱段（ecosystems.md 新增）**：可拆开使用、不默认走完整流程，哪个环节反复出错只补哪块；含 **user-invoked 提醒**——插件版模型无法自动调用，路由到这些 skill 时必须明确提醒用户手动启用。

### Changed

- `references/ecosystems.md` Superpowers 段重写：从「流程纪律层」改为「完整流程套件」，明确全套只在复杂/陌生/高风险值得走，任务不够复杂时从保护变负担（引用文章判据）。
- 重叠区处理加「Superpowers 全套 vs mattpocock 拆单 vs 直接最小」裁决行；降级路径表补 matt 不可用时的 fallback（grilling → 开工问询 + `expose-unknowns`；diagnosing-bugs → `code-change-workflow` §2；tdd → 手动红绿小步改；code-review → 内置 `code-review`）。

### Rationale

- 依据：JavaGuide《强模型时代，AI 编程 Skills 还有必要装吗？》（2026-08-14 阅读）——强模型已能自做读项目/找调用链/跑基础测试等基础步骤，全套流程对小任务从保护变负担；模型执行越快走错方向代价越大，需求模糊先澄清（`grilling`）；mattpocock 轻量组合按需拆单优于 Superpowers 式整套默认。用户确认 4 文件范围（SKILL.md / ecosystems.md / MAINTENANCE.md / CHANGELOG.md），test-prompts.json 用例待补。
- 未动：分类路径主体、风险矩阵、触发门禁、Step 1 信号表——本轮只补「流程深度」裁决维度，不删已有路由。

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
