---
name: cc-switch-setting-sync
description: 用户明确要求诊断或修复 cc-switch 切换 Claude provider 后的 settings.json 配置降级，或将 live 公共配置同步到 cc-switch DB 时使用；范围限于 Claude app_type。
disable-model-invocation: true
---
# cc-switch 设置同步（Claude）

> **自动化（2026-09-04 起）**：`hooks/settings-sync-auto.py` 已注册 PostToolUse（Edit|Write），
> settings.json 每次被编辑即自动同步 cc-switch DB，并按 live 目标键修正现有 `proxy_live_backup`（脚本自带 NO-OP 幂等，非命中路径毫秒级退出）。
> 本 skill 的 dry-run/写入步骤通常由 hook 代劳；以下手动流程仅用于排查、修复和验证。

把 `~/.claude/settings.json` 中 **provider 无关的公共配置** 同步进 ccswitch DB 的
`settings.common_config_claude`，使 ccswitch 下次切换 provider 时不再降级 settings.json。

机制详解见 [references/ccswitch-architecture.md](references/ccswitch-architecture.md)。

切换时按 `build_effective_settings_with_common_config`（cc-switch 源码 `services/provider/live.rs`）处理：以 provider 的 `settings_config` 为起点，把 DB 的 `common_config_claude` **深合并**进去（source 覆盖 target），再写 live `settings.json`。provider env 里非 ANTHROPIC 的 `CLAUDE_CODE_*` 键不应成为公共配置；其中 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 对 Codex OAuth provider 是必须保留的显式覆盖，用来压过 cc-switch 对 GPT-5.6 的 372000 默认值。本 skill 将其从 common/proxy 剔除，但 repair 不再删除 provider 覆盖；其他稳定行为键仍由 Windows 用户环境提供。

## 前置确认

1. 路径默认 `~/.claude/settings.json` 与 `~/.cc-switch/cc-switch.db`，非默认时问用户。
2. **不需要关 ccswitch**：它转发请求只写 `proxy_request_logs`，与 `settings` 表不冲突，
   SQLite WAL 允许并发读写。直接热改。
3. **确认 claude provider 已启用 Common Config**（providers 表
   `meta.commonConfigEnabled=true`）。切换时的「回提取公共配置」保护（v3.16.5+）
   **只对启用该开关的 provider 生效**，未启用时切换直接用 provider 快照覆盖
   settings.json（2026-08-13 事故根因）。UI 位置：provider 编辑表单的
   Common Config 区；查 DB：
   `SELECT name, meta FROM providers WHERE app_type='claude'`。

## 工作流

### 1. 预览（dry-run）

先看清差异再写：

```bash
python scripts/sync_claude_common.py --dry-run
```

输出 old/new 长度对比。`new < old` 说明 settings.json 比上次同步瘦了（可能丢了字段），
`new > old` 说明加了新配置。两者相等则是 NO-OP。

### 2. 写入

脚本自动：备份旧值到 `~/.cc-switch/backups/sync-backup-<ts>.json` → 用 live 配置精确覆盖
公共快照中的 `permissions` 与 `defaultMode` → 在同一事务中更新 `settings` 与现有
`proxy_live_backup` → 分别读回校验匹配。快照行缺失时只告警，不从 live 配置伪造重建。

```bash
python scripts/sync_claude_common.py
```

校验失败（marker 缺失或 provider 字段泄漏）脚本会 `[FAIL]` 并退出 1，不写库。

### 3. 切换验证

DB 改动在 **下次切换 provider** 时才生效（ccswitch 从 DB 重组写 settings.json）。
让用户在 ccswitch 里点当前 provider 重新应用一次，切完检查 settings.json：

```powershell
$sj = Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw
# 快速看最易降级的 marker
('enabledPlugins','hooks','extraKnownMarketplaces','env') | ForEach-Object {
  "{0,-4} {1}" -f ($(if($sj -match $_){'OK'}else{'!!'}), $_)
}
# provider 段应保留代理改写
$sj -match '"ANTHROPIC_BASE_URL"\s*:\s*"([^"]*)"' | Out-Null; $Matches[1]
```

provider 段 `ANTHROPIC_BASE_URL` 应是代理地址（如 `http://127.0.0.1:15721`），不是裸上游。
marker 全 OK 即无降级。

### 4. 修复模式（--restore，settings.json 已被降级时用）

若 settings.json 已丢字段（statusLine/hooks/enabledPlugins/permissions.deny 缺失）：

```bash
python scripts/sync_claude_common.py --restore
```

方向反转：DB common 快照 → settings.json 修复。保留 live 的 provider 字段
（`ANTHROPIC_*` env、`model`）；hooks 可保留 live 独有组，但 `permissions.allow`、
`permissions.ask`、`permissions.deny` 以快照逐项覆盖，不做并集合并，避免旧快照通过并集
重新复活已删除规则；`permissions.defaultMode` 同样以快照为准。改前备份到
`~/.claude/backups/`，语义幂等（键序差异不触发重写）。修复后记得按 §3 切换验证。

自动兜底：`~/.claude/hooks/settings-degrade-guard.py` 已在 SessionStart 注册，
每次 Claude 会话启动检测降级并自动执行同款修复（静默，恢复时输出提示）。

## 5. 一次性修复（`--repair`）

当 live 文件、公共快照、代理快照或 provider 环境键同时漂移时，不要分层手改；用一次 repair 生成同一目标并写入四层：

```bash
python scripts/sync_claude_common.py --repair --hooks-source db --dry-run
python scripts/sync_claude_common.py --repair --hooks-source db
```

`--auto-compact-window` 仍可识别但只提示弃用，不改变目标。`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 不进入 common/proxy；对 Codex OAuth 的 ChatGPT provider，必须在 provider 自身的 `settings_config.env` 中保留目标值，以覆盖 GPT-5.6 的 372000 默认值。以下其他稳定开关仍由 Windows 用户环境提供：`CLAUDE_CODE_DISABLE_ARTIFACT`、`CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`、`DISABLE_AUTOUPDATER`、`DISABLE_ERROR_REPORTING`、`DISABLE_TELEMETRY`。

repair 默认以 DB 公共快照的 hooks 为基线，并做当前接线的确定性收敛：`pretool-guard.py` 取代独立的 product/resource 入口，移除已停用的 `herdr-agent-state.ps1`，确保 `protocol-report.py` 接入 PreToolUse、PostToolUse、Stop。`--hooks-source live` 或 JSON 快照路径只在该来源已人工审阅时使用。

一次写入同时：

- 将修复后的公共配置写入 `settings.common_config_claude`；
- 保留 live 中已有的 provider 显式自动压缩值，重建 `settings.json` 公共部分；对齐 `proxy_live_backup.original_config` 的 hooks，代理快照继续清除用户环境键；
- 从 common/proxy 和所有 Claude provider 的 `settings_config.env` 清除其他稳定开关及 `CLAUDE_CODE_EFFORT_LEVEL`、`CLAUDE_CODE_MAX_CONTEXT_TOKENS`，但保留 Codex OAuth provider 的 `CLAUDE_CODE_AUTO_COMPACT_WINDOW` 显式覆盖，不改 provider 凭据、地址或模型。

`--dry-run` 不写文件、不写数据库；写入前保存完整 SQLite backup 与 settings 备份。若任一 Claude provider 未启用 Common Config、缺少代理快照或目标校验失败，repair 拒绝做部分写入。写入后重启 cc-switch，再执行 `--check`；用户环境变量则在下一次启动 Claude Code 时生效。


**进 common（保留）**：enabledPlugins、extraKnownMarketplaces、hooks、permissions、
statusLine、attribution、effortLevel、includeCoAuthoredBy，以及 env 中既非 provider 注入键、
也非用户环境权威键或 `CLAUDE_CODE_EFFORT_LEVEL` / `CLAUDE_CODE_MAX_CONTEXT_TOKENS` 的公共配置。

权限列表的公共快照以 live `settings.json` 为唯一权威：`allow`、`ask`、`deny` 每次同步都完整替换旧值，`permissions.ask` 可以是空数组，`permissions.defaultMode` 保持 `auto`；删除规则不会由旧快照并集恢复。

**不进 common（脚本剔除或拒绝）**：顶层 `model`；`env` 内的 `ANTHROPIC_API_KEY`、
`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`ANTHROPIC_MODEL`、
`ANTHROPIC_DEFAULT_*_MODEL[_NAME]` 整组；以及
`CLAUDE_CODE_AUTO_COMPACT_WINDOW`、`CLAUDE_CODE_DISABLE_ARTIFACT`、
`CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`、`DISABLE_AUTOUPDATER`、
`DISABLE_ERROR_REPORTING`、`DISABLE_TELEMETRY`、`CLAUDE_CODE_EFFORT_LEVEL`、
`CLAUDE_CODE_MAX_CONTEXT_TOKENS`。其中 Codex OAuth provider 的显式
`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 留在 provider 组中，由 cc-switch 切换时注入；其余 provider 组由 cc-switch 切换时注入 + 代理运行时改写，其他稳定键由 Windows 用户环境提供。

## 边界情况

- **只改了 settings.json，没切换过**：直接跑脚本同步即可。
- **provider 未启用 Common Config（meta.commonConfigEnabled=false）**：切换时不读
  common 快照，直接用该 provider 的旧快照覆盖 settings.json（同步无效）。先启用
  开关（见前置确认 3）→ `--restore` 修复 → 重启 ccswitch。
- **ccswitch 内存缓存旧值**：切换后仍降级，需重启 ccswitch 载入新 DB 值
  （重启本身不改 settings.json，代理只断几秒）。
- **要回滚**：从 `~/.cc-switch/backups/sync-backup-<ts>.json` 取旧 `common_config_claude` 全文，并按备份中的 `proxy_live_backup` 的 `app_type='claude'` 行同时恢复 `original_config` 与 `backed_up_at`；不要只回滚 common，否则代理停止或切换时仍可能使用新快照。
- **打开 Common Config 后立刻 401 Missing API key**：即上方「切割边界」里的
  `PROXY_MANAGED` 占位符所致（2026-09-21 实测）。确认快照里无该键；有就先跑一次
  `sync_claude_common.py` 重写快照，再重新打开开关。
- **codex/openclaw 等 app_type**：本 skill 只管 claude。其他 app_type 的 common_config
  各自独立（common_config_codex / common_config_openclaw），如需同步照搬本流程改 key 名。
- **自动压缩窗口的 provider 覆盖**：`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 对 Codex OAuth ChatGPT provider 不再只依赖 Windows 用户环境；目标值必须保留在 provider 自身的 `settings_config.env`，并在 live 中保留已有值。普通稳定开关仍由 Windows 用户环境提供；修改 provider 或 repair 后需重启 cc-switch，再切换 provider，Claude Code 新进程再读取 live 配置。
- **「关了的配置又回来」（四层一致性检查，2026-09-23 EFFORT 复活事故）**：CLAUDE_CODE_* 键
  存在于四层——注册表/进程 env、live settings.json、DB 公共快照、provider env。
  注入优先级 provider env > 公共快照；对 `CLAUDE_CODE_AUTO_COMPACT_WINDOW`，Codex OAuth provider 的显式值还优先于 GPT-5.6 的 372000 默认值。公共快照由 sync 脚本镜像 live，现有 `proxy_live_backup` 只修正目标键并保留其他代理字段，不从 live 配置伪造重建。
  规则：普通公共键仍只加 live 一处；`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 需同时保留在目标 Codex OAuth provider env，并在 live 写入同一目标值；`--repair` 不再删除该 provider 覆盖；
  **删键四层全扫**——live 用 grep，DB 用 `SELECT id,name FROM providers WHERE settings_config LIKE '%键名%'`
  （另查 settings 表 common_config_claude），注册表查 HKCU/HKLM Environment；
  **症状即信号**：改了 live 但切 provider 后旧值回来 = provider env 缺少显式覆盖或仍有旧 provider 快照。
  改 provider env 后重启 cc-switch 载入（内存缓存不改 settings.json）。

## 资源

- `scripts/sync_claude_common.py`：主同步脚本（备份+提取+写库+校验；`--restore` 修复模式）。
- `references/ccswitch-architecture.md`：ccswitch 组装 settings.json 的机制、DB schema、
  切割边界、WAL 热改安全、回滚说明。
