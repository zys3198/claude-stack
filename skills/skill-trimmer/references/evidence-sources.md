# 证据来源与数据驱动判定（原 SKILL.md「数据驱动」+「来源与核验」两节）

> 下沉自 SKILL.md（2026-09-08 渐进披露改造，内容原样下沉）。判定流程与十一档在入口 SKILL.md；本文件是使用信号来源与依据核验。

## 数据驱动：现状与轻量替代【框架】

主流框架用「遥测计数 + 溯源标签 + A/B 评测」做留删决策（Curator 机制：active → stale → archived；skill-up 工具做因果对照）。**本机现状没有遥测基建，不假装有。** 用轻量信号近似，证据链列全：

- **轻量信号**（替代遥测计数器）：
  - 文件 mtime / git 历史：半年未动 + 零引用 + D 类 → stale 候选（对应 Curator 的 stale→archived）。**已自动化（2026-08-17）**：scan_skills.py 每 skill 输出 `last_modified`（SKILL.md mtime）+ `usage_count`（读 metrics/skill-usage.log，由记账 hook 产生；**pi 侧记账 hook 未移植，pi 候选位 `~/.pi/agent/metrics/skill-usage.log` 缺失时 usage 归零**）+ `staleCandidate`（0 使用 + >180 天未改，STALE_DAYS=180），保鲜判据从人工回忆变数据驱动；插件 skill 不在 `~/.pi/agent/skills` 下不纳入本扫描。
  - 引用方活跃度：被 router 引用且 router 在迭代 → active；只有 memory 里历史提过 → 偏 stale。
  - `installing/` 台账日期：装后从未用过、台账无后续 → 可疑。
  - 用户实测：同任务「开/关该 skill」各跑一次对比 = 穷人版 A/B，不搭评测集。
  - **总量健康度（新增【文章】）**：库总量 vs 维护基线 <20——远超且大量零使用 = 书签心态信号，push 整体收敛，别因单个看似合理就放行。
  - **三维上下文成本（新增【工具】）**：`currentStartupTokens`（当前可发现入口启动成本）/ `shellStartupTokens`（触发空壳入口成本）/ `postCallTokens`（命中后完整内容成本）。`startup_delta = currentStartupTokens - shellStartupTokens`：正数写「入口缩短」、负数写「入口反增」、0 写「仅治理收益」。触发空壳只有当 `shellStartupTokens < currentStartupTokens` 才真的省启动 token，不把倒挂显示成节省。本机无遥测时三值标 `不可用`，不硬填 0（对应「描述列表预算 ~2%」的定量化）。
**本机自动化三件套（2026-08-17，使用信号的实际来源，命令在此）**：
- 记账（全自动）：**pi 侧未移植**（CC 时代 settings.json PostToolUse → `hooks/skill_ledger.py` → `~/.claude/metrics/skill-usage.log`）。pi 侧录音缺失 → usage_count 归零，stale 判据退化为纯 mtime；pi 候选位 `~/.pi/agent/metrics/skill-usage.log`，待记账 hook 到 pi 后自动生效。
- 保鲜（想审计时跑）：`python ~/.pi/agent/skills/skill-trimmer/scripts/scan_skills.py` → 扫两区（agent/skills 自建 + agent/skills-sync 第三方）→ inventory.json 每 skill 带 `usage_count`/`last_modified`/`staleCandidate`，stale 候选直接列在 stdout；去留拍板仍走本 skill 判定流程。
- 复盘（周惯例）：**pi 侧未移植**（CC 时代 `~/.claude/hooks/scripts/transcript_sweep.py` → transcript-weekly）。pi 下暂无对应产物，读高频主题补缺口暂靠人工回顾。
- **演进方向（当前不建）**：`github.com/alibaba/skill-up`（已验证存在的官方评测工具）做正式 A/B 需评测数据集，成本高；哪天想上再建。
- **状态映射**：active（在用/有引用）→ stale（mtime 久 + 零引用）→ archived（移入 `_weak-model-backup/`）。审计报告里给每个候选标当前状态。

---

## 来源与核验（2026-08-13）

【工具】层 = skill-slimming（LearnPrompt/carl-skills，2026-08-14 吸收）：复用其工具资产——`scripts/review_server.py`（1069 行，loopback 复审服务，仅绑 127.0.0.1、随机 token、无 subprocess/shell/网络、只写自己的状态目录、不读密钥；安全面 Gen Safe / Socket 0 alerts）+ `assets/review.html`（复审页）+ `references/audit-contract.md`（inventory 证据契约）+ 触发空壳合同 + 三维 token 模型 + 测量标签纪律。判定基准不吸收——slimming 的四层判据浅（只用使用频率分 global/project/trigger），替代不了本 skill 的十一档判定脑。品牌已归并（skill-slimming → skill-trimmer，状态目录 pi 侧 `~/.pi/agent/skill-trimmer/`）。

【文章】层 = JavaGuide 两篇：《再见 Superpowers！很多 Skill 真的可以扔掉了》(2026-07-23，本 skill 原始基准) + 《Skill 的选择与精简》(2026-08-13，javaguide.cn/ai-coding/practices/skill-selection-and-pruning.html，同作者同立场演进版——补充装前四问、先不装裸跑、维护量 <20、描述列表预算 ~2%/8000 字符、规则分流框架、装前必看 SKILL.md 安全面)。两篇一致处按原判据；后篇新增判据已并入核心立场 #5-7、流程 1.5、十一档「移入 CLAUDE.md/规则文件」。

【框架】层来自主流 Agent Skill 去留框架（用户 2026-08-13 提供调研稿）。关键引用已核验：

- **skill-up**：真实存在——`github.com/alibaba/skill-up`（Go 写的 Agent Skill 评测/演进工具）。
- **SLIM**：真实存在——arXiv《Dynamic Skill Lifecycle Management for Agentic RL》（Junhao Shen 等，机构未核）；「贡献变小→退役、失败场景→新建」机制与调研稿一致。
- **SkillLens / SkillOpt**：darwin-skill 已集成引用（arXiv 2605.23899 / 2605.23904，MS Research 系）；2605.23899 实题《From Raw Experience to Skill Consumption》，覆盖 skill 生命周期三阶段效用评测。
- **佐证论文**：Agent Skill Security 威胁模型、SkillWiki 治理基础设施、SKILL.md 语义供应链攻击（均在 arXiv 可查）。
- **Curator 遥测机制**：通用概念（多框架采用），无单一权威来源，本 skill 只取「轻量信号近似」做法。

【实践】层 = 腾讯技术工程《10万+ Skill 背后：腾讯SkillHub如何帮用户找到真正好用的那20%》(2026-08-10，赵秀雯，mp.weixin.qq.com/s/rSVXMwOMLSEhl7gC5KdBCg)。不整篇搬立场，只取与 skill 留删判定最相关的单点：**反馈滞后 → 静态评测不够、要试运行验证**。SkillHub 的 TRACE 五维（Trust/Reliability/Adaptability/Convention/Effectiveness）与三层次证据（静态结构 → 云端隔离运行 → 效果案例）里，「云端试运行」是本 skill 原判据缺失的一环；其余理念（二八法则 → 维护量基线 <20、受控标签 → 十一档固定体系、Trust 前置 → 工程体检安全面）本 skill 已覆盖，不重复加。核验：文章为真实平台复盘自述，SkillHub 数据（10 万+ Skill、月下载千万）未独立核实，本 skill 只取方法论不取数据。
