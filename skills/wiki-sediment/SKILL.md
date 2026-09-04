---
name: wiki-sediment
description: >-
  把学完的内容合规沉淀进本 wiki（C:\ZYS\Wiki），是落盘位置与流程的唯一规范：书籍/教程→
  knowledge-note、对话收获→learning-record（80-学习记录/NNNN-slug.md）、AI 纠偏→memory
  feedback、仪表盘刷新。触发：用户说「沉淀」「入库 wiki」「存进 wiki」「记成笔记」，或调用
  /wiki-save。不用于：公众号/抖音链接（走 content-to-note，纯 B站走 bili-note）、
  新建非笔记类治理文档、改存量笔记内容。
---
# wiki-sediment — 自动化沉淀进 wiki

把「学完 → 落库」固定成一条命令。结构规约的唯一权威是 `wiki-structure` skill（`C:\ZYS\Wiki\.claude\skills\wiki-structure\SKILL.md`——Wiki 仓库自带，不在全局 `~/.claude` 也不在 pi skills）——**动手前先读它**，本 skill 不重复 schema，只规定流程。

设计依据：`C:\ZYS\Wiki\docs\superpowers\specs\2026-08-11-wiki-sediment-design.md`（Wiki 仓库内，非本 skill 目录）。

## 入口与路径分发

`/wiki-save [路径] [参数]`；无参数时判断当前会话内容属于哪类，**先报判断再执行**。

| 路径 | 参数 | 产出 |
|---|---|---|
| 书籍/教程 | `/wiki-save 书籍 <源路径> [范围]` | `0X-域/` knowledge-note |
| 对话 | `/wiki-save 对话` | `80-学习记录/NNNN-slug.md` learning-record + 候选 Anki 卡面 |
| 错误 | `/wiki-save 错误` | memory feedback |
| 仪表盘 | `/wiki-save 仪表盘` | 刷新 `00-index.md` |

## 路径一：书籍/教程

1. 读源文件（本地优先；读不到 → 报缺失，禁止凭记忆编内容）。
2. 提关键点：按源结构组织，每条带「为什么/易错点」，不抄原文大段。
3. 判域（01-java-core … 06-system-design）。域不存在 → 先建目录；判断不准 → 报候选域等点头。
4. 套 `93-笔记模板/knowledge-note.md`，frontmatter 照 wiki-structure §3.2（mastery 默认 🟡、layer 默认 knowledge、staleness-window 14、next-review = 今天 +14）。
5. 文件名 `<slug>.md`（中文短横或英文 kebab，一眼看懂主题）；建好后路径不再改。
6. 「源」段用相对路径指回原文件（`../../Tutorial/...` 形式）。
7. 走 §收尾三步。

## 路径二：对话收获

1. 回顾当前会话，抽三类：会了什么 / 卡点 / 关键决策及理由。
2. 扫 `80-学习记录/` 取最大编号 +1，套 `93-笔记模板/learning-record.md`，落 `80-学习记录/NNNN-slug.md`。
3. 列**候选 Anki 卡面**（front/back 草稿），只列不建——用户确认后才落 `91-记忆卡/`（frontmatter 照 wiki-structure §3.1，新卡用 `category` 不用 `type`）。
4. 走 §收尾三步。

## 路径三：AI 纠偏

1. 抽本轮 AI 犯的新错误 + 用户纠正原文。
2. 写 memory feedback：pi 记忆是**单文件**（无 CC 式 memory 子目录/单条文件）——落 `~/.pi/agent/projects-memory/<project-slug>/MEMORY.md` 追加一段（`§` 分隔），尾部 `<!-- created=YYYY-MM-DD, last=YYYY-MM-DD -->`，段内带 **Why:** / **How to apply:**。
3. 同文件其他段引用同错误 → 一并更新时间戳，不重复建段；索引指针格式按 pi 现状适配（`- [Title](file.md) — hook` 是 CC 格式，pi 单文件无此索引行）。
4. 已在 memory 里的同类错误 → 更新旧段，不新增。

## 路径四：仪表盘

1. 跑 `python scripts/refresh-due.py` 刷到期复习段（AUTO 标记段，勿手改）。
2. 手刷其余段：各域笔记数（扫目录）、掌握度分布（扫 frontmatter `mastery`）、「最后更新」日期。
3. 手填时以各笔记 frontmatter 为准，防 drift。

## 收尾三步（路径一、二必走）

1. **回写 `00-index.md`**：主题域表笔记数/掌握度同步；learning-record 另加「最近 learning-records」表一行。
2. **主动回忆提醒**（对齐 wiki CLAUDE.md，一两句不啰嗦）：knowledge-note → 「合书自讲 3 分钟，讲不顺的建 Anki 卡」；Anki 卡 → 检查日新增 ≤20。
3. **输出落盘路径清单**。

## 硬边界

- 不自动 git commit（用户确认线：commit 前必须点头）
- 不自动建 Anki 卡（候选卡面确认后才建）
- 只新增，不改存量笔记
- 链接类内容（公众号/B站/抖音）让路 `content-to-note`
- 编辑配置/规约文件被 GateGuard 拦时：声明「无代码 import/无公共函数/无数据文件读写」+ 引用户指令原文，重试
