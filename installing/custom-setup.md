# 自建设施台账（非外部安装，自己造的）

记录自建 skill / hook / statusline / 全局配置的当前位置与迁移要点。外部装的见 [skill-install.md](skill-install.md)、[tool-install.md](tool-install.md)、[mcp-install.md](mcp-install.md)。

自建资产迁移原则：**git 仓库应追踪全部自建 skill**（新增自建 skill 必须在 `.gitignore` 的 skills/ 白名单登记）；`git clone` 即迁；memory 目录（`projects/*/memory/`）需单独拷贝（git 未追踪）。第三方/插件 skill 不在 git，靠另三本台账记录的地址与命令重装。

历史变更在 [archive/custom-setup.md](archive/custom-setup.md)，默认不读。

## 自建 skill（21）

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| ai-product-development | 在用 | `~/.claude/skills/ai-product-development/` | 自建 | git | — |
| article-writer | 在用 | `~/.claude/skills/article-writer/` | 自建 | git | 含 examples/ |
| auto-browser | 在用 | `~/.claude/skills/auto-browser/` | 自建 | git | 2026-09-24 自建合并 |
| awesome-design-md | 在用 | `~/.claude/skills/awesome-design-md/` | 自建 | git | — |
| bidirectional-steelman | 在用 | `~/.claude/skills/bidirectional-steelman/` | 自建 | git | — |
| cc-switch-setting-sync | 在用 | `~/.claude/skills/cc-switch-setting-sync/` | 自建 | git | 含 scripts/sync_claude_common.py |
| coding-workflow | 在用 | `~/.claude/skills/coding-workflow/` | 自建 | git | 含 references/；2026-09-25 加 `disable-model-invocation: true` |
| content-to-note | 在用 | `~/.claude/skills/content-to-note/` | 自建 | git | 2026-09-20 起仅手动调用 |
| dev-clean | 在用 | `~/.claude/skills/dev-clean/` | 自建 | git | 由 `commands/dev-clean.md` 迁入 |
| dev-status | 在用 | `~/.claude/skills/dev-status/` | 自建 | git | 由 `commands/dev-status.md` 迁入 |
| docker-only | 在用 | `~/.claude/skills/docker-only/` | 自建 | git | 含 references/；2026-09-25 加 `disable-model-invocation: true` |
| drawio-chart | 在用 | `~/.claude/skills/drawio-chart/` | 自建 | git | 含 examples/ |
| improver-skill | 在用 | `~/.claude/skills/improver-skill/` | 自建 | git | 原名 wiki-skill |
| install-ledger | 在用 | `~/.claude/skills/install-ledger/` | 自建 | git | 含 references/、scripts/；2026-09-25 加 `disable-model-invocation: true` |
| instruction-engineering | 在用 | `~/.claude/skills/instruction-engineering/` | 自建 | git | — |
| leader | 在用 | `~/.claude/skills/leader/` | 自建 | git | 2026-09-24 补进 `.gitignore` 白名单，此前一直被忽略 |
| local-env-pitfalls | 在用 | `~/.claude/skills/local-env-pitfalls/` | 自建 | git | 含 references/；2026-09-25 加 `disable-model-invocation: true` |
| parallel-delegation | 在用 | `~/.claude/skills/parallel-delegation/` | 自建 | git | 2026-09-25 加 `disable-model-invocation: true` |
| skill-auditor | 在用 | `~/.claude/skills/skill-auditor/` | 自建 | git | — |
| skill-trimmer | 在用 | `~/.claude/skills/skill-trimmer/` | 自建 | git | 含 references/ |
| task-notes | 在用 | `~/.claude/skills/task-notes/` | 自建 | git | 含 references/；**保持模型可见**（SessionStart hook 按名调用它） |

2026-09-25 逐条优化（token 线）：改动前逐份备份 `~/.claude/backups/skill-optimize-20260925/<名>/SKILL.md`，21 份已逐字节校验。诊断与逐条结论见 `C:\ZYS\Code\lab-area\notes\skill-hook-review\SKILL-REVIEW.md`。

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
| protocol_check.py | 在用 | `hooks/scripts/protocol_check.py` | 自建 | git | 校验门禁与记忆两份协议；源路径已删的项目的记忆只计数不细查；只读、非 hook，退出码 0 为全过 |
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
| context-monitor.js | 停用 | `~/.claude/statusline/context-monitor.js` | 自建 | git | ecc 时代产物，无引用方、无注册 |
| cost-tracker.js | 停用 | `~/.claude/statusline/cost-tracker.js` | 自建 | git | 同上 |
| metrics-bridge.js | 停用 | `~/.claude/statusline/metrics-bridge.js` | 自建 | git | 同上 |
| lib/utils.js | 停用 | `~/.claude/statusline/lib/utils.js` | 自建 | git | 仅被上面三个停用脚本 require |
| lib/agent-data-home.js | 停用 | `~/.claude/statusline/lib/agent-data-home.js` | 自建 | git | 同上 |

## 全局配置

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| CLAUDE.md | 在用 | `~/.claude/CLAUDE.md` | 自建 | git | 常驻指令；字符预算 7,000，超即复核删减；改动走确认线 |
| settings.json | 在用 | `~/.claude/settings.json` | 自建 | git | 与 cc-switch common_config 双向同步 |
| .gitignore skills 白名单 | 在用 | `~/.claude/.gitignore` | 自建 | git | 20 条 `!skills/<name>/` |
| session-hygiene.json | 在用 | `~/.claude/session-hygiene.json` | 自建 | git | 独占容器清单 |
| docs/protocols.md | 在用 | `~/.claude/docs/protocols.md` | 自建 | git | 协议总表 |
| docs/protocols/gate.md | 在用 | `~/.claude/docs/protocols/gate.md` | 自建 | git | 门禁协议；操作规则仍在 `CLAUDE.md` §1.3 |
| docs/protocols/memory.md | 在用 | `~/.claude/docs/protocols/memory.md` | 自建 | git | 记忆协议；合并宿主格式说明与各项目 MEMORY.md 头部的约定 |
| installing/ | 在用 | `~/.claude/installing/` | 自建 | git | 四张现状表 + `archive/` |
| ~/.claude/statusline/ 目录名 | 在用 | `~/.claude/statusline/` | 自建 | git | 与空的 `hooks/statusline/` 不是一处 |

## 已归档

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| company-discovery-evaluation-by-user | 已归档 | `~/.claude/archive-skills/company-discovery-evaluation-by-user/` | 自建 | git | — |
