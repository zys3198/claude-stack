---
name: frontend-guide
description: Use when 用户要做 UI、前端页面、组件、落地页、视觉设计、改样式、升级界面质感、做/改/审动画动效，且没明确点名具体前端/设计 skill。是前端/视觉域的开工路由器，路由到 design-taste-frontend / frontend-ui-engineering / shadcn-vue-guide / redesign-existing-projects / imagegen-frontend-* / design-an-interface / 各风格预设，动画动效类路由到 emil-design-eng / review-animations / improve-animations / find-animation-opportunities / animation-vocabulary / apple-design / pick-ui-library。触发词：做个页面、登录页、落地页、UI、前端、组件、界面设计、改样式、页面太丑、升级质感、网站设计、写个界面、做个界面、动画、动效、丝滑、回弹、过渡、转场。含"页面/界面/UI/落地页/登录页"或动画动效诉求且要视觉产出时优先于编码路由，即使用户同时提到"写代码/做完顺便写"——设计方向先行，实现阶段本路由已覆盖。不用于：纯写代码逻辑无界面（走 ai-coding-guide）、画图配图（走 drawio-chart）、写文章（走 article-writing-guide）。<!-- v1.5.3 -->
---

# 前端路由指南（Claude Code）

## 定位

前端/视觉域的**开工路由器**，对齐 `ai-coding-guide`（编码）、`article-writing-guide`（写作）、`learning-guide`（学习）。只回答「这个前端任务先走哪个 skill、按什么阶段组合」，不认领下游执行权威。

**不替代默认栈**：CLAUDE.md §6 已定前端默认 `shadcn/ui` + `npx shadcn@latest init`（Vue 项目走 `shadcn-vue-guide`）。本指南管的是**设计阶段裁决和重叠 skill 选谁**，不管基础组件库选型——那是已定的默认。

**质量底线：** skill 名先查当前会话可用清单再推荐；会话里没列出的当不存在，给 fallback。

## 触发门禁（路由前先跑，防编码域抢单）

派生前先输出 3 行门禁（目标是把「视觉任务被编码 router 抢走」扼杀在派生前）：

```
frontend-guide 相关？ YES/NO —— <一句理由>
当前会话是否存在？ YES/NO —— <可用清单依据>
若 NO → fallback： <design-taste-frontend / 手动阶段裁决>
```

## 开工问询（路由入口）

触发门禁后、定阶段前，先跑开工问询。**逐个问，一次一个，每个给推荐答案**；能从代码库/设计参考查到的不问用户。

**触发：** 需求模糊/缺背景/没明说模式 -> 走；明确任务/机械任务/用户说"直接做" -> 跳过，走默认。

**问询顺序：**
1. **模式**：这次 coach（我练）/ pair（一起想）/ driver（直接做讲为什么）？**按任务类型给推荐**——想练设计判断/该你会的前端核心 → 推荐 coach；不熟的设计方向 → 推荐 pair；有视觉产出+没说学习/机械改动 → 推荐 driver
   - coach：你想练设计判断时，你先给方向/参考/初判，AI 纠偏 + 对照标杆；**无设计背景或给不出初判时 coach 退化为 pair（决策点先问），不空转**
   - pair：不熟的设计方向，AI 给 2-3 方案你定
   - driver：有视觉产出+没说学习，AI 直接做，收尾讲设计决策 why
   - 用户卡壳给不出判断 -> AI 递参考判断，不死等
2. **背景**（模糊时才问）：为什么做/什么场景/谁触发/有无参考/品牌约束；能查的不问
3. -> 进「先定阶段」

**例外（不问，直接 driver）：** 机械改动（改文案/颜色/间距）、已指名标杆风格、用户说"直接做"。

**与现有机制分工：** 开工问询管 why（背景）+ how（模式）；「先定阶段」管 which（方向）；决策点先问管风格方向。不重叠。

## 环境自检

1. 只看当前会话 `Available skills` 为已证实。
2. 顶层独立 skill：`~/.claude/skills/`（cc-switch 同步，源 `~/.cc-switch/skills/`）。
3. reminder 没列出 ≠ 不存在；关键推荐前按磁盘复核。
4. 生态缺失 → 跳过给替代，不硬推。

## 先定阶段（核心裁决）

前端任务先问：处于哪个阶段？阶段决定主路径。

| 阶段 | 用户信号 | 主路径 | 说明 |
|---|---|---|---|
| **定方向** | 新做页面、没设计稿、要视觉方向 | `design-taste-frontend`（默认） | 读简报推断设计方向，反 AI 大路货 |
| **出参考图** | 要先看效果图再写码 | `imagegen-frontend-web`（网页）/ `imagegen-frontend-mobile`（App） | 先生成设计参考图 |
| **多方案探索** | 想看几个差异方案再定 | `design-an-interface` | 并行子代理出多个方案 |
| **实现** | 方向已定、要写生产级 UI | `frontend-ui-engineering` | 工程实现兜底 |
| **升级现有** | 页面太丑、要去 AI 味、提质 | `redesign-existing-projects` / `impeccable` | 审现有→改 |
| **动画动效** | 做/改/审动画、加动效、不够丝滑、回弹/过渡手感不对、效果叫什么 | `emil-design-eng`（综合默认）/ `review-animations`（审）/ `improve-animations`（改全库）/ `find-animation-opportunities`（找该动哪）/ `animation-vocabulary`（命名） | 动画专项，按子意图分流（见重叠裁决） |
| **特殊产物** | claude.ai artifact / 海报图 / 视频 | `web-artifacts-builder` / `canvas-design` / `hyperframes` / `remotion` | 非网页交付物 |

## 再定风格（叠加，可选）

方向阶段可叠加风格预设。**默认不指定就用 `design-taste-frontend` 自己推断**，用户点名风格才套：

| 风格 | skill |
|---|---|
| 极简编辑风、暖单色、bento 栅格 | `minimalist-ui` |
| 工业粗野、瑞士排版+军事终端 | `industrial-brutalist-ui` |
| 高端 agency 质感 | `high-end-visual-design` |
| 预设主题包（slides/docs/落地页） | `theme-factory` |

## 重叠裁决（同质 skill 选谁）

| 场景 | 选 | 不选 | 理由 |
|---|---|---|---|
| 定视觉方向 | `design-taste-frontend` | `frontend-design` | 现行默认 |
| 要" agency 级精确规范"（字体/间距/阴影数值） | `high-end-visual-design` | `design-taste-frontend` | 它给确切设计 token 而非方向 |
| 已有项目提质 | `redesign-existing-projects` | `design-taste-frontend` | 它先审现有 AI 味再改 |
| 组件库使用 | `shadcn-vue-guide` | 通用设计 skill | §6 默认栈，专用指南 |
| 动画综合判断/品味 | `emil-design-eng` | 通用设计 skill | 动画该不该动、easing 对错的领域专长 |
| 审已有动画 | `review-animations` | `redesign-existing-projects` | 严审动画规则，非整体重设计 |
| 全库动画改造 | `improve-animations` | `emil-design-eng` | 出优先级审计+可执行计划，非单点 |
| 找该动哪/该不该动 | `find-animation-opportunities` | `improve-animations` | 只读提案，不改代码；找点非审现有 |
| 动画命名/术语 | `animation-vocabulary` | `emil-design-eng` | 反查术语词表，不设计不实现 |
| 选动画/UI 库 | `pick-ui-library` | 手搓或乱装包 | 作者信任清单选型 |

## 组合顺序

典型全链路：**定方向 → （可选出参考图）→ 实现 → （可选升级）**。

- 串行不并联：定完方向才实现。
- 少叠加：默认 1 个阶段主路径 + 可选 1 个风格预设，不堆叠。
- 决策点先问（默认问、可直接做）：定方向/定风格这类有多种合理走向的决策，先给 2-3 个选项问用户，不让设计 skill 自行推断；用户说"你定/直接做"则跳过走默认。
- 参与度（开工问询定，见上）：coach 你先给设计判断 / pair AI 给方向选项你定 / driver AI 直接做讲设计决策 why；机械改动（改文案/颜色/间距）直接 driver；模式推荐按任务类型，不一刀切 coach。
- 跨界交接（只此三类，显式枚举防范围扩散）：写代码逻辑交 `ai-coding-guide`；配图交 `drawio-chart`；写文章交 `article-writing-guide`。

## 反模式

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 用户就说"做个登录页" | 先给 2-3 个方向选项问偏好（或问有无参考/品牌），再进 `design-taste-frontend`；用户说"你定/直接做"才让它推断 | 不声不响直接让 design-taste-frontend 拍脑袋定方向，或一上来套 3 个风格 skill |
| 用户点名"极简风" | `minimalist-ui` | 还走 design-taste-frontend 推断 |
| 老项目嫌丑 | `redesign-existing-projects` 先审 | 当新做重定方向 |
| 组件怎么装 | `shadcn-vue-guide` | 用通用设计 skill 答安装 |
| skill 缺失 | 给手动 fallback | 推荐不存在的 |
| 分类不清/跨域重叠 | 走共享兜底 [`ai-coding-guide/references/fallback-template.md`](../ai-coding-guide/references/fallback-template.md) | 在本 guide 重复写跨域反问 |

## 与兄弟路由器

- 编码逻辑 → `ai-coding-guide`
- 写作 → `article-writing-guide`
- 学习 → `learning-guide`
- **前端/视觉 → 本指南**

四域各管一边，跨界串行交接。

<!-- 路由表门禁：上表「先定阶段/再定风格/重叠裁决」条目由人工维护；删除任何条目前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）。v1.4.0 -->
