# Article Writing Guide — 详细路由规则

SKILL.md 给一句话路由表；本文件覆盖**边界 case、决策树、多 skill 串联顺序、反模式**。agent 在 SKILL.md §4 规则4（模糊无法匹配）时读本文件。

成本标注（与 SKILL.md 一致）：🪶轻 / 🪨重 / 🔥烧 token。

---

## 1. 起草阶段决策树

```
用户要写文章
├─ 有现成素材（笔记/碎片/旧稿）？
│   ├─ 是 + 纯碎片未结构化 → writing-fragments 🪶（挖素材）→ writing-shape 🪨（塑形）
│   ├─ 是 + 已有 .md 粗稿 → writing-shape 🪨
│   └─ 否（从零）→ 看文体
├─ 文体？
│   ├─ 博客/教程/方案/知识库/面试题/工具推荐/面经 → article-writer 🪨
│   ├─ 强叙事、想边写边选支线 → writing-beats 🪨
│   └─ JavaGuide 项目内（docs/ai 系列、my-submission/） → article-writer 🪨（JavaGuide 模式，执行规范见其 §6，终检判定见 javaguide-style-guide）
└─ 需要先调研？
    ├─ 本仓库 .md → doc-finder 🪶
    ├─ Obsidian 本地笔记库 → obsidian-vault 🪶
    ├─ 全网某话题近 30 天热度/讨论 → last30days 🪶（Reddit/X/HN/YouTube/TikTok）
    ├─ AI 行业资讯/日报/热点 → aihot 🪶（中文）
    ├─ 多平台定向检索（小红书/抖音/微博/B站/公众号…） → agent-reach 🪶
    ├─ 全网多源带引用 → deep-research 🔥（系统内置，先 §4 规则6 校验存在）
    └─ 产品/公司/人物深度研究 → hv-analysis 🔥（插件内置）
```

## 2. 改写 vs 润色 vs 规范化（最易混）

| 用户原话 | 真实意图 | skill |
|---------|---------|-------|
| "结构乱""重新组织""逻辑不顺""章节调整" | 改**骨架** | `edit-article` 🪨 |
| "AI 味重""不像人写的""文风生硬""改自然点" | 改**肉**（措辞/语气） | `ai-text-polisher` 🪨 |
| "中英文空格""标点不对""标题层级乱""引号格式""批量规范" | 改**皮**（排版） | `chinese-markdown-normalizer` 🪶 |
| "深度改写整篇""重写这篇""骨架和措辞都要动" | 改**骨架+肉**（整体重写） | `article-writer` 🪨（深度改写模式） |
| "帮我改改这篇"（模糊） | 不确定 | 先问改哪层；或按 骨架→肉→皮 顺序串行；若要整体重写走 `article-writer` |

**串行顺序**（三层都要改时）：`edit-article` → `ai-text-polisher` → `chinese-markdown-normalizer`。先动骨架会牵动措辞；最后规范排版避免反复改格式。

## 3. 审校三 skill + 发布闸选择

| 维度 | tech-article-review 🪨 | multi-review-pipeline 🔥 | review-doc 🔥 | publish-final-check 🔥 |
| 模式 | 逐段增量、可标 VERSION | 4 评论者并行 | 4 维度并行（事实/一致性/风格/结构） | 发布前强制关卡（4 子项） |
| 输出 | 评审意见 + 增量标注 | 修订清单 + **直接执行修正** | 聚合**报告**（不自动改） | PASS/FAIL + 必改清单（**不改**） |
| 何时用 | 单次快评、贴合 JavaGuide 风格 | 要"审查+批量改"一步到位 | 只要报告，人工决定改不改 | 发布前最后一闸，只放行 |
| 文体偏向 | 后端/AI/分布式/高并发 | 通用文档 | 中文技术文章 | 通用 |

**规则**：
- 用户说"审完顺手改了" → `multi-review-pipeline`。
- 用户说"先出报告我看看" → `review-doc`。
- 用户说"快速过一遍 / 逐段标一下" → `tech-article-review`。
- 用户说"发布前过一遍 / 能不能发了" → `publish-final-check`（强制关卡，末环）。
- JavaGuide 模式下审校**首选** `tech-article-review`（风格贴合）。
- **非后端文体**（前端/算法/数据结构/通用科普）→ `review-doc` 或 `multi-review-pipeline`（通用）；`tech-article-review` 仅后端/AI/分布式/高并发强相关时首选。

**叠加规则**：
- `tech-article-review`（逐段深挖）**可与** `review-doc`（全局报告）串行叠加：先 review-doc 全局定位 → 再 tech-article-review 对热点段逐段深挖。
- `multi-review-pipeline` 已含逐段审查，**不与** `tech-article-review`/`review-doc` 叠加（功能重叠）。
- 三者均不改成稿骨架，发布前再跑 `publish-final-check` 放行。

## 4. 配图两件套顺序

铁律：**先决策后画图**。

1. `drawio-article-illustration` 🪶 — 读正文，判断：哪里**真正需要**图（避免装饰图）、用什么图型（流程/架构/时序/状态机/ER）。输出"配图清单 + 类型建议"。
2. `drawio-chart` 🪨 — 按清单实际画，导出 PNG/SVG/PDF。
3. 画完回到 `drawio-article-illustration` 做**图文一致性校验**（图与正文是否对得上）。
4. **图注一致性**：每张图补图注/编号（图1、图2…），正文引用处与图注编号对齐；中文文章 alt 文本用中文简述，不空、不写文件名。

禁止：跳过 ① 直接 `drawio-chart` 画装饰图。

## 5. 查重前置条件（只比贴源模式）

`plagiarism-audit` 🪨 **只比用户贴的参考源**，不主动搜全网。前置：

- **必须**用户提供外部来源（URL / 文件路径 / 粘贴文本）。无来源 → 先问用户对齐哪些来源，或先用 `doc-finder`/`deep-research` 拉候选来源。
- 用户明确声明"无参考源" → 跳过查重，但终检报告标 `⚠️ 未查重`。

**判定边界**（plagiarism-audit 内核，两类文本区别对待）：
- **技术事实描述**（如"TCP 三次握手步骤""HTTP 状态码 200 含义"）→ **允许相似**，不必改。事实就是事实。
- **原创措辞搬运**（比喻/结构/举例/表达方式直接搬）→ **必改**。即使观点参考，措辞必须原创。

**JavaGuide 铁律**："只可参考不可抄袭"——参考要点 OK，但措辞、结构、举例必须原创。

**改写示例**：

| 原文（参考源） | 抄袭版（必改） | 原创版（OK） |
|---------------|---------------|-------------|
| "RAG 就像是给大模型开卷考试" | "RAG 如同给大模型开卷考"（同比喻换词） | "RAG 的本质是把检索当外挂记忆，模型答题前先翻资料"（换比喻+加判断） |
| "Agent 记忆分短期和长期" | "Agent 的记忆有短期和长期两类"（换虚词） | "Agent 记忆按生命周期切：当前会话的临时缓存 vs 跨会话的持久化沉淀"（换框架） |

**关键**：换同义词不算原创，换比喻/结构/视角才算。

## 6. 完整 pipeline 串联（含发布闸 + 落盘规则）

通用技术文章发布前，按序：

1. `article-writer` 🪨 起草（或 `writing-shape` 从素材塑形）
2. `edit-article` 🪨 调结构
3. `ai-text-polisher` 🪨 去 AI 味
4. `drawio-article-illustration` 🪶 + `drawio-chart` 🪨 配图
5. `multi-review-pipeline` 🔥 多维度审校 + 批量改
6. `plagiarism-audit` 🪨 查重（只比贴源，**需外部来源，否则跳过**）
7. `chinese-markdown-normalizer` 🪶 排版规范
8. **`publish-final-check`** 🔥 发布闸（4 子项 MUST/SHOULD 终检，MUST 全 PASS 才放行）

JavaGuide 模式：步骤1 切 JavaGuide 模式（执行规范见 `article-writer` §6）；步骤5 可换 `tech-article-review`；步骤6 对齐"只可参考不可抄袭"；步骤8 风格子项对照 `javaguide-style-guide` §1 M1-M9 + §2 量化阈值。

> **路径稳定性**：`my-submission/`、`docs/ai/` 等 JavaGuide 关键词以**目标仓库实际目录为准**（仓库重构时可能改名/迁移）；命中 JavaGuide 模式前先确认目录存在，别凭关键词硬套。

**中间产物落盘规则**（断点续跑 / 版本回滚用）：

```
<slug>/
├─ draft.md                 # 步骤1 起草产物
├─ draft-v2-structured.md   # 步骤2 调结构后
├─ draft-v3-polished.md     # 步骤3 去AI味后
├─ draft-v4-illustrated.md  # 步骤4 配图后
├─ draft-v5-reviewed.md     # 步骤5 审校改后
├─ draft-v6-final.md        # 步骤6-7 查重+排版后
└─ publish-report.md        # 步骤8 publish-final-check 报告
```

规则：每步输出独立文件，不覆盖上版；回滚直接取上一版；最终发布物 = `draft-v6-final.md`（publish-final-check PASS 后）。

## 7. 反模式（不要这样做）

- ❌ 用户说"写篇文章"就直接徒手写 → 应委派 `article-writer`。
- ❌ 用户说"去 AI 味"用 `edit-article` → 应 `ai-text-polisher`（edit-article 改结构不改文风）。
- ❌ 跳过 `drawio-article-illustration` 直接画图 → 易产装饰图。
- ❌ 无外部来源就跑 `plagiarism-audit` → 会空转（用户声明无源才跳过）。
- ❌ 把本路由器当执行器（自己重写各 skill 能力） → 本 skill 只**定路由**，执行委派给具体 skill。
- ❌ `multi-review-pipeline` 与 `review-doc` 同时调 → 功能重叠，选其一（要改选前者，要报告选后者）。
- ❌ 把 `publish-final-check` 当审校用 → 它是**发布闸**（只放行不改），审校在前序步骤 5 完成。
- ❌ 跳过 `publish-final-check` 直接发布 → 最后一闸缺失，死链/查重/风格硬伤可能漏网。
- ❌ `plagiarism-audit` 主动搜全网 → 当前模式**只比贴源**，主动搜未启用（如需启用另议）。
- ❌ 混淆 `javaguide-style-guide` 与 `article-writer` §6 → 前者**终检判定**（M1-M9 + 阈值），后者**写作执行**（含 §6.7 自检、§6.9 反例）；publish-final-check ③ 引用前者不引用后者。

## 8. 路由失败兜底

读完本文件 + SKILL.md §7 端到端示例仍无法定路由 → 反问用户三要素：
1. **文体**：博客 / 教程 / 方案 / 知识库 / 面试题 / 面经 / 叙事？
2. **阶段**：从零写 / 改现稿 / 审校 / 查重 / 配图 / 发布闸？
3. **目标仓库**：通用 还是 JavaGuide（docs/ai 系列）？

拿到答复后回 SKILL.md §1 表定位。

> 端到端路由示例见 SKILL.md §7（query → skill → 理由 10 条）。测试用 prompt 见同目录 `test-prompts.json`。
