# settings.json 接线补回片段

`settings.json` 在 `.gitignore:51–57`（「local-only secrets / personal config」）内，**不进 git**。后果是：从仓库恢复 `~/.claude` 只拿得到脚本、拿不到接线，`protocol-router.py` 会变成没人调用的死代码。`backups/` 同样不进 git，所以本文件是**唯一随仓库走的接线记录**。

适用场景：换机、从 GitHub 恢复、`settings.json` 被 cc-switch 快照覆盖后需要补回。

补法：把下面两段分别追加到 `settings.json` 的 `hooks.UserPromptSubmit` 与 `hooks.PreToolUse` 数组末尾。`UserPromptSubmit` 不支持 matcher，故第一段没有该键。

`hooks.UserPromptSubmit` 末尾：

```json
{"hooks":[{"command":"C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe \"C:/Users/zys31/.claude/hooks/scripts/protocol-router.py\"","timeout":10,"type":"command"}]}
```

`hooks.PreToolUse` 末尾：

```json
{"hooks":[{"command":"C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe \"C:/Users/zys31/.claude/hooks/scripts/protocol-router.py\"","timeout":10,"type":"command"}],"matcher":"Bash|PowerShell|Edit|Write|MultiEdit|NotebookEdit|Agent|Task"}
```

改动前先往 `backups/` 留一份 `settings.json` 副本——该文件没有 git 路径可回退。改完在会话里跑一条 Bash 命令（例如 `docker ps`），看是否收到协议注入；命中会在 `hooks/protocol-router.log` 留一行。

片段只覆盖 `protocol-router.py`。其余 hook 的接线见 `custom-setup.md` 的「hook」表，位置列就是注册位置；那些条目同样不在 git。
