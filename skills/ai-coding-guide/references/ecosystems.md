# 生态详情参考（生态格局 + 重叠裁决 + 降级 + 迁移闸门）

本文件只在用户问「为什么推荐 A 而不是 B」「X 和 Y 区别」「能不能把外部做法吸收进来」时展开。`routing.md` 负责路由；本文件负责生态解释与吸收闸门。

生态格局以 wayfinder 盘点拍板为准（2026-08-18 ticket 01/02）：套件不拆单件，路由只接门面。

---

## 生态角色（当前环境）

### mattpocock-skills：主力套件（条件路径）

依据当前插件 v1.2.3 的 README、manifest 和各 `SKILL.md` frontmatter，先按“谁启动”分层，再按任务选择，不把 25 个 skill 当成 25 个必走步骤。

**user-invoked：必须提醒用户手动敲命令并等待**

| skill | 手动命令 | 路由用途 |
|---|---|---|
| `ask-matt` | `/ask-matt` | 不知道下一步，询问 Matt 内部入口；只做选择，不替用户执行整套流程 |
| `grill-with-docs` | `/grill-with-docs` | 非机械代码变更第一跳；对齐需求、术语并写入 CONTEXT / ADR |
| `triage` | `/triage` | 外部原始 bug / request 尚未整理成可执行任务；不处理 `/to-tickets` 自产 Ticket |
| `improve-codebase-architecture` | `/improve-codebase-architecture` | 扫描代码库，找值得深化的结构候选；选中后回主流程 |
| `setup-matt-pocock-skills` | `/setup-matt-pocock-skills` | 仓库首次配置 issue tracker、标签和文档布局；不按任务重复运行 |
| `to-spec` | `/to-spec` | 已达成共识后固化 Spec；不重新采访、不填补空白决定 |
| `to-tickets` | `/to-tickets` | 跨会话、并行、多人，或需要显式阻塞关系时按用户结果拆 Ticket；单会话小任务可跳过 |
| `implement` | `/implement` | 按 Spec / Ticket 实现；在预先约定 seam 按需驱动 TDD，提交前必须完成 code-review；commit 仍受本地确认线约束 |
| `wayfinder` | `/wayfinder` | 目标大且路线不清；画 Decision Ticket 地图后回 `/to-spec` |
| `grill-me` | `/grill-me` | 无工作目录的非仓库想法澄清；仓库编码优先 `/grill-with-docs` |
| `handoff` | `/handoff` | 必须跨 Harness、目录或人员交接时生成临时交接物；普通会话过长先压缩 |
| `teach` | `/teach` | 跨多会话系统学习；编码域只在用户明确点名时保留，否则转 `learning-guide` |
| `to-questionnaire` | `/to-questionnaire` | 答案在客户、同事或专家手中；生成问卷，不让当前用户猜答案 |
| `wait-what` | `/wait-what` | 上一条回答没听懂时只重讲当前消息，不建立永久风格规则 |

**model-invoked：可自动调用；路由始终显示手动命令，用户明确要自己练时等待**

| skill | 手动命令 | 路由用途 |
|---|---|---|
| `prototype` | `/prototype` | 讨论无法回答设计问题时做可抛弃、可追溯原型 |
| `diagnosing-bugs` | `/diagnosing-bugs` | 难复现、原因不明的 bug / 性能回归；先建立变红反馈环 |
| `research` | `/research` | 缺少外部事实或官方依据时查高信任一手资料 |
| `tdd` | `/tdd` | 独立测试先行；`implement` 内部已覆盖时不重复手动调用 |
| `domain-modeling` | `/domain-modeling` | 术语、领域模型持续混乱或漂移 |
| `codebase-design` | `/codebase-design` | 模块、接口、Seam、深模块设计问题 |
| `code-review` | `/code-review` | 固定范围 Diff 的 Standards + Spec 双轴审查 |
| `resolving-merge-conflicts` | `/resolving-merge-conflicts` | 正在合并两组代码时按双方历史解决冲突 |
| `wizard` | `/wizard` | 必须由人登录、输入凭证或执行控制台步骤时生成向导 |
| `grilling` | `/grilling` | 被其他入口复用的分轮访谈底层能力；通常不作为第一跳 |
| `writing-for-agents` | `/writing-for-agents` | 编写或压缩 Skill、AGENTS.md、CLAUDE.md、Spec 等 Agent 文档 |

**主流程与跳步：**

```text
非机械代码变更：用户手动 /grill-with-docs →（需要固化需求时，用户手动 /to-spec）→ 实现
1-2 步单文件机械改：保留精简路径，不强行 grilling
跨会话 / 并行 / 多人 / 需显式阻塞关系：用户手动 /to-tickets
已有 Spec / Ticket：用户手动 /implement
实现内部：在预先约定 seam 按需 `/tdd` → 提交前必须 `/code-review`
独立测试先行或独立审查：才单独手动调用 `/tdd` / `/code-review`
路径本身不清且规模过大：先用户手动 `/wayfinder`，再回 `/to-spec`
```

`user-invoked` skill 可以驱动 `model-invoked` skill，但不能自动调用另一个 `user-invoked` skill；本路由把第一跳和后续 user-invoked 入口都交给用户逐个手动调用。`model-invoked` skill 可自动走，但路由始终显示对应手动命令，用户明确要自己练时才等待调用。

### superpowers：备用流程套件（2026-08-19 已卸载，仅留生态对比认知，路由不再指向）

- 单环手法借用：`brainstorming` / `systematic-debugging` / `test-driven-development` / `writing-plans` / `requesting-code-review` / `verification-before-completion` / `using-git-worktrees`
- 套件随附：executing-plans / receiving-code-review / subagent-driven-development / dispatching-parallel-agents / finishing-a-development-branch / writing-skills / using-superpowers（元 skill，每会话自动注入）

### ponytail：反过度设计层（条件路径）

- 门面 `ponytail`（最小实现、YAGNI）；随附 audit/debt/gain/help/review

### caveman：输出压缩（条件路径）

- 压缩句型与 cavecrew 小编辑 agent；coding 相关件（cavecrew/caveman-commit/caveman-review）随套件存活

### 官方/内置层

- `code-review`（轻量审查）、`security-review`（高风险双审）、`run`（横切收尾验证）、`/loop`（循环任务）、`claude-api`（Claude API 参考）、`skill-creator`（造 skill）
- 插件条件路径：`open-code-review:review`（ocr 独立重量审查）、`commit-commands:*`（提交）

### 独立工具（存活独立，不接路由）

- `ai-readable-project`（让 AI 看懂项目）、`better-harness`（harness 生命周期审查）、`frontend-design`（官方插件前端设计，未被前端视觉子路径点名，用户显式调用）
- `claude-md-management:revise-claude-md` / `claude-md-improver`（CLAUDE.md 维护）

### 理解 / 调研层

- `lean-ctx`（读结构，成本最低）/ `gitnexus-*`（调用链/影响面，gitnexus-guide 为参考层不直达）
- `agent-reach`（存证调研）/ `last30days`（近 30 天社区动态）

---

## 重叠区处理

| 冲突场景 | 默认裁决 | 原因 |
|---|---|---|
| `superpowers:brainstorming`（条件） vs 手动澄清 | 会话可调用且任务复杂 → Superpowers；否则开工问询 + `expose-unknowns` 判级 | 先按运行时可用性分层，再按任务规模 |
| `superpowers:writing-plans`（条件） vs `to-prd`/`to-issues` | 默认手动拆切片 + PLAN.md；用户只想整理需求项 → `to-prd` / `to-issues` | 计划质量优先但不过度依赖插件 |
| `code-review`（内置） vs `ocr review`（条件） vs Matt `/code-review`（model-invoked） | 轻量走内置 `code-review`；独立重量审查/提交前门禁在可用时叠加；路由始终显示 Matt 手动命令，用户明确要自己练时等待 | 审查入口和流程门禁不是同一层 |
| 内置 `security-review` vs 通用 review | 高风险任务用实际 reviewer + 内置 `security-review` 双审 | 安全审查是额外维度，不是替代关系 |
| `frontend-design`（独立件） vs `hallmark`/`impeccable` | 前端视觉默认 `hallmark`（新页面）/ `impeccable`（提质）；`frontend-design` 用户显式调用才用 | 子路径已点名门面，不双头 |
| `lean-ctx` vs `gitnexus-*` | 日常查代码先 `lean-ctx`（成本最低），调用链/影响范围再上 `gitnexus-*` | 成本更低 |
| Superpowers 全套（条件） vs mattpocock 拆单（user-invoked） vs 精简路径 | 复杂/陌生/高风险 → 状态机或 SP 单环；任务需要某一环 → 拆单用 matt；单点/机械 → 精简路径 | 流程深度由任务复杂度定，判断导向不设硬门槛（`routing.md` Step 0.4） |
| 交付状态机（本系统） vs Superpowers 全套（条件） | 重任务 / 跨会话 / 要脚本强制 → 本系统状态机；只需单环手法 → SP 单环 | 状态机管骨架门禁，SP 管手法，不双套流程 |

---

## 降级路径

| 默认路径不可用 | 降级到 |
|---|---|
| `superpowers:*` 不可用 | 手动流程：开工问询 + 缺口收齐 + 手动计划/实现（复杂走 `code-change-workflow`） |
| `ocr review` 不可用 | 通用 Code Reviewer agent + 内置 `code-review` / `security-review` |
| 专项 build slash command 不可用 | 项目构建原文 + 手动排查 |
| `gitnexus-*` 不可用 | 继续用 `lean-ctx` 聚焦读取；`lean-ctx` 也不可用才退原生搜索 + 精读文件 |
| `/loop` 不可用 | 明示不可用，改手动执行 |
| `hallmark` / `impeccable` 不可用 | 手动给方向选项 + 按项目栈直接实现，收尾自查 AI 味 |
| `mattpocock-skills:*` 不可用 / 用户不启用 | grilling → 开工问询 + `expose-unknowns` 判级；diagnosing-bugs → `code-change-workflow` §2；tdd → 手动红绿小步改；code-review → 内置 `code-review` |

---

## 轻量迁移闸门

用户拿外部 AI 编码文章/实践问"能不能优化进路由"时，先判它是否属于**路由器职责**。本路由只吸收"选型、分类、证据、fallback、维护"规则，不承接具体项目开发流水线。

| 可迁移 | 写入位置 | 不迁移 |
|---|---|---|
| 触发词、意图分类、优先级裁决 | `routing.md` Step 1 / Step 3 | 项目专属工具链脚本 |
| 推荐路径的输入/输出/失败分支 | 对应分类的主路径 / Fallback | Figma/TAPD/CGI/模拟器等业务流程 |
| 证据分级、先查后推荐、死引用处理 | 环境自检 / 证据门槛 / MAINTENANCE | 全量 TECH_SPEC 模板 |
| 跨会话收尾、docs/memory 同步 | 知识收尾 / MAINTENANCE | 红线 YAML 全套机制 |

迁移判定：能让未来路由更准、更少幻觉、更容易维护 → 加；只让某个项目执行更完整 → 不进路由，建议做项目专属 skill。

---

## 重机制黑名单

| 外部做法 | 本路由处理 | 原因 |
|---|---|---|
| 8 阶段 feature-dev 流水线 | 只抽象成"有需求文档/开发新功能/验证/知识收尾"路由 | 路由器不替代下游执行 skill |
| 项目 wiki 三级知识库 | 只保留"理解代码先 lean-ctx/gitnexus，完成后 neat-freak" | 项目地图应在项目内维护 |
| TECH_SPEC.md 完整模板 | 不内置；仅建议知识收尾时按项目需要沉淀 | 模板绑定项目复杂度 |
| 红线 YAML + 分阶段加载 | 不内置；保留 CHECKPOINT + 风险闸门矩阵 | 对路由层过重 |
| 模拟器/浏览器/构建专用验证 | 不内置；路由到 `run` / 相关 test/lint/build / 下游测试 skill | 验证细节由项目和语言决定 |

---

## 维护时要核的点

- 当前会话 reminder 里有没有该 skill
- `~/.claude/skills/` 是否存在独立 skill
- 插件是否启用以 `settings.json` 的 `enabledPlugins` 为准
- 推荐语气是否越界成「硬事实」
- 路由文件是否又长回百科全书

<!-- 吸收合并自 ai-coding-guide v1.9.0 references/ecosystems.md + cheatsheet.md，2026-08-18：ecc/understand-anything 已删清、/devflow 改指本系统状态机、决策速查弃（与 routing.md 重复） -->
