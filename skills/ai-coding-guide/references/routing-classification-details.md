# 低频分类细节（Step 2 下放）

本文件只在用户命中 `routing.md` Step 1 的低频分类时展开。`routing.md` 的 Step 2 只留索引行；本文件存每个分类的完整默认路径 / AskUserQuestion / Fallback。

**触发：** Step 1 命中以下任一分类 → 读本文件对应小节，按其中完整路径执行：
`学习型开发` / `判级/暴露未知` / `有需求文档` / `文档写作` / `路由指南维护` / `提交/收尾` / `知识收尾` / `循环任务` / `了解指南` / `编码域调研`

---

## 分类索引

| 信号（Step 1） | 分类 | 主路径一句话 |
|---|---|---|
| 学习型 AI 编码 | 学习型开发 | `ai-coding-coach` |
| 判级/暴露未知 | 判级/暴露未知 | `expose-unknowns` |
| 已有需求/PRD | 有需求文档 | 手动拆 4-6 切片 + PLAN.md |
| 文档写作 | 文档写作 | `article-writing-guide`（写作总路由） |
| 外部 AI 编码实践/审查 guide | 路由指南维护 | `guide-skill-auditor` |
| 要提交/收尾 | 提交/收尾 | 手动 git + diff 展示待确认 |
| 知识收尾/同步 | 知识收尾 | `neat-freak` |
| 循环任务 | 循环任务 | `/loop` |
| 纯对比/选型问题 | 了解指南 | 最小速查 + `ecosystems.md` |
| 编码域查最近动态 | 编码域调研 | `last30days` |

---

## 学习型开发

- 默认主路径 → `ai-coding-coach`
- 归属+persona 已由「开工问询」定（按任务类型推荐），此处不重复问；按已定归属进 `ai-coding-coach`
- 与代码改动叠加时：先用 `ai-coding-coach` 定归属（你练/我讲/我动手），再按实际任务进入开发新功能 / 调试 bug / 重构/简化 / 快速改动
- 高风险或用户明确要练判断 → 你练（peer 加深）；赶交付 → 我动手但保留 why-review

AskUserQuestion:
- A: 进 `ai-coding-coach`（按开工问询定的归属，推荐）
- B: 先看这套协作方式怎么工作
- C: 跳过你练直接进开发分类（收尾仍 why-review）

Fallback:
- `ai-coding-coach` 不在 → 手动执行：用户先给第一版方案，助手纠偏，对照项目标杆/官方做法，最后让用户讲 why

## 判级/暴露未知

- 默认主路径 → `expose-unknowns`（判四象限 → 按级选技巧 → 任务后反考）
- 判「未知的已知/未知的未知」需采访澄清 → `expose-unknowns` 内嵌路由到 `grill-me` / `ask-matt`（user-invoked，提醒用户手动敲；不敲则手动采访），不重复展开
- 只问四象限概念、不开工 → 直接解释，不强拉进流程

AskUserQuestion:
- A: `expose-unknowns`（默认）
- B: 只看判级方法说明
- C: 跳过判级直接开工

Fallback:
- `expose-unknowns` 不在 → 手动执行 `code-change-workflow` skill §1.1「动手前先判级」一行规则
- 需求模糊但用户未提判级/暴露词 → 仍走「开发新功能」的澄清步骤，不抢路由

## 有需求文档

- 默认主路径 → 手动拆 4-6 切片 + PLAN.md（按 `code-change-workflow` §3），确认后实现
- 用户只想先整理需求项 → `to-prd` / `to-issues`
- 条件路径：`mattpocock-skills:to-spec`（需求成型为 spec，user-invoked 需提醒手动敲）
- 中大型/跨会话 → 升档交付状态机（`routing.md` Step 0.4），REQUIREMENT 阶段以需求文档为输入

AskUserQuestion:
- A: 先拆切片出计划
- B: 先整理需求项（`to-prd` / `to-issues`）

Fallback:
- 用户只要结论不要计划 → 直接回答，不强拉进计划流程

## 文档写作

- 默认先走 `article-writing-guide`（写作总路由）
- 从零写且分类已明确 → `article-writer`
- 规范格式/统一 Markdown → `chinese-markdown-normalizer`

AskUserQuestion:
- A: 从零写
- B: 规范/润色
- C: 审校

Fallback:
- skill 不在 → 回到基础人工流程

## 路由指南维护

- 先判断是否值得迁移；只评估外部做法 → 只给结论，不改文件
- 审查/优化/新建任一 router 型 guide skill（含本系统路由层）→ `guide-skill-auditor`（十查 + 基线测试 + 分级修复）
- 小型路由/测试修正 → 补 RED 场景或最小检查，最小改 `references/routing*.md` / `evals/` / 必要参考文件，并跑审计
- 行为变化或要量化优化 → `darwin-skill`；造/改 skill 结构 → `skill-creator`
- 迁移内容只吸收路由规则：触发词、分类、证据门槛、fallback、反模式（闸门见 `ecosystems.md` §轻量迁移闸门）

AskUserQuestion:
- A: 只做最小迁移（推荐）
- B: 先完整评估再改
- C: 只给方案不改文件

Fallback:
- 外部做法太项目化 → 不迁移，建议做项目专属 skill
- 缺少可验证测试场景 → 先补 eval 用例，不直接改正文
- 用户要求"直接做" → 仍保留 RED 检查和审计，跳过 A/B/C 选择

## 提交/收尾

- 默认主路径 → 手动 git add/commit；commit/push 前展示 `git diff --cached --stat` 待确认（CLAUDE.md §1.3 人工确认线）
- 条件路径：`commit-commands:commit`（单提交）、`commit-commands:commit-push-pr`（**一条命令自动 push 远端 + gh 开 PR，不可逆**）、`ocr review`（commit 前独立审查）

AskUserQuestion:
- A: 手动提交（展示 diff 待确认）
- B: `commit-commands:commit`（条件路径）
- C: `commit-commands:commit-push-pr`（自动 push + 开 PR，跑前务必确认）

Fallback:
- 都不在 → 手动 git add/commit；`commit-push-pr` 类一条命令推远端，跑前务必确认

## 知识收尾

- 默认主路径 → `neat-freak`
- 用于会话/阶段完成后同步 docs、README、AGENTS/CLAUDE、memory，清理过期/重复/冲突知识
- 不用于代码重构；代码重构仍走「重构/简化」

AskUserQuestion:
- A: `neat-freak`（知识库收尾，推荐）
- B: 只同步 memory
- C: 只更新项目 docs

Fallback:
- `neat-freak` 不在 → 手动枚举 docs / README / AGENTS / memory，按受众同步，删过期重复

## 循环任务

- 循环/轮询/条件驱动 → `/loop`（固定间隔走定时；省略间隔让模型自定步调，覆盖条件驱动）

AskUserQuestion:
- A: 直接 `/loop`
- B: 先确认终止条件再 `/loop`
- C: 展示循环任务路径

Fallback:
- `/loop` 不可用 → 说明不可用并回到手动执行

## 了解指南

- 展示最小速查 + `references/ecosystems.md`
- 展示完后再问「现在要执行什么」

## 编码域调研（社区/舆情/最近动态）

- 编码场景下查「最近 X 有什么更新/讨论」 → `last30days`（近 30 天社区真实用户声音，跨 Reddit/X/HN/YouTube/TikTok）
- 不替代 `lean-ctx`（读代码）/ `gitnexus-exploring`（调用链）/ `agent-reach`（存证调研）：这些是结构性查询，本分类是时间敏感的舆情/动态
- Fallback：`last30days` 不在 → WebSearch 限时 + 用户口径限定

AskUserQuestion:
- A: 走 `last30days` 查近 30 天（推荐）
- B: 用 WebSearch 限时查
- C: 我只要一手官方 changelog

<!-- 吸收自 ai-coding-guide v1.9.0 references/classification-details.md，2026-08-18 -->
