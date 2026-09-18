# Changelog

本文件从 2026-09-12 起记；此前无版本惯例，历史变更只追溯安装台账。

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
