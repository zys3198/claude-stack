# Changelog

本文件记录 frontend-guide 路由 skill 的演进。格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

## [v1.5.3] - 2026-07-31

### Fixed

- 删 description「按阶段与风格」轻度流程词--对齐 guide-skill-auditor 十查 #1（无流程摘要）。
- 删风格表 `stitch-design-taste` 行（已移入 _weak-model-backup，仍当活跃引用，状态矛盾）。
- 重叠裁决表删 `design-taste-frontend-v1`（已移入备份，"不选"列对照失效）。

### Rationale

- guide-skill-auditor 组合审查（2026-07-31）：#1 borderline + #6 状态矛盾。stitch-design-taste / design-taste-frontend-v1 经 skill-trimmer 二轮移入备份（skill-trim-carl-article-2026-07-28），guide 引用未同步。

## [v1.5.2] - 2026-07-25

### Fixed

- 开工问询 coach 分支对齐视觉域：coach=想练设计判断时先给方向/参考/初判，AI 纠偏；**无设计背景或给不出初判时 coach 退化为 pair（决策点先问），不空转**。
- 模式默认从「默认推荐 coach」改「按任务类型推荐」（同 ai-coding-guide v1.4.2）；「组合顺序」参与度条同步。

### Rationale

- 2026-07-25 评审中风险：视觉域的 coach 若要求用户凭空给设计判断会空转——用户没设计背景时给不出；实质应退化为「决策点先问」。

## [v1.5.1] - 2026-07-25

### Fixed

- 开工问询标题摘「grill-me 式」字样（死引用，同 ai-coding-guide v1.4.1）。

## [v1.5.0] - 2026-07-25

### Added

- 新增「开工问询（grill-me 式，路由入口）」段：定阶段前逐个问模式（coach/pair/driver，默认 coach）+ 背景。三模式前端映射：coach=该你会的核心（布局/CSS/组件设计/动画原理）；pair=不熟设计方向 AI 给选项；driver=有视觉产出+没说学习直接做讲 why。
- 「组合顺序」加「参与度」条：按开工问询定的模式走。

### Rationale

- v2.2 落地：把 learning-first 从全局软声明变成 guide 硬触发（同 ai-coding-guide v1.4.0）。
- 默认 coach；机械改动（改文案/颜色/间距）直接 driver。

## [v1.4.1] - 2026-07-23

### Added

- 「组合顺序」新增**决策点先问（默认问、可直接做）**：定方向/定风格这类有多种合理走向的决策，先给 2-3 个选项问用户，不让设计 skill 自行推断；用户说「你定/直接做」则跳过走默认。
- 「反模式」首行改写：用户就说「做个登录页」从「默认定方向 `design-taste-frontend`」改为「先给 2-3 个方向选项问偏好（或问有无参考/品牌），用户说'你定/直接做'才让它推断」。

### Rationale

- 依据：用户明确反对「让 design-taste-frontend 自己拍脑袋定方向」（2026-07-23），对齐 CLAUDE.md「反查真需求」「grill-me 压清」。强度取「默认问、可直接做」，避免每次做页面被硬拦（对齐「别事事问」）。

## [v1.4.0] - 2026-07-23

### Added

- description 加动画触发词（动画 / 动效 / 丝滑 / 回弹 / 过渡 / 转场）+ 触发条件补「做/改/审动画动效」+ 动画 skill 路由清单（emil-design-eng / review-animations / improve-animations / find-animation-opportunities / animation-vocabulary / apple-design / pick-ui-library）。版本戳 `<!-- v1.4.0 -->`。
- 「先定阶段」表新增「动画动效」行：信号=做/改/审动画、加动效、不够丝滑、回弹/过渡手感不对、效果叫什么；主路径按子意图分流到 5 个动画 skill。
- 「重叠裁决」表新增 6 行动画选谁：综合判断→emil-design-eng、审已有→review-animations、全库改造→improve-animations、找该动哪→find-animation-opportunities、命名术语→animation-vocabulary、选动画库→pick-ui-library。
- `test-prompts.json` 新增 4 条动画镜像（id 8-11：改动画 / 审动画 / 动画命名 / 加动效）。

### Fixed

- description 删「先定阶段（定方向→出参考图→实现→升级现有），再定风格」流程枚举（九查 #1：description 只写触发条件，防 agent 照 description 执行而不读正文）。

### Rationale

- 2026-07-23 新装 emilkowalski/skills 7 个动画 skill 后，路由表零动画条目（真实域缺口，非臆测漂移）。
- 2026-07-23 动态基线（5 子代理裸跑，只给 description）：动画请求第一跳 5/5 进对域（无误路由 P0），但 4 个动画场景全靠「页面/界面/升级现有」泛词兜底命中，无一直接命中动画条目；命名类（场景3）靠排除法、审动画（场景2）靠猜，均仅 med 置信。修复=补动画专项条目让泛化变精准。
- 域边界「不用于」条款本轮基线验证正常（场景5 debounce 函数正确转 ai-coding），未动。
- 「再定风格」表本轮未动——基线未暴露风格路由缺陷，避免无证据漂移。

## [v1.3.0] - 2026-07-22

### Added

- description 扩触发词（登录页 / 做个界面 / 写个界面）+ 版本戳 `<!-- v1.3.0 -->` + 视觉任务优先于编码路由条款（即使同时提到写代码，设计方向先行）。
- 新增「触发门禁」3 行：派生前输出相关性 YES/NO + 存在性 + fallback（依据：社区实测无门禁 skill 触发率 0-20%，forced-eval 模式可达 84%）。
- 组合顺序补跨界交接显式枚举三类（编码 / 配图 / 写作），不用「其他/等」范畴词（依据：Superpowers issue #1301 范畴词禁令被放大解释）。
- 文末加 HTML 注释路由表门禁：删除条目前必须引用真实误路由事故或官方变更证据（防无证据漂移）。
- 新增 `test-prompts.json`（7 条：正向 4 + 跨界转介 3）。
- 新增 `references/MAINTENANCE.md`。

### Rationale

- 2026-07-22 RED 基线（子代理无正文加载）：「登录页极简风」「落地页+写码」两个视觉请求第一跳全被 ai-coding-guide 抢走。根因是 ai-coding-guide 在全局 CLAUDE.md §1.0 的优先级 + 本 description 无「视觉优先」条款。修复手段：description 加优先级条款 + ai-coding-guide 侧加「不用于」清单，双保险。
- 路由表本身（先定阶段/再定风格/重叠裁决）本轮未动——基线测试未暴露缺陷，避免无证据漂移。
