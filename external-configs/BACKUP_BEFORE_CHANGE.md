# BACKUP_BEFORE_CHANGE

改 cc-switch 配置前备份 checklist。

## 步骤

1. 备份 db（带时间戳）：
   ```bash
   TS=$(date +%Y%m%d_%H%M%S)
   cp "C:/Users/zys31/.cc-switch/cc-switch.db" "C:/Users/zys31/.cc-switch/backups/cc-switch.db.$TS"
   ```
2. 备份 settings.json：
   ```bash
   cp "C:/Users/zys31/.cc-switch/settings.json" "C:/Users/zys31/.cc-switch/settings.json.bak.$TS"
   ```
3. 记当前 `enabledPlugins`（哪些 true），改完用来对比：
   ```bash
   cat "C:/Users/zys31/.cc-switch/settings.json"
   ```
4. 改完后 diff 旧备份 vs 新文件，差异贴用户确认再落地：
   ```bash
   diff "C:/Users/zys31/.cc-switch/settings.json.bak.$TS" "C:/Users/zys31/.cc-switch/settings.json"
   ```

## 回滚

反向 cp（用步骤 1/2 产生的带时间戳文件）：
```bash
cp "C:/Users/zys31/.cc-switch/backups/cc-switch.db.$TS" "C:/Users/zys31/.cc-switch/cc-switch.db"
cp "C:/Users/zys31/.cc-switch/settings.json.bak.$TS" "C:/Users/zys31/.cc-switch/settings.json"
```

## 注意

- db 改前必须 cp（cc-switch 运行时改 db 不自动备份）。
- `enabledPlugins` 改动影响全 plugin 启用，diff 必看。
- `backups/` 目录已存在，直接用。
- 回滚后重启 cc-switch / Claude Code 让配置生效。
