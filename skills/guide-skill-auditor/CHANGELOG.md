# Changelog

本文件记录 guide-skill-auditor 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

## [v1.5.0] - 2026-08-11

### Changed（借鉴 ask-matt 设计思路，用户拍板全采纳）

- **第 6 项扩为「路由目标合法性（存在性 + 可直达性）」**：原只查幻觉引用（存在性）；新增②可直达性——直达目标的 description 若自声明「不主动响应 / 被 X 引用 / 判定源」类参考层身份 → P0 误路由面。证据：ask-matt「vocabulary underneath」参考层分层（Matt Pocock 生产路由器，社区一手）；javaguide-style-guide 自声明「不主动响应写作请求…终检时被 publish-final-check 引用」（本地一手实例，证明四域生态确有参考层）。
- **第 7 项扩为「默认值先于菜单 + 分支点问句化」**：菜单合理存在时，每分支须是可立即判定的是非/二选一问句 + 每支给具体路径；开放式空泛菜单 = FAIL。证据：ask-matt 分支点范式（"can you settle every question in conversation?" / "is this a multi-session build?"）。
- **第 5 项扩为「无范畴词兜底行 + 撞词行内联负向边界」**：高撞词行须行内内联「何时不选它」，只靠 description 全局「不用于」兜底不算。证据：ask-matt 条目级内联负向（"don't triage them"）+ 本地四域 tie-breaker 实践。
- **组合审查五维 → 六维**：第 3 维扩写组合边声明（产物边：A 产物是 B 输入须指明去向；内部驱动边：B 内部调 C 须让用户知道覆盖关系）；新增第 6 维「下游角色分层」（链上/独立/参考层/维护类区别对待，与第 6 项②呼应）。证据：ask-matt 的组合边声明（implement 内部驱动 tdd、research 喂 grill-with-docs）与 main flow/on-ramps/standalone/vocabulary 分层。

### Added（恢复 2026-08-07 丢失的 v1.4.0 修复，事件经过见下条 v1.4.0 补登）

- description 删方法摘要 + 补 what 角色句；第 3 项扩两处同查 + P1 行补盲区；test-prompts 新增 id7。

### Evidence（满足检查清单门禁）

- ask-matt SKILL.md 全文精读（`~/.claude/skills/ask-matt/`，Matt Pocock skills 的元路由器）——社区一手路由器设计，符合 router-guide-skill-quality-bar 的「官方+社区一手」证据 bar。
- 本地一手：javaguide-style-guide description 自声明参考层身份。
- 用户 2026-08-11 提出「借鉴 ask-matt」并逐条拍板采纳范围（P5/P1/P3/P2+P4 全采纳）；丢失修复的恢复亦经用户拍板。

### 动态基线（description 删方法摘要 → 必跑）

- 5 场景子代理裸跑新 description（af28dce / a1ae926 / aa27f7d / ac7fafa / ab3ae8c，全部存活无降级）：正向审查 ai-coding-guide ✅ / 执行型 ai-text-polisher 负向 ✅ / 选型问题转 ai-coding-guide ✅ / 视觉混合不抢主单 ✅ / 新建翻译域路由器 ✅。**5/5 良性，无 P0 误路由。**

### 未动区域（防无证据漂移）

- 十查仍为 10 项（第 3/5/6/7 项均扩写非新增）；description 的 use-when / 触发词 / 不用于语义未动（删的是方法摘要句——本身即自身第 1 项违规项）。
- 明确不借鉴：ask-matt 的 smart-zone/handoff 会话编排（开工路由器职责外，router 薄/single-step 见 v1.2.0 证据）；ask-matt 的 what-only description 形态（它 user-invoked 不用触发词，四域 model-invoked 必须 what+when，第 1 项不动）。

## [v1.4.0] - 2026-08-07（2026-08-11 补登 + 恢复）

### Fixed

- **① description 违反自身第 1 项**（14 天未发现）：含方法摘要「十项静态检查+子代理基线+分级修复」+ 缺 what 角色句。修：删摘要、补「本 skill 是 router 型 guide 的质量审查器」。证据：自审发现审查工具自己不合规自己标准 = 假绿灯。
- **② MAINTENANCE.md 九查残留**：L13/14「九查」改「十查」——v1.2.1 changelog 声称已改但磁盘实测未净。教训：CHANGELOG 记「已改」≠ 真改，须 grep 实测。
- **③ 第 3 项盲区**：扩为「不用于清单 + description 路由目标列表」两处同查；P1 行补盲区；test-prompts 新增 id7。证据：learning-guide「路由到…等」、frontend-guide「各风格预设」实测踩坑（当日已修，learning v1.4.8 / frontend v1.5.5）。

### 丢失与恢复事件

- 本轮修复 2026-08-07 完成并验收，后磁盘被旧备份回退至 v1.3.0 状态（头号嫌疑：cc-switch 回拉旧备份），三修复全部丢失。2026-08-11 对照 memory（guide-skill-auditor-v1-4-0-self-fix）逐条核实发现缺失，当日按 memory + 磁盘实测恢复，与 ask-matt 借鉴合并发布为 v1.5.0。教训：cc-switch 备份回拉可整体回退 skill 文件——恢复后勿再回拉旧备份覆盖。

## [v1.3.0] - 2026-07-24

### Added

- **组合审查五维**（新章节）：用户问「skill 组合/搭配是否合理」时，除逐 guide 十查外加审——域边界覆盖（两不管地带）/ 边界重叠（tie-breaker 一致性）/ 跨界交接对称性 / 共享兜底有效性 / 下游 skill 归属冲突。证据：2026-07-24 用户明确要「看 skill 的组合是否合理」，auditor 原流程只管单个 guide 不管整套；当日组合审实战检出 expose-unknowns 双挂无归属（learning-guide v1.3.2 修）。
- **动态基线豁免细化**：拆「description 一字未动」为两类——纯 P2 机械补齐可跳（原条款）；description 只加负向收窄条款（「不用于」类，无正向触发词改动）也可跳但须记理由。证据：article-writing-guide v1.3.3 加「不用于」时按旧条款「有任何改动必跑」与「纯收窄无新误路由面」冲突，人工走查后确立豁免。
- **反模式新增**：组合审 vs 单 guide 审的区分——用户要看「四域拼起来合不合理」时主会话直接组合审，不硬塞进单 guide 审查流程。

### Fixed

- **子代理降级路径补防滥用**：降级条件从「连挂 2 次」补为「连挂 2 次 + 落账须记录挂掉的子代理名+错误原文」，堵「懒人不派子代理直接走查」的口子。证据：2026-07-24 adversarial review 维度 3 自问——降级条款原文无举证要求。

### 未动区域（防无证据漂移）

- 十查 10 项标准、修复分级、输出格式、落账规则均未改。本轮 adversarial review 子代理（audit-rev2 等 3 个）再次连挂 API 400，复审仍由主会话人肉走查完成——五维逐项过，除上述 3 项外无新发现；可判定性/内部一致性/证据链/实战回放四维无发现。

## [v1.2.1] - 2026-07-24

### Added

- **动态基线子代理降级路径**：子代理连挂 2 次（API/环境故障）→ 主会话逐场景人肉走查替代，落账标注「人工走查替代子代理」。证据：2026-07-24 本会话 3 个子代理（auditor-reviewer / rev-half1 / rev-half2）连发 `API Error: 400 tokenization failed`，基线流程原无故障对策，会被卡死。
- **自身 `test-prompts.json`（6 条）**：清偿 v1.0.1 起挂账的九查第 9 项必须档债务。3 正向（审查/排查抢单/新建路由器）+ 1 负向（执行型 skill 不用于条款）+ 2 兄弟域边界（视觉混合意图转介 frontend-guide、工具选型转介 ai-coding-guide）。格式对齐 ai-coding-guide test-prompts.json 的 id/prompt/expected/scenario。

### Fixed

- **修复分级孤儿项**：原 P0/P1/P2 三档枚举不全，十查 FAIL 存在无档可归的漏洞（如第 3 项「无不用于」原列 P1，但缺不用于可直接造成兄弟域抢单=P0 级后果）。改为「P0=后果导向（任一项 FAIL 且能直接造成幻觉/误路由/域边界缺失）+ 显式映射（P1=第 1/4/5/7/10 项无实锤误路由；P2=第 2/8/9 项）」，十查 × 三档现在全覆盖无孤儿。证据：本会话人肉走查第 3 步发现。
- **MAINTENANCE.md 术语残留**：「复核九查第 2/9 项」「九查漏判」改「十查」；已知债务表删除 test-prompts.json 行（已清偿）。

### 未动区域（防无证据漂移）

- 十查 10 项检查标准本身、动态基线触发条件、输出格式、反模式表：均未改。本轮自审十查全 PASS（含 description 撞词「guide」场景走查良性），无证据不动。
- 独立 reviewer 子代理 review 因 API 故障未能执行，改为本会话人肉走查；下一轮优化时可补跑 adversarial review。

## [v1.2.0] - 2026-07-23

### Changed（翻案，依据官方+社区一手证据）

- **第 1 项重写：「description 只写触发条件」→「角色定位(what) + 触发条件(when)，无流程摘要」**。原标准押 Superpowers「只写 when」，与 Anthropic 官方三处一致（best-practices / skill-creator / Claude Code 文档均要 what+when 双全）正面冲突。修正洞察：官方与 Superpowers 解决的是**两种不同失败**——官方防「漏触发」（description 是触发决策唯一文本，须信息全），SP 防「跳正文」（写流程摘要→agent 拿 description 当捷径）。「what（角色定位）」不等于「流程摘要」：router 型必须含 what（声明分发角色）助触发，同时无流程摘要防跳正文。**取两派各自成立的半块**。注：四域 guide 的 description 本已是此形状（如 ai-coding-guide「开工路由器」=what + 触发词 + 不用于），歪打正着，是审查器标准写歪了，非 guide 写歪。
- **第 10 项重写：「模糊信号的意图摸查」→「枚举信号表 + 低置信缺口清单」**。v1.1.0 措辞「先摸清意图再路由」过于接近「一律采访」，且「置信度闸门」是代码路由（LangGraph `if conf>threshold`）概念，**prompt 里无可判定的 confidence 变量**——写进 SKILL.md 会退化成正确废话，并诱导 Claude 装自信而永不追问。修正为可判定动作：①明确信号→路径枚举表（命中即直跳=高置信快路由）；②不命中/多解时的缺口清单（按决策点问，不猜，允许「直接定」=低置信才停）。「查表命中/不命中」是「置信度」在 prompt 世界的可执行翻译。范本 ai-coding-guide Step 1（枚举）+ Step 0.7（缺口）。

### Evidence（满足检查清单门禁——官方变更/一手证据）

- Anthropic《Building Effective Agents》：routing=「classifies input and directs to specialized task」，直接分发，澄清非 routing 职责；总原则「simplest solution」。
- OpenAI triage 范例：先轻收集意图再 handoff，questions 要 subtle and natural，只在必要时拆分。
- Amazon Alexa 研究：对所有歧义都追问→损害体验，主张 selective triggering。
- Anthropic skill best-practices + skill-creator + Claude Code 文档：description 要 what+when 双全、第三人称、防 1536 字符截断。
- 社区（LangGraph/Towards AI）：router 薄、stateless、single-step，不直接答题（答题=scope creep）。
- 研究落盘：两路 subagent 一手核实（官方四来源 + 社区五来源），2026-07-23。

### Rationale

- 本轮由用户「先别急，再聊聊优秀 guide skill 该是什么样」驱动，经查官方+社区一手证据后翻案 v1.1.0 两处。关键判断：用户拍板「置信度换成枚举表+缺口清单」（因 prompt 无可判定 confidence）。

### 未动区域（防无证据漂移）

- 第 2–9 项、四域 guide 本体、被引用 skill：均未改。第 10 项改的是「审查判据」，四域 guide 是否需要各自补「枚举表/缺口清单」段，留待真实误路由事故驱动，不无证据先动。



### Added

- **第 10 项「模糊信号的意图摸查（条件触发）」**：用户信号模糊/多解时，guide 须有明确机制先摸清意图/背景/决策点再路由（内嵌最小信息清单，或路由到采访型 skill 如 `grill-me`）。信号明确时本项不适用，采访即误路由。与第 7 项互补夹出「按需摸查」：第 7 项防「明确信号给菜单」（过度采访），第 10 项防「模糊信号硬路由」（闭眼跳）。

### Rationale

- **触发**：用户 2026-07-23 提出设计原则「好的 guide skill 应在最开始摸清意图、弄清全部决策点/要求/背景信息/建议，否则没法做好路由」，并建议用 `/grill-me` 这类采访 skill 打头阵。
- **证据（满足检查清单门禁）**：① `grill-me` 真实存在于 `~/.cc-switch/skills/grill-me/SKILL.md`（描述即「relentlessly interview…one at a time…能从代码查到的就去查代码别问」）；② `ai-coding-guide` Step 0.7 最小信息清单 + CHECKPOINT「默认值先于菜单」证明「模糊才问、明确不问」是本体系已收敛的实战原则；③ 用户当会话明确提出。
- **关键设计约束**：初稿曾与用户原话「开场摸清**全部**决策点」有张力——若按字面写成「guide 一律 grill-me 打头阵」，会与第 7 项（defaults-not-menus）和 CLAUDE.md §1.1「别事事问」正面冲突，把「帮我提交」这类明确信号也变成开场采访。故收窄为**条件触发**：仅模糊/多解信号激活，明确信号豁免。这一收窄本身是对用户原则的关键修正，已与会话中对齐。
- **版本**：v1.0.1 → v1.1.0（新增检查项，语义化 minor）。

### 未动区域（防无证据漂移）

- 第 1–9 项检查标准、`grill-me`/`ai-coding-guide` 等被引用 skill 本体、四域 guide：均未改。本次只新增审查标准，不改任何被审对象——第 10 项是「审查时查什么」，不是「guide 运行时改成一律 grill」。四域 guide 是否要在各自正文补「模糊信号摸查」段，留待各自 guide 用真实误路由事故驱动，不在本轮无证据先动。



### Fixed

独立 reviewer（子代理 adversarial review）发现 2 P0 + 6 P1，本轮修 6 项、明示不修 2 项：

- **P0 基线跳过条件**：原「静态全 PASS 可跳基线」会把动态误路由（静态查不出的那类）永久豁免。改为按改动面触发：description/域边界/路由表有改动或 description 含兄弟域高频词必跑；仅 P2 机械补齐才可跳。
- **P0 幻觉引用误报**：原核对依据「当前会话 available skills 或磁盘」会在审查会话缺目标下游 skill 时误报。改为证据链降序：会话 → 磁盘（`~/.claude/skills/`、`~/.claude/plugins/cache/`、`~/.cc-switch/skills/`）→ 三处都无才记 P0；磁盘有但会话未装记「待本机会话验证」不算 FAIL。
- **P1 触发门禁标准不完整**：补位置要求（分类/委派动作之前）+ 范本指引（ai-coding-guide 触发门禁段）。
- **P1 配套文件过强**：拆必须档（test-prompts.json、CHANGELOG.md）/推荐档（references/MAINTENANCE.md）；自身补建 references/MAINTENANCE.md，test-prompts.json 记入已知债务。
- **P1 版本戳位置模糊**：明确 description 末尾为主，正文末门禁注释可同写且两处一致。
- **P1 路由表门禁语义**：与四域措辞对齐（「增删路由表条目须引用真实事故或官方变更证据」）。

### Won't-fix（明示）

- **第 1/7 项命名重叠**：reviewer 自己也承认「边界其实清楚」（一个管 description 文本、一个管正文菜单），改名收益低于漂移成本。
- **依据列不可本地验证**（#1301、84% 实测）：依据链已完整记录在四域 CHANGELOG 与 handoff，拷贝副本进本 skill 反而制造第二真相源。接受「agent 照单全收」——检查项本身的正确性由门禁条款兜底（增删须引用事故）。

### Rationale

- review 方法论：单 reviewer 子代理（中风险，CLAUDE.md §1.4）+ 自检。reviewer 两个 P0 均实锤（基线豁免漏洞、幻觉误报），立即修；P1 中 4 项修、2 项给反证不修。
- 审查器审自己：九查第 9 项原版会让本 skill 自判 FAIL，拆档后自身合规（CHANGELOG + MAINTENANCE 有，test-prompts 记债）。

## [v1.0.0] - 2026-07-22

### Added

- 初版：九查静态检查（description 只写触发条件 / 版本戳 / 不用于清单 / 触发门禁 / 无范畴词兜底行 / 幻觉引用 / 默认值先于菜单 / 路由表门禁 / 配套文件）+ 动态基线测试流程 + P0/P1/P2 修复分级 + 落账规则。

### Rationale

- 从 2026-07-22 四域 v1.3.0 改造实战提炼（handoff：`C:\ZYS\Code\lab-area\exp\2026-07-22-guide-skills-v130\handoff.md`）。
- TDD 证据链：对预埋 9 缺陷的样本 guide，RED 裸审子代理仅自发发现 4/9 项（漏 description 流程摘要、范畴词兜底行、防漂移门禁、版本戳、不用于清单——即「检查标准存在性」类问题）；GREEN 带本 skill 后 9/9 全识别并正确分级。
