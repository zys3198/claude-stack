# Changelog

本文件从 2026-09-12 起记；此前无版本惯例，历史变更只追溯安装台账。

## 1.8.0 — 2026-09-21

来源：按 Matt Pocock `writing-for-agents` v1.2.3 的上下文卫生方法做一轮精简。判据三条：no-op 测试（删掉这句，agent 的行为会变吗）、信息层级（每个分支都要读的内联，只有部分分支走到的下沉 `references/`）、单一事实来源（同一规则只留一个权威位置）。

- `description` 由「执行代码改动或修复 Bug，重构或审查 AI 代码，或回退改动时使用」改为「执行代码改动、修复 Bug、重构、审查 AI 代码或回退改动时使用；不用于纯问答、文章写作或学习调研」。原描述只有正向信号，与 `article-writer-by-user`、学习调研类任务的分界由指针措辞承担。
- §1.4、§1.6、§3 三节下沉到 `references/`，入口只留节号与指针行：`references/code-review.md`（§1.4 与 §1.4.1）、`references/worktree-and-resources.md`（§1.6）、`references/agent-dispatch.md`（§3）。正文原文搬移，节号保持，入口分节编号不变。§1.6 的脚本位置说明原本出现两次，合并保留位置更靠后的完整版本。
- §1.3 删掉重复的 Plan 触发半句：§1.1 有完整版本，触发条件已在 §1.1 给全，重复的那半句是同一规则的第二份拷贝。
- §1.0 编码硬约束未动：它是全局 `CLAUDE.md` 原文搬入（见 1.7.0），禁止式措辞是硬约束的适用形式。

验证补充：`description` 改动参加 10 个 model-invoked skill 的 27 条第一跳对照，改前改后主判零不一致。CLI 2.1.278 回归时先暴露三处 case 合同问题：`bug-fix` 的 10 轮上限低于历史成功运行实际需要的 14 轮，改为 16；`research-no-route` 与 `vague-feature` 的单个字面词 grader 改为对应语义词组。三项重跑 3/3，通过项与未改 case 合并后，当前 6 个 case 各有一次通过。三份新 `references` 尚未在真实任务里验证。

## 1.7.1 — 2026-09-21

整理轮，不改变行为：删重复表述、合并同类条目，判据是逐句做 no-op 测试（删掉这句，agent 的行为会变吗）。

- 删开头「来源：CLAUDE.md 2026-07-29 瘦身迁出（§1.1-1.4 / §2 / §3 / §4 原文）」。同一条来历在 1.7.0 条目里写得比它具体，正文留版本沿革会随文件继续漂移。
- §1.3 「审查动作清单（与 §1.3 三查互补）」改为「审查输出与顺序」。原清单三条里有一条是「审查三维」第 1、2 项的复述，删掉；剩下两条是顺序要求，与原清单标题不符，标题一并改准。
- 「删错了怎么找回」由四条 bullet 压成一段：四条里三条在讲同一件事（删除工作树不碰分支和提交），合并后信息量不变。

## 1.7.0 — 2026-09-21

来源：把本机全局 `CLAUDE.md` 的内容移入本 skill，为全局文件立预算（预算规则见 `instruction-engineering-by-user` 审查基准的「全局 CLAUDE.md 的预算」）。全局 `CLAUDE.md` §2.3 早已声明「本文件只保留两条全局底线：修根因、必须复核」，而它的 §2.1 却常驻着六个编码专属小节，两处互相矛盾。本次按前者解开：编码细则归本 skill，全局只留可靠指针。

- 新增 §1.0 编码硬约束：全局 `CLAUDE.md` §2.1 的六个小节（依赖与错误处理、文件与工具、改动范围、实现复杂度、修改测试与验证、Python 代码）原文搬来，一字未改。全局 §2.1 只留「协作与响应」与「工作量与设计」——那两节管对话行为，任何任务都触发，必须常驻。
- 全局 `CLAUDE.md` §2.3 第一条由「编码任务按当前场景和用户指定流程分诊，不预设某个执行 skill」改为显式指针。原文的分诊措辞在细则外移之后会留下空档：编码任务若不触发本 skill，§1.0 的约束就丢了。触发可靠性由指针的措辞决定，所以把触发条件逐个写出来。
- 新增 §1.3.1 验收相位：清单第 24 项，材料 `my-7-phases-of-ai-development` 第 7 相位。四步：先出 QA 计划、人审计划与实现、照计划验、发现的问题回成新工单再回执行相位；第 1 到第 4 步来回多轮是正常节奏。本机此前只在 §1.3 的「只构建通过不等于通过」里管证据要求，没有独立验收相位，也没有「问题回成新工单」这一步。
- 新增 §1.5.1 深模块与接口归属：清单第 25、26 项，材料 `ways-ai-coding-has-rewired-my-brain` 第 4、5、6、9 条与 `how-to-make-codebases-ai-agents-love`。深模块的词汇与判据不重写，指向插件 `mattpocock-skills`：主线 `improve-codebase-architecture`，参照物 `codebase-design`。主线不能指错——该插件的 `docs/engineering/improve-codebase-architecture.md:76` 写明，把 `codebase-design` 单独当任务派给新 agent 是已知失败模式，它没有自己的流程，agent 会自己发明一套再空转。本机另补两条分工规则：接口归人、实现归 AI、测试负责诚实；一个模块一个目录且对外只暴露接口文件。
- §1.6 新增功能分支归并：全局 `CLAUDE.md` §8 的模块制五步分支流程原文搬来，一字未改；全局那一行改成指向本节的短指针。
- §4 与 §1.0 原本互相冲突：§4 第 3 条并列给出 `git restore` → `git revert` → `git reset --hard HEAD~N`，§1.0 禁止用 Git 回滚任何代码。用户拍板保留禁令，删掉 §4 的 git 阶梯，回退按 §1.0 用文件编辑工具恢复。§4 触发行里的 `git reset --hard` 例外句一并去掉，后面的条目顺次上移。
- skill 由 `code-change-workflow-by-user` 改名为 `coding-workflow-by-user`：正文早已从「代码改动」扩到完整编码工作流（§1.0 硬约束、§1.3.1 验收相位、§1.5.1 模块设计、§1.6 工作树与本地资源），旧名对不上内容。正文标题同步由「代码改动全流程细则」改为「编码工作流细则」。同步改了 frontmatter `name`、6 份 eval 的 prompt 与 description、`.gitignore`、`instruction-engineering-by-user`（正文 2 处与 `references/refactor-roadmap.md`）、`article-writer-by-user`、本目录 `MAINTENANCE.md`（5 处）、全局 `CLAUDE.md`（3 处）。安装台账的历史条目与已发布的旧版本 CHANGELOG 条目保留旧名不动——那是当时的事实。frontmatter `description` 未动：改它属 major，要重跑触发验证，留待单独一轮。

全局 `CLAUDE.md` 的三处改动已落地：§2.1 删掉六个编码小节（原文见本节 §1.0）、§8 功能分支归并改成指针（原文见本节 §1.6）、§2.3 第一条改为显式指针。落地后全局 232 行 / 6,932 字符，落在 `instruction-engineering-by-user` 审查基准新立的 240 行 / 7,000 字符预算内。

未验证：验收相位与深模块两节尚未在真实任务里跑过。

## 1.6.1 — 2026-09-21

来源：Matt Pocock（AI Hero）材料第二轮，`essential-ai-coding-feedback-loops-for-type-script-projects` 与 `tips-for-ai-coding-with-ralph-wiggum` 第 5、6 条。

- §1.3 新增一条「反馈回路是上限」：能自动跑的检查（类型、lint、测试、pre-commit）比叮嘱有效，因为检查不过模型会自己重试，不因反复失败而泄气，所以约束该做成检查、不写成提醒；任务切多大也由反馈速率定，反馈速率就是速度上限，任务越大反馈越稀、质量越低。
- 与既有条目的关系：§1.3 原有的「只构建通过不等于通过」管的是证据要求，本条管的是把要求做成自动检查、以及任务粒度。`parallel-delegation-by-user` 第 3 条的单跑一轮管的是上并行或进循环前的触发条件，三条不重复。

## 1.6.0 — 2026-09-21

来源：把本机全局 `CLAUDE.md` §8「并行会话」「收尾」两段的细则移入本 skill，全局只留指针。移入前按 Matt Pocock `mattpocock-skills@1.2.3` 的 `.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md` 核对了一遍依赖强度——没有这些细则，收尾会做错而不只是做得不够好，属硬依赖，因此在 §1.6 写全，全局那两段合并成一句指针。

- §1.6 开工前新增三条：**一个任务一个工作树**（会话开始时看到「另有 N 个会话在用当前目录」的卫生提示，先调用 `EnterWorktree` 迁移再动手）；**独占资源先协商**（占用端口、容器或共享数据库之前，有活跃会话在用就先协商，协商不下交用户裁决）；**写库先确认**（会写共享数据库的进程启动前，先确认目标数据库和迁移开关）。
- §1.6 收工前新增一条「自己的收尾清单」：停掉自己启动的进程，删掉本会话建的空工作树，汇报分支名、路径和未完成项；在做的工作落到自己的分支上并 push；有未提交改动的工作树不删。与既有的「子代理留下的工作树由父会话收尾」并列，两条分别管自己建的和子代理建的。
- 同步改了全局 `CLAUDE.md` §8：原「并行会话」与「收尾」两段合并为一段「并行会话与收尾」，只留核心禁令加指向 §1.6 与 `~/.claude/session-hygiene.json` 的指针。

未验证：新增的四条尚未在真实的多会话场景里跑过。

## 1.5.1 — 2026-09-21

来源：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验，第 18 项先单跑一次（材料 §6.1）。材料的要求是「先单跑一遍不能省」——放进 AFK 循环之前先手动跑一次，亲眼看 agent 怎么走、停在哪里，把要补进 prompt 的调优在这一步做完，第一次暴露的往往是脚本和配置本身的问题（参数传错、prompt 漏条件、权限少开一项），与模型能力关系不大。

- 本机已有同源规则：`parallel-delegation-by-user` 第 3 条要求批量并行（≥2 个 worker）前先派一个 worker 单跑同类任务，症状清单与材料一致。差别只在触发条件写的是并行，循环场景没覆盖。
- §3「护栏以实际挂载为准」那条的长链编排句末尾补一句：进循环或放并行之前先单跑一轮同类任务，核对路由、权限、输入契约与产物格式，细见 `parallel-delegation-by-user` 第 3 条。规则正文仍只有一处，本处只补触发条件。

未验证：本机尚未跑过 AFK 循环。

## 1.5.0 — 2026-09-21

来源：用户核对本 skill 与插件 `mattpocock-skills` 的重复度后要求删掉重复内容、改为直接引用已有 skill。四处流程骨架原先在本机各写了一份，插件里已有更完整的版本，现改为指名引用：

- §1.1 grilling 协议：删掉设计树、前沿分批、每问附推荐答案、拍板后推进这几句复述，改为指向 `mattpocock-skills:grilling`（协议本体）、`grill-with-docs`（有仓库时）与 `grill-me`（无工作目录）。保留本机三条：数十问正常、纯文本不用 AskUserQuestion、每条拍板的决定记下依据。
- §1.3 Bug 修复：删掉「先写 2-3 个失败测试重现」的回路描述，改为指向 `mattpocock-skills:tdd` 与 `mattpocock-skills:diagnosing-bugs`；保留改实现前人工确认与验收 checklist 贴结果。
- §1.4 AI 代码审查：新增引用 `mattpocock-skills:code-review`（固定点 diff、Standards 与 Spec 两轴并行子代理、Fowler 坏味道基线、报告不合并），本机三维、审查动作清单、沟通技巧、权限归属、反模式照旧保留。
- §3 Agent 调度：删掉竖切规则与「第一片穿全部层」的复述，与 decompose 那条合并为一句指向 `mattpocock-skills:to-tickets`；保留一个计划分 4-6 片、外部可观察现象的判据与打回重切、沿用宿主执行计划、Plan 审批后执行。
- §1.5 新增一句：需要产出规格文档时手动调用 `mattpocock-skills:to-spec`。

依赖：插件 `mattpocock-skills@1.2.3` 已启用；其中 `code-review`、`tdd`、`diagnosing-bugs`、`grilling` 可自动触发，`to-spec`、`to-tickets`、`grill-with-docs`、`grill-me` 标记了 `disable-model-invocation`，需要用户手打命令或由主 agent 提示用户调用。

未验证：这四处引用尚未在真实编码任务里跑过一遍。

## 1.4.1 — 2026-09-21

来源：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验，第 10 项 design concept。插件 `mattpocock-skills@1.2.3` 的 `engineering/ask-matt/SKILL.md:17` 判定：在有工作目录时 `grill-with-docs` 严格优于 `grill-me`，因为它在同一套 `/grilling` 之外还用 `domain-modeling` 留下档案。本机原来只指了无状态的 `grill-me`，经用户拍板改用前者。

- §1.1 的 grilling 协议末尾，`mattpocock-skills:grill-me` 改为 `mattpocock-skills:grill-with-docs`，并写明它边问边落的两处产物：仓库根 `CONTEXT.md` 是纯术语表、不含实现细节；`docs/adr/` 只在难以逆转、缺上下文会让人意外、经过真实取舍三条同时成立时才写。
- 同步在全局 `CLAUDE.md` §8「产物去处」补上 `docs/adr/` 与仓库根 `CONTEXT.md` 两个去处，使它们不与「仓库根不新建任何文件或目录」冲突。

未验证：本机尚未在真实项目里跑过一次 `grill-with-docs`，`CONTEXT.md` 与 `docs/adr/` 的实际落盘形态未实测。

## 1.4.0 — 2026-09-18

来源：独立子代理对 1.3.0 新增内容的逐条审查。按裁定收敛：删掉与全局 `CLAUDE.md`、DTSF 项目 `CLAUDE.md`、`toolchain-pitfalls` 重复的条目，去掉只在单个仓库成立的 Git 协作规则，修正两处与实测不符的说法。

- 删掉 `scripts/worktree-remove-guard.py` 与 `settings.json` 里的 `WorktreeRemove` 挂钩。宿主清理工作树前自己会检查未提交改动与未推送提交，钩子重复了这套判断。
- §1.6 删掉五条重复项：工作树与分支名带任务语义、建工作树前扫同级目录、共享资源独占、迁移文件不可回改、会话产物路径。删掉 Git 协作小节，两条均来自 DTSF 项目规则。
- §1.6「删错了怎么找回」按实测改写：`git add` 过的内容已进对象库，工作区文件被删仍可用 `git fsck --unreachable` 捞出；没 `git add` 的才不可逆。保活窗口由 `gc.reflogExpire` 与 `gc.reflogExpireUnreachable` 决定，`gc.pruneExpire` 在其后起算。删掉「跑清点脚本判断窗口」一句，脚本不读这三个配置。
- §1.3「页面提示不代表通过」改为「只构建通过不等于通过」，合格证据里去掉截图（全局 `CLAUDE.md` §2.1 禁止主动使用视觉功能）。
- §3「护栏靠 hooks 不靠自觉」改为「护栏以实际挂载为准」。
- `toolchain-pitfalls` 删掉「不要手写成熟文件格式的解析器」与整节「触碰边界」，新增 Windows 父进程退出不连带终止子进程一条。
- `session-inventory.py`：删掉一处死条件；docker 查询失败时返回 `None` 并在调用处提示，不再与「容器没跑」混淆。

验证：清点脚本改后在 DTSF 实跑通过，退出码 0，输出 20 个工作树、18 条 stash、11 条无远端分支、2 个独占容器运行中。

未验证：eval case `worktree-closeout` 尚未跑 runner。

## 1.3.0 — 2026-09-18

来源：grill-me 会话（设计树三轮加一轮追加）。把 DTSF 项目 `CLAUDE.md` 与记忆库里跟具体项目无关的部分复制到通用位置，并补上并行会话与工作树的收尾规则。不改变 `description`，触发边界维持原样，因此是 minor。

- §1.6 新增「工作树与本地资源」。开头列出本机可能同时处的三种做法（单会话不派子代理、单会话派多个子代理、同时开多个会话）各自的隔离方式与收尾责任人，并写明收工纪律三种完全相同。收工前新增一条：子代理结束时宿主清理工作树前会检查未提交改动与未推送提交，任一存在就把工作树留在原地，由父会话核对、提交并推送，或确认后手动删除。开工前：建工作树前扫同级目录、一个端口一个实例、共享资源独占、迁移文件不可回改、本机配置位置。收工前：停掉自己启动的进程、改动 commit 并 push、删除工作树前自检、会话产物只写 `.claude/tmp/`。删错之后：已提交内容在对象库中可经 reflog 与 `git fsck --lost-found` 找回，未提交改动可从会话记录还原（窗口由 `cleanupPeriodDays` 决定）。另含从 DTSF 提炼的 Git 协作纪律：已推送分支同步上游一律 merge、冲突逐段按业务意图处理。
- §1.3 新增「页面提示不代表通过」证据门槛。
- §3 新增：写任务的子代理必须各自隔离，宿主提供 `isolation: "worktree"` 时用它。
- §3 钩子条补上工作树删除防护的指针。
- 新增 `scripts/session-inventory.py`：清点工作树（含未提交数与未推送数）、端口占用与属主、独占容器状态、stash 列表、无远端分支、未打包对象数量与最近打包时间。
- 新增 `scripts/worktree-remove-guard.py`：`WorktreeRemove` 事件钩子（1.4.0 删除）。
- 新增 1 个 eval case `worktree-closeout`。

验证：

- 清点脚本在 DTSF 实跑通过：输出 20 个工作树、18 条 stash、11 条无远端分支、7 个端口的占用与属主、2 个独占容器的运行状态。依据实测修正两处：中文列宽按字符数补空格会错位，改为按东亚字符宽度计算；配置从项目目录改为 `~/.claude/session-hygiene.json`，因为端口与容器属于本机资源，放进仓库后换工作树就看不见。
- 防护脚本在独立临时仓库夹具里跑 6 条用例全部通过。依据实测修正一处：钩子往标准错误写中文时按系统代码页编码，宿主要求 UTF-8 会读到乱码，已加 `sys.stdout|stderr.reconfigure(encoding="utf-8")`。
- 钩子载荷字段取自 Claude Code 二进制内的构造代码，为 `{...会话字段, hook_event_name: "WorktreeRemove", worktree_path: "<绝对路径>"}`。

未验证：

- eval case `worktree-closeout` 尚未跑 runner。

## 1.2.0 — 2026-09-17

来源：Matt Pocock AI Engineer 工作坊方法论（公众号文章结构化笔记，`lab-area/exp/2026-09-17-wechat-content-notes/notes/article-3.md`），经 grill-me 会话三分类后吸收。

- §1.1 追问环分档：机械改动维持 1-3 个轻量反问；需求/方案谈拢改用 grilling 协议（设计树、整批前沿、每问附推荐答案、纯文本不用 AskUserQuestion、追问并记录决策依据），手动调 `mattpocock-skills:grill-me`。
- §1.4 新增审阅顺序：先看测试是否测合理行为，再看代码。
- §1.5 新增三条：计划必须含「明确不做及理由」停止线，缺信息停下问；验收项必须一眼可判定；规划产物完成后标记，旧规划不作现行指令（迁移文件除外）。
- §3 新增竖切判据：每片完成须有外部可观察现象，第一片穿过全部受影响层，横切打回。

## 1.1.0 — 2026-09-12

来源实验：`C:\ZYS\Code\lab-area\exp\2026-09-11-claude-workflow-harness\`，经 skill-auditor 静态审计与 better-harness 0.7.0-alpha1 证据审计后同步。

- §1.1 新增「Context→追问→执行环」：非平凡任务先读最小上下文，目标/约束/验收缺失先问 1-3 个反向问题；明确机械改动不反问。
- §1.1 新增「Prompt → Context → Harness」分层：三者缺一时标缺口，不靠模型猜。
- §1.1 新增「角色边界」：AI 负责整理/初稿/疑点/检查，人负责目标/边界/取舍/最终结论。
- §1.1 新增「确认前先完成可授权准备」：只读调查先行，写入与不可逆动作留在确认后。
- §1.3 交付规则加证据回执：结果、改动范围、验证证据、未完成项/风险。
- §1.5 规范驱动产物改为宿主解耦：以项目实际 workflow contract/规格/状态机为准，不硬编码路径。
- §3 Agent 切片改为宿主实际执行计划/合同优先，移除固定 `02-design/execution-plan.md`。
- §3 新增 Harness 审计触发：改 Skill/规则/Hook 或出现返工、验证遗漏、规则冲突时显式运行 `/better-harness`。
- §3 Hook 规则改为宿主解耦：以 `settings.json` 实际挂载的 PreToolUse hooks 为准，移除固定 Claude/pi 路径。
- 新增 `CHANGELOG.md`、`references/MAINTENANCE.md`；evals 从 2 个 case 补到 5 个，model 字段更新为 `claude-haiku-4-5`。

验证：新 CLI 显式 `/code-change-workflow` 可加载全部新规则（证据见实验目录 `VERIFICATION.md`）。未验证：自然语言自动触发（headless `-p` 会话不注入 skill 清单）、eval runner（`claude plugin eval` 被组织 early-access gate 拦截）。

## evals 迁移到官方 runner 布局 — 2026-09-12（资产更新，不 bump skill 版本：SKILL.md 正文零改动）

- CLI 2.1.269 实测 eval 组织门已开放；旧 `evals/eval.yaml + cases/*.yaml`（v1alpha1）布局 runner 发现数为 0，从未真跑过。
- 5 个 case 全量迁移为 `evals/<case>/case.yaml`（schema_version "1.0"）；判词从 `output_contains` 改为确定性 `regex` grader（pattern 贴 SKILL.md 原词）；bug-fix、delivery-evidence 用 `scaffold_script` 在沙箱 cwd 落 fixture（`add_dirs` 只授读权限、不复制文件，已二进制+沙箱实证）。
- 旧布局存档于实验目录 `evals-legacy-archive/` 后删除；最终全量 5/5 绿（258s、$0.17），research-no-route 另跑 3/3 稳；证据见实验目录 `eval-runner-evidence/`。
- 附带证据：全部 eval trace 中子会话第一个工具调用均为 Skill code-change-workflow，自然语言自动触发在 eval 载体下已验证（headless `-p` 不注入清单的结论仅限该载体）。

## 1.0.0 — 2026-07-29（追认）

- 由全局 `CLAUDE.md` 瘦身迁出（台账事件 `claude-md-slimming-20260729`）：原 §1.1-1.4 / §2 / §3 / §4 成为改前/改中/改后清单、AI 代码审查方法论、调试工作流、Agent 调度、止血回退。
- 2026-07-29 至 2026-09-11 之间的具体演进 unknown：无版本字段、无变更记录，安装台账只有出处登记，不补编。
