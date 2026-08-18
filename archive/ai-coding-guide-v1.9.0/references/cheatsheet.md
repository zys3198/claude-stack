# 速查表（决策 + 生态 + 反模式）

本文件只在用户要看「为什么推荐 A 而不是 B」「我该说什么触发什么」时展开。主文件负责路由；本文件负责速查。

主文件路径：`SKILL.md`

---

## 决策速查（用户原话 → 默认建议）

| 你说 | 默认建议 |
|---|---|
| 「想写个功能」 | 开工问询 + 缺口收齐 → 轻量确认目标：范围小直接实现，跨模块/要设计先给实现计划确认；需求模糊先 `expose-unknowns` 判级；复杂/高风险走 `code-change-workflow`（插件流程 `superpowers:*` / `ponytail:ponytail` 为条件路径，当前会话可调用才走） |
| 「做个页面/页面太丑/加个动画」 | 前端视觉子路径：方向未定先给 2-3 个方向选项问用户 → `hallmark`（新页面）/ `impeccable`（提质）；动画走 `emil-design-eng` 系；方向已定直接实现，组件库优先复用项目现有依赖 |
| 「我想自己能力提高 / 不想依赖 AI」 | `ai-coding-coach`：你先想方案，我纠偏，对照标杆，最后讲 why |
| 「暴露未知 / 判级 / 这需求我没思路 / 反考我」 | `expose-unknowns`：判四象限 → 按级澄清 → 任务后反考 |
| 「我有 PRD，下一步怎么做」 | 手动拆 4-6 切片 + PLAN.md（`code-change-workflow` §3）；`superpowers:writing-plans` 为条件路径；只想整理需求项 → `to-prd` / `to-issues` |
| 「帮我 review」 | 当前 diff/分支/PR 走 `code-review`（内置）；指定文件/代码块走通用 Code Reviewer；高风险加内置 `security-review` 双审（`ecc:*review*` / `ocr review` 为条件路径） |
| 「这个 bug 怎么回事」 | `code-change-workflow` §2：失败测试/最小复现 → 定位根因（查所有调用方）→ 修复 → 验证（`superpowers:systematic-debugging` 为条件路径） |
| 「改个小文案」 | 直接最小改动，不弹 A/B/C（`ponytail:ponytail` 为条件路径）；超出 3 文件重新分类 |
| 「build 报错」 | 跑项目构建命令按错误原文排查（`ecc:*build*` 为条件路径） |
| 「这库怎么结构/X 怎么工作」 | 先 `lean-ctx`，调用链 `gitnexus-exploring` |
| 「帮我提交/发 PR」 | 手动 git + `git diff --cached --stat` 展示待确认（`commit-commands:*` 为条件路径，push 类一条命令不可逆跑前确认） |
| 「同步一下 / 整理文档 / 更新记忆 / 新人能接手」 | `neat-freak`：知识库收尾，不替代代码重构 |
| 「这篇 AI 编码文章/实践能不能优化进指南」 | 走「路由指南维护」：先判断是否值得迁移；小修最小改+审计；行为变化才上 `darwin-skill`（`superpowers:writing-skills` 为条件路径） |
| 「审查/优化这个 guide skill」 | `guide-skill-auditor`：十查静态体检 + 子代理路由基线 + P0/P1/P2 分级修复 |
| 「SP 和 agent-skills 区别」 | 展开 `references/ecosystems.md`，再问当前要执行什么 |
| 「最近 X 有什么更新/社区在讨论什么」 | `last30days`（编码域调研，时间敏感的舆情/动态；与 `lean-ctx` 读代码、`agent-reach` 存证调研不重叠） |

---

## 生态速查（详情见 `references/ecosystems.md`）

| 能力域 | 默认主路径 | 何时用 |
|---|---|---|
| 流程纪律 | 手动 + `code-change-workflow`（复杂/高风险） | 计划、调试、验证、审查；`superpowers:*` 为条件路径（当前会话可调用才走） |
| 学习型开发 | `ai-coding-coach` | 用户要提升自己 AI coding 能力、先自己想方案、对照最优实现、讲 why |
| SDLC 补充 | `to-prd` / `to-issues` | 需求整理为 PRD/issue；其余 Matt 系去留以全库审计报告为准 |
| 快速小改 | 直接最小改动 | 小范围改动、YAGNI、最短路径（`ponytail:ponytail` 为条件路径） |
| 前端/体验 | `hallmark` / `impeccable` / `emil-design-eng` 系 | 视觉方向、提质、动效；插件 `frontend-design` 当前会话不可调用（候选测试 FAIL），不写默认 |
| 语言专项 | `ecc:*review*` / `ecc:*build*`（条件路径） | 语言或框架专用 reviewer / build resolver，会话可调用才用 |
| 代码理解 | `lean-ctx` / `gitnexus-*` | 查结构、看影响范围、压缩上下文 |
| 文档写作 | `article-writing-guide` | 中文技术文章/教程写、审、润色、发布前总路由 |
| 指南维护 | `guide-skill-auditor` / `darwin-skill` | 外部 AI 编码实践、插件变化、死引用修复要进本指南 |

---

## 反模式与失败处理

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 用户只是问名词解释 | 直接解释 | 误拉进 A/B/C 执行选择 |
| 用户说「直接做」 | 跳过 AskUserQuestion | 继续追问流程选择 |
| 高风险审查 | 实际 reviewer / 内置 `code-review` + 内置 `security-review` 双审 | 只做一轮浅审或把未装插件写成默认 |
| 小改动开始跨模块 | 升级到「开发新功能」 | 硬留在「快速改动」 |
| 证据不足影响主推荐 | 停下来问用户 | 拍脑袋补全 |
| 外部 AI 编码文章很完整 | 先过轻量迁移闸门 | 把项目专属流水线整段塞进路由器 |
| 维护本指南 | 先补 RED 场景，再改 SKILL.md | 先改正文，事后才补测试 |
| 插件 skill 不在当前会话 | 走该分类 Fallback（手动/裸 skill） | 伪装直达、把插件写死为默认路径 |

---

## 轻量迁移闸门

用户拿外部 AI 编码文章/实践问"能不能优化进本指南"时，先判它是否属于**路由器职责**。本指南只吸收"选型、分类、证据、fallback、维护"规则，不承接具体项目开发流水线。

| 可迁移 | 写入位置 | 不迁移 |
|---|---|---|
| 触发词、意图分类、优先级裁决 | Step 1 / Step 3 | 项目专属工具链脚本 |
| 推荐路径的输入/输出/失败分支 | 对应分类的主路径 / Fallback | Figma/TAPD/CGI/模拟器等业务流程 |
| 证据分级、先查后推荐、死引用处理 | 环境自检 / 证据门槛 / 维护规则 | 全量 TECH_SPEC 模板 |
| 跨会话收尾、docs/memory 同步 | 知识收尾 / MAINTENANCE | 红线 YAML 全套机制 |

迁移判定：能让未来路由更准、更少幻觉、更容易维护 → 加；只让某个项目执行更完整 → 不进本指南，建议做项目专属 skill。

---

## 重机制黑名单

| 外部做法 | 本指南处理 | 原因 |
|---|---|---|
| 8 阶段 feature-dev 流水线 | 只抽象成"有需求文档/开发新功能/验证/知识收尾"路由 | 路由器不替代下游执行 skill |
| 项目 wiki 三级知识库 | 只保留"理解代码先 lean-ctx/gitnexus，完成后 neat-freak" | 项目地图应在项目内维护 |
| TECH_SPEC.md 完整模板 | 不内置；仅建议知识收尾时按项目需要沉淀 | 模板绑定项目复杂度 |
| 红线 YAML + 分阶段加载 | 不内置；保留 CHECKPOINT + 反模式表 | 对路由指南过重 |
| 模拟器/浏览器/构建专用验证 | 不内置；路由到 `run` / 相关 test/lint/build（`superpowers:verification-before-completion` 为条件路径）/ 下游测试 skill | 验证细节由项目和语言决定 |
