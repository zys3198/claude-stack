# Changelog

本文件记录 article-writing-guide 路由 skill 及下游 skill（`publish-final-check`、`javaguide-style-guide`）的演进。

格式参考 [Keep a Changelog](https://keepachangelog.com/)，日期 YYYY-MM-DD。

## 2026-06-27 — 路由收口到 de-ai-orchestrator

- 新增 `de-ai-orchestrator` skill：判档 + 串联 humanizer-zh / shuorenhua / ai-text-polisher，按档位自动跑；保留事实与术语；不接女娲（手动）。
- `article-writing-guide` §1 第 ⑤ 阶段从 `ai-text-polisher` 改为 `de-ai-orchestrator`。
- 默认 pipeline（通用 + JavaGuide 模式）第 ⑤ 步同步改为 `de-ai-orchestrator`。
- 现有 `ai-text-polisher` / `humanizer-zh` / `shuorenhua` 内部未改；保留直达入口。

## 2026-06-27 — JavaGuide 模式去 AI 味接管

- `de-ai-orchestrator` 新增 §JavaGuide 模式：外部传 `javaguide-mode: true` 时强制重度档，`humanizer-zh` / `shuorenhua` 切**连接词限制模式**（仅清连接词，不动风格层），保护 JavaGuide 强观点、钩子、生活化比喻。
- 用户显式“JavaGuide 深改 / 保风格” → 内部硬切 `ai-text-polisher` 单链路，跳过规则链；回执标 `style-mode: polisher-only`。
- 回执模板新增字段 `javaguide-mode` + `style-mode`（`full` / `connectives-only` / `polisher-only`）。
- `article-writing-guide` §5 JavaGuide 模式开关加一段接管说明，指 `de-ai-orchestrator` 自动接管 + 连接词限制模式。

## [0.6.0] - 2026-06-24

### javaguide-style-guide 补源码/表格呈现判定（article-writer §6.4 终检覆盖）

article-writer §6.4「源码/参数处理四原则」此前只在写作执行层，终检无法覆盖。本轮把四原则提炼为可判定的 checklist 项 + 量化阈值，补进判定层。

#### javaguide-style-guide SKILL.md
- Added: §1 MUST 加 **M10 源码注释与放置**——代码块不裸贴大段实现（关键片段带中文行内注释），大段完整实现进末尾独立章节不散落正文。对应 §6.4 原则2/3。`绝不裸贴`是硬约束，列 MUST。
- Added: §1 SHOULD 加 **S7 表格优先 + 图代源码**——表格为默认论证载体，复杂逻辑优先 Mermaid 而非堆源码。对应 §6.4 原则1/4。密度偏好因文体而异，列 SHOULD。
- Added: §2 量化阈值表加两行——大段裸贴代码（M10，>40行未注释且不在专节）、表格 vs 代码比（S7，源码密集型文表格行 ≥3×代码块）。
- Added: §3 正反例表加 M10/S7 两行。
- Changed: §5 SHOULD 范围 S1-S6 → S1-S7。
- Changed: §6 版本 0.3.0 → 0.4.0。

### 设计取舍
- M10/S7 刻意分层：裸贴大段源码（原则2/3，绝不）上 MUST 可拦发布；表格优先/Mermaid 代源码（原则1/4，密度偏好）留 SHOULD 不硬拦，避免误伤概念型文章（少表格少代码也合法）。
- 与 article-writer §6.4 不重叠：§6.4 给写作指引+实例（怎么写），本 skill 给判定阈值（验不验得过），延续 §0「写作执行/风格判定」分工。
- 未改 article-writer：§6.4 四原则本身保留在写作层不变，本 skill 只补判定视角。

## [0.5.0] - 2026-06-24

### Round 3b 优化（路由补全 + 漂移维护，dry_run）

对当前 available skills 列表交叉核对 §1 路由表，发现已漂移：路由表漏收录 3 个实际存在的调研类 skill，且无同步机制。本轮从「堵漏」（0.4.0 规则6）升级到「路由更准」。

#### article-writing-guide SKILL.md
- Added: §1 调研行补 `last30days`🪶（全网话题近 30 天热度）、`aihot`🪶（AI 行业资讯，中文）、`agent-reach`🪶（多平台定向检索）。三个实际存在于 available skills 但此前漏收录的轻量级调研工具。
- Changed: §2「调研四选」→「调研七选」，按信息源重新组织（本地/全网趋势/多平台/深度带引用），给「先按信息源定位」的裁决规则；新手优先五个 🪶 轻量级。
- Added: §6 演进「路由表漂移维护」——路由表靠人工维护会漂移，定期拿 available skills 列表与 §1 表交叉核对，逐项跑 §4 规则6 校验。

#### article-writing-guide REFERENCE.md
- Changed: §1 决策树「需要先调研」分支补 last30days / aihot / agent-reach 三条；deep-research 标注「先 §4 规则6 校验存在」。

### 实测验证（非 dry_run）
- 把 0.4.0 加的规则6（存在性校验）真用上了：发现 §1 表对 available skills 列表漂移（deep-research 不在列表、漏 3 个轻量调研工具）。规则6 从「理论兜底」变成「已被实战触发的补丁」。
- 漂移是真问题，不是空想：本轮即因交叉核对而发现并修复。

## [0.4.0] - 2026-06-24

### Round 3 优化（darwin-skill 评估驱动，dry_run）

基线 ~81（达标线 80）。本轮只动真短板，不凑分（HL-4 见好就收）。

#### article-writing-guide SKILL.md（dim3 + dim5 + dim7）
- Added: §4 规则6「目标 skill 存在性校验」——命中 §1 表后先核对目标在本会话 available skills 列表，不存在（被删/改名/未装）→ 🛑 STOP + 报告替代，不路由进虚空。把 javaguide-writer 逐个 redirect 泛化成通用兜底。最高杠杆改动（router 最大结构性风险）。
- Added: §7 端到端示例补「帮我改改这篇」模糊 case（新手最常踩，原缺）。
- Changed: §0 系统内置 skill 提示 `~/.Codex/skills/` → 「本地 skills 目录」（runtime 中立化）。
- Changed: §0 javaguide-writer 重定向交叉引用 §4 规则6。

#### article-writing-guide test-prompts.json（dim8 支撑）
- Added: #5「帮我改改这篇」模糊请求、#6 跨阶段「写并发布」、#7 含已删 skill 的多步请求。4 → 7 条，覆盖 §4 规则3/6 与 dim5 易混裁决。
- 验证：JSON 合法（7 条）。

### 评分变化（dry_run）
- dim3 失败模式编码 8→9（+1.2）：补目标存在性校验这一关键失败分支。
- dim5 可执行具体性 8→9（+1.7）：补模糊 case 示例。
- dim8 实测表现 7→8（+2.3）：test-prompts 扩充，覆盖 router 专属风险场景。
- 估算总分 ~81 → ~86（Δ +5，dry_run，重要决策需 full_test 复核）。

## [0.3.1] - 2026-06-23

### 生态清理
- Removed: `javaguide-writer` skill 目录删除（纯重定向桩，功能已并入 `article-writer`）。SKILL.md §0 与 test-prompts #4 重定向措辞从"目录残留"改为"已删除引导"，重定向能力降级为依赖主模型知识识别废弃名。

## [0.3.0] - 2026-06-12

### Round 2 优化（终审全部达标 ≥80）

终审评分：article-writing-guide **82** / publish-final-check **83** / javaguide-style-guide **81**（全过 80 线）。

#### javaguide-style-guide（80 → 81，修高危+2中项稳线）
- Fixed: §0 权威关系声明矛盾——"不覆盖"改为"终检时 §2 量化阈值**覆盖** §6 对应项"（终检比写作基线严，M5：写时 ≥1 处 / 终检 ≥3 处，有意加严）。
- Added: §2 量化阈值表"判定法"列补可执行 grep 正则（M5 数字密度 / M7 裸块 / M3 数字前缀 / M9 AI 味词 / M6 时效词）。
- Added: §3 正反例补 M5/M6/M8 量化项对照（原仅覆盖非量化项）。
- Added: §4 反模式补"写作基线 vs 终检阈值混用"一条；明确与 article-writer §6.9（写作向）互补关系。
- Changed: 版本号 0.3.0。

#### article-writing-guide（82，达标，余项锦上添花未做）
- 已达标。可选优化（未做）：test-prompts.json 扩充、§3 pipeline 末环独立成块、description 末句削弱重叠。

#### publish-final-check（83，达标，余项锦上添花未做）
- 已达标。可选优化（未做）：§2③ S6 跨文件命名对齐、端到端 trace 示例、②死链判据补状态码规则。

## [0.2.0] - 2026-06-12

### Round 1 优化（评分基线 68-74 → 目标 ≥80）

#### publish-final-check（74 → 目标 80+）
- Fixed: 全局错别字"柏验"→"查重"（description + 正文 + 报告格式，共 4 处）。
- Fixed: 子项③不再委派交互式 `ai-text-polisher`（polisher 是多轮改写 skill，不适合只扫不改）；AI 味改自检关键词黑名单。
- Added: §1 输入样例（成稿路径 + 参考源三形式 + 平台枚举 + JavaGuide 标记）。
- Added: §3 并行失败兜底（子项 exception 不阻塞其他子项，标未完成）。
- Changed: §2③ 风格判定引用 `javaguide-style-guide` §1 M1-M9 + §2 量化阈值（精确引用路径）。
- Added: §7 版本号 0.2.0。

#### javaguide-style-guide（68 → 目标 80+）
- Changed: **重构为薄判定层**，消除与 `article-writer` §6 重叠。明确三层权威：§6 写作执行 / 本 skill 终检判定 / publish-final-check 放行。
- Added: §2 量化阈值表（原创度<20%对齐、数字密度≥3、格式间隔≤5段、段等长<30%差、AI味词0、时效词0、口语词非均匀）——article-writer §6 缺失的补强。
- Added: §3 正反例对照（M1/M2/M3/M4/M7/M9 每项 ✅/❌）。
- Added: §4 判定向反模式（非 docs/ai 误用、证据失效、当写作教程、MUST/SHOULD 混淆）。
- Added: §6 版本号 0.2.0 + 季度复审机制 + 证据失效标"可能漂移"。
- Changed: frontmatter 明确"不主动响应写作请求"。

#### article-writing-guide SKILL.md（72 → 目标 80+）
- Added: §7 端到端路由示例 10 条（query → skill → 理由）。
- Changed: description 削弱与 article-writer 触发词重叠，强化元触发（"不知道用哪个 skill"）。
- Added: §0 注明 `deep-research`/`hv-analysis` 系统内置；`javaguide-writer` 残留重定向。
- Added: §2 "JavaGuide 风格三件套"区分（article-writer §6 写 / style-guide 判 / publish 放行）。
- Added: §8 路由失败兜底（与 REFERENCE §8 对齐）。

#### article-writing-guide REFERENCE.md
- Changed: 成本标注 🪶🪨🔥 全文统一（§1/§2/§3/§4/§6 表头 + 表内）。
- Changed: §6 JavaGuide 模式引用 `javaguide-style-guide` §1 M1-M9 + §2 量化阈值。
- Added: §7 反模式 +1（混淆 style-guide 与 article-writer §6）。
- Added: §8 指向 SKILL.md §7 端到端示例 + test-prompts.json。

## [0.1.0] - 2026-06-12

### Added（初版）
- 新建 `javaguide-style-guide` skill：JavaGuide docs/ai 风格基线，从 5 篇真文章反推的 MUST/SHOULD checklist。
- 新建 `publish-final-check` skill：发布前强制关卡。4 子项，MUST/SHOULD 两级拦截。
- `article-writing-guide/SKILL.md` §1 路由表：成本标注、obsidian-vault、⑩指向 publish-final-check、⑪参考源管理。
- `REFERENCE.md`：决策树加 obsidian、审校叠加规则、柏验只比贴源+边界+改写示例、pipeline 末环+落盘规则、反模式。
- `CHANGELOG.md`：演进记录机制。
