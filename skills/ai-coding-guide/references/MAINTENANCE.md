# 维护说明

本文件只在更新 `ai-coding-guide` 时使用。主文件负责运行时路由；本文件只负责维护规则、证据源和变更记录。

主文件路径：`SKILL.md`

---

## 何时必须更新

| 触发信号 | 必做动作 |
|---|---|
| 新装或卸载 Claude Code skill / 插件 | 复核 `SKILL.md` 推荐路径、`references/ecosystems.md` 生态说明、`test-prompts.json` 样例 |
| 当前会话 system reminder 新增或删除 skill / agent / 工具名 | 先对照当前会话，再对照 `~/.claude/skills/` 与 `~/.claude/plugins/cache/` |
| 用户指出推荐过时、死引用、错归属、错默认路径 | 先查证据，再修正文案，再补 changelog |
| 路由决策改了 A/B/C 选项或 fallback | 同步 `SKILL.md`、`references/ecosystems.md`、`test-prompts.json` |
| 新增或删除“必须 / 默认 / 官方 / 已装”类断言 | 复核证据等级，并把不确定项降级或删除 |
| `scripts/audit.ps1` 新增扫描规则或调整严重级别 | 同步本文件的证据说明和巡检说明 |

## 证据源

按以下顺序取证，不跳级：

1. **本地已证实**：当前会话可用清单（`Available skills` / `Available tools` / `Available agent types`）、`~/.claude/skills/`、`~/.claude/plugins/cache/`、当前仓库文件。历史摘要、memory、prior-session 内容不算可用性证据。
2. **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
3. **经验判断**：维护者推荐、默认建议、经验排序；必须显式标成推荐，不得写成硬事实。
4. **证据不足**：影响主推荐结论时停下来问用户；不影响时标“不确定”或直接删。

## 同步文件

每次维护至少检查以下文件是否一起更新：

- `SKILL.md`
- `references/ecosystems.md`
- `references/MAINTENANCE.md`
- `test-prompts.json`
- `scripts/audit.ps1`
- `references/TEST-RESULTS.md`（维护时新增/更新 RED/GREEN 或 dry_run 记录）
- `CHANGELOG.md`（2026-07-22 新增，v1.3.0 起版本条目记此处；此前历史以下方变更记录表为准）

## 更新流程

1. 读已批准 spec：`docs/superpowers/specs/2026-07-07-ai-coding-guide-accuracy-design.md`
2. 扫当前会话可用项和本地安装项
3. 先修 P0：死 skill / 死命令 / 死路径 / 错默认路径 / 错归属
4. 再修 P1：过满措辞、把推荐写成事实、数量和边界断言不稳
5. 最后修 P2：主文件过重、信息重复、规则散落
6. 运行 `scripts/audit.ps1`，并抽查 `test-prompts.json`
7. 记录 changelog

## 维护纪律

- 主语统一为 Claude Code 当前环境
- `SKILL.md` 不塞维护历史
- `references/ecosystems.md` 不抢主文件路由职责
- `scripts/audit.ps1` 只报疑点，不替代人工判真
- 看见死引用或错归属，当场修，不拖到下次
- 分类观察期：每半年复盘 Step2 各分类实际触发次数，零触发或仅误触发的降级/删除，防分类膨胀（spec §3 禁大全）

## 变更记录

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-07-07 | 重写维护说明为 Claude Code 专用准确性维护手册 | 与 accuracy spec 对齐，去掉旧多 IDE 残留和历史包袱 |
| 2026-07-12 | 清死引用 `/goal`（SKILL.md+ecosystems.md+test-prompts）；`agent-skills` 归属改 Matt Pocock skills（SKILL.md 描述+生态表+ecosystems.md 段）；audit.ps1 加死 slash 命令 P2 巡检 | 对齐当前装机栈：`goal` skill 不存在、`loop` 同时覆盖定时与条件驱动；SDLC 补充层经 setup-matt-pocock-skills 证实为 Matt Pocock 独立 skill，非 agent-skills namespace |
| 2026-07-12 | 加 4 路由分类：理解代码（`lean-ctx`/`understand`/`gitnexus-exploring`）、完工验证（`verify`/`superpowers:verification-before-completion`）、重构/简化（`simplify`/`request-refactor-plan`）、提交/收尾（`commit-commands:*`/`superpowers:finishing-a-development-branch`）；SKILL.md 信号表+分类块+决策速查同步 | 填高频任务路由 holes（原 0 路由），11 个 skill 全部已装核实；spec §3 禁大全，仅加 universal 缺口，TDD 不开独立分类 |
| 2026-07-12 | review 后结构修正：完工验证从独立分类降为 Step2 横切收尾检查点（`verify`+`superpowers:verification-before-completion`，改动类分类通用）；决策速查新增提交+理解 2 行（删与 Step2 重复的验证/重构行，速查表仍 9 行） | 完工验证是收尾阶段非独立任务型，与「理解/重构」并列入口不自然；决策速查与 Step2 块重复违反 spec §7.2 P2 |
| 2026-07-12 | 抽验路由 skill 一手行为（读 commit-commands README+command.md、simplify SKILL.md、verify builtin desc）：`commit-push-pr` 补"一条命令自动 push+开 PR 不可逆"警告；重构 A/B/C 改 3 真选项（simplify/request-refactor-plan/improve-codebase-architecture）；审查去虚 C 降到 A/B；test-prompts 加 4 条回归（理解/重构/提交/横切验证）；MAINTENANCE 加分类观察期规则 | spec §5 实测>二手 + §11 回归覆盖；防 commit-push-pr 误推远端 + 防新分类零回归覆盖 |
| 2026-07-12 | 子代理 review 后修 15 项：P1-3 构建错误 `frontend-design`→`ecc:*-build-resolver`（事实错归属）；P1-2 完工验证补入口（Step1 信号行+横切直进说明）；P1-4 audit 加死 skill 名 P2 巡检；P1-5 test 补构建错误+文档写作；P1-6 信号重叠裁决；P1-1/7 Step4 改两段式（AskUserQuestion 上限 4）；P2-1 删 audit 假阳性 pattern；P2-2 横切补构建错误；P2-3 删选型速判；P2-4 死命令扫 MAINTENANCE 规则段；P2-5 changelog 措辞；P2-6 重构加先理解前置；P2-7 Matt Pocock 证据锚点；P2-8 test#11 顺序 | review 0 P0/7 P1/8 P2 全闭环；达 spec §12.2 验收 |
| 2026-07-20 | 加“外部 AI 编码实践 → 路由指南维护”分类、轻量迁移闸门、重机制黑名单、test prompt #15；随后补 Step0 组合顺序、降低 AskUserQuestion 强制性、修 review 实际入口、修 build slash command 优先级、删除 `git clean` fallback、按运行时表面细分 verify；test prompt 扩到 25 条负向/组合/目标校准回归；同步 ecosystems.md；补定位主次：开工路由为主，生态地图/质量闸门/学习陪跑服务路由；新增路由输出契约、风险→闸门矩阵、最小信息清单、学习陪跑模式细分；本轮审查后又修正 description 非触发句、当前可用性证据口径、高风险审查反模式旧路径、文档写作总路由、audit 死 skill 误报，并新增 `references/TEST-RESULTS.md` dry_run 记录 | 吸收腾讯技术工程 AI 需求开发文章的可迁移部分，同时修独立 reviewer 发现的 P0/P1，并对齐用户目标：不把 8 阶段流水线/project_wiki/TECH_SPEC/红线 YAML/模拟器验证塞进路由器；避免 review/verify 混淆、构建入口错归属、互补 skill 被写成互斥 A/B/C、破坏性清理默认执行；防本 skill 膨胀成工具大全、执行流水线或学习课程；让路由输出更短、更稳定、更少乱问；补齐 skill TDD 证据记录，降低审计噪音 |
| 2026-07-22 | 加「判级/暴露未知」分类（Step1 信号行 + Step2 分类块含 A/B/C 与 fallback + 决策速查 1 行），主路径指向新 skill `expose-unknowns`；test prompt #26；修 test-prompts.json 带 BOM 导致 PS5.1 ConvertFrom-Json 假报 Invalid JSON（剥 BOM 后审计 0/0/0） | 吸收 SharkChili 暴露 unknown 实践文（转述 Thariq《A Field Guide to Fable》）的可迁移部分；执行细节（判级表/启发词/反考）按迁移闸门留在 `expose-unknowns` skill 不进路由器；判级一行规则同步进全局 CLAUDE.md §1.1 |
| 2026-07-22 | v1.3.0：description 加「不用于」清单（视觉任务走 frontend-guide / 写作走 article-writing-guide / 学习走 learning-guide）+ 版本戳；新增「域边界」段显式枚举三类转介 + 反例；新增「触发门禁」3 行（域归属+存在性+非编码转介）；质量底线加「默认值先于菜单」；文末加路由表门禁 HTML 注释；test prompt #27（落地页+写码转介）、#28（吃透 transformer 转介）；新建 `CHANGELOG.md` | RED 基线实锤本 guide 抢 frontend-guide 单（登录页/落地页两场景第一跳全错）；依据链：社区实测触发率 0-20% vs forced-eval 84%、Anthropic defaults-not-menus、Superpowers #1301 反范畴词；GREEN 验证子代理读新 description 后正确判 NO。详见 `CHANGELOG.md` [v1.3.0] 与 lab-area handoff（2026-07-22-guide-skills-v130） |
| 2026-07-22 | v1.3.1：「路由指南维护」分类接线新 skill `guide-skill-auditor`（Step1 信号行 + Step2 分类块 + 决策速查）；test prompt #29 | 新 skill 落成需路由可达；TDD 证据：RED 裸审 4/9 vs GREEN 带 skill 9/9 |
