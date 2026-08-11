# claude-stack

个人的 Claude Code 配置体系仓库（`~/.claude`）。统一管理 CLAUDE.md 全局指令、hooks、agents、skills、statusline、cc-switch 配置快照，以及第三方 plugin marketplace。

## 目录结构

| 目录/文件 | 内容 |
|---|---|
| `CLAUDE.md` | 全局指令（给 AI 的规则） |
| `agents/` | 自定义 agent 定义（design/engineering/security/testing） |
| `hooks/` | 拦截/守卫 hook（verify_gate、git_guard、secret_guard、placeholder_guard 等） |
| `skills/` | 只追踪自建 skill（`.gitignore` 白名单制，31 个，2026-08-11 用户人工复核定稿）；第三方 skill 不进 git，来源登记在 `installing/skill-install.md` |
| `statusline/` | 状态栏 JS（statusline.js、cost-tracker、context-monitor、metrics-bridge） |
| `docs/` | 配置清单、盘点、迁移计划 |
| `external-configs/` | cc-switch 非敏感配置**快照副本**（复制非 symlink，同步见该目录 README） |
| `plugins/marketplaces/` | 第三方 plugin marketplace clone，**不进 git**（2026-08-11 解除追踪，约 97 MiB）；来源与安装方法见 `installing/tool-install.md` |
| `lib/` | lib 资源 |

## 不进 git（.gitignore）

- **运行时会话**：`projects/`、`sessions/`、`session-data/`、`cache/`、`metrics/`、`telemetry/`、`backups/`、`plans/`、`ide/` 等
- **本地配置/密钥**：`settings.json`、`settings.local.json`、`config.json`、`history.jsonl`、`.env`、`*.token`、`*.key`
- **usage-data**：`facets/`、`session-meta/`（运行时生成）
- **external-configs 的敏感源**：`~/.cc-switch/cc-switch.db`、各 `auth.json`、`~/.claude.json` 等（见 `external-configs/README.md`）

## 维护

- **改配置** → 走 CLAUDE.md §1 流程（确认线 + commit 前展示 stat）。
- **同步 external-configs** → 源变更后手动 `cp`，见 `external-configs/README.md`。
- **cc-switch 的 skills 源**在 `~/.cc-switch/skills/`；本仓库 `skills/` 是解析后的实文件副本，两者不再自动同步。

## 历史里程碑

- 2026-08-05：skills 纳入 git（cc-switch 软链接解析为实文件）+ 运行时清理 + external-configs 快照 + 3 个 gitlink 解析为实文件 + .gitignore 修复。
- 2026-08-11：全面审查整改——skill 按用户人工复核分流（31 自建入 git / 154 非自建入 installing 台账）；marketplace clone 与运行缓存解除追踪（-97 MiB）；忽略 `ide/`（含 authToken lock）。
