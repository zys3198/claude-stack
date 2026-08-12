# Changelog

本文件记录 article-writing-guide 路由 skill 及下游 skill（`publish-final-check`、`javaguide-style-guide`）的演进。

格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

## [v1.5.1] - 2026-08-11

### Added

- `article-writer` 新增 §7.11「待实跑占位节」：证据必须亲手实跑才能拿到时（安装体感、报错原文、截图、实测数字），在对应小节后插入 `（待实跑）` 占位节，附 blockquote 跑法建议和「不跑」压缩预案，文末 `<!--发布前待补` 注释统一登记，填实料后删提示。
- `publish-final-check` 子项④ 发布面新增 MUST：grep 拦截残留写作占位（`待实跑`/`待补`/`needs evidence`/`<!--发布前待补`），未清不得发布——占位机制的收口闸。
- `article-writer` §3.5 新增「同源项目边界」：写 fork/二创/上下游系列文，每条特性归属核验到本体还是分支，不串台；对比只比默认形态和官方重心，不替任何一方说「做不到」。

### Rationale

- Pi 文章实战（2026-08-11）：核验拦下「OMP 特性写成 Pi 特性」「Pi 拒绝 MCP 生态」等归属错误；5 个待实跑缺口用结构化占位节预留，实跑前不编造、发布前有闸拦截。指南 SKILL.md 本体未改，版本戳不升。

## [v1.5.0] - 2026-08-11

### Added

- 从零创作和深度改写新增“全篇细骨架冻结门”：选定结构方向后，一次性展示完整 H2/H3；每个子节绑定问题、论点、依据 ID、证据/例子、读者获得感、目标篇幅、表现形式、前后过渡，改写模式再映射现稿位置。
- 骨架末尾汇总预计总篇幅、证据缺口、待补真实经历/截图和可合并章节。用户明确冻结前不得生成正文；明确要求“直接写/跳过骨架”时才可绕过。
- `test-prompts.json` 新增默认从零创作场景，验证用户未主动要求讨论结构时也会命中细骨架闸门。

### Changed

- 默认协作流改为：结构方案 → 方向确认 → 全篇细骨架 → 讨论修改 → 明确冻结 → 逐节正文预览 → 用户确认 → 落盘 → 审查循环。
- 删除“每节设计完停一下、不要一口气设计完整篇”的旧节奏；改为先一次性展示全篇细骨架，再逐节写正文。
- 同步更新 `article-writing-guide/SKILL.md`、`REFERENCE.md`、`test-prompts.json` 与 `article-writer/SKILL.md`；创作和优化模式都改为确认后落盘，优化模式不再默认覆盖现稿。

### Rationale

- 用户反馈：“从0开始写文章应该先列出最细致的骨架，讨论完毕后再动笔”。全篇骨架先行能在正文生成前暴露章节重复、证据缺口、前后依赖和篇幅失衡，减少长文返工。

## [v1.4.4] - 2026-07-31

### Fixed

- description 补 what 句「本 skill 是中文技术写作域开工路由器」--对齐 guide-skill-auditor 十查 #1。

### Rationale

- guide-skill-auditor 组合审查（2026-07-31）发现 #1 FAIL：description 缺 what（frontend/learning 已有，本域缺失）。

## [v1.4.3] - 2026-07-29

### Fixed

- 删除已移入 `_weak-model-backup/` 的 7 个 skill 引用：`writing-fragments`/`writing-shape`/`writing-beats`（起草三件套，素材成型与叙事节拍改路由到 `article-writer` 协作模式 §7）、`doc-finder`（本地仓库调研改 `lean-ctx`）、`hv-analysis`（深度研究改 `research`/`ecc:deep-research`）、`answer-evidence-finder`（问答场景走通用读取，删 ② 行）。
- §1 路由表、§2 起草四选/调研七选、§3 pipeline、§4 规则 7、§5 场景表同步清理。

### Rationale

- 2026-07-28 skill-trimmer 全库精简判定（Carl 四删五留 + 本机三决议），用户逐项拍板后执行；昨日 references.tsv 漏记 router 引用，本轮以实际 grep 为准修正；guide-skill-auditor 验证无死引用。

## [v1.4.2] - 2026-07-25

### Fixed

- 模式默认从「默认推荐 coach」改「按任务类型推荐」（同 ai-coding-guide v1.4.2）；§4 规则 4.6 同步。

## [v1.4.1] - 2026-07-25

### Fixed

- 开工问询标题摘「grill-me 式」字样（死引用，同 ai-coding-guide v1.4.1）。

## [v1.4.0] - 2026-07-25

### Added

- 新增「开工问询（grill-me 式，路由入口）」段：进 §1 路由表前逐个问模式（coach/pair/driver，默认 coach）+ 背景。写作域三模式：coach=该你会的写作核心（结构/论点/文体判断）；pair=协作流（默认）；driver=一次性文案直接写讲 why。
- §3 默认协作写作流从「用户说才触发」提升为「默认参与度 pair」，用户说「直接写」才降级。
- §4 新增规则 4.6 参与度。

### Rationale

- v2.2 落地：把 learning-first 从全局软声明变成 guide 硬触发。
- 消除原 §3 矛盾（「用户说才走」vs「默认走」）：v1.4.0 起默认就走，原信号仍适用但不需要主动说。

## [v1.3.3] - 2026-07-24

### Fixed

- description 补「不用于」兄弟域转介条款（前端视觉 → frontend-guide、纯代码逻辑 → ai-coding-guide、学习调研 → learning-guide）。v1.3.1 只补了 §0 正文的不用于段，description 漏补——description 才是路由唯一信号（guide-skill-auditor 十查 #3，2026-07-24 审查发现）。

### Unchanged（未动原因）

- §1 路由表、§2 易混区分、§3 pipeline、§7 示例全部未动：本轮 guide-skill-auditor 十查其余 9 项全 PASS，无真实误路由事故驱动；description 虽改但加的是负向条款（收窄触发面，正收窄风险），动态基线跳过——下轮有真实投诉再补撞词场景。

## [v1.3.2] - 2026-07-23

### Added

- §4 新增规则 4.5 **决策点先问（默认问、可直接做）**：起草/改写前若文体（博客/教程/方案）、读者、目的三要素不全，先问清再动手，不让下游写作 skill 自行推断定位；用户给了明确标杆/范文或说「直接写」则跳过走默认。

### Fixed

- 修死引用 `deep-research`：§1 表①主路由行与 §3 通用 pipeline 起点（原 :90）把已自认「本机未装」的 `deep-research` 当默认选项，改为从主路由行移除、仅作「已装时的备选」（§0 提示与 §2 调研七选的备选标注保留）。

### Rationale

- 决策点先问依据：用户明确反对「让下游 skill 自己拍脑袋定方向」（2026-07-23）。强度取「默认问、可直接做」，对齐「别事事问」。
- deep-research 死引用依据：guide-health-checker（2026-07-23）实测磁盘+会话无 `deep-research`，却仍占主路由位与默认 pipeline 起点。

## [v1.3.1] - 2026-07-23

### Fixed

- §0 新增「不用于（兄弟域转介）」：前端视觉 → frontend-guide；纯写代码/调试/重构/审查/构建 → ai-coding-guide；学习/调研/速成/做教程 → learning-guide；AI 编码工具选型 → ai-coding-guide（补齐与其他三域 description 「不用于」清单对齐；fix guide-skill-auditor 九查 #3）。

### Unchanged

- description 文本本身未动，§1 路由表、§2 易混区分、§3 pipeline、§7 示例全部未动：上一轮 RED 基线 5 场景子代理路由全对，本轮审查无 description 改动，跳过动态基线（遵循 guide-skill-auditor §第 2 步：仅 P2 机械补齐且 description 一字未动可跳）。

## [v1.3.0] - 2026-07-22

### Added

- description 加版本戳 `<!-- v1.3.0 -->`。
- §0 新增「触发门禁」3 行：委派前输出相关性 YES/NO + 目标 skill 存在性 + 最接近替代（依据：社区实测无门禁 skill 触发率 0-20%，forced-eval 模式可达 84%）。
- 文末加 HTML 注释路由表门禁：删除 §1 路由表条目前必须引用真实误路由事故或官方变更证据（防无证据漂移）。
- 新增 `references/MAINTENANCE.md`（对齐 ai-coding-guide 维护文档模式）。

### Unchanged

- §1 路由表、§2 易混区分、§3 pipeline、§7 示例本轮全部未动：2026-07-22 RED 基线（5 场景子代理）中「改稿+排版+能发吗」场景全程路由正确，本 guide 是四域中唯一未暴露路由缺陷的。避免无证据漂移。

## [0.8.2] - 2026-07-22

### Added

- `SKILL.md` 边学写节新增「信息价值过滤器」：增量初稿前判断一条信息是否值得写（①改变行为 ②反直觉 ③高频门槛 ④支撑主线），默认够用/查文档 30 秒可得/为求全堆参数的一律砍，防止边学边写退化成官方 reference 的搬运。
- `SKILL.md` 边学边写节新增「平台渲染记账」：全程记账目标平台不渲染的元素（公众号：mermaid/数学公式/HTML 表格），发布前统一转 PNG。
- `drawio-chart` SKILL.md 导出模式新增「多页文件导出坑（实测 30.2.6）」：`-p/--page-index/--page` 多页选择器失效恒导第 1 页，绕法为抽单页临时文件再导，并强调导出后须目检 PNG 内容而非只看命令返回成功。

### Rationale

- 来自 OCR 公众号文章实战：写作中途作者纠偏"不太重要的可以不写"，现场立的价值过滤器证明能把 reference 味正文拉回文章味，沉淀进路由 skill 供所有边学边写复用。
- mermaid 公众号不渲染是发布前才暴露的平台适配问题，提前记账比发布闸兜底更省返工。
- draw.io CLI 30.2.6 多页导出失效导致连续 3 次导出同一页，踩坑记录避免后人重复。

## [0.8.1] - 2026-07-20

### Added

- `SKILL.md` §1/§2/§7 与 `REFERENCE.md` §1/§8 新增 `tutorial-maker` 路由：系列教程、从零系统学习、课程计划走 `tutorial-maker`；单篇教程仍走 `article-writer`。
- `SKILL.md` §4 新增失败模式表，把目标 skill 缺失、跨阶段请求、写入闸门、无来源查重、英文文章误触中文专用 skill、模糊改稿 6 类失败转成 if-then 动作。
- `test-prompts.json` 新增 #10，覆盖“从零学 Redis 系列教程”路由。

### Fixed

- 修复 `REFERENCE.md` 审校表格缺分隔行导致的渲染问题。
- 修正 `deep-research`/漂移维护等描述中“§4 规则6”引用，存在性校验实际为 §4 规则7。

### Rationale

- `tutorial-maker` 已在当前 available skills 中，系统教程继续路由到 `article-writer` 会丢练习、折叠答案、from-zero 自审门等专用流程。
- 失败模式表比散文规则更利于路由器在压力场景下执行。

## [0.8.0] - 2026-07-20

### Added

- `SKILL.md` §3 新增 **默认协作写作流（结构 → 小节设计 → 生成 → 审查）**：用户希望先讨论文章结构、由 AI 给结构选项、用户补充想法、逐节设计内容、确认后生成正文、再由用户审查反馈时，默认走分阶段协作，不一次性全文起草。
- `REFERENCE.md` 新增 §2「默认协作写作流」并在起草决策树前置识别该模式，避免模糊路由时漏掉“先结构讨论再写”的需求。
- `article-writer` §7 新增 **协作式写作模式**：结构方案确认后逐节设计，只生成已确认设计的小节，用户审查后按结构→论点/例子→文风/排版处理反馈。
- `publish-final-check` 的 JavaGuide 风格判定从 `M1-M9` 更新为 `M1-M10`，覆盖 `javaguide-style-guide` 新增的 M10「源码注释与放置」。
- `test-prompts.json` 新增 #9，覆盖“结构讨论 → 逐节设计 → 生成 → 用户审查”的典型触发。

### Rationale

- 该模式适合用户边想边定稿，能减少全文一次性生成后的大返工。
- 该模式是 `article-writer` 前置协作层，不替代调研、去 AI 味、终检等下游 skill。

## [0.7.0] - 2026-07-13

### Added

- `article-writing-guide` 新增 **边学边写** 路由：用户想从 0 了解开源项目/工具，并把学习记录自然沉淀成文章时，先抓权威材料和学习路径，再按现稿结构增量写入，避免直接盲写全文。
- `SKILL.md`：frontmatter description、§1 路由表、§2 易混区分、§3 默认 pipeline、§7 示例均加入“边学习边写 / 学习记录成文”路径。
- `REFERENCE.md`：新增 §2「边学边写路径（学习记录自然成文）」，区分有现稿和无现稿两条路线，并补不要做的反例。
- `test-prompts.json`：新增 #8，覆盖“边学习边写开源项目，最后沉淀进文章”的典型触发。

### Rationale

- 本轮来自实战：Open Code Review 文章不是先完整研究再一次性起草，而是边读官方资料、边形成学习路径、边把心智模型和命令路径写回文章。该路径更适合工具体验文、开源项目入门文和源码阅读前置科普。
- 路由层要识别这种模式，否则会误走纯 `article-writer` 从零起草，丢失学习现场感；或误走纯 `edit-article`，缺少权威资料收集和学习路径阶段。
## [0.6.0] - 2026-06-24

### javaguide-style-guide 补源码/表格呈现判定（article-writer §6.4 终检覆盖）

article-writer §6.4「源码/参数处理四原则」此前只在写作执行层，终检无法覆盖。本轮把四原则提炼为可判定的 checklist 项 + 量化阈值，补进判定层。

#### javaguide-style-guide SKILL.md
- Added: §1 MUST 加 **M10 源码注释与放置**——代码块不裸贴大段实现（关键片段带中文行内注释），大段完整实现进末尾独立章节不散落正文。对应 §6.4 原则2/3。`绝不裸贴`是硬约束，列 MUST。
- Added: §1 SHOULD 加 **S7 表格优先 + 图代源码**——表格为默认论证载体，复杂逻辑优先 Mermaid 而非堆源码。对应 §6.4 原则1/4。密度偏好因文体而异，列 SHOULD。
- Added: §2 量化阈值表加两行——大段裸贴代码（M10，>40行未注释且不在专节）、表格 vs 代码比（S7，源码密集型文表格行 ≥3×代码块）。
- Added: §3 正反例表加 M10/S7 两行。
- Changed: §5 SHOULD 范围 S1-S6 → S1-S7。
- Changed: §6 版本 0.3.0 → 0.4.0。

### 设计取舍
- M10/S7 刻意分层：裸贴大段源码（原则2/3，绝不）上 MUST 可拦发布；表格优先/Mermaid 代源码（原则1/4，密度偏好）留 SHOULD 不硬拦，避免误伤概念型文章（少表格少代码也合法）。
- 与 article-writer §6.4 不重叠：§6.4 给写作指引+实例（怎么写），本 skill 给判定阈值（验不验得过），延续 §0「写作执行/风格判定」分工。
- 未改 article-writer：§6.4 四原则本身保留在写作层不变，本 skill 只补判定视角。

## [0.5.0] - 2026-06-24

### Round 3b 优化（路由补全 + 漂移维护，dry_run）

对当前 available skills 列表交叉核对 §1 路由表，发现已漂移：路由表漏收录 3 个实际存在的调研类 skill，且无同步机制。本轮从「堵漏」（0.4.0 规则6）升级到「路由更准」。

#### article-writing-guide SKILL.md
- Added: §1 调研行补 `last30days`🪶（全网话题近 30 天热度）、`aihot`🪶（AI 行业资讯，中文）、`agent-reach`🪶（多平台定向检索）。三个实际存在于 available skills 但此前漏收录的轻量级调研工具。
- Changed: §2「调研四选」→「调研七选」，按信息源重新组织（本地/全网趋势/多平台/深度带引用），给「先按信息源定位」的裁决规则；新手优先五个 🪶 轻量级。
- Added: §6 演进「路由表漂移维护」——路由表靠人工维护会漂移，定期拿 available skills 列表与 §1 表交叉核对，逐项跑 §4 规则6 校验。

#### article-writing-guide REFERENCE.md
- Changed: §1 决策树「需要先调研」分支补 last30days / aihot / agent-reach 三条；deep-research 标注「先 §4 规则6 校验存在」。

### 实测验证（非 dry_run）
- 把 0.4.0 加的规则6（存在性校验）真用上了：发现 §1 表对 available skills 列表漂移（deep-research 不在列表、漏 3 个轻量调研工具）。规则6 从「理论兜底」变成「已被实战触发的补丁」。
- 漂移是真问题，不是空想：本轮即因交叉核对而发现并修复。

## [0.4.0] - 2026-06-24

### Round 3 优化（darwin-skill 评估驱动，dry_run）

基线 ~81（达标线 80）。本轮只动真短板，不凑分（HL-4 见好就收）。

#### article-writing-guide SKILL.md（dim3 + dim5 + dim7）
- Added: §4 规则6「目标 skill 存在性校验」——命中 §1 表后先核对目标在本会话 available skills 列表，不存在（被删/改名/未装）→ 🛑 STOP + 报告替代，不路由进虚空。把 javaguide-writer 逐个 redirect 泛化成通用兜底。最高杠杆改动（router 最大结构性风险）。
- Added: §7 端到端示例补「帮我改改这篇」模糊 case（新手最常踩，原缺）。
- Changed: §0 系统内置 skill 提示 `~/.Codex/skills/` → 「本地 skills 目录」（runtime 中立化）。
- Changed: §0 javaguide-writer 重定向交叉引用 §4 规则6。

#### article-writing-guide test-prompts.json（dim8 支撑）
- Added: #5「帮我改改这篇」模糊请求、#6 跨阶段「写并发布」、#7 含已删 skill 的多步请求。4 → 7 条，覆盖 §4 规则3/6 与 dim5 易混裁决。
- 验证：JSON 合法（7 条）。

### 评分变化（dry_run）
- dim3 失败模式编码 8→9（+1.2）：补目标存在性校验这一关键失败分支。
- dim5 可执行具体性 8→9（+1.7）：补模糊 case 示例。
- dim8 实测表现 7→8（+2.3）：test-prompts 扩充，覆盖 router 专属风险场景。
- 估算总分 ~81 → ~86（Δ +5，dry_run，重要决策需 full_test 复核）。

## [0.3.1] - 2026-06-23

### 生态清理
- Removed: `javaguide-writer` skill 目录删除（纯重定向桩，功能已并入 `article-writer`）。SKILL.md §0 与 test-prompts #4 重定向措辞从"目录残留"改为"已删除引导"，重定向能力降级为依赖主模型知识识别废弃名。

## [0.3.0] - 2026-06-12

### Round 2 优化（终审全部达标 ≥80）

终审评分：article-writing-guide **82** / publish-final-check **83** / javaguide-style-guide **81**（全过 80 线）。

#### javaguide-style-guide（80 → 81，修高危+2中项稳线）
- Fixed: §0 权威关系声明矛盾——"不覆盖"改为"终检时 §2 量化阈值**覆盖** §6 对应项"（终检比写作基线严，M5：写时 ≥1 处 / 终检 ≥3 处，有意加严）。
- Added: §2 量化阈值表"判定法"列补可执行 grep 正则（M5 数字密度 / M7 裸块 / M3 数字前缀 / M9 AI 味词 / M6 时效词）。
- Added: §3 正反例补 M5/M6/M8 量化项对照（原仅覆盖非量化项）。
- Added: §4 反模式补"写作基线 vs 终检阈值混用"一条；明确与 article-writer §6.9（写作向）互补关系。
- Changed: 版本号 0.3.0。

#### article-writing-guide（82，达标，余项锦上添花未做）
- 已达标。可选优化（未做）：test-prompts.json 扩充、§3 pipeline 末环独立成块、description 末句削弱重叠。

#### publish-final-check（83，达标，余项锦上添花未做）
- 已达标。可选优化（未做）：§2③ S6 跨文件命名对齐、端到端 trace 示例、②死链判据补状态码规则。

## [0.2.0] - 2026-06-12

### Round 1 优化（评分基线 68-74 → 目标 ≥80）

#### publish-final-check（74 → 目标 80+）
- Fixed: 全局错别字"柏验"→"查重"（description + 正文 + 报告格式，共 4 处）。
- Fixed: 子项③不再委派交互式 `ai-text-polisher`（polisher 是多轮改写 skill，不适合只扫不改）；AI 味改自检关键词黑名单。
- Added: §1 输入样例（成稿路径 + 参考源三形式 + 平台枚举 + JavaGuide 标记）。
- Added: §3 并行失败兜底（子项 exception 不阻塞其他子项，标未完成）。
- Changed: §2③ 风格判定引用 `javaguide-style-guide` §1 M1-M9 + §2 量化阈值（精确引用路径）。
- Added: §7 版本号 0.2.0。

#### javaguide-style-guide（68 → 目标 80+）
- Changed: **重构为薄判定层**，消除与 `article-writer` §6 重叠。明确三层权威：§6 写作执行 / 本 skill 终检判定 / publish-final-check 放行。
- Added: §2 量化阈值表（原创度<20%对齐、数字密度≥3、格式间隔≤5段、段等长<30%差、AI味词0、时效词0、口语词非均匀）——article-writer §6 缺失的补强。
- Added: §3 正反例对照（M1/M2/M3/M4/M7/M9 每项 ✅/❌）。
- Added: §4 判定向反模式（非 docs/ai 误用、证据失效、当写作教程、MUST/SHOULD 混淆）。
- Added: §6 版本号 0.2.0 + 季度复审机制 + 证据失效标"可能漂移"。
- Changed: frontmatter 明确"不主动响应写作请求"。

#### article-writing-guide SKILL.md（72 → 目标 80+）
- Added: §7 端到端路由示例 10 条（query → skill → 理由）。
- Changed: description 削弱与 article-writer 触发词重叠，强化元触发（"不知道用哪个 skill"）。
- Added: §0 注明 `deep-research`/`hv-analysis` 系统内置；`javaguide-writer` 残留重定向。
- Added: §2 "JavaGuide 风格三件套"区分（article-writer §6 写 / style-guide 判 / publish 放行）。
- Added: §8 路由失败兜底（与 REFERENCE §8 对齐）。

#### article-writing-guide REFERENCE.md
- Changed: 成本标注 🪶🪨🔥 全文统一（§1/§2/§3/§4/§6 表头 + 表内）。
- Changed: §6 JavaGuide 模式引用 `javaguide-style-guide` §1 M1-M9 + §2 量化阈值。
- Added: §7 反模式 +1（混淆 style-guide 与 article-writer §6）。
- Added: §8 指向 SKILL.md §7 端到端示例 + test-prompts.json。

## [0.1.0] - 2026-06-12

### Added（初版）
- 新建 `javaguide-style-guide` skill：JavaGuide docs/ai 风格基线，从 5 篇真文章反推的 MUST/SHOULD checklist。
- 新建 `publish-final-check` skill：发布前强制关卡。4 子项，MUST/SHOULD 两级拦截。
- `article-writing-guide/SKILL.md` §1 路由表：成本标注、obsidian-vault、⑩指向 publish-final-check、⑪参考源管理。
- `REFERENCE.md`：决策树加 obsidian、审校叠加规则、柏验只比贴源+边界+改写示例、pipeline 末环+落盘规则、反模式。
- `CHANGELOG.md`：演进记录机制。
