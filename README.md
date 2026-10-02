# claude-stack

个人的 Claude Code 配置体系仓库（`~/.claude`）。统一管理 CLAUDE.md 全局指令、hooks、skills、statusline、commands，以及第三方 plugin marketplace；`external-configs/` 是 cc-switch 卸载前留下的非敏感快照留档。

## 目录结构

| 目录/文件 | 内容 |
|---|---|
| `CLAUDE.md` | 全局指令（给 AI 的规则） |
| `hooks/` | 会话生命周期守卫与工具链脚本（pretool-guard 合并入口、session-guard、product-guard、resource-guard、protocol-report、protocol-router） |
| `skills/` | `.gitignore` 白名单制，只追踪自建 skill。2026-10-02 实测：磁盘 43 项**全部为仓库内真实目录**（当日从 `~/.config/magpie/library/skills/` 的符号链接复制回来，该库不再充当真源）；git 追踪 23 个，其中 5 个已从磁盘删除、18 个在用。白名单与磁盘仍有错位，以 `installing/skill-install.md` 为准 |
| `statusline/` | 状态栏 JS（statusline.js、magpie-usage.js、`lib/session-bridge.js`） |
| `docs/` | 配置清单、盘点、迁移计划 |
| `external-configs/` | cc-switch 非敏感配置**快照副本**（复制非 symlink，同步见该目录 README） |
| `plugins/marketplaces/` | 第三方 plugin marketplace clone，**不进 git**（2026-08-11 解除追踪，约 97 MiB）；来源与安装方法见 `installing/tool-install.md` |
| `lib/` | lib 资源 |

## 不进 git（.gitignore）

- **运行时会话**：`projects/`、`sessions/`、`session-data/`、`cache/`、`metrics/`、`telemetry/`、`backups/`、`plans/`、`ide/` 等
- **本地配置/密钥**：`settings.json`、`settings.local.json`、`config.json`、`history.jsonl`、`.env`、`*.token`、`*.key`
- **usage-data**：`facets/`、`session-meta/`（运行时生成）
- **external-configs 的敏感源**：原为 `~/.cc-switch/cc-switch.db`、各 `auth.json`；cc-switch 已于 2026-10-01 卸载，敏感源不再同步，该目录现存的是卸载前留下的**非敏感快照副本**（只读留档，见 `external-configs/README.md`）

## 维护

- **改配置** → 走 CLAUDE.md §1 流程（确认线 + commit 前展示 stat）。
- **同步 external-configs** → 源变更后手动 `cp`，见 `external-configs/README.md`。
- **skills 的真源**就在 `~/.claude/skills/` 下，是仓库内的真实目录；本仓库按 `.gitignore` 白名单追踪自建 skill（第三方随插件走，不入 git）。真源不得放在仓库外——git 不跟随符号链接，2026-10-02 曾因此让自建 skill 静默失去版本备份，见 `docs/protocols/ledger/ledger.md` 第八节。

## 历史里程碑

- 2026-08-05：skills 纳入 git（cc-switch 软链接解析为实文件）+ 运行时清理 + external-configs 快照 + 3 个 gitlink 解析为实文件 + .gitignore 修复。
- 2026-08-11：全面审查整改——skill 按用户人工复核分流（31 自建入 git / 154 非自建入 installing 台账）；marketplace clone 与运行缓存解除追踪（-97 MiB）；忽略 `ide/`（含 authToken lock）。
