# 自建设施台账（非外部安装，自己造的）

记录自建 skill / hook / statusline / 全局配置的出处与迁移要点。外部装的见 skill-install.md / mcp-install.md / tool-install.md。

自建资产迁移原则：**git 仓库已追踪全部自建**（32 个 skill + CLAUDE.md + hooks + statusline + installing/ 本目录，见 `.gitignore` skills/ 白名单；2026-08-11 用户人工复核定稿：勾选确认的进 Git，未认领的移出），`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠 skill-install.md / tool-install.md 记录的地址与命令重装。

---

## git_guard.py 修改（2026-08-14）

- **位置**：`~/.claude/hooks/git_guard.py`（PreToolUse git 守卫，Python，约 120 行）
- **改动**：新建分支（`git checkout -b` / `git switch -c`）从无条件 deny 改为与 commit/push 一致的「用户确认放行」——`user_confirmed(data)`（读会话 transcript 检测用户最近消息含 确认/批准/授权/confirm 等词）命中则放行，否则 deny。仅改这一个 elif 分支。
- **保持不变**：BLOCK 列表（89-108 行）不可逆/破坏性操作（git reset --hard、branch -D、push --force、clean -f、rm -rf、SQL DROP、--no-verify、npm publish 等）仍无条件拦截；commit/push 确认放行逻辑未动。
- **需求来源**：用户指令「git_guard 修改成，除了不可逆的操作，在我确认之后都可以直接执行」（2026-08-14，子代理执行）。
- **验证**：`python -m py_compile git_guard.py` 通过（PY_COMPILE_OK）。
- **回退**：还原该 elif 分支为 `deny("CLAUDE.md §1.1: 新建分支前确认 git status 干净...")` 一行。

---

## 自建 skill（~/.claude/skills/ 下，非 cc-switch 同步）

### 四域开工路由器（v1.4.x，持续演进）
- `ai-coding-guide`（编码域，v1.4.9）/ `article-writing-guide`（写作域）/ `learning-guide`（学习域，v1.4.6）/ `frontend-guide`（前端域，v1.5.3）
- 出处：2026-07 多轮会话沉淀；质量标准见 memory `router-guide-skill-quality-bar`；审查工具 `guide-skill-auditor`
- 迁移要点：四个一起拷；各有 CHANGELOG.md 记演进；互相有跨域转介引用，别只拷一个。

### code-change-workflow
- 出处：2026-07-29 CLAUDE.md 瘦身（§1-4 流程迁入，memory `claude-md-slimming-20260729`）
- 内容：改前/改中/改后清单、AI 代码审查、调试、Agent 调度、止血回退

### expose-unknowns
- 出处：暴露 unknown 方法论沉淀（memory `expose-unknowns-method`）

### guide-skill-auditor（v1.3.0）
- 出处：router 型 guide 质量审查方法论固化（memory `router-guide-skill-quality-bar`）

### skill-trimmer
- 出处：skill 库精简判定框架（Carl 四删五留 + 本机三决议，memory `skill-trim-carl-article-2026-07-28`）

### cc-switch-setting-sync
- 出处：防 cc-switch 切换 provider 降级 settings.json 的同步流程

### learning-personas
- 出处：2026-08-16 从 DeepTutor（eduhub.deeptutor.info，本地装于 `C:\ZYS\Code\deep-tutor`）三 persona（peer/teacher/research-assistant）提炼，用户拍板独立 skill + CLAUDE.md 引用式
- 内容：**学习系统总纲 + 说话层角色库**。三个正交决定：判级查（expose-unknowns）/ 归属问（这技能归你吗→你练/我讲/存起来）/ 说话层（peer/teacher/research）。全系统学习模式唯一词汇源
- 接线：CLAUDE.md 尾部「## 学习角色（引用式）」被动触发规则（学习时刻才套，执行型任务不启用）；四 guide（learning-guide / ai-coding-guide / article-writing-guide / ai-coding-coach）开工问询词汇统一换为归属+persona 并引用本 skill（渐进式披露，不散落展开）；learning-first memory 四分支并进归属一问
- 迁移要点：SKILL.md 单文件；无脚本无依赖；与 cram-engine/deep-learn/expose-unknowns 互补（流水线 vs 说话方式）；换词涉及 guide 时同步改 CHANGELOG + references + test-prompts；**已入 git 白名单**（`.gitignore` skills/ 白名单新增 `!skills/learning-personas/`，2026-08-16）

### 写作 skill（自建 11 个）
- article-writer / chinese-markdown-normalizer / javaguide-style-guide / multi-review-pipeline / drawio-article-illustration / drawio-chart / publish-final-check / plagiarism-audit / review-doc / tech-article-review / content-to-note
- 出处：2026-06/07 写作流程沉淀；publish-final-check 演进耦合在 article-writing-guide/CHANGELOG.md；plagiarism-audit 针对实战漏网（Codex-book 整源漏审）设计；tech-article-review 与 review-doc 划边界（单 agent 逐段增量 vs 4 agent 并行）
- ~~edit-article~~：2026-08-11 复核用户未认领为自建，移出 Git 白名单（归 skill-install.md 待补来源）

### 学习 skill（自建 2 个）
- deep-learn / tutorial-maker
- ~~cram-engine~~：2026-08-11 复核用户未认领为自建，移出 Git 白名单（归 skill-install.md 待补来源）

### 2026-08-11 复核新增自建（7 个，已入 Git 白名单）
- ai-text-polisher / answer-evidence-finder / critical-thinking / doc-finder / humanizer-zh / interview-ai-agent-dev / interview-java-backend
- 出处：用户逐个勾选自认定稿（推翻此前「ignored 即第三方」的机器推断）。注：critical-thinking、humanizer-zh 公网存在同名项目，以用户判定为准——若实为改过/重写版本，建议日后在 SKILL.md 注明 fork 来源。

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

### 前端 skill（自建 1 个）
- shadcn-vue-guide（中文手写 + 本机 .bak 编辑痕）

### ai-coding-coach
- 学习陪跑模式（partner-coach/coach/engineer），ai-coding-guide 路由出口的协作行为定义

### ~~handoff / teach~~（更正 2026-08-07）
- **非自建**——磁盘上是 Matt 插件 symlink（指 plugins/cache），归 Matt 插件管，见 skill-install.md Matt Pocock 条目。之前误标自建。

### ~~obsidian-vault~~（2026-08-07 删除）
- 曾硬编码 wiki 路径（C:\ZYS\Code\wiki），用户拍板删除磁盘目录。若日后需要按 skill-install.md 散件检索重装。

### ai-text-polisher（更正 2026-08-11）
- 此前记录「2026-08-08 删除，被 human-writing 替代」**有误**：磁盘目录完整存在，用户复核确认为自建，已恢复 `.gitignore` 白名单追踪。human-writing 用户未认领，归第三方。

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

## hooks / statusline / 配置

### ~/.claude/hooks/
- ecc 系 hooks（Fact-Forcing Gate / GateGuard 等）随 ecc 插件来；另有自建/调整个别脚本
- 备份：`~/.claude/hooks/HOOKS_BACKUP.md`
- **~~turn_counter.py~~ / ~~learning_nudge.py~~（2026-08-08 已删）**：曾为死代码（settings.json 未引用），2026-08-08 经用户确认物理删除；状态文件 `turn_state.json` / `learning_state.json` 同删。hooks/ 现仅留 settings.json 引用的 7 个 Python hook。
- **settings-degrade-guard.py（2026-08-13 新建）**：SessionStart 自动检测 cc-switch 切 provider 降级 settings.json（缺 statusLine/enabledPlugins/extraKnownMarketplaces/permissions.deny 或 >3 个 hook），从 cc-switch DB `common_config_claude` 快照并集合并恢复（保留 provider env），原子写+备份到 `~/.claude/backups/settings.bak-guard-<ts>.json`。静默运行，恢复时输出 JSON 提示。注册在 settings.json SessionStart `*` matcher。与 cc-switch-setting-sync skill 的 `--restore` 同源逻辑（见该 skill SKILL.md §4）。

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

## memory
- 位置：`~/.claude/projects/C--Users-zys31/memory/`
- 迁移：整目录拷；MEMORY.md 是索引。
