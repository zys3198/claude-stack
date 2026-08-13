---
name: article-writing-guide
description: Use when 用户要写、改、审、润色、查重、配图、发布前检查中文技术文章/系统教程，且未明确指定具体写作 skill 或流程不清。本 skill 是中文技术写作域开工路由器。不用于：含「页面/界面/UI/落地页/登录页」的视觉任务（走 ai-coding-guide 前端视觉子路径，即使同时提到写代码）、纯写代码逻辑/调试/重构/审查/构建（走 ai-coding-guide）、学习调研（走 learning-guide）。<!-- v1.6.0 -->
---

# Article Writing Guide（写作总路由）

## 0. 何时用本 skill

用户提写作需求但**没点名具体 skill**，或点名的不一定是最优解时，先读本 skill 定路由。已明确点名（如"用 article-writer 起草"）时，本 skill 只做快速路由确认，不重复分发。

**触发门禁（§1 路由前先跑）：** 委派任一 skill 前先输出——

```
article-writing-guide 相关？ YES/NO —— <一句理由>
目标 skill 在当前会话？ YES/NO（§4 规则7）
若 NO → 最接近替代： <名字>
```

**开工问询（路由入口）**：触发门禁后、进 §1 路由表前，先跑开工问询。逐个问，一次一个，每个给推荐答案；能从现稿/笔记/文档查到的不问。

- **触发**：需求模糊/缺背景/没明说模式 -> 走；明确任务/机械任务/用户说"直接做" -> 跳过走默认。
- **问询顺序**：
  1. **模式**：coach（我练）/ pair（一起想）/ driver（直接做讲为什么）？**按任务类型给推荐**——想练写作核心（结构/论点/文体判断）→ 推荐 coach；协作流（AI 给结构/方向选项你定，写作域常见）→ 推荐 pair；一次性文案/样板 → 推荐 driver
     - coach：该你会的写作核心（结构/论点/文体判断），你先给，AI 纠偏
     - pair：协作流（AI 给结构/方向选项你定）-- 写作域默认
     - driver：一次性文案/样板，AI 直接写，收尾讲为什么
     - 卡壳 -> AI 递参考判断
  2. **背景**（模糊时）：为什么写/给谁看/什么目的/有无参考；能查的不问
  3. -> 进 §1 路由表
- **例外（不问，直接 driver）**：纯排版/格式规范、已指名标杆、用户说"直接写"。
- **分工**：开工问询管 why+how；§4 决策点先问管文体方向；写作纪律管依据。

**写作纪律（写作闸门，强制）**：所有会产出正文（起草 / 改写 / 续写 / 边学边写 / 协作写作流）阶段，默认必须随预览交付 **依据表 + basis map**：

- **依据表**（evidence inventory）：列 `ID / basis / source / how it will be used`。basis 可以是「现稿原文」「用户笔记」「官方文档」「已验证本地文件」「明确标记的推论」。
- **basis map**：把每个段落/句子映射到依据 ID，并说明为什么这样写。
- 依据缺失时必须标 `needs evidence`，**不得装成事实**；下游 skill 默认执行这一规则（`edit-article`、`article-writer`、`tutorial-maker` 均适用）。

这条闸门的目的：让用户能逐句判断学习，而不是被"读着顺"骗过去。

**废弃 skill 重定向**：用户点名 `javaguide-writer`（已删除，原功能合并入 `article-writer`）→ 引导改用 `article-writer` 指定 JavaGuide 模式；用户点名 `ai-text-polisher`（2026-08-08 已拍板 human-writing 完全替代，本轮移出路由表）→ 引导改用 `human-writing`（从零写+改写均覆盖，见 §2 改写四选；通用兜底见 §4 规则7）。

**系统内置 skill 提示**：`deep-research` 是系统/插件内置 skill（非本地 skills 目录），**本机未装**；命中调研需求时用 §1 表①已装项替代（`agent-reach`/`last30days`）。`ecc:deep-research` 为插件条件路径（当前会话可调用才走）。调用系统内置 skill 用 `Skill` 工具或 `/deep-research`，别在本地目录找 SKILL.md。

**语言边界**：本路由默认**中文**写作。英文文章可走 `article-writer` / `edit-article`，但跳过中文专用 skill（`chinese-markdown-normalizer`、`human-writing`）。

**不用于（兄弟域转介）**：
- 含「页面/界面/UI/落地页/登录页」且要视觉产出 → `ai-coding-guide` 前端视觉子路径（即使同时提写代码）
- 纯写代码逻辑 / 调试 / 重构 / 审查 / 构建 → `ai-coding-guide`
- 学习/调研/速成/查资料 → `learning-guide`
- **教程裁决**（两域都可能命中时）：「给自己学会/作为学习产物」→ `learning-guide`；「面向读者发布的教程文章」→ 本路由 §1 ③ 起草-系统教程/课程
- AI 编码工具/skill/插件选型 → `ai-coding-guide`

**规范源**：JavaGuide 风格基线见独立 skill `javaguide-style-guide`（终检判定用，**仅由 `publish-final-check` ③ 与终检流程内部引用，不作为用户第一跳**）；写作执行见 `article-writer` §6。

## 1. 一句话路由表

按 **写作生命周期阶段** 分发。成本标注：🪶轻 / 🪨重 / 🔥烧 token（新手别滥用）。

| 阶段 | 用户在说什么 | 调用 skill |
|------|-------------|-----------|
| ① 选型/调研 | "这个主题怎么写""有没有相关资料""帮我研究下 X""AI 圈最近有什么" | 本地：`lean-ctx`🪶；全网趋势/舆情：`last30days`🪶；多平台定向/AI 资讯：`agent-reach`🪶；深度调研：`agent-reach`🪶（详见 §2 调研七选；`ecc:deep-research` 为插件条件路径，`deep-research` 本机未装仅作已装时备选） |
| ③ 起草-从零 | "写一篇关于 X 的文章""帮我写篇博客/方案/单篇教程" | `article-writer`🪨（默认通用模式） |
| ③ 起草-系统教程/课程 | "从零学 X""做系列教程""把笔记变成教程" | `tutorial-maker`🪨（**对外发布**的系列教程/课程；给自己学会 → 转介 `learning-guide`；单篇教程仍走 `article-writer`） |
| ③ 起草-边学边写 | "我想边学习边写""从 0 了解 X，边学边沉淀成文章""像刚才那样学习记录写进文章" | `agent-reach` 收集权威材料 → 轻量学习路径 → 对话中给增量初稿 → 用户确认后才 `edit-article` 落盘；无现稿则先给对话初稿，用户确认后再 `article-writer` 起草/落盘 |
| ③ 起草-JavaGuide | "写 JavaGuide 文章""按 docs/ai 规范写" | `article-writer`🪨 指定 **JavaGuide 模式**（执行规范见其 §6，终检判定见 `javaguide-style-guide`） |
| ③ 起草-素材成型/叙事节拍 | "我有一堆笔记/碎片，帮我拼成文章""按故事线/节拍一步步写" | `article-writer`🪨 **协作模式**（§7：开工问询 → 结构方案 → 全篇细骨架 → 明确冻结 → 逐节生成） |
| ④ 结构改写 | "重新组织这篇""调整章节结构""逻辑不顺" | `edit-article`🪨 |
| ⑤ 去 AI 味/润色/降 AI 检测率 | "AI 味太重""改得像人写的""优化文风""AI 率太高""过不了朱雀""降 AIGC 率" | `human-writing`🪨（改写模式：改写作模式 + 注入真实智力，非表面替换） |
| ⑥ 排版规范化 | "统一 Markdown 格式""修中英文空格/标点""批量规范" | `chinese-markdown-normalizer`🪶 |
| ⑦ 配图 | "要不要加图""画个流程图/架构图""配图" | `drawio-article-illustration`🪶(决策+校验) → `drawio-chart`🪨(画图) |
| ⑧ 审校-逐段 | "逐段 review""标 VERSION 增量评审""快速过一遍" | `tech-article-review`🪨 |
| ⑧ 审校-多维度并行 | "全面审稿""多角度并行审查+批量改""先出报告我看看" | `multi-review-pipeline`🔥（并行审 → 修订清单 → 按用户确认批量改；只出报告时停在报告阶段） |
| ⑨ 查重/洗稿 | "这篇是不是抄了来源""查洗稿""只可参考不可抄袭" | `plagiarism-audit`🪨（需外部来源，**只比贴源**） |
| ⑩ 发布前总检 | "文章写完了，发布前过一遍""能不能发了" | `publish-final-check`🔥（强制关卡，MUST/SHOULD 两级拦截） |
| ⑪ 参考源管理 | "我参考了这几篇""这些是我的参考来源" | 收集参考源 URL/文件 → 喂给 ⑨ 查重 + ⑩ 终检①子项 |

## 2. 易混 skill 区分

- **起草四选**：单篇文章/博客/方案 → `article-writer`；对外发布的系统教程/系列课 → `tutorial-maker`；已有碎片要拼 / 要边写边选支线 → `article-writer`（协作模式 §7）。
- **边学边写路径**：用户要"从 0 了解某项目/工具并写成文章"、或明确说"边学习边写"时，不直接走纯起草。先用 `agent-reach` 抓权威资料，产出学习路径和关键心智模型；若已有文章，先在对话中给增量初稿，用户确认后再用 `edit-article` 按现有结构写入；若无现稿，先用学习记录生成对话初稿，确认后再交给 `article-writer` 起草/落盘。
- **改写四选**：调结构/逻辑 → `edit-article`；去 AI 味/文风 → `human-writing`（先读 2-3 篇同作者/目标风格低 AI 率样本提炼正面特征，对照改而非凭空套规则，详见 `article-writer` §7.8 优化模式）；纯排版/标点/空格 → `chinese-markdown-normalizer`；**深度改写整篇**（骨架+措辞都要动）→ `article-writer`（深度改写模式）。前三者可串行：先 edit-article → 再 human-writing → 最后 normalizer。**AI 味根因治理**：若 AI 味源于"一次性生成没搭骨架"（非纯文风问题），先走 `article-writer` §7.10 搭骨架五步法：选方向后一次性展开并冻结全篇细骨架，再逐节扩写；随后才用 `human-writing` 处理表层文风。
- **审校两选 + 发布闸**：逐段增量、单次快评 → `tech-article-review`；多维度并行 + 修订清单 + 按确认批量改（或先出报告）→ `multi-review-pipeline`；**发布前强制关卡**（只放行不改）→ `publish-final-check`。**裁决：要逐段标 VERSION/快评选 tech-article-review，要并行多角度选 multi-review-pipeline，二选一不叠加；发布闸是 pipeline 末环，两者之后才跑。**（`review-doc` 已按 2026-08-13 审计+用户拍板移出路由表：与 multi-review-pipeline 高度重叠，纯 D 类零资产。）
- **调研七选**（按信息源，决策树见 REFERENCE §1）：
  - 本地仓库 .md → `lean-ctx`（ctx_search/ctx_glob）🪶
  - 全网某话题近 30 天热度/讨论 → `last30days`🪶（Reddit/X/HN/YouTube/TikTok 等）
  - AI 行业资讯/日报/热点 → `agent-reach`🪶（公众号/多平台，中文）
  - 多平台定向检索（小红书/抖音/微博/B站/公众号…） → `agent-reach`🪶
  - 全网多源带引用 → `deep-research`🔥（系统内置，**本机未装**；装了走 `Skill` 工具）
  - 产品/公司/技术深度研究 → `agent-reach`🪶 / `ecc:deep-research`（插件条件路径，当前会话可调用才走）
  裁决：先按信息源定位（本地 vs 全网 vs 多平台）；🔥 烧 token 慎用，轻量级 🪶 起步。
- **配图两件套**：先 `drawio-article-illustration` 判断"哪里需要图、用什么图"，再 `drawio-chart` 实际画。不要跳过前者直接画。
- **JavaGuide 风格三件套**：写作执行 → `article-writer` §6（含 §6.7 自检、§6.9 反例 11 条）；终检判定 → `javaguide-style-guide`（M1-M10 + 量化阈值，终检流程内部引用）；发布放行 → `publish-final-check` ③ 引用 style-guide。三者不重叠：§6 教写，style-guide 判定，publish 放行。

## 3. 默认 pipeline（端到端）

> 🔴 **CHECKPOINT**：跨多阶段 pipeline 前，先与用户确认范围（跑全链路 / 只跑某几步 / 单点）。

### 通用技术写作
`lean-ctx/agent-reach`(选型) → 对话初稿/改稿预览 → 用户确认 → `article-writer`(起草) → `edit-article`(结构) → `human-writing`(去AI味) → `drawio-article-illustration`+`drawio-chart`(配图) → `multi-review-pipeline`(审校改) → `plagiarism-audit`(查重，**需外部来源，否则跳过**) → `chinese-markdown-normalizer`(排版) → **`publish-final-check`(发布闸)**

所有会写文件或改文件的步骤都受 §4 写入闸门约束：先预览，确认后落盘。

### 默认协作写作流（结构方案 → 全篇细骨架 → 冻结 → 逐节正文 → 审查）

用户说"我想和你讨论结构后再写""你给我选项，我也会补充想法""逐步设计每节再生成""生成后我来审查给建议"这类需求时，默认走协作流，不直接一次性全文起草（**v1.4.0 起为默认参与度 pair**：默认就走，不需要用户主动说；除非开工问询选了 driver 或 coach，用户说"直接写"才降级）：

1. **结构方案**：先给 2-4 个高层结构方案，每个说明适用场景和关键取舍；用户可选择、混搭、增删章节。
2. **方向确认**：用户选定主线后，先复述文章目的、读者、核心观点和篇幅约束，确认展开方向；此时仍不写正文。
3. **全篇细骨架**：一次性展示完整 H2/H3，让用户能检查全篇依赖、重复、证据缺口和篇幅失衡。每个子节至少写清：本节问题、关键论点、依据 ID、证据/例子（缺失标 `needs evidence`）、读者获得感、目标篇幅、表现形式、与前后文的过渡；优化模式再加现稿位置映射。
4. **讨论与明确冻结**：用户可调整章节顺序、合并重复内容、增删论点和重分篇幅。只有用户明确表示"骨架确认/按这个写/冻结"后，才进入正文；方向确认不等于骨架冻结。
5. **逐节正文预览**：按冻结骨架逐节生成，不在正文阶段临时扩出新主线。正文先在对话里展示并标注"初稿/待确认"，同时遵守依据表和 basis map 闸门。
6. **确认后落盘**：小节正文确认后再写入文件；长文按节落盘，避免一次性生成导致返工和断连丢失。
7. **用户审查循环**：用户审查后给建议，先改结构性问题，再改论点/例子，最后改文风和排版；不要把审查建议直接吞成无边界重写。

裁决：这是 `article-writer` 前置协作层，不替代下游 skill。需要调研先跑调研，需要去 AI 味再跑 `human-writing`，发布前仍跑 `publish-final-check`。

### 边学边写（项目/工具类文章）
`agent-reach`(权威资料) → 学习路径/心智模型(轻量讲解) → 对话中给增量初稿(不落盘) → 用户确认 → `edit-article`(把确认后的学习记录按现有结构写入) → `tech-article-review`(事实核查) → `human-writing`(必要时去AI味) → `chinese-markdown-normalizer`(排版) → `publish-final-check`(发布闸)

**主路径归口**：本节是写作域执行流程；「先学后写」的串行规则由 [`learning-guide` 裁决规则第 2 条](../learning-guide/SKILL.md) 拥有，本 guide 不重复展开。命中「学了要写成文章」时先入 learning-guide 取主路径，本节作为写作域的下游执行承接。

适用：开源项目学习、工具体验文、源码阅读前置科普、用户想"边学边写"。已有现稿时优先保留结构增量补，但仍必须先在对话中展示增量初稿；无现稿时，先把学习记录组织成对话初稿，确认后再交给 `article-writer` 起草/落盘。

**信息价值过滤器（增量初稿前必过）**：核完一堆依据后，不是凡核到的都进正文。一条信息**值得写**当且仅当满足任一——①改变行为（读者看完会做不同的事：改命令/避坑/决定用不用）；②反直觉（和想当然不同，如"include 不是白名单""delegate 不用配 LLM"）；③高频门槛（第一次用必踩）；④支撑文章主线（是核心论点的论据）。反之，默认就够用、查文档 30 秒可得、为求全而并列堆参数的一律砍。这是"怎么用/怎么理解"的文章，不是官方 reference——JavaGuide 风格的狠处正在于敢删。机制细节若读者按默认配置就对，不写。

**平台渲染记账**：边学边写全程记账目标平台不渲染的元素（公众号：mermaid、数学公式、HTML 表格），发布前统一转 PNG，别堆到发布闸才兜。

### JavaGuide 模式
同上，但第②步 `article-writer` **强制 JavaGuide 模式**（执行规范见其 §6）；查重对齐"只可参考不可抄袭"铁律；末环 `publish-final-check` 的风格子项对照 `javaguide-style-guide` §1 M1-M10。

> 详细串联顺序、边界 case、落盘规则见 [REFERENCE.md](REFERENCE.md) §8。

## 4. 路由执行规则

1. 读用户请求 → 匹配 §1 表"用户在说什么"列，或 §7 端到端示例。
2. 命中单一阶段 → 直接调用对应 skill，**不重复本 skill**。
3. 跨阶段（如"写并审"）→ 🔴 **CHECKPOINT**：先确认跑全链路还是单点，再按默认 pipeline 顺序调用多个 skill，逐个执行。
4. **写入闸门**：涉及起草、改写、边学边写、结构调整时，先在对话中给初稿/改稿预览；用户明确确认后，才允许写入文件或调用会改文件的下游 skill。
4.5 **决策点先问（默认问、可直接做）**：起草/改写前若文体（博客/教程/方案）、读者、目的三要素不全，先问清再动手，不让下游写作 skill 自行推断定位；用户给了明确标杆/范文或说"直接写"则跳过，走默认。
4.6 **参与度（开工问询定）**：路由前先按开工问询定模式（coach/pair/driver，按任务类型推荐）；写作域默认 pair（协作流），用户说"直接写"降级 driver，用户说"我想练"升 coach（你先写 AI 纠偏）；机械排版/格式直接 driver。
5. 模糊/无法匹配 → 🛑 **STOP**：读 [REFERENCE.md](REFERENCE.md) 取详细决策规则；仍无法定 → 反问用户三要素（文体/阶段/目标仓库），**不擅自猜测路由**。
6. **不要**自己重写各 skill 已封装的能力（如手工去 AI 味、手工查重）—— 一律委派。
7. **目标 skill 存在性校验**（先于委派）：命中 §1 表后，先在本会话 available skills 列表里核对目标存在；**不存在（被删 / 改名 / 未装）→ 🛑 STOP**，报告用户缺失项 + 给最接近的替代（如 `javaguide-writer` → `article-writer` JavaGuide 模式、`ai-text-polisher` → `human-writing`），**不路由进虚空**。内置 skill（`deep-research`）按其原生调用方式校验，不查本地目录。

### 失败模式表

| 触发条件 | 动作 |
|---|---|
| 目标 skill 不在 available skills | 🛑 STOP：报告缺失项 + 最接近替代，不委派 |
| 跨阶段请求（写并审、写完发布前检查） | 🔴 CHECKPOINT：先问跑全链路 / 几步 / 单点 |
| 起草/改写/边学边写要写文件 | 先给对话预览；用户明确确认后才落盘 |
| 从零起草或深度改写尚未冻结全篇细骨架 | 停在结构阶段；一次性展示完整 H2/H3 细骨架，讨论并明确冻结后再写正文 |
| 查重但无外部来源 | 先问 URL/文件/贴文；用户说无来源才跳过并标 `⚠️ 未查重` |
| 英文文章命中中文专用 skill | 跳过 `human-writing`、`chinese-markdown-normalizer` |
| "帮我改改这篇"无目标 | 先问改骨架/肉/皮；不擅自选 skill |

## 5. JavaGuide 模式开关

用户提以下任一关键词 → 全 pipeline 切 JavaGuide 模式：JavaGuide、docs/ai、Snailclimb、Java 面试系列、`my-submission/`。
切模式后：起草用 `article-writer` JavaGuide 模式（遵循其 §6）；查重对齐"只可参考不可抄袭"铁律（见 [REFERENCE.md](REFERENCE.md) §7）；终检 `publish-final-check` ③ 风格子项对照 `javaguide-style-guide` §1 M1-M10。

## 6. 演进

改动本 skill / REFERENCE.md / 下游 skill（`publish-final-check`、`javaguide-style-guide` 等）→ 记 [CHANGELOG.md](CHANGELOG.md)。checklist 类 skill（`publish-final-check` §2、`javaguide-style-guide` §1）设计成可插拔数组，增删项不动流程。

### v1.3.0（2026-07-22）

- description 加版本戳 `<!-- v1.3.0 -->`。
- §0 新增「触发门禁」：委派前输出相关性 YES/NO + 目标 skill 存在性 + 替代，与 §4 规则7 呼应（依据：社区实测无门禁 skill 触发率 0-20%，forced-eval 模式可达 84%）。
- §6 新增「路由表门禁」HTML 注释：删除条目前必须引用真实事故/官方证据（防无证据漂移）。
- 本轮基线测试（5 场景子代理）：本 guide 路由全对，路由表未动。

**路由表漂移维护**：§1 路由表靠人工维护，会随实际 available skills 列表漂移（skill 增删/改名/未装）。定期比对：拿本会话 available skills 列表与 §1 表交叉核对——缺的补、失效的删、改名更正；逐项用 §4 规则7（存在性校验）跑一遍确认能委派。

<!-- 路由表门禁：§1 路由表条目由人工维护；删除任何条目前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）。v1.6.0 -->

## 7. 端到端路由示例（query → skill → 理由）

| 用户原话 | 命中 skill | 理由 |
|---------|-----------|------|
| "帮我写一篇 RAG 入门博客" | `article-writer`（默认） | 从零创作，非 JavaGuide，单点起草 |
| "按 JavaGuide 风格写 Agent Memory 文章" | `article-writer`（JavaGuide 模式） | 命中 JavaGuide 关键词，走 §6 |
| "给我做一套从零学 Redis 的系列教程" | `tutorial-maker` | 对外发布的系统教程/系列课；给自己学会则转介 learning-guide（教程裁决） |
| "这篇文章 AI 味太重" | `human-writing` | 点名去 AI 味，单点改文风（2026-08-08 拍板替代 ai-text-polisher） |
| "把这几篇笔记拼成一篇文章" | `article-writer`（协作模式） | 素材未结构化，开工问询 → 结构方案 → 全篇细骨架 → 明确冻结 → 逐节生成 |
| "帮我改改这篇" | 先问改哪层；或按骨架→肉→皮 串行 | 模糊，见 REFERENCE §4 易混裁决，不擅猜 |
| "全面审下这篇并改好" | `multi-review-pipeline` | 要审 + 批量改 |
| "先出审校报告我看看，别改" | `multi-review-pipeline`（停在报告阶段） | 要报告；按用户确认后再批量改 |
| "这篇是不是抄了这几个来源" | `plagiarism-audit` | 查重，有贴源 |
| "文章写完了，发布前过一遍" | `publish-final-check` | 发布闸，强制关卡 |
| "写完并发布前检查" | `article-writer` → ... → `publish-final-check` | 跨阶段，先 CHECKPOINT 确认全链路 |
| "这个主题怎么写，有没有相关资料" | `lean-ctx` / `agent-reach` | 调研选型，仓库内 vs 全网/多平台 |
| "我想先和你讨论文章结构，你给我几个选项，我补充想法，定完再逐节设计和生成" | `article-writer`（协作模式） | 命中默认协作写作流：结构方案 → 方向确认 → 一次性展开全篇细骨架 → 讨论并明确冻结 → 逐节初稿预览 → 确认后落盘 → 审查循环 |
| "我想边学习边写这个开源项目" | `agent-reach` → 学习路径 → 对话初稿 → `edit-article`/`article-writer` | 先学出心智模型，再给用户看增量初稿；用户确认后才沉淀进现稿 |

## 8. 路由失败兜底

读 §1 + §7 仍无法定 → 走共享兜底 [`ai-coding-guide/references/fallback-template.md`](../ai-coding-guide/references/fallback-template.md) 第一问定主域，再回到本 guide §1 路由表收口。本 guide 不重复展开跨域反问。

**写作域专属兜底**：跨阶段（写+审、写+发布）、边学边写已分别走 §3 默认 pipeline 与 learning-guide 串行规则（见 §3 边学边写节「主路径归口」）。
