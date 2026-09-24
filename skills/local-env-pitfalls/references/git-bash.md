# Git Bash / MSYS

## 失败先自纠

命令因门禁 hook 或 MSYS 路径转换失败时，换一种执行形式重试：拆成简单形式、改用原生工具（Read/Grep/Glob）、或改用 PowerShell 原生命令。不要卡在原始失败上等用户介入。

## 路径转换

- **以 `/` 开头的参数会被改写**：`reg.exe /ve`、`/d`、`/f` 被 MSYS 当 POSIX 路径翻译，`reg.exe` 返回「错误: 无效语法」。根相对值（URL 路径、容器内路径、正则）同理。
- **优先用双斜杠前缀**：容器内绝对路径写 `//root/...`、`//probe/...`，避开改写。
- **`MSYS_NO_PATHCONV=1` 是次选**：给命令加前缀会改变命令文本，使不带前缀的 `Bash(docker *)` allow 规则匹配不上，反而触发一次权限询问（2026-09-24 实测）。只在双斜杠确实不够用时才加。
- **Windows 原生命令要 Windows 风格路径**：`claude.exe` 收到 `CLAUDE_CONFIG_DIR=/c/Users/...` 会判定全新安装，把 `~/.claude/.claude.json` 重置成 389B 骨架（原 167KB）。一律写 `C:/...`。
  - 出事后恢复：`~/.claude/backups/` 里按时间取最大的 `.claude.json.backup.*` 拷回（当前损坏版先备份）。会话/认证/`settings.json` 不受影响。
- **找 bash 要显式指路径**：`PATH` 里 `C:\Windows\System32\bash.exe`（WSL 转发器）排在 Git Bash 之前。Git for Windows 装在 `C:\ZYS\Software\Git`（非 Program Files）。要真 bash 的工具都显式指向 `bin/bash.exe`，否则误启 WSL。
- **GitHub 直连不通**：443 connect timeout。clone / release 下载走 `https://gh-proxy.com/<github-url>`（2026-08-18 实测 5719 commits + 6MB tar.gz 均成功）。

## 引号与展开

- **Bash 工具把整条命令交给 `bash -c "<双引号>"`**。后果：
  - heredoc 正文里的反引号和 `$(...)` 会被当命令替换执行——即便用 `<<'EOF'` 引用定界符，正文仍是外层双引号字符串的一部分。
  - 正文里的 `$1`、`$(` 要写成 `\$1`、`\$(`。反引号用 `String.fromCharCode(96)` 或 `\x60` 规避。
  - 大段含 `$`／反引号的内容（JS 正则源码等）改走 native Write，不经 shell 解析。
- **单引号包 PowerShell 命令时** `$_`、`$null` 不会被 bash 展开，安全；但正则转义仍归 PowerShell 解析。
- **调 PowerShell 时变量被 Bash 吃成空值**：改用单引号包裹，或写成独立脚本文件再执行。
- **超长内联命令会被解析器截断**：长 heredoc 和超长单行在 Git Bash 上解析失败。超过一屏就写成文件再执行。

## junction 与符号链接

- **Windows API 不认 MSYS 格式 target**：`os.symlink` + `/c/users/...` 建的链接，Claude Code 读不到 `SKILL.md`（`os.path.exists=False`）。现有能用的 `content-to-note@` 实际是 **junction**（`os.path.islink=False, exists=True`）。
  - 建：`cmd /c mklink /J <dst> <src>`，dst/src 用 Windows 路径。
  - 验：`os.path.isdir(dst)=True` 且能读到 `SKILL.md`。
- **删 junction 别经 Git Bash 调 `cmd.exe /d /c rmdir`**：MSYS 可能改写参数并启动交互式 cmd；改到 PowerShell 后安全钩子还会把 `/d` 误判为系统删除路径。
  - 正路：先 `fsutil reparsepoint query` 或 Python `os.lstat` 校 `FILE_ATTRIBUTE_REPARSE_POINT`，再 `os.rmdir` 删链接，最后核对目标目录仍存在。
- **删含 junction 的目录先删链接本身**：`[System.IO.Directory]::Delete($root, $true)` 遇内部 junction 报 `Access to the path 'current' is denied`。改 `[System.IO.Directory]::Delete($junction, $false)`（`$false` = 不递归，只删链接）再递归删根。
  - 删前 `(Get-Item -LiteralPath <p> -Force).LinkType` 确认为 `Junction`/`SymbolicLink`，别把实体目录当链接删。
  - `Move-Item` 移 junction 不可靠，跨目录搬家用 `New-Item -ItemType Junction` 重建。

## 启动外部程序

- **`chrome://` 不能走系统 `start`**：`cmd.exe /c start "" "chrome://inspect/#remote-debugging"` 会弹「选择应用」（不是 Windows 默认 URL 协议）。让工具官方流程自己开，或直接定位 `chrome.exe` 传参。
