---
name: ai-coding-guide
description: Use when user asks which skill/tool/ecosystem to use, how Superpowers/agent-skills (or any installed plugin) differ or compare, which fits a task, how to combine them, or when a new plugin/skill is installed and this guide needs updating. 中文触发：用哪个工具、X和Y区别/冲突吗、有什么工具能用、刚装了X插件、X不能用了、SP/agent-skills 怎么选、哪个更好、该用什么、怎么配合。Living doc — evolves as ecosystems are added.
---

# AI 编码多生态使用指南

## 定位与质量标准

**定位：** 本 skill 是选型路由器，负责推荐用哪个 skill / 生态。路由结论、决策表、反模式表用于**选型参考**，不认领整条工作流权威——下游 skill / agent 的执行纪律由各自 skill 和项目 CLAUDE.md 决定。用户没显式否定时，按本指南推荐走。

**质量底线（因被全局借鉴，故必须高）：**
- **准确**：命令/skill 名引用前 grep 或查当前会话系统 reminder 确认仍存在；规模数字加"≈"；作者/归属核实来源（marketplace.json / plugin 元数据），不凭记忆断言。
- **AI 可读**：决策走表格不走散文；每路径保持「触发条件 → 一线修复 → 兜底」三段式；无歧义标记（🔴 必做 / 🛑 停 / ⚠️ 异常 / ℹ️ 备注）。
- **可进化**：living doc，触发即改。发现过时/错误/新生态，当场更新并记 CHANGELOG（流程见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)），不拖到下次。

**环境自检（触发即执行）：** 本指南推荐跨越多套生态，但各生态是否实际安装因环境而异。触发本 skill 后，**先扫当前会话的 skill 列表（系统 reminder）**，对缺失生态做如下处理：

> ⚠️ **reminder ≠ 磁盘**：系统 reminder 是磁盘的不完整投影（实测会漏 namespace，SP 磁盘 14 但 reminder 暴露 13）。因此：reminder 里有的 = 一定可用；reminder 没有 ≠ 不存在，关键推荐前用 `ctx_shell` 跑 `ls ~/.claude/plugins/cache/` + `ls ~/.claude/skills/` 实测复核。
- 生态整体缺失（skill 列表无该命名空间）→ 推荐路径里跳过该生态，用 ✅标记的替代生态（见下表）
- 生态部分缺失（个别 skill 不在）→ 正常推荐，fallback 走"仍失败兜底"
- **不自检就推荐不存在的工具** = 最严重的路由失败

**当前环境生态可用性速判（2026-06-26 实测，Claude Code 副本）：**

| 生态 | 形态 | 状态 | 缺失时替代 |
|------|------|------|-----------|
| ✅ Superpowers | `superpowers:` 插件 | 14 skill 全在 | 流程纪律无替代 |
| ✅ **ECC** | `ecc:` 插件 v2.0.0 | **271 skill / 92 command / 67 agent 全载**（最大生态） | 通用流程走 SP；框架专属（react/python/rust/go/swift/kotlin/vue 等 reviewer/build-resolver）无替代 |
| ✅ agent-skills | 顶层 skill 无 namespace | 20+ 全在（spec/plan/test/review/ship/simplify/security/debug/observability/source/doubt/idea-refine/interview-me 等） | 通用流程与 SP 重复，留独有（doubt-driven/source-driven/idea-refine/interview-me） |
| ✅ mattpocock | 顶层 skill（setup-matt-pocock-skills 标记） | 28+ 全在（teach/zoom-out/writing-*/grill-*/design-an-interface/tdd/review 等） | 写作/教学/单用途主力，工程流程当 SP 补充 |
| ✅ understand-anything | `understand-anything:` 插件 + 顶层镜像 | 8 skill + 子 agent | 大仓库降级 gitnexus / mattpocock zoom-out |
| ✅ **gitnexus** | `gitnexus` MCP（17 工具）+ 9 顶层 skill | MCP：query / cypher / impact / api_impact / trace / pdg_query / route_map / explain / check / detect_changes / shape_check / tool_map / rename / context 等；skill：gitnexus-cli / -debugging / -exploring / -guide / -impact-analysis / -pdg-query / -pr-review / -refactoring / -taint-analysis（taint 在 skill 层，非 MCP）| understand-anything / CodeGraph |
| ✅ ponytail | `ponytail:` 插件 v4.8.3 + SessionStart hook | lazy senior dev 模式（YAGNI / stdlib first） | SP 设计先行（需完整流程时） |
| ✅ caveman | `caveman:` 插件 + SessionStart hook | 压缩模式（drop 冗余，省 ~75% token） | mattpocock caveman（同源） |
| ✅ karpathy | `andrej-karpathy-skills:` + 顶层 | karpathy-guidelines | — |
| ✅ codex-security 系 | **并入 ECC**（security-scan / deep-security-scan / security-diff-scan / threat-model / fix-finding 等） | ECC 内 security-* 全套 | 见 ECC |
| ✅ build-web-apps 系 | **并入 ECC**（frontend-/react-/vue-/angular-/nextjs-/vite-/nuxt4- 等） | ECC 内前端全套 | frontend-design 插件 |
| ✅ context7 | `a1b2c3d4-context7-mcp-001` + `plugin:context7:context7` MCP | 双实例，库/框架文档查询 | 直接查官方文档 / WebSearch |
| ✅ playwright | `b2c3d4e5-playwright-mcp-002` + `plugin:playwright:playwright` MCP | 双实例，浏览器自动化 | 手动测试 / curl |
| ✅ chrome-devtools | `plugin:ecc:chrome-devtools` MCP | DOM/console/network/perf/lighthouse | playwright MCP |
| ✅ lean-ctx | `lean-ctx` MCP | 77 工具 + shell 压缩 + AST 解析 18 语言 | headroom |
| ✅ headroom | pip + MCP | v0.23.0，有损压缩 + hash 取回 | lean-ctx |
| ✅ github | `plugin:github:github` MCP | 47 工具（PR/issue/branch/release/code search/commit/copilot review） | `gh` CLI |
| ✅ douyin | `douyin` MCP | 抖音视频信息/下载/音频识别 | 不适用（视频提取专用） |
| ✅ claude-api | anthropic-agent-skills 插件（cache 下 example-skills 子目录） | Claude API/SDK 文档 skill | — |
| ✅ last30days | 顶层 skill | v3.7.0 跨平台趋势研究（Reddit/X/YouTube/HN/Polymarket 等） | agent-reach（社交/资讯） |
| ✅ claude-md-management | `claude-md-management:` 插件 | revise-claude-md / claude-md-improver | 手改 CLAUDE.md |
| ✅ commit-commands | `commit-commands:` 插件 | commit / commit-push-pr / clean_gone | 手动 git |
| ✅ code-review | `code-review:` + `open-code-review:` 插件 | 本地 diff / PR review（open-code-review 走 `ocr` CLI） | SP requesting-code-review |
| ✅ feature-dev | `feature-dev:` 插件 | feature-dev + code-architect/code-explorer/code-reviewer | SP brainstorming + writing-plans |
| ✅ frontend-design | `frontend-design:` + `example-skills:frontend-design` | 反 slop 前端设计 | ECC frontend-/react-* |
| ✅ skill-creator | `skill-creator:` + `example-skills:skill-creator` + darwin-skill | skill 生成与优化 | — |
| ✅ claude-code-setup | `claude-code-setup:claude-automation-recommender` | hook/automation 推荐 | 手改 settings.json |
| ✅ darwin-skill | 顶层 skill + darwin-weekly-audit | skill 自优化（9 维 rubric + hill-climbing） | — |
| ✅ example-skills | `example-skills:` 插件（anthropic-agent-skills umbrella） | 17 skill（mcp-builder / web-artifacts-builder / webapp-testing / doc-coauthoring / claude-api / frontend-design / skill-creator / docx / pdf / pptx / xlsx 等） | — |
| ❌ Codex 受管循环 `/goal` | Claude Code 无 | `/loop` skill 可用，`/goal` 缺 | `/loop` + 手动条件检查 |
| ❌ harness 配置（update-config 等 Codex 机制） | Claude Code 用 `update-config` skill 或 settings.json | — | 手改 settings.json |

**证据门槛：** 本指南所有推荐均为基于生态设计哲学的**推理**（如"SP 管纪律"），非 benchmark 实测；重叠区优先级是经验判断。依赖 MCP 的生态（headroom/context7/playwright/understand-anything）不可用时需降级。用户质疑推荐时不辩解，贴更硬证据或承认不确定。

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
| 带任务信号 | 选择疑问 + 明确开工信号（写功能/写博客/学代码库/审查/调试等 Step 1 分类信号） | **不走了解指南**。按任务信号归入对应分类，在该分类推荐路径里直接给 A vs B 对比结论 + 文字停问确认，**不泛泛展示速查表** |
| 纯抽象对比 | 只问生态/工具本身，无具体任务（如"SP 和 agent-skills 有什么区别"） | 优先 **了解指南**，展示速查表 + Read references 详情，再问是否执行 |

典型用例："想写个登录功能，用 SP 还是 ponytail"→ 带任务，走开发新功能分类给对比；"SP 和 agent-skills 区别"→ 纯抽象，走了解指南。

**多生态同时触发检测：** 分类后若消息同时提到 ≥2 个生态的同类能力（如 SP brainstorming + agent-skills review、SP verification + agent-skills shipping、多套 TDD/plan/spec）→ **必查下方「反模式与失败处理」表**定优先级，按"SP 管流程纪律先行 / 技术生态随后"决定先后，**不并发触发**。

**明确优先级：** "了解指南" 以外的分类，先走决策路径，再解释概念。用户语调像咨询而非开工时，优先了解指南。

### Step 2：匹配推荐路径

> 🔴 **CHECKPOINT 规则**：每条推荐路径执行前**必须**文字停问确认（A 执行 / B 看详情 / C 看其他）。**🛑 STOP**：用户说"直接做/别问"才跳过确认；收敛流程见 Step 3（排除已拒 → 缩小范围 → 3 轮不成退 Step 4）。
>
> **🛑 STOP 执行规程**：(1) 每轮 A/B/C 问完即停，用户选前不动；(2) 用户明确表态才继续；(3) 同分类重复触发先 Re-read 收敛状态再问。
>
> ℹ️ Claude Code 无 AskUserQuestion 工具——本指南「停问」= 文字列 A/B/C 选项后停，等用户回。

根据分类 + 用户明确表达，选推荐路径。每分类提供 **3 选项**：A 执行推荐 / B 展示详情 / C 看其他选项。

每分类含三段式 fallback：触发条件 → 一线修复 → 仍失败兜底。

> ℹ️ 下方各分类 B/C 选项提到的对比表（「多生态流程对比」「诊断问题」「配合模式」「重叠区处理」）均已迁至 **`references/ecosystems.md`**，需 Read 展开后再展示给用户。主文件只保留「生态速查」「决策速查」「选型速判」三张速查表。

```
分类: 开发新功能
→ [SP] brainstorming 自动启动（设计先行）
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "检测到你要开发新功能，走 SP brainstorming 流程，是否执行？"

   A: "执行 SP brainstorming" → 跳过本 skill，触发 brainstorming skill
   B: "我有明确需求，看看其他方案" → 重分类"有需求文档"，走 SP writing-plans
   C: "只是看看有什么工具" → 展示"决策速查"表和 Step 2 参考内容，不行走 Step 4

  ⚠ 触发条件：SP brainstorming skill 不存在或未加载
     一线修复：文字问"替代方案：SP writing-plans？"
     仍失败兜底：用户描述需求，直接回答（不走流程）

   ⚠ 触发条件：同一 session 已触发审查类生态
    一线修复：走本分类 A 推荐（设计先行），审查后置。查「反模式与失败处理」首行确认顺序
    仍失败兜底：用户坚持串行 → 按用户指定顺序执行，不加干扰

   ⚠ 触发条件：用户选 B 后仍不满意 SP writing-plans
     一线修复：展示所有 plan 类 skill（writing-plans、planning-and-task-breakdown）
     仍失败兜底：用户手动描述，跳到 Step 4 无匹配

分类: 有需求文档
→ [SP] writing-plans（需求已定，跳过 brainstorming）
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "有明确需求，走 SP writing-plans 出实施计划，是否执行？"

   A: "执行 SP writing-plans" → 执行 writing-plans（拆任务+文件路径）
  B: "用 agent-skills planning-and-task-breakdown" → 拆有序任务，偏轻量
   C: "看看其他方案" → 展示"多生态流程对比"节（开发功能阶段行）+"决策速查"表

   ⚠ 触发条件：SP writing-plans 执行出错
     一线修复：退到 planning-and-task-breakdown（轻量拆任务）
     仍失败兜底：手动写出需求清单，不做 plan 直接实现

   ⚠ 触发条件：用户对计划不满意
     一线修复：展示替代 plan skill（writing-plans / agent-skills planning-and-task-breakdown / mattpocock to-prd / `feature-dev:code-architect`）
     仍失败兜底：文字问"要详细计划(>5 步)还是粗略路线(≤3 步)"

分类: 审查代码
→ [SP] requesting-code-review / `code-review:code-review` / `ecc:security-scan`

   🔴 前置门（先定审查对象，再选深度）：
   1. 有未提交改动（`git diff` 非空）→ 审本地改动
   2. 用户提供 PR 链接/编号 → 审远程 PR（`gh pr view` 或 `plugin:github:github` MCP）
   3. 都没有 → 文字二选一："贴代码块" / "给 PR 链接"
   对象未定前，**不**急着选轻量/深度。

   **🛑 STOP — 等审查对象确定后：**
   停问（对象已定后）：
   "审查对象 = X，推荐哪个深度？"

   快路径（避冗余）：贴代码块 / 改动 < 3 文件 / 非高风险（auth/DB/架构/安全）→ 默认 A 轻量，不再问；高风险或用户主动要"深度" → 直走 B/C。

   A: "轻量审查 SP requesting-code-review" → 执行 requesting-code-review（低/中风险够用）
   B: "结构审查 `code-review:code-review` / `open-code-review:review`" → 多轴代码质量（正确性/可读性/安全/性能），open-code-review 走 `ocr` CLI 行级
   C: "安全审查 `ecc:security-scan` / 对抗双审 `ecc:santa-loop`" → 高风险：auth/DB/架构/安全；santa-loop 两独立 reviewer 须都 approve

   ⚠ 触发条件：用户项目无 git diff 且无 PR 链接
     一线修复：文字问"贴代码块 or 远程 PR 链接？"
     仍失败兜底：用户贴代码块，逐行审查

   ⚠ 触发条件：`ecc:security-scan` 不可用
      一线修复：退到 SP requesting-code-review（轻量自检）+ `code-review:code-review`
     仍失败兜底：用户手动提供第三方扫描器或跳过对抗

分类: 调试 bug
→ [SP] systematic-debugging → 可选 `gitnexus:trace` / `:explain`（基于 graph 定位根因）
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "检测到调试需求，走 SP systematic-debugging（4阶段根因分析），是否执行？"

   A: "执行 SP systematic-debugging" → 触发 systematic-debugging skill
   B: "展示调试工具详情" → 展示"诊断问题"表中 SP 调试能力 + gitnexus trace
   C: "我自己来，看看参考信息" → 展示"自动化/循环"表 + "决策速查"表

   ⚠ 触发条件：systematic-debugging skill 不存在
     一线修复：手动执行 4 阶段（调查→复现→检查变更→加诊断）
     仍失败兜底：文字问错误信息/复现步骤，人工诊断

分类: 快速改动
→ [ponytail] 最简方案（YAGNI / stdlib first）
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "快速改动，走 ponytail 最简方案，是否执行？"

   A: "好，开始" → ponytail 强制最简实现，改完可选 SP verification-before-completion
   B: "展示步骤详情" → 展示"多生态流程对比"节（开发功能阶段行）+ "决策速查"表
   C: "我自己决定步骤" → 展示"选型速判"表

   ⚠ 触发条件：改动范围比预期大（>3 文件）
     一线修复：重新分类"开发新功能"，走 SP brainstorming
     仍失败兜底：直接手动改，不做 plan/review

分类: 构建错误
→ 手动框架检测 + `ecc:<lang>-build` / 语言无关排查
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "检测到构建错误，走框架修复流程，是否执行？"

   A: "执行构建修复" → 检测框架 → `ecc:react-build` / `:rust-build` / `:go-build` / `:kotlin-build` / `:flutter-build` / `:cpp-build` / `:gradle-build` / `:fastapi-review` 等（框架专属）/ 后端 tsc --noEmit / go build / mvn 等（按项目 CLAUDE.md §1.4 构建纪律）
   B: "展示可用构建修复工具" → 展示"诊断问题"表中构建相关行 + ECC build 命令族
   C: "先看看参考信息" → 展示"决策速查"表

   ⚠ 触发条件：无法自动检测框架
     一线修复：文字问"什么语言/框架？"
     仍失败兜底：按项目构建命令直接排查（tsc --noEmit / go build / mvn 等），贴编译错误原文人工分析

   ⚠ 触发条件：构建命令本身报错无法定位
     一线修复：展示编译错误原文，结合 import 链推断受影响模块
     仍失败兜底：回退到干净状态，用户手动排查

分类: 文档写作
→ 第三方 skill
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "文档类任务，走哪个方向？"

   A: "从零写文章" → 调用 article-writer skill（JavaGuide 模式可切换）
   B: "润色/规范格式" → 调用 chinese-markdown-normalizer / ai-text-polisher skill
   C: "审校已有文章" → 调用 review-doc / tech-article-review / multi-review-pipeline skill

   ⚠ 触发条件：article-writer skill 不在已安装列表
     一线修复：退到基础写作流程（问主题→出大纲→逐段写）
     仍失败兜底：用户直接说内容，手动组织

   ⚠ 触发条件：review-doc 需要原文路径但用户只贴了片段
     一线修复：用贴的片段做分段评审
     仍失败兜底：用户提供完整文件路径

分类: 循环任务
→ `/loop` skill（Claude Code 内置）
   **🛑 STOP — 停住，等用户选：**
   停问（A/B/C）：
   "循环任务，走哪个方案？"

   A: "定时轮询 /loop 5m <prompt>" → 用户补充间隔后执行
   B: "自定步 /loop <prompt>（omit interval 让模型自配速）" → 适合自定步任务
   C: "受管循环" → Claude Code 无独立受管循环生态；走 /loop + 手动 max-runs/max-duration 硬限制

   ⚠ 触发条件：/loop 不可用
      一线修复：用 `loop` skill（顶层）触发
     仍失败兜底：描述想要的效果，手动模拟第一次执行

   ⚠ 触发条件：loop 跑飞（无限循环）
     一线修复：提醒用户用 Ctrl+C 或 TaskStop 终止
     仍失败兜底：设置 max-runs=10 / max-duration=30m 硬限制

分类: 了解指南
→ 展示参考内容 + 决策速查表
   展示完后停问："看完了，需要执行什么？" → 回到 Step 1 重新分类

   ⚠ 触发条件：用户看完仍不确定做什么
     一线修复：走 Step 4（无匹配），让用户从 6 类中选
     仍失败兜底：直接问"你当前项目是什么场景？"手动匹配
```

### Step 3：流程仲裁【收敛追踪】

Step 1 分类 → Step 2 推荐路径 → 文字停问确认（A 执行 / B 看详情 / C 看其他）→ 执行或展示参考表。"了解指南"分类展示完参考内容后，停问问"要执行什么"→ 有目标回 Step 1 重分类，没有则结束。

**🛑 收敛规则（同 session 同分类重复触发）：**
- 首次拒绝推荐 A → 排除 A，从剩余选项缩小范围再问
- 第二次拒绝 → 排除已拒选项，展示剩余全部选项让用户自选
- 第 3 轮无共识 → 退 Step 4
- 同一 session 同一分类第二次触发 → 加载上次收敛状态（已拒选项），不重置

### Step 4：无匹配

无法分类或用户意图模糊 → 文字停问：

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
| 用户明确说"别问我，直接做" | 还问"是否执行" | 跳过停问，自动选 A |
| 用户只是聊天/吐槽（"今天代码又炸了"） | 分类为"调试 bug" | 确认是否真的需要帮助，还是纯吐槽 |
| 项目没有 git 仓库 | 走审查/PR 路径 | 展示文件级替代方案 |
| 用户连续 2 次拒绝推荐路径 | 继续推销 | 先排除已拒选项缩小范围再问；第 3 轮达不成 → 停，明说"当前推荐都不适合"让用户自述 |
| 两个分类都匹配（如"写个新功能但不知道怎么选"） | 只匹配一个 | 按分类优先规则二次分流：带任务信号→走任务分类给对比结论；纯抽象→了解指南 |
| 参考内容太长（>200 行） | 全部展示 | 按三层折叠规则执行：用户选 A"直接执行"→ 仅路由，0 参考表；走任务分类 → 折叠，仅决策速查 + 反操作清单 + 相关生态行；选"看详情"或分类=了解指南 → 完整展示 |
| 用户贴了代码段但没说意图 | 直接分类"审查代码" | 先问"这段代码做什么？你想审查/调试/还是当参考？"再走对应分类 |
| 用户说"查资料"但实际是调试场景 | 走"了解指南"展示速查表 | 确认意图：真查资料还是排查问题？后者走调试分类 |

### 生态速查（详情 Read [`references/ecosystems.md`](references/ecosystems.md)）

| 生态 | 一句话定位 | 独有亮点 | 代表命令（slash 直调） |
|------|-----------|---------|----------------------|
| Superpowers | 流程纪律 pipeline（设计先行 / TDD / 证据驱动，自动触发） | brainstorming HARD-GATE、subagent-driven-development | `superpowers:brainstorming` / `:writing-plans` / `:test-driven-development` / `:systematic-debugging` / `:verification-before-completion` |
| **ECC** | **最大生态**（271 skill + 92 command + 67 agent，v2.0.0），全栈框架 + 工作流 | 14 框架 build/review/test（react/vue/flutter/python/rust/go/cpp/swift/kotlin 等）/ santa-loop（adversarial 双审）/ gan-*（generator-evaluator）/ orch-*（编排）/ multi-*（并行）/ loop-*（持续）/ cost-* / production-audit / security-scan / agent-payment-x402 | `ecc:react-review` / `:python-review` / `:rust-build` / `:santa-loop` / `:code-review` / `:security-scan` / `:plan` / `:multi-execute` |
| agent-skills | SDLC 闭环 spec→ship，与 SP 重复留独有 | interview-me / idea-refine / doubt-driven-development / source-driven-development / context-engineering | skill 长名调用（spec-driven-development / planning-and-task-breakdown / doubt-driven-development / interview-me）。⚠ Claude Code 侧无 namespace，无 slash，用 skill 长名 |
| mattpocock | 28 单用途小 skill，显式调用为主 | teach / zoom-out / writing-* / grill-* / caveman / design-an-interface | 顶层 skill 长名调用（teach / zoom-out / writing-beats / grill-me / design-an-interface）|
| understand-anything | 代码库 → 知识图谱（8 skill + 子 agent） | graph.json / tour-builder / blast radius | `understand-anything:understand` / `:understand-chat` / `:understand-onboard` / `:understand-diff`（MCP 服务需先 build graph）|
| **gitnexus** | 代码库 → 知识图谱 + 控制流/数据流/taint 分析（MCP 17 工具 + 9 顶层 skill）| MCP：cypher / impact / pdg_query（CDG/RD 边）/ trace / route_map / shape_check / explain / check 等；skill：taint-analysis（source→sink）/ pr-review / refactoring / impact-analysis / pdg-query / debugging / exploring / cli / guide | `gitnexus` MCP + 顶层 `gitnexus-*` skill（taint 在 skill 层非 MCP）|
| ponytail | lazy senior dev 模式（hook 驱动，v4.8.3） | YAGNI / stdlib first / 不加未请求抽象；与 SP 设计先行冲突时的裁决 | SessionStart hook 自动激活；`ponytail:ponytail` / `:ponytail-review` / `:ponytail-audit` |
| caveman | 压缩模式（hook 驱动） | drop 冗余省 ~75% token；与 ponytail 配套 | SessionStart hook 自动激活；`caveman:caveman` / `:cavecrew` / `:caveman-compress` / `:caveman-review` |
| lean-ctx | 上下文压缩 MCP（77 工具 + 10 读模式 + AST 18 语言） | 替代 Read/Grep/Shell/Glob，节省 ~99% 上下文 | MCP 工具 `ctx_read` / `ctx_search` / `ctx_shell` / `ctx_compose` / `ctx_glob` / `ctx_tree` |
| headroom | 上下文压缩 MCP（有损 + hash 取回，v0.23.0） | headroom_compress / retrieve / stats（与 lean-ctx 三层栈） | MCP 工具 `headroom_compress` |
| context7 | 库/框架文档查询 MCP（双实例） | fetch current docs 而非凭训练数据；UI/setup/API 问题 | MCP 工具 `query-docs` / `resolve-library-id` |
| playwright | 浏览器自动化 MCP（双实例） | click / snapshot / network / console / type | MCP 工具 `browser_*` |
| chrome-devtools | 浏览器调试 MCP（ECC 内） | DOM / console / network / perf trace / lighthouse | MCP 工具 `click` / `fill` / `evaluate_script` / `lighthouse_audit` / `performance_*` |
| github | GitHub 操作 MCP（47 工具） | PR / issue / branch / release / code search / commit / copilot review | MCP 工具 `plugin_github_github__*` |
| karpathy | 编码行为规范准则 | 外科手术式改动 / 显式假设 / 可验证验收标准 / 不过度复杂化 | skill `karpathy-guidelines` |
| claude-api | Claude API/SDK 文档 skill（构建 LLM 应用时参考） | 模型 ID / 定价 / streaming / tool use / MCP / caching | skill 按需加载 |
| claude-md-management | CLAUDE.md 维护插件 | revise-claude-md（session 学习回写）/ claude-md-improver（审计改进）| `claude-md-management:revise-claude-md` / `:claude-md-improver` |
| commit-commands | git 工作流插件 | commit / commit-push-pr（一键三连）/ clean_gone（清已删远程分支）| `commit-commands:commit` / `:commit-push-pr` / `:clean_gone` |
| code-review / open-code-review | 代码审查插件 | code-review 本地 diff 多轴评审；open-code-review 走阿里巴巴 `ocr` CLI（行级 + 可自动 apply fix）| `code-review:code-review` / `open-code-review:review` |
| feature-dev | 特性开发插件 | code-architect 出实施蓝图（文件/接口/数据流/build order）/ code-explorer 追执行路径 / code-reviewer | `feature-dev:feature-dev` / `:code-architect` / `:code-explorer` / `:code-reviewer` |
| frontend-design | 反 slop 前端设计 | audit-first 重设计 / 真实设计系统 / 严格 pre-flight check | `frontend-design:frontend-design` |
| skill-creator | skill 生成与优化（含 darwin-skill） | skill-creator（本地 git history 抽模式）/ darwin-skill（9 维 rubric + hill-climbing 自优化） | `skill-creator:skill-creator` / 顶层 `darwin-skill` / `darwin-weekly-audit` |
| claude-code-setup | hook / automation 推荐 | claude-automation-recommender（扫 transcript 推荐 hook）| `claude-code-setup:claude-automation-recommender` |
| example-skills | Anthropic 官方 17 示例 skill（umbrella：anthropic-agent-skills/example-skills/）| 即用工具 + 范例：mcp-builder / web-artifacts-builder / webapp-testing / doc-coauthoring / claude-api / frontend-design / skill-creator / docx / pdf / pptx / xlsx | `example-skills:<name>` |
| last30days | 跨平台趋势研究 skill | Reddit / X / YouTube / TikTok / HN / Polymarket / GitHub 30 天实声 | 顶层 skill `last30days` |
| ❌ codex-security / build-web-apps / openai-developers | **Codex marketplace 独有**，Claude Code 不存在 | ECC 仅部分覆盖：security-scan/security-review（非完整 10 skill 管线）、react-patterns/react-build/react-review（非 6 skill 全链路）、agent-payment-x402（非 5 skill OpenAI 全套） | 用 ECC 内对应 skill + SP 兜底 |
| 全量查询类 | 看全部可用命令/skill 的入口 | 实时反射当前安装内容 | `/help` 或交互终端（内置命令全量） |

> 各生态哲学 / 命令 / 取舍 / 流程对比 / 重叠区处理：用户选 B「看详情」或分类「了解指南」时，Read `references/ecosystems.md` 展开。
>
> ⚠️ **推荐性质**：本表推荐均为推理非实测（重叠优先级=经验判断），详见上方「定位与质量标准 → 证据门槛」。MCP 依赖生态（headroom/context7/playwright/understand-anything）降级见 references「MCP 依赖与降级」节。

### 决策速查

| 你说 | 工具 | 理由 |
|------|------|------|
| "想写个功能" | SP brainstorming 自动启动 | 设计先行 |
| "审查这段代码" | SP requesting-code-review（日常自检）→ `code-review:code-review` 或 `open-code-review:review`（本地 diff/PR 多轴）→ `ecc:security-scan`（安全）→ `ecc:santa-loop`（高风险对抗双审） | 四层递进：自检→结构审查→安全→对抗多 pass |
| "我刚改完，确保没问题" | SP verification-before-completion（日常）→ `ecc:react-test` / `:flutter-test` 等框架 test（合并前）| 先证据检查后系统验证 |
| "写测试" | SP test-driven-development（流程纪律）→ `ecc:<lang>-test`（框架专属） | 流程纪律 + 框架执行 |
| "调试这个 bug" | SP systematic-debugging → `gitnexus:trace` / `:explain`（基于 graph 定位）/ `ecc:<lang>-build`（构建错误）| 4 阶段根因 + graph 辅助 |
| "安全扫描/安全审查" | `ecc:security-scan`（repo 全量）/ `ecc:security-review`（深度）/ `open-code-review:review`（PR/diff） | ECC 是当前最完整安全 skill；高风险用 santa-loop 对抗双审 |
| "写前端应用" | `frontend-design:frontend-design`（反 slop 设计）→ `ecc:react-build` / `:vue-review` / `:multi-frontend`（实现）/ `example-skills:web-artifacts-builder` | 设计→实现全链路 |
| "构建错误" | `ecc:<lang>-build`（cpp/go/rust/kotlin/flutter/gradle 等，框架专属）/ 后端按项目构建纪律（tsc --noEmit / go build 等，见 CLAUDE.md §1.4） | 框架自动检测 |
| "重构/重命名安全" | `gitnexus:rename` / `:impact` / `:refactoring`（基于 graph 的 blast radius）→ `feature-dev:code-architect` 出蓝图 | graph 驱动，避免漏改 |
| "理解陌生代码库" | `gitnexus:query` / `:route_map` / `:explain`（实时 graph）vs `understand-anything`（深度结构化 tour）vs `mattpocock zoom-out`（轻量摘要） | 实时查询选 gitnexus，深度学习选 understand-anything，速览选 zoom-out |
| "每 5 分钟检查" | `/loop` skill（Claude Code 内置） | 最轻量的定时方案 |
| "我刚做完，要发 PR" | `commit-commands:commit-push-pr`（一键三连）或 SP finishing-a-development-branch（选操作） | 前者最快，后者含合并/PR/保留/丢弃选项 |
| "改 CLAUDE.md" | `claude-md-management:revise-claude-md`（session 学习回写）/ `:claude-md-improver`（审计改进）/ `claude-md-audit`（独立审计） | 三件套覆盖改/审计/审计 |
| "配 hook / 自动化" | `claude-code-setup:claude-automation-recommender` | 扫 transcript 推荐 hook |
| "优化 skill 质量" | `darwin-skill`（9 维 rubric + hill-climbing）/ `darwin-weekly-audit`（基线体检）| skill 自优化 |
| "生成新 skill" | `skill-creator:skill-creator` / `example-skills:skill-creator` | 本地 git history 抽模式 |
| "看 Claude API/SDK" | `claude-api` skill | 模型 ID / 定价 / streaming / tool use / caching |
| "查库/框架文档" | `context7` MCP（`query-docs` / `resolve-library-id`） | fetch current docs，不凭训练数据 |
| "一行产品想法写 PRD" | `qiaomu-ai-prd` skill（速读卡 + 约束层 + 验收脚本，AI 可执行） | 重产出可执行 PRD 文档；若要落地实施计划 → SP writing-plans |
| "想看全部可用命令/skill" | `/help` 或交互终端（内置命令全量） | 实时反射当前安装内容，本指南只点代表不穷尽 |

> **审查深度原则**：高风险/重要模块用**循环返工审查**（reject-until-criteria，门下省式）而非单次 review。
>
> 单次轻量 review 跑一遍就过 = 无门下省；高风险（auth/DB schema/架构/安全敏感）需循环兜底。实际执行走 `ecc:santa-loop`（对抗双审，两独立 reviewer 须都 approve 才放行）或 SP requesting-code-review + `code-review:code-review`。`plagiarism-audit` / `multi-review-pipeline` 是查重/文档审查领域同款循环架构（多审查员多轮直到独立终判 PASS）的参考。

---

### 反模式与失败处理

| 场景 | 一线处理 | 仍失败兜底 | 不要做的事 |
|------|---------|-----------|-----------|
| 同时触发 SP brainstorming 和代码审查 | 优先走 SP 流程（设计先行），审查留在后面 | 用户明确说"审查代码"时 SP 的 HARD-GATE 不适用 | 不要两个同时跑——SP 的 HARD-GATE 会阻止写代码，审查需要代码存在 |
| SP 流程太啰嗦，想跳过设计直接写 | 坚持 HARD-GATE：没设计就不能写代码 | 用户说"我很确定不需要设计"→ 清理工作树后交给用户决定 | 不要跳过 SP brainstorming（SP 下游 skill 可能依赖设计文档） |
| 找不到合适 skill | 用 find-skills 按关键词搜，或 `/help` 看全部 | 直接问"你想要什么能力" | 不要花时间背 skill 列表 |
| SP 的 TDD 强制在不适合的项目触发 | 用户说"这个项目不适用 TDD"→ 不要自动触发 test-driven-development | 在项目 CLAUDE.md 声明 "skip TDD" | 不要手动删掉 test-driven-development skill |
| 两个生态同时建议同一件事（审查/验证） | 先用 SP 的轻量版本（requesting-code-review / verification-before-completion） | 仍有问题再上 `ecc:santa-loop`（对抗双审）或 `code-review:code-review` | 不要两个都跑——浪费 token |
| /loop 循环跑飞 | 确认有终止条件（max-runs / max-cost / max-duration） | 关 terminal 强制停 | 不要把 /loop 当背景噪音跑 |
| 同时触发 qiaomu-ai-prd / SP writing-plans（PRD 流程） | qiaomu-ai-prd（生成 AI 可执行 PRD）→ SP writing-plans（基于 PRD 出计划） | 用户只要 PRD 文档不落地则单跑 qiaomu-ai-prd | 不要两个都跑——产出重叠浪费 token |
| 同时触发 ponytail 与 SP（最简 vs 完整流程） | 快速改动 / 原型 / bug 修走 ponytail；新功能 / 完整开发走 SP | 用户要"快速改"但范围 >3 文件 → 重分类回 SP brainstorming | 不要两个 mode 同 session 反复切换——SessionStart hook 决定当轮基调 |
| 同时触发 gitnexus 与 understand-anything（代码库理解） | 实时查询 / 重构 blast radius 选 gitnexus；新项目深度 onboarding / 学习 tour 选 understand-anything | 大仓库 gitnexus build 超时 → 缩子目录或退 mattpocock zoom-out | 不要两个都 build——graph 重复构建浪费 |

### 选型速判

| 你的情况 | 推荐主力 | 原因 |
|---------|---------|------|
| 日常开发功能 | SP | 自动流程兜底，不担心漏步骤 |
| 快速原型/改 bug | ponytail（最简方案）/ SP systematic-debugging（bug） | ponytail 管最简改动；bug 走 SP |
| 团队项目（多语言栈） | SP + ECC（框架 build/review/test + santa-loop 对抗审）+ `code-review:code-review` | SP 管流程纪律；ECC 管框架专属；多轴审查走独立插件 |
| 个人文档项目（如 JavaGuide） | ponytail + 第三方写作 skill（article-writer / chinese-markdown-normalizer / publish-final-check） | SP 的 TDD 强制在此场景不适用；ponytail 管最简实现 |
| 代码质量要求高 | SP requesting-code-review + `ecc:santa-loop`（对抗双审）+ `code-review:code-review`（多轴） | 通用审查走 SP；对抗多 pass 走 santa-loop；结构质量走 code-review |
| 大型重构 / 跨文件改名 | `gitnexus:rename` / `:impact`（graph 驱动 blast radius）+ `feature-dev:code-architect`（蓝图） | graph 保证不漏改；蓝图保证接口契约 |
| 陌生代码库 onboarding | `understand-anything:understand`（深度 tour）或 `gitnexus:explain`（实时查询） | 前者结构化学习路径，后者按需查询 |
| 持续集成/自动化 | `/loop` skill + `claude-code-setup:claude-automation-recommender`（hook 推荐） | Claude Code loop 走 /loop skill；自动化靠 hook |

---

## 进化机制

维护说明（何时更新 / 怎么更新 5 步 / 维护纪律 / 变更记录）见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)。本指南是 living doc，随插件/skill 增删持续更新，触发即改。
