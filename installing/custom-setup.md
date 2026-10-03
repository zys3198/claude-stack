# 自建设施台账（非外部安装，自己造的）

记录自建 skill / hook / statusline / 全局配置的当前位置与迁移要点。外部装的见 [skill-install.md](skill-install.md)、[tool-install.md](tool-install.md)、[mcp-install.md](mcp-install.md)。

自建资产迁移原则：**git 仓库应追踪全部自建 skill**（新增自建 skill 必须在 `.gitignore` 的 skills/ 白名单登记）；`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠另三本台账记录的地址与命令重装。

历史变更在 [archive/custom-setup.md](archive/custom-setup.md)，默认不读。

## 自建 skill（17 在用）

2026-10-02 原 21 份在册（17 在用 + 4 空壳）全部处理：4 份空壳与 `company-discovery-evaluation-by-user` 已删，删因见流水同日。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| article-writer | 在用 | `~/.claude/skills/article-writer/` | 自建 | git | 含 examples/；2026-09-26：按 writing-for-agents 收窄为单篇中文技术内容的创作与深度改写入口；仍仅用户显式调用 |
| auto-browser | 在用 | `~/.claude/skills/auto-browser/` | 自建 | git | 2026-09-24 自建合并；2026-09-26：按 writing-for-agents 前置网页操作、抓取与验收入口，并保留两条浏览器路线 |
| awesome-design-md | 在用 | `~/.claude/skills/awesome-design-md/` | 自建 | git | 2026-09-26：触发描述补齐视觉约束与网页实现两种入口；保持本地资料来源边界 |
| bidirectional-steelman | 在用 | `~/.claude/skills/bidirectional-steelman/` | 自建 | git | 2026-09-26：按 writing-for-agents 收窄为方案取舍、技术选型与「怎么办」的论证入口；仍仅用户显式调用 |
| coding-workflow | 在用 | `~/.claude/skills/coding-workflow/` | 自建 | git | 含 references/；2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 收窄为代码改动、审查与回退入口；恢复模型可调用；2026-09-27：1.9.0 去除与 `docker-only`、`parallel-delegation`、`mattpocock-skills:code-review` 的重复规程，保留编码特有门禁 |
| content-to-note | 在用 | `~/.claude/skills/content-to-note/` | 自建 | git | 2026-09-20 起仅手动调用；2026-09-26：按 writing-for-agents 保留三类来源与学习型笔记目标；仍仅用户显式调用 |
| dev-clean | 在用 | `~/.claude/skills/dev-clean/` | 自建 | git | 由 `commands/dev-clean.md` 迁入；2026-09-26：触发描述收窄为用户明确项目收尾，并保留资源删除／停止与 push 门禁 |
| dev-status | 在用 | `~/.claude/skills/dev-status/` | 自建 | git | 由 `commands/dev-status.md` 迁入；2026-09-26：触发描述改为查看仓库状态并原样返回脚本输出 |
| docker-only | 在用 | `~/.claude/skills/docker-only/`（触发面；正文在 `docs/protocols/execution-env/execution-env.md`） | 自建 | git | 2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：触发描述前置运行动作、受限容器流程与宿主边界；恢复模型可调用。2026-09-27：正文挪进 `docs/protocols/execution-env/execution-env.md`，`references/new-project-setup.md` 移到 `docs/protocols/execution-env/`；本 Skill 只剩触发面与必读指针，仍 model-invocable |
| drawio-chart | 在用 | `~/.claude/skills/drawio-chart/` | 自建 | git | 含 examples/ |
| improver-skill | 在用 | `~/.claude/skills/improver-skill/` | 自建 | git | 原名 wiki-skill；2026-09-26：按 writing-for-agents 明确 Trace、Pattern、候选 Skill 与 gate 四个入口；仍仅用户显式调用 |
| leader | 在用 | `~/.claude/skills/leader/` | 自建 | git | 2026-09-24 补进 `.gitignore` 白名单，此前一直被忽略；2026-09-26：按 writing-for-agents 明确调研、独立执行与验收任务书入口；仍仅用户显式调用 |
| last30days | 在用 | `~/.claude/skills/last30days/` | 本地化，上游已切断 | git | v3.25.0；原第三方裸 skill 已本地化，`disable-model-invocation: true`，按 `/last30days` 手动调用；含 `references/` 与 `scripts/`，跳过上游 `assets/`。2026-09-29 的 git 复核与轻量化勘察见流水 2026-09-29。备份 `backups/skill-last30days-slim-2026-09-29/` |
| local-env-pitfalls | 在用 | `~/.claude/skills/local-env-pitfalls/` | 自建 | git | 含 references/；2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 前置脚本、命令与子代理执行前的坑位查询入口；恢复模型可调用 |
| parallel-delegation | 在用 | `~/.claude/skills/parallel-delegation/`（触发面；正文在 `docs/protocols/delegation/delegation.md`） | 自建 | git | 2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 明确单个／并行委派及配置确认门禁；恢复模型可调用。2026-09-27：正文挪进 `docs/protocols/delegation/delegation.md`，三份 `references/` 移到 `docs/protocols/delegation/`；本 Skill 只剩触发面与必读指针，仍 model-invocable |
| asset-auditor | 在用 | `~/.claude/skills/asset-auditor/` | 自建 | git | 含 references/；原名 skill-trimmer，2026-09-25 泛化改名——判定范围扩到原则文件映射表里的每一类资产，新增第 0 节资产类型映射表当唯一适配点；判据／扫描脚本／复审服务器未动；2026-09-26：按 writing-for-agents 收窄为库级留存、收窄、归档与新增审计，并保留只出建议边界；仍仅用户显式调用 |
| asset-guide | 在用 | `~/.claude/skills/asset-guide/` | 自建 | git | 含 references/；2026-09-25 新建；model-invocable（不加 `disable-model-invocation`），`description` 即常驻入口；正文八步流程，写作判据转 `/writing-for-agents`；2026-09-26：按 writing-for-agents 将八步流程收窄为资产变更前的类型、入口、元数据、索引与生命周期指针；2026-09-27：资产原则由 `rules/principles.md` 移入 `references/principles.md`（九条判据 + 本机正反例 + 边界 + 加载形态四格 + 映射表），并删去事后判据一条 |
| task-notes | 在用 | `~/.claude/skills/task-notes/`（触发面；正文在 `docs/protocols/task-notes/task-notes.md`） | 自建 | git | **保持模型可见**（SessionStart hook 按名调用它）；2026-09-26：按 writing-for-agents 前置跨会话接手、压缩与整理时的更新入口。2026-09-27：正文挪进 `docs/protocols/task-notes/task-notes.md`；本 Skill 只剩触发面与必读指针，名字与触发面未动 |

2026-09-25 逐条优化（token 线）：改动前逐份备份 `~/.claude/backups/skill-optimize-2026-09-25/<名>/SKILL.md`，21 份已逐字节校验。诊断与逐条结论见 `C:\ZYS\Workspace\notes\skill-hook-review\SKILL-REVIEW.md`。

（2026-09-30 曾给 4 份空壳补 `user-invocable: false` 以挡 `/` 菜单；这 4 份已于 2026-10-02 删除，该行随行删除留痕于流水。）

## 自建 agent（1 在用）

`agents/` 无忽略规则，真源随仓库追踪，不需要像 `skills/` 那样加白名单；子代理记忆落 `agent-memory/<name>/MEMORY.md`，已在 `.gitignore` 排除。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| dashboard-builder | 在用 | `~/.claude/agents/dashboard-builder.md` | 自建 | git | 2026-10-03 新建；只写 `.dashboard/` 与自身记忆；见流水 2026-10-03 |

## hook

`位置` 列的 `→ hooks.<事件>[<分组>]` 指 `settings.json` 里的注册位置。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| pretool-guard.py | 在用 | `hooks/scripts/pretool-guard.py` → `hooks.PreToolUse[0]` | 自建 | git | matcher `Bash\|EnterWorktree\|Write\|Edit\|MultiEdit`，timeout 45 |
| resource-guard.py | 在用 | `hooks/scripts/resource-guard.py` | 自建 | git | 由 pretool-guard.py 同进程加载，无独立注册 |
| product-guard.py | 在用 | `hooks/scripts/product-guard.py` | 自建 | git | 同上 |
| authorization_scope.py | 在用 | `hooks/scripts/authorization_scope.py` | 自建 | git | 授权范围唯一来源，被守卫导入 |
| context-budget-guard.py | 在用 | `hooks/scripts/context-budget-guard.py` → `hooks.PostToolUse[1]` | 自建 | git | timeout 10；2026-09-29 订正：实测挂在 `PostToolUse` 的 `.*` 组，原记 `hooks.UserPromptSubmit[0]` 不成立。同日修复**静默失效**：`emit()` 原为裸 `print()`，而裸 stdout 只在 `UserPromptSubmit`／`UserPromptExpansion`／`SessionStart`／`PostModelSwitch` 上注入，`PostToolUse` 只写调试日志——脚本一直在跑、判断一直对、输出一直丢。已改为 `hookSpecificOutput.additionalContext`，事件名从 payload 读（换接线位置不必改脚本）；测试 `hooks/tests/test_context_budget_guard.py`（原断言写的是「stdout 纯文本即注入内容」，正是那条把 bug 锁死的断言） |
| task-notes-reminder.py | 在用 | `hooks/scripts/task-notes-reminder.py` → `hooks.PreCompact[0]`、`hooks.SessionStart[1]` | 自建 | git | SessionStart 只挂 `compact` |
| session-guard.py | 在用 | `hooks/scripts/session-guard.py` → `hooks.SessionStart[0]`、`hooks.SessionEnd[0]` | 自建 | git | `start` / `end` 子命令 |
| session-status.py | 在用 | `hooks/scripts/session-status.py` | 自建 | git | 由 `/dev-status` 调用，非 hook |
| selftest.py | 在用 | `hooks/scripts/selftest.py` | 自建 | git | 自检入口，退出码 0 为全过 |
| protocol_check.py | 在用 | `hooks/scripts/protocol_check.py` | 自建 | git | 十一类判据（门禁／记忆／命名／体积／重复／密钥／生命周期／映射表／台账位置／顶层文档／指针）；`--file <路径>` 只查被写的那个文件（配 `--content <临时文件>` 改判「这次写完之后的样子」），`--only` 只跑某几类；只读、非 hook。退出码 0 全过／1 有命中／2 用法错误／3 有命中且在阻断区。**阻断面只此一处**：`BLOCK_SCOPE`（`CLAUDE.md`、`docs/protocols/*.md`、`docs/session-lifecycle.md`、`projects/*/memory/MEMORY.md`），按路径模式匹配。2026-10-02 实测修正：原记「十类」且名单缺「指针」、阻断面只记 2 个模式。同日新增两张豁免表，与判据上限同处一地：`SIZE_EXEMPT`（体量，`last30days/SKILL.md` 134.8 KB）与 `PARA_EXEMPT`（段落重复，按归一化原文逐字匹配，现有 1 条：`to-spec`／`to-tickets` 的入口引导句）。表内「复审」日期只是备注，代码不自动到期 |
| ledger_check.py | 在用 | `hooks/scripts/ledger_check.py` | 自建 | git | 2026-09-27 由 `skills/install-ledger/scripts/` 移入；只读、非 hook，检查台账列数与顺序、状态枚举、表内名称唯一、单表体量与 `archive/` 完整性 |
| protocol-report.py | 在用 | `hooks/scripts/protocol-report.py` → `hooks.PreToolUse[2]`、`hooks.PostToolUse[0]`、`hooks.Stop[1]` | 自建 | git | 资产判据的传输层：判据全在 protocol_check.py，本文件不含判据。PreToolUse 接阻断（检查器返 3 才拒，`deny` 形状照抄 product-guard.py，拒时留 `deny:` 日志）；PostToolUse 只报告；Stop 跑全量只读报告（本会话写过资产且命中与上次不同才出声） |
| protocol-router.py | 在用 | `hooks/scripts/protocol-router.py` → `hooks.PreToolUse[3]`、`hooks.UserPromptSubmit[1]` | 自建 | `git`（脚本）＋ `installing/settings-wiring.md`（接线；`settings.json` 与 `backups/` 都不进 git） | 按动作与领域把协议推到模型眼前：两张路由表（`UserPromptSubmit` 匹配用户输入的领域词，`PreToolUse` 匹配 tool_name + tool_input）。输出**必须**写成事实陈述句——官方警告命令式会触发提示注入防御、反被表面化。按 session 节流，上限 10 个会话。`PreToolUse` 的注入点在工具结果旁，对一次性高风险动作太晚，本脚本刻意不管。接线：`PreToolUse[3]` matcher `Bash\|PowerShell\|Edit\|Write\|MultiEdit\|NotebookEdit\|Agent\|Task`、timeout 10（`UserPromptSubmit` 不支持 matcher，故那组无 matcher）。2026-09-29 复核订正：matcher 原缺 `MultiEdit\|NotebookEdit`，与代码里 `EDIT_TOOLS` 不一致、那两条分支永不触发，已补齐。测试 `hooks/tests/test_protocol_router.py`（31 项）；备份 `backups/protocol-router-2026-09-29/`、`backups/protocol-router-matcher-2026-09-29/` |
| orca claude-hook.cmd | 在用 | `~/.orca/agent-hooks/claude-hook.cmd` → 12 个事件 | 待补 | 手工拷贝 | 不在 `~/.claude` 仓库内；2026-10-02 实测修正（原记 13） |
| rtk hook claude | 在用 | `settings.json → PreToolUse[4]`（matcher `Bash`，无 timeout） | rtk | 待补 | 2026-10-02 补记：此前无台账行。全局 Bash 拦截器，命令输出压缩层；第三方 CLI 不在 `~/.claude` 仓库内 |
| dashboard-scope-guard.py | 在用 | `hooks/scripts/dashboard-scope-guard.py` → `agents/dashboard-builder.md` 的 frontmatter `hooks.PreToolUse[0]` | 自建 | git | 不注册进 `settings.json`，只对 dashboard-builder 生效 |

## statusline

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| statusline.js | 在用 | `~/.claude/statusline/statusline.js` → `settings.json.statusLine` | 自建 | git | 入口 |
| magpie-usage.js | 在用 | `~/.claude/statusline/magpie-usage.js` | 自建 | git | 额度段数据源，同步读 `~/.config/magpie/quotas.json`（magpie 自己按秒轮询写），无缓存无子进程。2026-10-02 接替 `cc-switch-usage.js`，见流水同日 |
| lib/session-bridge.js | 在用 | `~/.claude/statusline/lib/session-bridge.js` | 自建 | git | 被 statusline.js require |

## 全局配置

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| CLAUDE.md | 在用 | `~/.claude/CLAUDE.md` | 自建 | git | 常驻指令，只放优先级裁决、门禁、索引三块；2026-09-25 拆出其余正文（183 行 / 14,306 B → 74 行 / 6,663 B，含 `asset-guide` 索引行），见流水；预算 7,000 字符；改动走确认线 |
| asset-guide/references/principles.md | 在用 | `~/.claude/skills/asset-guide/references/principles.md` | 自建 | git | 判据源；2026-09-27 由 `rules/principles.md` 移入（原是无 `paths` 的常驻规则，现随 `asset-guide` 按需加载）：九条原则 + 本机正反例 + 边界 + 加载形态四格 + 资产→形态→L0 映射表；`rules/` 目录已空 |
| settings.json | 在用 | `~/.claude/settings.json` | 自建 | **无 git 路径**（`.gitignore:54`） | 2026-10-01：cc-switch 卸载后不再有 common_config 双向同步（见流水 2026-10-01）。2026-09-29 订正仍有效：恢复列原写 `git` 实测不成立，改前须往 `backups/` 留副本。接线片段见 `installing/settings-wiring.md`。桌面 app 的推理网关另存 `AppData\Local\Claude-3p\configLibrary\`，不在本文件 |
| .gitignore skills 白名单 | 在用 | `~/.claude/.gitignore` | 自建 | git | 20 条 `!skills/<name>/` |
| session-hygiene.json | 在用 | `~/.claude/session-hygiene.json` | 自建 | git | 独占容器清单 |
| docs/protocols-index.md | 在用 | `~/.claude/docs/protocols-index.md` | 自建 | git | 协议总表；含「落点与命名」规约（原 `docs/protocols.md`）；2026-09-25 起是「删除判据」「触发点」两条维护条款的唯一来源，各协议正文只留分界 + 指针 |
| docs/protocols/gate/gate.md | 在用 | `~/.claude/docs/protocols/gate/gate.md` | 自建 | git | 门禁协议；操作规则仍在 `CLAUDE.md` §1.3 |
| docs/protocols/memory/memory.md | 在用 | `~/.claude/docs/protocols/memory/memory.md` | 自建 | git | 记忆协议；合并宿主格式说明与各项目 MEMORY.md 头部的约定 |
| docs/protocols/collaboration/collaboration.md | 在用 | `~/.claude/docs/protocols/collaboration/collaboration.md` | 自建 | git | 协作协议；原 `CLAUDE.md` §1.1／§1.4／§2.1／§2.3／§6／§7.2／§7.3 原文搬入 |
| docs/protocols/evidence/evidence.md | 在用 | `~/.claude/docs/protocols/evidence/evidence.md` | 自建 | git | 证据与交付协议；原 `CLAUDE.md` §3／§4 原文搬入 |
| docs/protocols/expression/expression.md | 在用 | `~/.claude/docs/protocols/expression/expression.md` | 自建 | git | 表达协议；原 `CLAUDE.md` §5 原文搬入 |
| docs/protocols/ledger/ledger.md | 在用 | `~/.claude/docs/protocols/ledger/ledger.md` | 自建 | git | 台账协议；2026-09-27 由 `skills/install-ledger/` 的 SKILL.md 正文 + 两份 `references/` 三合一并入；校验脚本另落 `hooks/scripts/ledger_check.py`；2026-10-02 新增第八节「真源在库外时的改动与回退」——`~/.claude/skills/` 43 项全为符号链接，真源的库不在 git 内，实测 18 项有 `~/.claude` 快照、25 项没有，回退走 `git show` 不走 `git checkout` |
| docs/protocols/task-notes/task-notes.md | 在用 | `~/.claude/docs/protocols/task-notes/task-notes.md` | 自建 | git | 任务笔记协议；2026-09-27 由 `skills/task-notes/SKILL.md` 正文挪入，skill 留触发面 |
| docs/protocols/execution-env/execution-env.md | 在用 | `~/.claude/docs/protocols/execution-env/execution-env.md` | 自建 | git | 执行环境协议；2026-09-27 由 `skills/docker-only/SKILL.md` 正文挪入，`new-project-setup.md` 落同目录子目录 `execution-env/` |
| docs/protocols/delegation/delegation.md | 在用 | `~/.claude/docs/protocols/delegation/delegation.md` | 自建 | git | 委派协议；2026-09-27 由 `skills/parallel-delegation/SKILL.md` 正文挪入，三份 `references/` 落同目录子目录 `delegation/` |
| docs/protocols/task-notes/dashboard.md | 在用 | `~/.claude/docs/protocols/task-notes/dashboard.md` | 自建 | git | 长任务进度看板协议；2026-10-03 新建于 `docs/protocols/dashboard/`，同日并入任务笔记协议作其视图层、移入 `task-notes/`，源仍是 `notes/<任务名>/STATE.md` |
| docs/protocols/instruction-assets/instruction-assets.md | 在用 | `~/.claude/docs/protocols/instruction-assets/instruction-assets.md` | 自建 | git | 指令资产协议；2026-09-27 合并 `skill-auditor` 与 `instruction-engineering` 两个 skill 的清单与模板，细则落同目录子目录 `instruction-assets/` |
| docs/session-lifecycle.md | 在用 | `~/.claude/docs/session-lifecycle.md` | 自建 | git | 会话启动、并发、收尾与工作树生命周期；由 `CLAUDE.md` §2 索引 |
| installing/ | 在用 | `~/.claude/installing/` | 自建 | git | 四张现状表 + `archive/` |
| docs/archive/ | 在用 | `~/.claude/docs/archive/` | 自建 | git | 4 份已废弃的时点产物，文件名 `<日期>-<主题>.md`，日期取内容反映的最新时点 |
| ~/.claude/statusline/ 目录名 | 在用 | `~/.claude/statusline/` | 自建 | git | 与空的 `hooks/statusline/` 不是一处 |
| ClaudeCode 托管设置 | 在用 | `C:\Program Files\ClaudeCode\managed-settings.json` | 自建 | **手工拷贝**（库外、需管理员；回退见流水 2026-10-03） | 机器级；含开 tool search 的 `env.ENABLE_TOOL_SEARCH`，**只对新会话生效**；见流水 2026-10-03 |

## 已归档

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
