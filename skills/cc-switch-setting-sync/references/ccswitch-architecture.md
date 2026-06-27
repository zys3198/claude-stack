# ccswitch Claude Config 同步机制

## 问题
ccswitch（com.ccswitch.desktop）切换或热切换 provider 时，会把组装好的完整 JSON
整体写回 `~/.claude/settings.json`。组装方式：

```
settings.json = provider.settings_config.config  (provider 片段：env.ANTHROPIC_*)
              + settings.common_config_claude    (公共片段)
```

DB 里 `common_config_claude` 若过时（缺了用户手动加的 hooks /
enabledPlugins / statusLine / model 等字段），每次切换都会把 settings.json 降级。

## 关键表与字段

数据库：`~/.cc-switch/cc-switch.db`（SQLite，WAL 模式）

- `settings(key, value)`：`key='common_config_claude'` 存公共配置（JSON 文本）。
  同步目标就是这个 value。
- `providers(id, app_type, name, settings_config, is_current)`：每个 provider 一行。
  `app_type='claude'` + `is_current=1` 是当前激活的 claude provider。
  `settings_config` 是 JSON，内含 provider 片段（env.ANTHROPIC_* 等）。
- `proxy_live_backup(app_type, original_config)`：热切换时抓的快照（JSON）。
- `proxy_config`：代理端口、超时等。

## 什么是 provider 片段（不进 common）

这些由 ccswitch 在切换时从 provider 模板注入，绝不放进 `common_config_claude`，
位于 settings.json 的 `env` 对象内：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<key 或 PROXY_MANAGED>",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "glm-5.2[1M]",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "glm-5.2",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.2[1M]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.1[1M]",
    "ANTHROPIC_MODEL": "glm-5.1"
  }
}
```

代理开启时，`ANTHROPIC_BASE_URL` 会在运行时被改写成代理地址
（如 `http://127.0.0.1:.../v1`），token 改成 `PROXY_MANAGED`——这是运行时行为，
由 ccswitch 控制。

识别规则：**所有 `ANTHROPIC_` 前缀的 env 键都视为 provider 片段**，extract 时剔除。
provider 无关的 env 键（`CLAUDE_CODE_*`、`ENABLE_TOOL_SEARCH` 等）保留。

## 什么是公共配置（进 common）

provider 无关的全部配置，例如：

```json
{
  "attribution": { "commit": "", "pr": "" },
  "includeCoAuthoredBy": false,
  "permissions": { "allow": ["mcp__lean-ctx__ctx_read", "..."] },
  "hooks": { "PostToolUse": [...], "PreToolUse": [...], "Stop": [...], "...": "..." },
  "enabledPlugins": { "ecc@ecc": true, "ponytail@ponytail": true, "...": "..." },
  "extraKnownMarketplaces": { "...": "..." },
  "model": "sonnet",
  "statusLine": { "type": "command", "command": "...", "padding": 0 },
  "effortLevel": "high",
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "max",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "ENABLE_TOOL_SEARCH": "true"
  }
}
```

## 切割边界（extract 逻辑）

从 `settings.json` 切出 common 时：

1. 解析 JSON。
2. 遍历 `env` 对象，删除所有 `ANTHROPIC_` 前缀键。
3. 若 `env` 删空则移除 `env` 键。
4. 其余顶层键（hooks/enabledPlugins/permissions/statusLine/model/...）全部保留。
5. 重新序列化为 JSON（indent=2, ensure_ascii=False）。

`sync_claude_common.py` 的 `extract_common()` 实现。

## WAL 与热改安全

ccswitch 开着时直接写 `settings` 表是安全的：ccswitch 请求转发只写
`proxy_request_logs`，与 `settings` 不冲突。SQLite WAL 允许并发读写。

## 生效时机

ccswitch 平时只转发请求，不读 `common_config_claude`。**下次切换 provider**
时从 DB 重组写 settings.json，新值才生效。切换后用脚本校验 settings.json 是否被降级。

## settings.json 相关标志（只读参考）

`~/.cc-switch/settings.json` 含代理开关、当前 provider 指针等运行时标志
（具体字段名以实际文件为准，如 `enableLocalProxy`、`currentProviderClaude` 类字段）。

## 回滚

backup json 在 `~/.cc-switch/backups/sync-backup-<ts>.json`，
含旧 `common_config_claude` 全量。恢复：

```sql
UPDATE settings SET value='<旧值>' WHERE key='common_config_claude';
```
或用 `sync_claude_common.py --dry-run` 检查后重新同步。
