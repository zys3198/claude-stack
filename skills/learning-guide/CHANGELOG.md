# Changelog

本文件记录 learning-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

## [v1.4.3] - 2026-07-31

### Fixed

- description 删流程摘要「先分类（...），再路由到」--对齐 guide-skill-auditor 十查 #1（无流程摘要），保留 what + skill 列表。
- 路由表「拆学习任务」主路径 `planning-and-task-breakdown` 改「手动列清单」--该 skill 已移入 _weak-model-backup，ai-coding-guide v1.4.3 已清引用，本域漏改。

### Rationale

- guide-skill-auditor 组合审查（2026-07-31）：#1 FAIL（流程摘要）+ #6 死引用。planning-and-task-breakdown 经 skill-trimmer 移除+改路由（skill-trim-carl-article-2026-07-28），本域未同步。

## [v1.4.2] - 2026-07-25

### Fixed

- 模式默认从「默认推荐 coach」改「按任务类型推荐」（同 ai-coding-guide v1.4.2）；裁决规则 4 同步。

## [v1.4.1] - 2026-07-25

### Fixed

- 开工问询标题摘「grill-me 式」字样（死引用，同 ai-coding-guide v1.4.1）。
- 裁决规则 3 第 4 点：判级/暴露未知归属从「编码判级 → ai-coding-guide、学习判级 → 本 guide」改为**不分域统一 → `expose-unknowns`**；learning-guide 只在学习任务入口负责路由到它。编码判级不再在学习域 guide 里被裁决归属（2026-07-25 评审：判级按域切开属绕路）。

## [v1.4.0] - 2026-07-25

### Added

- 新增「开工问询（grill-me 式，路由入口）」段：进路由表前逐个问模式（coach 深学/pair 概念解释/driver 速成备考，默认 coach）+ 背景。
- 裁决规则 4 升级为「决策点先问 + 开工问询」：先定模式 + 背景，再问产出形态。

### Rationale

- v2.2 落地：把 learning-first 从全局软声明变成 guide 硬触发。
- learning-guide 域内自带学习属性，主要是口径统一到 coach/pair/driver + 默认 coach。

## [v1.3.2] - 2026-07-24

### Added

- 「裁决规则」第 3 条边界重叠补「开工判级/扫盲」归属：编码任务开工判级 → `ai-coding-guide`（编码判级含栈/架构盲区）；学习任务开工判级 → 本 guide 走 `expose-unknowns`。

### Rationale

- 2026-07-24 组合审查发现 `expose-unknowns` 双挂：ai-coding-guide「判级/暴露未知」与 learning-guide「判级扫盲」都路由它且正文均无 tie-breaker，编码场景开工判级可能误入学习域。按主域分界归属，不动路由表条目本身（双挂非误路由，判级本就跨域——同一下游被两域引用属合理，缺的是归属说明）。

### Unchanged（未动原因）

- 路由表 10 行、其他裁决规则、test-prompts.json 未动：无真实误路由事故驱动；description 未动，动态基线跳过。

## [v1.3.1] - 2026-07-23

### Added

- 「裁决规则」第 4 条升级为**决策点先问（默认问、可直接做）**：分类不清或深浅/产出形态不明时，只问一个关键问题收口——「你是想自己学会，还是要产出教程/文章？深学吃透还是只要概念解释？」，不堆选项，也不让下游学习 skill 自行推断深浅；用户说「直接讲/你定」则跳过走默认。

### Rationale

- 依据：用户明确反对「让下游 skill 自己拍脑袋定方向/深浅」（2026-07-23）。原第 4 条只问「学会 vs 产出」一个二分题，升级后覆盖深浅维度；强度取「默认问、可直接做」，对齐「别事事问」。

## [v1.3.0] - 2026-07-22

### Added

- description 加「不用于」清单（写代码走 ai-coding-guide / 写技术文章走 article-writing-guide / 前端视觉走 frontend-guide）+ 版本戳 `<!-- v1.3.0 -->`。
- 新增「触发门禁」3 行：委派前输出相关性 YES/NO + 存在性 + fallback（依据：社区实测无门禁 skill 触发率 0-20%，forced-eval 模式可达 84%）。
- 组合顺序补 frontend-guide，明确四域枚举（编码 / 写作 / 前端视觉 / 学习），不用「其他/等」范畴词（依据：Superpowers issue #1301 范畴词禁令被放大解释）。
- 文末加 HTML 注释路由表门禁：删除条目前必须引用真实误路由事故或官方变更证据（防无证据漂移）。
- 新增 `test-prompts.json`（7 条：正向 4 + 跨界转介 3）。
- 新增 `references/MAINTENANCE.md`。

### Rationale

- 2026-07-22 RED 基线：「吃透 transformer」学习请求在子代理会话缺 learning-guide 时降级到 tutorial-maker——recall 问题非误路由，本域路由表本身未暴露缺陷，故路由表未动。
- 修复重点是防兄弟域抢单：description 加「不用于」清单与 ai-coding-guide 侧的域边界条款对齐（ai-coding-guide test #28 已收录「吃透 transformer → 转介 learning-guide」回归用例）。
