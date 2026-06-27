# docs/ai-coding 实战系列 — 写作风格指纹

> 调研来源：7 篇代表性文章（cases × 3 + practices × 4）
> 调研时间：2026-06-27
> 文章清单：
> - cases: cc-glm5.1 / claude-desktop-cc-switch / deepseek-v4-claude-code
> - practices: claude-md-best-practices / spec-coding / the-cool-tricks-for-vibe-coding / claudecode-tips

---

## 1. 开头钩子模式

### 1.1 统计表

| 篇目 | 子系列 | 开头模式 | 自称 |
|------|--------|----------|------|
| cc-glm5.1 | cases | 打招呼 + 上下文承接 + 本文目标三段式 | "大家好，我是 Guide"（一次） |
| claude-desktop-cc-switch | cases | 打招呼 + 上下文承接 + 本文目标三段式 | "你好，我是小 G" |
| deepseek-v4-claude-code | cases | 行业观察 + 字数预警 + 收藏暗示 + 导航列表 | 第三人称"Guide" |
| claude-md-best-practices | practices | 打招呼 + 读者来信承接 + 概念祛魅 | "你好，我是小 G" + 自称"小 G" |
| spec-coding | practices | 打招呼 + 填坑梗 + 读者催更截图 + 对话冲突开头 | "你好，我是小 G" |
| the-cool-tricks-for-vibe-coding | practices | 打招呼 + 读者反馈截图 + 体验回忆杀 + 真香反转 | "你好，我是小 G" |
| claudecode-tips | practices | 打招呼 + 数据炫耀（6w+）+ 体验回忆杀 + 真香反转 | "你好，我是小 G" |

### 1.2 普遍现象（≥4 篇出现）

**模式 A：打招呼 + 上下文承接（≥4 篇）**

5 篇用"你好，我是小 G"或"大家好，我是 Guide"开场（claude-desktop-cc-switch / claude-md-best-practices / spec-coding / the-cool-tricks-for-vibe-coding / claudecode-tips，cc-glm5.1 也用"大家好，我是 Guide"）。**cases 系列打招呼称呼偏正式（"大家好"），practices 系列统一为"你好，我是小 G"——这是两个子系列的稳定签名。**

实例 1（claude-desktop-cc-switch）：
> 你好，我是小 G。前面我们聊过了如何用 [CC Switch 让 Codex 和 Claude Code CLI 接入第三方模型](...)，今天我们聊聊如何让 Claude Desktop 也接入第三方模型。

实例 2（claude-md-best-practices）：
> 你好，我是小 G。前几天分享 [Claude Code 使用技巧](...) 的时候，我提到了一个很重要的文件 `CLAUDE.md`，并简单介绍了一下。
>
> 有 G 友在评论区留言：这个文件既然这么重要，能不能单独写一篇来讲？

实例 3（cc-glm5.1）：
> 大家好，我是 Guide。前面分享过 [IDEA 搭配 Qoder 插件的实战](...)和 [Trae 接入大模型的实战](...)，分别覆盖了 JetBrains 体系和 VS Code 体系下的 AI 辅助编码。这篇换个角度，聊聊 **Claude Code 接入第三方模型** 的实战体验。

**模式 B：本文目标三段式 / 导航列表（≥4 篇）**

cases 系列紧接打招呼给出"场景一/场景二"导航；practices 系列用"通过本文你将搞懂"列编号清单。

实例（cc-glm5.1）：
> 我选了两个比较有代表性的复杂场景来验证：
> - **场景一**：从零搭建一个基于 Arthas 的 JVM 智能诊断 Agent……
> - **场景二**：在百万级数据量的既有订单系统中定位并治理慢查询……

实例（deepseek-v4-claude-code）：
> 这篇文章接近 **7000 字**，建议收藏，通过本文你将搞懂：
> 1. **Claude Code 接入 DeepSeek V4 的两种方式**……
> 2. **五个真实开发任务的实战记录**……
> 3. **DeepSeek V4-Pro 和 Flash 的核心参数与定价**……

实例（spec-coding）：
> 这篇文章聊 Spec Coding 的核心思路，内容不少，建议收藏。通过本文你将搞懂：
> 1. Vibe Coding 和 Spec Coding 的实际差别……
> 2. 完整的 Spec Coding 落地流程……
> 3. Spec 在主流 AI IDE 里怎么配……

### 1.3 个别现象（1-2 篇）

- **对话冲突开头（spec-coding 独有）**：用同事/朋友的反驳对话切入，制造戏剧冲突：
  > 上周和同事聊天，他问我还在折腾 Spec Coding 干嘛。原话大概是："Claude Code 都能自己写代码了，你花时间写规范不是多此一举？"
  > 我当时没忍住怼了一句："AI 写出来的屎山代码，你来维护？"
  > 他愣了一下。

- **数据炫耀开头（claudecode-tips 独有）**：用公众号阅读量证明价值：
  > 公众号阅读一天时间就冲上了 6w+。

- **体验回忆杀 + 真香反转（practices 2 篇，the-cool-tricks 和 claudecode-tips）**：
  > 我反正是特别上头，24 年第一次接触 Cursor，真是惊为天人……（the-cool-tricks-for-vibe-coding）
  > 我一开始其实挺抵触命令行……结果用上之后，就真香了！（claudecode-tips）

### 1.4 cases vs practices 开头差异

| 维度 | cases | practices |
|------|-------|-----------|
| 自称 | "Guide" / "大家好，我是 Guide" | 统一"你好，我是小 G" |
| 钩子 | 场景导航（场景一/二） | 读者反馈截图 + 体验回忆杀 + 真香反转 |
| 字数暗示 | deepseek 篇暗示 7000 字 + 收藏 | spec-coding / the-cool-tricks 暗示"建议收藏" |
| 戏剧冲突 | 几乎没有 | 常用对话冲突 / 真香反转 |

---

## 2. 结构组织

### 2.1 cases 系列结构模板（3 篇高度一致）

```
1. 打招呼 + 上下文承接
2. 环境准备 / 安装配置（截图密集）
3. 场景一/实战一：需求 → AI 分析 → 代码 → 效果验证
4. 场景二/实战二（同上）
5. 实战总结（能力维度表 + 做得好/需注意 + 建议）
6. 写在最后 / 总结（哲学升华，强调人工评审）
7. 参考资料（cases 系列特有，列出官方文档链接）
```

cc-glm5.1 是这个模板的标本：环境准备 → 场景一（从零搭建 Agent） → 场景二（慢查询治理） → 实战总结（含能力维度表） → 写在最后 → 参考（5 条官方文档链接）。

deepseek-v4-claude-code 略有变体（实战 ×5 + 参数/定价表 + 场景建议表），但骨架一致。

claude-desktop-cc-switch 是 cases 中偏原理拆解的一篇：安装 → 配置全流程（含常见坑） → "背后在跑什么"原理拆解（架构/接管/请求翻译/容错） → "这些设计思路怎么用到 AI 应用开发里"。

### 2.2 practices 系列结构模板（4 篇高度一致）

```
1. 打招呼 + 读者反馈/催更/真香回忆
2. 概念祛魅 / 误区破题（"X 不是不能用" / "X 和 Y 不是一回事"）
3. 核心理念 / 四步法 / 主体内容（分小节，每节带代码块）
4. 进阶：项目变大后怎么管 / 分层 / 规模化策略
5. 踩坑 / 失败模式 / 常见错误（清单式）
6. 模板 / 命令清单 / 工作流清单（实战系列主力）
7. 总结（回扣核心理念，不写"写在最后"）
```

spec-coding 是标本：误区破题（Vibe Coding 不是不能用） → Spec Coding 是什么 → 四步落地 → 三色标签 → 项目大了怎么管 → 领域知识 → 完成自检清单 → 多代理协作 → Spec 不是写完就扔 → 模板 → 踩过的坑。

### 2.3 章节层级特征

**普遍现象（≥4 篇）**：

- **二级标题用问句 / 短句**（5 篇）：
  - "什么是 CLAUDE.md？"（claude-md-best-practices）
  - "Vibe Coding 不是不能用"（spec-coding）
  - "Spec Coding 到底是什么"（spec-coding）
  - "为什么 Claude Code 支持热切换而 Claude Desktop 不行"（claude-desktop-cc-switch）
  - "Spec 在 AI IDE 里怎么落地"（spec-coding）

- **导航列表 + 编号清单**（7 篇全有）：cases 用"场景一/场景二"，practices 用"通过本文你将搞懂 1/2/3"。

- **三级标题用动宾短语**（普遍）：如"添加 DeepSeek Provider"、"开启本地路由"、"切换并重启"。

### 2.4 ⭐️ 标记 / 表格使用

- ⭐️ 标记：**7 篇中未出现 ⭐️ 标记**（这是与 docs/ai 概念系列的可能差异点，实战系列更克制）。
- 表格密度高（普遍现象）：cc-glm5.1（能力维度表）、deepseek-v4-claude-code（参数表 ×2 + 定价表 + 场景建议表）、spec-coding（四步落地表 + 工具规范文件表）、claude-md-best-practices（vs AGENTS.md / vs .claude/rules / vs SPEC.md / 层级表）。**cases 系列表格偏"数据对比"，practices 系列表格偏"概念辨析"。**

---

## 3. 语言 DNA

### 3.1 高频口语词清单（按出现频率粗排）

| 词/短语 | 出现篇数 | 代表原文片段 |
|---------|----------|--------------|
| **真香** | 2（claudecode-tips、隐含 deepseek） | "结果用上之后，就真香了！"（claudecode-tips） |
| **爆肝** | 2（the-cool-tricks、claudecode-tips） | "于是，我爆肝了一篇"（两篇几乎同句） |
| **屎山代码** | 1（spec-coding） | "AI 写出来的屎山代码，你来维护？" |
| **一把梭** | 0（7 篇中未出现，注意区分概念系列） |
| **牛头不对马嘴** | 0（未出现） |
| **一本正经地胡说八道** | 0（未出现，但 deepseek-v4 有类似意象："看起来还挺像那么回事"） |
| **干活 / 干起活来** | 4+（普遍） | "V4-Pro 干起活来到底怎么样"（deepseek-v4）、"让 AI 干活"（spec-coding） |
| **翻车** | 3（the-cool-tricks、claudecode-tips、spec-coding） | "翻车情况也越来越多"（the-cool-tricks）、"翻车的场景不少"（spec-coding） |
| **兜底 / 兜得住** | 4+（普遍） | "失败了怎么兜底"（the-cool-tricks） |
| **跑起来 / 跑得起来** | 5+（普遍） | "代码看起来能跑"（spec-coding） |
| **劝退** | 2（spec-coding、the-cool-tricks） | "不然你会先被文档劝退"（the-cool-tricks） |
| **香**（单字，表性价比） | 1（deepseek-v4） | "Flash 的定价很香" |
| **还要什么自行车** | 1（deepseek-v4） | "考虑到 Flash 的价格优势——还要什么自行车？" |
| **能打** | 1（deepseek-v4） | "这个性价比相当能打" |
| **土但好用** | 1（claude-md-best-practices） | "我用一个很土但好用的问题" |
| **糊弄过去** | 1（the-cool-tricks） | "写一句'已验证'糊弄过去" |
| **赛博收银台 / 赛博** | 0（未出现） |

**与概念系列对比**：实战系列口语词总量更克制，更偏向"工程师行话"（兜底/翻车/干活/跑起来），概念系列的"真香/一把梭/牛头不对马嘴"这类夸张口语在实战系列明显减少。实战系列偶尔出现"屎山代码"（spec-coding），但整体口语化服务于"实操可信度"，不是为了趣味性。

### 3.2 第一人称密度

**普遍现象（7 篇全有）**：第一人称密度高，但 cases 与 practices 有差异。

- **practices 系列**：第一人称密度极高，几乎每段都有"我""小 G""我的项目""我自己的习惯"。典型句式：
  > 我一般只往里面放几类东西……我自己判断一条内容该不该放进去时，会用一个很土但好用的问题。（claude-md-best-practices）

- **cases 系列**：第一人称退到"笔者"或省略，更偏"操作记录体"。典型句式：
  > 笔者直接将系统日志中的慢查询告警丢给 AI，让其结合项目既有代码完成推理分析和优化方案设计。（cc-glm5.1）

**关键差异**：practices 用"我/小 G"建个人权威感（经验分享），cases 用"笔者/省略"建客观记录感（实战报告）。

### 3.3 误区破题范式（practices 系列签名手法，4/4 篇）

**普遍现象（practices 全部 4 篇）**：先立一个常见误区，再一句反转。

实例 1（spec-coding）：
> AI 当然能写，而且看起来还挺像那么回事。但问题也在这里：你没告诉它用户系统到底长什么样，它就只能自己猜。

实例 2（claude-md-best-practices）：
> 很多人跑完 `/init`，看到 Claude 生成了一份 `CLAUDE.md`，觉得"有总比没有好"，于是基本没改就提交了……这份文件有没有错？其实没有。问题在于，它对 Claude 几乎没什么约束力。

实例 3（the-cool-tricks-for-vibe-coding）：
> "代码要优雅、可维护、符合最佳实践"这种话，放在 Prompt 里看着很认真，实际约束力很弱。

实例 4（claudecode-tips）：
> 规则不是写给模型看的，是 Claude Code 自己执行的。也就是说，就算 prompt 里写了"请一定不要读 `.env`"，那仍然只是建议；deny 规则才是真正的拦截。

**句式模板**："很多人/一开始/看起来……（误区）→ 其实/但问题是/反过来（反转）→ 真正的问题是（正解）"。这是实战系列区别于概念系列的核心语言 DNA。

---

## 4. 格式元素

### 4.1 代码块密度

**普遍现象（7 篇全有，且密度远高于概念系列）**：

- cases 系列：代码块以 **AI 对话提示词 + 实战代码 + 配置文件** 为主。cc-glm5.1 有 10+ 个代码块（含 bash 指令、Java 代码、SQL DDL、JSON 配置）。deepseek-v4-claude-code 有 8+ 个代码块（settings.json、XML 依赖、bash 命令）。
- practices 系列：代码块以 **示例 Spec / 命令清单 / 模板** 为主。spec-coding 有 15+ 个代码块（requirements.md 示例、design.md 示例、tasks.md 示例、三种 Spec 模板）。claude-md-best-practices 有 8+ 个代码块（CLAUDE.md 示例、settings.json、rules 文件）。

**关键规律**：实战系列几乎每个论点都用代码块落地——"我说规则 → 我贴示例代码 → 我贴运行命令"。这与概念系列"我说概念 → 我贴比喻"形成对比。

### 4.2 截图密度（实战系列主力，区别于概念系列的本质特征）

**普遍现象（7 篇全有，密度极高）**：

| 篇目 | 截图数（粗计） | 截图用途 |
|------|----------------|----------|
| cc-glm5.1 | 13+ | 配置步骤 + AI 输出效果 + 优化前后对比 |
| claude-desktop-cc-switch | 12+（含 drawio svg） | 配置步骤 + 架构图 + 流程图 |
| deepseek-v4-claude-code | 15+ | 配置步骤 + 实战效果 + Benchmark 图表 |
| claude-md-best-practices | 8+ | 官方文档截图 + 规则文件关系图 + 维护流程图 |
| spec-coding | 5+（含读者催更截图） | 读者催更 + 四步流水线 + 三色标签 + 多代理流水线 |
| the-cool-tricks-for-vibe-coding | 8+ | 读者评论截图 + 官方文档截图 + 多 Agent 并行截图 |
| claudecode-tips | 8+ | 官方文档截图 + Sub-Agent 图 + Hook 流程图 |

**截图用法分类**：
1. **配置步骤截图**（cases 主力）：每一步配置都配截图，类似教程。cc-glm5.1 的"点击加号添加模型 → 选择模型 → 配置参数 → JSON 配置"四连截图。
2. **AI 输出效果截图**（cases 主力）：证明 AI 真的做到了。cc-glm5.1 的"AI 自主完成技术方案规划"、"AI 完成编码后输出的交付清单"。
3. **读者互动截图**（practices 主力，签名手法）：spec-coding 的"读者催更"、the-cool-tricks 的"读者评论"、claudecode-tips 隐含的"6w+ 阅读量"。**建立社交证明。**
4. **官方文档截图**（practices 主力）：claude-md-best-practices 多次贴 Claude Code 官方文档截图，建立权威性。
5. **优化前后对比截图**（cases 主力）：cc-glm5.1 的"18 秒 → 300ms"对比。

### 4.3 表格用法

**普遍现象（7 篇全有）**：

- cases 系列：**数据对比表**（参数/定价/能力维度）。
- practices 系列：**概念辨析表**（X vs Y vs Z）。claude-md-best-practices 的"CLAUDE.md vs AGENTS.md / vs .claude/rules/ / vs SPEC.md"三连对比表是标本。

### 4.4 Mermaid / drawio 用法

- **Mermaid：7 篇中未出现原生 Mermaid 代码块**。
- **drawio / svg 图片**：claude-desktop-cc-switch 用了 5+ 张 `.drawio.svg` 图片（架构图、流程图、状态机）。**实战系列倾向用图片而非 Mermaid 代码块。**

### 4.5 命令清单 / 工作流清单格式

**普遍现象（practices 主力，cases 偶用）**：

claudecode-tips 的"常用命令"是标本：
> 第一类是会直接干活的：
> - `/simplify`：当前版本里会用 4 个并行 Agent 审查当前改动……
> - `/batch`：把一个大需求自动拆成多个工作单元……

spec-coding 的"四步落地"表 + "三色标签"列表 + "踩过的坑"清单，是同一种"清单化输出"手法的不同变体。

---

## 5. 比喻范式

### 5.1 比喻密度

**关键发现**：实战系列比喻密度**显著低于**概念系列。实战系列重实操、重截图、重代码，比喻只在关键概念处偶用。

- cases 系列：比喻极少。cc-glm5.1 几乎无比喻（全篇是操作记录）。claude-desktop-cc-switch 偶有比喻。deepseek-v4-claude-code 偶有。
- practices 系列：比喻集中在"概念祛魅"段落，正文段落几乎无比喻。

### 5.2 比喻类型与实例

**类型 A：职场/身份类比（practices 偏好）**

实例（the-cool-tricks-for-vibe-coding）：
> 这就像请了一个资深架构师，结果天天让他改字段名、补 getter、调 CSS，钱花了，价值没用出来。

**类型 B：生活场景类比（偶现）**

实例（claudecode-tips）：
> 我一开始其实挺抵触命令行。毕竟习惯了 Cursor、IDEA 这种编辑器模式之后，再回到终端里和 AI 协作，总感觉有点原始人，反直觉。

实例（the-cool-tricks-for-vibe-coding）：
> 那种感觉就像小时候刚接触游戏一样，但比游戏还爽一些。

**类型 C：企业软件类比（claude-desktop-cc-switch 偏技术化）**

实例（claude-desktop-cc-switch）：
> 可以类比企业软件里的 SSO 或托管配置：应用启动时先读取本地托管配置，有可用配置就按配置连接第三方推理服务，没有才回到官方登录流程。

**类型 D：物理动作类比（偶现）**

实例（claude-md-best-practices）：
> 你可以把它理解成：在 Claude 开始干活之前，先坐在旁边提醒它几句。

### 5.3 与概念系列差异

概念系列比喻密度高、类型丰富（用比喻讲概念）；实战系列比喻稀疏、偏功能类比（用比喻破误区），且比喻多出现在开头"概念祛魅"段，正文实操段几乎不用比喻（用截图和代码代替）。

---

## 6. ai-coding 实战系列独有特征

区别于 docs/ai 概念系列的本质特征，提炼如下 8 条。

### 6.1 场景驱动闭环（cases 签名）

cases 系列每篇都是"提出场景 → 配置环境 → 跑 AI → 看效果 → 总结"。cc-glm5.1 的"场景一从零搭建 Agent + 场景二慢查询治理"是标本：**每个场景都有可量化的验收结果**（如"性能提升超过 60 倍"）。概念系列不会有这种端到端场景闭环。

### 6.2 截图密集 + 读者互动截图（实战系列主力）

7 篇平均 10+ 张截图。**practices 系列独有"读者评论/催更截图"作为社交证明**（spec-coding 的读者催更、the-cool-tricks 的读者评论、claudecode-tips 暗示 6w+ 阅读量）。这是概念系列完全没有的。

### 6.3 误区破题 + 反转句式（practices 签名）

practices 4 篇全部用"很多人觉得 X……其实/但问题是 Y"句式破题。**这是实战系列区别于概念系列的核心语言 DNA**——概念系列正面讲原理，实战系列反面破误区。

### 6.4 按风险/规模分层（实战系列签名）

practices 系列几乎每篇都有"分层"结构：spec-coding 的"10 个模块以内 / 10-30 个 / 30 个以上"按规模分层；the-cool-tricks 的"贵模型 vs 便宜模型"分工；claude-md-best-practices 的"CLAUDE.md vs rules vs Skills vs Hook"按约束硬度分层。**概念系列讲"是什么"，实战系列讲"什么场景用哪一层"。**

### 6.5 命令清单 / 模板清单（实战系列签名）

practices 系列每篇结尾附近都有可复制的命令清单或模板清单。claudecode-tips 的"常用命令"三类清单、spec-coding 的"三套 Spec 模板"、claude-md-best-practices 的"好的 CLAUDE.md 示例"都是此类。**这是概念系列没有的——概念系列不提供可直接复制的工程模板。**

### 6.6 失败模式 / 踩坑清单（实战系列签名）

practices 系列几乎每篇都有"踩过的坑"或"常见失败模式"段落。claudecode-tips 的"常见失败模式表"是标本（含"症状 + 更稳的处理方式"两列）。spec-coding 的"踩过的坑"、claude-md-best-practices 的"常见踩坑"同理。**这是实战系列的"风险预警"签名。**

### 6.7 打招呼开场 + 自称分化（实战系列签名）

5/7 篇用"你好/大家好，我是小 G/Guide"开场，且 cases 偏正式（"Guide"），practices 统一"小 G"。**概念系列无此签名（概念系列多直入主题）。**

### 6.8 第一人称经验权威（practices 签名）

practices 系列每篇都建立"我/小 G 在真实项目里踩过"的经验权威。spec-coding 的"老实说，多代理这块我自己也还在摸索"、claudecode-tips 的"我一般会把规则分成两类"——**用第一人称的"我"建立可信度，而非概念系列的"我们/大家"。**

### 6.9 cases 子系列 vs practices 子系列内部差异

| 维度 | cases | practices |
|------|-------|-----------|
| 自称 | "Guide" / "笔者" | "我" / "小 G" |
| 钩子 | 场景导航 | 读者反馈 + 真香回忆 |
| 主力格式 | AI 对话截图 + 优化前后对比 | 命令清单 + 模板清单 |
| 表格类型 | 数据对比（参数/定价） | 概念辨析（X vs Y） |
| 第一人称密度 | 中（"笔者"） | 高（"我"） |
| 比喻密度 | 极低 | 偏低（集中在破题段） |
| 结尾 | "写在最后" + 参考资料 | "总结" + 回扣核心理念（无参考资料） |
| 时态 | 操作记录体（已完成） | 经验分享体（持续性） |
| 失败模式段 | 在"实战总结"中带过 | 独立段落"踩过的坑" |
| 字数 | 偏长（cc-glm5.1 约 5000 字） | 偏长（spec-coding 约 6000 字） |

**核心区别**：cases 是"我做了 X，结果 Y"的**实战报告**；practices 是"我建议你这样做 X"的**经验手册**。两者共同点：都用截图和代码块建立可信度，都有误区破题，都按风险/规模分层。
