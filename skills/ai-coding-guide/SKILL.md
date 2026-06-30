---
name: ai-coding-guide
description: Use when user asks which skill/tool/ecosystem to use, how Superpowers/agent-skills (or any installed plugin) differ or compare, which fits a task, how to combine them, or when a new plugin/skill is installed and this guide needs updating. 中文触发：用哪个工具、X和Y区别/冲突吗、有什么工具能用、刚装了X插件、X不能用了、SP/agent-skills 怎么选、哪个更好、该用什么、怎么配合。Living doc — evolves as ecosystems are added.
---

# AI 编码多生态使用指南

## 定位与质量标准

**定位：** 本 skill 是选型路由器，负责推荐用哪个 skill / 生态。路由结论、决策表、反模式表用于**选型参考**，不认领整条工作流权威——下游 skill / agent 的执行纪律由各自 skill 和项目 AGENTS.md 决定。用户没显式否定时，按本指南推荐走。

**质量底线（因被全局借鉴，故必须高）：**
- **准确**：命令/skill 名引用前 grep 或查当前会话系统 reminder 确认仍存在；规模数字加"≈"；作者/归属核实来源（marketplace.json / plugin 元数据），不凭记忆断言。
- **AI 可读**：决策走表格不走散文；每路径保持「触发条件 → 一线修复 → 兜底」三段式；无歧义标记（🔴 必做 / 🛑 停 / ⚠️ 异常 / ℹ️ 备注）。
- **可进化**：living doc，触发即改。发现过时/错误/新生态，当场更新并记 CHANGELOG（流程见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)），不拖到下次。

**环境自检（触发即执行）：** 本指南推荐跨越多套生态，但各生态是否实际安装因环境而异。触发本 skill 后，**先扫当前会话的 skill 列表（系统 reminder）**，对缺失生态做如下处理：

> ⚠️ **reminder 是磁盘的不完整投影**：系统 reminder 列出的 skill 可能少于磁盘实际安装（实测：SP 磁盘 14 个但 reminder 只暴露 13 个，using-git-worktrees 缺席）。因此：reminder 里有的 = 一定可用；reminder 里没有的 ≠ 一定不存在，关键推荐前用 Get-ChildItem ~/.codex/skills / ~/.agents/skills 实测复核。
- 生态整体缺失（skill 列表无该命名空间）→ 推荐路径里跳过该生态，用 ✅标记的替代生态（见下表）
- 生态部分缺失（个别 skill 不在）→ 正常推荐，fallback 走"仍失败兜底"
- **不自检就推荐不存在的工具** = 最严重的路由失败

**生态可用性参考（需触发时实测复核，勿当静态事实）：**

| 生态 | 状态 | 缺失时替代 |
|------|------|-----------|
| ✅ Superpowers | 14 skill 全在 | 无需替代 |
| ✅ agent-skills | 24 skill 全在 | — |
| ✅ mattpocock | 多 skill 已装（含 `grill-me` / `teach` / `zoom-out`） | SP / ponytail / 直接回答 |
| ✅ codex-security | 10 skill 全在 | — |
| ✅ build-web-apps | 6 skill 全在 | — |
| ✅ openai-developers | 5 skill 全在 | — |
| ✅ understand-anything | 8 skill 已装（junction） | 大仓库降级 CodeGraph |
| ✅ headroom | v0.23.0（pip + MCP 已配） | 降级 lean-ctx |
| ✅ github | 4 skill 全在 | — |
| ✅ karpathy-skills | 1 skill 已装（karpathy-guidelines） | — |
| ✅ ponytail | v4.7.0，lazy senior dev mode（YAGNI / stdlib first / 不加未请求抽象） | SP 设计先行（需完整流程时）|
| ✅ claude-api | anthropic-agent-skills，Claude API/SDK 文档 skill | — |
| ✅ last30days-skill | v3.7.0，跨平台趋势研究（Reddit/X/YouTube 等） | agent-reach（社交/资讯）|
| ⚪ Trellis（外部 CLI） | 默认未装，需实测 | SP writing-plans / TaskCreate |
| ❌ harness 配置（update-config 等） | Codex 无此机制 | 手动改 config.toml |

**证据门槛：** 本指南所有推荐均为基于生态设计哲学的**推理**（如"SP 管纪律"），非 benchmark 实测；重叠区优先级是经验判断。依赖 MCP 的生态（headroom/context7/playwright/understand-anything）不可用时需降级。用户质疑推荐时不辩解，贴更硬证据或承认不确定。

**分层原则：** 默认先分清三层再推荐——`grill-me` 管轻量澄清，Superpowers 管重流程硬门禁，Trellis 管长任务执行期的任务树治理（外部 CLI，不默认假设已安装）。不要把三层混成一个“大而全默认答案”。

---

## 交互决策流程

**重要：** 触发本 skill 后，先执行以下决策流程，再展示参考内容。

### Step 1：提取用户意图

从用户消息中提取关键信息：

| 信号 | 分类 | 示例 |
|------|------|------|
| 开发新功能 | 开发新功能 | "写个登录", "做个新页面", "加个API" |
| 已有需求/PRD | 有需求文档 | "根据这份PRD实现", "需求文档见文件X" |
| 审查代码 | 审查代码 | "审查这段代码", "帮我review", "看看有什么问题" |
| 调试 bug | 调试 bug | "这个bug怎么回事", "报错了", "运行失败" |
| 快速原型/小改 | 快速改动 | "改个小功能", "加个按钮", "简单修一下" |
| 构建错误 | 构建错误 | "编译不过", "build报错", "类型错误" |
| 文档写作 | 文档写作 | "写篇文章", "写文档", "润色" |
| 持续/循环任务 | 循环任务 | "每5分钟检查", "持续跑到XX条件" |
| 单纯问指南 | 了解指南 | "SP和agent-skills有什么区别", "用什么工具" |

**分类优先规则：** 消息含"哪个好""怎么选""该用什么""推荐哪个"等比较/选择疑问 → **先做对比型二次分流**：

| 子类 | 判定 | 路由 |
|------|------|------|
| 带任务信号 | 选择疑问 + 明确开工信号（写功能/写博客/学代码库/审查/调试等 Step 1 分类信号） | **不走了解指南**。按任务信号归入对应分类，在该分类推荐路径里直接给 A vs B 对比结论 + AskUserQuestion 确认，**不泛泛展示速查表** |
| 纯抽象对比 | 只问生态/工具本身，无具体任务（如"SP 和 agent-skills 有什么区别"） | 优先 **了解指南**，展示速查表 + Read references 详情，再问是否执行 |

典型用例："想写个登录功能，用 SP 还是 ponytail"→ 带任务，走开发新功能分类给对比；"SP 和 agent-skills 区别"→ 纯抽象，走了解指南。

**多生态同时触发检测：** 分类后若消息同时提到 ≥2 个生态的同类能力（如 SP brainstorming + agent-skills review、SP verification + agent-skills shipping、多套 TDD/plan/spec）→ **必查下方「反模式与失败处理」表**定优先级，按"SP 管流程纪律先行 / 技术生态随后"决定先后，**不并发触发**。

**明确优先级：** "了解指南" 以外的分类，先走决策路径，再解释概念。用户语调像咨询而非开工时，优先了解指南。

### Step 2：匹配推荐路径

> 🔴 **CHECKPOINT 规则**：每条推荐路径执行前**必须**用 AskUserQuestion 确认（A 执行 / B 看详情 / C 看其他）。**🛑 STOP**：用户说"直接做/别问"才跳过确认；收敛流程见 Step 3（排除已拒 → 缩小范围 → 3 轮不成退 Step 4）。
>
> **🛑 STOP 执行规程**：(1) 每轮 A/B/C 问完即停，用户选前不动；(2) 用户明确表态才继续；(3) 同分类重复触发先 Re-read 收敛状态再问。

根据分类 + 用户明确表达，选推荐路径。每分类提供 **3 选项**：A 执行推荐 / B 展示详情 / C 看其他选项。

每分类含三段式 fallback：触发条件 → 一线修复 → 仍失败兜底。

> ℹ️ 下方各分类 B/C 选项提到的对比表（「多生态流程对比」「诊断问题」「配合模式」「重叠区处理」）均已迁至 **`references/ecosystems.md`**，需 Read 展开后再展示给用户。主文件只保留「生态速查」「决策速查」「选型速判」三张速查表。

```
分类: 开发新功能
→ 默认先判定是"需求还模糊"还是"需求已够清楚"
   - 需求模糊 / 用户自己也在犹豫方案 → 优先 `grill-me`（轻量澄清，逐问逐答）
   - 需求清楚但任务大 / 涉及架构或多模块 → 走 [SP] brainstorming（重流程设计先行）
   - 只是小功能 / 范围很小 → 重分类"快速改动"，走 ponytail

   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "检测到你要开发新功能，先走哪层？"

   A: "先 grill-me 澄清需求" → 触发 grill-me；澄清完回到本 skill 或转有需求文档
   B: "直接 SP brainstorming" → 跳过本 skill，触发 brainstorming skill
   C: "只是小改，走最简方案" → 重分类"快速改动"

  ⚠ 触发条件：`grill-me` 不存在或用户明确讨厌被连续追问
     一线修复：改走 SP brainstorming（要完整设计）或有需求文档（需求已定）
     仍失败兜底：用户描述需求，直接回答（不走流程）

   ⚠ 触发条件：同一 session 已触发审查类生态
    一线修复：先做澄清/设计，审查后置。查「反模式与失败处理」首行确认顺序
    仍失败兜底：用户坚持串行 → 按用户指定顺序执行，不加干扰

   ⚠ 触发条件：用户嫌 SP 太重，但又不是小改
     一线修复：先 grill-me，把需求压实后重分类"有需求文档"
     仍失败兜底：展示 plan 类 skill（writing-plans、planning-and-task-breakdown）

分类: 有需求文档
→ 默认先判定是"只缺执行计划"还是"要长任务治理"
   - 只缺落地计划 → [SP] writing-plans
   - 计划已定且预计长会话/多阶段执行 → `Trellis`（外部 CLI，需用户环境已装；未装则回落 TaskCreate + SP writing-plans）
   - 想轻量拆任务，不想进 SP 重流程 → agent-skills planning-and-task-breakdown

   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "有明确需求，下一步走哪种执行层？"

   A: "SP writing-plans" → 执行 writing-plans（拆任务+文件路径）
   B: "Trellis 任务树执行" → 说明这是外部 CLI；用于长任务保持上下文不跑偏
   C: "轻量拆任务" → 执行 planning-and-task-breakdown

   ⚠ 触发条件：SP writing-plans 执行出错
     一线修复：退到 planning-and-task-breakdown（轻量拆任务）
     仍失败兜底：手动写出需求清单，不做 plan 直接实现

   ⚠ 触发条件：用户提 Trellis，但当前环境未确认已安装
     一线修复：先把 Trellis 定位成"执行期外部治理层"，不直接假设可运行；回落到 SP writing-plans
     仍失败兜底：用户自己在项目根运行 `trellis init` 后再继续，或完全不走 Trellis

   ⚠ 触发条件：用户对计划不满意
     一线修复：展示替代 plan skill（writing-plans / agent-skills planning-and-task-breakdown / mattpocock to-prd）
     仍失败兜底：AskUserQuestion 问"要详细计划(>5 步)还是粗略路线(≤3 步)"

分类: 审查代码
→ [SP] requesting-code-review / codex-security:security-diff-scan

   🔴 前置门（先定审查对象，再选深度）：
   1. 有未提交改动（`git diff` 非空）→ 审本地改动
   2. 用户提供 PR 链接/编号 → 审远程 PR（`gh pr view`）
   3. 都没有 → AskUserQuestion 二选一："贴代码块" / "给 PR 链接"
   对象未定前，**不**急着选轻量/深度。

   **🛑 STOP — 等审查对象确定后：**
   AskUserQuestion（对象已定后）:
   "审查对象 = X，推荐哪个深度？"

   快路径（避冗余）：贴代码块 / 改动 < 3 文件 / 非高风险（auth/DB/架构/安全）→ 默认 A 轻量，不再问；高风险或用户主动要"深度" → 直走 B。

   A: "轻量审查 SP requesting-code-review" → 执行 requesting-code-review（低/中风险够用）
   B: "安全审查 codex-security:security-diff-scan" → 执行 security-diff-scan（高风险：auth/DB/架构/安全）
   C: "展示全部审查选项" → 展示"多生态流程对比"节（审查行）+ "重叠区处理"表 + "决策速查"表

   ⚠ 触发条件：用户项目无 git diff 且无 PR 链接
     一线修复：AskUserQuestion "贴代码块 or 远程 PR 链接？"
     仍失败兜底：用户贴代码块，逐行审查

   ⚠ 触发条件：security-diff-scan 需 MCP 但未配置
      一线修复：退到 SP requesting-code-review（轻量自检）
     仍失败兜底：用户手动提供第三方 API key 或跳过对抗

分类: 调试 bug
→ [SP] systematic-debugging
   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "检测到调试需求，走 SP systematic-debugging（4阶段根因分析），是否执行？"

   A: "执行 SP systematic-debugging" → 触发 systematic-debugging skill
   B: "展示调试工具详情" → 展示"诊断问题"表中 SP 调试能力
   C: "我自己来，看看参考信息" → 展示"自动化/循环"表 + "决策速查"表

   ⚠ 触发条件：systematic-debugging skill 不存在
     一线修复：手动执行 4 阶段（调查→复现→检查变更→加诊断）
     仍失败兜底：AskUserQuestion 问错误信息/复现步骤，人工诊断

分类: 快速改动
→ [ponytail] 最简方案（YAGNI / stdlib first）
   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "快速改动，走 ponytail 最简方案，是否执行？"

   A: "好，开始" → ponytail 强制最简实现，改完可选 SP verification-before-completion
   B: "展示步骤详情" → 展示"多生态流程对比"节（开发功能阶段行）+ "决策速查"表
   C: "我自己决定步骤" → 展示"选型速判"表

   ⚠ 触发条件：改动范围比预期大（>3 文件）
     一线修复：重新分类"开发新功能"，走 SP brainstorming
     仍失败兜底：直接手动改，不做 plan/review

分类: 构建错误
→ 手动框架检测 + build-web-apps / 语言无关排查
   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "检测到构建错误，走框架修复流程，是否执行？"

   A: "执行构建修复" → 检测框架 → build-web-apps:frontend-testing-debugging（前端）/ 语言无关的编译错误排查（后端：tsc --noEmit / go build 等，按项目 AGENTS.md §1.4 构建纪律）
   B: "展示可用构建修复工具" → 展示"诊断问题"表中构建相关行 + build-web-apps:frontend-testing-debugging
   C: "先看看参考信息" → 展示"决策速查"表

   ⚠ 触发条件：无法自动检测框架
     一线修复：AskUserQuestion 问"什么语言/框架？"
     仍失败兜底：按项目构建命令直接排查（tsc --noEmit / go build / mvn 等），贴编译错误原文人工分析

   ⚠ 触发条件：构建命令本身报错无法定位
     一线修复：展示编译错误原文，结合 import 链推断受影响模块
     仍失败兜底：回退到干净状态，用户手动排查

分类: 文档写作
→ 第三方 skill
   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "文档类任务，走哪个方向？"

   A: "从零写文章" → 调用 article-writer skill
   B: "润色/规范格式" → 调用 chinese-markdown-normalizer skill
   C: "审校已有文章" → 调用 review-doc skill

   ⚠ 触发条件：article-writer skill 不在已安装列表
     一线修复：退到基础写作流程（问主题→出大纲→逐段写）
     仍失败兜底：用户直接说内容，手动组织

   ⚠ 触发条件：review-doc 需要原文路径但用户只贴了片段
     一线修复：用贴的片段做分段评审
     仍失败兜底：用户提供完整文件路径

分类: 循环任务
→ 内置 /loop / /goal
   **🛑 STOP — 停住，等用户选：**
   AskUserQuestion:
   "循环任务，走哪个方案？"

   A: "简单定时轮询 /loop" → 用户补充间隔后执行
   B: "条件驱动 /goal" → 用户补充条件后执行
   C: "受管循环" → 走 /loop 或 /goal（Codex 无受管循环生态）

   ⚠ 触发条件：/loop 或 /goal 命令不可用
      一线修复：手动模拟循环（用 /loop）
     仍失败兜底：描述想要的效果，手动模拟第一次执行

   ⚠ 触发条件：loop 跑飞（无限循环）
     一线修复：提醒用户用 Ctrl+C 或 TaskStop 终止
     仍失败兜底：设置 max-runs=10 / max-duration=30m 硬限制

分类: 了解指南
→ 展示参考内容 + 决策速查表
   展示完后 AskUserQuestion："看完了，需要执行什么？" → 回到 Step 1 重新分类

   ⚠ 触发条件：用户看完仍不确定做什么
     一线修复：走 Step 4（无匹配），让用户从 6 类中选
     仍失败兜底：直接问"你当前项目是什么场景？"手动匹配
```

### Step 3：流程仲裁【收敛追踪】

Step 1 分类 → Step 2 推荐路径 → AskUserQuestion 确认（A 执行 / B 看详情 / C 看其他）→ 执行或展示参考表。"了解指南"分类展示完参考内容后，AskUserQuestion 问"要执行什么"→ 有目标回 Step 1 重分类，没有则结束。

**🛑 收敛规则（同 session 同分类重复触发）：**
- 首次拒绝推荐 A → 排除 A，从剩余选项缩小范围再问
- 第二次拒绝 → 排除已拒选项，展示剩余全部选项让用户自选
- 第 3 轮无共识 → 退 Step 4
- 同一 session 同一分类第二次触发 → 加载上次收敛状态（已拒选项），不重置

### Step 4：无匹配

无法分类或用户意图模糊 → 用 AskUserQuestion 问：

**示例：**
```
不太确定你想做什么，以下哪个最接近？
- A: 想写个新功能，但在犹豫用什么工具
- B: 有明确需求/文档，想落地实现
- C: 审查代码质量
- D: 调试一个 bug
- E: 文档写作/润色
- F: 单纯了解 SP 和其他生态的区别
```

选定分类后走 Step 2，按该分类默认选项 A 执行推荐路径。

---

## 参考内容（新手 & 深度了解用）

以下内容在用户选择"展示选项"或分类为"了解指南"时展示。描述生态特点和常见场景的推荐方案。

### 反操作清单（执行时停走信号）

以下场景按频率排序，标注在 skill 执行时看到信号就停。**出现任一条 → 停走决策流。**

| 场景 | 错误信号 | 正确动作 |
|------|---------|---------|
| 用户只是问了一个名词解释（"什么是SP"） | 走决策流程问"是否执行" | 直接回答，不走决策流 |
| 用户明确说"别问我，直接做" | 还问"是否执行" | 跳过 AskUserQuestion，自动选 A |
| 用户只是聊天/吐槽（"今天代码又炸了"） | 分类为"调试 bug" | 确认是否真的需要帮助，还是纯吐槽 |
| 项目没有 git 仓库 | 走审查/PR 路径 | 展示文件级替代方案 |
| 用户连续 2 次拒绝推荐路径 | 继续推销 | 先排除已拒选项缩小范围再问；第 3 轮达不成 → 停，明说"当前推荐都不适合"让用户自述 |
| 用户明确嫌 Superpowers 太重/太啰嗦 | 仍默认推 SP | 先降一层：`grill-me` 做轻量澄清；再看是否真需要 SP / Trellis |
| 用户提 dangerously-skip-permissions / 自动放权 | 把它当推荐默认项 | 只当执行期风险开关处理：需求很清楚 + 计划很硬 + 用户明确接受风险时才提；新项目/陌生仓库默认不推荐 |
| 两个分类都匹配（如"写个新功能但不知道怎么选"） | 只匹配一个 | 按分类优先规则二次分流：带任务信号→走任务分类给对比结论；纯抽象→了解指南 |
| 参考内容太长（>200 行） | 全部展示 | 按三层折叠规则执行：用户选 A"直接执行"→ 仅路由，0 参考表；走任务分类 → 折叠，仅决策速查 + 反操作清单 + 相关生态行；选"看详情"或分类=了解指南 → 完整展示 |
| 用户贴了代码段但没说意图 | 直接分类"审查代码" | 先问"这段代码做什么？你想审查/调试/还是当参考？"再走对应分类 |
| 用户说"查资料"但实际是调试场景 | 走"了解指南"展示速查表 | 确认意图：真查资料还是排查问题？后者走调试分类 |

### 生态速查（详情 Read [`references/ecosystems.md`](references/ecosystems.md)）

| 生态 | 一句话定位 | 独有亮点 | 代表命令（slash 直调） |
|------|-----------|---------|----------------------|
| Superpowers | 流程纪律 pipeline（设计先行 / TDD / 证据驱动，自动触发） | brainstorming HARD-GATE、subagent-driven-development | `superpowers:brainstorming` / `:writing-plans` / `:test-driven-development` / `:systematic-debugging` / `:verification-before-completion` |
| agent-skills | SDLC 闭环 spec→ship | interview-me / idea-refine / doubt-driven-development | skill 长名调用（spec-driven-development / planning-and-task-breakdown / code-review-and-quality / test-driven-development / shipping-and-launch / code-simplification）。⚠ Codex 侧无 namespace，slash 命令未装 |
| mattpocock | 28 个单用途小 skill，显式调用为主 | teach / zoom-out / writing-* / grill-* / caveman | 多为 Skill 工具调用，少数有 slash（`caveman:caveman`）；需求澄清优先看 `grill-me` |
| understand-anything | 代码库 → 知识图谱（8 skill，已装于 ~/.agents/skills/） | graph.json / tour-builder / blast radius | `understand` / `understand-chat` / `understand-onboard`（MCP 服务需先 build graph）|
| headroom | 上下文压缩 MCP（v0.23.0，pip 装于系统 Python） | headroom_compress/retrieve/stats（配合 lean-ctx 三层栈） | MCP 工具 `headroom mcp serve`，无 slash |
| Trellis | 长任务执行期任务树治理（外部 CLI，不是当前 skill 生态） | 任务树做持久真相源，减少长会话跑偏 | `trellis init --claude --codex`（仅在用户环境已装时提） |
| karpathy-skills | 编码行为规范准则（减少 LLM 常见编码错误，1 skill 已装） | karpathy-guidelines（外科手术式改动、显式假设、可验证验收标准） | Skill 调用 `karpathy-guidelines` |
| codex-security | 安全扫描全套（10 skill，openai-curated 插件） | deep-security-scan（多 pass）/ security-diff-scan（PR/commit）/ threat-model / attack-path-analysis / fix-finding / track-findings / triage-finding | codex-security:security-scan / :deep-security-scan / :security-diff-scan / :threat-model |
| build-web-apps | 前端开发全链路（6 skill，openai-curated 插件） | frontend-app-builder（从设计到代码）/ react-best-practices / shadcn / stripe / supabase / frontend-testing-debugging | uild-web-apps:frontend-app-builder / :react-best-practices / :shadcn / :frontend-testing-debugging |
| openai-developers | OpenAI 应用开发（5 skill，openai-curated 插件） | agents-sdk / build-chatgpt-app / chatgpt-app-submission / openai-api-troubleshooting / platform-api-key | openai-developers:agents-sdk / :build-chatgpt-app / :openai-api-troubleshooting |
| Codex marketplace 插件 | Codex 官方插件市场（openai-primary-runtime / openai-bundled / openai-curated 三源） | documents / spreadsheets / presentations（Office）；browser / computer-use（自动化）；github / figma / notion / playwright（集成） | `codex plugin add <name>@<marketplace>` / `codex plugin list` / `codex plugin marketplace add <owner>/<repo>` |
| 全量查询类 | 想看全部可用命令/skill 时的入口 | 实时反射当前安装内容 | `/help` 或交互终端（内置命令全量） |
| ponytail | lazy senior dev mode：强制最简方案（YAGNI / stdlib first / 不加未请求抽象） | 与 SP 设计先行冲突时的裁决 | skill 自动触发（v4.7.0）|
| claude-api | Claude API/SDK 文档（构建 LLM 应用时参考） | 与 openai-developers 互补 | skill 调用 |

> 各生态哲学 / 命令 / 取舍 / 流程对比 / 重叠区处理：用户选 B「看详情」或分类「了解指南」时，Read `references/ecosystems.md` 展开。
>
> ⚠️ **推荐性质**：本表推荐均为推理非实测（重叠优先级=经验判断），详见上方「定位与质量标准 → 证据门槛」。MCP 依赖生态（headroom/context7/playwright/understand-anything）降级见 references「MCP 依赖与降级」节。

### 决策速查

| 你说 | 工具 | 理由 |
|------|------|------|
| "想写个功能" | `grill-me`（需求模糊时）→ SP brainstorming（需求大且要重流程）→ ponytail（范围很小时） | 先澄清，再决定是否值得上重流程 |
| "审查这段代码" | SP requesting-code-review（日常自检）→ codex-security:security-diff-scan（安全审查）→ codex-security:deep-security-scan（高风险） | 三层递进：自检→安全→深度扫描 |
| "我刚改完，确保没问题" | SP verification-before-completion（日常）→ build-web-apps:frontend-testing-debugging（前端合并前） | 先证据检查后系统验证 |
| "写测试" | SP test-driven-development | 流程纪律驱动 |
| "调试这个 bug" | SP systematic-debugging | 4 阶段根因分析 |
| "安全扫描/安全审查" | codex-security:security-scan（repo 全量）/ security-diff-scan（PR/diff） | 当前最完整安全管线；高风险用 deep-security-scan（多 pass）|
| "写前端应用" | build-web-apps:frontend-app-builder（设计→代码）/ react-best-practices / shadcn | 前端全链路 |
| "用 OpenAI API 开发" | openai-developers:agents-sdk / build-chatgpt-app / openai-api-troubleshooting | OpenAI 官方 skill；配 platform-api-key 管 key |
| "构建错误" | build-web-apps:frontend-testing-debugging（前端）；后端按项目构建纪律排查（tsc --noEmit / go build 等，见 AGENTS.md §1.4） | 框架自动检测 |
| "每 5 分钟检查" | 内置 /loop 5m ... | 最轻量的定时方案 |
| "持续跑到目标达成" | 内置 /goal <condition>（环境依赖，不可用时降级 /loop）| 条件驱动 |
| "我刚做完，要发 PR" | SP finishing-a-development-branch（选操作） | SP finishing-a-development-branch 内含 PR 选项 |
| "一行产品想法写 PRD" | qiaomu-ai-prd skill（速读卡+约束层+验收脚本，AI 可执行） | 重产出可执行 PRD 文档；若要落地实施计划 → SP writing-plans |
| "系统学/上手新代码库" | understand-anything（深度结构化 graph + blast radius）vs mattpocock zoom-out（轻量摘要） | 深度学习/大重构影响分析选 understand-anything，快速浏览选 zoom-out；前者依赖 MCP 不可用需降级 |
| "长会话执行老跑偏" | Trellis（若已安装）→ 回落 TaskCreate / SP writing-plans | Trellis 价值在执行期任务树，不在前期头脑风暴 |
| "想开 dangerously-skip-permissions" | 默认不用 | 风险开关非生产力项；完整边界见下方「反操作清单」 |
| "想看全部可用命令/skill" | `/help` 或交互终端（内置命令全量） | 实时反射当前安装内容，本指南只点代表不穷尽 |

> **审查深度原则**：高风险/重要模块用**循环返工审查**（reject-until-criteria，门下省式）而非单次 review。
>
> 单次轻量 review 跑一遍就过 = 无门下省；高风险（auth/DB schema/架构/安全敏感）需循环兜底。实际执行走 codex-security 多 pass（deep-security-scan）或 SP requesting-code-review。`plagiarism-audit` 是查重领域同款循环架构（计划生成者→多审查员→反馈者，多轮直到独立终判 PASS）的参考。

---

### 反模式与失败处理

| 场景 | 一线处理 | 仍失败兜底 | 不要做的事 |
|------|---------|-----------|-----------|
| 同时触发 SP brainstorming 和代码审查 | 优先走 SP 流程（设计先行），审查留在后面 | 用户明确说"审查代码"时 SP 的 HARD-GATE 不适用 | 不要两个同时跑——SP 的 HARD-GATE 会阻止写代码，审查需要代码存在 |
| SP 流程太啰嗦，想跳过设计直接写 | 仅当"需求未成文的新功能"才坚持 HARD-GATE：没设计就不能写代码。已有明确需求/PRD → 走"有需求文档"分类，不强制 brainstorming | 用户说"我很确定不需要设计"→ 清理工作树后交给用户决定 | 不要在需求已成型时仍强制 SP brainstorming |
| 找不到合适 skill | 用 find-skills 按关键词搜，或 `/help` 看全部 | 直接问"你想要什么能力" | 不要花时间背 skill 列表 |
| SP 的 TDD 强制在不适合的项目触发 | 用户说"这个项目不适用 TDD"→ 不要自动触发 test-driven-development | 在项目 AGENTS.md 声明 "skip TDD" | 不要手动删掉 test-driven-development skill |
| 两个生态同时建议同一件事（审查/验证） | 先用 SP 的轻量版本（requesting-code-review / verification-before-completion） | 仍有问题再上 codex-security 深度版（deep-security-scan） | 不要两个都跑——浪费 token |
| /loop 循环跑飞 | 确认有终止条件（max-runs / max-cost / max-duration） | 关 terminal 强制停 | 不要把 /loop 当背景噪音跑 |
| 同时触发 qiaomu-ai-prd / SP writing-plans（PRD 流程） | qiaomu-ai-prd（生成 AI 可执行 PRD）→ SP writing-plans（基于 PRD 出计划） | 用户只要 PRD 文档不落地则单跑 qiaomu-ai-prd | 不要两个都跑——产出重叠浪费 token |

### 选型速判

| 你的情况 | 推荐主力 | 原因 |
|---------|---------|------|
| 新功能需求还模糊 | `grill-me` | 逐问逐答快速拍板，比先读长 brainstorm 文档轻 |
| 新功能需求已清楚 + 要重流程 | SP brainstorming → writing-plans | 自动流程兜底，不担心漏步骤 |
| 长会话执行老跑偏 | Trellis（若已安装）→ 回落 TaskCreate / SP writing-plans | Trellis 管执行期任务树，非默认前置 |
| 快速原型/改 bug | ponytail（最简方案）/ SP systematic-debugging（bug） | ponytail 管最简改动；bug 走 SP |
| 团队项目 | SP + codex-security | SP 管流程纪律，安全走 codex-security；前端 patterns 用 build-web-apps，通用工具按需用 mattpocock |
| 个人文档项目（如 JavaGuide） | ponytail + 第三方 skill | SP 的 TDD 强制在此场景不适用；ponytail 管最简实现 |
| 代码质量要求高 | SP requesting-code-review + codex-security | 通用审查流程走 SP + codex-security（深度安全用 deep-security-scan）|
| 持续集成/自动化 | 内置 /loop + /goal | Codex loop 能力走内置命令 |

---

## 进化机制

维护说明（何时更新 / 怎么更新 5 步 / 维护纪律 / 变更记录）见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)。本指南是 living doc，随插件/skill 增删持续更新，触发即改。
