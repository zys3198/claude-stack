---
name: tutorial-maker
description: Use when 用户要制作 Markdown 系列教程、课程计划、从零系统学习路径，或把主题/笔记变成循序渐进教程；触发词包括 教程制作、从零开始系统学习、生成系列教程、把笔记变成教程、系统性入门某主题、tutorial maker、make a tutorial series、从0学XX。
---

# Tutorial Maker

把一个主题（+可选本地材料）变成**面向 from-zero 学习者的、可发布的 Markdown 系列教程**。不是单课生成器，是系统课程生成器：先规划整条学习路径，审批后再逐课生成，每课过自审门。

## 工作区布局（两层分离）

```
<workspace>/
├── .tutorial-maker/          # 引擎状态（隐藏，不发布）
│   ├── intake.md             # 作者访谈结果
│   ├── curriculum.yaml       # 已审批知识点树（流水线核心操作对象）
│   ├── progress.md           # 生成进度 + 自审状态（resume 唯一真相源）
│   ├── sources.md            # 本地材料 + 溯源 + gaps（§13 防臆造）
│   └── reviews/              # 每课自审报告
└── <topic>-tutorial/         # 可发布产物（默认名，可覆盖）
    ├── README.md             # 课程索引 + 怎么用这套课 + 课索引含 time_estimate
    ├── lessons/01-<slug>..md # 每课一文件，编号 = 线性路径
    ├── cheatsheet-<stage>.md # 阶段速查表（每阶段一页，从该阶段课压缩）
    ├── recommended-resources.md # 推荐资源 ≤5（从 sources.md 筛，4 元数据）
    └── glossary.md           # 全局术语表
```

产物纯 Markdown 无 JS。反馈靠 `<details>` 折叠答案 + 「你来试」练习。**一题一个 `<details>`**，不合并——合并就等于"一次扔答案"，读者一展开全暴露，自欺。

## 命令

| 命令 | 行为 |
|------|------|
| `/tutorial <topic> start` | 跑 intake → 生成大纲 → **停在大纲审批门** |
| `/tutorial <topic> status` | 当前阶段 / 课状态 / 自审未过清单 / 节奏 |
| `/tutorial <topic> next` | 生成下一个 pending 课 |
| `/tutorial <topic> lesson <N>` | 指定生成第 N 课 |
| `/tutorial <topic> regen <N>` | 按反馈重生成（存 `.old`，不覆盖） |
| `/tutorial <topic> review <N>` | 对第 N 课重跑自审门 |
| `/tutorial <topic> resume` | 从 progress.md 断点继续 |

> **命令激活说明**：`/tutorial <topic> <subcmd>` 是本 skill 激活时的命令约定，由 agent 按 SKILL.md 解释执行，**非 harness 注册的斜杠命令**。触发方式：描述命中（教程制作 / 从零系统学习 / 把笔记变成教程 等触发词）或用户输入 `/tutorial ...` 由 agent 识别本 skill 后按上表执行。

## 主流程（4 暂停点，绝不盲刷）

```
start
  → 🔴 CHECKPOINT 1 · intake 汇总，作者确认抓对
  → 生成大纲（知识点树 + 线性序 + must-know）
  → 🛑 STOP · 审批门（硬门）：大纲不改不批不生成
  → 逐课生成（next / lesson N）
  → 🔴 CHECKPOINT 2 · 每课自审门：MUST 不过不标 done
  → 🔴 CHECKPOINT 3 · 每 3 课节奏检查（继续/加速/减速/跳过）
  → 全完成 → 生成 README + glossary → 收尾
```

分阶段细则见：[课程规划与每课生成](references/lesson-template.md) · [状态文件 schema](references/state-files.md) · [自审门](references/review-gate.md) · 起步模板在 [templates/](templates/)。

## 关键原则

- **大纲审批门是硬门**：路径错了后面全废，不批不准生成。
- **每课自审门（sub-agent）**：派独立 sub-agent 扮演「只读本课 + 前序课 objective + glossary 的 from-zero 读者」做 teach-back。判定来自模拟读者外部信号，非作者/AI 自评自卷。任一 MUST 不过 → status 留 `blocked`，不标 `done`。详见 [review-gate.md](references/review-gate.md)。
- **gaps 防臆造（§13）**：每条事实溯到本地材料，否则进 `sources.md` 的 gaps 清单明示缺失。v1 **不联网**，缺就标缺，不编。
- **objective 可观测**：禁"理解了"，必须"能说出/能做到 X"。
- **顽固点不死磕**：regen 2 次仍 MUST 不过 → 标顽固点建议作者手介入。
- **借思想不调 skill**：与 teach/cram-engine/ruthless-review/grill 是模式借鉴，运行时零依赖。v1 不调 article-writer/JavaGuide/drawio，不联网。

## 失败模式处理

| 触发 | 一线修复 | 仍失败兜底 |
|------|---------|-----------|
| intake 信息不足（受众/北极星空） | 继续 grill 补问 | 不进大纲生成 |
| 本地材料路径无效 | sources.md 标红警告 | 不阻塞，相关事实进 gaps |
| 单课 >600 行 | 触发 full-output-enforcement | 仍超 → 拆两课，回 curriculum.yaml 加课 |
| 自审 MUST 不过 | status 留 `blocked` + blockers | regen（存 `.old`）→ 2 次仍不过标顽固点 |
| 中断 | 读 progress.md | resume 从断点继续 |

## 反模式（不要做）

- 🚫 **一口气盲生成全部课**——审批门通过后才逐课生成。
- 🚫 **自评自卷**——自审门必须派独立 sub-agent，主 agent 不准自己判 `done`。
- 🚫 **臆造 gaps 外的事实**——本地材料和命名权威源都没有的细节，标 gaps，不编。
- 🚫 **objective 写"理解/掌握"**——必须可观测（能说出/能做到 X）。
- 🚫 **答案合并到一个 `<details>`**——必须一题一个折叠，规约读者一次一题。
- 🚫 **跳过 `common_mistakes` / `exit_criteria`**——curriculum.yaml 声明的常见错误必须在课内「常见错误」节真覆盖；阶段 `exit_criteria` 必须在 README 学习路径里明示。
- 🚫 **regen 死磕**——同一课 regen 2 次仍不过即标顽固点，不硬刷。
- 🚫 **联网补查（v1）**——v1 只命名权威源不抓取内容；缺口标 gaps 留 v2。
- 🚫 **运行时调其他 skill**——与 teach/cram-engine/ruthless-review/grill 是思想借鉴，零依赖。

## v2 留口（schema 已留位，不在 v1 实现）

缺口补查联网 + citation（gaps 清单入口）/ 前置依赖 DAG（prereq 字段入口）/ 难度曲线分析 + 多 persona（audience 对象可扩展）/ 配图与交互 quiz。
