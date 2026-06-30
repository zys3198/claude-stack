# ccswitch Codex Config 同步机制

## 问题
ccswitch（com.ccswitch.desktop）切换或热切换 provider 时，会把组装好的完整 TOML
整体写回 `~/.codex/config.toml`。组装方式：

```
config.toml = provider.settings_config.config  (provider 片段)
            + settings.common_config_codex     (公共片段)
```

DB 里 `common_config_codex` 若过时（缺了用户手动加的 sandbox_mode /
memories / desktop 段等），每次切换都会把 config.toml 降级。

## 关键表与字段

数据库：`~/.cc-switch/cc-switch.db`（SQLite，WAL 模式）

- `settings(key, value)`：`key='common_config_codex'` 存公共配置（纯 TOML 文本）。
  同步目标就是这个 value。
- `providers(id, app_type, name, settings_config, is_current)`：每个 provider 一行。
  `app_type='codex'` + `is_current=1` 是当前激活的 codex provider。
  `settings_config` 是 JSON，内含 `auth`、`config`（provider 片段 TOML）、`modelCatalog`。
- `proxy_live_backup(app_type, original_config)`：热切换时抓的快照（JSON）。
- `proxy_config`：代理端口、超时等。codex 默认 `127.0.0.1:15721`。

## 什么是 provider 片段（不进 common）

这些由 ccswitch 在切换时从 provider 模板注入，绝不放进 `common_config_codex`：

```toml
model_provider = "custom"
model = "glm-5.2"

[model_providers]
[model_providers.custom]
name = "zhipu_glm"
base_url = "https://open.bigmodel.cn/api/coding/paas/v4"
wire_api = "responses"
requires_openai_auth = true
experimental_bearer_token = "<key 或 PROXY_MANAGED>"
```

代理开启时，base_url 会在运行时被改写成 `http://127.0.0.1:15721/v1`，
bearer 改成 `PROXY_MANAGED`——这是运行时行为，由 ccswitch 控制。

## 什么是公共配置（进 common）

provider 无关的全部配置，例如：

```toml
model_reasoning_effort = "high"
sandbox_mode = "danger-full-access"
approval_policy = "never"
[features]
hooks = true
memories = true
[hooks.state]
'C:\...\hooks.json:pre_tool_use:0:0'
trusted_hash = "sha256:..."
[projects.'c:\zys\code\lab-area']
trust_level = "trusted"
[desktop]
localeOverride = "zh-CN"
[env]
OPENAI_BASE_URL = "http://127.0.0.1:4444/v1"
```

## 切割边界（extract 逻辑）

从 `config.toml` 切出 common 时丢弃：

1. 顶层 `model_provider = ...`
2. 顶层 `model = "..."`
3. 空表头 `[model_providers]`
4. `[model_providers.custom]` 整个块直到下一个 `[` 开头的表头

其余全部保留。`sync_codex_common.py` 的 `extract_common()` 实现。

## WAL 与热改安全

ccswitch 开着时直接写 `settings` 表是安全的：ccswitch 请求转发只写
`proxy_request_logs`，与 `settings` 不冲突。SQLite WAL 允许并发读写。

## 生效时机

ccswitch 平时只转发请求，不读 `common_config_codex`。**下次切换 provider**
时从 DB 重组写 config.toml，新值才生效。切换后用脚本校验 config.toml 是否被降级。

## settings.json 相关标志（只读参考）

`~/.cc-switch/settings.json`：
- `enableLocalProxy`：本地代理开关。
- `preserveCodexOfficialAuthOnSwitch`：切换时是否保留官方 OAuth。
- `unifyCodexSessionHistory`：统一会话历史。
- `currentProviderCodex`：当前 codex provider 的 id（对应 providers.id）。

## 回滚

backup json 在 `~/.cc-switch/backups/sync-backup-<ts>.json`，
含旧 `common_config_codex` 全量。恢复：

```sql
UPDATE settings SET value='<旧值>' WHERE key='common_config_codex';
```
或用 `sync_codex_common.py --dry-run` 检查后重新同步。
