# 自建设施台账（非外部安装，自己造的）

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
| `~/.claude/hooks/scripts/session-guard.py` | `start` / `end` 两个子命令。开发前报告本仓库主检出与各工作树的卫生状况，开发结束写收尾记录。不删除任何东西。收尾记录的追加与裁剪共用一把锁，裁剪在锁内重新读取，避免读到旧快照整份写回而丢掉并发追加的记录 |
| `~/.claude/hooks/scripts/product-guard.py` | PreToolUse 拦截：`git worktree add` 的目标路径解析后不在本仓库主检出 `.claude/worktrees/` 下，或工作树名不合规（hash、纯日期、保留名、非 kebab-case）；`EnterWorktree` 的 `name` 与 `path` 同样校验。命令拆成词后取出每一处真正的目标路径再规范化比对，不按子串判断；带值选项按 git 2.54 的用法行登记 |
| `~/.claude/hooks/scripts/session-status.py` | 只读汇总活跃会话、工作树四分类、孤儿目录、stash、主检出、仓库根散落文件、登记端口、容器。会话枚举失败时显式标注降级，可清理项标出被忽略内容 |
| `~/.claude/hooks/scripts/selftest.py` | 自检，`python selftest.py`，退出码 0 表示全过 |

纯 stdlib，无第三方依赖。Python 解释器固定用 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`（与 settings.json 其他 hook 一致）。

设计取舍：只有工作树位置与命名进硬拦截，因为它们是客观可判定的，且建错位置的代价高。仓库根建文件由 `/dev-status` 报告违规项；产物放错目录没有自动检查，靠文本约定。所有删除都走 `/dev-clean` 并逐条确认，不存在自动删除路径。子代理工作树由 harness 以 `agent-<hash>` 命名创建，拦截管不到，只能靠 `/dev-status` 的孤儿目录分类暴露。把命令再包一层解释器（`bash -c "…"`、`python -c "os.system(…)"`）之后顶层拆词看不到 `git worktree add`，会放行；拦截的定位是防止误建，不作为安全边界。

### 命令与配置

- `~/.claude/commands/dev-status.md`、`~/.claude/commands/dev-clean.md`
- `~/.claude/settings.json` hooks 段新增：`SessionStart` 第 3 组（session-guard start，timeout 25）、`SessionEnd` 1 组（session-guard end，timeout 15）、`PreToolUse` 1 组（product-guard，matcher `Bash|EnterWorktree`，timeout 15）
- `~/.claude/CLAUDE.md` 第 8 节「会话、产物与本地资源」，7 段：工作树 / 产物去处 / 交接文档 / 并行会话 / 收尾 / Git 写权限 / 查看与清理
- `~/.claude/docs/session-lifecycle.md`：机制说明、操作方式、故障处理

### 运行时数据

`~/.claude/session-handoff.jsonl`（收尾记录，保留 7 天，按 `repo` 字段过滤，只报告本仓库的遗留；`repo` 统一取主检出根，所以从链接工作树里开会话也能对上）、`~/.claude/session-handoff.lock`（收尾记录的写入锁，正常跑完即删，超过 30 秒视为陈旧锁自动接管）、`~/.claude/session-guard.log`（异常，以及过期记录被丢弃时留下的路径与改动数）、`~/.claude/product-guard.log`。

活跃会话来自 `claude agents --json`，这是官方文档给出的受支持接口（`cwd`、`kind`、`startedAt`、`pid`、`status`、`sessionId` 等字段）。不读 `~/.claude/sessions/*.json`——官方文档从未描述该目录，并与 `~/.claude/jobs/<id>/` 同属被明确声明为「不是稳定接口」的内部层。`/dev-status` 用它区分工作树是在用还是可清理；枚举失败时 `active_sessions()` 返回 None，输出显式标注「活跃会话 枚举失败」并提示不要据此删除，不伪装成无人占用。

### 验证

自检脚本 `~/.claude/hooks/scripts/selftest.py`（`python selftest.py`，退出码 0 表示全过）：122 个用例全部通过。覆盖工作树位置越界、相对路径上跳、`..` 路径穿越、`.claude/worktrees/` 只出现在 `-b` 参数或注释里、`.claude` 下的非约定目录、`worktrees-old` 前缀混淆、hash 命名、保留名与纯日期、非 kebab-case 命名、反斜杠写法、`worktree list` / `worktree remove` 放行、同一条命令里串联多处 `git worktree add`、重定向被当成目标路径、`--lock` / `--track` 不带值的选项、`git -C <仓库>` 与 `cd <仓库> &&` 的判定基准、`EnterWorktree` 的 `name` 与 `path` 两条入口、非 git 目录静默、`~/.claude` 静默、跨仓库遗留不串味、从链接工作树里开会话按主检出汇报、会话枚举为空或字段缺失时不崩溃、退出提示不承诺自动清理、收尾记录并发追加不丢、过期记录丢弃写日志、无需裁剪时不重写文件、陈旧锁自动接管、仓库根散落文件与孤儿目录（含符号链接）的识别、被忽略内容单列、枚举失败打印降级告警。在脚本同级建临时 git 仓库当沙箱，`try/finally` 保证跑完自删。

真实仓库实测（2026-09-18，dtsf，1 个工作树）：SessionStart 耗时 0.65 秒，`/dev-status` 耗时 1.48 秒。

收尾记录的并发行为实测：两个裁剪进程加一个追加进程各跑独立 Python 进程，6 轮共追加 240 条，丢失 0 条。修复前同一套用例的丢失率是 22.5%（240 条丢 54 条），成因是裁剪读到快照后整份写回，覆盖了这期间追加的记录。

性能随工作树数量近线性：`/dev-status` 约每棵 84 毫秒，SessionStart 约每棵 73 毫秒，主导成本是每棵一次 `git status --porcelain` 子进程。70 棵工作树时 `/dev-status` 约 7.2 秒。

Windows 编码：hook 输出必须显式 `sys.stdout.reconfigure(encoding="utf-8")`，否则默认 GBK 会破坏中文 JSON。三个脚本的 `main` 都有这一行。

### 删除安全边界

删除是不可恢复动作，机制按三条线约束：

1. **机制自身不删任何东西。** 没有自动清理路径，只有 `/dev-clean` 命令，且必须逐条列出路径等用户确认。
2. **有未提交改动的工作树删不掉。** `/dev-clean` 只列零改动的项，`git worktree remove` 本身也会拒绝脏工作树。被拒时不许用 `--force`。
3. **孤儿目录一律不删。** git 已不再注册它们，里面的改动不在任何分支上，`/dev-status` 会标出有没有同名分支。标「无同名分支」的目录是内容的唯一副本，机制不碰，交用户判断。
4. **被 `.gitignore` 覆盖的内容会被连带删除，所以单列标注。** `git status --porcelain` 看不到被忽略的文件，只含这类文件的工作树会被判定为干净并列入可清理，而 `git worktree remove` 会连那些文件一起删掉且退出码为 0。`/dev-status` 因此在可清理项上标出「另有 N 项被忽略内容」，`/dev-clean` 要求用户确认完整路径清单后才执行。

### 回退

从 `~/.claude/settings.json` 的 hooks 段删掉 `SessionStart` 第 3 组、`SessionEnd`、`PreToolUse` 三段即可，三个脚本变成不被调用的惰性文件。命令与文档（`dev-status.md`、`dev-clean.md`、`session-lifecycle.md`、`selftest.py`）可一并删除。

运行时数据也要清掉：`session-handoff.jsonl`、`session-handoff.lock`（残留的锁会让下次写入等待 2 秒再降级）、`session-guard.log`、`product-guard.log`。`session-hygiene.json` 是本机端口与独占资源台账，独立于本机制，应保留。

机制本体已提交并推送到 `~/.claude` 仓库，远程 `origin` 为 `https://github.com/zys3198/claude-stack`。要恢复某个版本，从该仓库检出对应提交即可；看当前实现则直接读 `~/.claude/hooks/scripts/` 下四个脚本。

---

## 自建 skill（当前目录 + 历史记录，非 cc-switch 同步）

- 2026-09-11 新增全局 `ai-product-development`，详见下方独立台账条目。
- 2026-09-11 新增全局 `company-discovery-evaluation`，详见下方独立台账条目。

当前可用（2026-09-02，以 `skills/` 实际目录为准）：
`ai-coding-coach`、`ai-readable-project`、`article-writer`、`article-writing-guide`、`bidirectional-steelman`、`bili-note`、`cc-switch-setting-sync`、`code-change-workflow`、`content-to-note`、`deep-learn`、`drawio-article-illustration`、`drawio-chart`、`expose-unknowns`、`generic-course-tutor`、`goal-run`、`improver-skill`、`install-ledger`、`learning-guide`、`learning-personas`、`parallel-delegation`、`preflight-check`、`skill-auditor`、`skill-trimmer`、`tech-learning-roadmap`、`tutorial-maker`、`wiki-sediment`。

`generic-course-tutor-workspace` 是配套工作区，不计入 skill。

### generic-course-tutor（2026-09-01，全局）
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

### cc-switch-setting-sync
- 出处：防 cc-switch 切换 provider 降级 settings.json 的同步流程

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

### 学习 skill（自建 2 个）
- deep-learn / tutorial-maker
- ~~cram-engine~~：2026-08-11 复核用户未认领为自建，移出 Git 白名单（归 skill-install.md 待补来源）

### ~~2026-08-11 复核新增自建（7 个，已入 Git 白名单）~~（2026-08-16 核实全不在磁盘，白名单已清）
- ~~ai-text-polisher / answer-evidence-finder / critical-thinking / doc-finder / humanizer-zh / interview-ai-agent-dev / interview-java-backend~~
- 出处：用户逐个勾选自认定稿（推翻此前「ignored 即第三方」的机器推断）。注：critical-thinking、humanizer-zh 公网存在同名项目，以用户判定为准——若实为改过/重写版本，建议日后在 SKILL.md 注明 fork 来源。
- **2026-08-16 审查实测**：7 个磁盘目录均不存在（疑 2026-08-13 清理随备份夹消失），`.gitignore` 白名单条目已移除；**恢复口径更正（2026-08-16 盘查）**：7 个全部存在于 `d57e5c0^`（28-skill 移备份批次的父提交），`git checkout d57e5c0^ -- skills/<名>` 即恢复，无需重建；ai-text-polisher 例外——已删、被 human-writing 替代，**不恢复**，见下文终判。critical-thinking 来源见 skill-install.md 更正。

### ai-readable-project（2026-08-13，全局）
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

### wiki-sediment + /wiki-save（2026-08-11，全局）
- 位置：`~/.claude/skills/wiki-sediment/SKILL.md` + `~/.claude/commands/wiki-save.md`（全局，随 ~/.claude git 迁移——已加 .gitignore skills/ 白名单）
- 出处：spec `C:\ZYS\Wiki\docs\superpowers\specs\2026-08-11-wiki-sediment-design.md`（原 commit 3cdfb7e 为 wiki 项目级，同日用户拍板改全局）
- 内容：沉淀四路径（书籍→knowledge-note / 对话→learning-record / 错误→memory feedback / 仪表盘刷新），复用 wiki-structure 规约；wiki 目标路径硬编码 `C:\ZYS\Wiki`（迁机需改）
- 依赖：`C:\ZYS\Wiki` 的 wiki-structure skill、`93-templates/`、`scripts/refresh-due.py`

### /fy 翻译命令（2026-08-14，全局）
- 位置：`~/.claude/commands/fy.md`（全局自定义命令，单文件，随 ~/.claude git 迁移）
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
- 配置备份：`~/.claude/backups/settings-before-six-hook-prune-20260908-112215.json`。
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
- 备份：`~/.claude/hooks/HOOKS_BACKUP.md`
- **~~turn_counter.py~~ / ~~learning_nudge.py~~（2026-08-08 已删）**：曾为死代码（settings.json 未引用），2026-08-08 经用户确认物理删除；状态文件 `turn_state.json` / `learning_state.json` 同删。hooks/ 现有 settings.json 引用的 8 个 Python hook，另有 2 个未挂载的 dormant Python hook：`plugin_drift_check.py`、`skill_ledger.py`。
- **settings-degrade-guard.py（2026-08-13 新建）**：SessionStart 自动检测 cc-switch 切 provider 降级 settings.json（缺 statusLine/enabledPlugins/extraKnownMarketplaces/permissions.deny 或 >3 个 hook），从 cc-switch DB `common_config_claude` 快照并集合并恢复（保留 provider env），原子写+备份到 `~/.claude/backups/settings.bak-guard-<ts>.json`。静默运行，恢复时输出 JSON 提示。注册在 settings.json SessionStart `*` matcher。与 cc-switch-setting-sync skill 的 `--restore` 同源逻辑（见该 skill SKILL.md §4）。
- **skill_ledger.py（2026-08-17 新建）**：PostToolUse 记账 hook，matcher `Skill`。记 Skill 调用 → `~/.claude/metrics/skill-usage.log`（JSONL，坏输入/非 Skill 静默 exit(0) 不阻塞）。配 skill-trimmer 的 scan_skills.py 做使用计数（`load_usage()` 读它，剥 `plugin:` 前缀归一）。Python312 调用。
- **hooks/scripts/transcript_sweep.py（2026-08-17 新建）**：周复盘脚本，非 hook（不进 settings.json）。扫最近 N 天会话 user 消息 → 去重/CJK 高频主题 → `~/.claude/metrics/transcript-weekly-YYYYMMDD.md`。纯 stdlib。周惯例手动跑：`python ~/.claude/hooks/scripts/transcript_sweep.py 7`。
- **2026-08-17 settings.json**：PostToolUse 末尾加独立 `Skill` matcher 分组（调 skill_ledger.py）；备份见常规 settings 快照。
- **2026-08-17 skill 修改（非新建，git 已追踪）**：code-change-workflow 加 §1.4.1「Agent 汇报核对清单」（JavaGuide Redis 案例）；skill-trimmer 加保鲜维度——scan_skills.py 每 skill 输出 `last_modified`/`usage_count`/`staleCandidate`（STALE_DAYS=180）+ SKILL.md 数据驱动段加「本机自动化三件套」命令引用。

### statusline（已脱离 ecc）
- 位置：`~/.claude/statusline`，含 cost + git 分支段（memory `statusline-independent-of-ecc`）
- 文件清单（2026-08-08 实测）：`statusline.js`（入口，settings.json statusLine 调它）+ `cost-tracker.js` + `context-monitor.js` + `metrics-bridge.js` + `lib/`（agent-data-home.js / session-bridge.js / utils.js）
- **2026-08-13 数据源剥离完成**：statusline 脚本早已独立，但其 cost/工具计数数据源（`post:ecc-metrics-bridge` hook 写 `/tmp/ecc-metrics-{session}.json`）此前仍绑 ecc 插件。已复制为自建 hook：`~/.claude/hooks/ecc-metrics-bridge.js` + `~/.claude/hooks/lib/`（agent-data-home.js / session-bridge.js / utils.js，ecc 版；require 路径已改 `./lib/`）。settings.json PostToolUse 已注册 `*` matcher 调它。验证：喂真实 session 数据 → bridge 文件生成 → statusline 输出含 `Nt 时长` 段。cc-switch `common_config_claude` 快照已同步。
- **2026-08-13 晚：ecc 插件整体卸载**（见下方「ecc 剥离/卸载」章节），原 `env.ECC_DISABLED_HOOKS`（禁 ecc 原版 metrics-bridge + gateguard）已随卸载删除。自建 metrics-bridge 是唯一 bridge 数据源，无双写问题。

### settings.json 关键本机定制
- `enabledPlugins` 清单快照见 tool-install.md
- lean-ctx 注入段在 CLAUDE.md 尾部（`<!-- lean-ctx -->` 包围，官方注入，别手改）

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
- **MCP**：chrome-devtools 独立保留 → `claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest`（写入 `~/.claude.json` 顶层 mcpServers，user scope；原 ecc `.mcp.json` 定义）。**注意**：settings.json 顶层不支持 `mcpServers`（死配置，官方确认），别放那。
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
- **配置**：`~/.claude/settings.json` 的 `hooks` 现只有 `Notification`、`PostToolUse`、`SessionStart`、`StopFailure` 四类；`~/.claude/session-hygiene.json` 不变。
- **依赖**：psutil（本机 Python 3.12.10 已装 7.2.2）；清点脚本用绝对解释器路径 `C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe` 调用，换机器需要改 `SKILL.md` 对应那一行。
- **验证**：清点脚本改后在 DTSF 实跑通过（退出码 0，20 个工作树、18 条 stash、11 条无远端分支、2 个独占容器运行中）。审查同时查出两处与实测不符的既有记载并已改正：memory `avoid-second-vite-port.md` 关于 9528 与 `strictPort` 的说法、`session-inventory.py` 输出里关于未提交改动能否恢复的说法。
- **未验证**：宿主在三条自动清理路径上保留工作树的行为取自 `claude.exe` 代码与审查者复核，未做端到端实测；eval case `worktree-closeout` 尚未跑 runner。
- **已知缺口**：`~/.claude/docs/config-checklist.md` §2.1 与 `config-inventory.md` §1.3 记载的七个 PreToolUse 脚本（`git_guard.py`、`secret_guard.py`、`dep_gate.py`、`placeholder_guard.py`、`edited_tracker.py`、`verify_recorder.py`、`verify_gate.py`）在 `~/.claude/hooks/` 下均不存在，`settings.json` 也没有挂载 `PreToolUse`；两份文档尚未按实际状态改写。
- **回退**：`SKILL.md` 与 `CHANGELOG.md` 恢复到 1.3.0 内容并重新加入钩子脚本与 `settings.json` 挂钩；`toolchain-pitfalls` 的删除项需从会话记录还原。
