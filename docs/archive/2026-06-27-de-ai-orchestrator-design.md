---
name: de-ai-orchestrator-design
description: 设计新编排 skill `de-ai-orchestrator`，自动串联 `humanizer-zh` / `shuorenhua` / `ai-text-polisher`，按档位路由去 AI 味处理；不替代 deep 改稿，而是入口和分流。
date: 2026-06-27
status: draft
---

# De-AI Orchestrator — 设计 spec

## 1. 背景与目标

### 现状

- `ai-text-polisher`（本地，深度交互式去 AI 味）：会诊 + 多轮追问观点 + 改稿；强但慢、依赖用户参与。
- `humanizer-zh`（已装，op7418/Humanizer-zh）：基于维基“AI 写作特征”的规则清洗，固定规则快扫一遍。
- `shuorenhua`（已装，MrGeDiao/shuorenhua）：场景化 AI 套路检查，按力度控制，保留事实、术语、语域、责任主体。
- `article-writing-guide` §1 第 ⑤ 阶段当前直达 `ai-text-polisher`，未利用 `humanizer-zh` / `shuorenhua`。

### 痛点

- 用户说“去 AI 味”时，路由不清晰：轻症也走 polisher，浪费 token；全自动场景没人接管。
- 多适配器需要有人统一判档、串联、降级、回执；这件事缺一个明确入口。

### 目标

- 新建一个编排 skill，做“判档 + 串联 + 降级 + 回执”，不替代任何 deep 改稿 skill。
- 既有入口（直达 `ai-text-polisher`）保留；新增“直达编排器”和“被 `article-writing-guide` 接管”两条路径。
- 最低改动：1 个新 skill + 改 `article-writing-guide` 两处。

### 非目标

- 不替 `ai-text-polisher` 做深改。
- 不替 `humanizer-zh` / `shuorenhua` 做规则判定。
- 不自动接女娲（始终手动）。
- 不动 `article-writer`、不动 `publish-final-check`。

## 2. 概念与档位

### 三个档位

| 档位 | 触发条件（任一） | 链 | 期望耗时 | 用户参与 |
| --- | --- | --- | --- | --- |
| 轻 | 用户说“轻度去 AI 味 / 自动扫一遍 / 给终稿先用规清洗” | `humanizer-zh` | 🪶 | 无 |
| 中 | 用户说“去 AI 味 / 自然一点 / 改得像人写的” | `humanizer-zh` → `shuorenhua` | 🪨 | 无 |
| 重 | 用户说“深改 / 要观点 / 注入见解 / 更像我 / 要踩坑感” | `ai-text-polisher` → `humanizer-zh` → `shuorenhua` | 🪨+ | 至少 1 轮 |

> 档位也允许“全自动也走重”，但只在用户主动选“深改+不停顿”时触发；其他情况走轻/中。

### 路由判定顺序

1. 文本语言非中文 → 不接编排器，退出交回现有英文链。
2. 文本类型是代码块、API 字段、合规条款、表格 → 仅做极轻（仅“风格连接词”），标“事实保真优先”。
3. 用户点名重度信号词（见上） → 重度。
4. 用户明示要全自动 / 不要停 → 走轻或中（不强行重）。
5. 默认 → 中。

## 3. 适配器契约

### 输入

- 文本或文件路径。
- 档位（可省略，自动判）。
- 模式：`auto`（默认）/ `interactive`（重度档强制走多轮）。

### 输出

- 清洗后文本。
- 回执：档位 / 链路顺序 / 跳过的适配器及原因 / 用户被问次数（重度才有）/ 是否建议手动女娲/人工校对。

### 适配器清单

| 适配器 | 来源 | 必备 | 降级行为 |
| --- | --- | --- | --- |
| `humanizer-zh` | 本地 skills（op7418） | 必备 | 缺失时：中/重度档直接跳到 `ai-text-polisher` 或 `shuorenhua`，回执说“已跳规则扫描” |
| `shuorenhua` | 本地 skills（MrGeDiao） | 可选 | 缺失时：中度档只剩 `humanizer-zh`；重度档砍尾，回执说“已跳 AI 套路检查” |
| `ai-text-polisher` | 本地 skills | 可选 | 缺失时：重度档退化为 `humanizer-zh` → `shuorenhua`，回执说“已退回纯规则链” |
| 女娲 | 手动 | — | 永远不被编排器调用；回执最后一行提示“需要学你文风请手动跑” |

## 4. 失败与降级

### 缺适配器

- 缺 `shuorenhua`：跳过该步，链路其余继续，回执记录。
- 缺 `humanizer-zh`：跳到下一档，回执标“已降级”。
- 缺 `ai-text-polisher` + 用户要重度：弹一句警告，问是否接受降级到中档；默认不降级，告知用户结果差。

### 自动 vs 交互

- 重度档默认进 `ai-text-polisher` 多轮追问。
- 用户在调用时说“全自动 / 不要停”：重度档内部硬切到“仅深改版 + 不暂停”，仍走 `ai-text-polisher` 一遍，再接 `humanizer-zh` / `shuorenhua` 收尾。

### 不该洗的文本

- 识别信号：包含代码块 > 30%、表格 > 30%、`config / api / license / 法律` 等关键词。
- 行为：仅清“风格连接词”（此外、然而、综上所述…），不改事实/术语。
- 回执额外写一条：“事实保真优先，已限制清洗范围”。

### 护栏

- `humanizer-zh` / `shuorenhua` 都不编造经历、立场、数据。
- 只有 `ai-text-polisher` 能动观点层。
- `ai-text-polisher` 多轮阶段不接受回写原文件——只在 final 输出阶段写。

## 5. 输出与回执

### 回执结构

```text
## 去 AI 味回执

- 档位：中
- 链路：humanizer-zh → shuorenhua
- 跳过的适配器：无
- 询问轮次：0（auto 模式）
- 后续建议：需要学你文风请手动跑女娲
```

### 输出格式

- 默认：对话内输出新文。
- 显式传文件路径：原地覆盖；备份原文件到 `<name>.bak`。
- 中间产物可见性：
  - 重度档：分段贴出 “polisher 改写 → humanizer 处理 → shuorenhua 处理”。
  - 中档：贴出 “humanizer 处理 → shuorenhua 处理”。
  - 轻档：贴出 “humanizer 处理”。
- 改写完成后自动跑 `chinese-markdown-normalizer` 做最后排版（写回原文件时启用）。

## 6. 文件改动清单

| 文件 | 改动 | 重要度 |
| --- | --- | --- |
| `C:\Users\zys31\.claude\skills\de-ai-orchestrator\SKILL.md`（新增） | 新建编排 skill | 主 |
| `C:\Users\zys31\.claude\skills\article-writing-guide\SKILL.md` | 第 ⑤ 阶段从“`ai-text-polisher`”改为“`de-ai-orchestrator`”；默认 pipeline 同步 | 辅 |
| `C:\Users\zys31\.claude\skills\article-writing-guide\CHANGELOG.md` | 加一条变更记录 | 辅 |

### 新 skill 元信息草稿

- `name: de-ai-orchestrator`
- `description`: 去 AI 味编排器。判档（轻/中/重），按档位自动串联 humanizer-zh / shuorenhua / ai-text-polisher，保留事实与术语；支持自动和交互两种模式。

### 触发词

- “去 AI 味 / 像人写的 / 自然一点 / 改得更像我 / 自动改 / 深改 / 注入观点”。

### 不触发

- 用户点名“用 humanizer-zh / shuorenhua / polisher”具体 skill → 跳过编排器，直达该 skill。
- 英文文本 → 跳过编排器。

## 7. 自检清单（spec 落地前）

- [ ] 不重复 `ai-text-polisher` 现有能力
- [ ] 不破坏现有路由路径
- [ ] 三个档位边界清晰、可解释
- [ ] 缺适配器时不阻塞链路
- [ ] 重度档默认走交互，可被显式覆写
- [ ] 自动覆写不会破坏 `ai-text-polisher` 自身原则
- [ ] 不接女娲
- [ ] 每次输出都带回执

## 8. 待用户确认项

- 是否同意“轻 / 中 / 重”三档默认划分与触发词。
- 是否同意“重度档可被显式覆写为全自动”。
- 是否同意“英文文本退出编排器”边界。
- 是否同意“自动跑 `chinese-markdown-normalizer` 收尾”。