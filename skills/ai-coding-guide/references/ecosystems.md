# 生态详情参考

本文件只在用户要看「为什么推荐 A 而不是 B」时展开。主文件负责路由；本文件负责解释。

主文件路径：`SKILL.md`

---

## 生态角色（Claude Code 当前环境）

### Superpowers

**定位：** 流程纪律层。负责 `brainstorming`、`writing-plans`、`test-driven-development`、`systematic-debugging`、`verification-before-completion` 这类硬门禁流程。

**什么时候优先用：**
- 新功能需要设计
- 已有 spec 需要落地计划
- bug 需要根因分析
- 完工前需要证据驱动验证

**不要把它当成：** 所有小改动的默认入口。小改动先看 `ponytail:ponytail`。

### Matt Pocock skills

**定位：** SDLC 补充层。本机独立 skill 集（来源 Matt Pocock skills 仓库，经 cc-switch 同步），补上 spec、breakdown、review、security、debugging 这类可拆分能力。代表项：`grill-me`、`planning-and-task-breakdown`、`to-prd`、`to-issues`、`review-doc`、`security-and-hardening`、`triage`、`tdd`。注意是独立 skill，不是插件 namespace——调用用裸名（`grill-me`），不要写成 `agent-skills:grill-me`。社区泛称 agent skills，但本机无 agent-skills 插件。

**证据锚点：** 来源标记见 `setup-matt-pocock-skills`（独立 skill，其描述列 `to-issues`/`to-prd`/`triage`/`tdd` 为其管辖）；本机 `~/.cc-switch/skills/` 下裸名存在、无 namespace 前缀。属「官方可证实 + 本机目录可见」级别，非运行时实测。

**什么时候优先用：**
- 已经知道要做 review / security / planning-and-task-breakdown
- 想给 Superpowers 主流程补一个专项环节

**不要把它当成：** 替代 Superpowers 的总流程默认层。两套都能做时，先按主文件路由决定谁做主、谁做补充。

### ponytail / caveman

**定位：** 最简实现层。`ponytail:ponytail` 负责最短工作路径，caveman 负责压缩表达。

**什么时候优先用：**
- 单点小改
- 不值得开完整设计/计划流程
- 用户明确要「快、少、别铺开」

**升级条件：** 一旦改动跨 3 个以上文件、跨模块、开始触及架构边界，就回到主流程。

### claude-plugins-official 补充层

**代表项：** `frontend-design`、`feature-dev:*`、`code-review:*`、`commit-commands:*`。

**作用：** 在主流程确定后，补前端、特性开发、代码审查、提交收尾这些专项动作。`code-review` 面向当前 diff；`review` 面向 PR、分支或指定基线对比；`superpowers:requesting-code-review` 更适合实现完成后请求独立复核。

### ecc 语言专项层

**代表项：** `ecc:*review*`、`ecc:*build*`。

**作用：** 当任务已经明确落在某个语言或框架上时，提供更窄的 reviewer 或 build resolver。构建失败优先用 `ecc:<lang>-build` slash command；slash command 不在但 resolver agent 存在时，才派 `ecc:<lang>-build-resolver` agent。

**用法：** 先确定任务类型，再决定是否需要专项层；不要先按语言插件倒推任务。

### 上下文 / 理解层

**代表项：** `lean-ctx`、`understand`、`gitnexus-*`。

**作用：** 看结构、看依赖、看影响范围、压缩上下文。

**默认顺序：** 先 `lean-ctx`，再按需要上 `understand` 或 `gitnexus-*`。

---

## 重叠区处理

| 冲突场景 | 默认裁决 | 原因 |
|---|---|---|
| `superpowers:brainstorming` vs `ponytail:ponytail` | 新功能走 Superpowers，小改动走 ponytail | 先按任务规模分层 |
| `superpowers:writing-plans` vs `planning-and-task-breakdown` | 已有 spec 默认 `superpowers:writing-plans` | 计划质量和落地细节更稳 |
| `superpowers:requesting-code-review` vs `review` / `code-review` | 当前 diff 走 `code-review`；PR/分支/指定基线走 `review`；实现完成后请求复核再用 `superpowers:requesting-code-review` | 审查入口和流程门禁不是同一层 |
| `security-review` / `security-and-hardening` vs 通用 review | 高风险任务用实际 reviewer + `security-review`；需要加固方案再叠 `security-and-hardening` | 安全审查和加固建议是额外维度，不是替代关系 |
| `frontend-design` vs `feature-dev:*` | UI/页面骨架先 `frontend-design`，功能实现再 `feature-dev:*` | 先定界面，再做交互 |
| `lean-ctx` vs `understand` | 日常查代码先 `lean-ctx`，大范围建模再 `understand` | 成本更低 |

---

## 降级路径

| 默认路径不可用 | 降级到 |
|---|---|
| `grill-me` 不在 | `superpowers:brainstorming` 或手动单问单答 |
| `security-review` 不在 | 实际 reviewer + `security-and-hardening`，并明示缺少安全审查入口 |
| 专项 build slash command 不在 | 对应 build resolver agent；再不在则项目构建原文 + 手动排查 |
| `understand` / `gitnexus-*` 不在 | 继续用 `lean-ctx` 聚焦读取；`lean-ctx` 也不可用才退原生搜索 + 精读文件 |
| `/loop` 不可用 | 明示不可用，改手动执行 |

---

## 维护时要核的点

- 当前会话 reminder 里有没有该 skill
- `~/.claude/skills/` 是否存在独立 skill
- `~/.claude/plugins/cache/` 是否存在插件附带 skill
- 推荐语气是否越界成「硬事实」
- 主文件是否又长回百科全书
