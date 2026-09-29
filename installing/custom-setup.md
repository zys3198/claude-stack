# 自建设施台账（非外部安装，自己造的）

记录自建 skill / hook / statusline / 全局配置的当前位置与迁移要点。外部装的见 [skill-install.md](skill-install.md)、[tool-install.md](tool-install.md)、[mcp-install.md](mcp-install.md)。

自建资产迁移原则：**git 仓库应追踪全部自建 skill**（新增自建 skill 必须在 `.gitignore` 的 skills/ 白名单登记）；`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠另三本台账记录的地址与命令重装。

历史变更在 [archive/custom-setup.md](archive/custom-setup.md)，默认不读。

## 自建 skill（19 在用 + 4 归档）

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| ai-product-development | 已归档 | `~/.claude/skills/ai-product-development/`（触发空壳） | 自建 | `backups/ai-product-development-removal-2026-09-27/` | 2026-09-27：移除-被覆盖——路线 100% 指向 `mattpocock-skills`，`ask-matt` 已完整覆盖；独有增量并进 `coding-workflow` §1.5.1／§1.5.2。观察截止 2026-11-26 |
| article-writer | 在用 | `~/.claude/skills/article-writer/` | 自建 | git | 含 examples/；2026-09-26：按 writing-for-agents 收窄为单篇中文技术内容的创作与深度改写入口；仍仅用户显式调用 |
| auto-browser | 在用 | `~/.claude/skills/auto-browser/` | 自建 | git | 2026-09-24 自建合并；2026-09-26：按 writing-for-agents 前置网页操作、抓取与验收入口，并保留两条浏览器路线 |
| awesome-design-md | 在用 | `~/.claude/skills/awesome-design-md/` | 自建 | git | 2026-09-26：触发描述补齐视觉约束与网页实现两种入口；保持本地资料来源边界 |
| bidirectional-steelman | 在用 | `~/.claude/skills/bidirectional-steelman/` | 自建 | git | 2026-09-26：按 writing-for-agents 收窄为方案取舍、技术选型与「怎么办」的论证入口；仍仅用户显式调用 |
| cc-switch-setting-sync | 在用 | `~/.claude/skills/cc-switch-setting-sync/` | 自建 | git | 含 scripts/sync_claude_common.py；2026-09-26：按 writing-for-agents 保留同步、restore 与四层 repair 入口；repair 一次对齐 live/common/proxy/provider，6 个稳定行为键改由 Windows 用户环境唯一提供，脚本同步时剔除并要求 repair 后重启 cc-switch；仍仅用户显式调用 |
| coding-workflow | 在用 | `~/.claude/skills/coding-workflow/` | 自建 | git | 含 references/；2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 收窄为代码改动、审查与回退入口；恢复模型可调用；2026-09-27：1.9.0 去除与 `docker-only`、`parallel-delegation`、`mattpocock-skills:code-review` 的重复规程，保留编码特有门禁 |
| content-to-note | 在用 | `~/.claude/skills/content-to-note/` | 自建 | git | 2026-09-20 起仅手动调用；2026-09-26：按 writing-for-agents 保留三类来源与学习型笔记目标；仍仅用户显式调用 |
| dev-clean | 在用 | `~/.claude/skills/dev-clean/` | 自建 | git | 由 `commands/dev-clean.md` 迁入；2026-09-26：触发描述收窄为用户明确项目收尾，并保留资源删除／停止与 push 门禁 |
| dev-status | 在用 | `~/.claude/skills/dev-status/` | 自建 | git | 由 `commands/dev-status.md` 迁入；2026-09-26：触发描述改为查看仓库状态并原样返回脚本输出 |
| docker-only | 在用 | `~/.claude/skills/docker-only/`（触发面；正文在 `docs/protocols/execution-env.md`） | 自建 | git | 2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：触发描述前置运行动作、受限容器流程与宿主边界；恢复模型可调用。2026-09-27：正文挪进 `docs/protocols/execution-env.md`，`references/new-project-setup.md` 移到 `docs/protocols/execution-env/`；本 Skill 只剩触发面与必读指针，仍 model-invocable |
| drawio-chart | 在用 | `~/.claude/skills/drawio-chart/` | 自建 | git | 含 examples/ |
| improver-skill | 在用 | `~/.claude/skills/improver-skill/` | 自建 | git | 原名 wiki-skill；2026-09-26：按 writing-for-agents 明确 Trace、Pattern、候选 Skill 与 gate 四个入口；仍仅用户显式调用 |
| install-ledger | 已归档 | `~/.claude/skills/install-ledger/`（触发空壳） | 自建 | git | 2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 明确资产变更后的登记核对入口，并保留只写台账边界。2026-09-27：正文与两份 `references/` 三合一进 `docs/protocols/ledger.md`，`scripts/ledger_check.py` 移到 `hooks/scripts/`；已加 `disable-model-invocation: true`，触发面不再占 listing。观察截止 2026-11-26 |
| instruction-engineering | 已归档 | `~/.claude/skills/instruction-engineering/`（触发空壳） | 自建 | git | 2026-09-26：按 writing-for-agents 明确建立项目上下文与审查指令资产两条入口。2026-09-27：正文并入 `docs/protocols/instruction-assets.md`，`references/` 移到 `docs/protocols/instruction-assets/`；已加 `disable-model-invocation: true`，触发面不再占 listing。观察截止 2026-11-26 |
| leader | 在用 | `~/.claude/skills/leader/` | 自建 | git | 2026-09-24 补进 `.gitignore` 白名单，此前一直被忽略；2026-09-26：按 writing-for-agents 明确调研、独立执行与验收任务书入口；仍仅用户显式调用 |
| last30days | 在用 | `~/.claude/skills/last30days/` | 本地化，上游已切断 | git | v3.25.0；原第三方裸 skill 已本地化，`disable-model-invocation: true`，按 `/last30days` 手动调用；含 `references/` 与 `scripts/`，跳过上游 `assets/`。**2026-09-29 纳入 git 复核**：`.gitignore:131` 白名单虽已加，但从未 `git add`——135 文件 / 2.85 MB 一直是 untracked，本列写 `git` 的恢复路径**当时不成立**，提交 `b92a9d5` 后才成立。同日「轻量化」勘察：`references/` 分层**已完成**（8 份 127 KB，主文件各 Step 0.x 章只剩指针），剩余 143,486 B 是必须常驻的契约带（文内 `:87`/`:179` 记着规则移出前部后连续失败的实例），可移量仅约 4%；故只把 `## WHEN USER RESPONDS` 主体移入 `references/followup.md` 留指针，143,486 → 137,989 B，字节完全对账。保留 `CONTEXT MEMORY`、`## Output Summary Footer`、`Security & Permissions`（ht-ml.app 发布门禁）。备份 `backups/skill-last30days-slim-2026-09-29/` |
| local-env-pitfalls | 在用 | `~/.claude/skills/local-env-pitfalls/` | 自建 | git | 含 references/；2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 前置脚本、命令与子代理执行前的坑位查询入口；恢复模型可调用 |
| parallel-delegation | 在用 | `~/.claude/skills/parallel-delegation/`（触发面；正文在 `docs/protocols/delegation.md`） | 自建 | git | 2026-09-25 曾加 `disable-model-invocation: true`；2026-09-26：按 writing-for-agents 明确单个／并行委派及配置确认门禁；恢复模型可调用。2026-09-27：正文挪进 `docs/protocols/delegation.md`，三份 `references/` 移到 `docs/protocols/delegation/`；本 Skill 只剩触发面与必读指针，仍 model-invocable |
| skill-auditor | 已归档 | `~/.claude/skills/skill-auditor/`（触发空壳） | 自建 | git | 2026-09-26：按 writing-for-agents 扩展为单 Skill 审计、减量、组合边界与来源重复审查。2026-09-27：审计清单与三份设计方法合并进 `docs/protocols/instruction-assets.md`；已加 `disable-model-invocation: true`，触发面不再占 listing。观察截止 2026-11-26 |
| asset-auditor | 在用 | `~/.claude/skills/asset-auditor/` | 自建 | git | 含 references/；原名 skill-trimmer，2026-09-25 泛化改名——判定范围扩到原则文件映射表里的每一类资产，新增第 0 节资产类型映射表当唯一适配点；判据／扫描脚本／复审服务器未动；2026-09-26：按 writing-for-agents 收窄为库级留存、收窄、归档与新增审计，并保留只出建议边界；仍仅用户显式调用 |
| asset-guide | 在用 | `~/.claude/skills/asset-guide/` | 自建 | git | 含 references/；2026-09-25 新建；model-invocable（不加 `disable-model-invocation`），`description` 即常驻入口；正文八步流程，写作判据转 `/writing-for-agents`；2026-09-26：按 writing-for-agents 将八步流程收窄为资产变更前的类型、入口、元数据、索引与生命周期指针；2026-09-27：资产原则由 `rules/principles.md` 移入 `references/principles.md`（九条判据 + 本机正反例 + 边界 + 加载形态四格 + 映射表），并删去事后判据一条 |
| task-notes | 在用 | `~/.claude/skills/task-notes/`（触发面；正文在 `docs/protocols/task-notes.md`） | 自建 | git | **保持模型可见**（SessionStart hook 按名调用它）；2026-09-26：按 writing-for-agents 前置跨会话接手、压缩与整理时的更新入口。2026-09-27：正文挪进 `docs/protocols/task-notes.md`；本 Skill 只剩触发面与必读指针，名字与触发面未动 |

2026-09-25 逐条优化（token 线）：改动前逐份备份 `~/.claude/backups/skill-optimize-2026-09-25/<名>/SKILL.md`，21 份已逐字节校验。诊断与逐条结论见 `C:\ZYS\Workspace\notes\skill-hook-review\SKILL-REVIEW.md`。

## hook

`位置` 列的 `→ hooks.<事件>[<分组>]` 指 `settings.json` 里的注册位置。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| pretool-guard.py | 在用 | `hooks/scripts/pretool-guard.py` → `hooks.PreToolUse[0]` | 自建 | git | matcher `Bash\|EnterWorktree\|Write\|Edit\|MultiEdit`，timeout 45 |
| resource-guard.py | 在用 | `hooks/scripts/resource-guard.py` | 自建 | git | 由 pretool-guard.py 同进程加载，无独立注册 |
| product-guard.py | 在用 | `hooks/scripts/product-guard.py` | 自建 | git | 同上 |
| authorization_scope.py | 在用 | `hooks/scripts/authorization_scope.py` | 自建 | git | 授权范围唯一来源，被守卫导入 |
| context-budget-guard.py | 在用 | `hooks/scripts/context-budget-guard.py` → `hooks.UserPromptSubmit[0]` | 自建 | git | timeout 10 |
| task-notes-reminder.py | 在用 | `hooks/scripts/task-notes-reminder.py` → `hooks.PreCompact[0]`、`hooks.SessionStart[2]` | 自建 | git | SessionStart 只挂 `compact` |
| session-guard.py | 在用 | `hooks/scripts/session-guard.py` → `hooks.SessionStart[1]`、`hooks.SessionEnd[0]` | 自建 | git | `start` / `end` 子命令 |
| session-status.py | 在用 | `hooks/scripts/session-status.py` | 自建 | git | 由 `/dev-status` 调用，非 hook |
| selftest.py | 在用 | `hooks/scripts/selftest.py` | 自建 | git | 自检入口，退出码 0 为全过 |
| protocol_check.py | 在用 | `hooks/scripts/protocol_check.py` | 自建 | git | 十类判据（门禁／记忆／命名／体积／重复／密钥／生命周期／映射表／台账位置／顶层文档）；`--file <路径>` 只查被写的那个文件（配 `--content <临时文件>` 改判「这次写完之后的样子」），`--only` 只跑某几类；只读、非 hook。退出码 0 全过／1 有命中／2 用法错误／3 有命中且在阻断区。**阻断面只此一处**：`BLOCK_SCOPE`（`CLAUDE.md`、`projects/*/memory/MEMORY.md`），按路径模式匹配 |
| ledger_check.py | 在用 | `hooks/scripts/ledger_check.py` | 自建 | git | 2026-09-27 由 `skills/install-ledger/scripts/` 移入；只读、非 hook，检查台账列数与顺序、状态枚举、表内名称唯一、单表体量与 `archive/` 完整性 |
| protocol-report.py | 在用 | `hooks/scripts/protocol-report.py` → `hooks.PreToolUse[2]`、`hooks.PostToolUse[0]`、`hooks.Stop[0]` | 自建 | git | 资产判据的传输层：判据全在 protocol_check.py，本文件不含判据。PreToolUse 接阻断（检查器返 3 才拒，`deny` 形状照抄 product-guard.py，拒时留 `deny:` 日志）；PostToolUse 只报告；Stop 跑全量只读报告（本会话写过资产且命中与上次不同才出声） |
| settings-degrade-guard.py | 在用 | `hooks/settings-degrade-guard.py` → `hooks.SessionStart[0]` | 自建 | git | matcher `.*`，未设 timeout |
| settings-sync-auto.py | 在用 | `hooks/settings-sync-auto.py` → `hooks.PostToolUse[0]` | 自建 | git | 只挂 Edit\|Write 类；CLI 改 settings.json 不触发 |
| claude-notify.ps1 | 在用 | `hooks/claude-notify.ps1` → `hooks.Notification[0]`、`hooks.StopFailure[0]` | 自建 | git | 不挂 PostToolUseFailure，避免工具失败噪声 |
| herdr-agent-state.ps1 | 停用 | `hooks/herdr-agent-state.ps1` | herdr | 手工拷贝 | 2026-09-24 摘除 SessionStart 注册：`HERDR_ENV` 未设即 `exit 0`，实测 Herdr 已不在本机，每次会话白起进程。文件归 herdr 管，重装会覆盖 |
| orca claude-hook.cmd | 在用 | `~/.orca/agent-hooks/claude-hook.cmd` → 13 个事件 | 待补 | 手工拷贝 | 不在 `~/.claude` 仓库内 |
| test_install_ledger_reminder.py | 停用 | `hooks/tests/test_install_ledger_reminder.py` | 自建 | git | **孤立**：无对应脚本、无注册 |

## statusline

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| statusline.js | 在用 | `~/.claude/statusline/statusline.js` → `settings.json.statusLine` | 自建 | git | 入口 |
| cc-switch-usage.js | 在用 | `~/.claude/statusline/cc-switch-usage.js` | 自建 | git | 被 statusline.js require，额度数据源 |
| lib/session-bridge.js | 在用 | `~/.claude/statusline/lib/session-bridge.js` | 自建 | git | 被 statusline.js require |

## 全局配置

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| CLAUDE.md | 在用 | `~/.claude/CLAUDE.md` | 自建 | git | 常驻指令，只放优先级裁决、门禁、索引三块；2026-09-25 拆出其余正文（183 行 / 14,306 B → 74 行 / 6,663 B，含 `asset-guide` 索引行），见流水；预算 7,000 字符；改动走确认线 |
| asset-guide/references/principles.md | 在用 | `~/.claude/skills/asset-guide/references/principles.md` | 自建 | git | 判据源；2026-09-27 由 `rules/principles.md` 移入（原是无 `paths` 的常驻规则，现随 `asset-guide` 按需加载）：九条原则 + 本机正反例 + 边界 + 加载形态四格 + 资产→形态→L0 映射表；`rules/` 目录已空 |
| settings.json | 在用 | `~/.claude/settings.json` | 自建 | git | 与 cc-switch common_config 双向同步 |
| .gitignore skills 白名单 | 在用 | `~/.claude/.gitignore` | 自建 | git | 20 条 `!skills/<name>/` |
| session-hygiene.json | 在用 | `~/.claude/session-hygiene.json` | 自建 | git | 独占容器清单 |
| docs/protocols-index.md | 在用 | `~/.claude/docs/protocols-index.md` | 自建 | git | 协议总表；含「落点与命名」规约（原 `docs/protocols.md`）；2026-09-25 起是「删除判据」「触发点」两条维护条款的唯一来源，各协议正文只留分界 + 指针 |
| docs/protocols/gate.md | 在用 | `~/.claude/docs/protocols/gate.md` | 自建 | git | 门禁协议；操作规则仍在 `CLAUDE.md` §1.3 |
| docs/protocols/memory.md | 在用 | `~/.claude/docs/protocols/memory.md` | 自建 | git | 记忆协议；合并宿主格式说明与各项目 MEMORY.md 头部的约定 |
| docs/protocols/collaboration.md | 在用 | `~/.claude/docs/protocols/collaboration.md` | 自建 | git | 协作协议；原 `CLAUDE.md` §1.1／§1.4／§2.1／§2.3／§6／§7.2／§7.3 原文搬入 |
| docs/protocols/evidence.md | 在用 | `~/.claude/docs/protocols/evidence.md` | 自建 | git | 证据与交付协议；原 `CLAUDE.md` §3／§4 原文搬入 |
| docs/protocols/expression.md | 在用 | `~/.claude/docs/protocols/expression.md` | 自建 | git | 表达协议；原 `CLAUDE.md` §5 原文搬入 |
| docs/protocols/ledger.md | 在用 | `~/.claude/docs/protocols/ledger.md` | 自建 | git | 台账协议；2026-09-27 由 `skills/install-ledger/` 的 SKILL.md 正文 + 两份 `references/` 三合一并入；校验脚本另落 `hooks/scripts/ledger_check.py` |
| docs/protocols/task-notes.md | 在用 | `~/.claude/docs/protocols/task-notes.md` | 自建 | git | 任务笔记协议；2026-09-27 由 `skills/task-notes/SKILL.md` 正文挪入，skill 留触发面 |
| docs/protocols/execution-env.md | 在用 | `~/.claude/docs/protocols/execution-env.md` | 自建 | git | 执行环境协议；2026-09-27 由 `skills/docker-only/SKILL.md` 正文挪入，`new-project-setup.md` 落同目录子目录 `execution-env/` |
| docs/protocols/delegation.md | 在用 | `~/.claude/docs/protocols/delegation.md` | 自建 | git | 委派协议；2026-09-27 由 `skills/parallel-delegation/SKILL.md` 正文挪入，三份 `references/` 落同目录子目录 `delegation/` |
| docs/protocols/instruction-assets.md | 在用 | `~/.claude/docs/protocols/instruction-assets.md` | 自建 | git | 指令资产协议；2026-09-27 合并 `skill-auditor` 与 `instruction-engineering` 两个 skill 的清单与模板，细则落同目录子目录 `instruction-assets/` |
| docs/session-lifecycle.md | 在用 | `~/.claude/docs/session-lifecycle.md` | 自建 | git | 会话启动、并发、收尾与工作树生命周期；由 `CLAUDE.md` §2 索引 |
| installing/ | 在用 | `~/.claude/installing/` | 自建 | git | 四张现状表 + `archive/` |
| docs/archive/ | 在用 | `~/.claude/docs/archive/` | 自建 | git | 4 份已废弃的时点产物，文件名 `<日期>-<主题>.md`，日期取内容反映的最新时点 |
| codex-home-2026-09-09 | 已归档 | `~/.claude/backups/codex-home-2026-09-09/` | 自建（快照） | **无 git 路径** | Codex home 快照，90 文件 / 3,400,308 B；`~/.codex/` 已不存在，**这是唯一副本**；`backups/` 在 `.gitignore` 内，只有一份 |
| ~/.claude/statusline/ 目录名 | 在用 | `~/.claude/statusline/` | 自建 | git | 与空的 `hooks/statusline/` 不是一处 |

## 已归档

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| company-discovery-evaluation-by-user | 已归档 | `~/.claude/archive-skills/company-discovery-evaluation-by-user/` | 自建 | git | — |
