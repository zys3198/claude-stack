# 速查表（决策 + 生态 + 反模式）

本文件只在用户要看「为什么推荐 A 而不是 B」「我该说什么触发什么」时展开。主文件负责路由；本文件负责速查。

主文件路径：`SKILL.md`

---

## 决策速查（用户原话 → 默认建议）

| 你说 | 默认建议 |
|---|---|
| 「想写个功能」 | 默认先 `superpowers:brainstorming`；模糊先 `grill-me` 压清问题；清楚且跨模块再 `superpowers:writing-plans`；很小走 `ponytail:ponytail` |
| 「我想自己能力提高 / 不想依赖 AI」 | `ai-coding-coach`：你先想方案，我纠偏，对照标杆，最后讲 why |
| 「暴露未知 / 判级 / 这需求我没思路 / 反考我」 | `expose-unknowns`：判四象限 → 按级澄清 → 任务后反考 |
| 「我有 PRD，下一步怎么做」 | `superpowers:writing-plans` |
| 「帮我 review」 | 当前 diff/分支/PR 走 `code-review` 或 `review`；指定文件/代码块走语言 reviewer 或通用 Code Reviewer；高风险加 `security-review` |
| 「这个 bug 怎么回事」 | `superpowers:systematic-debugging` |
| 「改个小文案」 | `ponytail:ponytail` |
| 「build 报错」 | 先用专项 slash command（如 `ecc:react-build`）；没有再派 build resolver agent；仍无则回构建原文 |
| 「这库怎么结构/X 怎么工作」 | 先 `lean-ctx`，大范围 `understand`，调用链 `gitnexus-exploring` |
| 「帮我提交/发 PR」 | `commit-commands:commit-push-pr`；长分支收尾 `superpowers:finishing-a-development-branch` |
| 「同步一下 / 整理文档 / 更新记忆 / 新人能接手」 | `neat-freak`：知识库收尾，不替代代码重构 |
| 「这篇 AI 编码文章/实践能不能优化进指南」 | 走「路由指南维护」：先判断是否值得迁移；小修最小改+审计；行为变化才上 `superpowers:writing-skills` + `darwin-skill` |
| 「审查/优化这个 guide skill」 | `guide-skill-auditor`：九查静态体检 + 子代理路由基线 + P0/P1/P2 分级修复 |
| 「SP 和 agent-skills 区别」 | 展开 `references/ecosystems.md`，再问当前要执行什么 |
| 「最近 X 有什么更新/社区在讨论什么」 | `last30days`（编码域调研，时间敏感的舆情/动态；与 `lean-ctx` 读代码、`research` 存证调研不重叠） |

---

## 生态速查（详情见 `references/ecosystems.md`）

| 能力域 | 默认主路径 | 何时用 |
|---|---|---|
| 流程纪律 | `superpowers:*` | 新功能设计、计划、TDD、调试、验证 |
| 学习型开发 | `ai-coding-coach` | 用户要提升自己 AI coding 能力、先自己想方案、对照最优实现、讲 why |
| SDLC 补充 | Matt Pocock skills | spec / review / security / breakdown 这类补充能力 |
| 快速小改 | `ponytail:ponytail` | 小范围改动、YAGNI、最短路径 |
| 前端/体验 | `frontend-design` / `feature-dev:*` | UI、前端特性、体验型任务 |
| 语言专项 | `ecc:*review*` / `ecc:*build*` | 语言或框架专用 reviewer / build resolver |
| 代码理解 | `lean-ctx` / `understand` / `gitnexus-*` | 查结构、看影响范围、压缩上下文 |
| 文档写作 | `article-writing-guide` | 中文技术文章/教程写、审、润色、发布前总路由 |
| 指南维护 | `superpowers:writing-skills` / `darwin-skill` | 外部 AI 编码实践、插件变化、死引用修复要进本指南 |

---

## 反模式与失败处理

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 用户只是问名词解释 | 直接解释 | 误拉进 A/B/C 执行选择 |
| 用户说「直接做」 | 跳过 AskUserQuestion | 继续追问流程选择 |
| 高风险审查 | 实际 reviewer / `code-review` + `security-review`；需加固建议再叠 `security-and-hardening` | 只做一轮浅审或只要加固建议不审代码 |
| 小改动开始跨模块 | 升级到「开发新功能」 | 硬留在 `ponytail:ponytail` |
| 证据不足影响主推荐 | 停下来问用户 | 拍脑袋补全 |
| 外部 AI 编码文章很完整 | 先过轻量迁移闸门 | 把项目专属流水线整段塞进路由器 |
| 维护本指南 | 先补 RED 场景，再改 SKILL.md | 先改正文，事后才补测试 |

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
| 项目 wiki 三级知识库 | 只保留"理解代码先 lean-ctx/understand/gitnexus，完成后 neat-freak" | 项目地图应在项目内维护 |
| TECH_SPEC.md 完整模板 | 不内置；仅建议知识收尾时按项目需要沉淀 | 模板绑定项目复杂度 |
| 红线 YAML + 分阶段加载 | 不内置；保留 CHECKPOINT + 反模式表 | 对路由指南过重 |
| 模拟器/浏览器/构建专用验证 | 不内置；路由到 `run` / `superpowers:verification-before-completion` / 构建 resolver / 下游测试 skill | 验证细节由项目和语言决定 |
