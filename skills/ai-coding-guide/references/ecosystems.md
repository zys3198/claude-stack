# 生态详情参考

本文件只在用户要看「为什么推荐 A 而不是 B」时展开。主文件负责路由；本文件负责解释。

主文件路径：`SKILL.md`

---

## 生态角色（Claude Code 当前环境）

**全局规则（2026-08-13 起）：** 所有插件条目（`superpowers:*` / `ecc:*` / `ponytail:*` / `commit-commands:*` 等）一律按**条件路径**处理——当前会话可调用清单里出现才走，否则走各分类 Fallback。判定依据：`settings.json` 的 `enabledPlugins` + 当前会话 `Available skills` 清单；磁盘 cache 只证明「已安装/可候选」。

### Superpowers：完整流程套件（条件路径）

**定位：** 完整软件开发流程套件。`brainstorming`（需求澄清）→ `writing-plans`（设计/计划）→ `test-driven-development`（执行）→ `requesting-code-review`（审查）→ `verification-before-completion`（验证）一条完整链。

**什么时候才值得走全套（会话可调用时）：**
- 复杂项目、陌生代码库、高风险改动、跨模块设计
- 已有 spec 需要落地完整计划
- 完工前需要证据驱动验证

**什么时候不要走：** 单点改动、机械任务、强模型已能自做的基础步骤（读项目、找调用链、跑基础测试）。任务不够复杂时，全套流程从保护变负担（依据：JavaGuide 2026-08《强模型时代，AI 编程 Skills 还有必要装吗？》——Superpowers 容易让小任务背上过重流程）。

**默认替代（会话不可调用时）：** 开工问询 + Step 0.7 缺口收齐 + 手动计划/实现；复杂/高风险走 `code-change-workflow`。不要把插件流程写死成所有任务的默认链。

### mattpocock-skills：轻量工具箱（user-invoked，条件路径）

**定位：** 可拆开使用的小 skill 组合，不默认要求任务走完同一条流程。哪个环节反复出错就只补哪块，任务变复杂再把几个组合起来。

**常用单环：**
- `grilling` — 动手前持续追问需求（一次一问，能查的自己查、取舍的交给用户），减少方向错误
- `diagnosing-bugs` — bug 定位
- `tdd` — 红绿重构
- `code-review` — 提交前检查

**用法：** 任务需要某一环时单独启用，不整套启用。模型写代码够快时返工多发生在开工太早（需求没定就动手），所以需求模糊时先 `grilling`。

**⚠️ user-invoked 提醒：** mattpocock-skills 插件版模型无法自动调用（需用户手动启用）。路由到这些 skill 时必须明确提醒用户手动启用（不能自己调就提示用户调用）。

### devflow：重任务状态机（直达路径）

**定位：** Tencent/LoopForge 脚本化状态机，2026-08-18 落地为本机「重任务并行通道」（官方原版 + 规则层定制）。复杂项目 / 陌生代码库 / 高风险改动 / 跨模块设计 / 重任务跨会话 → Step 0.4 全套档主路径。澄清 → 设计 → 执行 → 审查 → 测试 → 总结，脚本写 `workflow-state.json`，断点可续跑。

**用法：** 口令必须明说规模 small/medium/large，不说会被自判 small（canary 实测）；断点续跑已装未实测，首次真断线即验收。与 Superpowers 分工：devflow 管骨架（阶段/产物/门禁），SP 单环管手法（brainstorming / TDD / verification）；进了 devflow 不另套 SP 完整链。

### 顶层独立 skill（直达路径）

本机 `~/.claude/skills/` 下的裸 skill 为直达路径（96 项全库审计 2026-08-13：全部当前会话可见）。与路由相关的代表项：

- `ai-coding-coach`（学习型开发）、`expose-unknowns`（判级）、`lean-ctx`（读代码）、`gitnexus-*`（调用链/影响面）、`code-change-workflow`（复杂/高风险改动流程）、`neat-freak`（知识收尾）、`guide-skill-auditor`（十查审查 guide）、`darwin-skill`（skill 优化）、`to-prd` / `to-issues`（需求整理）、`article-writer` / `chinese-markdown-normalizer`（写作域）、`last30days`（舆情调研）。
- 前端视觉直达：`hallmark`（新页面/redesign）、`impeccable`（提质/审计）、`emil-design-eng`（动画综合）、`improve-animations`（全库动画改造）、`find-animation-opportunities`（找该动哪）、`shadcn-vue-guide`（Vue 项目已采用时）、`apple-design`（Apple 风格参考）。
- 历史：Matt Pocock 系独立 skill 经 2026-07 skill 精简审计大部分已移 `~/.cc-switch/skills/_weak-model-backup/`（`grill-me` / `triage` / `tdd` / `setup-matt-pocock-skills` / `planning-and-task-breakdown` 等）；`review-doc` / `security-and-hardening` / `simplify` / `request-refactor-plan` 的去留见全库审计报告（2026-08-13），用户拍板前不再作为本指南直达项。

### ponytail / caveman

**定位：** 最简实现层（条件路径）+ 全局表达模式。`ponytail:ponytail` 负责最短工作路径（当前会话可调用才走；默认替代=直接最小改动）；`caveman` 是全局输出模式开关，不进路由面。

**升级条件：** 一旦改动跨 3 个以上文件、跨模块、开始触及架构边界，就回到主流程。

### claude-plugins-official 补充层（条件路径）

**代表项：** `frontend-design`、`feature-dev:*`、`code-review:*`、`commit-commands:*`。

**作用：** 在主流程确定后，补前端、特性开发、代码审查、提交收尾这些专项动作。

**frontend-design 实测状态（2026-08-13）：** 候选第一跳测试 FAIL——当前会话 `Unknown skill: frontend-design:frontend-design`，`settings.json` 无 `enabledPlugins`。故前端视觉默认走本机裸 skill（`hallmark` / `impeccable` 系），`frontend-design` 仅在启用后重测通过才可升级为默认。

### ecc 语言专项层（条件路径）

**代表项：** `ecc:*review*`、`ecc:*build*`。

**作用：** 当任务已经明确落在某个语言或框架上时，提供更窄的 reviewer 或 build resolver。构建失败优先用 `ecc:<lang>-build` slash command；slash command 不在但 resolver agent 存在时，才派 `ecc:<lang>-build-resolver` agent。会话不可调用 → 跑项目构建命令按错误原文排查。

**用法：** 先确定任务类型，再决定是否需要专项层；不要先按语言插件倒推任务。

### 上下文 / 理解层

**代表项：** `lean-ctx`、`gitnexus-*`（直达）。

**作用：** 看结构、看依赖、看影响范围、压缩上下文。

**默认顺序：** 先 `lean-ctx`，调用链接 `gitnexus-*`。

---

## 重叠区处理

| 冲突场景 | 默认裁决 | 原因 |
|---|---|---|
| `superpowers:brainstorming`（条件） vs 手动澄清 | 会话可调用且任务复杂 → Superpowers；否则开工问询 + `expose-unknowns` 判级 | 先按运行时可用性分层，再按任务规模 |
| `superpowers:writing-plans`（条件） vs `to-prd`/`to-issues` | 默认手动拆切片 + PLAN.md；用户只想整理需求项 → `to-prd` / `to-issues` | 计划质量优先但不过度依赖插件 |
| `code-review`（内置） vs `ecc:*review*`（条件） vs `ocr review`（条件） | 轻量走内置 `code-review`；语言专项/独立重量审查在会话可调用时叠加 | 审查入口和流程门禁不是同一层 |
| 内置 `security-review` vs 通用 review | 高风险任务用实际 reviewer + 内置 `security-review` 双审 | 安全审查是额外维度，不是替代关系 |
| `frontend-design`（候选 FAIL） vs `hallmark`/`impeccable` | 前端视觉默认 `hallmark`（新页面）/ `impeccable`（提质）；候选重测通过再议 | 实测当前会话不可调用，不伪装直达 |
| `lean-ctx` vs `gitnexus-*` | 日常查代码先 `lean-ctx`（成本最低），调用链/影响范围再上 `gitnexus-*` | 成本更低 |
| Superpowers 全套（条件） vs mattpocock 拆单（user-invoked） vs 直接最小 | 复杂/陌生/高风险 → 全套；任务需要某一环 → 拆单用 matt；单点/机械 → 直接最小 | 流程深度由任务复杂度定，不全套兜底 |
| `/devflow` 全套（直达） vs Superpowers 全套（条件） | 重任务 / 跨会话 / 要脚本强制 → `/devflow`；只需单环手法 → SP 单环 | devflow 管骨架门禁，SP 管手法，不双套流程 |

---

## 降级路径

| 默认路径不可用 | 降级到 |
|---|---|
| `superpowers:*` 不可用 | 手动流程：开工问询 + 缺口收齐 + 手动计划/实现（复杂走 `code-change-workflow`） |
| `ecc:*review*` 不可用 | 通用 Code Reviewer agent + 内置 `code-review` / `security-review` |
| 专项 build slash command 不可用 | 项目构建原文 + 手动排查 |
| `gitnexus-*` 不可用 | 继续用 `lean-ctx` 聚焦读取；`lean-ctx` 也不可用才退原生搜索 + 精读文件 |
| `/loop` 不可用 | 明示不可用，改手动执行 |
| `/devflow` 不可用 | 手动流程：开工问询 + 缺口收齐 + 手动计划/实现（复杂走 `code-change-workflow`；`superpowers:*` 链为条件路径） |
| `hallmark` / `impeccable` 不可用 | 手动给方向选项 + 按项目栈直接实现，收尾自查 AI 味 |
| `mattpocock-skills:*` 不可用 / 用户不启用 | grilling → 开工问询 + `expose-unknowns` 判级；diagnosing-bugs → `code-change-workflow` §2 / `superpowers:systematic-debugging`（条件）；tdd → 手动红绿小步改；code-review → 内置 `code-review` |

---

## 维护时要核的点

- 当前会话 reminder 里有没有该 skill
- `~/.claude/skills/` 是否存在独立 skill
- `~/.claude/plugins/cache/` 是否存在插件附带 skill；`settings.json` 的 `enabledPlugins` 是否启用
- 推荐语气是否越界成「硬事实」
- 主文件是否又长回百科全书
