# 维护说明

本文件是 `ai-coding-guide` 的维护者参考。主文件触发时不加载本文件；仅当需要更新指南（新插件/skill 装入、生态重命名、用户反馈重叠触发）时 Read。

主文件路径：`SKILL.md`（同目录）

---

## 进化机制（自我维护）

本指南是 living doc，随插件/skill 增删持续更新。触发即改，不拖延。

### 何时更新

| 触发信号 | 动作 |
|---------|------|
| 用户 `/plugin install` 或 `/plugin marketplace add` 新插件 | 新增"#### 生态名（作者）"小节，填哲学/命令/亮点/取舍四件套 |
| 用户手动 clone 新 skill 到 `~/.codex/skills/ 或 ~/.agents/skills/` | 同上，或归入已有生态（若属 SP 子集） |
| skill 列表（系统 reminder）出现新前缀（如 `xxx:`） | 识别为新插件命名空间，加生态小节 |
| 某生态命令/skill 重命名或删除 | 全文 grep 旧名，替换或移除 |
| 用户反馈"X 和 Y 重复触发" | 在"重叠区处理"表加行，定优先级 |
| 两次以上同模式困惑 | 升级"反模式与失败处理"表 |
| 发现引用的命令/skill 名过时或不存在 | grep/查系统 reminder 核实，改并记 CHANGELOG |
| 用户质疑某推荐准确性 | 不辩解，贴证据或改措辞为"经验判断/推理"，记 CHANGELOG |

### 怎么更新（5 步）

1. **扫现状**：读系统 reminder 的 skill 列表，或 `ls ~/.codex/skills/ 或 ~/.agents/skills/` + `ls ~/.codex/plugins/`，比对本指南已列生态。
2. **定位差异**：新增 / 删除 / 重命名 / 版本升级。
3. **改四件套**：新生态 → 加"哲学 + 命令 + 亮点 + 取舍"四段；已有生态 → 增量改对应行。
4. **更新决策表**：在"决策速查"和"选型速判"表里加该生态的推荐场景行。
5. **记 CHANGELOG**：在本文件下方"变更记录"追加一行（日期 + 动作 + 原因）。

### 维护纪律

- **不删历史**：旧生态停用也保留小节，标注"已停用 + 日期"，方便回溯。
- **不堆砌**：每生态小节 ≤ 20 行，超了拆 references/ 子文件。
- **交叉验证**：引用命令前 grep 确认仍存在（skill 名可能改）。
- **触发即改**：用户说"装了 X"或"X 不能用了"当场更新，不等下次。

---

## 变更记录

| 日期 | 动作 | 原因 |
|------|------|------|
| 2026-06-30 | 吸收 2026 工作流长文，重写默认推荐重心。主文件：新增"分层原则"（grill-me/SP/Trellis 三层）；开发新功能改先判 grill-me/SP/ponytail；有需求文档区分 SP 计划层 vs Trellis 执行治理；反操作清单加"SP 太重先降 grill-me"与 dangerously-skip-permissions 风险边界 | 核心观点：Superpowers 方法论对但默认包装太重；grill-me 更适合前期轻量澄清 |
| 2026-06-30 | ecosystems.md 同步：grill-me 轻量澄清定位、Trellis 小节、流程对比改"澄清层/设计层/执行层"、重叠区拆"计划"+"执行治理"两行、冗余处理原则纳入 grill-me/Trellis | 让参考文档承接而非另起路由 |
| 2026-06-30 | 四路并行审校后修复残留：选型速判"日常开发功能=SP"改三层分流（P0）；反模式绝对 HARD-GATE 收窄到"需求未成文"分支；有需求文档 Trellis 加"未装回落"；环境表去"实测"过满口气；Trellis 小节去"核心价值"断言 | 主代理自审不可信，派 4 独立 agent 对抗式核查抓出残留 SP-first 路由 |
| 2026-06-13 | 主文件新增「定位与质量标准」H2 节（H1 后、决策流程前）：声明本 skill 触发后为整条 AI 编码工作流默认参考；立「准确/AI 可读/可进化」三质量底线 + 证据门槛；何时更新表加 2 行（命令名过时核实、用户质疑推荐改措辞） | 用户要求加一条：触发后整条工作流借鉴本 skill，故质量/准确性/AI 可读性/可进化性必须显式定标准 |
| 2026-06-13 | 主文件减负：进化机制+变更记录移至本文件（references/MAINTENANCE.md）；删 Step3 Mermaid 流程图改文字；description 收窄删过宽触发词（"不知道怎么做/用什么、没思路、求建议、迷茫"） | 主文件每次触发加载维护内容污染推理上下文（省 ~40 行）；Mermaid 给人看非 LLM，删之省 token；过宽触发词致普通编码问题误触发路由 skill |
| 2026-06-12 | 决策速查表加 qiaomu-ai-prd（一行想法→AI 可执行 PRD）一行；反模式表加 PRD 三件套（qiaomu-ai-prd / /plan-prd / /prp-prd）重叠优先级行 | 本会话装 qiaomu-ai-prd 第三方 skill（skills.sh 市场），非新生态故不单列小节，仅入决策表 + 重叠处理 |
| 2026-06-12 | 分类优先规则加"对比型二次分流"（带任务信号→任务分类给 A vs B 对比，纯抽象→了解指南）；Step1 加"多生态同时触发检测"挂接反模式表；反操作清单标题去 dim9 meta 标签 | 原规则把带任务的对比型咨询误推了解指南；多触发场景的反模式表未被决策流引用，需显式挂接 |
| 2026-06-11 | 内容审查修正：understand 9→8 skill（事实错）；SP 作者改"Jesse Vincent (obra)"（核 marketplace.json，删未经证"Prime Radiant"）；ECC/SP 数字加"≈"；"anthropic 官方"改"官方市场插件（含第三方）"（context7/playwright 非官方）；加推荐推理型声明 + MCP 降级表 | understand skill 数订正；SP 作者核实；措辞严谨化（规模加≈、官方→市场插件）；补推荐推理声明 |
| 2026-06-11 | 渐进式披露拆分：7 生态详情 + 流程对比 + 重叠区表迁至 `references/ecosystems.md`，主文件留生态速查表 + pointer | 详情按需 Read，控制主文件体量 |
| 2026-06-11 | 新增 understand-anything / headroom / anthropic 官方基础设施 三生态小节 | 扫本地 plugins 发现代码库知识图谱、上下文压缩 MCP、官方 MCP 基础设施三块 ai-coding 能力未纳入指南 |
| 2026-06-11 | 新增 mattpocock/skills 第四生态小节（28 skill 全装，5 类别，独有 teach/zoom-out/writing-*/grill-*/caveman） | 用户核对本地已装 mattpocock skill 集，确认生态完整，单列小节便于决策速查 |
| 2026-06-11 | 从 `ecc-superpowers-guide` 更名为 `ai-coding-guide`，新增 agent-skills 第三生态，加本进化机制节 | 用户安装 addyosmani/agent-skills 插件，指南从双生态扩展为多生态 living doc |
| 2026-06-14 | 生态速查表加「代表命令」列（点 SP:*/agent-skills:*/ecc:* 等 slash 直调入口）；新增「harness 配置类」「全量查询类」两行；决策速查补 2 行（改设置→update-config、全量查→/ecc-guide+/help） | 用户问"包含所有 aicoding 相关 skill 和命令吗"，反馈指南只点 skill 漏命令族（SP/agent-skills slash 命令与 skill 同名平行存在但完全隐形）；写作/研究类 skill 按定位（编码工作流路由器）不纳入 |
| 2026-06-22 | 大版本更新——五个仓库重装 + 三文件全面修正。安装：ECC（codex plugin marketplace add，271 skill）、agent-skills（skill-installer，24 skill）、karpathy（1 skill）、understand-anything（install.ps1 codex，8 skill junction）、headroom（pip install headroom-ai v0.23.0 + MCP 已配）。新增生态：codex-security（8 skill）、build-web-apps（6 skill）、openai-developers（5 skill）三个 Codex marketplace 插件小节。重叠区处理表重写（9 域，每域标明主力 vs 冗余）。SKILL.md 加环境自检机制（触发即扫 skill 列表，缺失生态跳过推荐）。平台残留修正：CLAUDE.md→AGENTS.md、~/.claude/→~/.codex/、删 harness 配置类（Claude Code 独有）、ECC 数字 261→271、作者修正（headroomlabs-ai/Egonex-AI）。MCP 降级表删 context7（Claude Code 特有） | 用户质疑指南组合是否合理+是否最优；完整扫描发现 5 个推荐生态在 Codex 不存在（Claude Code 迁移残留）；重装后冗余严重（每域 3-5 套实现），需显式标明分工策略 |
| 2026-06-23 | ECC 状态从 ⚠️（完全不可用）改为 🔶（部分可用）：64 个框架专属 skill 从 marketplace root（`~/.codex/.tmp/marketplaces/ecc/skills`）本地拷到 `~/.codex/skills/`。覆盖全栈：Java/Spring(5)、Python/Django/FastAPI(8)、前端 JS(11)、Rust/Go/C++(6)、Kotlin/Android(7)、Swift/iOS(5)、Flutter/Dart(2)、.NET(3)、Laravel/Quarkus/Perl/Tinystruct(12)、数据库(5)。通用流程类（plan/blueprint/tdd-workflow/santa-loop/verification-loop/orch-*/loop-* 等 ~55 个）及所有斜杠命令仍不可用（上游 bug openai/codex#26037），走 SP/codex-security 替代。三文件同步：SKILL.md 自检表/速查表/决策速查/选型速判 ECC 行改 🔶；ecosystems.md ECC 小节加加载状态声明、重叠区表替代声明改 🔶。验证：64/64 SKILL.md 完整、frontmatter name 零不匹配 | ECC 全标 ⚠️ 太保守——框架专属类是 ECC 真正独有价值，与 SP 不重复，本地拷后即可用；通用流程类才与 SP 重复，排除合理 |
| 2026-06-23 | 审查后修复（P0→P3，22 处替换 + ecosystems.md 5 处）。P0 决策树死路径：4 个分类（有需求文档/审查代码/快速改动/构建错误）A 选项从 ecc:* 改为活路径（SP writing-plans / requesting-code-review / ponytail / 框架专属 verification）；决策速查表 6 行死命令修正（ecc:plan/santa-loop/verification-loop/build-resolver/pr/plan-prd）。P0 状态标记矛盾：反操作清单 ECC 行精确化（消 🔶/⚠️/✅ 三信号矛盾，统一为通用流程不可用/框架专属可用）；ecosystems.md 5 处同步。P1 自检机制：加 reminder 不完整警告（实测 SP 磁盘14但reminder只暴露13）；权威认领弱化（路由器不认领整条工作流权威）。P3 description 收窄（删「这场景怎么办」「推荐个方案」过宽触发词）。 | darwin-skill 审查发现：决策树推荐死路径（最严重路由失效）+ 状态自相矛盾 + 自检根基不可靠 |
| 2026-06-23 | 体检修正（四维审查）。ECC 状态 ✅→⚠️：实测 plugin cache skills/ 未加载到会话（上游 bug openai/codex#26037），所有 ecc:* 引用当前为死路径，加"⚠️生态直接走 fallback"全局规则 + 选型速判表无ECC替代主力 + 决策速查表上方声明 + 反操作清单行强化。ECC 数字修正：271→249（plugin.json 自报）/ 271 目录（marketplace root）双标。SP 数字修正：≈13→14。补遗漏生态：karpathy/ponytail/claude-api/last30days 进自检表+速查表，ecosystems.md 加 ponytail（lazy senior dev mode，与 SP 设计先行冲突裁决）+ claude-api 小节。context7 降级行恢复（之前误删，理由"Claude Code 特有"事实错误——context7 是 Upstash 跨平台 MCP，config.toml 已配）。重叠区表标题"6 生态"→"9+ 生态"，加无ECC替代声明 | 四维体检（环境真实性/覆盖冗余/决策路径/平台时效）发现 ECC 标 ✅ 但实际不可加载（最严重路由失效）、遗漏 ponytail 等 3 个已装生态、context7 内部矛盾、数字过时 |
| 2026-06-23 | ECC 机制根本修正（磁盘实测推翻 bug #26037 归因）。发现历史版本把 ECC **commands 误当 skill**：`/plan` `/code-review` `/pr` `/santa-loop` `/loop-start` 等在 `marketplaces/ecc/commands/`（92 个 .md），从未在 skills/ 目录，却被标为"通用流程 skill 不可用"。实测：① plugin.json 的 `"skills":"../../skills/"` 路径断裂（指向 cache 中不存在目录），故 271 skill 无法自动加载，仅 63 个手动拷可用；② plugin.json **无 commands 字段**（全插件仅 ponytail 声明了），故 92 commands 不加载；③ 67 agents 同理；④ `blueprint`/`tdd-workflow`/`verification-loop`/`intent-driven-development` 是真 skill 但未拷贝。归因从"上游 bug #26037"（无法在线核实）改为"plugin.json 结构断裂"（磁盘可证）。三文件修正：新增 `references/ecc-structure.md` 证据文档（含可复现验证命令）；SKILL.md 自检表/生态速查/决策速查表/反操作清单/审查深度原则/Step 2 决策流共 ~25 处；ecosystems.md ECC 小节+重叠区表~10 处；删旧脚注（与新脚注重复）。 | 用户质疑"内容不一定正确，要有铁证"。磁盘扫证后发现 commands/skill 混淆是历代修正的根因——每次"修死路径"都在错误前提下打补丁，ECC 状态才会在一天内摇摆三次（⚠️→🔶→22处修） |
| 2026-06-23 | **彻底移除 ECC**（用户决定 Codex 侧不用 ECC，仅 Claude Code 副本保留）。四文件清理：SKILL.md 删自检表/生态速查/决策速查/反操作清单/选型速判全部 ECC 行（ECC 残留 0），构建错误分类 A 选项去 ECC 化（改 build-web-apps + 构建纪律）；ecosystems.md 删 ECC 小节、流程对比表从 SP vs ECC 双栏改 SP 单栏、重叠区表删 ECC 列；删 `references/ecc-structure.md` 整文件；audit.ps1 删 ECC 扫描段。附带修复：codex-security 数字 8→10（补 track-findings/triage-finding）；audit.ps1 `Get-PluginMeta` SkillsDir 上溯 version 目录 bug（原全报 0，现正确报 superpowers=14 等）。ECC「63 可用」虚报根因确认：实际 overlap 仅 29，且声称的 Kotlin/Swift/Flutter/.NET/C++ 框架 skill 全未拷。 | 审查发现 ECC 是 P0 问题高发区（29 vs 63 虚报 + 死路径），用户不维护 Codex 侧 ECC → 删除比保留更省维护成本。两副本（.agents 与 .claude）独立非共享，删 Codex 副本零影响 Claude Code 使用 |
| 2026-06-23 | 子代理独立审查后修复三处自审盲区。① agent-skills 死斜杠命令（P0，与 ECC 死路径同构）：8 个 `/build` `/spec` `/plan` `/review` `/ship` `/test` `/code-simplify` `/webperf` 全是死引用（Codex 侧经 skill-installer 装为独立 skill，commands 从未安装），改为 skill 长名调用（spec-driven-development / planning-and-task-breakdown / code-review-and-quality / test-driven-development / shipping-and-launch / code-simplification / performance-optimization）；删 `agent-skills:` namespace 错误声明。② 命名漂移：SKILL.md 4 处引用"多生态流程对比"与 ecosystems.md 真实标题"多生态核心流程对比"不一致，改标题去"核心"对齐。③ SKILL.md:310 一个 0x08 退格控制字符把 build-web-apps 吃成 uild-web-apps，删除。 | 用户不信主代理自审结论，派两个独立 explorer 子代理并行核查。两个代理各自抓出主代理漏掉的问题，其中 agent-skills 死命令是独立 P0（非 ECC 残留，是任务开始就带的盲区）。教训：主代理自审不可信，需独立代理对抗式核查 |
