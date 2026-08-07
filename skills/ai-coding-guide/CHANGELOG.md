# Changelog

本文件记录 ai-coding-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

详细维护规则与变更证据见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md) 的变更记录表（2026-07-22 之前的历史改动以该表为准）。

## [v1.4.9] - 2026-08-07

### Added

- Step 2「调试 bug」加 `diagnosing-bugs`（硬 bug/反复修不好/性能回退先走诊断循环）；「开发新功能」加 `spec-driven-development`（需求不清先立 spec）；「理解代码」加 `zoom-out`（不熟代码先看架构定位）。

### Rationale

- 用户拍板（2026-08-07，skill 路由接线会话）：三者为高价值盲区 skill（119 个人 skill 中 40 个未被任何 guide 路由），按「资深全栈+AI 独立开发」画像判为高频，接进编码域路由。全局 `CLAUDE.md` §0 同步补「域外直调」段当元路由。
- 本 guide 内 ecc `*-review`/`*-build` 引用核实为 slash command（真实存在于 ecc commands/ 目录），`ecc:xxx` 引用格式合法、非死引用，不改。
- 验证：三处均为路由表加行（非删改），未动既有分类路径（防无证据漂移）。

## [v1.4.8] - 2026-08-07

### Changed

- 开工问询第 4 出口「handoff→teach（解耦学）」由「自带流程」改为**纯转介 `learning-guide`**：删去本 guide 内的流程展开，只留一句「这是学习流程，转介 learning-guide（其路由表解耦学行 + 完整流程块为唯一执行定义）」。

### Rationale

- 用户拍板（2026-08-07）：「以 learning-guide 为主，ai-coding-guide 命中了可以直接转到它上面」。v1.4.7 把流程同时写进两边 = 双份执行定义，违反单一权威（执行定义归下游路由，本 guide 只路由不展开，对齐 MAINTENANCE 职责分层）。现 learning-guide 为唯一执行定义，本 guide 仅跨域转介。
- 验证：`scripts/audit.ps1` P0:0 P1:0 P2:4（4 个同 v1.4.7 已知假阳性，未新增）。

## [v1.4.7] - 2026-08-07

### Added

- 开工问询模式加第 4 出口「handoff→teach（解耦学）」：用户信号「这块我是真不懂/想单独学透/别当场展开」时，提示 `/handoff` 打包 → `C:\ZYS\Wiki\` 下 `/teach` 单独学 → 归档 learning-record 到 `80-records/`。跨域指针，执行定义归 `learning-guide` v1.4.4（学习域路由器）。

### Rationale

- 用户拍板（2026-08-07）：解耦学的完整用法说明归 `learning-guide` 所有；本 guide 只留一条开工问询跨域指针（编码任务里卡点的出口），不重复展开流程。衔接全局 memory `ai-assist-learning-first-default` v2.3 分支 d。
- `/handoff`、`/teach` 均 `disable-model-invocation`（user-invoked），故本出口仅提示、由用户手动敲，agent 不自动调。
- 验证：`scripts/audit.ps1` P0:0 P1:0 P2:4（4 个为已知假阳性——`/handoff`/`/teach` 是 user-invoked slash 本机无独立文件、`disable-model-invocation`/`run` 为 YAML 字段/关键字非 skill，均未新增真实死引用）。
- 未动区域：Step 1 信号表、Step 2 各分类路径未暴露缺陷，保持原样（防无证据漂移）。

## [v1.4.6] - 2026-08-06

### Added

- 「开发新功能」+「有需求文档」两分类各加一条 **Matt 流程转介**提示（B 主 A 辅）：命中 Matt 独有信号（多会话拆工单 / 留 CONTEXT.md-ADR 纸迹采访 / 原型代码验证 / wayfinder 雾大绿野 / triage 灵感堆积）时，提示手动 `/mattpocock-skills:ask-matt` 进 Matt 编排；只提示不抢路由，未命中不提。「开发新功能」覆盖全部 5 信号，「有需求文档」聚焦多会话工单流（to-spec→to-tickets→implement）。

### Rationale

- 用户拍板「ask-matt 重点用，B 为主 A 为辅」（2026-08-06）：B=guide 转介接线，A=用户手动主力。ask-matt 是 Matt 内部路由器，对 idea→ship 主流程编排比本 guide 深；但其两形态（cc-switch 裸名 + 插件版）均 `disable-model-invocation: true`（user-invoked，模型调不到，只能用户手动敲），故只能转介提示用户敲，不能模型自动调。
- 方案 1（最小改）：只两高频分类加转介行，不新增独立分类、不动 Step 1 信号表 —— 防分类膨胀（MAINTENANCE 分类观察期规则），triage/wayfinder 信号折中并入「开发新功能」转介提示。
- 验证：`scripts/audit.ps1` P0:0 P1:0 P2:2（2 个为已知假阳性 disable-model-invocation/run，未新增）；`mattpocock-skills:ask-matt` 带前缀未被误报。
- 未动区域：其余 17 个分类、Step 1 信号表、cheatsheet/ecosystems 未暴露缺陷，保持原样（防无证据漂移）。

## [v1.4.5] - 2026-08-06

### Fixed

- 清 `planning-and-task-breakdown` 残留死引用 3 处：`references/ecosystems.md` Matt 段代表项与「什么时候优先用」行、重叠区裁决表行；`test-prompts.json` id:3 expected。该 skill v1.4.3 已从 SKILL.md 删除（移 `_weak-model-backup/`），但这几处漏清；当前会话与 `_weak-model-backup/` 均无此 skill，仅 cc-switch 源残留 → 死引用。ecosystems.md 改引 `to-prd`/`to-issues`（裸名磁盘+会话双在，Matt 系 model-invoked）；test-prompts id:3 B 选项同步改。
- `references/ecosystems.md` Matt Pocock 段重写：补**双形态并存**（cc-switch 裸名 vs claude-plugins-official 插件版 `mattpocock-skills:` 前缀 24 个）+ 插件版主流程骨架（`to-spec`/`to-tickets`/`implement`/`wayfinder`）+ user/model-invoked 可调性差异（14 个 user-invoked 模型调不到需手动敲）；删过时自述「非运行时实测」「本机无 agent-skills 插件」。
- 版本戳对齐：文末路由表门禁注释 `v1.3.0` → `v1.4.5`，与 description 一致。

### Rationale

- guide-skill-auditor 审查（2026-08-06）：十查第 6 项幻觉引用详查——经磁盘+当前会话双证，主文件引用零幻觉（`grill-me` 等 cc-switch 裸名均 model-invoked 可调，撤回初判"调不到"疑点）；但 ecosystems.md/test-prompts 残留 v1.4.3 已删 skill 的死引用（P0），Matt 生态地图只画裸名一半漏插件版（P1），版本戳脱节（P2）。
- 动态基线 5 场景（撞词「登录页面」/写作/插件问答/生态对比/调试）全对，零误路由。
- 未动区域：SKILL.md 主文件 Step 1 信号表、Step 2 各分类路径未暴露缺陷，保持原样（防无证据漂移）。

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
