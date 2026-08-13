---
name: guide-skill-auditor
description: Use when 审查、优化、新建 router 型 guide skill（各域开工路由器，如 ai-coding-guide / article-writing-guide / learning-guide），或排查 guide 误路由、漏触发、兄弟域抢单问题。本 skill 是 router 型 guide 的质量审查器。触发词：审查 guide、优化 guide、路由 skill 体检、guide 抢单、误路由排查、新建路由器、route skill audit。不用于：非路由型执行 skill 的内容审查（走该 skill 自己的维护流程）。<!-- v1.6.1 -->
---

# Guide Skill 审查器

审查对象是 **router 型 guide skill**——靠 frontmatter description 被触发、正文含路由表把请求分发给下游 skill 的那类。执行型 skill 不在范围。

**质量底线：** 所有修复建议必须引用证据（真实误路由事故 / 官方变更 / 基线测试失败），不接受「应该会更好」式漂移。

## 审查流程

### 第 0 步：定靶

读目标 guide 的 SKILL.md 全文 + description。列出它声明的域和兄弟域。

### 第 1 步：静态十查（按顺序，逐条给 PASS/FAIL + 位置）

| # | 检查项 | 通过标准 | 依据 |
|---|---|---|---|
| 1 | **description = 角色定位(what) + 触发条件(when)，无流程摘要** | ①须含 what——一句角色定位（router 型必须声明「X 域开工路由器」这类分发角色，否则 Claude 不理解它的路由职责，会漏触发）。②须含 when——触发条件/触发词。③**无流程摘要**（步骤/阶段枚举/「先…再…最后…」）——写了流程 agent 会照 description 执行而不读正文。三者缺一即 FAIL | Anthropic 官方三处一致要 what+when 双全（best-practices / skill-creator / Claude Code 文档）；Superpowers SDO 实测「写流程摘要→agent 跳过正文」。本项取两派各自成立的半块：what 助触发（官方），无流程摘要防跳正文（SP） |
| 2 | **版本戳** | description 末尾有 `<!-- vX.Y.Z -->`（正文末门禁注释可同写，两处一致） | 四域 v1.3.0 惯例 |
| 3 | **「不用于」清单 + description 路由目标列表无范畴词** | 两处同查：①「不用于」显式枚举兄弟域转介条款，无「其他/等/任何」范畴词；②description 里枚举路由目标的列表同样无范畴词（「路由到 A/B…等」「各风格预设」类写法 = FAIL） | Superpowers #1301 范畴词被放大解释；2026-08-07 实测踩坑：learning-guide「路由到…等」、frontend-guide「各风格预设」（当日已修，learning v1.4.8 / frontend v1.5.5） |
| 4 | **触发门禁** | 正文有显式 3 行输出模板：相关性 YES/NO + 目标存在性 + fallback，位置在分类/委派动作之前（范本：`ai-coding-guide` 触发门禁段） | 社区实测无门禁触发率 0-20%，forced-eval 84% |
| 5 | **路由表无范畴词兜底行 + 撞词行内联负向边界** | 每行都是具体信号→具体路径；「其他」类兜底行必须给出具体反问模板，不是空泛「问用户」。与兄弟域共享触发词的高撞词行，须在行内内联「何时不选它/何时选兄弟域」；只靠 description 全局「不用于」兜底不算——全局清单管触发面，行内内联管正文分发时的近端防线 | #1301；ask-matt 条目级内联负向范式（「Triage is only for issues you didn't create… don't triage them」，社区一手路由器）；本地四域 tie-breaker 实践 |
| 6 | **路由目标合法性（存在性 + 可直达性 + 归属）** | ①存在性：路由表每个 skill 名核对证据链（严格降序）：ⓐ当前会话 available skills ⓑ磁盘 `~/.claude/skills/`、`~/.claude/plugins/cache/`、`~/.cc-switch/skills/`。三处都查不到 → 记 P0 幻觉。磁盘能查到但当前会话未装 → **不算幻觉**，记「待本机会话验证」。禁止仅因审查会话没装就判 FAIL。②可直达性：直达目标的 description 若自声明「不主动响应 / 被 X 引用 / 判定源」类参考层身份 → P0 误路由面（用户会被分发到一个声明不接客的 skill）；参考层只应被其他 skill 在流程内部引用，不作路由终点。③归属错位：路由目标是「每轮任务都要遵守的项目约定 / 漏一次就出事的机械约束」类 skill（该进 CLAUDE.md/AGENTS.md 或 hook/CI/linter，非 skill 职责）→ P1 归属错位，建议改路由移除该目标、把规则挪到规则文件/hook | §12 证据门槛 + 2026-07-22 reviewer 误报教训；ask-matt「vocabulary underneath」参考层分层（社区一手路由器）；javaguide-style-guide 自声明「不主动响应写作请求…终检时被 publish-final-check 引用」（本地一手实例）；JavaGuide《Skill 的选择与精简》(2026-08-13) 规则分流框架（项目约定→AGENTS.md、机械约束→hook/CI/linter、特定任务流程→Skill） |
| 7 | **默认值先于菜单 + 分支点问句化** | A/B/C 仅在「路径选择改变成本/风险/产物且无法判断」时出现；用户意图明确时直接给默认路径。菜单合理存在时，每个分支须写成用户/Claude 可立即判定的是非/二选一问句（如「这是多会话构建吗？」），且每支给具体下一步路径；开放式「你想要哪种」式空泛菜单 = FAIL | Anthropic defaults-not-menus；ask-matt 分支点问句化范式（「can you settle every question in conversation?」/「is this a multi-session build?」，社区一手路由器） |
| 8 | **路由表门禁** | 文末有 HTML 注释声明：增删路由表条目须引用真实事故或官方变更证据 | 防无证据漂移 |
| 9 | **配套文件** | 必须：`test-prompts.json`、`CHANGELOG.md`。推荐：`references/MAINTENANCE.md`（单文件 guide 可缓建）。审查器自身按同一标准执行 | 四域 v1.3.0 对齐结构 |
| 10 | **枚举信号表 + 低置信缺口清单** | router 型 guide 须有两张表：①**明确信号→路径的枚举表**——用户信号命中某条即直跳，不采访（高置信快路由）。②**不命中/多解时的缺口清单**——按决定「走哪条路」的决策点逐点问，不猜，允许用户说「直接定」（低置信才停）。两张表皆无 → 闭眼硬路由 = FAIL。**措辞红线**：本项判据是「有没有这两张可查的表」，不是让 guide 写「评估置信度」——prompt 里无可判定的 confidence 变量，写「置信度闸门」会诱导 Claude 装自信而永不追问。范本：`ai-coding-guide` Step 1 信号→分类表（枚举）+ Step 0.7 最小信息清单（缺口） | 社区置信度+风险双轴（Anthropic《Building Effective Agents》routing 直接分发、OpenAI triage 轻收集、Amazon selective-triggering）的 prompt 翻译——代码路由的 `if conf>threshold` 在 prompt 里须换成「查表命中/不命中」这一可判定动作。用户 2026-07-23 提出并拍板「置信度换成枚举表+缺口清单」 |

### 第 2 步：动态基线（静态十查查不出误路由，以下情况必跑）

触发条件（满足任一即跑，不以静态结果豁免）：

- description / 域边界条款 / 路由表有任何改动 → 必跑
- description 含兄弟域高频词（如写作 guide 含「文章」、编码 guide 含「页面」）→ 必跑撞词场景
- 仅 P2 机械补齐（版本戳、配套文件、门禁注释）→ 可跳
- description 只加负向收窄条款（「不用于」类，无正向触发词新增/改动）→ 可跳但须记理由（收窄=降低误触发，不引入新误路由面；正向触发词改动不在此豁免，仍必跑）

造 3-5 个边界场景 prompt（重点：兄弟域边界信号、模糊信号、点名下游 skill 的场景），派子代理裸跑（只给 description 不给正文）看第一跳。**子代理连挂 2 次（API/环境故障）→ 改由主会话逐场景人肉走查，并在落账时标注「人工走查替代子代理」（须同时记录挂掉的子代理名+错误原文，防被滥用成偷懒不派子代理的口子）**：

- 第一跳进错域 → **P0 误路由**，改 description + 域边界条款
- 第一跳对但下游 skill 不存在 → **P0 幻觉**，修路由表
- 降级到合理 fallback → 良性，记录即可

每个边界 bug 修复后补一条镜像 test-prompt（本 guide 和兄弟 guide 各一），格式对齐现有 `test-prompts.json` 的 id/prompt/expected/scenario。

### 第 3 步：修复分级

| 级别 | 内容 | 动作 |
|---|---|---|
| P0 | 幻觉引用、误路由、域边界缺失（含十查中任一项 FAIL 且能直接造成上述后果，如第 3 项缺「不用于」致兄弟域抢单） | 立即修，修完跑 GREEN 子代理验证 |
| P1 | 第 1/4/5/7/10 项 FAIL 但无实锤误路由；或第 3 项仅 description 路由目标列表部分 FAIL（「不用于」清单本身合规）——触发门禁缺失、兜底行空泛、强制菜单、模糊信号无意图摸查机制、目标列表范畴词等削弱项 | 本轮修 |
| P2 | 第 2/8/9 项 FAIL——版本戳、配套文件、门禁注释 | 本轮补齐，机械操作 |

### 第 4 步：落账

- 目标 guide 的 `CHANGELOG.md` 加版本条目（Added/Fixed/Rationale）
- `references/MAINTENANCE.md` 变更记录表加一行
- 未暴露缺陷的路由表区域**不动**，并在 changelog 写明「未动原因」（防无证据漂移的正面记录）

## 输出格式

```
十查结果: <PASS n/10> —— FAIL 项列表
基线测试: <跑了 N 场景 / 跳过及原因>
P0: <清单或"无">
P1/P2: <清单>
已修: <文件列表>
待用户本机验证: <子代理跑不了的部分>
```

## 反模式

| 场景 | 正确动作 | 不要做 |
|---|---|---|
| 十查全 PASS | 报告 PASS，不动文件 | 没病开药，凑改动 |
| 路由表某区没暴露缺陷 | 明确记录「未动 + 原因」 | 顺手「优化」措辞 |
| description 改完 | 补兄弟 guide 的镜像 test-prompt | 只改单边，回归断链 |
| 子代理会话缺目标 skill | 验证「不抢单」侧即可，端到端标注「待用户本机跑」 | 假装端到端已验证 |
| 用户要看的是「三域拼起来合不合理」 | 主会话直接组合审（域边界/重叠/交接/兜底/下游归属），单 guide 十查照跑 | 把组合审硬塞进单 guide 审查流程 |

## 组合审查（审三域整套，非单个）

用户问「skill 的组合/搭配是否合理」时，除逐 guide 跑十查外，加审六维（主会话即可，子代理故障降级同第 2 步）：

1. **域边界覆盖**：三域拼起来有没有两不管地带（翻译/录屏/运维等域外信号归谁——按 fallback-template D 分支收口）。
2. **边界重叠**：正向触发词重叠时 tie-breaker 是否三家一致（看交付物/目标）。
3. **跨界交接一致性 + 组合边声明**：A 说转 B、B 是否对称接 A；无死循环、无转介进虚空。另查两类组合边是否显式声明——产物边（A 的产物是 B 的输入时，A 处是否指明「下一步去 B」）；内部驱动边（B 内部驱动 C 时，用户拿到 B 的产出是否知道 C 已被覆盖、无需单独触发）。
4. **共享兜底有效性**：fallback-template 被几家引用、能否兜住「三域都不命中」。
5. **下游 skill 归属冲突**：同一下游被多域引用时是否有归属说明（如 `expose-unknowns` 判级按主域分界）。
6. **下游角色分层**：三域下游 skill 按角色分层审（开工链上 / 独立工具 / 参考层 / 维护类），guide 是否区别对待——参考层不出现在直达路由表（与十查第 6 项②呼应）；链上存在天然先后关系的，路由表是否表达顺序或显式声明单跳即终态。

## 实证来源

本检查清单从 2026-07-22 四域 v1.3.0 改造实战提炼（handoff：`C:\ZYS\Code\lab-area\exp\2026-07-22-guide-skills-v130\handoff.md`）。RED 基线证明：裸审代理能自发发现幻觉引用/自相矛盾/菜单僵化约 4/9 项，但系统漏掉 description 流程摘要、范畴词兜底行、防漂移门禁三类——本 skill 把这三类变成强制检查项。第 6 项③归属错位判据来自 JavaGuide《Skill 的选择与精简》(2026-08-13) 规则分流框架（项目约定→AGENTS.md、机械约束→hook/CI/linter、特定任务流程→Skill）。

<!-- 检查清单门禁：增删检查项前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）。v1.6.1 -->
