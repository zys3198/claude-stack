# 前端视觉子路径细节

本文件只在 `routing.md` Step 1 命中「前端视觉」分类时展开。`routing.md` 只留决策骨架一行；本文件存完整五分支 / AskUserQuestion / 组合顺序 / 验证。

**触发：** Step 1 命中「前端视觉」（做/改页面视觉、UI/动画库选型、动效；含「页面/界面/UI/落地页/登录页」且要视觉产出）→ 读本文件，按阶段走分支。

---

## 决策骨架（routing.md 已留）

**阶段先于风格。** 先判交付物/阶段（方向未定 / 提质 / 实现 / 动画 / 特殊产物），再选工具。方向类决策先问用户，不让设计 skill 自行拍脑袋。

## 五分支

- **方向未定**（新页面、没设计稿、要视觉方向）→ 决策点先问：给 2-3 个方向选项问用户（或问有无参考/品牌约束），**不让设计 skill 自行拍脑袋定方向**；用户选定后 → `hallmark`（新页面/redesign/URL 抽取，反 AI 大路货）
- **已有页面提质**（页面太丑、去 AI 味）→ `impeccable`（先审现有 AI 味再改）/ `hallmark`（要 audit/redesign 时）
- **实现**（方向已定、只写组件/代码）→ 按项目栈直接实现（可跑 `inspect_context.py` 拿 manifests 证据定栈）；**组件库原则：先检查项目现有依赖并复用**，Vue 项目已采用或点名才走 `shadcn-vue-guide`
- **动画动效**（做/改/审动画、加动效、手感不对）→ `emil-design-eng`（综合/审）/ `improve-animations`（全库改）/ `find-animation-opportunities`（找该动哪）；专用严审由用户显式运行 `review-animations`（当前会话可见才可运行）
- **风格叠加**（可选，点名才套）→ `apple-design`（Apple 风格参考）等；默认 1 个阶段主路径 + 可选 1 个风格叠加，不堆叠
- **特殊产物** → claude.ai artifact 用内置 Artifact 工具；视频产物无会话已验证默认路径（手动实现）

## 负边界

- `design-an-interface` 是**模块 API/interface 设计**，不进视觉路径
- 不涉及视觉方向的纯前端工程问题走编码通用分支
- `frontend-design`（官方插件）为存活独立件，未被本子路径点名；要用由用户显式调用

## 组合顺序

定方向 → 实现 → （可选提质）；串行不并联。

## 验证

需要浏览器行为、可访问性或视觉证据 → 实现后串联 `browser-testing-with-devtools`（chrome-devtools MCP）；需要自动化流程驱动（表单填写/多步交互/截图采集）→ `playwright`。两者互补：前者偏验证取证，后者偏自动化，不另建 router。

---

## AskUserQuestion

- A: 先选视觉方向（给 2-3 个方向选项，推荐）
- B: 已有方向/参考，直接实现
- C: 已有页面提质（进 `impeccable`）

## Fallback

- 用户说「直接做/你定」→ 跳过方向问询，走 `hallmark`（新页面）或 `impeccable`（提质）默认
- `hallmark` / `impeccable` 不在 → 手动给方向选项 + 按项目栈直接实现，收尾自查 AI 味

<!-- 吸收自 ai-coding-guide v1.9.0 references/frontend-visual.md，2026-08-18：验证环节补 playwright（ticket 02 拍板） -->
