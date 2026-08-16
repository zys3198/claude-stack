---
name: learning-guide
description: Use when 用户要学、调研、吃透、入门、速成、备考、做教程、记笔记、查资料，且没明确点名具体学习类 skill。是学习/知识输入域的开工路由器，路由到 deep-learn / cram-engine / tutorial-maker / tech-learning-roadmap / agent-reach / last30days / wiki-sediment / expose-unknowns。触发词：学 X、调研 X、入门 X、吃透 X、速成、备考、做教程、记笔记、查资料、怎么学、学习路径。学习模式/说话层词汇统一走 learning-personas（peer/teacher/research）。不用于：写代码任务（走 ai-coding-guide）、写技术文章（走 article-writing-guide）、前端视觉（走 ai-coding-guide 前端视觉子路径）、提升 AI 辅助编码能力/练 AI coding 判断力（走 ai-coding-guide → ai-coding-coach）。<!-- v1.6.0 -->
---

# 学习路由指南（Claude Code）

## 定位

学习/知识输入域的**开工路由器**，对齐 `ai-coding-guide`（编码域）和 `article-writing-guide`（写作域）。只回答「这类学习任务先走哪个 skill」，不认领下游 skill 的执行权威——执行细节以下游 skill 为准。

**质量底线：** skill 名先查当前会话可用清单再推荐；生态缺失给 fallback，不硬推不存在的工具。

## 触发门禁（路由表前先跑）

委派前先输出 3 行门禁：

```
learning-guide 相关？ YES/NO —— <一句理由>
目标 skill 在当前会话？ YES/NO
若 NO → fallback： <路由表 Fallback 列>
```

## 开工问询（路由入口）

触发门禁后、进路由表前，先跑开工问询。**逐个问，一次一个，每个给推荐答案**；能从笔记/文档/代码库查到的不问用户。

**触发：** 需求模糊/缺背景/没明说模式 -> 走；明确任务/机械任务/用户说"直接讲" -> 跳过，走默认。

**问询顺序：**
1. **归属**：这技能归你吗？——归你/该练 → **你练**（AI 纠偏）；不归你/只要会用 → **我讲**（AI 生成你追问）；太大 → 存起来另会话。**按任务类型给推荐**——该你深学吃透的核心 → 你练；概念解释/追问读懂 → 我讲；速成/备考 → 你练 + 判对错
2. **场景**：深学吃透 / 概念解释 / 速成备考 / 学习路线 / 记笔记 —— 决定走哪个流程 skill
3. **说话层**：按当下认知状态取 persona（探索→peer / 求讲清→teacher / 要下结论→research），执行细节见 `learning-personas`
4. **背景**（模糊时）：为什么学/什么场景要用/有无范围/何时验收；能查的不问
5. -> 进路由表

**例外（不问，直接我讲）**：纯查资料存证、已指名 skill、用户说"直接讲"。

**与现有机制分工：** 开工问询管归属+场景+persona；裁决规则 4 管深浅/产出形态方向。不重叠。

## 环境自检

触发后按顺序复核可用性，**只在会话 `Available skills` 里出现的才算已证实**：

1. 先看当前会话可用清单（唯一可信源）。
2. 再看顶层独立 skill：`~/.claude/skills/`。
3. **关键提醒**：reminder 没列出 ≠ 一定不存在；关键推荐前按磁盘再复核一次。
4. 生态缺失 → 跳过该路径给已装替代，不硬推不存在的工具。下表是本机 cc-switch 盘点，会话里没列出的当不存在。

## 路由表

| 用户信号 | 分类 | 主路径 | Fallback |
|---|---|---|---|
| 陌生领域、无教材、要系统吃透/调研到能聊 | 深度调研学习 | `deep-learn` | 手动：五视角→矛盾→考试→速查表 |
| 有课程重点/考试范围、期末速成 | 速成备考 | `cram-engine` | 手动四阶段：拆→讲→考→补 |
| 把主题做成系列教程/学习路径（输出物） | 做教程 | `tutorial-maker`（**给自己学会/作为学习产物**） | 手动规划路径再逐课；对外发布的教程文章转介 `article-writing-guide` |
| 学习者本人要一条可执行路线+作业（学习路线/学习计划/roadmap/帮我学/我想学/学习路径/制定学习计划） | 学习路线图 | `tech-learning-roadmap` | 手动分阶段列路线+作业 |
| 委派后台查一手资料、存成 md | 查资料 | `agent-reach`（多平台检索） | 前台 WebSearch + 落盘 |
| 查近 30 天社区/舆情/真实用户声音 | 舆情调研 | `last30days` | WebSearch 限时 |
| 笔记/速查表存进 wiki 落库 | 记笔记 | `wiki-sediment` | 手动写 md 到 `C:\ZYS\Wiki` |
| 开工前不知道自己不知道什么、要扫盲判级 | 判级扫盲 | `expose-unknowns` | `code-change-workflow` skill §1.1 判级一行 |
| 工作区内教我一个技能、多会话（**仅用户手动 `/teach` 触发**，`disable-model-invocation`，agent 不可自动调） | 跟学技能 | 用户自行 `/teach`（本会话未装，待用户本机确认） | 手动分次讲解 |
| 考前/面试前要被拷打、压力测试理解 | 被考官考 | `deep-learn` 第 8 步 | 手动出 10 题逐题问 |
| 学习计划拆任务、排期 | 拆学习任务 | 手动列清单 | -- |

## 裁决规则

1. **点名优先**：用户点名 skill 直接用它，不拦。
2. **少叠加**：默认 1 个主路径。学习与写作叠加（学了要写成文章）→ **本 guide 拥有这条串行规则**：先学习域 skill 学完，再交 `article-writing-guide` §3 边学边写路径（不并行、不在 article-writing-guide 重复展开）。
3. **边界重叠**：
   - 「调研 X 然后做成教程」→ 先 `deep-learn`（输入）后 `tutorial-maker`（输出），串行不并行。
   - 「速成」有范围 → `cram-engine`；无范围纯陌生 → `deep-learn`。
   - 「查资料」只为存证 → `agent-reach`；为学会 → `deep-learn`。
   - 「开工判级/扫盲」归属：判级/暴露未知不分域，统一 → `expose-unknowns`；本 guide 只负责在学习任务入口路由到它。编码任务同样由 `ai-coding-guide` 路由进 `expose-unknowns`（v1.2.1 组合审查新增；v1.4.1 删除域分半句，判级不切开）。
4. **决策点先问 + 开工问询（默认问、可直接做）**：开工问询先定归属（你练/我讲）+ 场景（深学/概念/速成，按任务类型推荐）+ 背景；说话层 persona 按认知状态从 `learning-personas` 取（探索→peer / 求讲清→teacher / 要下结论→research）。分类不清或深浅/产出形态不明时，只问一个关键问题收口——「你是想自己学会，还是要产出教程/文章？深学吃透还是只要概念解释？」，不堆选项，也不让下游学习 skill 自行推断深浅；用户说"直接讲/你定"则跳过走默认。

## 反模式

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 用户说"给我讲讲 X" | 问一句要深学还是只要概念解释；只要解释就直接答 | 一律拉进 deep-learn 十步 |
| 只要概念解释 | 直接解释，不开流程 | 强拉进学习闭环 |
| 学习 skill 缺失 | 给手动 fallback | 推荐不存在的 skill |
| 学了要写文 | 学完交 article-writing-guide | 学习写作混一个流程 |
| 分类不清/跨域重叠 | 走共享兜底 [`ai-coding-guide/references/fallback-template.md`](../ai-coding-guide/references/fallback-template.md) | 在本 guide 重复写跨域反问 |

## 组合顺序（与兄弟路由器）

- 学习任务 → 本指南
- 编码任务 → `ai-coding-guide`
- 写作任务 → `article-writing-guide`
- 前端/视觉 → `ai-coding-guide` 前端视觉子路径

三个路由器各管一域（显式枚举，无第四域），不互相嵌套。跨界时串行交接，不并联。

<!-- 路由表门禁：路由表条目由人工维护；删除任何条目前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）。v1.5.0 -->
