# docs/ai 概念系列 — 写作风格指纹

> 调研来源：8 篇代表性文章（mcp / skills / context-engineering / harness-engineering / rag-optimization / rag-basis / llm-gateway / agent-interview-questions）
> 调研时间：2026-06-27

---

## 1. 开头钩子模式

### 1.1 模式分布统计表

| 模式 | 篇数 | 占比 | 出现文章 |
|------|------|------|----------|
| 个人经历/踩坑引入 | 3 | 37.5% | mcp、rag-optimization、context-engineering |
| 常见误区/反直觉破题 | 2 | 25% | harness-engineering、rag-basis |
| 场景对话/面试官对话 | 1 | 12.5% | llm-gateway |
| 读者困惑/两种极端 | 1 | 12.5% | agent-interview-questions |
| 团队协作痛点 | 1 | 12.5% | skills |

### 1.2 各模式原文片段佐证

**模式 A：个人经历/踩坑引入（最主流，3 篇）**

- **mcp**：开篇先承认自己曾经的判断错了。
  > "做 LLM 应用时，我一开始也以为最麻烦的是模型接入。后来发现不是。OpenAI、Claude、DeepSeek、Qwen 这些模型虽然接口不完全一样，但各家 SDK 已经把很多细节包掉了……更烦的是工具。"

- **rag-optimization**：用"很多玩家的体验都差不多"切入普遍痛点。
  > "第一次做 RAG 时，很多人的体验都差不多：文档切了，向量库建了，Top-K 也调大了，模型还是一本正经地胡说八道。"

- **context-engineering**：先共情读者的 OS（内心独白）。
  > "你好，我是小 G。现在这个时候再去聊 Context Engineering，很多朋友内心 OS 是：还有必要吗？这不老掉牙的概念了么？……说实话，我之前也是这么想的。但后来实际去深入了解了才发现，根本不是这么回事。"

**模式 B：常见误区/反直觉破题（2 篇）**

- **harness-engineering**：一句话否定读者直觉。
  > "别只盯模型。很多人第一次做 Agent，直觉都是先买更贵的模型。结果模型换了，Agent 还是会重复犯错……有个实验挺能说明这件事：同一个模型，只换了文件编辑接口的调用方式，编码基准分数从 6.7% 跳到了 68.3%。"

- **rag-basis**：先讲团队常见错误做法，再引出主题。
  > "做企业知识库问答时，很多团队的第一反应都是：把文档全塞给大模型，让它自己读。文档少的时候，这招确实能跑。一旦知识库涨到几十万字，问题很快就出来了。"

**模式 C：场景对话/面试官对话（1 篇，效果最戏剧化）**

- **llm-gateway**：直接用面试场景的对话开场，像剧本。
  > "面试官看了一眼我的 AI 项目架构图，突然停住了。'你这个 Agent，每次都是调用旗舰模型？' 我点点头：'对啊，肯定得用地表最强的啊，效果好。' 他沉默了两秒……"

**模式 D：读者困惑/两种极端（1 篇）**

- **agent-interview-questions**：先列举两种常见极端回答，再给出中间路线。
  > "AI Agent 面试最容易出现两种极端：一种是把 Agent 讲得像'全自动数字员工'，什么都能自己规划、自己执行；另一种是把 Agent 讲得像'几个 Prompt 串起来'……真正好的回答要落到中间。"

**模式 E：团队协作痛点（1 篇）**

- **skills**：从团队里重复粘贴 Prompt 的真实场景切入。
  > "团队里有套完整的代码审查规范，想让 Claude 按这个来 review。最直接的做法是每次粘到 Prompt 里——它倒是照做了，但下次换个会话，换个同事，又得粘一遍。"

### 1.3 关键规律（普遍现象，≥5 篇）

- **开头不写"本文将介绍 X"**：8 篇全部用故事/痛点/反直觉开场，没有一篇用学术化摘要开头。
- **第二段才点题**：所有文章在 2-4 段铺垫后才出现"这就是 X 要解决的问题"或"本文就聊聊 X"的转折句。
- **第一人称代入感强**："我一开始也以为""说实话，我之前也是这么想的""很多朋友的体验都差不多"。

---

## 2. 结构组织

### 2.1 章节层级习惯

- **## 一级标题是主骨架**：每篇 8-15 个 `##` 标题，密度高（约每 500-800 字一个）。
- **### 二级标题用于细分**：出现在概念拆解型文章中（mcp、skills、context-engineering、rag-optimization），面试题和 RAG 基础篇用得少。
- **#### 三级标题极少**：仅 harness-engineering 在案例小节里用（如"OpenAI：三个人，五个月"下的子小节）。

### 2.2 导航列表（普遍现象，6/8 篇）

绝大多数文章在开头第 3-5 段放一个编号列表，明确告知"本文 X 字，主要看这几块"。格式高度统一：

- **skills**："本文接近 9000 字，建议收藏，通过本文你将搞懂：1. ... 2. ... 3. ..."
- **context-engineering**："文章比较长，接近 1w 字。看完之后你大概能搞明白几件事：1. ..."
- **harness-engineering**："全文接近 7800 字，主要看这几块：1. ..."
- **rag-optimization**："接近 1.5w 字，建议收藏。主要内容：1. ..."
- **rag-basis**："这篇文章接近 6200 字，主要讲清楚几件事：1. ..."
- **llm-gateway**："本文接近 1.2w 字，建议收藏，通过本文你将搞懂：1. ..."

**个别现象**（mcp、agent-interview-questions）：无字数导航，但 mcp 有 blockquote 版本声明，interview-questions 用编号列表代替。

### 2.3 内容组织模式归类

| 文章 | 组织模式 | 说明 |
|------|----------|------|
| mcp | 概念拆解型 | 全称拆解 → 角色关系 → 调用流程 → 协议细节 → 落地清单 |
| skills | 概念拆解型 | 定义 → 边界关系 → 写法规范 → 进阶策略 → 踩坑清单 |
| context-engineering | 概念拆解型 | 反差现象 → 定义 → 失效机理 → 加载策略 → 落地组装 |
| harness-engineering | 系统工程+案例型 | 概念 → 六层架构 → 瓶颈分析 → 落地优先级 → 一线团队案例 |
| rag-optimization | 系统工程型 | 全链路拆解 → 数据 → Chunk → 召回 → 重排 → 上下文 → 评估 → 排查路径 |
| rag-basis | 概念拆解+面试导向型 | 定义 → 必要性 → 对比（搜索/微调/长上下文） → 优劣势 → 面试清单 |
| llm-gateway | 系统设计型 | 定义 → 动机 → 能力拆解 → 设计落地 → 方案选型 → 指标 |
| agent-interview-questions | 面试题索引型 | 按主题分组，每组给出关键点+高频题+回答框架 |

### 2.4 标题句式特征

- **疑问句密度极高**（普遍现象，8/8 篇）：几乎每个 `##` 都用疑问句。
  - "MCP 到底是什么？""MCP、Function Calling、Agent 到底是什么关系？""stdio 和 Streamable HTTP 怎么选？"
  - "为什么 MCP 用 JSON-RPC？""MCP 接进来之后，就能直接上生产吗？"
  - "RAG 优化到底在优化什么？""Chunk 策略：别把知识切碎了""Top-K 不是越大越好"
  - "长上下文窗口会取代 RAG 吗？""RAG 和微调怎么选？"

- **⭐️ 标记**：仅 skills 用了 `⭐️` 前缀标记重要章节（"⭐️SKILL.md 到底怎么写？""⭐️延迟加载与渐进式披露""⭐️总结下写 Skill 时最容易踩的坑"）。其他 7 篇不用。属于个别现象。

- **口语化句式**：标题里直接用"到底""能不能""怎么选""别把 X 切碎了""不是越大越好"等口语表达。普遍现象。

- **否定式/反直觉标题**："别把知识切碎了""不是越大越好""别把模型当垃圾桶""为什么瓶颈经常不在模型？"。rag-optimization 和 harness-engineering 最爱用。

---

## 3. 语言 DNA

### 3.1 高频口语词清单（按跨篇出现频率排序）

| 口语词/短语 | 出现篇数 | 代表原文片段 |
|-------------|----------|-------------|
| **说白了** | 5+ | rag-optimization "RAG 说白了，就是先从知识库里找"；rag-basis "RAG 说白了" |
| **坑 / 踩坑** | 8（全系列） | mcp "这里最容易踩的坑"；skills "写 Skill 最容易踩的 8 个坑"；rag-optimization "这里有个坑" |
| **别 / 不要** | 8（全系列） | rag-optimization "别把模型当垃圾桶"；skills "不要把 Skill 写成科普文" |
| **搞懂 / 搞明白** | 5+ | skills "通过本文你将搞懂"；context-engineering "你大概能搞明白几件事" |
| **其实** | 8（全系列） | mcp "其实就很清晰了"；rag-basis "RAG 要做的事其实很直接" |
| **更稳的做法 / 更好的做法** | 6+ | rag-optimization "更稳的做法是：能预过滤就预过滤"；mcp "更推荐把工具拆小一点" |
| **这种 / 这类** | 8（全系列） | 几乎每段都有 |
| **一句话** | 5+ | context-engineering "用一句话概括就是"；rag-basis "简单来说" |
| **注意 / 需要注意** | 8（全系列） | skills "需要注意" |
| **说白了 / 简单说 / 简单来说** | 8（全系列） | 极高频 |
| **不是 X，是 Y** | 8（全系列） | mcp "它不是让模型变聪明……它更像一套接线规范" |
| **至少 / 最好** | 8（全系列） | mcp "至少先看源码" |

### 3.2 第一人称密度

- **"我"**：mcp、context-engineering、rag-optimization、llm-gateway 高频使用（每篇 10-20 次）。开头和总结段尤其密集。
- **"我们"**：较低频，主要用于"我们换一个改写看看"（context-engineering）、"我们前面列举的"（skills）这类引导语。
- **"Guide"**（第三人称自称）：出现在 rag-optimization（"Guide 的经验是""Guide 的建议""Guide 比较推荐的排查路径"）和 context-engineering（"Guide 见过不少团队"）。约 5-8 次/篇。属于部分文章特征。
- **"G 友"**（对读者的称呼）：mcp 和 context-engineering 用过（"G 友问""G 友发来一句话"）。个别现象。

### 3.3 句式特征

- **短句 + 长句交替**：极有节奏感。典型段落模式——一句短观点（10 字内）+ 一句长解释（30-50 字）。
  - mcp："MCP 解决的就是这类问题。"（短）→ 后跟长段解释。
  - harness-engineering："别只盯模型。"（4 字开篇）→ 后跟长段。
  - rag-optimization："Demo 阶段这样挺好。问题是一到生产，麻烦就会出来。"

- **转折方式**：高频用"但""不过""反过来""问题是""麻烦的是"。
  - mcp："它不是银弹。它不像 gRPC 那样有强 IDL……"
  - skills："但这种写法没有规定 Agent 必须按哪个文件……"

- **确定性表达**：大量使用加粗的判断句作为段落的"锚点"。
  - context-engineering："**上下文不够的时候，模型再强也只能靠猜；上下文给对了，中等水平的模型也能把任务做下去。**"
  - rag-optimization："**它本质上是数据、切分、索引、召回、重排、上下文、生成、评估共同组成的系统工程，不是单点调参。**"

### 3.4 误区破题范式（"很多人以为 X，其实 Y"）

**普遍现象**（7/8 篇使用），是该系列最核心的说理范式。

代表实例：

- mcp："这里最容易踩的坑是把 MCP 当成'模型调用工具'的全部过程。其实模型只负责判断和生成调用意图，MCP 负责把这个调用接到外部系统上。"
- skills："所以不建议把 Skill 说成'基于 Function Calling 的封装'，这个说法容易把人带偏。"
- context-engineering："很多朋友（包括我刚开始学的时候）会觉得：窗口越大，能塞的信息越多，模型的表现应该越好才对。但实际情况是：**上下文存在边际收益递减，塞过头了效果反而可能变差。**"
- harness-engineering："第一次听到这个结论，很多人会觉得反直觉。模型不够聪明，那等更强的模型出来不就好了？"
- rag-optimization："很多人直接上 reranker，发现没效果，根因是粗召回阶段就没把正确文档找出来。"
- llm-gateway："很多朋友第一次做 AI 应用都会踩这个坑：以为模型越强，系统越稳。"

---

## 4. 格式元素

### 4.1 代码块

- **密度**：概念拆解型（mcp/skills/context-engineering）每千字约 0.5-1 个代码块；系统设计型（rag-optimization/llm-gateway）每千字约 1-2 个。
- **语言标注分布**：
  - `json`：最高频（协议示例、配置、Trace 日志）。mcp、rag-optimization、llm-gateway 大量使用。
  - `yaml`：skills（元数据）、llm-gateway（路由配置）。
  - `python`：mcp（Server 示例）、skills（脚本示例）、context-engineering（Context Assembler 伪代码）。
  - `java`：llm-gateway 独有（`LLMGateway` 接口、`RuleBasedModelRouter`）。
  - `text` / `bash` / `markdown`：用于目录结构、命令、SKILL.md 示例。
  - `mermaid`：rag-optimization 大量使用（4 个 flowchart），其他篇偶用。
  - `ebnf`：harness-engineering 用过一次（GAN 架构语法描述）。
- **中文注释**：普遍存在。代码块内注释用中文。
  - mcp Python 示例：`"""获取指定城市的天气信息"""`
  - skills Python 示例：`# ✓ 推荐：错误条件写清楚`
  - llm-gateway Java 示例注释为英文字段名，但正文解释用中文。

### 4.2 表格

- **密度**：极高。8 篇全部使用，平均每篇 5-10 个表格。
- **类型分布**：
  - **对比型**（最常见）：两个概念/方案的维度对比。如 mcp 的"场景 vs 更关键的东西"、rag-basis 的"RAG vs 微调"、llm-gateway 的"LLM Router vs LLM Gateway"。
  - **层级/分层型**：如 harness-engineering 的六层架构表、llm-gateway 的"任务三层分层"。
  - **诊断/排查型**：如 rag-optimization 的"失败样本分类"、llm-gateway 的"错误类型 vs 是否适合 fallback"。
  - **清单型**：如 mcp 的"企业落地检查清单"、rag-optimization 的"指标表"。
- **首列加粗**：普遍现象。skills 的"好的命名 vs 不好的命名"表、llm-gateway 的路由策略表、harness-engineering 的阶段表，首列均加粗。

### 4.3 Blockquote

- **用途分布**：
  - **官方引用**：context-engineering 引用 Tobi Lutke 原话、harness-engineering 引用 OpenAI/Anthropic 原话。
  - **补充说明/版本声明**：mcp 开头的版本声明 blockquote（"说明一下：MCP 还在快速演进……"）。
  - **扩展阅读引导**：rag-basis 在正文中用 blockquote 引导到其他篇章。
- **密度**：低。每篇 0-3 个。不作为主要表达手段。

### 4.4 Mermaid

- **密度**：rag-optimization 独占鳌头（4 个 flowchart），其他篇 0-1 个。
- **配色**：rag-optimization 的 Mermaid 有统一的 classDef 配色方案——`client`（青色 #00838F）、`business`（橙色 #E99151）、`infra`（紫色 #9B59B6）、`success`（绿色 #4CA497）、`warning`（黄色 #F39C12）、`danger`（红色 #C44545）、`gateway`（紫色 #7B68EE）。
- **方向**：LR 为主（流程链路），TB 用于层级递进（如 Top-K 分层、排查路径）。
- **节点样式**：统一用 `rx:10,ry:10` 圆角矩形。

### 4.5 配图

- **预制图为主**（普遍现象，8/8 篇）：所有文章的架构图、概念图都是 `https://oss.javaguide.cn/` 上的预制 PNG/SVG/JPEG。
  - mcp：`mcp-simple-diagram.png`、`mcp-four-layer-architecture.png`、`mcp-call-seq.png`、`mcp-transport-decision.png`、`mcp-fc-agent-layer.png`
  - context-engineering：`why-the-same-agent-performs-so-differently.png`、`prompt-vs-context-engineering-dimension-comparison.svg`
  - harness-engineering：`harness-agent-equals-model-harness-arch.png`、`harness-engineering-six-layer-architecture.svg`
  - skills：`skills-agent-execution-link.png`、`skills-progressive-disclosure-three-layer-model.png`
- **文件名规范**：英文短横线分隔，语义化命名，带主题前缀。如 `mcp-four-layer-architecture.png`、`context-engineering-run-time-retrieval.png`。
- **截图**：skills 有 2 张截图（`skillssh.png`、`superpowers-skills.png`），是平台/工具的实际截图。其他篇几乎没有截图。
- **密度**：每篇 3-8 张预制图，平均每 800-1200 字一张。

---

## 5. 比喻范式

### 5.1 密度

- **平均每千字 1-2 个生活化比喻**。概念首次出现或抽象难懂处必出比喻。
- mcp、context-engineering、harness-engineering、skills 比喻密度最高；rag-optimization 和 llm-gateway 相对少（更偏工程清单）。

### 5.2 比喻类型分类

| 类型 | 实例数 | 代表 |
|------|--------|------|
| 厨房/做饭类比 | 3+ | mcp 厨师做凉拌黄瓜、context-engineering 厨师+厨房 |
| 工作台/书桌类比 | 2+ | context-engineering "工作台"、rag-optimization "垃圾桶" |
| 操作系统/内存类比 | 2 | context-engineering "LLM 的内存管理"、harness-engineering "CPU + OS" |
| 开卷考试类比 | 1 | context-engineering "长上下文就像开卷考试" |
| 旅游/地图类比 | 2 | skills "查书一样"、harness-engineering "到新城市+地图" |
| 员工/团队类比 | 2 | skills "老员工脑子里的规矩"、harness-engineering "给新员工搭工作环境" |
| 日用品/场景类比 | 多 | rag-basis "员工手册背 vs 查"、rag-optimization "证据加工流水线" |

### 5.3 精彩比喻清单（技术概念 = 生活场景）

1. **MCP = 接线规范/USB-C**（mcp）——原文："它更像一套接线规范"，但作者主动吐槽"AI 领域的 USB-C"这个比喻"容易让人误会它什么都能统一"。
2. **Resources/Tools/Prompts = 食材/动作/家庭偏好**（mcp）——"Resources 像食材和菜谱……Tools 像具体动作，比如切菜、拌料、开火……Prompts 像家里的固定偏好，比如少放辣、必须放香菜"。
3. **Context Engineering = 给厨师准备厨房**（context-engineering）——"如果 Prompt Engineering 是'告诉厨师这道菜怎么做'，那 Context Engineering 更像是给厨师准备厨房——食材放在哪、刀具怎么摆、调料怎么分类"。
4. **Context Engineering = LLM 的内存管理**（context-engineering）——"上下文窗口就是一块有限内存……窗口满了就得淘汰内容，这跟操作系统里的页面置换是一个思路，比如 LRU"。
5. **长上下文 = 开卷考试**（context-engineering）——"长上下文就像开卷考试，你把一大堆资料带进考场。理论上资料越多越好，但资料带多了不代表你能快速找到答案"。
6. **长上下文 = 工作台（不是垃圾桶）**（context-engineering）——"长上下文不是垃圾桶，不能什么都往里丢。它更像一张工作台"。
7. **Agent = Model + Harness = CPU + OS**（harness-engineering）——"可以把模型想成 CPU，把 Harness 想成操作系统。CPU 再强，OS 如果天天崩，体验也不会好"。
8. **Harness 六层 = 给新员工搭工作环境**（harness-engineering）——"L1 是岗位说明……L2 是办公工具……L3 是标准操作流程……L4 是项目管理系统和笔记本……L5 是质检流程……L6 是红线规则和应急预案"。
9. **渐进式披露 = 查书/到新城市给地图**（skills/harness-engineering）——"就像查书一样。你不会先把整本书背下来，而是先看目录"。"你不需要一上来背完整本旅游指南，先给一张地图"。
10. **RAG = 证据加工流水线**（rag-optimization）——"RAG 更像一条证据加工流水线：原始资料先被解析、清洗、切块、打标签、建索引"。
11. **RAG = 随查随用 vs 微调 = 背下来**（rag-basis）——"RAG 的思路是随查随用，把手册放在外面。微调的思路是把手册背下来"。
12. **上下文窗口 = 垃圾桶**（rag-optimization）——章节标题直接用"别把模型当垃圾桶"。
13. **Skill = 老员工脑子里的规矩**（skills）——"它更像是把'老员工脑子里的规矩'写进 SKILL.md"。
14. **context resets = 程序重启恢复检查点**（harness-engineering）——"这有点像程序遇到内存泄漏……重启进程，再从检查点恢复状态"。

### 5.3 比喻出现位置规律（普遍现象）

1. **概念首次定义后立即出比喻**：定义完抽象概念，紧跟一句"打个比方"或"可以这么理解"。
2. **反直觉/难懂机理处出比喻**：如 Context Rot、Lost in the Middle、Token 预算这些机理，必配比喻。
3. **对比两个易混概念时出比喻**：RAG vs 微调、Prompt vs Context Engineering、Router vs Gateway，都靠比喻拉开差异。

---

## 6. docs/ai 概念系列独有特征（区别于实战系列的本质特征）

### 特征 1：疑问句标题 + 误区破题是骨架，不是装饰

8 篇文章的 `##` 标题几乎全是疑问句，正文几乎每个核心论点都用"很多人以为 X，其实 Y"范式展开。这不是偶发修辞，而是该系列的说理骨架——先立靶子（常见误区/直觉判断），再打靶子（给出工程真相）。实战系列更偏"怎么做"，概念系列更偏"为什么不是你想的那样"。

### 特征 2：导航列表 + 字数声明是标配开头仪式

6/8 篇在开头第 3-5 段固定放"本文接近 X 字，主要看这几块：1. 2. 3."。这个仪式感极强的开头模板，是该系列的签名特征。实战系列通常不会有这种"阅读契约"。

### 特征 3：比喻密度极高，且每个核心概念必配一个"锚定比喻"

概念系列平均每千字 1-2 个生活化比喻，且每个抽象概念（MCP、Context Engineering、Harness、RAG、Progressive Disclosure）都有一个会被反复回引的"锚定比喻"（接线规范/厨房/内存管理/CPU+OS/流水线/查书）。比喻不是点缀，是概念系列让读者记住概念的主要载体。

### 特征 4：预制图为主，Mermaid 仅在流程密集篇出现

8 篇全部使用 `oss.javaguide.cn` 上的预制 PNG/SVG 图，文件名英文短横线化、语义化。Mermaid 流程图只在 rag-optimization 这种"全链路流程"文章里密集出现（4 个），且有统一配色体系。其他篇靠预制图+表格表达结构，不用 Mermaid。

### 特征 5：交叉引用织入正文，不单列"相关阅读"

context-engineering 在讲 Progressive Disclosure 时直接内链到 skills 文章；harness-engineering 在讲渐进式披露时内链到 skills；rag-basis 在讲优化时内链到 rag-optimization。交叉引用是论证的一部分，不是文末附录。

### 特征 6：表格是该系列的"第二语言"

平均每篇 5-10 个表格，用于对比、分层、诊断、清单。概念系列几乎不用纯文字段落来表达"多个维度的对比"——只要有对比结构，必然表格化。首列加粗是惯例。

### 特征 7：结尾必回扣"误区破题" + 给出最小可行路径

所有文章的总结段都会回到开头的误区，并给出一条"先做 X，再做 Y"的最小落地路径。如 context-engineering 结尾"先把 System Prompt 和工具边界写清楚；再把 RAG 检索做准"；harness-engineering 结尾"先把 L1 和 L6 做好"；rag-optimization 结尾给 9 步落地优先级。概念系列的总结不是"本文讲了什么"，而是"你现在该先做什么"。

### 特征 8：第一人称 + 口语化短句构建"老司机在跟你聊"的氛围

"我一开始也以为""说实话""说白了""这里有个坑""更稳的做法是"——这套语言 DNA 让技术概念文章读起来像一个有实战经验的人在面对面给你讲，而不是教科书在陈述定义。这在面试题篇和概念篇里尤其突出。
