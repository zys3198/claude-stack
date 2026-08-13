---
name: ai-coding-guide
description: Use when user asks which skill/tool/ecosystem to use inside Claude Code, how Superpowers/Matt Pocock skills/ponytail/ecc (or any installed plugin) differ or compare, which fits a task, how to combine them, when a new plugin/skill is installed, or when external AI-coding practices should be evaluated for this guide. 本 skill 是 Claude Code 编码域开工路由器（含前端视觉任务判定）。中文触发：用哪个工具、X和Y区别/冲突吗、有什么工具能用、刚装了X插件、X不能用了、SP/Matt Pocock skills 怎么选、哪个更好、该用什么、怎么配合、这篇文章/做法能不能优化进指南；页面/界面/UI/落地页/登录页的视觉方向与实现也走本路由（前端视觉子路径）。不用于：中文技术文章写改审（走 article-writing-guide）、学习调研（走 learning-guide）。<!-- v1.5.0 -->
---

# AI 编码路由指南（Claude Code）

## 定位与质量标准

**定位：** 本 skill 是 Claude Code 当前环境下的**开工路由器**。它先回答「这类任务先走哪条流程、该用哪个 skill、哪些能力要组合、哪些质量闸门必须保留」。生态地图、质量闸门、学习陪跑都服务这个开工路由：

1. **开工路由（主目标）**：把用户意图分到正确流程，少选错工具。
2. **生态地图**：解释 Superpowers / ECC / ponytail / Matt Pocock / lean-ctx 等边界和组合方式。
3. **质量闸门**：让 review / verify / TDD / 提交前检查各归其位，防假完成、误提交、错用危险 fallback。
4. **学习陪跑**：用户想练 AI coding 判断力时，路由到 `ai-coding-coach`，让用户先想方案，助手纠偏和复盘。

它不认领下游 skill 的完整执行权威；执行纪律以下游 skill 与项目级 `CLAUDE.md` 为准。

**域边界（显式枚举，防范围词放大）：** 以下两类任务不在本路由范围，命中即转介，不展开分类流程——
- 中文技术文章的写/改/审/润色/发布 → `article-writing-guide`（Step 2「文档写作」分类仅作为本域的细分确认入口，最终仍交写作总路由）。
- 学习/调研/吃透/做教程 → `learning-guide`。
- **教程裁决**（两域都可能命中时）：「给自己学会」或作为学习产物 → `learning-guide`；「面向读者发布的教程文章」→ `article-writing-guide`。
- **前端视觉任务**（含「页面/界面/UI/落地页/登录页」且要视觉产出）→ **留在本路由**，走 Step 2 前端视觉子路径（用户同时提到"写代码"也算，设计方向先行）。纯前端工程问题（不涉及视觉方向）走编码通用分支。
- 反例（留在本路由）：纯后端 API、CLI 工具、构建/调试/审查/提交、工具选型问答。

**质量底线：**
- **准确**：skill 名、命令名、目录路径、插件归属先查当前会话或本地文件，再写结论。
- **AI 可读**：主文件只放路由和最小速查；长解释外置到 [`references/ecosystems.md`](references/ecosystems.md)。
- **可进化**：发现死引用、错归属、错默认路径时当场修，并同步 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)。
- **默认值先于菜单**：各分类 AskUserQuestion 是例外而非默认；默认路径明确、用户点名、或说「直接做」时直接执行不问。每分类至多一次提问。

## 触发门禁（分类前先跑，防误路由）

Step 1 分类前先输出 3 行门禁：

```
域归属： 编码（含前端视觉）/ 写作 / 学习 —— <一句理由>
ai-coding-guide 在当前会话？ YES/NO
若域归属非编码 → 转介对应 router，不进 Step 1
```

## 开工问询（路由入口）

触发门禁后、分类前，先跑开工问询。**逐个问，一次一个，每个给推荐答案**；能从代码库/文档查到的不问用户。

**触发：** 需求模糊/缺背景/没明说模式 -> 走；明确任务/机械任务/用户说"直接做" -> 跳过，走默认。

**问询顺序：**
1. **模式**：这次 coach（我练）/ pair（一起想）/ driver（直接做讲为什么）？**按任务类型给推荐**——该你长期持有的核心技能/有学习点 → 推荐 coach；不熟的库/偶用模式/要权衡 → 推荐 pair；一次性/胶水/样板/明确交付 → 推荐 driver
   - coach：该你长期持有的核心技能，你先给判断，AI 纠偏 + 对照标杆 + 复盘 why
   - pair：不熟的库/偶用模式/要权衡，AI 给 2-3 选项你定
   - driver：一次性/胶水/样板，AI 直接做，收尾 why-review
   - 用户卡壳给不出判断 -> AI 递参考判断，不死等
2. **背景**（模糊时才问）：为什么做/什么场景/谁触发/约束；能查的不问；**Step 0.7 已覆盖的缺口（复现步骤、错误原文、审查对象、提交范围等）此处不重复问，留给 Step 0.7**
3. -> 进 Step 1 分类

**例外（不问，直接 driver）：** 机械任务（1-2 步单文件/改文案/格式）、明确 bug、已指名标杆；用户说"直接做"。

**与现有机制分工：** 开工问询管 why（背景）+ how（模式）；决策点先问管 which（方向 A/B/C）；Step 0.7 管 what（缺口）。不重叠。

## 环境自检

触发本 skill 后，先按 Claude Code 当前环境复核可用性：

1. **先看当前会话可用清单**：只把当前 `Available skills` / `Available tools` / `Available agent types` 视为已证实；历史摘要、memory、prior-session 内容不算可用性证据。
2. **再看顶层独立 skill**：`~/.claude/skills/`（本机常由 cc-switch 同步，源目录通常是 `~/.cc-switch/skills/`）。
3. **再看插件附带 skill**：`~/.claude/plugins/cache/*/skills/`；插件是否启用以 `settings.json` 的 `enabledPlugins` 为准。
4. **关键提醒**：reminder 没列出 ≠ 一定不存在；关键推荐前要按磁盘再复核一次。

- 生态整体缺失 → 推荐路径里跳过该生态，改给当前已装替代。
- 生态部分缺失 → 正常推荐主路径，但写清 fallback。
- 不自检就推荐不存在的工具 = 最严重的路由失败。

**路径角色标记：** 本文各分类的推荐分两种——**直达路径**（当前会话可见的裸 skill / 内置命令，直接走）与**条件路径**（插件 skill，标记「条件」：仅在当前会话可调用清单中出现时才走，否则用该分类 Fallback，不伪装直达）。判定依据 = 环境自检第 1 条。

**角色分层（不可直达清单）：** 以下只可被流程内部引用或作为参考层，**不作为用户第一跳**——`gitnexus-guide`（GitNexus 家族参考层，其内部路由到兄弟 skill）、`animation-vocabulary`（动画术语参考层，前端子路径内部查阅用）。

## 证据门槛

- **本地已证实**：当前会话可见、本机目录可见、当前仓库文件可见。
- **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
- **经验判断**：默认建议、经验排序、惯用主路径；要写成推荐，不写成定律。
- **证据不足**：影响主推荐结论时停下来问用户；不影响则标「不确定」或删除。

## 轻量迁移闸门 & 重机制黑名单

外部 AI 编码实践要吸收进本指南时，先过迁移闸门（只吸收路由规则，不承接项目流水线）；重机制（8 阶段流水线、wiki 三级库、TECH_SPEC 模板等）不内置。详见 [`references/cheatsheet.md`](references/cheatsheet.md) §轻量迁移闸门 / §重机制黑名单。

---

## 交互决策流程

🔴 **CHECKPOINT · 🛑 STOP**：先分类 → 再推荐。只有路径选择会改变成本/风险/产物且请求无法判断时，才用 AskUserQuestion A/B/C 收口并停；目标明确、用户点名 skill/slash command、或用户说「直接做 / 别问」时，直接走默认路径。AskUserQuestion 不可用时，用一句自然语言问同一个关键问题。

### Step 0：组合顺序

1. **点名优先**：用户点名某个已装 skill/slash command → 先用它；若与安全、不可逆操作或当前环境冲突，先说明冲突再停。
2. **插件能力走条件路径**：`superpowers:*` / `ecc:*` / `ponytail:*` / `commit-commands:*` / `understand-anything:*` 等插件条目，只在当前会话可调用清单中出现时才走（环境自检第 1 条）；没有则走各分类的 Fallback，不把插件写成默认直达。
3. **流程优先**：同一任务命中多个 skill 时，先主路径，再专项型（审查/安全/文档），不先按插件名倒推任务。
4. **少叠加**：默认 1 个主路径 + 必要 1 个专项 + 收尾验证；不要把所有相关 skill 一次性全调用。高风险审查、构建失败、外部发布例外。
5. **能组合就组合**：用户同时问结构和调用链、实现和验证、提交前确认时，按顺序串联能力，不让用户在互补能力之间二选一。
6. **收尾固定**：产生产品代码改动后才进横切收尾；纯理解、纯审查、纯文档不强行 verify。

### Step 0.5：路由输出契约

默认输出 6 行，除非用户要求展开：

```markdown
分类：<Step 1 分类>
主路径：<第一个要调用的 skill / slash command / agent>
组合：<必要附加能力；没有写"无">
参与度：<coach / pair / driver -- 一句理由>
闸门：<TDD / review / verify / 提交确认 / 无>
下一步：<直接执行 / 问 1 个关键问题 / 等用户确认>
```

- 解释只补"为什么不是另一路径"的关键一句。
- 用户问生态对比时，再展开 `references/ecosystems.md`。
- 用户进入学习陪跑时，输出先改为 `模式 / 你先做什么 / 我怎么纠偏 / 收尾复盘什么`。

### Step 0.6：风险 → 闸门矩阵

| 风险 | 触发 | 必要闸门 |
|---|---|---|
| 低 | 文案、样式微调、单文件机械改 | 最小检查；不强制 review / verify |
| 中 | 功能逻辑、bug 修复、重构 | 失败测试或最小复现 → 实现 → 相关 test/lint/build → 必要 review |
| 高 | auth、权限、DB schema、迁移、支付、外部 IO、安全边界、架构 | 计划/设计确认 → TDD/复现 → 专项 reviewer + security-review → verify/证据 |
| 不可逆/外发 | commit、push、PR、删除文件、清理未跟踪文件、密钥、数据库写操作 | 先展示范围/状态/diff 或删除清单，得到用户确认后才执行 |

### Step 0.7：最小信息清单

开工问询已问过的背景（为什么做/什么场景/谁触发）此处不重复收；本清单只补任务级技术缺口。

| 任务 | 只问这些缺口 |
|---|---|
| 构建错误 | 语言/框架、执行命令、完整错误、最近改动 |
| 调试 bug | 复现步骤、期望/实际、错误原文、最近改动 |
| 审查代码 | 对象：当前 diff / PR / 分支 / 文件 / 代码块；风险域 |
| 验证生效 | 要证明的行为、入口/命令、验收信号 |
| 提交/PR | 提交范围、是否 push/开 PR、目标分支 |
| 学习陪跑 | 想练：方案设计 / debug / review / 工具选择；希望我教练还是直接做 |
| 多会话工作 | 是否跨多个会话、需要什么显式交接物（计划/状态文件）、断点续跑方式 |

### Step 0.8：参与度模式（coach/pair/driver）

三模式是**路由词汇**，不是下游 skill 的执行定义。开工问询已在路由入口定好模式（按任务类型推荐，见开工问询第 1 条），此处只做两件事：一、把词汇带上路由输出契约（Step 0.5）和「学习型开发」分类；二、指向真正拥有执行定义的下游 skill——进 `ai-coding-coach` 后，协作行为以该 skill 为准（partner-coach / coach / engineer），本表不再重复定义。

| 模式 | 触发 | 路由动作 |
|---|---|---|
| coach | "我先想""你别直接给答案""训练判断力" / 默认（有学习点） | 路由到 `ai-coding-coach`；进 coach 后按该 skill 的 coach mode 执行 |
| pair | "一起想""帮我权衡" | 助手给 2-3 个可选路径和取舍，用户定方向后按实际分类执行 |
| driver | "直接做，但讲为什么" / 机械任务 | 助手按工程师模式执行，收尾用 3 行复盘关键判断 |

### Step 1：提取用户意图

| 信号 | 分类 | 示例 |
|---|---|---|
| 开发新功能 | 开发新功能 | "写个登录""加个 API""改个后端服务"（含『页面/界面/UI/落地页/登录页』且要视觉产出 → 前端视觉子路径，见 Step 2） |
| 做/改页面视觉、UI/动画库选型、动效 | 前端视觉 | "做个登录页""页面太丑要提质""选个 UI 库""加个动画"（设计方向先行，实现阶段本分类已覆盖） |
| 学习型 AI 编码 | 学习型开发 | "我想自己能力提高""别让我依赖 AI""和我一起想方案""我先想你纠偏" |
| 判级/暴露未知 | 判级/暴露未知 | "暴露未知""判级""这个需求我没思路""让 AI 采访我""反考我""出题验收""开工前先把盲点摊出来" |
| 已有需求/PRD | 有需求文档 | "根据这份 PRD 实现""需求文档见文件 X" |
| 想读懂代码 | 理解代码 | "这库怎么结构""X 怎么工作""谁调用了 Y" |
| 审查代码 | 审查代码 | "帮我 review""审查这段代码" |
| 改完要验证 | →横切收尾（Step2 顶部） | "改完了验证下""确认真生效""别假完成" |
| 调试 bug | 调试 bug | "报错了""这个 bug 怎么回事" |
| 要重构/简化 | 重构/简化 | "帮我重构""简化这段""代码太乱" |
| 快速小改 | 快速改动 | "改个按钮文案""小修一下" |
| 构建错误 | 构建错误 | "build 报错""类型错误" |
| 文档写作 | 文档写作 | "写文章""润色""审文档" |
| 外部 AI 编码实践 | 路由指南维护 | "这篇文章能不能优化进指南""把某个 AI 编码流程吸收到 ai-coding-guide""某做法要不要加进路由" |
| 审查/优化 guide skill | 路由指南维护 | "审查这个 guide""优化路由 skill""guide 体检""误路由排查""新建一个路由器 skill" |
| 要提交/收尾 | 提交/收尾 | "帮我提交""发个 PR""这分支收尾" |
| 知识收尾/同步 | 知识收尾 | "同步一下""整理文档""更新记忆""这个阶段做完了""新人能直接上手""阶段完成后同步 docs / README / AGENTS/CLAUDE / memory" |
| 循环任务 | 循环任务 | "每 5 分钟检查""持续跑到满足条件" |
| 纯对比/选型问题 | 了解指南 | "SP 和 agent-skills 区别""该用哪个工具" |
| 编码域查最近动态/社区 | 编码域调研 | "最近 React 有什么更新""K8s 社区最近在讨论什么""Next.js changelog 看一眼" |

**优先规则：**
- 带明确开工信号的"怎么选"问题，不走泛泛介绍；按任务分类直接给 A/B/C。
- 只有纯抽象对比、没有开工信号时，才走「了解指南」。
- **信号重叠裁决**：带 PRD/需求文档字样 →「有需求文档」优先于「开发新功能」；build/compile/类型错误 →「构建错误」优先于「调试 bug」（调试=运行时/逻辑错）；「想改代码」优先于「想读代码」（重构优先于理解，除非用户明说"先看懂"）；「改样式/提质感」优先判前端视觉（页面提质走视觉子路径，纯文案微调走快速改动）。
- **混合意图裁决（tie-breaker）**：单一请求跨多域时按「最终交付物/目标」定归属，不猜——「代码+写作」看交付物（交付文章→`article-writing-guide`，交付代码→留本路由）；「修 bug+求理解」看目标（要修好→留本路由「调试 bug」，要学会了→`learning-guide`）；「做页面+写代码」→ 前端视觉子路径（设计方向先行）。判不出 → 按 Step 4 问，不擅自二选一。
- **决策点先问（默认问、可直接做）**：涉及方向/方案/栈选型等有多个合理走向的决策点时，先给 2-3 个选项问用户，不让下游 skill 自行推断；用户说「直接做/你定/别问」则跳过，走默认路径。

### Step 2：匹配推荐路径

> 🔴 **横切收尾（所有产生产品代码改动的分类通用）**：开发新功能 / 前端视觉 / 调试 bug / 重构简化 / 快速改动 / 构建错误 完工前，先按运行时表面验证：有可驱动流程 → 用 `run` 驱动真实流程验证；无运行时表面 → 跑相关 build / lint / test / check。随后组织验证证据（`superpowers:verification-before-completion` 为条件路径，当前会话可调用才用；不可用时手写证据清单：行为、命令、输出），再宣布完成。审查代码 ≠ 完工验证：review 是人读挑错，验证是跑起来证行为对，互补。**用户直接说「帮我验证/确认生效」→先确认最近改动属哪类改动，再走本检查点；若还要求提交，验证通过后继续进入「提交/收尾」。**

分类: 开发新功能
- 默认主路径 → 开工问询 + Step 0.7 缺口收齐 → 轻量确认目标：范围小直接实现；跨模块/要设计先给实现计划（手动拆 4-6 切片 + PLAN.md，按 `code-change-workflow` §3）确认后实现
- 需求很模糊 → 先 `expose-unknowns` 判级或 AskUserQuestion 澄清，再回本分类
- 条件路径（当前会话可调用才走）：`superpowers:brainstorming`（澄清+方案探索）、`superpowers:writing-plans`（计划）、`superpowers:test-driven-development`（TDD）、`ponytail:ponytail`（最小实现）
- 复杂/高风险改动 → `code-change-workflow`（改前/改中/改后清单 + Verify 分级）

AskUserQuestion:
- A: 先给实现计划确认（跨模块/要设计时，推荐）
- B: 直接实现（范围小/明确）
- C: 先判级澄清需求（`expose-unknowns`）

Fallback:
- 需求仍模糊 → 手动单问单答压清问题（目标/约束/验收），再回本分类
- 用户明确讨厌重流程 → 降到最小改动，边做边确认
- 仍失败 → AskUserQuestion「你的真实目标是什么？」重分类

分类: 前端视觉
- 先判交付物/阶段（阶段先于风格）：
  - **方向未定**（新页面、没设计稿、要视觉方向）→ 决策点先问：给 2-3 个方向选项问用户（或问有无参考/品牌约束），**不让设计 skill 自行拍脑袋定方向**；用户选定后 → `hallmark`（新页面/redesign/URL 抽取，反 AI 大路货）
  - **已有页面提质**（页面太丑、去 AI 味）→ `impeccable`（先审现有 AI 味再改）/ `hallmark`（要 audit/redesign 时）
  - **实现**（方向已定、只写组件/代码）→ 按项目栈直接实现；**组件库原则：先检查项目现有依赖并复用**，Vue 项目已采用或点名才走 `shadcn-vue-guide`
  - **动画动效**（做/改/审动画、加动效、手感不对）→ `emil-design-eng`（综合/审）/ `improve-animations`（全库改）/ `find-animation-opportunities`（找该动哪）；专用严审由用户显式运行 `review-animations`（当前会话可见才可运行）；术语命名内部查阅 `animation-vocabulary`（参考层，不作第一跳）
  - **风格叠加**（可选，点名才套）→ `apple-design`（Apple 风格参考）等；默认 1 个阶段主路径 + 可选 1 个风格叠加，不堆叠
  - **特殊产物** → claude.ai artifact 用内置 Artifact 工具；视频产物无会话已验证默认路径（手动实现；候选工具去留待全库审计报告用户拍板）
- 负边界：`design-an-interface` 是**模块 API/interface 设计**，不进视觉路径；不涉及视觉方向的纯前端工程问题走编码通用分支
- 验证：需要浏览器行为、可访问性或视觉证据 → 实现后串联 `browser-testing-with-devtools`（chrome-devtools MCP 本机已配置），不另建 router
- 组合顺序：定方向 → 实现 → （可选提质）；串行不并联

AskUserQuestion:
- A: 先选视觉方向（给 2-3 个方向选项，推荐）
- B: 已有方向/参考，直接实现
- C: 已有页面提质（进 `impeccable`）

Fallback:
- 用户说「直接做/你定」→ 跳过方向问询，走 `hallmark`（新页面）或 `impeccable`（提质）默认
- `hallmark` / `impeccable` 不在 → 手动给方向选项 + 按项目栈直接实现，收尾自查 AI 味

分类: 学习型开发
- 默认主路径 → `ai-coding-coach`
- 模式已由「开工问询」定（按任务类型推荐），此处不重复问；按已定模式进 `ai-coding-coach`
- 与代码改动叠加时：先用 `ai-coding-coach` 定协作模式，再按实际任务进入开发新功能 / 调试 bug / 重构简化 / 快速改动
- 高风险或用户明确要练判断 → coach；赶交付 → driver 但保留 why-review

AskUserQuestion:
- A: 进 `ai-coding-coach`（按开工问询定的模式，推荐）
- B: 先看这套协作方式怎么工作
- C: 跳过 coach 直接进开发分类（收尾仍 why-review）

Fallback:
- `ai-coding-coach` 不在 → 手动执行：用户先给第一版方案，助手纠偏，对照项目标杆/官方做法，最后让用户讲 why

分类: 判级/暴露未知
- 默认主路径 → `expose-unknowns`（判四象限 → 按级选技巧 → 任务后反考）
- 判「未知的已知/未知的未知」需采访澄清 → `expose-unknowns` 内嵌路由到 `superpowers:brainstorming`（条件路径，不可用则手动采访），不重复展开
- 只问四象限概念、不开工 → 直接解释，不强拉进流程

AskUserQuestion:
- A: `expose-unknowns`（默认）
- B: 只看判级方法说明
- C: 跳过判级直接开工

Fallback:
- `expose-unknowns` 不在 → 手动执行 `code-change-workflow` skill §1.1「动手前先判级」一行规则
- 需求模糊但用户未提判级/暴露词 → 仍走「开发新功能」的澄清步骤，不抢路由

分类: 有需求文档
- 默认主路径 → 手动拆 4-6 切片 + PLAN.md（按 `code-change-workflow` §3），确认后实现
- 用户只想先整理需求项 → `to-prd` / `to-issues`
- 条件路径：`superpowers:writing-plans`（当前会话可调用才走）

AskUserQuestion:
- A: 先拆切片出计划
- B: 先整理需求项（`to-prd` / `to-issues`）

Fallback:
- 用户只要结论不要计划 → 直接回答，不强拉进计划流程

分类: 理解代码
- 日常查结构/看某处实现 → `lean-ctx`（成本最低，先走）
- 调用链/影响范围/谁调用谁 → `gitnexus-exploring`
- 同时问结构 + 调用链 → `lean-ctx` 后接 `gitnexus-exploring`，不让用户二选一
- 条件路径：大范围建模/架构全貌 → `understand-anything:understand`

AskUserQuestion:
- A: 先 `lean-ctx`
- B: `gitnexus-exploring` 查影响
- C: 大范围建模（条件路径 `understand-anything:understand`）

Fallback:
- `lean-ctx` 不可用 → 原生搜索 + 精读文件
- `gitnexus-*` 不可用 → 继续用 `lean-ctx` 聚焦读取

分类: 审查代码
- 先定对象：代码块 / 当前 diff / 指定文件 / PR / 分支
- **轻量审查**（快速、有会话上下文）：当前 diff / PR / 分支 / 指定基线对比 → `code-review`（内置命令：commit / 分支 / tag / main / HEAD~N）
- 指定文件 / 代码块 → 通用 Code Reviewer agent
- 高风险（auth / DB / 架构 / 安全） → 轻量 reviewer + `security-review`（内置命令）+ 通用 Code Reviewer agent 双审，防"自己审自己"盲区
- 条件路径：`ecc:python-review` / `ecc:react-review`（语言专项 reviewer）、`ecc:security-review`、`ocr review` / `/open-code-review:review`（独立重量审查）、`superpowers:requesting-code-review`（实现完成后请求复核）

AskUserQuestion:
- A: 审当前 diff / 分支 / PR（轻量，会话内）
- B: 审指定文件 / 代码块
- C: 安全/高风险审查

Fallback:
- 对象不明确 → 先问「贴代码块、给文件路径，还是审当前 diff？」
- 专项 reviewer 不在 → 用通用 Code Reviewer agent 或 `code-review`
- 仍失败 → 停止审查，先问意图（审查/调试/当参考）再走对应分类

分类: 调试 bug
- 默认主路径 → `code-change-workflow` §2 调试工作流：先补失败测试/最小复现 → 定位根因（检查所有调用方）→ 修复 → 验证
- 条件路径：`superpowers:systematic-debugging`（当前会话可调用才走）
- 定位后需要修代码 → 修复 + 横切收尾

AskUserQuestion:
- A: 进入系统化调试（复现→定位→根因）
- B: 我只要你直接判断

Fallback:
- 用户不给复现信息 → 先收错误信息、触发条件、最近改动（Step 0.7）

分类: 重构/简化
- **前置**：行为未理解先走「理解代码」
- 默认主路径 → 手动列坏味道 + 逐步改，每步跑测试（原则源：项目 CLAUDE.md §2.3 简洁优先 / §2.4 精准修改）
- 会话/阶段收尾、文档/记忆/README/AGENTS 同步清理 → `neat-freak`（知识库洁癖，不替代代码重构）
- 复杂/高风险重构 → `code-change-workflow`（改前/改中/改后清单 + Verify 分级）

AskUserQuestion:
- A: 手动小步改（行为不变，推荐）
- B: 复杂/高风险，走 `code-change-workflow` 全流程
- C: 先出重构计划再改

Fallback:
- 都不在 → 手动列坏味道 + 逐步改，每步跑测试

分类: 快速改动
- 默认主路径 → 直接最小改动（1-2 步单文件/改文案/格式），不弹 A/B/C
- 改动超出 3 文件或开始跨模块 → 重新分类为「开发新功能」
- 条件路径：`ponytail:ponytail`（当前会话可调用才走）

AskUserQuestion:
- A: 直接最小改动
- B: 改成完整功能流程

Fallback:
- 用户说「别省，按完整流程来」 → 升到「开发新功能」

分类: 构建错误
- 默认主路径 → 跑项目已有构建命令，按错误原文排查
- 条件路径：`ecc:react-build` / `ecc:rust-build` 等专项 slash command、对应 resolver agent（当前会话可调用才走）

AskUserQuestion:
- A: 直接排构建错误
- B: 我先贴错误原文

Fallback:
- 框架未知 → 先问语言/框架
- 仍失败 → 停止自动清理，展示工作区状态和完整错误；如需删除未跟踪文件，单独确认删除范围

分类: 文档写作
- 默认先走 `article-writing-guide`（写作总路由）
- 从零写且分类已明确 → `article-writer`
- 规范格式/统一 Markdown → `chinese-markdown-normalizer`

AskUserQuestion:
- A: 从零写
- B: 规范/润色
- C: 审校

Fallback:
- skill 不在 → 回到基础人工流程

分类: 路由指南维护
- 先判断是否值得迁移；只评估外部做法 → 只给结论，不改文件
- 审查/优化/新建任一 router 型 guide skill（含本指南自身）→ `guide-skill-auditor`（十查 + 基线测试 + 分级修复）
- 小型路由/测试修正 → 补 RED 场景或最小检查，最小改 `SKILL.md` / `test-prompts.json` / 必要参考文件，并跑审计
- 行为变化或要量化优化 → `darwin-skill`；条件路径：`superpowers:writing-skills`
- 迁移内容只吸收路由规则：触发词、分类、证据门槛、fallback、反模式

AskUserQuestion:
- A: 只做最小迁移（推荐）
- B: 先完整评估再改
- C: 只给方案不改文件

Fallback:
- 外部做法太项目化 → 不迁移，建议做项目专属 skill
- 缺少可验证测试场景 → 先补 test prompt，不直接改正文
- 用户要求"直接做" → 仍保留 RED 检查和审计，跳过 A/B/C 选择

分类: 提交/收尾
- 默认主路径 → 手动 git add/commit；commit/push 前展示 `git diff --cached --stat` 待确认（CLAUDE.md §1.3 人工确认线）
- 条件路径：`commit-commands:commit`（单提交）、`commit-commands:commit-push-pr`（**一条命令自动 push 远端 + gh 开 PR，不可逆**）、`superpowers:finishing-a-development-branch`（长分支收尾）、`ocr review`（commit 前独立审查）

AskUserQuestion:
- A: 手动提交（展示 diff 待确认）
- B: `commit-commands:commit`（条件路径）
- C: `commit-commands:commit-push-pr`（自动 push + 开 PR，跑前务必确认）

Fallback:
- 都不在 → 手动 git add/commit；`commit-push-pr` 类一条命令推远端，跑前务必确认

分类: 知识收尾
- 默认主路径 → `neat-freak`
- 用于会话/阶段完成后同步 docs、README、AGENTS/CLAUDE、memory，清理过期/重复/冲突知识
- 不用于代码重构；代码重构仍走「重构/简化」

AskUserQuestion:
- A: `neat-freak`（知识库收尾，推荐）
- B: 只同步 memory
- C: 只更新项目 docs

Fallback:
- `neat-freak` 不在 → 手动枚举 docs / README / AGENTS / memory，按受众同步，删过期重复

分类: 循环任务
- 循环/轮询/条件驱动 → `/loop`（固定间隔走定时；省略间隔让模型自定步调，覆盖条件驱动）

AskUserQuestion:
- A: 直接 `/loop`
- B: 先确认终止条件再 `/loop`
- C: 展示循环任务路径

Fallback:
- `/loop` 不可用 → 说明不可用并回到手动执行

分类: 了解指南
- 展示最小速查 + `references/ecosystems.md`
- 展示完后再问「现在要执行什么」

分类: 编码域调研（社区/舆情/最近动态）
- 编码场景下查「最近 X 有什么更新/讨论」 → `last30days`（近 30 天社区真实用户声音，跨 Reddit/X/HN/YouTube/TikTok）
- 不替代 `lean-ctx`（读代码）/ `gitnexus-exploring`（调用链）/ `agent-reach`（存证调研）：这些是结构性查询，本分类是时间敏感的舆情/动态
- Fallback：`last30days` 不在 → WebSearch 限时 + 用户口径限定

AskUserQuestion:
- A: 走 `last30days` 查近 30 天（推荐）
- B: 用 WebSearch 限时查
- C: 我只要一手官方 changelog

### Step 3：收敛规则（🛑 同分类重复触发时执行）

- 第一次拒绝 A → 排除 A，只问剩余选项
- 第二次仍拒绝 → 展示剩余全部选项让用户自选
- 第三轮仍无共识 → 停止路由，直接问用户当前真实目标
- 同一分类在同一 session 重复触发时，沿用上次被拒选项，不重置

### Step 4：无匹配

分类不清时，先问一个关键问题，再按答案收口（单题上限 4 选项）：

**第一问（按最终交付物）：**
- A: 写代码（新功能 / 有需求文档 / 重构 / 快速改动）
- B: 看代码（理解 / 审查）
- C: 修问题（调试 bug / 构建错误）
- D: 非编码交付或独立工具请求（对外内容 → `article-writing-guide`；学习结果 → `learning-guide`；视觉产出 → 前端视觉子路径；**仅需直接回答/调用独立工具 → 直接执行，不制造第四 router**）

**第二问：** 按第一问选定方向，列出该方向下的具体分类让用户选。

---

## 参考内容（新手 & 深度了解用）

速查与反模式见 [`references/cheatsheet.md`](references/cheatsheet.md)（决策速查 / 生态速查 / 反模式 / 迁移闸门 / 重机制黑名单）；生态详情见 [`references/ecosystems.md`](references/ecosystems.md)。用户选「展示选项」或分类为「了解指南」时展开。

---

## 进化机制

维护规则、证据源、同步清单、变更记录见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)。

<!-- 路由表门禁：Step 1 信号表、Step 2 分类路径由人工维护；删除任何分类/条目前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）。v1.5.0 -->
