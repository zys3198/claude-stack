# Changelog

本文件记录 learning-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

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
