# agent-browser 路线

选择通用网页操作、抓取、截图、Electron 或 Slack 时读取本文件。命令以当前安装版本为准，不凭记忆补参数。

## 先取用法

```bash
agent-browser skills get core            # 工作流、常见模式、排错
agent-browser skills get core --full     # 附完整命令参考
agent-browser skills list                # 当前版本装了哪些子 skill
```

## Windows 三个坑

1. **管道会挂死。** daemon 首次启动时继承当次命令的 stdout 句柄且不释放，`agent-browser … | cat` 让读端等不到 EOF。每个 namespace 的第一条命令必须重定向到文件再读；中招后运行 `agent-browser doctor --fix`，并清掉对应 user-data-dir 的 Chrome。
2. **直接调原生入口。** 优先使用 `%APPDATA%\\npm\\node_modules\\agent-browser\\bin\\agent-browser-win32-x64.exe` 或 `.cmd`，不要经过 Git Bash 的 `sh → node → exe` 包装。
3. **批量摊薄启动开销。** 多条独立命令用 `batch`，不要为每条命令重复启动 daemon。

输出、截图和抓取结果按调用任务的证据目录保存；凭据不写入命令、脚本、终端输出或截图。
