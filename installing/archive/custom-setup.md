# 自建设施台账（非外部安装，自己造的）

> 已归档（2026-09-24 现状表与流水分家）：本文件是**流水**，默认不读，追溯时按名或日期定位；现状表见 [`../custom-setup.md`](../custom-setup.md)。文中 `[X.md](X.md)` 形式的链接指向本目录内的同名流水。

记录自建 skill / hook / statusline / 全局配置的出处与迁移要点。外部装的见 skill-install.md / mcp-install.md / tool-install.md。

自建资产迁移原则：**git 仓库应追踪全部自建 skill**（新增自建 skill 必须在 `.gitignore` 的 skills/ 白名单登记）；`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠 skill-install.md / tool-install.md 记录的地址与命令重装。

---

## git_guard.py 修改（2026-08-14）

- **位置**：`~/.claude/hooks/git_guard.py`（PreToolUse git 守卫，Python，约 120 行）
- **改动**：新建分支（`git checkout -b` / `git switch -c`）从无条件 deny 改为与 commit/push 一致的「用户确认放行」——`user_confirmed(data)`（读会话 transcript 检测用户最近消息含 确认/批准/授权/confirm 等词）命中则放行，否则 deny。仅改这一个 elif 分支。
- **保持不变**：BLOCK 列表（89-108 行）不可逆/破坏性操作（git reset --hard、branch -D、push --force、clean -f、rm -rf、SQL DROP、--no-verify、npm publish 等）仍无条件拦截；commit/push 确认放行逻辑未动。
- **需求来源**：用户指令「git_guard 修改成，除了不可逆的操作，在我确认之后都可以直接执行」（2026-08-14，子代理执行）。
- **验证**：`python -m py_compile git_guard.py` 通过（PY_COMPILE_OK）。
- **回退**：还原该 elif 分支为 `deny("CLAUDE.md §1.1: 新建分支前确认 git status 干净...")` 一行。

### git_guard.py 意图授权升级（2026-08-28，自 pi safety-net guards.js explicitApproval 移植）

- **改动**：`user_confirmed()` 从「仅确认词表」升级为 pi 语义五层判定——**否定意图 → 确认词 → 疑问句/查询 → 操作意图**。指令含操作动词（提交/推送/建分支）且非疑问句即视为用户明确指令，无需确认词。同时修了两个 __main__ 结构 bug（hook 模式早退吞自检、SELF_TEST 标志缺失）。
- **验证**：`--self-test` 8/8 断言过（确认词放行/操作指令放行/否定意图拦/疑问句拦/推送口语放行/推送动词放行/查询意图拦×2）；hook 模式实测未确认 commit 被 deny、非 git 命令静默放行。
- **回退**：还原 user_confirmed 为确认词表版本即可（git 历史有 2026-08-14 版本）。

---

## 自建 hook 新增（2026-08-28）

### plugin_drift_check.py（SessionStart 插件台账漂移检测，自 pi skill-sync-watch 移植）

- **位置**：`~/.claude/hooks/plugin_drift_check.py`（Python，~100 行，纯 stdlib）
- **历史注册状态**：曾挂载于 `~/.claude/settings.json` 的 SessionStart 第 4 个分组；当前未挂载，文件保留为 dormant，不自动运行。
- **行为**：对照 `settings.json` enabledPlugins 与 baseline 快照（`~/.claude/installing/plugin-drift-baseline.json`，首轮自动建）：新增 enabled → 报「台账新增」；baseline 内消失 → 报「移除/禁用」；enabled 但缓存缺失（`~/.claude/plugins/cache/<mp>/<pl>`，`@skills-dir` 除外）→ 报「破损 enable」。**只报告不自动修复**（pi 治理哲学：纳入须人确认），经 hookSpecificOutput.additionalContext 注入会话，无漂移静默。
- **历史验证**：曾验证 baseline 建立及新增/移除检测方向正确；当前因未挂载不会执行。
- **当前状态**：文件仍在磁盘，但 `settings.json` 当前未注册该 SessionStart hook；如需恢复，需重新评估 baseline 与启用状态后再挂载。
- **回退**：恢复本段历史注册描述即可；不涉及 settings.json、hook 文件或 baseline。

---

## 会话生命周期机制（2026-09-18）

需求来源：用户指令「更简单、更干净、更能掌控；前面的会话不留残留影响后面的会话，不同会话间不互相影响；主要是规则要做好，工作产物不能胡乱产生」。

### 脚本

| 文件 | 作用 |
|------|------|
| `~/.claude/hooks/scripts/session-guard.py` | `start` / `end` 两个子命令。开发前报告本仓库主检出与各工作树的卫生状况，开发结束写收尾记录。不删除任何工作树。收尾记录的追加与裁剪共用一把锁，裁剪在锁内重新读取，避免读到旧快照整份写回而丢掉并发追加的记录。锁等待超时改写独占命名的溢出文件；锁文件记持有者令牌，释放时比对一致才删，被接管之后不会误删接管者的锁 |
| `~/.claude/hooks/scripts/product-guard.py` | PreToolUse 拦截：`git worktree add` 的目标路径解析后不在本仓库主检出 `.claude/worktrees/` 下，或工作树名不合规（hash、纯日期、保留名、非 kebab-case）；`EnterWorktree` 的 `name` 与 `path` 同样校验。命令拆成词后取出每一处真正的目标路径再规范化比对，不按子串判断；`git worktree add` 的带值选项与 git 全局选项里吃下一个词的项都按 git 2.54 实测结果逐条登记；heredoc 正文在拆词前剥掉，提交消息与脚本正文里出现命令字样不会被当成执行 |
| `~/.claude/hooks/scripts/session-status.py` | 只读汇总活跃会话、工作树四分类、孤儿目录、stash、主检出、仓库根散落文件、登记端口、容器。会话枚举失败时显式标注降级，可清理项标出被忽略内容。收尾记录的时间戳只认数值，缺字段或类型错误时计数照常、明细跳过 |
| `~/.claude/hooks/scripts/selftest.py` | 自检，`python selftest.py`，退出码 0 表示全过 |

纯 stdlib，无第三方依赖。Python 解释器固定用 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`（与 settings.json 其他 hook 一致）。

设计取舍：只有工作树位置与命名进硬拦截，因为它们是客观可判定的，且建错位置的代价高。仓库根建文件由 `/dev-status-by-user` 报告违规项；产物放错目录没有自动检查，靠文本约定。所有工作树删除都走 `/dev-clean-by-user` 并逐条确认，不存在自动删除路径。子代理工作树由 harness 以 `agent-<hash>` 命名创建，拦截管不到，只能靠 `/dev-status-by-user` 的孤儿目录分类暴露。把命令再包一层解释器（`bash -c "…"`、`python -c "os.system(…)"`）之后顶层拆词看不到 `git worktree add`，会放行；拦截的定位是防止误建，不作为安全边界。机制自身所在仓库（`~/.claude`）按普通仓库处理，不特殊跳过。

### Skills 与配置

- `~/.claude/skills/dev-status-by-user/SKILL.md`、`~/.claude/skills/dev-clean-by-user/SKILL.md`
- `~/.claude/settings.json` hooks 段新增：`SessionStart` 第 3 组（session-guard start，timeout 25）、`SessionEnd` 1 组（session-guard end，timeout 15）、`PreToolUse` 1 组（product-guard，matcher `Bash|EnterWorktree`，timeout 15）
- `~/.claude/CLAUDE.md` 第 8 节「会话、产物与本地资源」，7 段：工作树 / 产物去处 / 交接文档 / 并行会话 / 收尾 / Git 写权限 / 查看与清理
- `~/.claude/docs/session-lifecycle.md`：机制说明、操作方式、故障处理

#### Skills 迁移（2026-09-20）

- 来源：原全局命令 `~/.claude/commands/dev-status.md`、`~/.claude/commands/dev-clean.md`
- 日期：2026-09-20
- 安装命令原文：`mkdir -p "C:/Users/zys31/.claude/skills/dev-status" "C:/Users/zys31/.claude/skills/dev-clean"`，随后执行 `mv "C:/Users/zys31/.claude/skills/dev-status" "C:/Users/zys31/.claude/skills/dev-status-by-user" && mv "C:/Users/zys31/.claude/skills/dev-clean" "C:/Users/zys31/.claude/skills/dev-clean-by-user"`；文件正文由 Claude Code 原生 `Write` 写入
- 安装位置：`~/.claude/skills/dev-status-by-user/SKILL.md`、`~/.claude/skills/dev-clean-by-user/SKILL.md`
- 依赖：`C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`、`~/.claude/hooks/scripts/session-status.py`
- 备注：保持原参数和执行规则；按自建 skill 命名约定使用 `-by-user` 后缀，调用名相应改为 `/dev-status-by-user`、`/dev-clean-by-user`；迁移后删除旧 `commands/*.md`

### 运行时数据

`~/.claude/session-handoff.jsonl`（收尾记录，保留 7 天，按 `repo` 字段过滤，只报告本仓库的遗留；`repo` 统一取主检出根，所以从链接工作树里开会话也能对上。时间戳只认数值，缺字段或类型不对的记录排在排序前面，计数照常、明细跳过）、`~/.claude/session-handoff.d/`（锁等待超时时写的溢出记录，独占命名，开发前检查与 `/dev-status-by-user` 都读它，下一次裁剪并回主文件）、`~/.claude/session-handoff.lock`（收尾记录的写入锁，正常跑完即删，超过 30 秒视为陈旧锁自动接管，修改时间在将来时同样按陈旧接管）、`~/.claude/session-guard.log`（异常，以及过期记录被丢弃时留下的路径与改动数）、`~/.claude/product-guard.log`。

活跃会话来自 `claude agents --json`，这是官方文档给出的受支持接口（`cwd`、`kind`、`startedAt`、`pid`、`status`、`sessionId` 等字段）。不读 `~/.claude/sessions/*.json`——官方文档从未描述该目录，并与 `~/.claude/jobs/<id>/` 同属被明确声明为「不是稳定接口」的内部层。`/dev-status-by-user` 用它区分工作树是在用还是可清理；枚举失败时 `active_sessions()` 返回 None，输出显式标注「活跃会话 枚举失败」并提示不要据此删除，不伪装成无人占用。

### 验证

自检脚本 `~/.claude/hooks/scripts/selftest.py`（`python selftest.py`，退出码 0 表示全过）：153 个用例全部通过。覆盖工作树位置越界、相对路径上跳、`..` 路径穿越、`.claude/worktrees/` 只出现在 `-b` 参数或注释里、`.claude` 下的非约定目录、`worktrees-old` 前缀混淆、hash 命名、保留名与纯日期、非 kebab-case 命名、反斜杠写法、`worktree list` / `worktree remove` 放行、同一条命令里串联多处 `git worktree add`、重定向被当成目标路径、`--lock` / `--track` 不带值的选项、git 全局选项里吃下一个词的项（`-c`、`--git-dir`、`--work-tree`、`--namespace`）后仍判出越界且不误拒只读命令、`git -C <仓库>` 与 `cd <仓库> &&` 的判定基准、`git.exe` 与绝对路径形式的 git、名字像 git 但后面不是 `worktree add` 的写法、`EnterWorktree` 的 `name` 与 `path` 两条入口（含两者同时给出时都要校验）、command 不是字符串时放行且不抛异常、非 git 目录静默、机制自己的仓库按普通仓库汇报、跨仓库遗留不串味、从链接工作树里开会话按主检出汇报、会话枚举为空或字段缺失时不崩溃、枚举失败打印降级告警且不把工作树报成无会话占用、退出提示不承诺自动清理、收尾记录并发追加不丢、过期记录丢弃写日志、无需裁剪时不重写文件、陈旧锁自动接管、接管后原持有者不误删新锁、锁时间在将来时按陈旧接管、降级追加写溢出文件且裁剪时并回主文件、收尾记录时间戳缺字段或类型不对时不崩溃且不打印明细、仓库根散落文件与孤儿目录（含符号链接）的识别、被忽略内容单列。在脚本同级建临时 git 仓库当沙箱，`try/finally` 保证跑完自删。

真实仓库实测（2026-09-18，dtsf，1 个工作树）：SessionStart 耗时 0.65 秒，`/dev-status-by-user` 耗时 1.48 秒。

收尾记录的并发行为实测：两个裁剪进程加一个追加进程各跑独立 Python 进程，6 轮共追加 240 条，丢失 0 条。修复前同一套用例的丢失率是 22.5%（240 条丢 54 条），成因是裁剪读到快照后整份写回，覆盖了这期间追加的记录。

第二轮审计（2026-09-19）复跑：3 个追加进程加 2 个裁剪进程，8 轮共 288 条，丢失 0 条。这一轮又查出锁的两处缺口并修掉。其一，持锁超过 30 秒被接管之后，原持有者释放时删掉了接管者的锁，两个进程同时进入临界区，实测第三方能直接拿到锁。其二，拿不到锁时的降级路径直接往共用文件追加，而同一文件并发追加在 Windows 上会互相覆盖，6 个进程同时降级时实测丢 6.7%（30 条丢 2 条）。降级改写独占命名的溢出文件之后，同样 5 轮 × 6 个进程共 30 条，丢失 0 条。另外补上了 `git.exe` 与绝对路径形式的 git 调用绕过拦截的缺口。

第三轮审计（2026-09-19）复跑：锁令牌契约 17 项、降级与裁剪 35 项、放行与拒绝判定 60 项、状态汇总 9 项、并发与全局选项 14 项，除本轮查出的缺陷外全部通过。并发不丢记录用 48 条降级写入配 2 个裁剪线程交错，存活 48/48。查出并修掉三处。其一，`session-status.py` 打印最近记录时直接下标取 `ts`，记录缺该字段时抛 `KeyError`、写成字符串时抛 `TypeError`，`/dev-status-by-user` 与 `/dev-clean-by-user` 整个不可用；排序处早已用 `isinstance` 兜底，只有打印这段漏了。其二，`product-guard.py` 的选项跳过循环只认 `-C`，带 `--git-dir` 与 `-c` 的越界命令里取值被当成子命令位置，整个 `git worktree add` 看不到而放行，真实 git 确认两条都能在仓库外建出目录；git 全局选项按 2.54 实测逐条核对后登记，等号形式与空格形式都覆盖。其三，拆词时把 heredoc 正文也算进命令，任何提交消息或脚本文本里出现 `git … worktree add` 字样都会被拒绝，实测本轮修复自己的提交消息就被拦下；改为拆词前剥掉正文，按结束标记定位，找不到标记时原样判定。同一轮里也确认机制自己的仓库按普通仓库处理只产出一行主检出提示，据此取消了 `~/.claude` 的静默跳过；`selftest.py` 原有的「`~/.claude` 静默」用例是靠该跳过才为空的，从未真正验证过 `handle_start` 能处理这个仓库，已改为断言它照常汇报。

性能随工作树数量近线性：`/dev-status-by-user` 约每棵 84 毫秒，SessionStart 约每棵 73 毫秒，主导成本是每棵一次 `git status --porcelain` 子进程。70 棵工作树时 `/dev-status-by-user` 约 7.2 秒。

第三轮的性能实测（真实仓库，2026-09-19）：SessionStart 在 `~/.claude` 约 0.11 秒、在 dtsf 约 0.58 秒，SessionEnd 在 dtsf 约 0.27 秒，`/dev-status-by-user` 在 dtsf 约 1.09 秒。收尾记录 4000 条（0.8 MB）时一次裁剪 15 毫秒；锁等待窗口固定 2 秒，与记录条数无关，空闲时追加实测 0 毫秒。

Windows 编码：hook 输出必须显式 `sys.stdout.reconfigure(encoding="utf-8")`，否则默认 GBK 会破坏中文 JSON。三个脚本的 `main` 都有这一行。

### 删除安全边界

删除是不可恢复动作，机制按三条线约束：

1. **机制自身不删任何东西。** 没有自动清理路径，只有 `/dev-clean-by-user` 命令，且必须逐条列出路径等用户确认。
2. **有未提交改动的工作树删不掉。** `/dev-clean-by-user` 只列零改动的项，`git worktree remove` 本身也会拒绝脏工作树。被拒时不许用 `--force`。
3. **孤儿目录一律不删。** git 已不再注册它们，里面的改动不在任何分支上，`/dev-status-by-user` 会标出有没有同名分支。标「无同名分支」的目录是内容的唯一副本，机制不碰，交用户判断。
4. **被 `.gitignore` 覆盖的内容会被连带删除，所以单列标注。** `git status --porcelain` 看不到被忽略的文件，只含这类文件的工作树会被判定为干净并列入可清理，而 `git worktree remove` 会连那些文件一起删掉且退出码为 0。`/dev-status-by-user` 因此在可清理项上标出「另有 N 项被忽略内容」，`/dev-clean-by-user` 要求用户确认完整路径清单后才执行。

### 回退

从 `~/.claude/settings.json` 的 hooks 段删掉 `SessionStart` 第 3 组、`SessionEnd`、`PreToolUse` 三段即可，三个脚本变成不被调用的惰性文件。命令与文档（`dev-status.md`、`dev-clean.md`、`session-lifecycle.md`、`selftest.py`）可一并删除。

运行时数据也要清掉：`session-handoff.jsonl`、`session-handoff.d/`、`session-handoff.lock`（残留的锁会让下次写入等待 2 秒再降级）、`session-guard.log`、`product-guard.log`。`session-hygiene.json` 是本机端口与独占资源台账，独立于本机制，应保留。

机制本体已提交并推送到 `~/.claude` 仓库，远程 `origin` 为 `https://github.com/zys3198/claude-stack`。要恢复某个版本，从该仓库检出对应提交即可；看当前实现则直接读 `~/.claude/hooks/scripts/` 下四个脚本。

---

## 自建 skill（当前目录 + 历史记录，非 cc-switch 同步）

- 2026-09-11 新增全局 `ai-product-development`，详见下方独立台账条目。
- 2026-09-11 新增全局 `company-discovery-evaluation`，详见下方独立台账条目。
- 2026-09-23 新增全局 `jev-browser-acceptance-by-user`，详见下方独立台账条目。**2026-09-24 已合并进 `auto-browser`。**

### jev-browser-acceptance-by-user（2026-09-23，全局）
- 出处：本地自建；用户要求将 JEV Browser 固定脚本验收方式做成全局 skill。
- 原始安装命令：未留存；使用原生 Write 创建 `SKILL.md`。
- 位置：`~/.claude/skills/jev-browser-acceptance-by-user/SKILL.md`
- 依赖：JEV Browser 运行包、Browser Harness/CDP/Chromium 容器和项目验收脚本；不依赖 TypeSafe 或文本模型密钥。
- 当前状态：已创建；`disable-model-invocation: false`，允许模型按描述自动调用；当前会话可发现该 skill。
- 验证：固定 `Browser` 探针已连接 CDP、观察登录页、识别 12 个动作并保存登录页截图；未填写、未提交、未写入业务数据。
- 回退：用户确认后删除上述 skill 目录，并移除 `.gitignore` 中的 `!skills/jev-browser-acceptance-by-user/` 和本条台账记录。
- **2026-09-24 处置：已合并进 `auto-browser`**，原目录移入 `~/.claude/backups/skills-before-merge-auto-browser-2026-09-24/jev-browser-acceptance/`（1 文件 SKILL.md，4573 B）。判据=与 agent-browser 互补非替代，合并后按环境分支选路线。**更正**：本条记的 `-by-user` 后缀名不适用，实际目录一直是 `~/.claude/skills/jev-browser-acceptance/`（无后缀），`.gitignore` 白名单也一直是 `!skills/jev-browser-acceptance/`。内容未丢：`Browser.reuse` 标签页复用、daemon 5 秒 IPC 上限、凭据脱敏、标签页清单收尾均已写进 auto-browser。恢复=移回 `~/.claude/skills/jev-browser-acceptance`。

### auto-browser（2026-09-24，全局，自建合并）
- 出处：用户拍板「合并为 auto-browser 单 skill」，把第三方 junction `agent-browser` 与自建 `jev-browser-acceptance` 合为一条，按任务分支。
- 位置：`~/.claude/skills/auto-browser/SKILL.md`；`.gitignore` 白名单 `!skills/auto-browser/`。
- 结构：路线 A = agent-browser（宿主通用，覆盖强：shadow DOM / iframe / file input / Electron）；路线 B = JEV Browser（正确性守卫、CDP 直连、跨脚本复用标签页）。
- 依赖：A 需全局 `agent-browser` CLI 0.38.1；B 需 `~/.claude/tools/jev-ultrafast`（uv 环境，`uv sync` 装 `browser-harness==0.1.13`）。
- 关键实测：JEV 在宿主**必须带 `PYTHONUTF8=1`**，否则 `browser.py:31` 的 `Path.read_text()` 走 GBK 解码抛 `UnicodeDecodeError`——上游只在 Linux 容器跑过，宿主路径从未验证。端到端已实测：headless Chrome 上 `observe()` 读出 title/text 并发现 4 个动作（click / fill / Open / wait）。
- 当前状态：已创建；`disable-model-invocation: false`，按描述自动调用。
- 正文修订（2026-09-24，writing-for-agents 审核后）：补回合并时丢失的 JEV 固定脚本约束（不调用 `Agent`／不要求文本模型密钥）、路线 B 执行流程、验收约束、完成标准；description 触发词 6→3；删环境缓存（`skills list` 输出、`uv sync` 装法）；`Browser(url)` 禁令保持祈使语气并指名违规写法。6535 → 7659 B。
- 并行会话改动（2026-09-24 17:26:37）：项目 `C--ZYS-Code-dtsf` 的 EAM 验收会话直接 Edit 本文件，加「点 naive-ui 组件要用真鼠标事件」一节（源 `jev-browser-acceptance` 备份中无此内容，属该会话新得经验）。已保留。
- 回退：删 `~/.claude/skills/auto-browser`；从 `~/.claude/backups/skills-before-merge-auto-browser-2026-09-24/` 移回 `jev-browser-acceptance`；按 `skill-install.md` 的 `New-Item -ItemType Junction` 重建 agent-browser junction；`.gitignore` 白名单还原为 `!skills/jev-browser-acceptance/`。

当前可用（2026-09-23，20 个，全部带 `-by-user` 后缀，以 `skills/` 实际目录为准）：（**2026-09-24 更正**：`skills/` 下实际**无任何** `-by-user` 后缀目录，是上面这份清单记错了；以 `skills/` 实际目录为准。同日新增 `auto-browser`、移除 `jev-browser-acceptance`。）
`ai-product-development-by-user`、`article-writer-by-user`、`awesome-design-md-by-user`、`bidirectional-steelman-by-user`、`cc-switch-setting-sync-by-user`、`code-change-workflow-by-user`、`company-discovery-evaluation-by-user`、`content-to-note-by-user`、`dev-clean-by-user`、`dev-status-by-user`、`drawio-article-illustration-by-user`、`drawio-chart-by-user`、`improver-skill-by-user`、`install-ledger-by-user`、`instruction-engineering-by-user`、`jev-browser-acceptance-by-user`、`parallel-delegation-by-user`、`skill-auditor-by-user`、`skill-trimmer-by-user`、`toolchain-pitfalls-by-user`。

`generic-course-tutor-workspace` 是配套工作区，不计入 skill。

### ~~generic-course-tutor~~（2026-09-19 已删除，用户拍板）
- 删除前状态：本地自建全局 Skill，单文件 `~/.claude/skills/generic-course-tutor/SKILL.md`，用户 2026-09-01 台账审计确认归属。
- 出处：本地自建；用户于 2026-09-01 台账审计确认归属。
- 关键文件：`~/.claude/skills/generic-course-tutor/SKILL.md`
- 迁移：复制整个 `generic-course-tutor/` 目录，并在 `.gitignore` 加入 `!skills/generic-course-tutor/`。
- 依赖：无外部运行时依赖；课程内容由调用方提供。

### ~~lesson-svg-diagram~~（2026-09-02 已删除，原误归自建）
- 归属更正：用户确认按 Matt 历史版本/派生版归为第三方；当前 Matt 插件缓存未找到同名文件，精确来源未锁定。
- 处置：已物理删除 `~/.claude/skills/lesson-svg-diagram/`；不计入当前可用自建列表。
- 恢复：需重新查证原始来源后再安装；本条不构成可直接重装命令。

### 四域开工路由器（历史记录，部分已退役）
- ~~`ai-coding-guide`（编码域，v1.4.9）~~ **更正 2026-09-02**：编码域散文路由器终版 v1.9.0 已退役归档（`~/.claude/archive/ai-coding-guide-v1.9.0/`）；后续 fork 版已删除并备份（`~/.claude/backups/ai-coding-guide-delete-20260902/`） / `article-writing-guide`（写作域）/ `learning-guide`（学习域，v1.4.6）/ `frontend-guide`（前端域，v1.5.3）
- 出处：2026-07 多轮会话沉淀；质量标准见 memory `router-guide-skill-quality-bar`；审查工具 `guide-skill-auditor`
- **2026-09-21 复查**：`~/.claude/archive/ai-coding-guide-v1.9.0/` 与 `~/.claude/backups/ai-coding-guide-delete-20260902/` 两处路径均已不存在（`~/.claude/archive/` 整个目录不存在），本条只剩历史出处价值，恢复需重建。
- 迁移要点：四个一起拷；各有 CHANGELOG.md 记演进；互相有跨域转介引用，别只拷一个。

### code-change-workflow
- 出处：2026-07-29 CLAUDE.md 瘦身（§1-4 流程迁入，memory `claude-md-slimming-20260729`）
- 内容：改前/改中/改后清单、AI 代码审查、调试、Agent 调度、止血回退
- 2026-09-12 同步：将实验候选中已核对的 Context→追问→执行、`Prompt → Context → Harness`、AI/人工责任边界、交付证据、规范产物宿主解耦、Harness 审计触发和 Hook 宿主解耦规则合并到全局 `~/.claude/skills/code-change-workflow/SKILL.md`。
- 验证：候选静态检查、Better Harness evidence bundle、3 路只读审计和 renderer validation 均通过；隔离插件显式 `/code-change-workflow` 可读取候选独有规则。
- 未验证：自然语言自动触发仍为 `unknown`；真实代码 fixture 修改和测试未执行，不能据此声称自动路由或完整执行闭环已生效。
- 未同步：实验报告、证据包、runtime-test、fixture、Hook 配置和全局 `CLAUDE.md`。
- 回退：按同步前正式 Skill 内容恢复 `~/.claude/skills/code-change-workflow/SKILL.md`；不删除实验材料。

### ai-product-development（2026-09-11，全局）
- 出处：用户提供的 Runline 视频内容提炼；用户确认做成全局 skill。
- 创建命令：`mkdir -p "C:/Users/zys31/.claude/skills/vibe-coding-workflow"`；随后使用原生 Write 创建 `SKILL.md`，再重命名目录。
- 位置：`~/.claude/skills/ai-product-development/SKILL.md`
- 依赖：无外部运行时依赖。
- 备注：独立提炼 AI 辅助产品开发思路，不编排或调用其他 skill；手机远程开发仅作为可选案例，不作为触发条件；`disable-model-invocation: true`，仅用户显式调用 `/ai-product-development` 时执行。

### company-discovery-evaluation（2026-09-11，全局）
- 出处：用户提供的抖音视频内容提炼；用户确认做成全局 skill。
- 创建命令：`mkdir -p "$HOME/.claude/skills/company-discovery-evaluation"`；随后使用原生 Write 创建 `SKILL.md`。
- 位置：`~/.claude/skills/company-discovery-evaluation/SKILL.md`
- 依赖：宿主当前网页检索、页面阅读或用户提供链接/材料；无外部运行时依赖。
- 备注：仅用户显式调用 `/company-discovery-evaluation` 时执行；`disable-model-invocation: true`；不自动路由。
- 回退：用户确认后删除全局目录；实验源保留于 `C:\ZYS\Code\lab-area\exp\2026-09-11-company-discovery-evaluation\company-discovery-evaluation\`。

### expose-unknowns
- 出处：暴露 unknown 方法论沉淀（memory `expose-unknowns-method`）

### bidirectional-steelman（2026-09-02）
- 出处：用户审计确认自建；用于方案取舍、选型和决策双向论证。
- 位置：`~/.claude/skills/bidirectional-steelman/SKILL.md`
- 依赖：无外部运行时依赖。

### parallel-delegation（2026-09-02）
- 出处：用户审计确认自建；用于独立、可验收任务的并行委派与统一验收。
- 位置：`~/.claude/skills/parallel-delegation/SKILL.md`
- 依赖：依赖当前会话提供的 Agent/subagent 能力，无额外运行时依赖。

### ~~guide-skill-auditor~~（历史名称，当前 skill 为 skill-auditor）
- 出处：router 型 guide 质量审查方法论固化（memory `router-guide-skill-quality-bar`）

### skill-trimmer
- 出处：skill 库精简判定框架（Carl 四删五留 + 本机三决议，memory `skill-trim-carl-article-2026-07-28`）

### semantic-confirmation-guard（2026-09-24）
- 出处：用户确认的确认架构重设计计划 `~/.claude/plans/humble-swimming-scott.md`；本轮为现有全局 Hook、规则、Skill 与 cc-switch 同步闭环的定向改动。
- 位置：`~/.claude/CLAUDE.md`、`~/.claude/settings.json`、`~/.claude/hooks/scripts/resource-guard.py`、`~/.claude/hooks/scripts/authorization_scope.py`、`~/.claude/hooks/settings-degrade-guard.py`、`~/.claude/hooks/settings-sync-auto.py`、四个相关 Skill 与 `sync_claude_common.py`。
- 改动：主模型负责 R0-R4 与目标识别；授权按 `session_id`、`task_id`、精确 scope 绑定；Hook 只保留客观守卫、硬阻断和高风险失败关闭；静态权限移除宿主工具链宽泛 allow 与 Git ask；公共权限快照改为 live 精确覆盖。
- 依赖：现有 Python 3.12、cc-switch SQLite、Claude Code PreToolUse/SessionStart/PostToolUse Hook；未新增模型、服务、插件或第三方依赖。
- 当前状态：已启用；授权状态写入 `~/.claude/authorization/`；`permissions.defaultMode` 保持 `auto`；`permissions.ask` 允许为空。
- 验证：授权测试与资源守卫完整测试在受限一次性容器内通过；固定 Docker payload 回放无 Hook 输出；cc-switch 三层切换验证尚未执行。
- 回退：按用户确认后用文件编辑恢复本轮涉及的全局文件；同步脚本写库前生成的 `~/.cc-switch/backups/sync-backup-<ts>.json` 保留用于公共快照与代理快照恢复；不自动删除备份或授权状态。

### cc-switch-setting-sync
- 出处：防 cc-switch 切换 provider 降级 settings.json 的同步流程
- 2026-09-24 改动：`sync_claude_common.py` 同步公共配置时，原子修正 `proxy_live_backup` 中的 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 与禁止的 `CLAUDE_CODE_*` 键；`--check` 同时检测公共配置和代理快照；备份文件纳入代理快照。
- 位置：`~/.claude/skills/cc-switch-setting-sync-by-user/scripts/sync_claude_common.py`
- 验证：Python 语法检查、临时 SQLite 回归测试、真实 `--check` 和 `--dry-run` 均通过；当前快照与公共配置匹配。
- 未验证：重启 cc-switch/Claude 后的真实代理热切换回放尚未执行。
- 回退：恢复脚本原文件；运行时 DB 写入前自动生成的 `~/.cc-switch/backups/sync-backup-<ts>.json` 可恢复公共配置和代理快照。

### learning-personas
- 出处：2026-08-16 从 DeepTutor（eduhub.deeptutor.info，本地装于 `C:\ZYS\Code\deep-tutor`）三 persona（peer/teacher/research-assistant）提炼，用户拍板独立 skill + CLAUDE.md 引用式
- 内容：**学习系统总纲 + 说话层角色库**。三个正交决定：判级查（expose-unknowns）/ 归属问（这技能归你吗→你练/我讲/存起来）/ 说话层（peer/teacher/research）。全系统学习模式唯一词汇源
- 接线：CLAUDE.md 尾部「## 学习角色（引用式）」被动触发规则（学习时刻先主动问角色+归属，再套用；执行型任务不启用）；三 guide（learning-guide / article-writing-guide / ai-coding-coach）开工问询词汇统一换为归属+persona 并引用本 skill（渐进式披露，不散落展开）；learning-first memory 四分支并进归属一问
- 迁移要点：SKILL.md 单文件；无脚本无依赖；与 cram-engine/deep-learn/expose-unknowns 互补（流水线 vs 说话方式）；换词涉及 guide 时同步改 CHANGELOG + references + test-prompts；**已入 git 白名单**（`.gitignore` skills/ 白名单新增 `!skills/learning-personas/`，2026-08-16）

### 写作 skill（历史自建清单，当前状态以本节上方清单为准）
- 历史清单：article-writer / chinese-markdown-normalizer / javaguide-style-guide / multi-review-pipeline / drawio-article-illustration / drawio-chart / publish-final-check / plagiarism-audit / tech-article-review / content-to-note
- 当前仍在磁盘：article-writer / article-writing-guide / drawio-article-illustration / drawio-chart / content-to-note
- 当前目录已无或已退役：chinese-markdown-normalizer / javaguide-style-guide / multi-review-pipeline / publish-final-check / plagiarism-audit / tech-article-review
- 出处：2026-06/07 写作流程沉淀；publish-final-check 演进耦合在 article-writing-guide/CHANGELOG.md；plagiarism-audit 针对实战漏网（Codex-book 整源漏审）设计；tech-article-review 与 review-doc 划边界（单 agent 逐段增量 vs 4 agent 并行）
- ~~edit-article~~：2026-08-11 复核用户未认领为自建，移出 Git 白名单（归 skill-install.md 待补来源）

### 学习 skill（自建 2 个，均已退役）
- ~~deep-learn / tutorial-maker~~：2026-09-03 随 skill 库精简批次卸载，移入 `~/.claude/backups/skill-trim-20260903/`（见 [skill-install.md](skill-install.md)「Skill 库精简（2026-09-03）」）。**该备份目录 2026-09-21 实测已不存在，恢复路径失效。**
- ~~cram-engine~~：2026-08-11 复核用户未认领为自建，移出 Git 白名单（归 skill-install.md 待补来源）

### ~~2026-08-11 复核新增自建（7 个，已入 Git 白名单）~~（2026-08-16 核实全不在磁盘，白名单已清）
- ~~ai-text-polisher / answer-evidence-finder / critical-thinking / doc-finder / humanizer-zh / interview-ai-agent-dev / interview-java-backend~~
- 出处：用户逐个勾选自认定稿（推翻此前「ignored 即第三方」的机器推断）。注：critical-thinking、humanizer-zh 公网存在同名项目，以用户判定为准——若实为改过/重写版本，建议日后在 SKILL.md 注明 fork 来源。
- **2026-08-16 审查实测**：7 个磁盘目录均不存在（疑 2026-08-13 清理随备份夹消失），`.gitignore` 白名单条目已移除；**恢复口径更正（2026-08-16 盘查）**：7 个全部存在于 `d57e5c0^`（28-skill 移备份批次的父提交），`git checkout d57e5c0^ -- skills/<名>` 即恢复，无需重建；ai-text-polisher 例外——已删、被 human-writing 替代，**不恢复**，见下文终判。critical-thinking 来源见 skill-install.md 更正。

### ~~ai-readable-project~~（2026-09-19 已删除，思想并入 instruction-auditor）
- 位置：`~/.claude/skills/ai-readable-project/`（SKILL.md + references/DESIGN.md + references/templates/ 3 模板）
- 出处：腾讯技术工程微信文章《从胡言乱语到精准改代码：我是如何让 AI 读懂老项目的》（AI 上下文工程）提炼；设计决策见 references/DESIGN.md
- 内容：让项目能被 AI 看懂——产出根 CLAUDE.md + AGENTS.md 知识索引 + 模块领域说明 + 长期维护规范；CLAUDE.md 用 `@AGENTS.md` 导入实现单源双生态（Claude Code 官方不读 AGENTS.md，只读 CLAUDE.md，@ 导入为官方推荐做法，不双写）
- 触发：显式（「让 AI 看懂这个项目 / 建 AGENTS.md」等）；纯独立不接 guide 路由
- 交付：分析报告 + 草稿到 `docs/ai-context/`，不直接改项目文件
- 依赖：无

### preflight-check（2026-08-14，全局）
- 位置：`~/.claude/skills/preflight-check/SKILL.md`（单文件）
- 出处：/insights 2026-08-14 friction #1（git add 错 repo root / JSON 引号断裂 / GBK 乱码）；「防方向错误」类 skill
- 内容：多步任务开工环境预检——repo root、目标路径存在性、文件编码、容器路径、shell 引号；只验证不执行，猜错即停
- 触发：多步任务/跨目录/容器路径/编码/shell 引号假设；code-change-workflow §1.1 已接线
- 依赖：无

### 前端 skill（历史自建，当前目录无对应 skill）
- shadcn-vue-guide（中文手写 + 本机 .bak 编辑痕）

### ai-coding-coach
- 学习陪跑模式（partner-coach/coach/engineer）；曾作为旧编码路由的协作行为定义

### ~~handoff / teach~~（更正 2026-08-07）
- **非自建**——磁盘上是 Matt 插件 symlink（指 plugins/cache），归 Matt 插件管，见 skill-install.md Matt Pocock 条目。之前误标自建。

### ~~obsidian-vault~~（2026-08-07 删除）
- 曾硬编码 wiki 路径（C:\ZYS\Code\wiki），用户拍板删除磁盘目录。若日后需要按 skill-install.md 散件检索重装。

### ~~ai-text-polisher~~（2026-08-16 终判：磁盘无、白名单已清）
- 2026-08-11 更正曾称「磁盘目录完整存在，已恢复 `.gitignore` 白名单追踪」**有误**：2026-08-16 审查实测磁盘无此目录、未追踪，白名单条目已移除；2026-08-08「删除，被 human-writing 替代」为有效终态。human-writing 用户未认领，归第三方。

### learning-guide 配套归档
- 学习记录归档流程，归档目录 `C:\ZYS\Wiki\80-records`（外部路径，迁移时另拷）

### ~~wiki-sediment + /wiki-save~~（2026-09-19 已删除，用户拍板）
- 位置：`~/.claude/skills/wiki-sediment/SKILL.md` + `~/.claude/commands/wiki-save.md`（全局，随 ~/.claude git 迁移——已加 .gitignore skills/ 白名单）
- 出处：spec `C:\ZYS\Wiki\docs\superpowers\specs\2026-08-11-wiki-sediment-design.md`（原 commit 3cdfb7e 为 wiki 项目级，同日用户拍板改全局）
- 内容：沉淀四路径（书籍→knowledge-note / 对话→learning-record / 错误→memory feedback / 仪表盘刷新），复用 wiki-structure 规约；wiki 目标路径硬编码 `C:\ZYS\Wiki`（迁机需改）
- 依赖：`C:\ZYS\Wiki` 的 wiki-structure skill、`93-templates/`、`scripts/refresh-due.py`

### /fy 翻译命令（2026-08-14，全局）
- 位置：`~/.claude/commands/fy.md`（全局自定义命令，单文件，随 ~/.claude git 迁移）
- **2026-09-21 实测：已不在本机**——`~/.claude/commands/` 已空，`fy.md` 不存在，也没有 skill 顶替。删除时间与原因未登记；同目录的 `dev-clean.md`、`dev-status.md` 是 2026-09-20 迁为 `-by-user` skill 的已知项，`fy.md` 不属于该批次，待用户确认是否有意删除。恢复：`git -C ~/.claude checkout -- commands/fy.md`。
- 出处：需求「/ 命令菜单描述看不懂，想要预翻译/实时翻译功能」→ 边界澄清后拍板做按需翻译命令。约束依据（官方 docs 已核）：内置命令/内置 skill 描述硬编码、无 i18n 无本地化、同名命令无法覆盖；`/` 菜单由 TUI 渲染、hook 无法改写显示。故「实时改菜单」形态不存在，能做的是「按需翻译」+「自有 skill 描述预翻译」（后者用户本次未选）。
- 内容：`/fy <英文>` 或 `/fy <粘贴的英文描述>` → 当前会话 Claude 直接翻成中文；只输出译文；输入已中文则原样返回并提示；空输入有提示。零依赖（走本会话 LLM，不配 API、无脚本）。
- 验证：重启会话后 `/` 菜单出现 /fy；`/fy /permissions` 或 `/fy statusline` 应返回中文说明。

### goal-run（目标自动续跑，2026-08-28，自 pi-goal 语义移植）
- 出处：pi-goal（pi 13 扩展包之一）语义 → CC 原生 ScheduleWakeup 封装；用户方向「pi 侧实现过的想法在 CC 复刻」。CC 侧对应能力：ScheduleWakeup + Monitor + run_in_background + /loop，本 skill 只定义行为契约（入口 4 项固化 / 空闲边界自续 / 三终结 goal_complete|blocked|wait / 安全上限 25 轮·3 次无进展即停·token 预算），不新增任何脚本或依赖。
- 构成：`~/.claude/skills/goal-run/SKILL.md` 单文件
- 验证：可被 Skill 工具显式调用（description 已出现在可用列表）；触发方式「/goal <目标>」或「自动续跑直到 X」
- 回退：删目录即回；未挂 settings.json，无全局副作用

### ~~cold-skills-index~~（2026-09-02 已删除）
- 出处：冷/深冻三阶技能治理移植（自 pi 三阶治理，2026-08-28）。
- 构成：曾为 `~/.claude/skills/cold-skills-index/SKILL.md` 单文件；冷技能为空，仅索引一个禁用插件。
- 处置：已物理删除 `~/.claude/skills/cold-skills-index/`，并移除 `.gitignore` 白名单；禁用插件状态继续由 `tool-install.md` 记录。
- 恢复：需重新确认冷/深冻索引仍有必要后，再从 Git 历史或备份内容恢复。

## hooks / statusline / 配置

### 2026-09-08 追加卸载 secret_guard.py
- 用户明确要求删除本地自定义敏感信息守卫。来源：本地自建／调整脚本，原始创建命令未留存；原位置 `~/.claude/hooks/secret_guard.py`，依赖 Python 标准库。
- 原生 Edit 移除 PostToolUse 命令组、PreToolUse 命令组及 MCP 组中的三个 secret_guard 注册；宿主 permissions 与插件开关未改。自动同步 cc-switch 两次均返回 `[DONE]`。
- 删除命令：`python312 -` 接收 PowerShell here-string；实际删除语句 `src.unlink()`，`src=Path('C:/Users/zys31/.claude/hooks/secret_guard.py')`。删除前只读核对 live/DB 均无引用，并逐字节比对备份。
- 备份：`C:/ZYS/Code/lab-area/exp/2026-09-08-hook-repair/pruned-six/secret_guard.py`。同目录 `test_before_secret_removal.py` 保存删除专属测试前版本。
- 保留：共享库、历史日志、状态数据及插件 hook；自定义密钥路径拦截与输出提醒不再提供。恢复需用户授权，从备份复制并重建三条注册后同步。
- Git guard 状态：此前备份曾被拒绝；用户随后再次授权，现已卸载，详见下方追加记录。

### 2026-09-08 追加卸载 git_guard.py
- 用户明确授权删除本地 Git／删除操作授权守卫；原位置 `~/.claude/hooks/git_guard.py`，来源为本地自建／调整，原始创建命令未留存，依赖 Python 标准库。
- 原生 Edit 移除最后一个本地 PreToolUse 注册组，自动同步 cc-switch 返回 `[DONE]`；宿主 permissions 和插件开关未改。
- 执行命令：`python312 -` 接收 PowerShell here-string，实际删除语句 `src.unlink()`，`src=Path('C:/Users/zys31/.claude/hooks/git_guard.py')`。删除前校验本地和 DB 无引用、文件与备份字节一致。
- 备份：`C:/ZYS/Code/lab-area/exp/2026-09-08-hook-repair/pruned-six/git_guard.py`；原 Git 测试归档为同目录 `test_git_guard_retired.py`。
- 本地剩余：`ecc-metrics-bridge.js`、`settings-sync-auto.py`、`settings-degrade-guard.py`，共 3 条注册；所有插件 hook、共享库、历史日志与状态保留。
- 测试收尾：此前更新被权限拒绝；用户再次授权后，已将 `hooks/tests/test_verification_hooks.py` 改为退休守卫文件缺失及注册清除检查，实跑 1/1 通过；实验目录卸载回归 6/6 通过。原 Git 行为测试保留在备份中，不将退休测试替换声称为修复原守卫缺陷。
- 恢复：仅在用户授权后复制备份回原位置，按历史 hook-baseline.json 恢复相应注册并同步 cc-switch。



### 2026-09-08 逐项讨论后精简六个本地 hook
- 授权：用户逐项确认删除，并最终确认执行；插件自带 hook 全部保留。
- 已卸载：`check-console-log.js`、`placeholder_guard.py`、`dep_gate.py`、`skill_ledger.py`、`verify_recorder.py`、`gateguard-destructive.js`。原位置均为 `~/.claude/hooks/`。
- 来源：`check-console-log.js`、`gateguard-destructive.js` 由第三方 ECC 剥离，本地维护；其余为本地自建／调整脚本，历史创建命令未完整留存。
- 配置：原生 Edit 移除六条注册及相应无内容的事件组；现有五个本地入口、七条注册保留，enabledPlugins 未改。每次配置 Edit 后 settings-sync-auto 回报 `[DONE]`。
- 执行：`python312 -` 接收 PowerShell here-string 脚本；删除语句为 `(root/'hooks'/name).unlink()`，`root=Path('C:/Users/zys31/.claude')`，name 遍历上述六个文件。删除前断言 settings 与 cc-switch common_config_claude 无对应注册，且脚本与备份逐字节一致。
- 脚本备份：`C:/ZYS/Code/lab-area/exp/2026-09-08-hook-repair/pruned-six/`；同目录 `hook-baseline.json` 保存卸载前注册及插件开关，不含 provider 凭据。
- 配置备份：`~/.claude/backups/settings-before-six-hook-prune-20260908-112215.json`。**2026-09-21 实测该文件已不存在，本条的恢复路径失效**；`~/.claude/backups/` 现只剩 `claude-md-slim-2026-09-19/`、`drawio-chart-embedded-git-2026-09-19/`、`skill-prune-2026-09-19/` 三项。同条目引用的 `~/.claude/hooks/HOOKS_BACKUP.md` 与 `hook-baseline.json` 亦需按上表复查。
- 保留：`git_guard.py`、`secret_guard.py`、`ecc-metrics-bridge.js`、`settings-sync-auto.py`、`settings-degrade-guard.py`；全部插件 hook、共享库、历史日志及状态数据。Python／Node 未卸载，权限规则未改。
- 验证：卸载回归 6/6 通过；本地与 cc-switch hooks、enabledPlugins 读回一致，剩 5 个入口、7 条本地注册。退休 recorder 的 6 个专属测试已移除，保留 4 个 Git／密钥守卫测试；后者实跑 3 通过、1 错误（组合 Git 命令授权预期与现行返回不一致，JSONDecodeError）。原测试备份也复现该问题，本轮未修改守卫实现或断言。
- 恢复：仅经用户授权后从备份复制脚本、按 hook-baseline.json 恢复相应注册并同步 cc-switch；不要整体覆盖当前 settings，以免回滚其他后续变更。


### 2026-09-08 卸载安装提醒与 MCP 健康检查 hook
- 用户明确要求删除 `install-ledger-reminder.py` 与 `mcp-health-check.js`。
- 来源：前者为本地自建命令正则识别／台账提醒 hook；后者由第三方 ECC 2.0.0 剥离为本地自维护脚本，历史来源见下方 ECC 卸载记录。
- 原位置：`~/.claude/hooks/install-ledger-reminder.py`、`~/.claude/hooks/mcp-health-check.js`。
- 配置操作：原生 Edit 移除 settings.json 中前者的 PostToolUse 注册、后者的 PreToolUse 与 PostToolUseFailure 注册；其他 hook 保留。每次 Edit 后 settings-sync-auto 均回报 cc-switch 同步 `[DONE]`。
- 删除命令：`python312 -`，通过 PowerShell here-string 输入 Python 脚本；实际删除语句为 `src.unlink()`，其中 `root=Path('C:/Users/zys31/.claude')`、`names=['install-ledger-reminder.py','mcp-health-check.js']`、`src=root/'hooks'/name`。执行前校验注册已移除，并执行 `shutil.copy2(src,dst)`、`assert src.read_bytes()==dst.read_bytes()` 校验备份。
- 备份：`C:/ZYS/Code/lab-area/exp/2026-09-08-hook-repair/uninstalled/` 下同名文件。
- 依赖与保留项：不卸载 Python/Node，不删除 hooks/lib 共享库、auto-log.jsonl、MCP 状态或历史台账；MCP 服务本体与注册不变。
- 验证：核对脚本缺失、settings.json 与 cc-switch common_config_claude 无对应命令；回归测试改为校验卸载状态，不再运行已退休 hook。
- 恢复：仅在用户要求恢复时，从上述备份复制回原位置，重建原事件注册并同步 cc-switch；卸载不影响 CLAUDE.md 的正式安装登记要求。


### ~/.claude/hooks/
- ecc 系 hooks（Fact-Forcing Gate / GateGuard 等）随 ecc 插件来；另有自建/调整个别脚本
- 备份：`~/.claude/hooks/HOOKS_BACKUP.md`（2026-09-21 实测该文件已不存在，仅存历史记载）
- **~~turn_counter.py~~ / ~~learning_nudge.py~~（2026-08-08 已删）**：曾为死代码（settings.json 未引用），2026-08-08 经用户确认物理删除；状态文件 `turn_state.json` / `learning_state.json` 同删。~~hooks/ 现有 settings.json 引用的 8 个 Python hook，另有 2 个未挂载的 dormant Python hook：`plugin_drift_check.py`、`skill_ledger.py`。~~（此句已过期）
- **hooks 现状（2026-09-21 实测，以此为准）**：磁盘 `~/.claude/hooks/` 下 7 个脚本被 `settings.json` 注册，合计 9 条注册——Python 4 个（`settings-degrade-guard.py`、`scripts/session-guard.py`、`scripts/product-guard.py`、`settings-sync-auto.py`）、Node 1 个（`ecc-metrics-bridge.js`）、PowerShell 2 个（`herdr-agent-state.ps1`、`claude-notify.ps1`）。未挂载的 dormant 脚本只剩 `plugin_drift_check.py` 一个；`skill_ledger.py` 已于 2026-09-08 卸载（见上方条目），磁盘无此文件。另有不注册为 hook 的工具脚本 `scripts/session-status.py`、`scripts/selftest.py`、`scripts/transcript_sweep.py` 与 `tests/`。
- **settings-degrade-guard.py（2026-08-13 新建）**：SessionStart 自动检测 cc-switch 切 provider 降级 settings.json（缺 statusLine/enabledPlugins/extraKnownMarketplaces/permissions.deny 或 >3 个 hook），从 cc-switch DB `common_config_claude` 快照并集合并恢复（保留 provider env），原子写+备份到 `~/.claude/backups/settings.bak-guard-<ts>.json`（2026-09-21 实测 `~/.claude/backups/` 下已无任何 `settings.bak-guard-*` 文件，历史自动备份已被清理）。静默运行，恢复时输出 JSON 提示。注册在 settings.json SessionStart `*` matcher。与 cc-switch-setting-sync skill 的 `--restore` 同源逻辑（见该 skill SKILL.md §4）。
- **skill_ledger.py（2026-08-17 新建；2026-09-08 已卸载，2026-09-21 复查磁盘无此文件）**：PostToolUse 记账 hook，matcher `Skill`。记 Skill 调用 → `~/.claude/metrics/skill-usage.log`（JSONL，坏输入/非 Skill 静默 exit(0) 不阻塞）。配 skill-trimmer 的 scan_skills.py 做使用计数（`load_usage()` 读它，剥 `plugin:` 前缀归一）。Python312 调用。**该 hook 已随 2026-09-08 六个本地 hook 精简批次卸载**（见上方条目），`settings.json` 与 cc-switch `common_config_claude` 均无注册，本段保留为历史。
- **hooks/scripts/transcript_sweep.py（2026-08-17 新建）**：周复盘脚本，非 hook（不进 settings.json）。扫最近 N 天会话 user 消息 → 去重/CJK 高频主题 → `~/.claude/metrics/transcript-weekly-YYYYMMDD.md`。纯 stdlib。周惯例手动跑：`python ~/.claude/hooks/scripts/transcript_sweep.py 7`。
- **2026-08-17 settings.json**：PostToolUse 末尾加独立 `Skill` matcher 分组（调 skill_ledger.py）；备份见常规 settings 快照。
- **2026-08-17 skill 修改（非新建，git 已追踪）**：code-change-workflow 加 §1.4.1「Agent 汇报核对清单」（JavaGuide Redis 案例）；skill-trimmer 加保鲜维度——scan_skills.py 每 skill 输出 `last_modified`/`usage_count`/`staleCandidate`（STALE_DAYS=180）+ SKILL.md 数据驱动段加「本机自动化三件套」命令引用。

### statusline（已脱离 ecc）
- 位置：`~/.claude/statusline`，含 cost + git 分支段（memory `statusline-independent-of-ecc`）
- 文件清单（2026-08-08 实测）：`statusline.js`（入口，settings.json statusLine 调它）+ `cost-tracker.js` + `context-monitor.js` + `metrics-bridge.js` + `lib/`（agent-data-home.js / session-bridge.js / utils.js）
- **2026-08-13 数据源剥离完成**：statusline 脚本早已独立，但其 cost/工具计数数据源（`post:ecc-metrics-bridge` hook 写 `/tmp/ecc-metrics-{session}.json`）此前仍绑 ecc 插件。已复制为自建 hook：`~/.claude/hooks/ecc-metrics-bridge.js` + `~/.claude/hooks/lib/`（agent-data-home.js / session-bridge.js / utils.js，ecc 版；require 路径已改 `./lib/`）。settings.json PostToolUse 已注册 `*` matcher 调它。验证：喂真实 session 数据 → bridge 文件生成 → statusline 输出含 `Nt 时长` 段。cc-switch `common_config_claude` 快照已同步。
- **2026-08-13 晚：ecc 插件整体卸载**（见下方「ecc 剥离/卸载」章节），原 `env.ECC_DISABLED_HOOKS`（禁 ecc 原版 metrics-bridge + gateguard）已随卸载删除。自建 metrics-bridge 是唯一 bridge 数据源，无双写问题。

### settings.json 关键本机配置
- `enabledPlugins` 清单快照见 tool-install.md
- `hooks` 现注册 6 类事件：`SessionStart`、`SessionEnd`、`PreToolUse`、`PostToolUse`、`Notification`、`StopFailure`（2026-09-21 实测）
- ~~lean-ctx 注入段在 CLAUDE.md 尾部（`<!-- lean-ctx -->` 包围，官方注入，别手改）~~ **失效**：lean-ctx 已于 2026-09-05 卸载，2026-09-21 实测 `~/.claude/CLAUDE.md` 内 `lean-ctx` 命中 0 处，无需再避让该段。
- `env.CLAUDE_CODE_AUTO_MODE_SERVER="0"`（2026-09-21 加）：告知 Claude Code 本机不请求服务端 auto mode 安全检查，消除「会话不合格」拦截通知。原因是请求经 `127.0.0.1:8787`（headroom）代理，服务端检查拿不到结果。计费行为不变（classifier 请求照旧按 token 计费）。该变量为官方临时配置，后续版本可能移除。**回退**：删 `env` 中该键即可。已随 settings-sync-auto 同步进 cc-switch `common_config_claude`（实测 DB 命中）。

## ecc 剥离/卸载（2026-08-13）

- **来源**：ecc 插件 2.0.0（`~/.claude/plugins/cache/ecc/ecc/2.0.0/`，市场源 affaan-m/ECC）。271 skills + 67 agents + 92 commands + 28 hooks 噪声大，用户拍板卸载，仅剥 3 个 hooks + 1 MCP 成自建。
- **剥离成自建**（复制自 ecc `scripts/`，均已改 require 指向 `./lib/`，不依赖 ecc 插件路径）：
  - `~/.claude/hooks/mcp-health-check.js`（零依赖；settings.json PreToolUse + PostToolUseFailure 注册）
  - `~/.claude/hooks/check-console-log.js`（require `./lib/utils`，复用已有 hooks/lib/utils.js；Stop 注册）
  - `~/.claude/hooks/gateguard-destructive.js`（原 ecc `gateguard-fact-force.js` 复制改名 + 加自执行入口；require `./lib/shell-substitution`；PreToolUse Bash 注册）——**只留 destructive 门**（rm -rf / reset --hard / force push / find -exec 等），Edit/Write 事实门与 routine Bash 门不保留（routine 靠 `env.GATEGUARD_BASH_ROUTINE_DISABLED=1` 关）
    - **2026-09-05 修正**：当时台账称 Write 门已裁，实际裁剪不完全——hook 源码 Write 首建事实门仍在，且 settings.json Edit|Write matcher 里也注册着此 hook，会话中被拦 4 次。当日已从 Edit|Write matcher 摘除该注册（hook 文件未动，Bash 注册保留），settings.json 变更已自动同步 cc-switch DB。Write 门从此仅存于 hook 源码，未注册不生效。
    - **2026-09-05 补充**：同日用户确认后彻底清除 hook 源码内 Edit/Write/MultiEdit 事实门死代码（分支 + editGateMsg/writeGateMsg/condensedGateMsg/getFullDenialBudget/markCheckedAndCountDenial/sanitizePath/EDIT_WRITE_HOOK_ID），denyResult 默认 hookId 改为 BASH_HOOK_ID。行为不变：destructive 与 routine Bash 门保留，实测 deny→retry→allow 与 Write/Edit 透传均通过。
  - `~/.claude/hooks/lib/shell-substitution.js`（零依赖）
  - 未剥离：format-typecheck / suggest-compact / memory-persistence（用户不要，随 ecc 消失）
- **MCP**：chrome-devtools 独立保留 → `claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest`（写入 `~/.claude.json` 顶层 mcpServers，user scope；原 ecc `.mcp.json` 定义）。**注意**：settings.json 顶层不支持 `mcpServers`（死配置，官方确认），别放那。**2026-09-21 状态**：chrome-devtools 已于 2026-09-07 卸载（见 [mcp-install.md](mcp-install.md)），当前 `~/.claude.json` 顶层 `mcpServers` 只剩 `headroom` 一条；关于 settings.json 不支持 mcpServers 的注意事项仍然有效。
- **settings.json 变更**：`ecc@ecc:false`；删 `ECC_DISABLED_HOOKS`；加 `GATEGUARD_BASH_ROUTINE_DISABLED=1`；PreToolUse Bash 加 gateguard-destructive + mcp-health-check；PostToolUseFailure 加 mcp-health-check；Stop 加 check-console-log。备份 `settings.json.bak-ecc-rm-20260813`（更早 `settings.json.bak-ecc-20260813` 在卸载前；**注意该备份含死配置 mcpServers 段，回退时删掉**）。
- **卸载**：`claude plugin uninstall ecc@ecc`（2026-08-13）。缓存 `plugins/cache/ecc/` 目录残留（未删，留作回退对照）。
- **marketplace 删除**（2026-08-13）：`claude plugin marketplace remove ecc`（市场源 affaan-m/ECC），登记 + 缓存 `plugins/marketplaces/ecc/` 一并清除，其余 11 个 marketplace 不受影响。`~/.claude.json` 的 `ecc@ecc`/`ecc@inline` pluginUsage 统计段已手术式清除（Python 字节级替换 + JSON 校验通过）。
- **依赖**：gateguard-destructive 需 `~/.claude/hooks/lib/shell-substitution.js`；check-console-log 需 `hooks/lib/utils.js`（已有）。gateguard 状态文件 `~/.gateguard/`（会话记忆，无害）。
- **回退**：`claude plugin install ecc@ecc` + 还原 `settings.json.bak-ecc-rm-20260813`（保留 settings 自建 hooks 需再评估是否与新装 ecc 冲突）。cc-switch 同步备份 `~/.cc-switch/backups/sync-backup-20260813_142504.json`。

### CLAUDE.md 本身
- 2026-07-29 瘦身至 ~8.3KB，备份 `CLAUDE.md.bak-20260729`
- 常驻硬约束在 §1；装后登记规则见 §1 最后一行（installing/ 本台账）

### wiki-course-tutor（2026-09-02，Wiki 项目级）
- 出处：基于本地 OpenMAIC `C:\ZYS\Code\lab-area\OpenMAIC\skills\openmaic\SKILL.md` 与 `references/generate-flow.md` 提炼；吸收课程场景、互动、PBL、分阶段推进和状态处理，改为 Wiki 纯文字教学流程。
- 位置：`C:\ZYS\Wiki\.claude\skills\wiki-course-tutor\SKILL.md`
- 内容：规划、课堂、验收、沉淀四种模式；源教程事实边界；单轮互动；最小实操；失败/边界测试；换场景迁移；learning-record 草稿规则。
- 依赖：Wiki `AGENTS.md`、`wiki-structure` 规约和源教程原文；无 OpenMAIC 运行时、API Key 或外部服务依赖。
- 验证：检查 SKILL.md frontmatter、源依据和 Wiki 状态/证据约束；`git diff --check` 通过。
- 回退：删除 `C:\ZYS\Wiki\.claude\skills\wiki-course-tutor\`，并移除本登记项；不涉及 OpenMAIC、Wiki 知识正文或全局配置。


## Claude Code → Codex CLI 配置迁移（2026-08-25 前后，精确日期与任务源待补）

**背景**：把 Claude Code 配置生态（规则/skills/hooks/MCP）搬到 Codex CLI，过渡期并存，最终卸掉 Claude Code。claude 侧零改动（指纹对比：settings.json 一致；skills 目录 21:00 后 mtime 零变化；.claude.json 变化来自运行中的 claude.exe 自身写入）。

**认证**：cc-switch GUI 切 codex app → OpenAI Official（领导手动）；`codex login` 浏览器授权一次（领导手动），~/.codex/auth.json 21:24 写入。doctor auth ✓。

**AGENTS.md**：~/.codex/AGENTS.md 由 ~/.claude/CLAUDE.md 转换（删 claude 特有：/goal、slash commands、statusline、marketplace；保留决策分层/人工确认线/代码质量/验证交付；注明来源与日期）。验收：exec 输出含「人工确认线」「决策分层」；反向验证改名→FILE_NOT_FOUND，还原→恢复。

**skills**：31 自建 skill 目录拷入 ~/.codex/skills/（源 ~/.claude/skills/，排除 -workspace、manifest.json、README.md、lean-ctx、learned）。SKILL.md frontmatter 全部校验通过。codex exec 问出可见 skills ≥31（见 PROGRESS.md 验收输出）。

**hooks**（~/.codex/hooks.json + ~/.codex/hooks/）：
- secret_guard.py / edited_tracker.py / verify_recorder.py 拷自 ~/.claude/hooks/，state path 改 ~/.codex/hooks/，python 用 C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe
- 兼容性修两处：① codex 的 Bash tool_response 是**字符串**非 dict（.get("stdout") 会抛异常导致 PostToolUse hook Failed）→ secret_guard/verify_recorder 已加 isinstance(resp,str) 分支；② codex 编辑工具名是 **apply_patch** 非 Edit/Write → edited_tracker matcher 改 Edit|Write|apply_patch，并从 patch 文本（*** Add/Update/Rename File:）解析路径
- edited_tracker 的 SessionStart 挂载须单独 matcher 组（与 lean-ctx 合并同组会被 codex 重写 hooks.json 时冲掉）
- lean-ctx observe/codex-pretooluse/codex-session-start 按官方 codex onboard 装（保留在 hooks.json）
- ecc-metrics-bridge 不迁（ecc 已卸载）
- 验收：红→绿→还原全过（secret_guard 拦 sk- 输出模型引述警告原文 → 禁用后 NO HOOK WARNING → 还原后警告恢复；verify_recorder 记录 verify_cmds；edited_tracker 记录编辑路径）
- 待领导：codex `/hooks` 批准 trust（当前 exec 需 --dangerously-bypass-hook-trust）

**MCP**（config.toml [mcp_servers]）：gitnexus = npx -y gitnexus@latest mcp；chrome-devtools = cmd /c npx -y chrome-devtools-mcp@latest；lean-ctx = C:/Users/zys31/.cargo/bin/lean-ctx.exe + LEAN_CTX_DATA_DIR env。`codex mcp list` 3 个 enabled。config.toml 备份 config.toml.bak-20260825-mcp。

**回退**：删 ~/.codex/ 下 AGENTS.md、skills/、hooks.json、hooks/、config.toml 的 mcp_servers 段即可；claude 侧无任何改动无需回退。

## Codex CLI 卸载（2026-08-26，任务源 exp/2026-08-26-purge-codex/）

**范围**：卸载 npm 全局包 @openai/codex@0.149.1 + 整个 ~/.codex/ 移回收站（可撤销，未彻底删）。**保留**：~/.cc-switch/ 全部（cc-switch.db、codex_oauth_auth.json、settings.json）——cc-switch 的 codex 账号/登录配置不动。

**命令**：`npm uninstall -g @openai/codex`（removed 2 packages）；~/.codex 移回收站用 scripts/trash_codex.py（SHFileOperationW FOF_ALLOWUNDO，Python 标准库 ctypes）。

**验证**：where codex 无结果；npm ls -g 无 @openai/codex；~/.codex 不存在；~/.cc-switch/ 三文件完好。PowerShell profile 无 codex 引用，无需清理。

**残留复查（2026-08-26）**：① ~/.codex 实占 **约 2.8GB**（du 漏算 .tmp/marketplaces 2466MB，回收站确认 $R3O40KE.codex），回收站保留可恢复；② %TEMP% 下 11 个 codex-* 调试残留（迁移期遗留，127K）已删；③ 其他 codex 引用均为他软件自身文件非残留：npm-cache _npx/ 内 loopforge-cli/claude-mem 的 .codex 适配、~/plugins/*.codex-plugin 元数据、deeptutor(deeptutor_web) 的 codex provider 代码、herdr agent-detection codex.toml。

**恢复路径**：如需重装，`npm i -g @openai/codex` + 从 cc-switch GUI 切 codex app 写回登录（~/.codex/ 整个被删，需重建配置）。

## bidirectional-steelman（2026-08-31，全局）

- **出处**：从 `~/.claude/CLAUDE.md` 原“双向钢人论证”规则拆分；用户确认独立 skill 化，保留全局自动触发路由。
- **位置**：`~/.claude/skills/bidirectional-steelman/SKILL.md`；`.gitignore` 已加入自建 skill 白名单。
- **内容**：决策/判断/选型/取舍分析的四步方法、正反双方钢人化、关键变量、输出格式、纯执行跳过和“直接给/别折腾”绕过。
- **依赖**：无；Markdown 单文件。
- **验证**：检查 SKILL.md frontmatter、触发/跳过条件、全局路由引用和 Git 白名单。
- **回退**：恢复 `CLAUDE.md` 原规则，删除 skill 目录、`.gitignore` 白名单行和本登记项。

### parallel-delegation（2026-08-31，全局）

- **出处**：用户提供文章 https://mp.weixin.qq.com/s?__biz=MzE5ODc3Njc0NQ==&mid=2247484429&idx=1&sn=1cb67d6c6baa4f7f12a11710e7b5e623&chksm=9701ac8f1625d8eb8116f3752109735f119d89b2badacb8f648938228efc300e57be9bc8e6f5&mpshare=1&scene=1&srcid=0831RMVutN6h4pVnxAhC0ON6&sharer_shareinfo=fb8307e673915c06c1ce7c6d2eb36718&sharer_shareinfo_first=fb8307e673915c06c1ce7c6d2eb36718#rd；抽取为不绑定模型、供应商、推理档位和固定并发的通用执行层。
- **位置**：`~/.claude/skills/parallel-delegation/SKILL.md`；Windows 使用复制，不使用 symlink；`.gitignore` 已加入 `!skills/parallel-delegation/` 白名单。
- **内容**：主代理拆解、隔离和最终验收；worker 按 handoff 契约执行；读操作可并行，写操作需隔离或不重叠；失败、冲突、阻塞和越界结果不算总完成。
- **依赖**：宿主提供 agent/subagent 调度能力；模型覆盖、并发和 worktree/隔离能力按运行时实际支持处理；无脚本/API 依赖。
- **接线**：当前不依赖编码域总入口；不修改 `settings.json`，不替代 `/to-tickets` 或交付状态机。
- **验证**：实验版 `evals/evals.json` 已覆盖独立任务拆解、读写隔离和单文件不触发；历史路由评估用例已随旧编码总入口删除。
- **回退**：删除 `~/.claude/skills/parallel-delegation/` 即可；不涉及其他 skill、全局配置或实验数据。

### improver-skill（由 wiki-skill 改名，2026-08-31，全局）
- **出处**：依据 Google WikiSkill 论文设计的本地轻量实现；源文件来自 `C:\ZYS\Code\lab-area\.claude\skills\wiki-skill\SKILL.md` 与 `C:\ZYS\Code\lab-area\exp\2026-08-31-wikiskill\wikiskill.py`。
- **位置**：`~/.claude/skills/improver-skill/`，包含 `SKILL.md` 与 `wikiskill.py`；Windows 使用复制，不使用 symlink。
- **内容**：手动驱动 Raw Trace、Wiki Pattern、候选 Skill 和轻量 gate；Raw Trace 不可覆盖，Wiki 追加保留，候选拒绝不回滚 Wiki，候选基线 hash 防止过期 Skill 覆盖当前 active。
- **依赖**：Python 3.12 标准库；不依赖模型、API、Hook 或 `skill-up`。
- **触发**：手动调用 `improver-skill`；当前为手动流程，不修改 `settings.json`，不自动写入 `C:\ZYS\Wiki`。
- **验证**：全局 `wikiskill.py` 编译通过；实验版 `test_wikiskill.py` 6 个测试通过；CLI `--help` 可用。
- **回退**：删除 `~/.claude/skills/improver-skill/` 即可；不涉及全局配置、Hook、官方 `alibaba/skill-up` 或 Wiki 数据。

### install-ledger（2026-09-02，全局）

- **出处**：针对安装台账分散、当前状态与历史记录混写、自然语言触发不稳定的问题新建；用户确认作为自建 skill。
- **位置**：`~/.claude/skills/install-ledger/SKILL.md`；`.gitignore` 已加入 `!skills/install-ledger/` 白名单。
- **内容**：统一四类台账职责、来源与当前状态取证、用户归属确认、历史保留、最小差异修改和验收输出。
- **依赖**：无额外运行时依赖；使用宿主提供的文件读取、状态核验和 Git 工具。
- **触发**：显式 `/install-ledger`，或明确提出整理、登记、核对安装台账；不接管普通安装/卸载任务。
- **验证**：已检查 frontmatter、触发边界、台账分工和最小验收场景；实际运行验证待本次台账整理完成后执行。
- **回退**：删除 `~/.claude/skills/install-ledger/` 与 `.gitignore` 白名单行，并移除本登记项；不涉及其他 skill 或配置。

---

## 全局配置收窄+skill 沉淀（2026-09-08，三方观点审计落地第一份）

- **依据**：`C:\ZYS\Code\lab-area\exp\2026-09-08-wechat-audit\landing-plan.md`（三篇微信文章 24 条观点逐条确认，领导 2026-09-08 拍板）；执行任务书同目录。
- **改动 1**：`~/CLAUDE.md`——§0 加 PRIORITY 行（用户显式指令 > 本文件 > skills，被规则卡住须报文件+原文）；§1.1 首条改「常规缺口自行假设并继续」语义、矛盾条改「裁决后继续」；§2.4 按三问删 2 条（ctx_compose 死引用、上下文压缩 harness 职责）。**§1.3 确认线收窄编辑被 auto mode classifier 拦截，旧版仍在，待领导裁决（见 BLOCKED.md B1）**。
- **改动 2**：`~/skills/skill-auditor/SKILL.md` v2.0.0→v2.1.0——十查后新增「渐进披露追加检查」11/12 两查+反模式 1 条；原十查未动。
- **改动 3**：`~/skills/ai-readable-project/`——AGENTS-template.md 知识索引段加六类骨架注释+新增「### 边界与验证」（IBV）；SKILL.md 维护规则加根入口 ≤120 行预算条。
- **验证**：各文件验收命令+反向验证（红→绿）全过；skill-auditor 187 行、ai-readable-project 95 行、CLAUDE.md 153 行（收窄未落地，行数待 §1.3 落地后复核）；两 skill 新 description 已被宿主热加载（会话内实证）。
- **回退**：`git -C ~/.claude checkout -- <文件>` 逐文件还原到 479ea70（未 commit，工作区 diff 即全部改动）。

---

## skill 库整库审计+渐进披露改造（2026-09-08，landing-plan 批次 3）

- **依据**：`C:\ZYS\Code\lab-area\exp\2026-09-08-wechat-audit\landing-plan.md` 批次 3；执行任务书同目录（第二份）；审计规程 `~/skills/skill-auditor/SKILL.md` v2.1.0（静态十查+渐进披露 11/12）。
- **审计**：22/22 自建 skill 逐个过 v2.1.0，一行结论见工件目录 `audit-report.md`（22 行 wc 基线+P0×1/P1×4/P2 若干+结构扫描表）。
- **修复 4 个**（入口改写为最小路由器，内容按主题下沉 references/；触发边界/输入输出契约/验证闭环/风险确认点保留在入口；description 逐字节未动）：
  1. `article-writer` 783→193 行；新增 `references/style-craft.md`、`human-writing.md`、`javaguide-style.md`、`ai-writing-discipline.md`
  2. `drawio-chart` 594→195 行；新增 `references/color-tokens.md`、`xml-templates.md`、`cli-export.md`、`layout-principles.md`
  3. `drawio-article-illustration` 233→185 行；新增 `references/chart-type-checklists.md`；其对 drawio-chart 的 §二 引用同步改新路径
  4. `skill-trimmer` 216→194 行；新增 `references/evidence-sources.md`（~/.pi 死路径原文保留，处置见 BLOCKED B3-4）
- **验证**：每个修复对象 wc ≤200、`grep -c "references/"` ≥1、反向验证（入口路由行临时改名 grep=0 → 还原 grep≥1，cmp 逐字节一致）、frontmatter（含 description）与改前备份逐字节一致、十查自检全 PASS、第一跳 3 场景×4 与修复前判定一致（无触发漂移）。全部证据录 `audit-report.md`。
- **回滚**：改前备份在 `C:\ZYS\Code\lab-area\exp\2026-09-08-wechat-audit\bak\<skill名>-SKILL.md`，复制回 `~/.claude/skills/<skill名>/SKILL.md` 即还原；新增 references 文件可按需删除。
- **遗留**：见工件目录 `BLOCKED.md` 批次 3 节（code-change-workflow 幻觉目标 P0、bili-note/.codex 与 wiki-sediment/.pi 与 skill-trimmer/.pi 死路径、examples 死接线、bili-note 与 generic-course-tutor 超行未修）。

---

### Claude Code Windows Toast 点击无动作（2026-09-10，全局）

- **来源**：本地自建；用户要求区分 VS Code／Windows Terminal、覆盖输入／决定／工具错误／API 错误／回复完成，并最终选择点击不执行动作。
- **位置**：通知入口 `~/.claude/hooks/claude-notify.ps1`；空操作启动器 `~/.claude/hooks/claude-notify-focus.vbs`；当前用户协议 `HKCU\Software\Classes\claude-notify`。
- **安装命令原文**：先注册协议：`MSYS_NO_PATHCONV=1 reg.exe add 'HKCU\Software\Classes\claude-notify' /ve /d 'URL:Claude Notify Focus Protocol' /f && MSYS_NO_PATHCONV=1 reg.exe add 'HKCU\Software\Classes\claude-notify' /v 'URL Protocol' /d '' /f && MSYS_NO_PATHCONV=1 reg.exe add 'HKCU\Software\Classes\claude-notify\shell\open\command' /ve /d 'powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\zys31\.claude\hooks\claude-notify-focus.ps1" "%1"' /f`；最终处理命令改为：`MSYS_NO_PATHCONV=1 reg.exe add 'HKCU\Software\Classes\claude-notify\shell\open\command' /ve /d 'wscript.exe "C:\Users\zys31\.claude\hooks\claude-notify-focus.vbs" "%1"' /f`。脚本由 Claude Code 原生 Write/Edit 写入。
- **行为**：Toast 使用宿主 AppUserModelID 和 `claude-notify://dismiss`；VBS 立即退出，因此点击无白框、无跳转、无新窗口。通知脚本仅按 VS Code 环境变量识别宿主，不遍历进程、不调用 `user32.dll`、不动态 `Add-Type`，也不再尝试前台窗口抑制。`StopFailure.error` 按 `server_error`、`authentication_failed`、`billing_error`、`rate_limit`、`cloud_credential_error`、`unknown` 分别生成准确文案。
- **安全处置**：前台抑制实验在隐藏合成测试中被卡巴斯基行为分析报为 `PDM:Trojan.Win32.Generic`，主脚本被删除；用户确认后以最简版本重建，并执行 `Remove-Item -LiteralPath 'C:\Users\zys31\.claude\hooks\claude-notify-focus.ps1' -Force -Confirm:$false` 删除停用的聚焦脚本。四条通知 hook 同时移除不必要的 `-ExecutionPolicy Bypass`。不要恢复该实验脚本或直接添加杀软白名单。
- **依赖**：Windows PowerShell 5.1、Windows WinRT Toast、系统自带 `wscript.exe`、当前用户注册表写权限；无第三方包。
- **验证**：重建脚本 Parser 为 0 错误；静态核对无 `Add-Type`、进程遍历或 `user32.dll`；settings.json 可解析且包含 Notification／PostToolUseFailure／StopFailure／Stop，四条命令均不含 `Bypass`；注册表逐字读回为 `wscript.exe "C:\Users\zys31\.claude\hooks\claude-notify-focus.vbs" "%1"`；无 Bypass 空输入启动退出码 0。重建后的自然 Stop 通知和卡巴斯基行为仍需观察。
- **回退**：经删除确认后，在 Git Bash 执行 `MSYS_NO_PATHCONV=1 reg.exe delete 'HKCU\Software\Classes\claude-notify' /f`，删除 `claude-notify-focus.vbs`，并从 settings.json 移除四类通知 hook；不要只删通知脚本而留下失效注册。


### code-change-workflow 1.1.0 维护资产（2026-09-12，全局）
- **来源**：`C:\ZYS\Code\lab-area\exp\2026-09-11-claude-workflow-harness\` 任务书执行；只动白名单内路径。
- **新增/修改**：`~/.claude/skills/code-change-workflow/CHANGELOG.md`（1.0.0 追认 + 1.1.0）、`references/MAINTENANCE.md`（版本规则/改动流程/eval 跑法/验证边界，36 行）；`SKILL.md` 仅两处追加（frontmatter `version: 1.1.0`、末尾维护入口一行；diff 对实验目录 baseline-SKILL.md 仅两处）；`evals/eval.yaml` 仅 model 改 claude-haiku-4-5；`evals/cases/` 新增 research-no-route.yaml、delivery-evidence.yaml、missing-acceptance.yaml，bug-fix/vague-feature 两冻结 case sha256 不变。
- **验证**：fixture 红→绿闭环（过期 token 500→401，双 PASS，含反向 FAIL→还原 PASS，test_fixture.py sha256 `083d1a0f…337fa` 不变）；5 case 零依赖结构自检 PASS，删 judge 键反向验证 FAIL；evidence-bundle.postfix.json（schema v3）实证 pluginAssets=5 是资产面数（plugins/skills/agents/hooks/mcps 五面，8/52/7/8/2 项），enabledPluginCount=8 是启用插件实例数；5 findings 处置见实验目录 FINDINGS-DISPOSITION.md。
- **未验证/阻塞**：自然语言自动触发 unknown（headless `-p` 不注入 skill 清单，双探针一致）；`claude plugin eval` 被组织 early-access gate 拦截；3 个新 case 尚未登记进 eval.yaml 的 cases.files（白名单仅限改 model），见实验目录 BLOCKED.md。
- **回退**：删 CHANGELOG.md、references/MAINTENANCE.md 与 3 个新 case；SKILL.md 按实验目录 baseline-SKILL.md 恢复；eval.yaml model 恢复 claude-sonnet-4-6。实验材料保留不删。

### code-change-workflow evals 迁移官方 runner 布局（2026-09-12，全局）
- **来源**：同上实验验收暗卷；用户授权「迁移并实跑，全绿后删旧文件（先存档）」。
- **背景**：CLI 自动更新至 2.1.269（二进制 `claude.exe`，03:32），eval early-access 门消失；实测旧 `eval.yaml + cases/*.yaml` 布局 runner 发现 0 case（新发现规则 `evals/**/case.yaml|prompt.md + graders/*.md`）。
- **新增/修改**：`evals/<5 case>/case.yaml`（regex grader，判词贴 SKILL.md 原词）；bug-fix、delivery-evidence 各配 `scaffold.sh` 落 fixture；删除 `evals/eval.yaml` 与 `evals/cases/`（删前 6 文件 sha256 与实验目录 `evals-legacy-archive/` 逐一核对一致）；CHANGELOG.md 加资产更新段（不 bump 版本，SKILL.md 零改动）；references/MAINTENANCE.md 更新 evals 跑法与自动触发证据。
- **验证**：`claude plugin eval . --scaffold --allow-tools Edit --ablation none --runs 1 --no-publish --trust-plugin` 全量 5/5 绿（258s，$0.17）；research-no-route `--runs 3` 3/3；trace 证实 Skill 自动触发（首工具即 Skill）。证据：实验目录 `eval-runner-evidence/`（aggregate-result.json + report.html）。
- **关键机制**：`add_dirs` 只授读不复制（fixture 必须走 scaffold_script）；Edit 要运行时 `--allow-tools` grant；`evals/results/` 是可再生产物（删除被安全门拦，现保留在 skill 目录，待用户裁）。
- **回退**：case 目录从 `evals-legacy-archive/` 恢复旧布局（但旧布局在 2.1.269 下不可运行，仅留档用）；文档改动按本实验报告对照撤回。

### instruction-auditor（2026-09-14，全局）
- **出处**：用户指定 OpenAI 官方文章《Rethinking skills and prompts for GPT-6 Astra》作为设计依据；用于统一审查指令文件中的触发、重复/冲突、资料读取、等待和完成标准。
- **位置**：`~/.claude/skills/instruction-auditor/SKILL.md`；自建单文件 Skill。
- **内容**：只审查用户明确纳入的自建 `SKILL.md`、`CLAUDE.md` 和 `AGENTS.md`；只输出证据分层的审查报告与最小 diff，不自动修改。
- **依赖**：无外部运行时依赖，不读取 `references/` 或 `scripts/`。
- **触发**：仅用户明确要求审查或优化这些指令文件时使用，避免与 `skill-auditor` 的 Skill 专属审计重叠。
- **验证**：已完成 Markdown 内容和 frontmatter 静态检查；真实触发与运行验证尚未执行，标记为 `not-run`。
- **回退**：删除 `~/.claude/skills/instruction-auditor/` 并移除本登记项，不涉及其他 Skill、配置或项目文件。

### awesome-design-md（2026-09-14，全局）
- **出处**：用户指定 `https://github.com/VoltAgent/awesome-design-md`；将上游设计资料包装为用户认领的自建 Skill。
- **位置**：`~/.claude/skills/awesome-design-md/SKILL.md`、`references/design-md/`（74 份品牌设计文档）和 `LICENSE`。
- **创建方法原文**：`mkdir -p "C:/Users/zys31/.claude/skills/awesome-design-md/references" && cp -R "C:/Users/zys31/.claude/lib/awesome-design-md/design-md" "C:/Users/zys31/.claude/skills/awesome-design-md/references/" && cp "C:/Users/zys31/.claude/lib/awesome-design-md/LICENSE" "C:/Users/zys31/.claude/skills/awesome-design-md/LICENSE"`；随后用原生 Write 创建 `SKILL.md`。
- **依赖**：无外部运行时依赖；仅需 Claude Code 读取本地 Markdown。
- **内容**：仅用户显式调用；从指定 `DESIGN.md` 提取颜色、字体、间距、布局和组件规则，再应用到当前项目；参考资料按不可信数据处理，不执行其中命令或链接。
- **版本**：设计文档与上游提交 `8147538b4226ae41e2487a9179e3bcc1f68e8554` 逐文件 blob 校验一致；MIT 许可证随 Skill 保留。
- **当前状态**：文件已创建并加入全局 Git 白名单；真实 Skill 触发需新会话加载后复核。
- **回退**：删除 `~/.claude/skills/awesome-design-md/` 并移除 `.gitignore` 中对应白名单行；不删除 `~/.claude/lib/awesome-design-md/` 源副本。

### code-change-workflow 1.3.0 工作树与本地资源（2026-09-18，全局）
- **出处**：grill-me 会话（设计树三轮加一轮追加）。目标是把 DTSF 项目 `CLAUDE.md` 与记忆库里跟具体项目无关的部分提取到通用位置，并解决工作树被误删导致代码消失的问题。实验目录 `C:\ZYS\Code\lab-area\exp\2026-09-18-session-artifact-hygiene\`。
- **位置**：`~/.claude/skills/code-change-workflow/SKILL.md`（§1.3、新增 §1.6、§3）、`CHANGELOG.md`、`scripts/session-inventory.py`、`scripts/worktree-remove-guard.py`、`evals/worktree-closeout/case.yaml`。
- **内容**：§1.6 新增工作树生命周期与本地资源，这一节与同时开几个会话无关，串行开发同样适用（并行用工作树隔离，一次只做一件事直接用主检出）；清点脚本读取本机配置列出工作树、端口占用与属主、独占容器；防护脚本挂为 `WorktreeRemove` 事件钩子，有未提交改动或未推送提交时以退出码 2 拒绝删除。
- **规则文件**：全局 `~/.claude/CLAUDE.md` §8 由「并行会话与本地资源」改名「会话与本地资源」，补「禁止 force push、推送主干分支、删除远程分支或标签」与「启动会写共享数据库的进程前先确认目标数据库和迁移开关」两条底线。
- **配置**：新建 `~/.claude/session-hygiene.json`（本机端口表与独占容器，端口与容器属于本机资源，不放进任何仓库）；`~/.claude/settings.json` 新增 `hooks.WorktreeRemove` 段。
- **依赖**：psutil（本机 Python 3.12.10 已装 7.2.2）；钩子命令使用绝对解释器路径 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`，换机器需要改这一行。
- **验证**：清点脚本在 DTSF 实跑通过，输出 20 个工作树、18 条 stash、11 条无远端分支、7 个端口的占用与属主、2 个独占容器的状态；防护脚本在独立临时仓库夹具跑 6 条用例全部通过。实测修正两处自身缺陷：中文列宽按字符数补空格错位、钩子写标准错误时未设 UTF-8。详见 `CHANGELOG.md` 1.3.0 条目。
- **未验证**：钩子在会话退出、子代理结束、删除后台会话三条真实清理路径上的触发；`ExitWorktree` 中途主动退出已实测不经过该钩子。钩子放行之后由谁执行删除尚未确认。
- **回退**：`SKILL.md` 与 `CHANGELOG.md` 恢复到 1.2.0 内容，删除 `scripts/` 与 `evals/worktree-closeout/`，移除 `~/.claude/settings.json` 的 `hooks.WorktreeRemove` 段；`~/.claude/session-hygiene.json` 可保留（清点脚本读不到时会跳过这两节）。

### toolchain-pitfalls（2026-09-18，全局）
- **出处**：从 DTSF 项目记忆库 `~/.claude/projects/C--ZYS-Code-dtsf/memory/` 复制出的通用工具链坑，含 MSYS 路径转换、PowerShell 引号提前展开、代码页与输出编码、包装器与可执行文件、工作树与子代理机制。
- **位置**：`~/.claude/skills/toolchain-pitfalls/SKILL.md`；自建单文件 Skill。
- **内容**：按路径与引号、编码与输出、脚本与解析、工作树与子代理四节列出坑位与当时的判据。2026-09-18 审查后删掉「不要手写成熟文件格式的解析器」（与全局 `CLAUDE.md` §2.1 逐字重复）与整节「触碰边界」（属敏感数据处理规则，已有对应 memory），并收录 Windows 父进程退出不连带终止子进程一条。
- **依赖**：无外部运行时依赖。
- **验证**：内容静态检查通过；其中「Python 输出非 ASCII 内容前先设编码」一条在本次实验中再次实测复现——脚本未设编码时，宿主读到的是系统代码页字节。
- **回退**：删除 `~/.claude/skills/toolchain-pitfalls/` 并移除本登记项。memory 侧对应条目已于 2026-09-18 删除，回退需从会话记录还原。

### code-change-workflow 1.4.0 按审查收敛（2026-09-18，全局）
- **出处**：独立子代理对 1.3.0 新增内容的逐条审查（必要性、合理性、与既有规则是否重复）。审查对象为全局 `CLAUDE.md` §8、`SKILL.md` §1.3/§1.6/§3、`CHANGELOG.md`、`toolchain-pitfalls/SKILL.md`、`session-inventory.py`、`session-hygiene.json`、`settings.json` 的 `WorktreeRemove` 挂钩。
- **位置**：`~/.claude/skills/code-change-workflow/SKILL.md`（1.4.0）、`CHANGELOG.md`、`scripts/session-inventory.py`、`~/.claude/skills/toolchain-pitfalls/SKILL.md`、`~/.claude/CLAUDE.md`（无改动，§8 八条审查后全部保留）。
- **内容**：删掉 `scripts/worktree-remove-guard.py` 与 `settings.json` 的 `hooks.WorktreeRemove` 段——宿主清理工作树前自己会检查未提交改动与未推送提交，钩子重复了这套判断，且曾因按载荷字段顺序取到会话的 `cwd` 而误判主检出、静默放行。§1.6 删掉五条与全局 `CLAUDE.md` §8 或 DTSF 项目 `CLAUDE.md` 重复的条目，删掉源自 DTSF 的 Git 协作小节；「删错了怎么找回」按实测改写。§1.3「页面提示不代表通过」改「只构建通过不等于通过」，合格证据去掉截图。§3「护栏靠 hooks 不靠自觉」改「护栏以实际挂载为准」。
- **配置**：`~/.claude/settings.json` 的 `hooks` 当时只有 `Notification`、`PostToolUse`、`SessionStart`、`StopFailure` 四类；**2026-09-21 实测为六类**，同日新增 `SessionEnd` 与 `PreToolUse`（见上文「会话生命周期机制（2026-09-18）」）。`~/.claude/session-hygiene.json` 不变。
- **依赖**：psutil（本机 Python 3.12.10 已装 7.2.2）；清点脚本用绝对解释器路径 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe` 调用，换机器需要改 `SKILL.md` 对应那一行。
- **验证**：清点脚本改后在 DTSF 实跑通过（退出码 0，20 个工作树、18 条 stash、11 条无远端分支、2 个独占容器运行中）。审查同时查出两处与实测不符的既有记载并已改正：memory `avoid-second-vite-port.md` 关于 9528 与 `strictPort` 的说法、`session-inventory.py` 输出里关于未提交改动能否恢复的说法。
- **未验证**：宿主在三条自动清理路径上保留工作树的行为取自 `claude.exe` 代码与审查者复核，未做端到端实测；eval case `worktree-closeout` 尚未跑 runner。
- **已知缺口**：`~/.claude/docs/config-checklist.md` §2.1 与 `config-inventory.md` §1.3 记载的七个 PreToolUse 脚本（`git_guard.py`、`secret_guard.py`、`dep_gate.py`、`placeholder_guard.py`、`edited_tracker.py`、`verify_recorder.py`、`verify_gate.py`）在 `~/.claude/hooks/` 下均不存在，`settings.json` 也没有挂载 `PreToolUse`；两份文档尚未按实际状态改写。
- **回退**：`SKILL.md` 与 `CHANGELOG.md` 恢复到 1.3.0 内容并重新加入钩子脚本与 `settings.json` 挂钩；`toolchain-pitfalls` 的删除项需从会话记录还原。

### 自建 skill 精简批次（2026-09-19，用户逐项拍板）

- **删除 `generic-course-tutor`**：`~/.claude/skills/generic-course-tutor/SKILL.md`（单文件），同步移除 `.gitignore` 白名单行 `!skills/generic-course-tutor/`。备份：`~/.claude/backups/skill-prune-2026-09-19/skills/generic-course-tutor/`。
- **删除 `ai-readable-project`，思想并入 `instruction-auditor`**：原 8 个文件（SKILL.md、evals ×2、references/DESIGN.md 与 refactor-roadmap.md、templates ×3）。并入内容为上下文工程四类上下文、产物结构、六步执行流程、完成条件、债务观察清单、`@AGENTS.md` 单源双生态文件策略、维护规则；三个模板移到 `instruction-auditor/references/templates/`。未并入：`references/refactor-roadmap.md`（重构五步路线属 code-change-workflow 域）。备份：`~/.claude/backups/skill-prune-2026-09-19/skills/ai-readable-project/`。
- **删除 `wiki-sediment`**：全局 `~/.claude/skills/wiki-sediment/` 是悬空指针，它指向的 `C:\ZYS\Wiki\.claude\skills\wiki-sediment\SKILL.md` 在此之前已不存在（Wiki 仓库 git status 记为未提交删除）。同时删除全局 `~/.claude/commands/wiki-save.md`；用户同日删除整个 `C:\ZYS\Wiki` 目录，Wiki 侧 `wiki-save` 命令随之消失。两份命令文件备份：`~/.claude/backups/skill-prune-2026-09-19/commands/` 与 `wiki-commands/`。
- **`content-to-note` 移回全局**：实体从 `C:\ZYS\Wiki\.claude\skills\content-to-note\` 移回 `~/.claude/skills/content-to-note\`（16 个源码文件 + `scripts/wechat/node_modules`，合计 12M），覆盖原指针 SKILL.md。SKILL.md 与 `references/note-template.md` 改写落盘约定：删除 wiki 固定目录（`71-公众号文章/`、`70-视频笔记/`）与仓库根 `.archive/`，改为**调用时由用户指定笔记目录**，未指定就不落盘、只输出到对话；归档目录默认取笔记目录下的 `.archive/<slug>/`。`.gitignore` 保留 `!skills/content-to-note/`，新增 `skills/content-to-note/scripts/wechat/node_modules/` 排除，12M 依赖不入 git。
- **`bidirectional-steelman` 触发条件重写**：原 description 只暴露「用户明确要求方案对比」一条路径，并写着「普通『该不该/哪个好』问答不触发」，与正文触发范围（「该不该」「值不值得」「哪个好」「怎么办」问句触发）直接矛盾，这是它在真实决策场景从不触发的直接原因。description 改为把三类未决取舍纳入触发，负向边界收为「只有唯一可验证答案的事实问题、方案已定的执行任务、用户要求直接给结论」。版本标记 v1.1.0 → v1.2.0。正文未改。
- **验证**：`content-to-note` 的 `python -m pytest tests` → 26 passed；`check_environment.py --json` 核心路线 OK（Python 3.12.10、脚本齐全、ffmpeg 与 yt-dlp 在位；funasr 缺失属增强路线）；wechat 依赖 `node -e require('cheerio'/'dayjs'/'qs')` 加载正常。`git status -- skills/` 确认三处删除、三处修改、新增文件目录正确，无 node_modules 泄漏。`instruction-auditor` 与 `bidirectional-steelman` 的新 description 已被宿主热加载（会话内实证）。
- **未验证**：`content-to-note` 新落盘约定的真实执行（需要一次真实链接提取）；`instruction-auditor` 第一部分未在真实项目上跑过；`bidirectional-steelman` 新触发条件是否在真实决策场景命中，需后续观察。
- **回退**：三个删除项从 `~/.claude/backups/skill-prune-2026-09-19/` 复制回原位，并恢复 `.gitignore` 白名单行；`content-to-note` 的项目实体可从 Wiki git 仓库历史取回；`bidirectional-steelman` 的 description 恢复为 v1.1.0 文本。

### 自建 skill 目录统一加 `-by-user` 后缀（2026-09-19，用户拍板）

- **决策**：用户要求「从名称就能知道这是我自建的」。全局 `~/.claude/skills/` 下 17 个自建 skill 目录全部改名加 `-by-user` 后缀；第三方与插件 skill 不加（插件 skill 在宿主里本来带 `插件名:` 前缀，天然可分）。
- **未加后缀的第三方**：`agent-browser`（junction 到 npm 包）、`agent-reach`、`archify`、`eli5`、`leader`。（2026-09-24 注：其中 `eli5` 已于 2026-09-22、`agent-reach` 已于 2026-09-24 归档；`agent-browser` junction 已于 2026-09-24 删除，能力并入 `auto-browser`。本条为 2026-08 快照。）
- **改名清单**：`ai-product-development`、`article-writer`、`awesome-design-md`、`bidirectional-steelman`、`cc-switch-setting-sync`、`code-change-workflow`、`company-discovery-evaluation`、`content-to-note`、`drawio-article-illustration`、`drawio-chart`、`improver-skill`、`install-ledger`、`instruction-engineering`、`parallel-delegation`、`skill-auditor`、`skill-trimmer`、`toolchain-pitfalls` 各自加 `-by-user`。
- **改动范围**：17 个目录改名 + 各自 `SKILL.md` 的 frontmatter `name:` 与正文自指；`.gitignore` 白名单 17 行与 node_modules 排除路径；全局 `CLAUDE.md` §8 尾部两处引用；`hooks/settings-sync-auto.py` 的同步脚本绝对路径（不改会让 PostToolUse 同步失效）；`external-configs/README.md`；`skills/leader/SKILL.md`（第三方 skill 对 `parallel-delegation` 的转介）；各 skill 的 evals/cases、references、test-prompts 里的互指。
- **保留原名的部分**：`skill-trimmer` 的状态目录名与 `skill-trimmer-workspace`、`review_server.py` 与 `scan_skills.py` 里的 `[skill-trimmer]` 日志前缀和 state root 目录名（内部程序标识，改了会让已有状态数据失联）；`CHANGELOG.md` 与台账历史条目（记录当时事实）；`drawio-chart` 示例 XML 的 `agent="drawio-chart"` 属性。
- **验证**：`content-to-note-by-user` 的 `python -m pytest tests` → 26 passed；`settings-sync-auto.py` 指向的 `sync_claude_common.py` 路径实测存在；全仓 grep 排除历史文档与 CHANGELOG 后无残留旧名；宿主已热加载新名字。
- **回退**：目录名去掉后缀，`.gitignore` 白名单与 `hooks/settings-sync-auto.py` 路径还原；`CLAUDE.md`、`external-configs/README.md` 与各 skill 内互指按本条逐项还原。

### content-to-note 改为仅手动调用（2026-09-20，用户拍板）

- **改动**：`~/.claude/skills/content-to-note-by-user/SKILL.md` 的 frontmatter 新增 `disable-model-invocation: true`；模型不再按「分享公众号/B站/抖音链接」自动加载，改由用户显式调用 `/content-to-note-by-user`。
- **未改动**：description、正文触发说明、`scripts/`、`references/`、`.gitignore` 白名单。
- **验证**：frontmatter 读回 1 处 `disable-model-invocation: true`；全库 grep 无其他文件引用本 skill 的自动触发路径。宿主侧生效需新会话加载 skill 清单后复核（同批次已有 10 个带该字段的自建 skill 在本机清单中均不出现）。
- **回退**：删除该行即恢复自动触发。

### resource-guard.py 资源守卫（2026-09-21，全局）

- **出处**：DTSF 会话中用户定下「只能用 docker、docker 内存占用必须严格限制」后，要求把限制做成其他项目也能生效的机械检查。
- **位置**：新建 `~/.claude/hooks/scripts/resource-guard.py`；`~/.claude/settings.json` 的 `hooks.PreToolUse` 新增一条，matcher `Bash|Write|Edit|MultiEdit`，超时 30 秒；`~/.claude/session-hygiene.json` 的 `exclusive` 由两条变三条：原有两条各补 `service` 与 `project` 字段，并订正 nginx 那条描述（现挂命名卷 `dtsf_frontend_dist`，不再挂主检出的 dist），第三条登记 `frontend-build` 的 `docker compose run` 一次性容器，用 `container_prefix` 代替 `container`。
- **内容**：三条判据。一、改动 compose 文件后，相对改动前新增的服务必须同时声明 `mem_limit` 与 `security_opt`，缺项时提请确认；只查新增服务，历史文件里本来就缺限制的老服务不重复报。二、命令要对 `session-hygiene.json` 独占清单里的容器做变更动作、该容器正在运行、且本机另有活跃 Claude 会话时提请确认；条目用 `container` 精确名与 `container_prefix` 前缀两种写法匹配运行中的容器名，后者给 `docker compose run` 起的一次性容器用（实测名字格式 `<compose 文件所在目录名>-<服务名>-run-<12 位十六进制>`，登记时给不出完整名字）；容器与端口按本机共享，不按项目隔离。三、命令要在宿主机上执行构建工具链（`pnpm`、`npm`、`npx`、`yarn`、`bun`、`corepack`、`node`、`vite`、`tsc`、`vue-tsc`、`tsx`、`ts-node`、`webpack`、`mvn`、`mvnw`、`gradle`、`gradlew`、`java`、`javac`）时提请确认，判定要求名字处在命令起首位置（行首，或管道与分号、换行、包装命令、环境变量赋值之后），因此容器内执行的 `docker compose exec <服务> mvn test`、提交消息与普通实参里的同名文字都不会被拦。
- **内容补充（拆词、包装命令与 Bash 写入路径）**：拆词改用 `shlex` 的 `punctuation_chars`，换行与回车先转成子句分隔符，因此把命令写成多行、用分号连接、控制符紧贴上一词都取得到起首位置；`sh`/`bash`/`zsh`/`dash`/`ksh`/`ash` 的 `-c`（含 `-lc` 这类合并短选项）、`cmd /c`（Git Bash 的 MSYS 路径转换会逼着人写成 `//c`，两种都认）、`powershell`/`pwsh` 的 `-Command`（含缩写）、`eval` 的载荷会被拆出来递归再扫，最多三层。`COMMAND_PREFIX`（`env`、`sudo`、`time`、`nohup`、`exec`、`command`、`xargs`、`winpty`）与 `WRAPPER_WITH_ARGS`（`timeout`、`nice`、`ionice`、`stdbuf`、`setsid`、`chroot`、`doas`、`watch`、`parallel`、`unbuffer`、`taskset`、`wsl`、`start`）之后到本子句结束都按命令起首位置处理；两类都会吃选项与取值，被包装的命令名字不紧跟在后面，因此回溯扫描认这两类的并集，`sudo -u root pnpm build`、`time -p pnpm build`、`xargs -I{} pnpm build` 都拦得住。heredoc 正文按行剥掉：正文是数据，里面的工具链名字不是命令；正文交给宿主机上的 shell 解释器时才保留（`bash <<'EOF'`、`sudo bash <<'EOF'`），交给容器里的 shell 时仍剥掉（`docker compose exec x sh <<'EOF'`），否则正文里的 `mvn` 会因为它前面多出一个子句分隔符而被当成宿主机上的命令。docker 侧补了三处：旧式 `docker-compose` 命令、`docker container restart X` 这类对象名词形式、以及不带 `-p`/`-f` 的整项目命令（用 `-p` 项目名、`-f` 所在目录名、`--project-directory` 目录名、命令里的 `cd` 目标与当前工作目录名五者之一对项目名）。判据一在 Bash 路径上按「写文件命令加目标文件名」粗判：重定向 `>`/`>>`、`tee`、`cp`、`mv`、`sed -i`（含 `-Ei`、`-i.bak`、`--in-place`）取出的目标基本名命中 compose 文件名正则时提请确认，`cp` 与 `mv` 只取最后一个位置实参（前面的算来源），`sed` 不带 `-i` 视为只读不触发，输入重定向 `<` 不算。三条判据同时命中时结论合并成一个 JSON 输出，之前分两次打印会让标准输出变成两行、调用方解析不了。判据三不含 `python`：宿主机上的 python 在本机只用于只读查看（查进程与端口、跑 `~/.claude` 下的状态脚本），而它是通用解释器，命令行上看不出是查一下还是起一个服务。三条都用 `permissionDecision: "ask"`，不直接拒绝。
- **依赖**：`PyYAML` 6.0.3（本机 Python 3.12.10 已装）；`docker` 与 `claude` 两条命令走子进程调用。钩子命令使用绝对解释器路径 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`，换机器需要改这一行。
- **验证**：断言套件 `~/.claude/hooks/tests/test_resource_guard.py` 131 条全部通过（拆词与目标提取 21 条、Bash 写 compose 文件的目标提取 11 条、独占清单命中 11 条、compose 判据 7 条、Bash 判据 27 条、宿主工具链拆词 13 条、多行与 shell 包装 35 条、宿主工具链端到端 6 条）。判据二原先照实机跑，断言只能写成「要么放行要么提问」，两种结果都接受等于不测；现改为在子进程里替换掉独占清单、容器运行状态与活跃会话数三处读取，命中断言不随机器状态变化，同时走的是同一个 `main()`。拦下路径覆盖多行、分号紧贴、回车分隔、圆括号子壳、`sh -c`、`bash -c`、`bash -lc`、`cmd /c` 与 `cmd //c`、`powershell -Command`、`pwsh -Command`、`eval`、两层 shell 包装、`timeout`/`nice`/`sudo`/`xargs` 吃取值、旧式 `docker-compose`、对象名词形式、不带 `-f` 的整项目命令、`--project-directory`，以及 Bash 路径上重定向、`tee`、`cp`、`sed -i`、heredoc 五种改写 compose 文件的写法。反向不误报覆盖容器内构建、容器内 `exec mvn`、`git status`、提交消息里的工具链名、普通实参里的包装命令与工具链名、引号里的分号与换行、`echo sudo -u root pnpm`、`docker ps`、别的服务、写普通文件、读 compose 文件、`sed` 不带 `-i`、`cp` 的来源、输入重定向、一次性容器没在跑、精确名条目不被前缀命中。
- **验证补充**：三条判据同时命中时标准输出只有一行（`docker compose ... up -d nginx && pnpm build` 实测），两条理由都在同一个 `permissionDecisionReason` 里。耗时实测：空命令 68 毫秒、普通命令 68 毫秒、多行加 shell 载荷 69 毫秒、heredoc 写文件 67 毫秒。
- **未验证**：本机另有会话这一条依赖 `claude agents --json` 的输出结构与 `sessionId` 字段，只按 session-guard 的既有读法对齐，未做双会话实测；命令替换 `$(...)` 里的文本取不到，会放行；判据一在 Bash 路径上认不出 `python -c "open(...)"` 与变量拼出来的目标路径；判据二在 `-p`、`-f` 目录名、`--project-directory`、`cd` 目标与当前目录名五者都对不上时放行；判据三的名单是人工枚举，名单以外的运行方式（`py -m http.server`、`go run`、`dotnet run`）不覆盖，需要时往 `HOST_TOOLCHAIN` 加名字。- **回退**：删除该脚本与 `settings.json` 的对应 `hooks.PreToolUse` 条目；`session-hygiene.json` 的两条 `service`/`project` 字段可保留（旧守卫不读它们，新守卫读不到时会跳过独占判据）。

### context-budget-guard.py 上下文预算提醒（2026-09-21，全局）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法落到本机配置的实验中，用户拍板「加自动提醒机制，在上下文快到压缩阈值时提醒 Agent 写接续笔记」，并定下压缩阈值 200k、提醒线 150k。
- **位置**：新建 `~/.claude/hooks/scripts/context-budget-guard.py` 与 `~/.claude/hooks/tests/test_context_budget_guard.py`；`~/.claude/settings.json` 的 `hooks.PostToolUse` 新增一条，matcher `.*`，超时 10 秒；同文件 `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW` 由 `"150000"` 改为 `"200000"`。会话状态目录 `~/.claude/context-budget/`（每个会话一个文件，内容是一行数字）。
- **内容**：PostToolUse 钩子。读 payload 的 `transcript_path`，从文件尾部往前找最后一条带 `message.usage` 的 assistant 记录，把 `input_tokens`、`cache_read_input_tokens`、`cache_creation_input_tokens`、`output_tokens` 四项求和，得当前上下文规模。达到 `REMIND_AT`（150k）就注入 `additionalContext`，文案给出当前用量并列出接续笔记该写的四类内容（做到哪一步、为什么这么选、哪条路已否掉、下一步），已有的 commit/diff/文档要求引路径。节流靠会话状态文件：记下上次提醒时的用量，涨过 `REMIND_STEP`（25k）才再提醒一次，否则每次工具调用都会刷同一条。
- **依据**：150k 是 Matt Pocock 的 smart zone 终点（`mattpocock-skills@1.2.3` 的 `ask-matt/PHASE-BOUNDARIES.md:21`）。提醒落在线上而不是线后，因为越过之后模型判断力下降，此时写的接续笔记质量也跟着下降。压缩点抬到 200k 是用户决定，代价是 150k 到 200k 这段在降智区干活。
- **依赖**：无第三方依赖，只用标准库。钩子命令使用绝对解释器路径 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`，换机器需要改这一行。
- **验证**：断言套件 `~/.claude/hooks/tests/test_context_budget_guard.py` 15 条全部通过（usage 求和与跳行 5 条、文件读取与扩窗 2 条、端到端提醒与节流 7 条、真实 transcript 1 条）。注入通道与用量计算端到端实测：把 `REMIND_AT` 临时降到 50k，紧接着一次 Edit 的工具结果里出现 `PostToolUse:Edit hook additional context: 上下文已用约 118k。…`，确认 payload 里的 `session_id` 与 `transcript_path` 在本机形态下可用、算出的用量与真实值一致；改回 150k 后同会话不再触发。真实阈值触发同日实测：会话内用量涨到 151k 时提醒自动出现一次（文案「上下文已用约 151k。150k 是 smart zone 终点…」），之后数次工具调用不再重复，节流生效。cc-switch 侧核实 `settings.common_config_claude` 已带上 `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = "200000"` 与第三个 PostToolUse 组；当前 provider（OpenCode Go）的 `meta.commonConfigEnabled` 实测为 `true`，切换时读 common 快照，provider 快照里本来就没有这些键，无需另改。
- **未验证**：transcript 异步写入的滞后幅度只按官方文档记载（「may lag in-memory conversation」），未实测偏差大小；提醒是否真的促成 Agent 写笔记，需要后续长会话观察。
- **回退**：删除 `~/.claude/hooks/scripts/context-budget-guard.py`、`~/.claude/hooks/tests/test_context_budget_guard.py` 与 `settings.json` 的对应 `hooks.PostToolUse` 条目；`env.CLAUDE_CODE_AUTO_COMPACT_WINDOW` 改回 `"150000"`；`~/.claude/context-budget/` 可直接删除（丢了最多让某个会话重复提醒一次）。改完 settings.json 需让 cc-switch 重新同步一次 common 快照。

### task-notes-by-user 任务笔记三级结构（2026-09-21，全局）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）中，接续笔记写成一个 `STATE.md` 越写越长（163 行 / 17,893 字节），用户据此定下做法：先要求「笔记也应该做成类似于 SKILL.md 和 MEMORY.md 具体条目的那样，也就是一个目录文件里面索引其他笔记文件」，再要求「把渐进式披露做到极致」，最后要求「可以做成一个 skill 专门管这个，这些专门放到一个最外层的 notes 文件夹里面」。
- **位置**：新建 `~/.claude/skills/task-notes-by-user/SKILL.md`（目录名带 `-by-user` 后缀）；`~/.claude/.gitignore` 白名单新增一行 `!skills/task-notes-by-user/`，插在 `skill-trimmer-by-user`（第 151 行）与 `toolchain-pitfalls-by-user` 之间；全局 `CLAUDE.md` §8 的「产物去处」增加一项 `notes/<任务名>/`，原句「仓库根不新建任何文件或目录」收窄为「除这几处之外，仓库根不新建任何文件或目录」。
- **内容**：三级结构。入口 `STATE.md` 只放目的、当前会话目录名、进度、下一步候选、未决、产物指针表，每个新会话都要读，所以按一屏控制；索引 `ITEMS.md` 放清单表格与一行一条的记录索引，索引行格式 `- <编号> [<标题>](<会话目录>/<同级文件名>) — <一句结论>`，hook 写结论而不写同义反复；单条 `<会话目录>/<编号>-<短名>.md` 放一条笔记的完整正文，按自足接续单元写。存放位置 `<仓库根>/notes/<任务名>/`，任务名用 `YYYY-MM-DD-主题`，单条再按会话落子目录（见本台账下一条）。写作要求五条：及时（时点是相位边界，不等压缩触发）、必要、无冗余（别处已有的引路径）、无遗漏（被否掉的路子漏了算遗漏，改了哪些文件漏了不算）、准确（拿不准的标「未验证」）。维护动作三步：建单条笔记文件、索引加一行、入口只改进度那一行。写作时避开「落地、落到」这类词，全程用完整动宾结构。
- **依赖**：无。skill 不引用任何宿主专有工具，正文只讲文件结构。
- **验证**：宿主热加载生效，本会话的可用 skill 清单里出现 `task-notes-by-user`，description 与文件一致，按「新建、追加或整理任务笔记时」触发。结构实例 `lab-area/notes/2026-09-21-context-hygiene/` 同日建成：入口 35 行 / 2,175 字节、索引 77 行 / 3,512 字节、10 个笔记文件合计 11,871 字节，全部相对链接在搬迁后重算（索引行由 `notes/xx.md` 改为同级 `xx.md`，材料路径由 `../2026-09-17-wechat-content-notes/...` 改为 `../../exp/2026-09-17-wechat-content-notes/notes/article-3.md`），搬迁用 `git mv` 保留历史，搬空的 `exp/2026-09-21-context-hygiene/` 目录已删除。
- **回退**：删除 `~/.claude/skills/task-notes-by-user/` 与 `.gitignore` 白名单那一行；全局 `CLAUDE.md` §8「产物去处」去掉 `notes/<任务名>/` 一项并把「除这几处之外」还原为「仓库根不新建任何文件或目录，说明文档、日志、笔记、脚本都不例外」。

### code-change-workflow 的 grilling 入口改用 grill-with-docs（2026-09-21，用户拍板）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）第 10 项。插件 `ask-matt/SKILL.md:17` 写明在有工作目录时 `grill-with-docs` 严格优于 `grill-me`：跑同一套 `/grilling`，另用 `domain-modeling` 留下档案。本机原来只指了无状态的 `grill-me`，用户拍板改用前者。
- **位置**：`~/.claude/skills/code-change-workflow-by-user/SKILL.md` 第 26 行（§1.1 的 grilling 协议末尾）；同目录 `CHANGELOG.md` 新增 1.4.1 条；`~/.claude/CLAUDE.md` §8「产物去处」。
- **内容**：指名由 `mattpocock-skills:grill-me` 改为 `mattpocock-skills:grill-with-docs`，并写明两处产物——仓库根 `CONTEXT.md` 是纯术语表、不含实现细节，`docs/adr/` 只在难以逆转、缺上下文会让人意外、经过真实取舍三条同时成立时才写。§8 产物去处补「架构决定放 `docs/adr/`」「项目术语表放仓库根 `CONTEXT.md`」两项，使它们不与同段的「仓库根不新建任何文件或目录」冲突。
- **依赖**：插件 `mattpocock-skills@1.2.3` 的 `engineering/grill-with-docs` 与 `engineering/domain-modeling` 两个目录已存在于缓存，属手动调用的 skill，无需额外安装。
- **验证**：改后两处文件读回一致；`grill-with-docs/SKILL.md` 与 `domain-modeling/SKILL.md` 实测存在。全库 grep `grill-me|grill-with-docs`，其余命中都是历史记录或举例（本台账的会话出处、`docs/config-inventory.md` 的清单、`skill-trimmer` 的两处举例、`code-change-workflow` CHANGELOG 的旧版本条目），没有别处仍把 `grill-me` 当作入口。
- **未验证**：本机尚未在真实项目里跑过一次 `grill-with-docs`，`CONTEXT.md` 与 `docs/adr/` 的实际落盘形态未实测。
- **回退**：SKILL.md 第 26 行改回 `mattpocock-skills:grill-me` 并删掉产物那半句；§8 去掉 `docs/adr/` 与 `CONTEXT.md` 两项；CHANGELOG 的 1.4.1 条按本台账惯例保留为历史。

### code-change-workflow 去重：四处流程骨架改为引用插件 skill（2026-09-21，用户要求）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）。用户先问该 skill 与插件 `mattpocock-skills` 是否重复，核对后确认四处流程骨架重复、约束层不重复；随后要求「删除其中冗余的内容，改成直接引用已有的 skill」。
- **位置**：`~/.claude/skills/code-change-workflow-by-user/SKILL.md` 的 §1.1 grilling 协议、§1.3 Bug 修复、§1.4 AI 代码审查、§1.5 规范驱动产物、§3 Agent 调度；同目录 `CHANGELOG.md` 新增 1.5.0 条；frontmatter `version: 1.4.0` 改为 `1.5.0`。
- **内容**：grilling 协议删掉设计树、前沿分批、每问附推荐答案、拍板后推进四句复述，改指 `mattpocock-skills:grilling` 与两个入口 skill，保留本机三条（数十问正常、纯文本不用 AskUserQuestion、每条拍板记依据）。Bug 修复删掉红绿回路描述，改指 `mattpocock-skills:tdd` 与 `diagnosing-bugs`，保留人工确认与验收 checklist。§1.4 新增引用 `mattpocock-skills:code-review`（固定点 diff、两轴并行子代理、Fowler 坏味道基线），本机三维、动作清单、权限归属、反模式保留。§1.5 新增一句指向 `mattpocock-skills:to-spec`。§3 删掉竖切规则与「第一片穿全部层」，与 decompose 那条合并为指向 `mattpocock-skills:to-tickets`，保留 4-6 片、外部可观察现象判据、沿用宿主执行计划、Plan 审批后执行。
- **依赖**：插件 `mattpocock-skills@1.2.3` 已启用（`tool-install.md` 记 2026-09-21 实测启用列表含它）。`code-review`、`tdd`、`diagnosing-bugs`、`grilling` 无 `disable-model-invocation`，可自动触发；`to-spec`、`to-tickets`、`grill-with-docs`、`grill-me` 标了 `disable-model-invocation`，需用户手打命令。
- **验证**：改后 SKILL.md 读回逐段核对；全库 grep 四个被删概念的残留表述（设计树/前沿、2-3 个失败测试、竖切判据、第一片）确认只在本台账与 CHANGELOG 的历史条目里出现。
- **未验证**：这四处引用尚未在真实编码任务里跑过一遍。
- **回退**：从本台账前两条（1.4.1、本条）的正文可还原被删语句；SKILL.md 恢复复述文字并去掉四个引用，CHANGELOG 保留 1.5.0 条为历史。

### code-change-workflow 补「进循环前先单跑一轮」（2026-09-21）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）第 18 项先单跑一次（材料 §6.1）。材料要求放进 AFK 循环前先手动跑一次，把要补进 prompt 的调优在这一步做完，第一次暴露的通常是脚本与配置问题，与模型能力关系不大。
- **位置**：`~/.claude/skills/code-change-workflow-by-user/SKILL.md` 第 148 行（§3「护栏以实际挂载为准」那条的长链编排句末尾）；frontmatter `version: 1.5.0` 改为 `1.5.1`；同目录 `CHANGELOG.md` 新增 1.5.1 条。
- **内容**：补一句「进循环或放并行之前先单跑一轮同类任务：核对路由、权限、输入契约与产物格式（细见 `parallel-delegation-by-user` 第 3 条），单步不可靠就上并行或进循环，只会同时收到一堆看不懂的改动」。本机原有同源规则在 `parallel-delegation-by-user` 第 3 条（批量并行 ≥2 个 worker 前先单跑），触发条件只写了并行，本次只补「循环」这一半，规则正文不复制。
- **依赖**：无。两处都是本机自建 skill 的正文。
- **验证**：改后读回第 148 行；`parallel-delegation-by-user` 第 3 条原文比对，症状清单与材料一致，未发现第三处同义规则。
- **未验证**：本机尚未跑过 AFK 循环。
- **回退**：删掉第 148 行末尾补的那一句，`version` 退回 1.5.0；CHANGELOG 的 1.5.1 条按本台账惯例保留为历史。

### docker-only-by-user（2026-09-21，全局）

- **出处**：DTSF 会话中用户定下「之后只看 docker 的事情」，三条目的为限制占用、全部在容器里执行、安全性；同轮先做 `resource-guard.py` 机械检查，再要求「做一个 skill 专门让项目来实现我要的 docker 需求」。
- **位置**：新建 `~/.claude/skills/docker-only-by-user/SKILL.md`（单文件）；`~/.claude/.gitignore` 白名单新增 `!skills/docker-only-by-user/`，插在 `content-to-note-by-user` 的 node_modules 排除行与 `drawio-article-illustration-by-user` 之间。
- **内容**：开头三条目的。接入清单七条——容器定义集中到项目 `deploy/` 目录、代码来源用环境变量指向工作树、每个服务写全五个资源字段、端口只绑回环、按需启动的服务挂 `profiles`、容器内自设上限低于容器上限、名称与端口登记到 `~/.claude/session-hygiene.json`。资源字段按 `${VAR:-默认值}` 留出部署时覆盖的入口。机械保证一节只写 `resource-guard.py` 挂在哪里、拦哪三类动作，判据细节指回脚本头部注释，不在 skill 正文里复述。
- **关键规则**：`memswap_limit` 与 `mem_limit` 写成同一个变量表达式，两者相等即完全禁用交换；上限走顶层字段而不写进 `deploy.resources.limits`，同一个服务里两者同值可以共存、异值报 `can't set distinct values`，`pids_limit` 更严格，只要 `deploy.resources.limits` 在而里面没有同名项就冲突。这两条由本机实测得出，写进 skill 是为了不再重复踩。
- **依赖**：无外部运行时依赖；引用的 `~/.claude/hooks/scripts/resource-guard.py` 与 `~/.claude/session-hygiene.json` 均已存在。
- **验证**：宿主热加载生效，本会话可用 skill 清单里出现 `docker-only-by-user`，description 与文件一致。
- **未验证**：尚未在新项目上按这份清单接入过一次。
- **回退**：删除 `~/.claude/skills/docker-only-by-user/` 与 `.gitignore` 白名单那一行。

### task-notes-by-user 单条笔记按会话分目录（2026-09-21，用户要求）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）中，用户提出「笔记应该要按会话分开，免的串了。记录到笔记 skill 里面吧」。两个会话写同一份 `notes/<任务名>/` 时，单条笔记落在同一个平面上，编号会撞、会话之间分不清谁写的。经 AskUserQuestion 确认：方案取「会话子目录」，生效范围取「只对新会话生效」（已写在顶层的那批笔记不搬，本会话后续笔记仍写顶层，新会话才启用）。
- **位置**：`~/.claude/skills/task-notes-by-user/SKILL.md` 五处——frontmatter 的 description、第 10 行存放位置句、第 18 行三级表格的「单条」行、新增的「## 会话目录」小节（第 22-29 行）、第 42 行索引行示例、第 70 行维护动作句。本台账上一节「task-notes-by-user 任务笔记三级结构」的内容描述同步改写为会话子目录口径。
- **内容**：会话目录名 `<日期>-s<序号>`，序号从 1 起按该任务已有会话目录递增。开工先读入口的「当前会话」行，那个目录是自己写过（上下文里还有当时内容）就沿用，认不出就是新会话，取下一个序号新建并把入口那一行改成新目录。同一会话续写只往自己目录加文件，不新建目录、不改别的会话目录里的文件。索引行写相对路径如 `2026-09-21-s2/18-single-run-first.md`，总索引仍是一份跨会话共用，行只由产出它的会话新增，别的会话可改错字但不重排别人的行。入口的「进度、下一步、未决」三块仍是单份跨会话共写，因此入口文件那一节的「只放四块」改为「只放五块」，加进「当前会话」。
- **依赖**：无。skill 不引用宿主专有工具。
- **验证**：改后 SKILL.md 读回全文一致；入口文件一节与「## 会话目录」小节对「当前会话」行的要求互相对上，不存在只在一处出现的字段。本会话（`2026-09-21-s1`）已有 20 个顶层笔记文件按生效范围保持原位不动。
- **未验证**：会话子目录模式尚未在真实的新会话里跑过一次，序号递增与「当前会话」行的识别办法都没有实战检验。
- **回退**：删掉「## 会话目录」小节与「当前会话」行要求；第 18 行「单条」行改回 `<编号>-<短名>.md`，第 10 行、第 42 行、第 70 行、description 各自退回上一版本的说法；本台账上一节的内容描述照旧改回。

### Claude Code 减负：四个开关与七个裸工具名 deny（2026-09-21，用户拍板）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）。用户提出「还有 matt 建议的 claude code 关闭不必要东西」，材料笔记里没有这一段，用户指示「去网页找吧」。找到 Matt 本人的文章《How to kill the bloat in Claude Code's system prompt》（`https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt`），方法六步：`/context` 看分类 → 插代理排出每个工具的体积名次 → 开顶层 `disable*` 开关 → 用裸工具名进 `permissions.deny` → 完整清单 → 重启再测。机制经官方文档确认（`code.claude.com/docs/en/permissions`：「`Bash(*)` is equivalent to `Bash`… As a deny rule, both forms remove the tool from Claude's context」，裸名移除对 `EndConversation` 之外的所有工具生效；`settings-reference` 确认四个键名与 `skillOverrides`）。
- **位置**：`~/.claude/settings.json`。顶层新增 `disableBundledSkills: true`、`disableClaudeAiConnectors: true`、`disableWorkflows: true`、`enableArtifact: false`（`disableRemoteControl: true` 原已存在）；`permissions.deny` 由空数组填入七个裸名 `CronCreate`、`CronDelete`、`CronList`、`DesignSync`、`NotebookEdit`、`PushNotification`、`RemoteTrigger`。`env` 段未动。
- **内容**：三层减负手段。顶层开关按功能整块关；`permissions.deny` 的裸工具名把工具定义整个从上下文移除，带作用域的规则（如 `Bash(git push*)`）只拦调用、定义留着，两者省下的量不同；`skillOverrides`（本次未用）能隐藏单个 skill。有意保留：EnterPlanMode 与 ExitPlanMode（Plan 审批流程）、AskUserQuestion、ReportFindings（`code-review` 流程用）、ScheduleWakeup（后台任务）、SendMessage 与 ListAgents 与 Agent 与 Task 系列（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 开着）。
- **依赖**：无外部依赖。本机已开 `ENABLE_TOOL_SEARCH`，多数非核心工具走延迟加载、定义本来就不在每次请求里，因此 deny 它们省下的是名字列表那一小块，省得多的是 `Workflow` 这种原本带完整定义、且 Matt 实测常为最大一项的。
- **验证**：改后 `settings.json` 用 Python 解析通过并逐键读回；`settings-sync-auto.py` hook 自动同步，DB `settings.common_config_claude` 与 live 逐键一致（五个新键与七项 deny 全部对上）；四个 claude provider 的 `settings_config` 快照实测都不含 `enableArtifact`（即无 `true` 值），符合 `keep-artifact-disabled` 要求的三处核对；本会话的工具列表实测立即少了 CronCreate、CronDelete、CronList、DesignSync、NotebookEdit 五项。
- **未验证**：payload 实际缩减量未测（Matt 的第一步是用代理排工具体积名次，本机 8787 已被 headroom 占用，未改端口重跑）。设置改动要重启 Claude Code 才完整生效，重启后的 `/context` 前后对比未做。`disableBundledSkills` 关掉的具体是哪些自带 skill，本机没有从安装目录查到（`~/.local/share/claude/versions/<ver>` 是单文件可执行，无 skills 目录）。
- **回退**：删掉四个顶层键（`enableArtifact` 除外，见下）；`permissions.deny` 改回 `[]`。`enableArtifact: false` **不可逆**——官方文档写明「no file can turn it back on」，写回 `true` 开不回来，这一条没有回退路径，是本次改动里唯一不可撤销的一项（用户已在选项说明中确认）。

### 上下文卫生实验的 skill 与全局 CLAUDE.md 改动补记（2026-09-21，全局）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`）。此前多轮改动直接落到各 skill 与全局 `CLAUDE.md`，没有当轮登记，此处按 §7.1 补齐；每条的内容明细以对应 skill 自己的 `CHANGELOG.md` 为准，没有 CHANGELOG 的看实验笔记 `notes/2026-09-21-context-hygiene/`（回退与验证步骤同样在那里）。
- **instruction-engineering-by-user**：检查表从七项扩到九项——第一次新增「常驻划分」并写入三条判据，第二次给「审查基准」补三条（两个负担 context load / cognitive load、信息层级三级阶梯与渐进披露、正面陈述）并新增第九项「逐句剪除」，第三次补五处 Matt 审计原则：拆分判据、完成标准的防御顺序与判据的可检验性、锚定词的分量、context pointer 的硬软依赖（源 ADR 0001）、逐句剪除段的 relevance 两条失效路径。该 skill 无 CHANGELOG，未新建；明细见实验笔记的 `instruction-engineering-expansion.md` 与 `2026-09-21-s1/matt-audit-principles.md`。
- **skill-auditor-by-user**：核心边界新增两条（被动读材料取词汇是一行指针、改变它才构成 skill；skill 间依赖写成 `/skill` 形式的散文调用、不跨目录链文件）；通用 Skill 原则新增第 7 条「不加冗余机制」；Router 追加检查新增第 8 条「同步义务」。frontmatter 与正文末尾版本戳升 v2.2.0，`CHANGELOG.md` 新增 v2.2.0 条；v2.1.0 的条目在既有记录里缺失，照实记缺口不补编。
- **code-change-workflow-by-user**：§1.6 新增开工前三条（一个任务一个工作树、独占资源先协商、写库先确认）与收工前「自己的收尾清单」一条，承接全局 `CLAUDE.md` §8「并行会话」「收尾」两段的细则；frontmatter `version` 1.5.1 → 1.6.0，`CHANGELOG.md` 新增 1.6.0 条。
- **task-notes-by-user**：入口文件的「下一步候选」写明该走哪个 skill 或取哪份材料。无 CHANGELOG，未新建。
- **parallel-delegation-by-user**：Route 第 1 条补收益的两笔（并行省下的时间、主代理窗口省下的上下文）与不委派的判据（需要跟主代理已有上下文一起权衡的决策不委派）；description 改写为单个子代理也触发。
- **docker-only-by-user**：description 改写为「本机执行环境约定」，覆盖「随手想跑个服务」这类不配置 docker 的场景。
- **全局 `~/.claude/CLAUDE.md`**：§2.4 补「任务切分归用户给的清单与方案，Agent 不重划任务边界」；§6.3 docker 是唯一执行环境、§8 端口独占与收尾两段、§2.5 子代理调用确认三处外移，各自只留核心禁令加一行指针，细则分别落在 `docker-only-by-user`、`code-change-workflow-by-user` §1.6、`parallel-delegation-by-user` 的 Configuration gate。外移后实测 274 行 / 8,203 字符，外移前 280 行 / 8,377 字符。
- **验证**：各 skill 改动后逐处读回；两个带 CHANGELOG 的 skill 其 frontmatter 版本与 CHANGELOG 最高条目对得上；全局 `CLAUDE.md` 的行数与字符数由脚本读出。
- **回退**：各 skill 按自己的 `CHANGELOG.md` 逐条退回；全局 `CLAUDE.md` 三处外移按上列对应位置反向取回原文。

### Matt 材料第二轮：计划写法、编排调用轴、反馈回路（2026-09-21，全局）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`），用户要求继续挖掘 aihero.dev 与 GitHub 的一手材料后再优化配置。本轮固定入口与已读清单见 `notes/2026-09-21-context-hygiene/2026-09-21-s2/matt-sources-inventory.md`；逐条判定见同目录 `local-application.md`。
- **来源核对**：上游 `mattpocock/skills` 的 `package.json` 版本为 1.2.3，与本地插件 `mattpocock-skills` 一致，本轮未升级插件。
- **全局 `~/.claude/CLAUDE.md`**：§5.2「回复风格」新增一条——计划文本要极简、为求简洁可以牺牲语法，结尾用编号列表列出具体步骤再列出未决问题。源 `my-agents-md-file-for-building-plans-you-actually-read` 与 `plan-mode-introduction`，两篇给的三条原句合并成一条。
- **skill-auditor-by-user**：核心边界新增一条——按「谁能调用」分两类，只能手动敲的（`disable-model-invocation: true`）负责编排，能被模型自动选中的负责执行，编排可以调用执行、编排之间不互相调用。源 GitHub 仓库 README 的治理规则。正文末尾版本戳升 v2.3.0，`CHANGELOG.md` 新增 v2.3.0 条。
- **code-change-workflow-by-user**：§1.3「改后」新增一条「反馈回路是上限」——能自动跑的检查比叮嘱有效（检查不过模型会自己重试，不因反复失败而泄气），任务粒度也由反馈速率定。源 `essential-ai-coding-feedback-loops-for-type-script-projects` 与 `tips-for-ai-coding-with-ralph-wiggum` 第 5、6 条。frontmatter `version` 1.6.0 → 1.6.1，`CHANGELOG.md` 新增 1.6.1 条。
- **task-notes-by-user**：「与相邻机制的区别」段首补一条「什么时候写」——判据是可携带性，只有工作真的要移动到别处时才写文件（换宿主、换目录或仓库、交给同事、分叉出独立支线），同一宿主同一目录只是从规划转到实现用 `/compact`。源 `skills-handoff`。无 CHANGELOG，未新建。
- **验证**：四处改动逐处读回；`code-change-workflow-by-user` 的 frontmatter 版本与 CHANGELOG 最高条目对得上。
- **回退**：按上列各文件反向逐条删除本轮新增句；两个带 CHANGELOG 的 skill 连版本戳与条目一起退回。
- **本轮判定不改的项**：破坏性 git 命令的 hook 未加——`git_guard.py` 与 `gateguard-destructive.js` 是 2026-09-08 经用户逐项确认后删除的，Matt 的 `git-guardrails` 建议在本机属评估后弃用。状态栏的 git 三项计数未加——本机 statusline 曾专门做过提速，加三次 git 子进程与那次优化相抵。两处理由与证据见 `notes/2026-09-21-context-hygiene/2026-09-21-s2/local-application.md`。

### coding-workflow-by-user 1.7.0：更名、全局 CLAUDE.md 外移落位、验收相位与深模块（2026-09-21，全局）

- **出处**：把 Matt Pocock（AI Hero）的上下文卫生方法应用到本机配置的实验（`lab-area` 的 `2026-09-21-context-hygiene`），用户指令为「全局 claude.md 的预算立起来、记忆也修复，三可以做独立和深模块」，中途另行拍板改名。逐条判定见实验笔记；明细见该 skill 的 `CHANGELOG.md` 1.7.0 条。
- **更名**：`~/.claude/skills/code-change-workflow-by-user/` → `~/.claude/skills/coding-workflow-by-user/`（命令原文 `mv code-change-workflow-by-user coding-workflow-by-user`）。改名理由是正文已从「代码改动」扩到完整编码工作流。同步改到的位置：frontmatter `name` 与正文标题；6 份 `evals/*/case.yaml` 的 prompt 与 description；`~/.claude/.gitignore` 第 139 行的白名单；`instruction-engineering-by-user/SKILL.md` 2 处与 `references/refactor-roadmap.md` 1 处；`article-writer-by-user/SKILL.md` 1 处；`references/MAINTENANCE.md` 5 处；全局 `~/.claude/CLAUDE.md` 3 处。frontmatter `description` 未动（改它属 major，要重跑触发验证）。本台账与已发布 CHANGELOG 里的旧名保持原样，那是当时的事实。
- **全局 `~/.claude/CLAUDE.md` 三处改动落地**：§2.1 删掉六个编码小节（依赖与错误处理、文件与工具、改动范围、实现复杂度、修改测试与验证、Python 代码），原文一字未改地进该 skill 的 §1.0；§8 功能分支归并的五步流程进该 skill 的 §1.6，全局只留一行指针；§2.3 第一条由「按当前场景和用户指定流程分诊，不预设某个执行 skill」改为显式要求先读 `coding-workflow-by-user`。落地后实测 232 行 / 6,932 字符。
- **预算规则**：`instruction-engineering-by-user/SKILL.md` 审查基准新增一条「全局 `CLAUDE.md` 的预算」——上限定 240 行 / 7,000 字符，超了按常驻划分的三条判据外移。本文件即该预算的检查口径来源。
- **该 skill 正文新增**：§1.0 编码硬约束（全局 §2.1 六节原文）、§1.3.1 验收相位（QA 计划 → 人审计划与实现 → 照计划验 → 问题回成新工单）、§1.5.1 深模块与接口归属（主线走插件 `mattpocock-skills:improve-codebase-architecture`，词汇取 `codebase-design`）、§1.6 功能分支归并。frontmatter `version` 1.6.1 → 1.7.0。
- **§4 git 回退阶梯删除（用户拍板）**：§4「止血与回退」第 3 条原本并列给出 `git restore` → `git revert` → `git reset --hard HEAD~N`，与 §1.0 搬入的「禁止用 Git 回滚任何代码」直接冲突（该冲突在搬入前就跨全局文件与 skill 两处存在）。用户拍板保留禁令、删阶梯，回退按 §1.0 用文件编辑工具恢复；§4 触发行里的 `git reset --hard` 例外句一并去掉。改后全库 `git reset --hard|git restore|git revert` 在自建 skill 内零命中。
- **依赖**：插件 `mattpocock-skills@1.2.3` 已启用，§1.5.1 的两个引用落在它身上（`plugin.json` 第 26、36 行确认在 25 个启用技能内）。
- **验证**：改名后全库检索旧名，剩余命中全在本台账与旧 CHANGELOG 的历史条目内；全局 `CLAUDE.md` 改后按小节检索确认六个编码小节与五步流程已不在该文件，且两处内容在该 skill 内逐字存在；行数字符数由 `wc -l` 与 `python -c "print(len(open(...).read()))"` 读出。
- **回退**：`mv` 改回原名并逐处反向替换；全局 `CLAUDE.md` 三处按该 skill 的 §1.0、§1.6 与本节上列原文取回；其他 skill 按各自改动反向删除本轮新增句。

### task-notes-by-user 补「任务收尾后的处置」（2026-09-21，用户拍板）

- **出处**：同上实验。`notes/<任务名>/` 与 `docs/` 下的产物在任务收尾后怎么处置，本机此前没有规则（材料 §4.4 也自认没有答案），用户在第三轮要求按建议处置。
- **位置**：`~/.claude/skills/task-notes-by-user/SKILL.md`，在「维护动作」与「与相邻机制的区别」之间新增一节，并改「与相邻机制的区别」里 memory 那条的结尾指向该节（原文为「任务结束随笔记目录一起处置」，无内容）。
- **内容**：笔记目录随分支并入主干留档，不删、不改写成摘要、不搬去 `docs/`；收在入口那层（`STATE.md` 与 `ITEMS.md` 保留，正文靠索引抵达）；已成规则的条目在索引那一行标「已落地」；判定不改的照旧留（价值在防止下个会话重提同样的候选）；过期就地改，不追加旧值。
- **验证**：新增节读回一致；该 skill 无 CHANGELOG，未新建。
- **回退**：删掉新增节，把 memory 那条的结尾改回「任务结束随笔记目录一起处置」。

### ai-product-development-by-user 改写为路线图（2026-09-21，用户要求）

- **出处**：同上实验。第三轮核对该 skill 与插件 `mattpocock-skills` 的覆盖关系，结论是七步里六步有对应物、一步没有，逐条见 `notes/2026-09-21-context-hygiene/2026-09-21-s3/global-budget-and-rename.md` 第六节。用户据此要求把它改成一张流程图，每一步只建议该调哪个 skill。
- **位置**：`~/.claude/skills/ai-product-development-by-user/SKILL.md`，整份重写（129 行 → 56 行）。frontmatter 未动，`disable-model-invocation: true` 保留，模型仍然只能手动调用。该 skill 无 CHANGELOG，本次未新建。
- **新内容**：mermaid 路线图（七步，节点内写该调的 skill）；一张「每一步调什么」表（调用、谁发起、产出）；五条路线判据（第 2、3 步不跳、第 6 步不在现场改代码、通过与否由用户拍板、单点故障走 `diagnosing-bugs` 不回到本路线、代码库形态留到第一版跑通之后）。
- **删掉的内容**：七步的散文说明、每轮产出清单、完成判断、大部分约束。这些在插件 skill 里有更完整的版本，或已由本机 `coding-workflow-by-user` §1.3.1 承担。
- **核对过的事实**：该 skill 引用的调用逐个对过插件 `.claude-plugin/plugin.json` 的启用清单。`to-spec`、`to-tickets`、`implement`、`handoff`、`improve-codebase-architecture` 五个带 `disable-model-invocation`，只能用户手敲；`grilling`、`prototype`、`diagnosing-bugs` 可自动调用；`impeccable`（插件 impeccable 4.1.1）无该标记，但其路由写明无参数时先出菜单、不自动跑子命令。
- **验证**：全文读回一致。
- **回退**：原文件在 `~/.claude` 仓库的版本控制内，用 `git show 2c17cd8:skills/ai-product-development-by-user/SKILL.md` 取回原文，再用文件编辑工具写回。

### task-notes-by-user 触发点重建、全局 CLAUDE.md 加触发句、删 skill-routing-boundary 记忆（2026-09-21，用户拍板）

- **出处**：用户问 `task-notes-by-user` skill 是否消耗 token，核对后结论是 skill 正文只在触发后加载一次、不是开销大头，缺口在触发：该 skill 的 description 触发句「新建、追加或整理任务笔记时使用」自我指涉（模型得先知道自己要写笔记才知道该调它），且全局 `CLAUDE.md` §2.4 的「到段落边界主动把接续状态落盘」常驻规则不点名 skill，两条之间没有指针。skill 正文末句「该做的是在相位边界提醒」把这个缺口写出来了，但提醒机制无实体（查 `~/.claude/settings.json` 全部 hooks，无一条涉及 `notes`/`task-notes`；项目 `.claude/` 下无 settings.json）。
- **改动原文对比**（`~/.claude/CLAUDE.md` §2.4 第 2 条）：
  - 原文：`长任务按已定的切分推进，到段落边界主动把接续状态落盘到文件并提示用户开新会话承接，不靠对话历史续接；任务切分归用户给的清单与方案，Agent 不重划任务边界。同一件事未做完不建议重开，换不相干任务时建议清空重开而非压缩续聊。`
  - 改后：`长任务按已定的切分推进，跨会话任务开工先读该任务的 \`notes/<任务名>/STATE.md\`，到段落边界按 skill \`task-notes-by-user\` 把接续状态落盘并提示用户开新会话承接，不靠对话历史续接；任务切分归用户给的清单与方案，Agent 不重划任务边界。同一件事未做完不建议重开，换不相干任务时建议清空重开而非压缩续聊。`
  - 两个触发时刻：接手跨会话任务开工读入口，段落边界落盘并用该 skill 的三步维护动作。
- **删除的记忆**：`~/.claude/projects/C--ZYS-Code-lab-area/memory/skill-routing-boundary.md`，理由是它禁止「全局规则引用具体 skill」，与本次决定冲突。完整原文备份在 `memory/recovery/2026-09-21-skill-routing-boundary.md`。连带清理两处引用：`MEMORY.md` 的索引行删除；`standalone-video-skill-extraction.md` 结尾的 `关联：[[skill-routing-boundary]]` 去掉，其余正文未动。
- **删除时一并失去的内容**：该记忆除「全局不绑定具体 skill」外，还有一条 2026-09-03 精简拍板的四条判据（①禁建纯域路由器 skill ②与插件重叠的自建 skill 让位插件 ③带真资产的路由器先收窄不删 ④判定前先查插件库实际内容）。这四条与本次决定不冲突，目前只存在于备份文件里，用户未指示另行安置。
- **`task-notes-by-user` 的 description 改触发句**（`~/.claude/skills/task-notes-by-user/SKILL.md` frontmatter）：
  - 原文：`跨多轮会话的任务把接续笔记按「入口 → 索引 → 单条」三级存放在仓库根 notes/<任务名>/，每条一个文件、按会话分目录、索引只放指针；新建、追加或整理任务笔记时使用。`
  - 改后：`跨多轮会话的任务把接续笔记按「入口 → 索引 → 单条」三级存放在仓库根 notes/<任务名>/。跨会话任务开工接手、会话压缩（/compact）前后、定期整理维护时使用。`
  - 三处改动：触发句由动作名（「新建、追加或整理任务笔记」——模型得先知道自己要写笔记才轮得到这句）换为情境时点；按 `instruction-engineering-by-user/SKILL.md:147`「description 尽可能短，只说明 what 和 when」删掉「每条一个文件、按会话分目录、索引只放指针」，该细节正文已有；用户说明笔记的用途就是补 `/compact` 的损失，故把「会话压缩（/compact）前后」列为触发时点。
  - 常驻成本与原文基本持平。
- **skill 正文两处改动**（`~/.claude/skills/task-notes-by-user/SKILL.md`）：
  - ①「与相邻机制的区别」的「什么时候写」判据（改后第 87 行）：原文 `判据是可携带性，只有工作真的要移动到别处时才写文件——换宿主、换目录或仓库、交给同事、中途分叉出一支独立支线。同一宿主、同一目录、只是从规划转到实现，用 /compact。` 改后 `判据是压缩损失。自动摘要挑不出来的（为什么这么选、被否掉的路子、下一步、未决）在压缩或切换前落盘。可携带性不设门槛：换宿主、换目录或仓库、交给同事、分叉出独立支线照写，同宿主同目录的长任务同样写。` 理由：用户说明笔记的用途就是补 `/compact` 的损失，原判据末句把同宿主同目录的长任务推给 `/compact`，与本 skill 末句「自动摘要挑不出来的『为什么这么选』和『下一步』只有当事人挑得出来」不同调。
  - ②「维护动作」新增一段（改后第 74 行）：`定期维护：入口超过一屏、或索引长到扫不完时整理一次。入口的明细外移到索引或单条；索引里已过期且不再适用的行删掉；单条正文过期就地改。判定不改的条目、已成规则的条目（标「已落地」）不删。` 理由：用户提出三级结构即渐进式披露，代价是定期维护并删掉无用条目。与既有三处「不删」的划界为：该删的是入口膨胀与真过期条目，原有的「判定不改的照旧留」管任务内条目，两者不冲突，用户认可该判读。
- **验证**：改后按行数与字符数核对全局 `CLAUDE.md`——233 行 / 7204 字符（预算 240 行 / 7000 字符，规则写明「日常按行数看」，行数口径达标，字符口径超出，超出部分为本次改动之前既存）。记忆文件删除后 `recovery/` 备份读回在位；`MEMORY.md` 与 `standalone-video-skill-extraction.md` 改后无残留引用。description 改后原生读取读回一致，且宿主随即按新描述重新注册该 skill（本轮系统提示中的 skill 列表已是新文案），热重载生效。skill 正文两处改后原生读取读回一致。
- **回退**：全局 `CLAUDE.md` 按上列原文替换回；记忆文件从 `memory/recovery/2026-09-21-skill-routing-boundary.md` 复制回原名，并在 `MEMORY.md` 恢复索引行、在 `standalone-video-skill-extraction.md` 结尾恢复关联指针；`task-notes-by-user/SKILL.md` 的 `description` 与正文两处均按上列原文替换回，其中「维护动作」新增的那一段整段删除。

### 自建 skill 正文瘦身（2026-09-21，用户要求，8 个 skill）

- **出处**：用户要求对自己 8 个偏大的自建 skill 做正文瘦身，用 `/skill-auditor-by-user` 起手。经提问确认两点：范围＝全部 8 个大件，瘦的层＝`SKILL.md` 正文（不含附属资产）。此前的盘点结论：自建 skill 总计约 200 KB，这 8 个的 `SKILL.md` 占 142.2 KB（71%）；description 合计仅约 7.5 KB，不是开销大头，触发后加载的正文本体才是。
- **判据**：逐句做 no-op 测试——删掉这句，agent 的行为会变吗（相对模型的默认行为，不相对作者意图）。只删三类：①同一事实在本文件别处已写全 ②版本沿革、迁出来历等读者用不到的过程记录 ③已被清单/表格/正文吸收的死规则。外移内容一律按用户既有原则用原文搬走，不改写成摘要。
- **位置与改动**（`~/.claude/skills/<name>/SKILL.md`，括号内为字节数变化）：

  1. `skill-auditor-by-user`（15032→14127）：删文件尾部 HTML 注释（与 `references/MAINTENANCE.md` 的「变更门禁」同句重复，版本沿革归 `CHANGELOG.md`）。`CHANGELOG.md` 加 `[v2.3.1]` 一条。
  2. `coding-workflow-by-user`（26465→25383）：删开头「来源：CLAUDE.md 2026-07-29 瘦身迁出（§1.1-1.4 / §2 / §3 / §4 原文）」；§1.3「审查动作清单（与 §1.3 三查互补）」改为「审查输出与顺序」（原三条里一条是「审查三维」第 1、2 项的复述，删，标题随实际内容改准）；「删错了怎么找回」四条 bullet 压成一段（三条讲同一件事）。frontmatter `version` 1.7.0→1.7.1，`CHANGELOG.md` 加 1.7.1 一条。
  3. `skill-trimmer-by-user`（24918→21433）：开头五层来源段改为一句 + 指针；核心立场 #3 去掉 Superpowers 套件措辞；删「本机叠加规则 #11」与整张「已定冲突」三行表（三行与 #9/#10/#11 完全重复），余下清单改名「本机决议」并重编号 1/2/3；「skill 两种形态」的正确性更正压成一句当前事实；删已不存在的 `skills/learned/` 条目（核对过目录不存在）；「套件时机」表去 SP 列；删「保留-SP套件」档并从网页判定映射去掉；`（§6.1）` 补成 `（CLAUDE.md §6.1）`；删红线里「不审 Superpowers 套件」条；合并两条重复的 `skill-auditor-by-user` 条目，删 `skill-up`、`skill-slimming` 两条已吸收的；删尾部 HTML 注释；收尾清「执行移动用 `mv` 到 `_weak-model-backup/`（软链）或 lab-area 备份（直管目录）」里的软链/直管残留（该区分已在上文声明作废），改为 `archive/_weak-model-backup/` 或 lab-area exp 目录。
  4. `instruction-engineering-by-user`（23882→18029）：新建 `references/review-basis.md`，把六条审查基准（两个负担 / 信息层级 / 正面陈述 / 锚定词 / context pointer / 归置相邻）连出处整段原文搬入；SKILL.md 原位留一句软依赖指针（六条判据垫在检查表之下，九项检查本身可直接执行，判据只在两项冲突或拿不准时定夺）；删一处已移出的长出处段；删文件尾部 `# 边界` 一节（三条断言在 L64/L68/L76/L173/L189/L227 均已覆盖），连带删掉删除后悬空的末条 bullet。
  5. `content-to-note-by-user`（20527→19261）：`## 相关文件` 的 12 项脚本逐条清单压成一段（脚本清单见 `scripts\`，每个脚本 `--help` 有完整参数）并保留 references 与自测入口；`check_environment.py` 补一句 `--json` 用途；删「检查依赖和可用路线」小节（与「依赖与环境检查」节重复）；第 4 节去掉重复的 CDP 句；微信公众号节合并重复的「微信 UA + 跟随 302」表述，去掉冗余坑条目，`原理：` 改为行内括注。
  6. `article-writer-by-user`（11389→10134）：概述风格模式补「按本项目的风格写作」触发词（吸收 §7.2 的额外信号）；删 §7.1 模式判断与 §7.2 风格模式判断（与概述两张表重复）；§7.3-§7.9 顺次重编号为 §7.1-§7.7，两处交叉引用 `§7.7`→`§7.5` 同步改；新建 `references/prompt-templates.md`，把 §8 使用模板（默认模式与 JavaGuide 模式的创作/优化四段提示词）原文搬入，原位改标题为「§8 调用模板」加指针并在 references 清单登记；删尾部 HTML 注释。
  7. `drawio-chart-by-user`（10897→9163）：Step 3 生成前检查清单补两项（边框用语义类别色或 `strokeColor=none`、全图统一系统字体栈）；删「七、使用示例」（三例与 Step 1 决策表重复）；「三、操作流程」「五、文件命名规范」去掉与文内编号体系不符的中文序号；删「九、不要做什么（反例清单）」11 行（约九成与失败模式表和 Step 检查清单重复，其中 `>50 节点` 与失败模式表的 `>30 节点` 数值互相冲突，删后以失败模式表为准）；删尾部 HTML 注释。
  8. `drawio-article-illustration-by-user`（9090→7648）：删「## 反模式：这些情况不要配图」六条，其中四条与上文「不配图条件」重复，把独有的两条（图里出现正文没提的概念/缩写/组件、一篇文章配 10+ 张图）并入「不配图条件」；「与 drawio-chart-by-user skill 的协作」的 16 行 ASCII 示意图压成一段文字，信息量不变；「校验报告模板」18 行代码块压成一段（检查项、结果、说明、综合判断、修改建议）；删尾部 HTML 注释。

- **合计**：8 个文件 142200 → 125178 字节（-11%），1244 → 1108 行。逐个：skill-auditor -6%、coding-workflow -4%、skill-trimmer -13%、instruction-engineering -24%、content-to-note -6%、article-writer -11%、drawio-chart -15%、drawio-article-illustration -15%。
- **核对过的事实**：外部锚点未受影响——全局 `CLAUDE.md` 引用的 `coding-workflow-by-user` §1.6 与 `ai-product-development-by-user` 引用的 §1.3.1 在改动后仍是 H2 标题（`SKILL.md:164`、`SKILL.md:101`）。删除内容的悬挂引用全量搜过（`保留-SP套件`、`已定冲突`、`审查动作清单`、`反模式`），命中的都是别的 skill 里同名的自有小节或 `CHANGELOG.md` 里的历史记录，无一处指向本次删掉的内容。`article-writer-by-user` 重编号后两处 `§7.5` 引用指向「一次性展开并冻结全篇细骨架」，语义正确。新建的两个 references 文件（`instruction-engineering-by-user/references/review-basis.md` 5911 字节、`article-writer-by-user/references/prompt-templates.md` 1011 字节）存在且被 SKILL.md 正确指向。
- **本次未处理的既有冲突**（改动前就存在，不在瘦身范围，留给用户定夺）：①`coding-workflow-by-user/SKILL.md:26`「禁止读写 /tmp 目录下的内容」与 `drawio-chart-by-user/SKILL.md:153`「写入 `%TEMP%`（Windows）/ `/tmp`（Unix）」、`drawio-article-illustration-by-user/SKILL.md:89`「尝试写入 `/tmp` 或 `%TEMP%`」冲突；②`skill-trimmer-by-user/SKILL.md:11` 定义五层标记（`【OpenAI 官方文章】`/`【补充来源】`/`【补充框架】`/`【本机决议】`/`【实践】`），而同 skill 正文与 `references/evidence-sources.md` 实际用的是四层（`【工具】`/`【文章】`/`【框架】`/`【实践】`），两套未对齐。
- **验证**：8 个文件改动后均原生读取读回，内容与预期一致。改动前后字节数与行数逐文件比对，见上。删除断言前逐条在文件内 grep 确认已有等价表述（例如 `instruction-engineering-by-user` 删掉的末条 bullet，其三条断言分别在 L64/L68/L76/L173/L189/L227 命中）。`coding-workflow-by-user` frontmatter `version` 与 `CHANGELOG.md` 1.7.1 条目一致。
- **回退**：改动前的逐字副本在 `~/.claude/tmp/skill-trim-20260921/<skill>/SKILL.md`（临时目录，8 个齐全）。其中 4 个（`skill-trimmer-by-user`、`content-to-note-by-user`、`drawio-chart-by-user`、`drawio-article-illustration-by-user`）改动前工作区干净且在版本控制内，可直接 `git checkout -- skills/<name>/SKILL.md` 还原；另外 4 个用不了 git——`coding-workflow-by-user` 是从 `code-change-workflow-by-user` 改名而来且尚未提交（未跟踪），`instruction-engineering-by-user`、`skill-auditor-by-user`、`article-writer-by-user` 在本轮开工前就已是已修改状态（`git checkout` 会退回更早的版本，丢掉用户自己先前的改动），这 4 个只能用 `.bak` 副本还原。`skill-auditor-by-user` 与 `coding-workflow-by-user` 的 `CHANGELOG.md` 新增条目按标题整段删除即可回退。两个新建的 `references/*.md` 是原文搬迁，还原 SKILL.md 后删除即可。

### /tmp 禁令对齐与 skill-trimmer 标记体系重组（2026-09-21，用户拍板）

上一条瘦身登记的「本次未处理的既有冲突」两项，用户逐条给了处置：①遵守 `§1.0` 的 `/tmp` 禁令，另两个 skill 换位置；②「系统都重新组织」，范围限定 `skill-trimmer-by-user`。

#### ① `/tmp` 禁令对齐

- **依据**：`coding-workflow-by-user/SKILL.md:26`「禁止读写 /tmp 目录下的内容」是权威，且该条自己给了替代位置——「你应该输出在当前目录下的一个特定的用于存放中间结果的目录；该目录需要被 gitignore」。与全局 `CLAUDE.md` §8 的 `.claude/tmp/` 及 `docker-only-by-user/SKILL.md:31` 一致，故取 `.claude/tmp/`。
- **改动**：`drawio-chart-by-user/SKILL.md` 失败模式表第 9 行「写入 `%TEMP%`（Windows）/ `/tmp`（Unix）」→「改写当前目录下的 `.claude/tmp/`（需被 gitignore）」；`drawio-article-illustration-by-user/SKILL.md` 失败处理「尝试写入 `/tmp` 或 `%TEMP%`」→「改写当前目录下的 `.claude/tmp/`（需被 gitignore）」。
- **同类问题仍在，未处理**：`agent-reach` 有 6 处 `/tmp`（`SKILL.md:64,88`、`references/social.md:141`、`references/video.md:17,20,29,53,77,94`），其中 `SKILL.md:88` 明确要求「不要在 agent workspace 创建文件。使用 `/tmp/` 存放临时输出」。它是外部项目，用户本轮只点了自建的两个，未授权改动外部 skill。（2026-09-24 注：该 skill 已归档，本条不再需要处理。）

#### ② `skill-trimmer-by-user` 标记体系重组

- **改动前实际状态**：不是报告里说的「两套」，是**四套并存**。`SKILL.md:11` 声明五个标记（`【OpenAI 官方文章】`/`【补充来源】`/`【补充框架】`/`【本机决议】`/`【实践】`），同一句里先写「四类」再写「五层」末句又写「四层」；`SKILL.md` 正文实际只用其中四个（`【OpenAI 官方文章】` 在 `:32` 写成了普通括号）；`references/evidence-sources.md` 用 `【工具】`/`【文章】`/`【框架】`/`【实践】`；`references/retention-rubric.md` 用 `【文章】`/`【本机】`/`【实践】`/`【框架】`。逐条对过内容确认 `【补充来源】` ≡ `【文章】`（`:34` 装前反向测试、`:35` 维护量 <20、`:36` 描述列表预算三条都落在 `evidence-sources.md` 的 JavaGuide 段）。
- **用户选定方案**：按优先级分三层——`【本机】` 用户拍板与本机先例，覆盖其余全部；`【外部】` 外部来源的判定基准，具体出处写在判据后面；`【工具】` skill-slimming 的工具资产，只出工具不出判据。
- **改动**：`SKILL.md` 的 `:11` 声明段重写为三层定义；`:25` `【补充来源】` → `【外部】`；`:34/:35/:36` `（新增【补充来源】）` → `（JavaGuide 2026-08-13 文新增）`；`:37` `（新增【实践】，来自 SkillHub 内容治理复盘）` → `（腾讯 SkillHub 内容治理复盘）`；`:104/:109/:110/:116/:118/:120` `【补充框架】` → `【外部】`；`:112/:124` `【实践】` → `【外部】`；`:122` `（【补充来源】规则分流框架）` → `（JavaGuide 规则分流框架）`；`:184` 输出契约由「标清是五个来源层中的哪个」改为「标清是【本机】还是【外部】，标【外部】的写出具体出处」；`:199` references 清单的「五层判定依据」改为「三层判定依据」并列出三个标记。`references/evidence-sources.md` 节首加三层与出处的对应说明，来源节四个段落改为「**【工具】层**」「**【外部】层出处一 · JavaGuide 两篇**」「**出处二 · 主流框架调研稿**」「**出处三 · 腾讯 SkillHub 复盘**」；`:5` 节标题、`:14`/`:15` 括注同步。`references/retention-rubric.md` 的 `:6` 三层说明重写，`:21/:25/:29` 括注、`:52/:57` 节标题、`:111/:113/:123/:127/:131/:142/:150` 标记全部改到新体系。
- **顺带修掉的三处实质缺陷**（改动前既有，核查标记时发现）：
  1. **`SKILL.md:32` 来源错标**：原文写「套件流程型要重审启用时机（**OpenAI 官方文章**原则）」，但 `retention-rubric.md:59` 对同一段判据自证来源是「判据（**文章**为什么「很少再用 Superpowers」）」——Superpowers 正是 JavaGuide 2026-07-23 文的标题主题，同节还写「文章作者现在偏爱 mattpocock/skills」，与 JavaGuide 那篇一致；而 `evidence-sources.md` 从头到尾没有 OpenAI 这一层的登记（`installing/` 台账里唯一那篇 OpenAI《Rethinking skills and prompts for GPT-6 Astra》登记在 `instruction-engineering-by-user` 名下，用途是统一审查指令文件）。已改为「（JavaGuide 2026-07-23 文主论点）」，不留错标痕迹。附带结果：`【OpenAI 官方文章】` 这一层随之消失，五层变三层不再缺出处。
  2. **「本机决议」两清单编号歧义**：`SKILL.md:39` 的清单是 3 条，`retention-rubric.md:81` 的清单是 5 条，而 rubric 内部用 `#2`/`#4` 引用自己那份（`:121` 弱模型兜底、`:137` 留主路径）。第一轮瘦身在 SKILL.md 重编号后，两处的 `#3` 含义不同（SKILL.md 是「分类建议必须用户拍板」，rubric 是「Superpowers 不审」），且 `#4` 在 SKILL.md 里不存在。已改为两处都按条目名引用（「流程型/E 类 → 留兜底」「同能力多个 → 留 router 指定的主路径那个」），SKILL.md 的清单同时去掉编号改用条目名，并注明两处按名字对应不按编号。
  3. **「冲突 #2」断链**：`retention-rubric.md:65` 引用「冲突 #2」，而定义该冲突清单的 `SKILL.md`「已定冲突」表在第一轮瘦身时被删（判定为与 #9/#10/#11 重复）。`retention-rubric.md:6` 自己写明「冲突处在第四节『本机护栏』逐条标注张力」，故改为直接指向第四节该条下的「与文章张力」标注。
- **验证**：全文 `【…】` 标记扫描后只剩三种——`【外部】` 26 处、`【本机】` 8 处、`【工具】` 5 处；旧标记（`【文章】`/`【框架】`/`【实践】`/`【补充来源】`/`【补充框架】`/`【OpenAI 官方文章】`/`【本机决议】`）全量搜索零命中；`retention-rubric.md` 章节标题一至十完整，章内引用（「第一节第 1 问」「第三节」「第四节」「第十节」）逐条确认目标存在；外部引用搜过，命中的只有 `skill-trimmer-workspace/` 里 2026-08-13 那次审计的历史产物，用的是「本机决议 #N」档位编号而非 `【】` 标记，属历史记录不改。`git diff --check` 干净。文件大小：`SKILL.md` 21651 B、`references/retention-rubric.md` 14495 B、`references/evidence-sources.md` 7086 B。
- **未处理**：`retention-rubric.md` 仍留着 Superpowers 相关残留——第四节第 3 条「Superpowers 套件 → 不审（2026-08-19 更新：SP 插件已卸载，本决议失效存档。）」、第三节「套件流程型」节末的「只对**非 SP** 套件或散装流程型 skill 生效」限定、第二节第 92 行同处。第一轮瘦身把 `SKILL.md` 里的 SP 内容删净了，两份 references 未同步。该条目自称「失效存档」，保留了不确定是否用户有意，未擅自删。
- **回退**：三份文件在版本控制内且本轮开工前工作区干净，`git checkout -- skills/skill-trimmer-by-user/SKILL.md skills/skill-trimmer-by-user/references/retention-rubric.md skills/skill-trimmer-by-user/references/evidence-sources.md` 可整体还原到本轮之前。两个 drawio skill 的两行同样用 `git checkout` 还原（两个文件开工前也干净）。改动前的逐字副本另在 `~/.claude/tmp/skill-trim-20260921/skill-trimmer-by-user/`（临时目录）。

### task-notes-by-user 单条笔记改成固定字段、只记重点（2026-09-21，用户要求）

- **出处**：用户提出「记笔记的时候只记结构化的笔记，并且是只记重点。具体记什么重点可以先想想」。此前单条笔记的模板只写「正文」两字，没有形式约束，实测产物写成两段议论文；索引的 hook 长成 100 到 260 字的分号串；入口 `STATE.md` 涨到 137 行 / 10,720 字节，超过 skill 自定的「一屏」。经 AskUserQuestion 确认两项：字段取五字段并另加「其他」兜底；存量笔记整目录删除。
- **位置**：`~/.claude/skills/task-notes-by-user/SKILL.md` 的八个小节——三级表格、入口文件、索引文件、单条笔记、写作要求、维护动作、任务收尾后的处置、与相邻机制的区别。
- **内容**：
  - 单条笔记的模板由「正文」改为固定字段 `材料 / 结论 / 取舍 / 改动 / 未决 / 其他`，并附一份填好的示例。硬约束五条：一个字段一行、一行只放一件事、字段之外的正文不写；有字段没内容就删掉那一行（「材料」与「结论」必写，「改动」没有改动写「无」）；一个字段里超过三条要点即拆条；结论写成判断，机制解释与举例与推导过程留给原文、引路径；日期不写，会话目录名里有。
  - 材料里读出来的收获先问去处：要长期留下的写进 skill、memory 或 `docs/`，笔记只记改到哪并留指针。
  - 索引的 hook 改为逐字照抄单条「结论」那一行，原句「hook 写这一条的结论」被它取代；索引与单条只有这一处重复。
  - 入口五块改为一行一条短句、一行指到单条或会话目录；未决一行一条、一条一句话，内容超过一句的落成单条。
  - 写作要求原「必要」一条换成「只记重点」，列出不记的四类：材料的复述与解释、讨论过程与轮次、改动的具体内容（git 记得）、已被改掉的说法。「无遗漏」去掉「改了哪些文件漏了不算」半句，「改动」字段已承担该事。
  - 自足口径由「只读这一份也能接着做」改为「读这一份、加上它引的材料就能接着做」，与「只记重点」不再互相拉扯。
  - 「任务收尾后的处置」首句由「随分支并入主干留档，不删、不改写成摘要、不搬去 `docs/`」改为「把笔记目录列给用户，留档还是删除由用户定，用户不说就留档」；「与相邻机制的区别」里 memory 那条的结尾「留档」同步改为「处置」。
- **依赖**：无。skill 不引用宿主专有工具。
- **验证**：改后全文 115 行读回一致，八个小节的改动互不冲突。改前副本 `~/.claude/tmp/task-notes-fields-20260921/SKILL.md`（93 行，逐字抄自改前读回的内容）与改后文件做 `diff`，差异只落在本轮编辑区间内，没有别的行被动过。
- **连带删除**：结构实例 `lab-area/notes/2026-09-21-context-hygiene/`（39 个文件 / 154,349 字节）按用户指令删除，`lab-area` 仓库提交 `c642bf2`；父提交 `7add926` 仍可达，`git checkout 7add926 -- notes/` 可取回。本台账早前各节里 7 处指向该目录的路径（出处、验证、回退）随之指向空目录，需要明细时按该提交取回。
- **回退**：该 skill 文件在 `~/.claude` 仓库里未被跟踪（`git status` 显示 `?? skills/task-notes-by-user/`），git 还原不了；用 `~/.claude/tmp/task-notes-fields-20260921/SKILL.md` 覆盖回去即可。

### task-notes-by-user 加自动压缩计数触发 hook（2026-09-21，用户要求）

- **出处**：用户提出「`task-notes-by-user` 加个 hook 提示，因为这个技能的触发条件也很奇怪，比如自动 compact 三次之后第四次 compact 之前就提示模型使用」。触发条件由用户给定：自动压缩累计 3 次。
- **位置**：新建 `~/.claude/hooks/scripts/task-notes-reminder.py`、`~/.claude/hooks/tests/test_task_notes_reminder.py`；改 `~/.claude/settings.json`（新增 `hooks.PreCompact` 段，`hooks.SessionStart` 追加第 4 组）。
- **事件与匹配**：`PreCompact` matcher `auto` 跑 `task-notes-reminder.py pre`；`SessionStart` matcher `compact` 跑 `task-notes-reminder.py start`。
- **为什么是两个事件**：本机 `C:\Users\zys31\.local\bin\claude.exe` 内置代码里，`PreCompact` 与 `PostCompact` 的执行器（`Nie`/`j5e`）返回值只有 `userDisplayMessage`，即只显示给用户、进不了模型上下文；`hookSpecificOutput` 的联合类型没有这两个事件的变体。能送进模型上下文的是 `SessionStart`、`UserPromptSubmit` 等。压缩流程中先 `post_compact` 钩子、再 `nG(session,"compact",…)` 触发 `SessionStart`，所以由 `PreCompact` 记数、由 `SessionStart` 读同一份状态文件后输出。
- **计数口径**：只数 `trigger == "auto"`，手动 `/compact` 不计——手动压缩是用户主动发起。计数写在 `~/.claude/task-notes-reminder/<session_id>`，每文件一个整数，目录按 mtime 保留最近 50 个。这两个 hook 装上之前的压缩次数不计，计数从装上那一刻开始。
- **输出文案**：模型侧 `hookSpecificOutput.additionalContext` = 「你该开始笔记模式了：调用 task-notes-by-user。」；用户侧顶层 `systemMessage` = 「笔记模式已开启」（均已核对 `systemMessage` 是「显示给用户的 UI 消息」，上限 4000 字符）。自动压缩累计 ≥3 时每次压缩后都提醒。
- **依赖**：Python 3.12（`C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`）。无第三方包。
- **验证**：`python.exe ~/.claude/hooks/tests/test_task_notes_reminder.py` 21 项断言全过（`ALL PASS`），其中包含读回 `settings.json` 断言两处接线与 matcher 正确；`settings-degrade-guard.py` 喂 `SessionStart` payload 后无告警输出（rc=0，快照未判降级）；改 `settings.json` 两次编辑各触发一次 `settings-sync-auto.py`，均返回「已自动同步 cc-switch DB: [DONE]」。**未验证**：真实压缩触发链路（需要对一个会话实际跑满 3 次自动压缩才能观测），`~/.claude/task-notes-reminder.log` 会记录每次 `pre` 计数与每次提醒，首次真实压缩后看该文件即可确认。
- **回退**：删除 `settings.json` 里 `hooks.PreCompact` 整段与 `hooks.SessionStart` 中 matcher 为 `compact` 的那一组，再删三个新文件（脚本、测试、状态目录 `~/.claude/task-notes-reminder/`）。`settings.json` 改动前副本：`~/.claude/settings.json.bak-autocompact-20260918_151656` 不含本轮改动，可按需对照。

---

### 21 个自建 skill 按上下文卫生方法精简（2026-09-21，用户要求）

- **出处**：用户要求「skill 体积更小、更精简、更准确的命中、更优的效果」，范围限定「全过，只动自建的，agent-reach 和 agent-browser 不是自建的」。方法取自 Matt Pocock 插件 `mattpocock-skills@1.2.3` 的 `skills/productivity/writing-for-agents/SKILL.md` 与 `SKILL-MECHANICS.md`。
- **范围**：21 个自建 skill。10 个 model-invoked：`dev-status-by-user`、`dev-clean-by-user`、`bidirectional-steelman-by-user`、`toolchain-pitfalls-by-user`、`parallel-delegation-by-user`、`docker-only-by-user`、`install-ledger-by-user`、`task-notes-by-user`、`article-writer-by-user`、`coding-workflow-by-user`。11 个 user-invoked：`skill-trimmer-by-user`、`skill-auditor-by-user`、`instruction-engineering-by-user`、`content-to-note-by-user`、`improver-skill-by-user`、`drawio-chart-by-user`、`drawio-article-illustration-by-user`、`company-discovery-evaluation-by-user`、`cc-switch-setting-sync-by-user`、`ai-product-development-by-user`、`awesome-design-md-by-user`。第三方 5 个未动：`agent-reach`、`agent-browser`、`archify`、`eli5`、`leader`；归属按本台账与 `skill-install.md` 判定，不按目录名前缀。
- **改动**：四类。一、删除重复：同一规则在两处出现时只留权威版本。删掉的有 `skill-auditor-by-user` 的「反模式」整节（10 条全部与前面检查表逐字重复）、`company-discovery-evaluation-by-user` 的「最终检查」整节（6 条全部重复）、`skill-trimmer-by-user` 红线 11 条里的 9 条、`drawio-chart-by-user` 失败模式表 10 条里的 5 条。二、删除复述宿主环境的缓存：`improver-skill-by-user` 复述全局 `CLAUDE.md` §1.3 确认线的整段、`ai-product-development-by-user` 复述 `disable-model-invocation` 机制的两句。三、修悬空引用：`article-writer-by-user` 的编号体系删除后，4 个 `references/` 文件里「下沉自 SKILL.md §X」的溯源句与 2 处正文引用一并改准，`§6.10 AI 找弹药` 改标到实际所在的 `javaguide-style.md`。四、下沉与建索引：`coding-workflow-by-user` 的 §1.4、§1.6、§3 三节移入 `references/`，入口保留节号与指针行。
- **未改**：`coding-workflow-by-user` §1.0 编码硬约束（全局 `CLAUDE.md` 原文搬入，禁止式措辞是硬约束的适用形式）；11 个 user-invoked skill 的 `description`（不常驻，长度不占预算）；第三方 skill；`drawio-chart-by-user/README.md`（给人看的说明文档，与 `SKILL.md` 分工不同）。
- **验证**：持久脚本 `~/.claude/skill-slim-audit-2026-09-21/measure_all.py` 逐文件读回后剥离空白计数。10 个 model-invoked 的 description 常驻字符 961 → 821（−14.6%），正文 569 → 479 行（−15.8%）；11 个 user-invoked 正文 1249 → 1174 行（−6.0%）；21 个合计正文 1818 → 1653 行（−9.1%）。三处 description 变长是有意取舍（`dev-status-by-user` +19 加触发锚点，`parallel-delegation-by-user` +3 补触发分支），`install-ledger-by-user` 一度 +39 已压回 −2。删节后全库 `§` 悬空引用扫描零命中。10 个 model-invoked skill 的 27 条第一跳请求改前改后逐条对照，主判零不一致。
- **evals 迁移**：Claude CLI 2.1.278 只发现 `evals/**/case.yaml` 或 `prompt.md + graders/*.md`。新增官方布局：`skill-auditor-by-user` 5 个、`instruction-engineering-by-user` 1 个、`parallel-delegation-by-user` 9 个，共 15 个 case；后者原自然语言 assertions 改为 LLM grader。`instruction-engineering-by-user` 增加 `scaffold.sh`。旧格式 9 个文件已有持久备份；删除命令被权限分类器以 `[Irreversible Local Destruction]` 拒绝，现仍在原位，但 runner 不发现它们。
- **evals 验证**：27 个 case 均至少运行一次，命令统一使用 `--no-publish`。首次结果：`coding-workflow-by-user` 3/6、`skill-auditor-by-user` 5/5、`instruction-engineering-by-user` 0/1、`skill-trimmer-by-user` 0/3、`improver-skill-by-user` 1/3、`parallel-delegation-by-user` 5/9。随后修正 runner 合同：`coding-workflow-by-user` 三个失败项重跑 3/3，通过项与未改 case 合并后当前 6 个 case 各有一次通过；`skill-trimmer-by-user` 调整后 3/3；`instruction-engineering-by-user` 两个文件 grader 2/2，但子会话 300 秒超时；`improver-skill-by-user` 仍为 1/3；`parallel-delegation-by-user` 的 1、4 仍失败，2 因费用上限跳过 grader，9 在用户终止前未生成。用户随后明确要求「不用跑了」，不再执行。runner 已报告费用约 1.65 美元；超时 case 显示 0.00 美元，实际计费未知。证据在 `lab-area` 工作树 `output/skill-slimming-evals/`。
- **未验证**：`parallel-delegation-by-user` case 2 调整后的 grader 结果与 case 9 调整后的行为；`instruction-engineering-by-user` 无超时的完整退出；`coding-workflow-by-user` 的三份新 `references` 在真实任务中的表现。`improver-skill-by-user` 调整后仍有两个失败 case，按真实结果保留。
- **回退**：改前全量副本在 `C:\Users\zys31\.claude\backups\skills-before-slim-2026-09-21\`，21 个目录、2267 个文件，已核对各 `SKILL.md` 字节数与改前一致。覆盖对应文件即可回到改前状态；不用 `git checkout` 或 `git restore`，目标文件里有 12 个带开工前的用户未提交改动。测量脚本、description 提取脚本和第一跳命中材料在 `C:\Users\zys31\.claude\skill-slim-audit-2026-09-21\`。

### docker-only-by-user 增加 Docker 产物收尾询问（2026-09-21）

- **出处**：用户要求规划删除 Docker 工作产物，随后明确每项删除前必须询问用户。
- **位置**：`~/.claude/skills/docker-only-by-user/SKILL.md`，新增「任务结束时清理」小节。
- **内容**：任务结束前盘点容器、网络、卷、镜像、构建缓存、日志和挂载目录产物；一次性容器是否使用 `--rm`、常驻服务是否执行 `docker compose down --remove-orphans`，都先列出影响资源并逐项询问用户；卷、数据库文件和挂载目录生成物列出准确路径与用途后询问是否删除；删除后复查资源和台账。
- **依赖**：无新增依赖；沿用现有 Docker 规则与全局删除确认线。
- **验证**：原生读回新增小节，确认自动删除措辞已移除，并保留逐项询问要求；尚未执行 Docker 删除操作。
- **回退**：删除该小节即可恢复修改前的 Docker Skill 内容。

### 上下文卫生增补到七个 Skill（2026-09-21，全局）

- **出处**：Matt Pocock 上下文卫生方法在本机 Skill 体系中的后续应用；用户要求继续优化，范围限定为七个与上下文管理直接相关的自建 Skill。
- **位置**：`~/.claude/skills/coding-workflow-by-user/SKILL.md`、`task-notes-by-user/SKILL.md`、`instruction-engineering-by-user/SKILL.md`、`parallel-delegation-by-user/SKILL.md`、`skill-auditor-by-user/SKILL.md`、`skill-trimmer-by-user/SKILL.md`、`improver-skill-by-user/SKILL.md`。
- **内容**：编码工作流增加构思/规格/拆票与实现工单的上下文相位边界、相位切换前的接续材料和隔离调查；任务笔记明确相位边界与 handoff 的 agent 交接职责；指令工程增加知识分层与固定成本核算；委派流程增加主会话中间材料与 worker 摘要成本判据；Skill 审计增加上下文生命周期和可选隔离执行检查；Skill 精简增加路由、固定注入、正文读取和回流材料四项成本；Skill 改进评测增加上下文成本观察项。
- **依赖**：无新增脚本、插件、配置或运行时依赖；`context: fork` 仅作为宿主提供时的可选审计项。
- **验证**：七个目标文件均已写入并通过关键词定位；全局 Skill 仓库 `git diff --check` 通过；项目工作树 `git status --short`、`git diff --stat`、`git diff --cached --stat` 均无输出。本轮未运行 Skill eval 或真实编码任务。
- **回退**：按本条列出的七个文件和新增规则逐段删除本轮句子，保留此前用户改动；不使用 Git 回退覆盖既有未提交内容。

---

### Skill 根入口减量方法接入审计体系（2026-09-22，用户确认）

- **出处**：用户先要求研究 Matt Pocock 如何缩小 Skill 且保持效果，随后澄清目标为「把优化思路、方法论加入某些自建 Skill」，并确认采用单一事实来源方案。
- **职责**：`skill-auditor-by-user` 保存完整减量方法；`skill-trimmer-by-user` 只在能力应保留但根入口出现 `sprawl` 时转介，不复制方法；`instruction-engineering-by-user` 与 `improver-skill-by-user` 已分别拥有跨文件逐句剪除和同条件 gate，不重复增加正文。
- **位置**：修改 `skills/skill-auditor-by-user/SKILL.md`、`CHANGELOG.md`、`test-prompts.json`，新增 `references/skill-size-optimization.md` 与 `evals/size-optimization/case.yaml`；修改 `skills/skill-trimmer-by-user/SKILL.md` 本地分流一行。
- **方法**：减量审计先区分固定注入、description、调用正文和回流材料，再把内容归为根入口步骤、根入口参考、分支参考、环境事实或可删除内容；分支专用原文迁入 reference，context pointer 同时写清读取条件、材料内容和读取强度；只在有证据时删除 duplication、sediment、relevance 或 no-op；安全、权限、业务和验收门禁不得削弱。
- **等效门禁**：基线与候选使用相同模型、宿主、工具、场景、runs、超时和 grader；逐项通过 target、guardrail、holdout 后再比较真实上下文成本。无法观测时记 `not-run`，不把字节估算冒充运行值；正式 gate 可转 `/improver-skill-by-user`。
- **测试资产**：`test-prompts.json` 新增 id 13；新增 Claude CLI 可发现布局 `evals/size-optimization/case.yaml`，检查「减量审计」「信息层级」「baseline」「holdout」。
- **验证**：根入口指针、参考文件五个核心章节、`skill-trimmer` 转介和两项新增文件均已定位；目标文件 `git diff --check` 通过。当前 `skill-auditor-by-user/SKILL.md` 为 199 行、14647 字节，按需参考为 132 行、6932 字节，`skill-trimmer-by-user/SKILL.md` 为 194 行、21019 字节。尝试通过 Skill 工具验证实际加载时，宿主按 `disable-model-invocation: true` 正确拒绝并要求用户显式运行 `/skill-auditor-by-user`；因此动态模式输出与新增 eval 记为 `not-run`，没有宣称行为已通过。
- **既有改动保护**：开工时全局配置仓库已有大量未提交改动，目标 Skill 和本台账也已修改；本轮使用完整行锚点追加，没有覆盖、清理、暂存或提交既有内容。
- **回退**：逐项删除本条列出的新增参考、评测和 v2.4.0 记录，并撤去根入口减量模式与 `skill-trimmer` 转介；保留开工前已有未提交内容，不使用 Git 回退。

### 自建 skill 精简批次（2026-09-22，用户拍板）

- **出处**：用户指令「精简 skill 库：插件已覆盖大部分通用能力，只留本机定制化 skill」。经 skill-trimmer-by-user 流程盘点全局 `~/.claude/skills/` 26 项（25 目录 + agent-browser junction），逐项拍板后归档 2 项，保留 24 项。
- **归档 `drawio-article-illustration-by-user`**（自建）：与 `drawio-chart-by-user` 职责重叠（前者管配图决策/图文校验，后者管图表生成/导出），用户拍板归档合并。移动至 `~/.claude/backups/skills-before-slim-2026-09-22/drawio-article-illustration-by-user/`。
- **归档 `eli5`**（第三方，归属见 skill-install.md 第 70-76 行）：模型原生「讲人话」能力，零资产零使用，2026-08 已标记冷。移动至 `~/.claude/backups/skills-before-slim-2026-09-22/eli5/`。
- **连带改动**：`drawio-chart-by-user/SKILL.md` 与 `references/xml-templates.md` 各删一处指向被归档 skill 的死引用；`~/.claude/.gitignore` 删除 `!skills/drawio-article-illustration-by-user/` 白名单行。
- **未归档但用户拍板保留**：bidirectional-steelman-by-user、leader、archify、agent-reach（曾列为通用能力候选，用户未选）。**2026-09-24 更新：`agent-reach` 已归档，本条对其失效**，见 `skill-install.md` 2026-09-24 状态行。
- **验证**：移动后 `~/.claude/skills/` 剩 24 项；死引用 grep 零命中；scan_skills.py 重跑 inventory 更新（见 `~/.claude/skill-trimmer-workspace/inventory.json`）。
- **回退**：从 `~/.claude/backups/skills-before-slim-2026-09-22/` 复制回两目录，恢复 `.gitignore` 白名单行，按 `ARCHIVED.md` 还原 drawio-chart 两处引用；eli5 亦可按 skill-install.md 第 70-76 行命令重装。

### 通用配置防重置加固（2026-09-23，用户确认）

- **出处**：用户指令「保证通用配置正确而且不能被重置修改」，目标是防止 cc-switch 切换 provider 时把已删除的配置键复活并固化。
- **根因**：cc-switch 切换时以 provider 的 settings_config 为起点、把 DB 的 common_config_claude 深合并后写 live settings.json；3 个 claude provider 的 env 潜伏 `CLAUDE_CODE_EFFORT_LEVEL=max`，Codex-公司账号另有 `CLAUDE_CODE_MAX_CONTEXT_TOKENS=372000`（372k 窗口来源），切换后注入 live 并被 settings-sync-auto hook 固化进 DB 快照。
- **修改**：
  - cc-switch DB `providers` 表（app_type='claude' 四个 provider）：删除 env 里的 `CLAUDE_CODE_EFFORT_LEVEL` 与 `CLAUDE_CODE_MAX_CONTEXT_TOKENS`。备份 `~/.cc-switch/backups/sync-backup-20260923_003144.json`。
  - `~/.claude/skills/cc-switch-setting-sync-by-user/scripts/sync_claude_common.py`：PROVIDER_ENV_KEYS 增加 `ANTHROPIC_MODEL`（防切换后固化）。
  - `~/.claude/hooks/scripts/resource-guard.py`：修复 node 误拦——执行 `~/.claude/` 或当前仓库 `.claude/` 下脚本时跳过宿主工具链拦截（10 场景测试 PASS，docker 独占回归 PASS）。
  - `~/.claude/hooks/settings-degrade-guard.py`：新增期望基线检测——env 出现 FORBIDDEN_ENV（EFFORT_LEVEL/MAX_CONTEXT_TOKENS）告警、env 缺失 AUTO_COMPACT_WINDOW 告警、permissions.allow/ask/defaultMode=auto 检查、modelSettings 四模型检查（8 场景测试 PASS）。
  - live↔DB 不一致修复：settings.json 的 opus-5 effort 被外部改为 high（00:24），DB 快照仍是 medium；用户确认以 live 为准，`sync_claude_common.py` 执行后 readback MATCH，dry-run NO-OP。
- **依赖**：无新增依赖；沿用 cc-switch 现有 common config 机制与 settings-sync-auto hook。
- **验证**：切换深合并模拟（复刻 Rust json_deep_merge）四个 provider 均无污染键；sync 幂等 NO-OP；两个 hook py_compile 通过；degrade-guard 真实 live 配置无误报。
- **回退**：DB provider env 改动可从 `sync-backup-20260923_003144.json` 或 `cc-switch.db.bak-20260923-001029`（job tmp）还原；脚本改动逐行撤销；guard 增强删除新增检查段即可。

---

## 环境修剪批（2026-09-23 会话 s1）

需求来源：环境修剪任务（notes/2026-09-23-claude-env-pruning/），边界=第三方只整体去留、自建可优化、轻量化优先。

- **ai-product-development-by-user**：去 3 处 impeccable 插件引用（mermaid 节点 B/D、两表格行、末句菜单说明），改为直接起草 `PRODUCT.md` 与「出 2–3 套文字方向供用户选」。原因：impeccable 插件已禁用（见 tool-install.md 2026-09-23 条）。回退：`~/.claude` git 历史。
- **cc-switch-setting-sync-by-user**：边界情况节新增「四层一致性检查」条目（2026-09-23 EFFORT 复活复盘：注册表/进程 env、live、公共快照、provider env 四层；加键只加 live；删键四层全扫含 providers 表 SQL；症状即信号；改 provider env 后重启 cc-switch）。与凌晨批的 degrade-guard FORBIDDEN_ENV 告警互补。回退：删除该条目。
- **company-discovery-evaluation-by-user**：归档至 `~/.claude/archive-skills/`（0 用，求职场景暂结束，用户拍板）。恢复 = 目录移回 `~/.claude/skills/`。
- **cc-switch DB（容器内操作）**：provider「Codex-个人账号」env 显式钉入 `CLAUDE_CODE_AUTO_COMPACT_WINDOW=200000`（原键缺失，372000 系 freelist 幽灵；与公共快照值一致，防漂移）。备份：`~/.cc-switch/backups/cc-switch.db.pre-autocompact-20260923`。生效需重启 cc-switch。
- 未动：cc-switch-setting-sync 正文其余、drawio-chart 等待裁决中的 skill。

### 持久资料避开临时目录（2026-09-23）

- **出处**：用户发现交接文件 `C:\Users\zys31\.claude\jobs\20223c05\tmp\env-pruning-handoff-2026-09-23.md` 已不存在，要求记录临时目录易被清理，持久资料不能放入其中。
- **位置**：全局 `~/.claude/CLAUDE.md` §8 产物路径规则。
- **内容**：`.claude/tmp/` 与 `$CLAUDE_JOB_DIR/tmp` 只放可丢弃、可重新生成的临时内容；持久化交接、任务状态和重要资料放 `notes/<任务名>/STATE.md`、`docs/`、`output/` 或获授权的 auto-memory。
- **依赖**：无。
- **验证**：目标文件写入成功；规则与现有临时文件、任务笔记、正式文档路径保持一致。未运行服务、构建或测试。
- **未验证**：未复测任务目录的自动清理机制。
- **回退**：将全局 `CLAUDE.md` §8 对应产物路径条目恢复为改动前版本。

### docker-only-by-user 放宽常规清理确认（2026-09-23）

- **出处**：用户确认不希望 Docker 常规操作持续弹出确认，并要求修改；`settings.json` 已配置 `CLAUDE_CODE_AUTO_ALLOW_DOCKER=1` 与 `Bash(docker *)` allow。
- **更正（2026-09-24，据 Claude Code 配置标准实验 3.4 第 1 项实测）**：上一条里的 `CLAUDE_CODE_AUTO_ALLOW_DOCKER=1` **是惰性配置，从不存在**。该字符串在 Claude Code 2.1.281 二进制（`~/.local/bin/claude.exe`，240 MB）中零匹配；`~/.claude/hooks/` 下也无任何脚本读取它（`resource-guard.py` 全文不含任何 `CLAUDE_CODE_*` 引用）。Docker 的放行**完全来自同一句里的 `Bash(docker *)` 等四条 allow 规则**（`Bash(docker *)`、`Bash(docker-compose *)` 及两者带 `MSYS_NO_PATHCONV=1` 的变体）。本条历史记载保留不改，以免抹掉当时的实际操作；该变量已在 `settings.json:33` 移除。
- **位置**：`~/.claude/skills/docker-only-by-user/SKILL.md` 的一次性容器和任务结束时清理规则。
- **内容**：一次性容器默认使用 `--rm`；常驻服务可直接执行 `docker compose down --remove-orphans`；只有卷、数据库文件、绑定挂载目录生成物和其他可能含真实数据的资源继续询问。
- **依赖**：无新增依赖；沿用全局确认线与 Docker 授权边界。
- **验证**：重读当前 Skill 后完成两处规则编辑；目标文件写入成功。未运行 Docker 命令或真实权限弹窗回归。
- **未验证**：Claude Code 实际会话是否已热加载最新 Skill 内容。
- **回退**：恢复一次性容器 `--rm` 和 `docker compose down --remove-orphans` 的旧确认条款。

### 全局确认降噪与范围授权（2026-09-24）
- 同日补记：`sync_claude_common.py` 经两轮只读审查后加固根 JSON/嵌套结构校验、restore 公共环境覆盖与权限标量恢复；`--check` 使用只读单事务读取，`--dry-run` 不创建数据库；SKILL.md 补齐回滚、`ANTHROPIC_MODEL` 和禁止键边界。容器回归、实际 `--check` 与 `--dry-run` 均通过。

- **出处**：用户选择「低打扰安全默认」并补充「明确授权后不重复询问」。
- **位置**：全局 `~/.claude/CLAUDE.md` §1.3、§2.3；`~/.claude/settings.json` 权限列表；`parallel-delegation-by-user`、`coding-workflow-by-user`、`dev-clean-by-user`、`install-ledger-by-user`；`hooks/scripts/resource-guard.py` 及其自测。
- **内容**：可逆、只读、工作树内和容器内常规操作直接执行；用户明确授权的命令、目标或范围内同类动作不重复询问，只有扩大范围、改变目标、影响升级或共享资源串扰才重新确认；委派默认沿用当前配置；资源守卫对缺少硬约束的 Compose、宿主机工具链和无法核验的 Compose 重写直接阻断，跨会话独占容器仍询问；移除过宽的 `git remote*` 权限询问，保留远程 Git 和本地丢弃类操作门槛。
- **依赖**：无新增依赖；保留 `permissions.deny` 硬阻断。
- **验证**：容器内 `test_resource_guard.py` 全部通过，`TEST_RC=0`；覆盖阻断、询问、阻断优先级和原有 Docker 判据。同步检查返回 `SYNC_RC=2`，原因是现有 `settings.json` 的 `CLAUDE_CODE_MAX_CONTEXT_TOKENS` 被同步脚本列为禁止公共环境键；PostToolUse 自动同步同样失败，未擅自删除该键。
- **未验证**：实际 Claude 会话是否已热加载全部 Skill；权限列表改动尚未固化到 cc-switch 公共快照；真实权限弹窗行为待后续同步成功后复测。
- **回退**：按本条位置恢复各文件改动前规则；资源守卫自测同步恢复旧的 `ask` 断言；`settings.json` 恢复旧 `permissions.ask` 列表。

### 自建 skill 去 -by-user 后缀（2026-09-24）

- **变更**：20 个自建 skill 目录去 `-by-user` 后缀；唯一例外 `toolchain-pitfalls-by-user` → `local-env-pitfalls`。本文件此前各条保留旧名——那是当时的事实，同 `coding-workflow/CHANGELOG.md:34` 口径。
- **同期改**：全局 `CLAUDE.md`（13 处）、`.gitignore` 白名单（21 → 20 条，删去已归档的 `company-discovery-evaluation` 死行）、`hooks/` 4 文件（含 `settings-sync-auto.py:7`、`settings-degrade-guard.py:20` 两处代码路径常量）、`docs/session-lifecycle.md`、`plans/` 2 文件（10 处，含 `humble-swimming-scott.md` 一条 skill 脚本路径）、`external-configs/README.md`、lab-area 与 dtsf 记忆及交接文档、skill 内交叉引用（69 文件 133 处）。
- **不改**：`installing/` 全部、各 `CHANGELOG.md`、`archive-skills/`、会话转录。
- **备份**：`~/.claude/backups/skill-rename-2026-09-24/`（含改前逐文件副本与 sha256 校验）。
- **回退**：目录改回原名，`.gitignore` 白名单同步改回。

### 全局 `CLAUDE.md` 增 §5.3 文件内容（2026-09-24）

- **变更**：`~/.claude/CLAUDE.md` 第 5 节加 `### 5.3 文件内容`，3 条：落盘产物字段精简必要、能用符号就不用字；能推出的不写、`→` `←` `|` 代连词与说明句；既有文件是否重写属范围决策、先问用户。
- **依据**：用户当日要求「任何记录在文件里面的，字段应该精简、必要，不能冗余……台账、任务笔记、交接文档这种都应该这样」，并明确「以后都应该遵守」。按本项目定的 M4 分界（必须动手前无差别生效 → `CLAUDE.md`）放常驻位；记忆 `terse-file-content` 留作来由记录。
- **备份**：无独立备份——纯新增 3 行，删去该节即回退。

### caveman 效果并入 §5.1/§5.2（2026-09-24）

- **变更**：`~/.claude/CLAUDE.md` §5.1 加 3 条（删填充词·客套·无对象模糊限定｜短语片段可成句｜术语精确·代码与报错原样引用），§5.2 加 2 条（安全警告·不可逆确认·多步流程切回完整表达｜提交信息与注释不简化）。来源是 caveman 插件 SessionStart 注入的 1,230 字符 ruleset，改写为中文适用版。
- **依据**：用户当日定「caveman 提取到本地、ponytail 不动」。原 ruleset 里删 a/an/the、短同义词等是英文专用，中文无效，故改写非照抄；§5.1 原有「直接肯定句、删空泛总起」已覆盖其一半，只补差值。
- **未做**：caveman 插件**尚未卸载**——等用户新会话验证新文本生效后再卸。卸载会删 `plugins/cache/caveman/caveman/25d22f864ad6`，届时先整份备份。
- **备份**：`~/.claude/backups/claude-md-caveman-2026-09-24/CLAUDE.md.before`（13,317 B 改前全文）。
- **回退**：还原该备份；或删掉 §5.1 后 3 条与 §5.2 后 2 条。
- **备注**：caveman 实际注入的是 `src/hooks/caveman-activate.js` 内的 fallback 常量——SKILL.md 路径算错（`<root>/src/skills/` 不存在），readFileSync 抛错走 catch。故三档注入完全相同（1,230 字符），SKILL.md 从未被读。

### 19 个自建 skill 的 description 改写（2026-09-24）

- **变更**：`~/.claude/skills/` 下 19 个 `SKILL.md` frontmatter 的 `description` 按 S4 重写；其中 `article-writer`、`bidirectional-steelman` 另加 `disable-model-invocation: true`（转 user-invoked）。**只改 frontmatter，正文一字未动。**
- **依据**：REPORT 第 3.3 节 C1/C2；判据 S4（前置领先词·一分支一触发·砍正文已承载的身份说明·禁 no-op·不写否定式）与 S5（只有「模型必须自己够得着」或「被别的 skill 调用」才留 model-invoked）。用户 09-24 确认两项决策：① 转 user-invoked ② 删 4 条交叉排除句。
- **效果**：自建常驻 description 857→292 字符（每轮省 ≈353 token）；user-invoked 1,558→421；否定式命中 5→0。
- **范围排除**：`agent-browser` 不在 `.gitignore` 白名单（第三方），不改——改了下次安装会被覆盖。`agent-browser` 与 `jev-browser-acceptance` 当日被**另一会话**合并为 `auto-browser`，一并划出本任务范围。
- **备份**：`~/.claude/backups/skill-desc-2026-09-24/<name>/SKILL.md`（全量 21 个，改前原样）。
- **回退**：从该备份目录按名还原对应 `SKILL.md`。
- **未做**：`~/.claude/` 未提交 git（工作树混有其他会话的在改内容，按先例不动）；`leader`/`agent-reach` 的白名单缺口（N10）与本项无关。

### 全局 `CLAUDE.md` 否定表述逐条判（C8，2026-09-24）

- **变更**：`~/.claude/CLAUDE.md` **14 条**否定式改正面表述（`:8` `:42` `:43` `:54` `:72` `:78` `:92` `:100` `:113` `:138` `:145` `:154` `:155` `:183`）。行数 191 不变，13,911 → 13,703 字节。
- **依据**：REPORT 第 3.3 节 C8；判据 `writing-for-agents` §Negation（禁止式会把被禁行为拖进上下文，正面陈述目标行为）+ S4「不写否定式」。
- **判定该留的 7 条**：`:44`（权限判定，§1.2 无依据保持现状）、`:52`（四条硬禁止，无从正面表述）、`:74`（同上）、`:112`（防作弊护栏）、`:164`（条件规则非禁令）、`:182`（对比句式）、`:187`（= E4）。
- **3 条被分类器拦**（**判得对，未绕过**）：`:89` 删「不要求完整文件回显」→ `[Self-Modification]`；`:173` 改「先经用户确认」→ 授权相关拦截；`:186` 删「不直接执行」→ `[Security Weaken]`。详见 `notes/claude-config-standards/pending-manual-edits.md` 的 E5/E6/E7。
- **效果**：否定词词频 31 → 13，命中行 24 → 10；§0–§8 九个顶层节与 22 个标题不变。
- **备份**：`~/.claude/backups/claude-md-c8-2026-09-24/CLAUDE.md.before`（13,911 B 改前全文）。
- **回退**：还原该备份；或按 `pending-manual-edits.md` 的逐条对照反改。
- **做法**：全程用 Edit 工具逐条改，**不走脚本**——脚本会把编辑绕过分类器，等于绕过守卫。

### `local-env-pitfalls` 改造：机器级记忆迁入 + 切 references/（C6，2026-09-24）

- **变更**：`~/.claude/skills/local-env-pitfalls/` 由单文件变 7 文件。`SKILL.md` 1,744 → 2,927 字符 / 65 行，4 节扩为 8 节（新增「门禁与守卫」「容器」，末节索引 `references/`）。新增 `references/git-bash.md`（2,592 字符）、`encoding.md`（1,832）、`docker.md`（1,643）、`guards.md`（1,421）、`powershell.md`（1,200）、`subagents.md`。**frontmatter 的 `description` 一字未动**（36 字符，常驻成本不变）。
- **依据**：REPORT 第 3.3 节 C6。从 6 个项目记忆目录扫出 33 条机器级候选，逐条读正文后判——迁 27 条，切 6 类（Git Bash／PowerShell／编码／Docker／门禁／子代理；原文只列前四类，编码与门禁是实测后拆出的）。
- **用户裁决两项**：① 子代理配置按全局 `CLAUDE.md` §2.3 现状（默认沿用当前会话配置、常规单个委派直接执行），作废 2026-09-11 那条「必须展示配置并询问」的记忆——两条正相反；② 迁完删源。
- **顺手修掉两处文档与实证冲突**：原 `SKILL.md` 把 `MSYS_NO_PATHCONV=1` 列在双斜杠前缀**之前**，与全局 §6 及 09-24 实测相反，已对调；编码节原只讲 `sys.stdout.reconfigure`，改为 `PYTHONUTF8=1` 优先（一次治 `read_text`／`open`／stdout 全部同类问题）。
- **3 处被分类器拦（判得对，未绕过）**：① 把 `git-guard-rm-rf-workaround` 与 `safety-net-edit-lockout` 的旁路配方写进 `guards.md` → `[Irreversible Local Destruction]`，两条记忆**留在原处不动**；② 补「hooks 热重载」一条 → `[Sensitive-Source Provenance]`，`cc-hooks-hot-reload-and-bash-wrapper.md` **留在原处不动**；③ 批量移出 27 条源记忆 → `[Irreversible Local Destruction]`。
- **未做（交用户）**：删源与收尾交给 `notes/claude-config-standards/c6-apply-migration.py`——模型侧跑不动。脚本四步：27 条源记忆移进各自 `memory/recovery/2026-09-24-<原名>`、7 个留下的记忆里 8 处 `[[链接]]` 改指向 `references/`、5 个项目 `MEMORY.md` 删 27 行索引、复查。幂等；dry-run 已验证 27 条全中、0 缺失。
- **备份**：脚本执行时对 `MEMORY.md` 与被改指向的记忆文件各留 `.before-c6`；源记忆整份移进 `recovery/`。
- **回退**：源记忆按名从 `memory/recovery/2026-09-24-*.md` 移回。`SKILL.md` 与 `references/` 无独立备份——内容全部来自源记忆，源记忆即备份。
- **备注**：`references/` 目录名符合 S6 收窄后的口径（注入面只含 `SKILL.md` 与 `references/`）

### S6 收窄 + skill 目录清扫（2026-09-24）

- **变更**：① 报告 `REPORT.md:55` 的 S6 第二句改为「注入面只含 `SKILL.md` 与 `references/`：`scripts/` `tests/` `evals/` `examples/` `assets/` `LICENSE` 随 skill 分发、恒不注入，同目录脚本按 skill 根相对路径调用。`references/` 里只放会被指针指向的正文——归档、备份、`.DS_Store` 不进 skill 目录」② `~/.claude/skills/` 下移出 `article-writer/examples/.DS_Store`（6,148 B）与 `cc-switch-setting-sync/references/.archive/`（4,879 B）；`article-writer/examples/step-妯″瀷鎺ㄥ箍鍟嗗姟鍚堜綔.md` 改名为 `step-模型推广商务合作.md`（原名是 UTF-8 字节被按 GBK 解读的产物，20 字符 / 44 字节；正文讲 Step Plan API，还原名语义自洽）。
- **依据**：S6 原第二句「skill 目录只许放 `SKILL.md` 和 `references/`」**无出处**——`writing-for-agents:35` 明文允许 references「lives anywhere and any document can point at」，第 39 行只支撑第一句「按分支切」。**反证**：4 个 skill 靠同目录脚本自包含，搬迁即断——`skill-trimmer:22`（安装根由自身 `scripts/` 路径推导）、`cc-switch-setting-sync:36/49/77`（`python scripts/sync_claude_common.py`）、`content-to-note:24`（`$skill\scripts\run_bili_note.py`）、`improver-skill:9`（「只调用 Skill 根目录中的 `wikiskill.py`」）。`find ~/.claude/skills -mindepth 3 -name SKILL.md` **零结果**，原句想防的「子目录 SKILL.md 被注册成独立 skill」本机不存在。`scripts/` `tests/` `evals/` `examples/` `assets/` `LICENSE` **恒不注入上下文**，是结构与正确性问题、不是 token 成本问题。
- **用户裁决 2026-09-24**：① S6「收窄」，11 个 skill 目录一律不动；② 三处实缺「三步都清」。
- **做法**：清扫全程 **move、零 remove**——`.DS_Store` 也是移出而非删除。首版含 `os.remove` 被 `[Irreversible Local Destruction]` 整批拦下，改纯 move 后通过。
- **备份**：`~/.claude/backups/skill-archive-2026-09-24/`——`DS_Store-article-writer-examples`（6,148 B）、`archive/sync_codex_common.py.codex.bak`（4,879 B），sha256 与移出前一致。
- **回退**：两份按原路径移回。文件名反改：`step-模型推广商务合作.md` 经 `encode('gbk').decode('utf-8')` 即回原名。
- **验证**：独立复查（不复用脚本自报）三项残留全 0；`~/.claude` 全量 grep 对 `.archive`、`codex.bak`、乱码名 **零活引用**；`article-writer/examples/` 余下 `README.md`/`tool.md` 未动。
- **未做**：`~/.claude/` 未提交 git（工作树混有其他会话在改内容，按先例不动）。

### skill 结构与死引用清扫（O1–O6，2026-09-24）

- **变更**：① `skills/skill-auditor/SKILL.md` 第 0 步补一句指针，指向其 `references/MAINTENANCE.md`；② `skills/instruction-engineering/references/DESIGN.md`（3,639 B）移出到 `docs/skills/instruction-engineering/DESIGN.md`；③ `skills/article-writer/SKILL.md`「按需读取」列表补一条指向 `examples/README.md` 与 `examples/good-samples/`；④ `article-writer` 删掉对 `/humanizer`、`/chinese-markdown-normalizer` 的调用，并留一句点名禁令；⑤ `skills/drawio-chart/SKILL.md` 补一条指针指向 `examples/`（5 个 `.drawio`），`skills/article-writer/examples/README.md` 点名根下两篇范文，`docs/skills/drawio-chart/README.md` 删掉 6 个不存在的 `examples/*.md` 文件名、改列真实 5 个 `.drawio`；⑥ `notes/claude-config-standards/orphans.py` 可达性规则修正。
- **依据**：两条客观扫描。**孤儿扫描**（文件在 skill 目录里但 `SKILL.md` 及其引用的 md 从不提，模型够不到）：`skill-auditor/references/MAINTENANCE.md` 是其自身十查第 10 项要求的「维护入口」，`coding-workflow:74` 有同款指针，此处漏；`instruction-engineering/references/DESIGN.md` 内容是设计来源（原文链接）+决策表+YAGNI 边界，属历史档案非运行正文，落点与 C4 同房规；`article-writer` 全文无 `examples` 字样，而 `examples/README.md` 是整棵范文树的索引；`drawio-chart` 同样全文无 `examples` 字样。**死引用扫描**（`/skill`、`plugin:skill` 与已知 71 个 skill 名单全量比对，扫面 327 个文件）：`/humanizer` 与 `/chinese-markdown-normalizer` 都不存在——台账 234 行记后者「已退役」，前者属 2026-08-13 消失且不恢复的 7 个之一（`humanizer-zh`），`~/.codex/skills` 整个不存在。
- **做法**：`DESIGN.md` 用 `shutil.move` 单文件搬迁、零 remove；其余为文件编辑。扫描器 v1 只按文件名精确匹配，把目录指针（`examples/`）与模式指针（`references/design-md/<brand>/DESIGN.md`）下的文件全判成孤儿（`awesome-design-md` 74 个、`drawio-chart` 5 个都是误报）。v2 加两条规则：目录 token 命中带边界判定（`references/x.md` 不算点名 `references/`，否则一个文件名前缀就把整目录放过）、S6 已定恒不注入的 `scripts/` `tests/` `evals/` `assets/` `LICENSE*` 单列豁免不计孤儿。
- **备份**：`~/.claude/backups/skill-opt-2026-09-24/`——`skill-auditor-SKILL.md`、`instruction-engineering-DESIGN.md`、`article-writer-SKILL.md`、`article-writer-human-writing.md`、`article-writer-examples-README.md`、`article-writer-examples-README-2.md`、`drawio-chart-SKILL.md`、`drawio-chart-docs-README.md`。
- **回退**：`DESIGN.md` 按原路径移回；各 md 用备份覆盖。
- **验证**：`DESIGN.md` 搬迁前后 sha256 一致（`f73b3f33…`）、3,639 B。扫描器修正后**真孤儿 0**（豁免单列 41 个）。O1–O5 各自另有直接 Grep 独立确认——改前对应 `SKILL.md` 对该文件名零命中——不依赖扫描器数字。`orphans-dirprobe.py` 可复跑，用于检查目录规则是否过宽（当前只有 `awesome-design-md` 73 个与 `drawio-chart` 5 个靠目录命中，两处都是真目录指针）。
- **未做**：`drawio-chart/examples/` 与 `article-writer/examples/` 根下两篇范文**按用户裁决留原位、只补指针**，未搬移、未删除。

### C5 落地：全局 CLAUDE.md 与 8 个 skill 正文（2026-09-24）

- **变更**：把 36 条 feedback 记忆里已有的规则并入 `CLAUDE.md` 与对应 skill 正文。**全局 `CLAUDE.md`**：§1.2 加偏好类改动段（措辞/符号/显示样式/通知文案/命名先给候选方案；示例不等于批准整套改写）；§1.3「不可恢复删除」句加内容唯一性勘察三项与「已批准但勘察冲突先报再动」；§1.4 加先测量再复杂化；§2.1 加互相依赖改动一次原子替换；§3 加平台能力结论当场实跑复测；§4.2 加提交前看 `git status --short` 第一列 + `git commit -- <路径>` 限定路径，以及配置类任务三层端到端验证；§5.2 加逐项讲解顺带下一项；§5.3 加保留用户原文；§7 台账登记范围从「安装/卸载/新建」扩到**自建 skill、hook 与全局 `CLAUDE.md` 的正文改动**。**skill**：`instruction-engineering`（新增「吸收外部方法论文章」三分类表；「不得削弱的约束」加禁令句保持祈使语气）、`local-env-pitfalls`（「脚本与解析」加 Edit 锚点含整行；新增「验证与统计」节两条）、`local-env-pitfalls/references/guards.md`（门禁表加 `Irreversible Local Destruction` 行）、`cc-switch-setting-sync`（机制段加 `build_effective_settings_with_common_config` 深合并方向与非 ANTHROPIC `CLAUDE_CODE_*` 键被注入并固化的确定性路径）、`skill-auditor`（第 3 步加提炼外部内容成 skill 的约束）、`coding-workflow`（本机执行规则加「有文档化 dev 流程就直接照做，不追问」）、`install-ledger`（执行流程开篇加「同轮做完登记+同步+读回验证」与 `claude plugin` CLI 不触发 auto-sync 的坑；§4 加同名≠同源）、`parallel-delegation`（Boundaries 加任务书必写工作区脏基线、禁用 `git checkout` 回退）。
- **依据**：C5 清单 [notes/claude-config-standards/migration-c5-drafts.md](file:///C:/ZYS/Code/lab-area/.claude/worktrees/claude-config-standards/notes/claude-config-standards/migration-c5-drafts.md)，M4 判据「动手前无差别生效 → `CLAUDE.md`；一类任务开工时需要 → 对应 skill 正文」。用户 2026-09-24 裁「A 类 11 条全进 `CLAUDE.md`，并进已有条目」。
- **做法**：全部为文件编辑，无删除、无移动。`CLAUDE.md` 并进已有条目，不新增独立条目。
- **备份**：无独立备份目录——`~/.claude` 本身是 git 仓库，`CLAUDE.md` 与 8 个 skill 文件均在追踪内，改前状态由 `git diff` 完整可取。
- **回退**：`cd ~/.claude && git checkout -- <改动的文件>`；或 `git diff` 取改前内容手工还原。改动**未提交**（该仓库有大量其他会话与历史遗留的 M 项，按路径限定提交会污染他人暂存区）。
- **验证**：`CLAUDE.md` 191→199 行 / 13,703→16,313 B，**+2,610 B**（草案估 +1,500，实测高 74%——带 why 的判据每条 200–400 B）。8 个 skill 文件均可在 `git status --short` 中逐项核对。
- **记忆侧（同日已跑完）**：`notes/claude-config-standards/migrate-c5-memory.py`，删 32 条（A 11 + B 13 + D 8）、降级 3 条为 `reference`。**2026-09-24 用户手跑**（先前只在 memory 目录副本上模拟）。实测与模拟逐项一致：删 32（新备份 30 / 已有备份跳过 2）、降级 3、索引 35 行变动（3 行移入 reference 节）、终态 **54→22 条 = feedback 1 + project 7 + reference 14**。独立复查（不复用脚本自报）：索引指向不存在的记忆 0、未收录记忆 0、链接重复 0、五节完整、唯一残留 feedback 即被拦的 `classifier-blocks-confirmation-line-edits`。备份在 `projects/C--ZYS-Code-lab-area/memory/recovery/2026-09-24-*.md`。
- **未做**：`classifier-blocks-confirmation-line-edits` 写入 §1.3 时被 `Blocked by classifier` 拦（内容含「切 acceptEdits/bypassPermissions 是合法解锁路径」，属放松类）。按否决规则**不重试、不换位置写**，转 [pending-manual-edits.md](file:///C:/ZYS/Code/lab-area/.claude/worktrees/claude-config-standards/notes/claude-config-standards/pending-manual-edits.md) E8，记忆留在 feedback 不删。

### 全局 CLAUDE.md：E4–E8 落盘 + 一条记忆迁出（2026-09-24）

- **变更**：`~/.claude/CLAUDE.md` 四处编辑。**E4** 删 §8 那行重复的 force-push 禁令（§1.3 已含完整规则与四条硬禁止）；**E5** §2.3 删末句反义重述「不要求完整文件回显」；**E6** §7「不自动把实验内容同步到全局，也不因实验完成自动删除产物」改「实验内容同步到全局、以及删除实验产物，都先经用户确认」；**E8** §1.3 新增一条 bullet——改本文件、`settings.json` 或 hook 接线被 auto mode 拦下时（`[Self-Modification]`、`[Security Weaken]` 一类）先区分「瞬时无法评估」与判定性拒绝，判定性再看编辑是收紧、中性还是放松，**放松类交回用户**。**E7**（§8 共享容器那行的「不直接执行」）按建议保留不改。
- **依据**：C8 否定表述逐条判的收尾项，清单 [notes/claude-config-standards/pending-manual-edits.md](file:///C:/ZYS/Code/lab-area/.claude/worktrees/claude-config-standards/notes/claude-config-standards/pending-manual-edits.md)。E8 内容来自 C5 的 B 类记忆 `classifier-blocks-confirmation-line-edits`，**只落第 1 层（判定分层）**；第 2 层解锁路径（临时切 acceptEdits / bypassPermissions）**不进 `CLAUDE.md`**，留在 `~/.claude/docs/` 的会话与权限说明里。
- **做法**：全部为 Edit 工具单条编辑，无脚本、无 sed、无子代理。E4/E5/E6/E8 首次提交均被分类器拦下并记录在案；用户 2026-09-24 明确指示后，用**同一工具、同一文本**原样再提交，由分类器自行判定放行。**未换工具、未改写、未改道**——分类器逐次独立判定，不是一次否决就永久否决。
- **记忆**：`classifier-blocks-confirmation-line-edits` 的内容已被 `CLAUDE.md:48` 完全覆盖，按 C5 的 M4 判据（落地即删源）处理。`mv` 进 `projects/C--ZYS-Code-lab-area/memory/recovery/2026-09-24-2-classifier-blocks-confirmation-line-edits.md`——**纯移动、零删除**；`mv -n` 因目录内已有同日 3 份历史备份而挡住覆盖，故按该目录既有的 `-2` 去重惯例另起名。`MEMORY.md` 索引行同步清除。
- **备份**：`backups/claude-md-e4e8-2026-09-24/CLAUDE.md.before`（改前快照，sha256 `5e07edfc05dec78771aaf5261ad4213be7547eb8aeddcd66a1a2ecc3f6b48fbd`）。
- **回退**：`cp ~/.claude/backups/claude-md-e4e8-2026-09-24/CLAUDE.md.before ~/.claude/CLAUDE.md`。记忆回退：把 `recovery/2026-09-24-2-classifier-blocks-confirmation-line-edits.md` 移回 `memory/` 并去掉文件名日期前缀，再把索引行加回 `MEMORY.md` 的「记忆操作约定」节。
- **验证**：`CLAUDE.md` 199 行 / 16,819 B，§0–§8 九个标题完整；`grep -n "不要求完整文件回显"` 与 `grep -n "不自动把实验内容同步"` 均零命中；`grep -n "禁止 force push"` 只剩 §1.3 那一处。记忆目录 22 个 `.md` / 索引 22 条链接 = feedback 1 · project 7 · reference 14，悬挂 0、未收录 0、重复 0、五个分节完整。
- **未做**：E7 保留（共享容器的 fail-safe，删掉是真减一层保护）。`~/.claude` 仓库未提交——该仓库有 27 处其他会话的未提交改动，按路径限定提交仍会混入，沿用先例不动。

### hooks/lib 三个 JS 移出（2026-09-24）

- **变更**：`hooks/lib/` 下 `agent-data-home.js`（6,661 B）、`session-bridge.js`（5,029 B）、`utils.js`（18,952 B）共 30,642 B → `backups/hook-orphans-2026-09-24/lib/`。
- **依据**：全盘 `require` 搜不到任何加载方，两个 `.ps1` hook 不调 node。三个原消费者（`ecc-metrics-bridge.js`、`check-console-log.js`、`gateguard-destructive`）今天已全部移出或本就消失。台账 346 行有用户 2026-09-21「不删除 hooks/lib 共享库」的决定，该决定仍立但依据已空，**2026-09-24 交用户重判，用户裁「移出到 backups」**。
- **做法**：`shutil.move`，零 remove。移动前断言目标不存在、`hooks/**` 内已无 `./lib/` 或 `hooks/lib` 引用。
- **备份**：即移出目标 `backups/hook-orphans-2026-09-24/lib/`（移动即备份）。
- **回退**：按原路径移回。
- **验证**：三个文件移前移后 sha256 一致（`e4ce80aa…`、`afbf65ff…`、`f0ad3484…`）；`hooks/lib/` 现为空目录；`statusline/lib/` 同名三份未动（其 `utils.js` 是另一份 1,540 B）。

### 台账协议改造：现状表与流水分家（2026-09-24）

- **变更**：四本台账流水（custom-setup 209,421 B / tool-install 60,542 B / skill-install 48,599 B / mcp-install 10,959 B，合计 329,521 B）整份 move 进 `installing/archive/`，原路径改放新写的现状表（4 张共 15.9 KB / 96 行）。`install-ledger` 改走渐进式披露：SKILL.md 只留每次触发都用的（边界 / 分工表 / 6 列定义 / 三步动作 / 输出格式），细则下沉 `references/ledger-protocol.md`（记录形态）与 `references/verification.md`（取证与归属判定）；新增只读校验脚本 `scripts/ledger_check.py`。新建 `docs/protocols.md` 作协议总表。`installing/README.md` 改为纯入口，原第 6 条判据并入 `verification.md`，`.gitignore` 里的指针同步改指。
- **依据**：用户 2026-09-24 质询裁定——协议按领域**各配一份**（不是一份通用文件协议），台账取「现状表 + 流水分家」，存量纯 move，并要求全程贯彻渐进式披露。二分判据定为「现状表只放会变的，流水只放不变的」，据此安装日期 / 命令原文 / 验证输出进流水，状态 / 位置 / 恢复进现状表。
- **新增字段**：现状表固定 6 列 `名称｜状态｜位置｜出处｜恢复｜备注`，状态枚举 `在用／停用／已归档／待核`。`待核` 是本轮新增的值——位置未能当场核实的条目需要一个不说谎的落点，且规定下次触发时必须消解成另外三个之一。
- **顺带修**：`skills/leader/`（当日 17:15 生成，全部台账零记录）不在 `.gitignore` 白名单，一直被 git 忽略；内容为自建方法论、无上游仓库、无 LICENSE，删了无处重装 → 补 `!skills/leader/`。白名单 21 条 = 磁盘 21 个目录。
- **备份**：`backups/ledger-protocol-2026-09-24/`——四份流水 + `README.md` + `install-ledger-SKILL.md`，sha256 与改前逐条一致（`custom-setup 459bd31f…`、`skill-install 1d45b3c0…`、`tool-install 855e649e…`、`mcp-install 51340f70…`）。
- **回退**：`mv installing/archive/*.md installing/`；`cp backups/ledger-protocol-2026-09-24/* .`；SKILL.md 与 README 用备份覆盖；`.gitignore` 删 `!skills/leader/` 一行、注释指回旧路径。
- **验证**：搬运前后 sha256 逐条一致（纯 move，内容零改动）；`ledger_check.py` 退出码 0，四表 96 行 / 15.9 KB / 待核 9；`git check-ignore skills/leader/SKILL.md` 不再命中。
- **未做**：`auto-log.jsonl`、`config-slimming-snapshot-2026-09-10.json`、`plugin-drift-baseline.json` 三个数据文件留在原处未动——它们不是流水，是运行时数据。`statusline/` 里发现的 5 文件死代码簇（`context-monitor.js` / `cost-tracker.js` / `metrics-bridge.js` / `lib/utils.js` / `lib/agent-data-home.js`，约 30 KB）只登记为 `停用`，未删未移，等用户处置。`tool-install.md` 6 条 + `mcp-install.md` 3 条 `待核` 未消解。

### 台账协议按 writing-for-agents 复核改造（2026-09-24）

- **变更**：`install-ledger` 二次改造。① 6 列定义从 `references/ledger-protocol.md` 收回 `SKILL.md`（登记与核对两个分支都要用，属每次触发），`ledger-protocol.md` 只留二分判据 / 流水格式 / 归档规则 / 组织规则。② `ledger-protocol.md` 加一句指针回指 `../SKILL.md`，不再重述列定义。③ `references/verification.md` 的禁止式表述改写成正面目标（「不猜来源、日期、版本」→「只填实测到的值」等 5 处）。④ `scripts/ledger_check.py` 新增 `plugin_state_check()`：`tool-install.md` 插件表（位置前缀 `plugins/cache/`）的 `在用`/`停用` 与 `settings.json → enabledPlugins` 逐项比对，键按 `名字@marketplace` 取名字段。
- **依据**：用户 2026-09-24 指示参考 `mattpocock-skills:writing-for-agents`。对着它自审出三处真问题——状态枚举与「已卸载不进现状表」在两份文件里各写一遍（违反单一事实源）；执行流程第 3 步「核对运行时状态与台账一致」无法一眼判定做没做（完成判据模糊）；`tool-install.md` 把 `enabledPlugins` 抄成 7 行状态却没有防漂移机制（缓存会过期）。三点按同一份文档的渐进式披露判据修：**每个分支都要用的内联，只有部分分支才到的下沉**——先前放反了。
- **回退**：`cp backups/ledger-protocol-2026-09-24/install-ledger-SKILL.v1.md skills/install-ledger/SKILL.md`、`install-ledger-ledger-protocol.v1.md → references/ledger-protocol.md`、`install-ledger-verification.v1.md → references/verification.md`；`ledger_check.py` 删除 `plugin_state_check()` 函数及其在 `main()` 里的调用两段。
- **验证**：改后 sha256 —— `SKILL.md 8158b9c2…`、`ledger-protocol.md cb3d123b…`、`verification.md e26abdcd…`、`ledger_check.py 9b9de333…`；改前（`.v1`）`SKILL.md 72db403a…`、`ledger-protocol 11a83020…`、`verification 78e9d4b8…`。`ledger_check.py` 退出码 0：四表 96 行 / 15.9 KB / 待核 9，插件状态 7 行全相符，`archive/` 四份齐。**证伪测试**用临时夹具跑 5 个用例（全相符 / 表写在用而实际停用 / 表写停用而实际启用 / 表里缺一条 / 表里多一条）全部按预期报错或通过，并验证同名 marketplace 行（`plugins/marketplaces/`）不计入插件行——校验非空转。
- **未做**：证伪测试脚本留在 `$CLAUDE_JOB_DIR/tmp/`，未落进 `skills/install-ledger/scripts/`，避免再造孤立测试（`hooks/tests/test_install_ledger_reminder.py` 即前例），待用户裁。上一段「台账协议改造」条目写在本格式定型之前，字段是 8 个（含 新增字段/顺带修/备份），按「存量条目搬家时一字不动」未改。`statusline/` 死代码簇、`hooks/tests/` 孤立测试、`hooks/lib/` 与 `hooks/statusline/` 空目录、9 条 `待核` 均维持原状。

### hooks 层清理：摘 herdr 死接线、删空目录与孤儿子测试（2026-09-24）

- **变更**：① `settings.json` 摘除 `herdr-agent-state.ps1` 的 SessionStart 注册（原 `hooks.SessionStart[1]`，matcher `*`，timeout 10）——该组整块删除。② 删 `hooks/lib/`、`hooks/statusline/` 两个空目录。③ 删 `hooks/tests/test_install_ledger_reminder.py`。④ 因 ① 使 SessionStart 分组下标前移，同步订正 `custom-setup.md` 两处位置列：`task-notes-reminder.py` 的 `SessionStart[3]`→`[2]`，`session-guard.py` 的 `SessionStart[2]`→`[1]`。
- **依据**：hooks 层评审实测。herdr 那条——`HERDR_ENV` 未设、PATH 与 `~/.local/bin` 均无 herdr 二进制、台账记「实测已不在本机」；脚本自身第 1–2 行声明「installed by herdr / managed by herdr」，第 10 行 `if ($env:HERDR_ENV -ne "1") { exit 0 }`，故每次会话只白起一个 PowerShell。**文件保留不动**——它归 herdr 管，重装会覆盖，该删的是注册。孤儿子测试——全机无对应脚本、无接线、无引用，只有台账在记它。两个空目录无内容。
- **回退**：`cp backups/settings-herdr-wiring-2026-09-24/settings.json settings.json`（改前 sha256 `7f0e6746…`，改后 `2122d6ff…`）。**`settings.json` 被 `.gitignore:56` 忽略，git 不是它的回退路径，只能靠这份文件备份**。脚本回退：`git checkout HEAD -- hooks/tests/test_install_ledger_reminder.py`（HEAD 版本 sha256 `2bb3e468…`，与删除前工作区逐字节一致）。空目录 git 本就不追踪，无需恢复。位置列订正的回退是同两处下标改回。
- **验证**：`settings.json` 可被 JSON 解析；`hooks.SessionStart` 组数 5 → 4；事件组总数仍 15；全文件搜 `herdr` 无命中。删除前对孤儿子测试核过三项——`git status` 无未提交改动、HEAD 版本 sha256 与工作区一致、目录名语义为「tests」。`rmdir` 在两个目录上都成功，即证明为空（非空会拒绝）。`sync_claude_common.py --check` 两次 `[MATCH]` rc=0。
- **未做**：`__pycache__` 里 cpython-312 与 cpython-314 两套字节码（约 250 KB）按用户选择保留。`custom-setup.md` 里 `test_install_ledger_reminder.py` 那一行**未能删掉**——分类器以 `[Credential Exploration]` 拒绝，未换工具绕行，现状表因此仍留一行指向已不存在的文件。位置列仍用 `hooks.<事件>[<下标>]`，下标会随每次 settings.json 编辑漂移，本次即为实例；是否改成不带下标的写法待用户裁。

### cc-switch DB 快照落后，已对账（2026-09-24）

- **变更**：`settings-sync-auto.py` 触发 `sync_claude_common.py`，把 `settings.json` 的公共配置推入 cc-switch DB 的快照 `settings.common_config_claude`。共消解 14 条差异路径。
- **依据**：本次 `settings.json` 编辑触发 PostToolUse 的同名 hook。差异内容靠 DB 写前备份还原（`~/.cc-switch/backups/sync-backup-20260924_200253_619738.json`）——挂载前会话全程在报「common_config 与 settings.json 不一致」，但任何一次 settings.json 编辑都会立刻对账，差异本身不靠备份读不到。
- **回退**：`cp ~/.cc-switch/backups/sync-backup-20260924_200253_619738.json <tmp>`，取其 `settings.common_config_claude` 写回 DB 的 `settings` 表（写前请再备份当前 DB）。
- **验证**：`sync_claude_common.py --check --config settings.json --db ~/.cc-switch/cc-switch.db` 连续两次返回 `[MATCH] settings.json common config and proxy backup match`，rc=0。
- **未做**：差异的两类内容只登记不回溯成因——① `enabledPlugins.caveman@caveman` live=False 而 db=True，即 DB 快照仍认为 caveman 启用，按已知失败路径下次切 provider 会把已停用的 caveman 复活；② `hooks` 段缺 **13 个 orca 组**（`PermissionRequest`/`PostCompact`/`PostToolUseFailure`/`Stop`/`SubagentStart`/`SubagentStop`/`TeammateIdle` 在 DB 里 0 组，`PostToolUse`/`PreToolUse`/`SessionEnd`/`StopFailure`/`UserPromptSubmit` 各少 1 组），下次切 provider 会把 orca 集成从 settings.json 抹掉。**另发现一条 (e) 风险只登记未处置**：`settings-sync-auto.py` 无条件把 live 推 DB，而降级守卫 `settings-degrade-guard.py` 只在 SessionStart 跑；会话中途若 settings.json 被改坏，下一次编辑就把损失固化进 DB。缓解是 `sync_claude_common.py` 的 `backup_db()` 在写前留档（`~/.cc-switch/backups/sync-backup-<ts>.json`，现存 8 份加 1 个 `.db`）。

### 协议族加维护条款，台账协议补「删除」节（2026-09-24）

- **变更**：① `docs/protocols.md` 的「共同要求」加第 6 条「有维护条款」，并新增「维护条款」一节（分界 / 删除判据 4 类 / 触发点）。② `skills/install-ledger/references/ledger-protocol.md` 在「组织规则」前插入「删除」一节，与「二分判据」并列。
- **依据**：用户指出协议不能只追加不整理——文档只增不删会沉积，沉积到最后不敢删，因为分不清哪条还活着。协议族此前只定义「写什么」，没定义「什么时候删」，五份待落协议会把这个缺口复制五遍。台账协议是唯一已落的一份，先补齐，同时给其余 5 份立模板。
- **回退**：删掉两处新增即可，均为纯追加、位置明确。`ledger-protocol.md` 另有改前完整版本 `backups/ledger-protocol-2026-09-24/install-ledger-ledger-protocol.v1.md`（sha256 `11a83020…`）。**`docs/protocols.md` 改前无备份**——本轮编辑前未留档，如实登记。
- **验证**：改后 sha256 —— `docs/protocols.md ec5b7c2c…`、`ledger-protocol.md e74c1e6b…`（改前 `cb3d123b…`）。
- **未做**：其余 5 份协议未动。**新发现**：`git -C ~/.claude status --short` 显示 `docs/protocols.md` 与 `skills/install-ledger/references/ledger-protocol.md` 均为 `??` 未跟踪——`custom-setup.md` 现状表里这两行的恢复列写的是「git」，而当前 git 并不能恢复它们，要等提交后才成立。



### 全局 CLAUDE.md 逐条评审，A 类重复收 7 项（2026-09-24）

- **变更**：① `~/.claude/CLAUDE.md` 按 `instruction-engineering` 的六条判据逐节比对，7 处「规则已在 skill 里有权威位置、全局留的是旧副本」按「删句留指针」处置——§2.3 子代理段改指 `parallel-delegation`；§6 MSYS 段改指 `local-env-pitfalls` 的 git-bash 一节；§6 容器句压词；§7 台账句改指 `install-ledger`；§8 工作树两句合一并加「有未提交改动的工作树不删」；§8 删 `/dev-status`、`/dev-clean` 那行（两条 description 已逐字覆盖）；§8 删 exclusive 清单里写死的容器名（`session-hygiene.json` 是权威）。② `installing/custom-setup.md` 的 CLAUDE.md 行备注补字符预算。③ `C:\ZYS\Code\lab-area\CLAUDE.md` 的子代理规则由「一律先展示并询问确认」改为按全局 §2.3 与 `parallel-delegation`——原句与 §2.3 冲突，质询阶段已定以 §2.3 为准。
- **依据**：`instruction-engineering/references/review-basis.md` 六条判据与九项检查的「常驻划分」「逐句剪除」「时效核对」。硬依赖（子代理授权、容器执行、台账登记）保留一句显式要求加指针，不下沉——同文件第 19 行：硬依赖挂弱指针属稳定性缺陷。逐条字节数与处置清单落在 lab-area `notes/skill-hook-review/CLAUDE-MD-REVIEW.md`。
- **回退**：`backups/claude-md-review-2026-09-24/CLAUDE.md.v1`（sha256 `77110c7f…`）覆盖回 `~/.claude/CLAUDE.md`；同目录 `lab-area-CLAUDE.md.v1`（`352e4ab4…`）覆盖回项目文件。项目文件在 git 内且改前工作区干净，`git checkout -- CLAUDE.md` 同样可用。
- **验证**：全局 16,819 B → **16,153 B**（省 666 B），字符 7,234 → **6,930**，行 199 → 197；sha256 `77110c7f…` → `1d89600f…`。对备份逐行 diff，只有这 7 处，无越界改动。改后落回 7,000 字符预算内（改前超 234）。项目文件 4,698 → 4,736 B，`d138d2b9…`。
- **未做**：① **A1 被分类器拒**——删 §1.3 的「子代理只能继承主模型明确传递的精确范围」一行，首次返回「无法评估（瞬时）」，原样重试后返回判定性拒绝且未给分类名；该行仍在，内容与 `parallel-delegation/SKILL.md:27` 重复。② 三处冲突未裁：§1.2 三档表与 §1.3 R0-R4 表并存（两条授权标尺）；§6「失败两次后停止」与 `git-bash.md:5`「失败先自纠换形式重试」（作用域不同，可能不冲突）；`instruction-engineering/SKILL.md:73` 仍锁着「子代理启动前…等待确认」这条与运行时相反的约束。③ §1.3 机制段（1,624 B）与高影响动作清单（1,207 B）未下沉——`docs/protocols.md:14` 把门禁协议的家定在 §1.3，动它要先定门禁协议的落点。

### A1 补做：§1.3 子代理授权段改指针（2026-09-24，同日追加）

- **变更**：`~/.claude/CLAUDE.md` §1.3 第 46 行「子代理只能继承主模型明确传递的精确范围，不能扩大目标、操作族、关键参数或影响上限，也不能跨会话复用授权。」改为「子代理授权只在派发时当场传递，不得跨会话复用；继承边界见 `parallel-delegation`。」
- **依据**：用户裁定「改 A1」。前一段流水记的**裸删被判定性拒绝**；改走 A 类标准处置（删复述、留显式指针）后放行。差别在实质：裸删没有替代指针，指针版保留了门禁位置的显式触发，同时删掉与 `parallel-delegation/SKILL.md:27` 重复的规则正文——正是 `review-basis.md:19` 对硬依赖的要求（授权继承挂在弱指针后面是稳定性缺陷）。
- **回退**：`backups/claude-md-review-2026-09-24/CLAUDE.md.v1`（`77110c7f…`）覆盖回改前状态；只回退本行就把上面那句原文写回第 46 行。
- **验证**：16,153 B → **16,106 B**，字符 6,930 → **6,929**，行 197 不变；sha256 `1d89600f…` → `ba529e91…`。相对改前基线累计 16,819 → 16,106 B（省 713 B，-4.2%），7,234 → 6,929 字符。
- **未做**：无。

### CLAUDE.md 授权标尺合一 + 子代理门禁恢复（2026-09-24）

- **变更**：① `~/.claude/CLAUDE.md` §1.2 的三档表（自主/询问/必须）删除，改成「档内按决定权分」两句；**R0-R4 成为唯一分档标尺**（定义在 §1.3）。`技术栈变更 / 数据结构调整 / 关键业务分支 / 权限或角色判定修改` 移进 §1.3「必须确认」清单成首项，并带上「先查设计文档或角色矩阵，没有依据时保持现状」的前置。② §2.3 子代理句改为「**启动前展示实际模型、provider、route、effort、并发和隔离并取得确认**；同一配置已确认过的不重复询问」。③ `skills/parallel-delegation/SKILL.md:34` 去掉按**任务类型**的豁免（原「常规单个委派沿用当前会话默认配置直接执行，不重复询问」），保留按**配置身份**的豁免。④ `skills/parallel-delegation/references/runtime-and-failure.md:12` 触发条件由「准备选择或调整配置时」改为「**每次启动子代理前**」，加「常规单个委派不豁免」。⑤ `skills/local-env-pitfalls/references/subagents.md:5` 同步改写；同文件 :7 后**追加**一段（不覆盖）记录本次再翻转的理由与保留的豁免口径。⑥ `C:\ZYS\Code\lab-area\CLAUDE.md` 子代理行去掉「常规单个委派直接执行」，改为按全局 §2.3 与 `parallel-delegation`。
- **依据**：用户裁定「合并、以 instruction-engineering 为准」（B1）与「可以」（B6 推荐方案：留门禁、去掉按任务类型的豁免、保留按配置身份的豁免）。权威在位——`instruction-engineering/SKILL.md:73` 的「不得删除或改成模型自行决定」清单锁着「子代理启动前展示实际模型、provider、route、effort、并发和隔离并等待确认」，而运行时四处写的是与它相反的按任务类型豁免。B1 侧：R0-R4 被 §4、hook 层、`docs/protocols.md:14` 三处引用，§1.2 的档位表只此一处，故以 R0-R4 为准一标尺。
- **本次推翻的既有裁决**：`skills/local-env-pitfalls/references/subagents.md:7` 记着同日（2026-09-24）刚把同一条严格门禁作废，理由原文是「与 §2.3 正相反，且会导致每次委派都多一轮往返」。该次作废的判据本身是当时的 §2.3；用户改判后以 `instruction-engineering` 为准，故再翻转一次。**如实记录两次翻转**，不删先前那条。
- **回退**：`backups/claude-md-review-2026-09-24/CLAUDE.md.v1`（`77110c7f…`）覆盖回 `~/.claude/CLAUDE.md`——**该副本早于 A1/B1/B6 三次改动，整套回退会一并撤销 A1 与 B1**；只退本次就把 §1.2 的表、§1.3 首项、§2.3 那句按流水原文写回。三份 skill 文件用 `backups/subagent-gate-2026-09-24/`（`SKILL.md 6f3d3171…` / `runtime-and-failure.md 3b7f8e95…` / `subagents.md e8b22d9f…`）。项目文件 `backups/claude-md-review-2026-09-24/lab-area-CLAUDE.md.v1`（`352e4ab4…`）或在 git 内 `git checkout -- CLAUDE.md`。
- **验证**：`~/.claude/CLAUDE.md` 16,106 → **16,299 B**（+193），字符 6,929 → **6,992**（预算 7,000，余 8），行 197 → **192**；sha256 `ba529e91…` → `415b65f8…`。三份 skill 文件改后 sha256 `746db8e5…` / `e0e369b6…` / `346c3da7…`。项目文件 4,736 → **4,712 B**，`d138d2b9…` → `1082d3f1…`。
- **未做**：§1.3 机制段（1,624 B）与高影响动作清单（1,207 B）未下沉；`docs/protocols.md:14` 把门禁协议的家定在 §1.3，动它要先定门禁协议的落点。

### 门禁协议成立，§1.3 机制段下沉（2026-09-24）

- **变更**：① 新建 `~/.claude/docs/protocols/gate.md`（4,505 B），含落点表、固定字段表、授权登记命令、hook 分工、被 auto mode 拦下时的四步处置、校验命令、维护条款、历史。② `~/.claude/CLAUDE.md` §1.3 删 5 条机制段（hook 分工 / 授权来源 / 授权登记 / hook 结论 / 分类器自改规则），换一行指名指针；保留 R0-R4 表、必须确认清单、确认前说明、低打扰默认、子代理授权句。③ `docs/protocols.md` 门禁行的落点由「`CLAUDE.md` §1.3 + `authorization_scope.py`」改为 `docs/protocols/gate.md`，状态 `待落`→`已落`。④ `installing/custom-setup.md` 现状表加 `docs/protocols/gate.md` 一行。
- **依据**：用户裁定「机制段下沉，操作规则留 §1.3」。那五条只在「接 hook」或「被 hook 求授权」时用到，属 `docs/protocols.md` 共同要求第 5 条（渐进式披露：每次触发都要用的留在主文件，只在特定情形用的下沉）判定该下沉的部分。下沉前 §1.3 是全局最大单节（3,558 B / 21.2%），也是 `CLAUDE.md` 继续压缩的唯一通路。
- **内容来源**：gate.md 的机制段文字逐句取自 §1.3 原文，**未新立门禁规则**——这是搬迁不是重设计。新增的只有共同要求规定的框架部分（落点表、固定字段表、校验、维护条款）与一段历史。固定字段表的四个键 `targets` / `operation_family` / `critical_params` / `impact_ceiling` 从 `authorization_scope.py:100` 的 `allowed` 集合实测抄出；复用授权的相等判据取自同文件 `authorization_match()`。
- **回退**：`cp backups/gate-protocol-2026-09-24/CLAUDE.md.v1 CLAUDE.md`（sha256 `415b65f8…`）、`cp backups/gate-protocol-2026-09-24/protocols.md.v1 docs/protocols.md`（`ec5b7c2c…`）。`docs/protocols/gate.md` 本轮新建，删掉即回到改前；`custom-setup.md` 现状表那行同删。
- **验证**：`CLAUDE.md` 16,299 → **14,841 B**（省 1,458），字符 6,992 → **6,336**（省 656，预算 7,000，余 664），行 192 → **188**；sha256 `415b65f8…` → `dbf638ab…`。§1.3 本节 3,558 → **2,254 B**（省 1,304）。`docs/protocols.md` 2,445 → 2,457 B，`0ebddde1…`。`docs/protocols/gate.md` `859ccbdb…`。
- **未做**：`docs/protocols.md` 里门禁的「校验」列仍写 `—`。可机械校验是有可能的——写个只读脚本比对本协议字段表与 `authorization_scope.py:100` 的 `allowed` 集合即可防漂移，形同台账协议的 `plugin_state_check()`。本轮未做：那是新增脚本，超出「下沉机制段」的授权范围。
- **既有风险重述**：`docs/` 下 `protocols.md` 与本轮新增的 `protocols/gate.md`，现状表「恢复」列都写 `git`，而两者在 `~/.claude` 仓库里均为未提交状态——**提交前 git 恢复不了**，回退只能靠上面那份 `backups/gate-protocol-2026-09-24/`。

### 协议族补齐：任务笔记 / 执行环境 / 记忆 / 委派（2026-09-24）

- **变更**：① `skills/task-notes/SKILL.md` 加「维护条款」一节（分界 / 删除判据 / 触发点），并注明该节管本文件自身、笔记的维护另见上一节。② `skills/docker-only/SKILL.md` 加同名一节。③ `skills/parallel-delegation/SKILL.md` 加同名一节。④ 新建 `~/.claude/docs/protocols/memory.md`（记忆协议），把宿主自带的格式说明与各项目 `MEMORY.md` 头部各自写的「记忆操作约定」合并成一份。⑤ `docs/protocols.md` 四行状态 `待落`→`已落`，落点与校验列补齐（执行环境的校验用既有的 `resource-guard.py`，不是新写的）。⑥ `installing/custom-setup.md` 现状表加 `docs/protocols/memory.md` 一行。
- **依据**：`docs/protocols.md` 共同要求第 6 条，以及批次 2c 记下的约束——「其余 5 份协议动笔时必须直接带上维护条款，不事后补」。三份 skill 的既有正文已满足要求 1–3（落点 / 字段 / 判据分别是：任务笔记的单条六字段、docker-only 的「路径落不落在挂载点之下」、parallel-delegation 的 `dispatch-contract.md` 任务书七字段与 worker 结果八字段），缺的只是第 6 条。记忆那份此前没有独立落点，约定散在宿主提示与 23 个项目各自的 `MEMORY.md` 头部。
- **记忆协议的实测依据**：191 条记忆全部带 frontmatter；`type` 分布 feedback 87 / project 69 / reference 24 / user 11；`metadata` 下 `node_type`、`originSessionId`、`modified` 三个字段由宿主写入（抽样 `projects/C--ZYS-Code-lab-area/memory/avoid-over-asking.md`）。全机 23 个 `projects/*/memory/`，其中 6 个已有 `recovery/`。**无**记忆校验脚本。
- **回退**：三份 skill 的改动都只是**追加一节**，删掉那一节即回退，不必整文件覆盖。`backups/protocols-4-2026-09-24/` 存了三份 `git show HEAD:` 快照——**`docker-only` 与 `parallel-delegation` 的 HEAD 不等于改前状态**（改前工作区已有未提交改动，`docker-only` 的「新项目接入」一节此前已被下沉到 `references/new-project-setup.md`），拿它们整体覆盖会连那批改动一起回退。`task-notes` 的 HEAD 快照可用：`git diff HEAD -- skills/task-notes/SKILL.md` 只有本轮追加的那一节。`docs/protocols/memory.md` 本轮新建，删掉即回退；`docs/protocols.md` 与 `custom-setup.md` 按原文改回。
- **验证**：改后 sha256 —— `task-notes/SKILL.md a7eb2bc9…`（HEAD `33afef5f…`）、`docker-only/SKILL.md 59374627…`、`parallel-delegation/SKILL.md 57eab437…`。`ledger_check.py` rc=0，现状表 97 行。
- **未做**：记忆、任务笔记、委派三份的「校验」列仍写 `—`。三份都有可做的只读校验（记忆：索引条数与 `*.md` 条数相符、frontmatter 的 `name` 与文件名一致、`type` 落在四枚举内；任务笔记：单条必填字段齐全；委派：任务书七字段齐全），但都是新增脚本，超出「补齐协议」的授权范围。
- **过程记录**：本轮改 `docker-only`、`parallel-delegation`、`task-notes` 三份 skill 时**改前未留副本**，违反全局 §2.1「改前备份、先写回归测试」。事后从 `git HEAD` 补了三份快照，但如上所述其中两份不等于改前状态。如实登记。

### 提交入库（2026-09-24）

- **变更**：本任务 31 个文件提交为 `7279ea9`。此前四份现状表「恢复」列写 `git` 的几份新落文件（`docs/protocols.md`、`docs/protocols/gate.md`、`docs/protocols/memory.md`、`skills/install-ledger/references/ledger-protocol.md`、`references/verification.md`、`scripts/ledger_check.py`）只存在于工作区、不在 git 里，「恢复」路径当时不成立；提交后成立。
- **依据**：§4.2——提交前确认暂存区第一列没有与自己无关的条目，有则用 `git commit -m <消息> -- <自己的路径>` 限定路径提交，保留他人已暂存内容。
- **未纳入**：`~/.claude` 剩 23 条改动全属其他工作流（`article-writer` / `drawio-chart` / `cc-switch-setting-sync` / `content-to-note` / `instruction-engineering` / `skill-auditor` / `local-env-pitfalls/SKILL.md` 与 `references/guards.md`、`hooks/lib/` 三处删除）与运行时状态（`authorization/`、`task-notes-reminder/`）；lab-area 剩 33 条为 headroom / last30days / `.tmp-*` 实验临时文件。
- **回退**：`git reset --soft HEAD~1` 回到提交前的索引（`--soft` 不丢他人已暂存内容）。文件清单见 `git show --stat 7279ea9`。
- **验证**：`git diff --cached --check` 返回 2，556 条 trailing whitespace 全在 `installing/archive/mcp-install.md`(81) 与 `installing/archive/tool-install.md`(475)。实测这两份的 `HEAD:` 原件本就带同样 CRLF（81 / 475 条），archive 副本与 HEAD 原件 sha256 逐字节一致（`51340f70` / `855e649e`）——既有内容经纯 move 保留，非本轮引入，未做行尾归一。

### 协议校验脚本：门禁与记忆（2026-09-24）

- **变更**：新建 `hooks/scripts/protocol_check.py`（只读、非 hook、退出码 0 为全过）。`docs/protocols.md` 的 `记忆` 与 `门禁` 两行「校验」列由 `—` 改为该脚本命令，表下加一句说明另两份为何仍是 `—`。本表 hook 表加 `protocol_check.py` 一行。
- **范围决定（实测，非推断）**：四份待补协议里只有两份存在可判的固定形态。
  - 门禁：`docs/protocols/gate.md` 固定字段表的 4 个键与 `authorization_scope.py` 的 `allowed` 集合比对。实测一致。
  - 记忆：`projects/*/memory/` 下每条记忆的 frontmatter（围栏、`name`、`description`、`metadata.type` 落四枚举），以及 `MEMORY.md` 链接覆盖全部 `*.md`。
  - 任务笔记：本机两个实例（`lab-area/notes/claude-config-standards`、`notes/skill-hook-review`）的产物是自由形态的扫描稿与清单表格，没有「材料/结论/取舍」字段，也没有 `NN-` 编号。硬套字段检查会当场报约 30 条假警。
  - 委派：`references/dispatch-contract.md` 的契约是 prompt 模板，磁盘上无待验产物；`Isolation` 的取值枚举全机只出现这一处，无第二处可比。
  按 `docs/protocols.md` 共同要求第 4 条「能写成只读检查的就该有，**没有就写 `—`**」，后两份维持 `—`。
- **回退**：删 `hooks/scripts/protocol_check.py`；`docs/protocols.md` 用 `backups/protocol-check-2026-09-24/protocols.md.v1`（改前 sha256 `2f9669c4`）覆盖；`custom-setup.md` 删掉那一行。
- **验证**：真跑 `门禁 全相符`、`记忆 191 条 · 已进索引 189 · 6 处问题`，rc=1。**证伪测试**（夹具，不改脚本本体）4 组全按预期：改坏字段名报 1 处、脚本侧多一个键报 1 处、好数据报 0 处、`无围栏`/`缺 description`/`type 越界` 各报 1 处。测试脚本在 `$CLAUDE_JOB_DIR/tmp`，未落盘。
- **首跑实测到的既有漂移**（只报未改，均不在本仓库内）：`C--Users-zys31--claude` 的 `isolate-python-mock-patches.md` 与 `C--ZYS-wiki` 的 `learning-route-deduplication.md` 没进各自 `MEMORY.md` 索引；`ai-guided-from-zero.md`、`feedback-teach-before-testing.md`、`feedback-tutorial-repo-freshness.md` 只有 `---` 开围栏、没有闭围栏；`dingtalk-qa-output-redaction.md` 缺 `description`。批次 5 记过「191 条记忆全带 frontmatter」，那条口径更松；本次按围栏口径测得 3 条不合，以本次为准。
- **未做**：`任务笔记` 与 `委派` 两份的校验仍为 `—`；上述 6 处漂移属别项目名下，本脚本只报不改。

### 协议校验脚本：认出已删项目的记忆（2026-09-24）

- **起因**：用户指出 `C--ZYS-wiki` 已删。查证：源目录 `C:\ZYS\wiki` 确实不在，但 `~/.claude/projects/C--ZYS-wiki/memory/` 仍在，20 条记忆加 `MEMORY.md.before-c6` 与 `recovery/`；`projects/` 不在 git 追踪范围，那是唯一副本。上一版脚本照报它的 3 处 frontmatter 与索引问题，属无意义噪声。
- **变更**：`hooks/scripts/protocol_check.py` 的记忆一项加「源路径已删」判定——以 `~/.claude.json` 的 `projects` 映射为候选路径池（宿主只在目录被打开过时登记、且不删条目，故为「曾有过的 cwd」的超集），逐条 `os.path.isdir` 过滤得到活路径集；不在其中的项目目录只计数、不进 frontmatter 与索引检查。输出加一行分组。`docs/protocols/memory.md` 补一段孤儿记忆的处置（走协议已有的删除判据，删前进 `recovery/`），`docs/protocols.md` 表下同步说明。
- **编码规则实测**：cwd 的 `:`、分隔符、`.` 四种字符一律换成 `-`，不是只换分隔符。`C:\Users\zys31\.claude` → `C--Users-zys31--claude`。只按分隔符替换会把 `~/.claude` 与全部 `--claude-worktrees-*` 误判成已删（第一版脚本踩过）。
- **盘点结果（2026-09-24）**：`projects/` 36 个目录，源路径已不存在 27 个，其中 **16 个带记忆、共 52 条**；活着的 9 个目录 139 条。两条独立算法（`.claude.json` 映射、遍历 `C:\Users\zys31` 与 `C:\ZYS`）在孤儿集上一致，均 16 / 52。已直接核对 `C:\ZYS\Code\{my-code,pi-java,wiki,open-code-review,agent-framework}` 均不存在。
- **回退**：`git checkout b806c8f -- hooks/scripts/protocol_check.py docs/protocols.md installing/custom-setup.md`；本文件按原文改回；`docs/protocols/memory.md` 删掉新增那段。
- **验证**：真跑 `门禁 全相符`、`记忆 139 条 · 已进索引 138 · 3 处问题`，另计 `16 个目录 / 52 条（合计 191）`，rc=1。余下 3 处全在活项目里：`C--Users-zys31--claude` 1 处索引缺行、`C--ZYS-Code-dtsf` 1 处缺 `description`、`C--ZYS-Code-interview-guide` 1 处缺闭围栏。证伪测试扩到 11 组全过，含「全部当已删时不细查、只计数」。测试脚本仍在 `$CLAUDE_JOB_DIR/tmp`，未落盘。
- **未做**：那 16 个目录 / 52 条记忆未删未动。属不可恢复删除，需用户逐项确认，且按记忆协议删前要先进 `recovery/`。

### 孤儿记忆清理：52 条备份后删除（2026-09-25）

- **起因**：用户说「没用的就删了吧」。
- **口径纠正**：那 52 条孤儿记忆不加载、不召回，**占 0 token**。删它们是卫生（`~/.claude` 少 16 个查不到的死目录），不是 (a) 收益。（b）同类的还有 `.claude.json` 里 27 条死 cwd 注册，那是宿主的活状态文件，本次未动。
- **判定**：逐条读全文再判，不看文件名。52 条中——被活记忆同名覆盖 1 条（`eam-fill-existing-demo-minimal-architecture`，`C--ZYS-Code-dtsf` 下的同名条是它的超集）；被活 skill 覆盖 5 条；文章写作类已由 `article-writer` 覆盖 6 条；项目消失且内容不可迁移 39 条；过期 1 条。
- **变更**：备份到 `backups/orphan-memories-2026-09-25/`（79 个文件 = 52 条 + 16 个 `MEMORY.md` + 9 个 `recovery/` + 3 个 `.before-c6`），逐字节核对通过后删 `projects/<16 个目录>/memory/` 整棵子树。只删 `memory/`，同目录的会话记录不动——实测这 16 个目录除 `memory/` 外本来就是空的（无 `.jsonl`），删完留 16 个空壳目录未清。
- **核对缺口（如实登记）**：71 个顶层文件逐字节核对；9 个 `recovery/` 与 3 个 `.before-c6` 在子目录里，由 `shutil.copytree` 原样带过、未单独核对。
- **回退**：`projects/` 不在 git 追踪范围，回退靠 `backups/orphan-memories-2026-09-25/<项目目录名>/` 手工拷回。脚本 `purge-orphan-memories.py` 只在 `$CLAUDE_JOB_DIR/tmp`，未落盘。
- **验证**：真跑 `protocol_check.py`，「另有已删项目的 16 个目录 / 52 条」一行消失，余下 3 处漂移全在活项目，rc=1。
- **遗留风险**：`my-code-deepseek-key-exposed` 记的是 2026-07-15 有真实 DeepSeek key 进过会话上下文、要求轮换。记忆已删，轮换做过没有需用户确认。

### 六组未覆盖教训迁入活的位置（2026-09-25）

- **起因**：上一条里查出的 6 组教训在 `CLAUDE.md`、`skills/`、`.claude.json` 里都没有副本，删掉会真的丢。用户「按你建议的来」。
- **变更**：4 组进 `skills/local-env-pitfalls/SKILL.md` 的要点行——Read `offset` 只照抄工具返回行号（扩写既有的「短文件读取偏移量」一条）、Grep `glob` 禁嵌套花括号替代组、会话主目录非目标仓库时命令显式绑定路径、隔离工作树不继承 `node_modules`、`getpass` 脚本不交后台（并入同次事故的「异常报告留脱敏定位信息」）。2 组进 `projects/C--Users-zys31--claude/memory/`——`one-question-per-turn.md`、`critique-needs-full-constraint-read.md`，并补进该目录 `MEMORY.md` 索引。
- **顺带修**：同一份 `MEMORY.md` 漏掉 `isolate-python-mock-patches.md` 的索引行（`protocol_check.py` 报过的既有漂移之一），一并补上。该目录现 7 条、索引全覆盖。
- **回退**：`backups/orphan-salvage-2026-09-25/`（改前 `SKILL.md` `b10b7582…`、`MEMORY.md` `ba104688…`）。改后 `SKILL.md` `c2671693…`（6,968 → 8,430 B）、`MEMORY.md` `fff9225a…`。
- **验证**：真跑 `protocol_check.py` → `141 条记忆 · 已进索引 141 · 2 处问题`（余下 2 处在别的活项目）。
- **未做**：`dev-clean` / `dev-status` 两条自家 skill 是否改 `disable-model-invocation: true` 未定，见任务笔记。

### 自建 skill 正文逐条优化（2026-09-25）

- **变更**：21 个自建 skill 的 `SKILL.md` 正文按 `writing-for-agents` 的尺子逐条过，17 份有改动、4 份判定已是最紧。5 份补 `disable-model-invocation: true`（`coding-workflow`、`docker-only`、`install-ledger`、`parallel-delegation`、`local-env-pitfalls`）。改动集中在删无操作句、合并重复、否定改正面、删正文已承载的身份信息。
- **依据**：用户裁定「skill 正文逐条优化交给子代理去做」，配置 opus、并发 1。范围只含 (a) token 成本；输出质量与系统稳定性是禁改线，未触碰。
- **回退**：`cp backups/skill-optimize-2026-09-25/<名>/SKILL.md skills/<名>/SKILL.md` 覆盖回去。`references/`、`scripts/`、`evals/`、`assets/` 全部未动。
- **验证**：逐份 `diff` 备份与当前文件——17 份有差异、4 份逐字节相同（`awesome-design-md`、`dev-clean`、`leader`、`local-env-pitfalls`）；21 份字节合计 122,484 → 119,597（−2,887）。改动时间戳分两段（01:13–01:19、01:35–01:40），无目标之外的写入。逐条理由与「拿不准但没动」的 10 处见 `C:\ZYS\Code\lab-area\notes\skill-hook-review\SKILL-REVIEW.md`。
- **未做**：① `local-env-pitfalls` 另有 3 处待改（未翻译英文「拒绝 applies to the outcome」、未定义术语「四件套声明」、一条里塞两个无关教训）。② `article-writer` 的 `SKILL.md:144` 指向的 `examples/good-samples/` 不存在，6 篇范文可从 `5505dfa^` 取回，去向待定。③ 台账分层重构与路径命名规约已议定未执行。

### 落点与命名规约落盘 + 全库改名归位（2026-09-25）

- **起因**：交接文档九项队列的第 1/3/4/5/8/9 项。用户裁定：工作树命名并进规约、写只读校验器、范文库从 JavaGuide 公众号文章里选（旧 6 篇 + 新 2 篇，不用笔记只留原文）、72 MB 的 `.tmp-ccswitch-bak.db` 删、九项按序做完。
- **规约落盘**：`docs/protocols.md` → `docs/protocols-index.md`；「共同要求」加第 7 条与新增「落点与命名」一节（目录载分类 / 文件名载身份 / 日期或状态词载时间与状态；分类取类别轴；日期一律 `YYYY-MM-DD`；名字一律 ASCII；只管自建对象；工作树名同属本节）。`CLAUDE.md` §8、`docs/session-lifecycle.md` 的 §二 · §七 · §九 共 5 处改指规约，**解开 `CLAUDE.md` §8 ↔ `session-lifecycle.md` 的循环引用**。
- **校验器**：`hooks/scripts/protocol_check.py` 加「命名」一项，扫 `docs/`、`installing/` 全树与 `backups/` 顶层。改前实测报 32 处，全部是真问题、无假阳性。
- **backups 改名**：30 项 `YYYYMMDD` → `YYYY-MM-DD`（已合规 2 项与 CLI 写的 5 个 `.claude.json.backup.*` 未动）；全库改写 79 处引用 / 13 文件。脚本 `rename-backups.py` 在 `$CLAUDE_JOB_DIR/tmp`，未落盘。
- **docs 归档**：4 份时点产物 → `docs/archive/<日期>-<主题>.md`。日期取**内容反映的最新时点**：`config-checklist` 2026-08-11（口径头注）、`config-inventory` 2026-06-30（生成）、`opencode-migration-plan` 2026-07-03（生成）、`wsl2-sandbox-migration` 2026-09-21（评估）。四份各加一行归档头注（原路径 + 「文内路径是当时实况」），文内散文路径未改写；两份文档间的相对链接已改指新名。
- **其他改名**：`docs/handoff/` 3 个子目录补日期（`session-lifecycle-final-audit-2026-09-19`、`session-lifecycle-reaudit-2026-09-18`、`oa-dingtalk-2026-09-18`），5 处内引同步；`installing/config-slimming-snapshot-2026-09-10.json` 改名，`installing/archive/` 3 处恢复路径同步。`reaudit-2026-09-18/HANDOFF.md:137` 里的 dtsf 路径**故意未改**（另一个仓库，当时并未落地）。
- **孤本迁移**：`lab-area/.tmp-header-check/`（Codex home 快照，90 文件 / 3,400,308 B，`~/.codex/` 已不存在故为唯一副本）→ `backups/codex-home-2026-09-09/`。**未删**。注意 `backups/` 在 `.gitignore` 内，该副本仍不受 git 保护，只有一份。
- **lab-area 归位**：根目录 22 份散件 → `.claude/tmp/2026-09-25-root-cleanup/`（headroom 抓取页 12 份、last30days 运行文件 3 份、ccswitch 审计脚本 7 份、classifier-probe、4 个 `.tmp_*.js`、`.tools/`、`.impeccable/`）。两个 headroom 路由脚本**未按临时件处理**——`tool-install.md:443` 记着是用户决定保留的——移到 `exp/2026-09-09-headroom-routing/` 并配 README。`.gitignore` 加 `.claude/tmp/` 与 `.claude/worktrees/`。**这两个脚本现在跑不通 config.toml 分支**：`~/.codex/config.toml` 已于 2026-09-10 随 Codex 清除。
- **删除（不可逆，用户确认）**：`lab-area/.tmp-ccswitch-bak.db`，72,105,984 B，mtime 2026-09-09 22:12，sha256 `5d186fc4c9fe0927…`。删前复核非孤本：活库 `~/.cc-switch/cc-switch.db` 93,245,440 B（当日 09:58）+ `~/.cc-switch/backups/` 7 份库备份（2026-09-19…24，86–93 MB）全部比它新。
- **article-writer 范文库**：`examples/good-samples/` 重建 8 篇 / 181,419 B。6 篇取自 `C:\ZYS\Study\JavaGuide` clone `d76264cb`，2 篇取自 JavaGuide 公众号（`claude-code-to-pi.md`、`better-harness-health-check.md`）。加工只有三件：去 VitePress frontmatter 与 `@include` 广告指令、去纯图片行（`SKILL.md:29` 明令不产图片链接）、去提取器分节（摘要段是正文开头的截断副本、`## 提取元信息` 是工具产物）；正文逐字保留，每篇加一行出处（JavaGuide 为 Apache-2.0，署名是许可义务）。`examples/README.md` 索引分「面试／技术问答类」「AI Coding 类」两组。
- **回退**：规约与 CLAUDE.md 用 `backups/naming-protocol-2026-09-25/`（`CLAUDE.md.v1` `dbf638ab…`、`session-lifecycle.md.v1` `e79b2a91…`、`protocols.md.v1` `cb77a58c…`、`protocol_check.py.v1` `e9fc38b0…`、`custom-setup.md.v1` `fd72597c…`）；范文库索引用 `backups/article-writer-samples-2026-09-25/examples-README.md.v1`，8 篇范文删掉即可回到断裂态；改名类全部是 `git mv`，`git mv` 反向 + 引用同法改回；`codex-home-2026-09-09/` 移回 `lab-area/.tmp-header-check/`；`.tmp-ccswitch-bak.db` **无回退**。
- **验证**：`protocol_check.py` 真跑，「命名 90 个名字（backups/ 顶层 · docs/ · installing/），**全相符**」，问题数由 32 归 0；门禁 4 键全相符、记忆 142 条全进索引。改名后逐项目核对文件数与字节（`codex-home` 迁前迁后均 90 文件 / 3,400,308 B）。范文库核对：图片行与 `@include` 残留均为 0。
- **未做**：① 队列第 6 项（`skill-install` 台账分层重构）**未执行**——议定形状是 `installing/<账本>/<资产>/<日期>.md`，但 `skill-install` 的流水里除资产条目外还有大量**跨资产的事件批次**（2026-08-25/26 插件化清理、2026-09-03 库精简、2026-09-10 插件全量精简、ArkCLI 卸载、wiki 系迁移），没有对象轴可挂；硬按资产拆就是议定里明令避免的「造假拆分」。设计取舍待用户裁。② 队列第 7 项（`local-env-pitfalls` 3 处）未动。

### 队列第 7 项 + 流水归档头（2026-09-25）

- **起因**：队列第 7 项，以及第 6 项勘察中发现的流水文件缺归档标识。
- **local-env-pitfalls 三处**（`skills/local-env-pitfalls/SKILL.md`，8,461 → 8,846 B，sha256 `d3b8e5415b2eb5f0…`）：① 「拒绝 applies to the outcome」改为中文并去掉否定式引导——「分类器拒了就停手报告：拒绝针对的是**结果**（这个产出能不能落地），不是这一条命令的写法」；② 「四件套声明」补出四项内容（调用者／无重复／数据文件性质／用户指令原文引用）并留 `references/guards.md` 指针；③ 原「`getpass` 脚本不交后台」一条里塞的第二件事（验收脚本异常报告要留脱敏后的失败阶段、目标路径与异常类型）拆出，独立成条移入「验证与统计」。
- **流水归档头**：`installing/archive/` 四份流水各在 H1 后加一行——标「已归档（2026-09-24 现状表与流水分家）／默认不读／现状表见 `../<台账>.md`／文中 `[X.md](X.md)` 指向本目录同名流水」。搬迁时保留了旧现状表头（「记录自建 skill / hook / statusline / 全局配置…」），读起来像现役索引。
- **断链修复**：`archive/` 三份的 `模板见 [README.md](README.md)` → `../README.md`（`archive/README.md` 不存在）。其余 `[tool-install.md](tool-install.md)` 类链接**故意未动**——目标存在且部分确实意指本目录同名流水（如 `custom-setup.md:239` 引的「Skill 库精简（2026-09-03）」只在流水里有），意图逐条不同，不能批量改。
- **记忆 frontmatter 修复**（两个活项目，`protocol_check.py` 长期报的既有缺陷）：`projects/C--ZYS-Code-interview-guide/memory/ai-guided-from-zero.md` 补 `---` 围栏结尾（sha256 `2594939aef9424870fda…`）；`projects/C--ZYS-Code-dtsf/memory/dingtalk-qa-output-redaction.md` 把 `description` 从 `metadata:` 下提到顶层（`docs/protocols/memory.md` 的固定字段如此规定；宿主的 `node_type`/`originSessionId`/`modified` 原样留在 `metadata` 下），sha256 `1fffe8d08b2a7433c88b…`。
- **行尾与 diff 可读性**：改 `archive/tool-install.md` 时编辑工具把整文件 CRLF 翻成 LF，`git diff` 一度涨到 1,004 行；已转回 CRLF，diff 收回 4+/2−。该库四份流水里 `tool-install`／`mcp-install` 是 CRLF、其余是 LF（`git ls-files --eol` 可查），`git diff --check` 会把 CRLF 的新增行一律报成 trailing whitespace。已在**本库** `~/.claude/.git/config`（非追踪文件）设 `core.whitespace cr-at-eol`，`--check` 由 6 条假阳性归 rc=0。
- **回退**：两份记忆改前副本在各自 `memory/recovery/2026-09-25-<原名>.md`；`local-env-pitfalls` 用 `backups/local-env-pitfalls-2026-09-25/SKILL.md.v1`（`f9d131d7a38c316a…`）；流水头与断链去掉那几行即可；`git config --unset core.whitespace`。
- **验证**：`ledger_check.py` rc=0（101 行 · 待核 9 · 17.8 KB，插件 7 行相符，archive 四份齐）；`protocol_check.py` **rc=0**——「记忆 142 条 · 已进索引 142 · frontmatter 与索引全相符」「命名 93 个名字，全相符」「门禁 4 键全相符」。
- **未做**：队列第 6 项（台账分层重构）仍未动。本轮补充勘察：`installing/README.md:15` 明写 `archive/` **默认不读**，重构流水不省任何 token；`archive/skill-install.md` 的 6 条单件登记里 `eli5`／`modlens`／`archify`／`agent-browser`／`cangjie-skill` 已不在盘上，`last30days` 在 `plugins/cache/`、`leader` 归自建台账管——**现状表（2 行）与实际在用集合相符**，「两处真相」的实用风险不成立。取舍待用户裁。
