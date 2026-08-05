# external-configs

claude-stack 体系中外部的非敏感配置**快照副本**。实际位置在 `~/.claude` 之外，由各自工具管理（cc-switch、codex）。此处副本仅作版本化备份。

## 为什么是复制副本（2026-08-05 决策）

- **不用 symlink**：Windows 下 symlink 常失败（CLAUDE.md §9），git 追踪 symlink 在 Windows clone 出来也失效。
- **不给 `~/.cc-switch` 建独立 git**：cc-switch 含 25M 数据库 + 68M repos + 认证凭据，整体版本化代价大；且 cc-switch 自带 `cc-switch-setting-sync` skill 可能已有同步机制。
- **选复制副本进 `~/.claude`**：总仓库保留体系全貌，轻量可立即做。代价是**脱节**（见下）。

## 来源与同步

| 文件 | 源路径 |
|---|---|
| cc-switch-settings.json | `~/.cc-switch/settings.json` |
| cc-switch-model-pricing.json | `~/.cc-switch/model-pricing.json` |
| codex-model-catalog.json | `~/.codex/cc-switch-model-catalog.json` |
| BACKUP_BEFORE_CHANGE.md | `~/.cc-switch/BACKUP_BEFORE_CHANGE.md` |
| RESTORE_SYMLINKS.md | `~/.cc-switch/RESTORE_SYMLINKS.md` |

源文件变更后，跑以下命令覆盖副本并 commit：

```bash
cp ~/.cc-switch/settings.json            ~/.claude/external-configs/cc-switch-settings.json
cp ~/.cc-switch/model-pricing.json       ~/.claude/external-configs/cc-switch-model-pricing.json
cp ~/.codex/cc-switch-model-catalog.json ~/.claude/external-configs/codex-model-catalog.json
cp ~/.cc-switch/BACKUP_BEFORE_CHANGE.md  ~/.claude/external-configs/
cp ~/.cc-switch/RESTORE_SYMLINKS.md      ~/.claude/external-configs/
```

## 脱节风险（重要）

**源文件是真相源，副本是快照。** cc-switch/codex 运行时会更新源（如 settings.json 切换 provider），副本不会自动跟随。已知 `cc-switch-settings.json` 副本与源曾有 9 字节差异（源被运行时改过）。需要最新值时以源为准或重新 cp。

## 不纳入此处（敏感 / 运行时 / 大 / 重复）

| 类别 | 内容 | 原因 |
|---|---|---|
| 敏感 | `~/.claude.json` | 含 OAuth 令牌与 API 凭据 |
| 敏感 | `~/.codex/config.toml`、`auth.json` | 含认证令牌 |
| 敏感 | `~/.cc-switch/codex_oauth_auth.json`、`copilot_auth.json` | 认证凭据 |
| 敏感+大 | `~/.cc-switch/cc-switch.db`（25M） | SQLite，含 provider 凭据 |
| 运行时 | `~/.codex/*.sqlite`（memories/goals/logs/state） | 数据库 |
| 运行时 | `~/.codex/sessions/`、`cache/`、`tmp/`、`archived_sessions/` | 会话/缓存 |
| 大+重复 | `~/.cc-switch/repos/`（68M） | git clone 源仓库 |
| 重复 | `~/.cc-switch/skills/`（225） | 与 `.claude/skills/` 重复 |
| 待确认 | `~/.cc-switch/sync-backup-*.json` | 可能含敏感快照 |

## 创建历史

- **2026-08-05**：创建。作为 claude-stack 仓库整理的一部分（skills 纳入 git + 运行时清理 + .gitignore 修复），把 cc-switch/codex 的非敏感配置快照纳入总仓库。同期 commit：`chore: add external-configs snapshots, fix .gitignore over-exclusion`。
