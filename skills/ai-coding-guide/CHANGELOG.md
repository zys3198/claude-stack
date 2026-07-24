# Changelog

本文件记录 ai-coding-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

详细维护规则与变更证据见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md) 的变更记录表（2026-07-22 之前的历史改动以该表为准）。

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
