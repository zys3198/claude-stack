# ccswitch Claude settings.json 同步机制

## 问题
ccswitch（com.ccswitch.desktop）切换或热切换 provider 时，会把组装好的完整 JSON
整体写回 `~/.claude/settings.json`。组装方式：

```
settings.json = claude provider 的 settings_config  (provider 片段)
              + settings.common_config_claude       (公共片段)
```

DB 里 `common_config_claude` 若过时（缺了用户手动加的 enabledPlugins /
hooks / permissions / statusLine 段等），每次切换都会把 settings.json 降级。

## 关键表与字段

数据库：`~/.cc-switch/cc-switch.db`（SQLite，WAL 模式）

- `settings(key, value)`：`key='common_config_claude'` 存公共配置（纯 JSON 文本）。
  同步目标就是这个 value。
- `providers(id, app_type, name, settings_config, is_current)`：每个 provider 一行。
  `app_type='claude'` + `is_current=1` 是当前激活的 claude provider。
  `settings_config` 是 JSON，顶层含 `env`、`model`、`enabledPlugins`、`hooks`、
  `permissions`、`statusLine`、`effortLevel` 等（provider 片段与公共字段混在一起）。
- `proxy_live_backup(app_type, original_config)`：热切换时抓的快照（JSON）。
- `proxy_config`：代理端口、超时等。

## 什么是 provider 片段（不进 common）

这些由 ccswitch 在切换时从 provider 模板注入，绝不放进 `common_config_claude`：

- 顶层 `model`
- `env` 内的 `ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、
  `ANTHROPIC_DEFAULT_*_MODEL[_NAME]` 整组

代理开启时，`ANTHROPIC_BASE_URL` 会在运行时被改写成 `http://127.0.0.1:15721`，
`ANTHROPIC_AUTH_TOKEN` 改成 `PROXY_MANAGED`——这是运行时行为，由 ccswitch 控制。

## 什么是公共配置（进 common）

provider 无关的全部配置，例如：

```json
{
  "attribution": {"commit": "", "pr": ""},
  "effortLevel": "high",
  "includeCoAuthoredBy": false,
  "enabledPlugins": {"mattpocock-skills@mattpocock": true},
  "extraKnownMarketplaces": {...},
  "hooks": {"PostToolUse": [...], "PreToolUse": [...]},
  "permissions": {"allow": [...]},
  "statusLine": {...},
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "ENABLE_TOOL_SEARCH": "true"
  }
}
```

注意 `env` 是混合字段：`ANTHROPIC_*` 是 provider 相关（剔除）；其余通常是公共配置。以下 5 个稳定键由 Windows 用户环境提供，不应残留在 live/common/proxy/provider 快照：`CLAUDE_CODE_DISABLE_ARTIFACT`、`CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`、`DISABLE_AUTOUPDATER`、`DISABLE_ERROR_REPORTING`、`DISABLE_TELEMETRY`。`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 不进入 common/proxy；Codex OAuth provider 的 `settings_config.env` 必须保留显式目标值，以覆盖 cc-switch 对 GPT-5.6 的 372000 默认值。`CLAUDE_CODE_EFFORT_LEVEL`、`CLAUDE_CODE_MAX_CONTEXT_TOKENS` 仍视为 provider 覆盖风险，也不允许进入公共快照。

repair 模式还会把 live、`settings.common_config_claude` 与 `proxy_live_backup.original_config` 的 hooks 对齐，并从公共层和所有 Claude provider 的 `settings_config.env` 清除上述 5 个用户环境键及两个 context 覆盖键；Codex OAuth provider 的 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 显式覆盖保留；provider 凭据、地址和模型字段保持不变。

## 切割边界（extract 逻辑）

从 `settings.json` 切出 common 时，JSON 字段级操作（不同于 Codex 的 TOML 行级正则）：

1. `json.loads` 解析
2. `pop("model", None)` 删顶层 model
3. `env` dict 内删 `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_BASE_URL` /
   `ANTHROPIC_DEFAULT_*_MODEL[_NAME]` 整组，以及 5 个用户环境键（自动压缩键虽不进 common，但保留为 Codex OAuth provider 覆盖）
4. `json.dumps(indent=2, ensure_ascii=False)` 重新输出

其余全部保留。`sync_claude_common.py` 的 `extract_common()` 实现；普通用户环境键只在新启动的 Claude Code 进程中读取，Codex OAuth 的自动压缩窗口则由 provider 显式值随下一次切换写入 live。

## WAL 与热改安全

ccswitch 开着时直接写 `settings` 表是安全的：ccswitch 请求转发只写
`proxy_request_logs`，与 `settings` 不冲突。SQLite WAL 允许并发读写。

## 生效时机

ccswitch 平时只转发请求，不读 `common_config_claude`。**下次切换 provider**
时从 DB 重组写 `settings.json`，新快照才生效；repair 后必须先重启 cc-switch，丢弃旧内存快照，再切换 provider。普通用户环境键则在下一次启动 Claude Code 时读取；Codex OAuth 的自动压缩窗口随 provider 显式值在下一次切换时写入 live。切换后用脚本校验 settings.json 是否被降级。

## settings.json 相关标志（只读参考）

`~/.cc-switch/settings.json`（ccswitch 自己的配置，不是 Claude 的）：
- `enableClaudePluginIntegration`：claude plugin 集成开关。
- `currentProviderClaude`：当前 claude provider 的 id（对应 providers.id）。
- `skipClaudeOnboarding`：跳过 claude onboarding。
- `visibleApps.claude`：claude app 在 ccswitch UI 是否可见。
- `preserveCodexOfficialAuthOnSwitch` / `unifyCodexSessionHistory` /
  `currentProviderCodex`：codex 侧标志（本 skill 不管 codex）。
- `skillSyncMethod` / `skillStorageLocation`：skill 同步方式（与本 skill 无关）。

## 回滚

普通同步的 backup json 在 `~/.cc-switch/backups/sync-backup-<ts>.json`，含旧
`common_config_claude` 与代理快照。恢复：

```sql
UPDATE settings SET value='<旧值>' WHERE key='common_config_claude';
```

repair 模式另生成 `~/.cc-switch/backups/repair-<YYYY-MM-DD>_<时间>.db` 与
`~/.claude/backups/settings-repair-<YYYY-MM-DD>_<时间>.json`；四层回退优先恢复这两份，
不要只恢复 common 快照。
