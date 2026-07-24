---
name: cc-switch-setting-sync
description: 把 Claude 的 ~/.claude/settings.json 公共配置同步进 ccswitch 数据库（~/.cc-switch/cc-switch.db 的 settings.common_config_claude），防止 ccswitch 切换/热切换 provider 时用旧值覆盖降级 settings.json。触发场景：用户提到 ccswitch 覆盖/重置/降级了 claude 配置、切换 provider 后 enabledPlugins/hooks/permissions 丢失、想把 claude 设置同步到 ccswitch、ccswitch 数据库、cc-switch.db、"同步 claude 配置"、"settings.json 被覆盖"、"防止降级"、"ccswitch 设置同步"。也适用于首次发现 ccswitch 热切换导致 enabledPlugins/hooks/statusLine 等字段丢失需要修复的情况。
---

# cc-switch 设置同步（Claude）

把 `~/.claude/settings.json` 中 **provider 无关的公共配置** 同步进 ccswitch DB 的
`settings.common_config_claude`，使 ccswitch 下次切换 provider 时不再降级 settings.json。

机制详解见 [references/ccswitch-architecture.md](references/ccswitch-architecture.md)。

## 前置确认

1. 路径默认 `~/.claude/settings.json` 与 `~/.cc-switch/cc-switch.db`，非默认时问用户。
2. **不需要关 ccswitch**：它转发请求只写 `proxy_request_logs`，与 `settings` 表不冲突，
   SQLite WAL 允许并发读写。直接热改。

## 工作流

### 1. 预览（dry-run）

先看清差异再写：

```bash
python scripts/sync_claude_common.py --dry-run
```

输出 old/new 长度对比。`new < old` 说明 settings.json 比上次同步瘦了（可能丢了字段），
`new > old` 说明加了新配置。两者相等则是 NO-OP。

### 2. 写入

脚本自动：备份旧值到 `~/.cc-switch/backups/sync-backup-<ts>.json` →
UPDATE `settings` → 读回校验匹配。

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

## 切割边界

**进 common（保留）**：enabledPlugins、extraKnownMarketplaces、hooks、permissions、
statusLine、attribution、effortLevel、includeCoAuthoredBy、env（非 ANTHROPIC_* 部分）等
全部 provider 无关配置。

**不进 common（脚本剔除）**：顶层 `model`；`env` 内的 `ANTHROPIC_AUTH_TOKEN`、
`ANTHROPIC_BASE_URL`、`ANTHROPIC_DEFAULT_*_MODEL[_NAME]` 整组。这些由 ccswitch 切换时从
provider 模板注入 + 代理运行时改写。

## 边界情况

- **只改了 settings.json，没切换过**：直接跑脚本同步即可。
- **ccswitch 内存缓存旧值**：切换后仍降级，需重启 ccswitch 载入新 DB 值
  （重启本身不改 settings.json，代理只断几秒）。
- **要回滚**：从 `~/.cc-switch/backups/sync-backup-<ts>.json` 取旧 `common_config_claude`
  全文，`UPDATE settings SET value='<旧值>' WHERE key='common_config_claude'`。
- **codex/openclaw 等 app_type**：本 skill 只管 claude。其他 app_type 的 common_config
  各自独立（common_config_codex / common_config_openclaw），如需同步照搬本流程改 key 名。

## 资源

- `scripts/sync_claude_common.py`：主同步脚本（备份+提取+写库+校验）。
- `references/ccswitch-architecture.md`：ccswitch 组装 settings.json 的机制、DB schema、
  切割边界、WAL 热改安全、回滚说明。
