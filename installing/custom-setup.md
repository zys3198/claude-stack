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

## 自建 skill（当前目录 + 历史记录，非 cc-switch 同步）

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
