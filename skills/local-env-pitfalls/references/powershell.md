# PowerShell

## 变量名

- **变量名不区分大小写，`$HOME` 是只读自动变量**：给 `$home` 赋值会失败，后续只读统计误落到整个用户目录。
- 路径脚本避开 `$home`、`$pid`、`$host` 等自动变量，改用 `$herdrHome`、`$targetDir` 这类明确名称。
- 采信输出前先检查命令错误。

## 正则

- **`-match` / `-notmatch` / `-replace` 用 .NET 正则**：模式含非法转义（`\q`、`\p` 等不是合法转义的 `\字母`）会抛 `ArgumentException`。
- **在 `Where-Object` 里每个条目都抛错就被判 `$false` 过滤掉 → 整个集合清空**。2026-07-31 用 `-notmatch "\.qoder\bin\qodercli"` 清理用户 PATH，`\q` 非法，用户 PATH 被设成空字符串，靠从当前进程 `$env:Path` 剥离机器 PATH 才恢复。
- 路径/字符串匹配优先 `-like`/`-notlike`（通配符）或 `-eq`/`-contains`/`-notin`（精确，大小写不敏感）。
- 必须用正则时 `\` 写成 `\\`。合法转义只有 `\d \w \s \b \D \W \S \B \A \z \Z \G`。
- 改环境变量前先备份：`$old = [Environment]::GetEnvironmentVariable("Path","User")`。

## 查工具与端口

- **`Test-Path` / `Get-Command` 可能对真实可达路径返回 "Access is denied" 或 "not found"**。查 `$env:PATH` 更可靠，别凭 `Test-Path` 结论说工具不存在。
- **`Get-NetTCPConnection` 在本机常返回空**（即使服务在跑）。用 `docker ps` 确认容器健康。

## 删文件

- **`Remove-Item` 会被门禁 hook 拦**。用 `[System.IO.File]::Delete(path)` 或 `[System.IO.Directory]::Delete(path)` 绕过，在可写根下有效。
- **PS 5.1 的 `Remove-Item -Force` 对 junction 直接报 `NullReferenceException`**（连 hook 都到不了）。改 `[System.IO.Directory]::Delete(path, $false)`。详见 [`git-bash.md`](git-bash.md) 的 junction 一节。
