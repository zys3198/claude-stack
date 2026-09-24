# 编码

本机系统区域编码是 GBK。三处入口各自默认走它，同一个根因反复出现。

## Python：先设 `PYTHONUTF8=1`

- `open()` / `Path.read_text()` 默认用系统区域编码，不是 UTF-8。读含非 ASCII 的 UTF-8 文件抛 `UnicodeDecodeError`。
- **首选修法**：跑之前在环境里设 `PYTHONUTF8=1`（Python 3.7+ 的 UTF-8 模式）。一次治 `read_text`、`open`、stdout 全部同类问题。
- 脚本内兜底：`sys.stdout.reconfigure(encoding="utf-8")` 只治 stdout；`open(..., encoding="utf-8")` 只治那一处。只有当文件只有一个、且调用方无法保证环境变量时才改代码。
- 实例：JEV Ultrafast `browser.py:31` 的 `read_text()` 读含非 ASCII 的 `snapshot.js`，宿主导入即报 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 4229`。上游只在 Linux 容器跑过，宿主路径从未验证。同机 FunASR `transcribe.py` print emoji 抛 `UnicodeEncodeError` 也是这个根因。
- **别信 `requires-python` 声明**：声明写 `>=3.12`，uv 实际选了 3.14.5。环境差异只能靠实跑暴露。

## PowerShell 5.1：stdin 按 GBK 解码

- Claude Code 在 Windows 执行 hook 命令时经 Git Bash（`CLAUDE_CODE_GIT_BASH_PATH`）拉起 `powershell.exe` = **Windows PowerShell 5.1**，不是 pwsh 7。
- **stdin**：payload 是 UTF-8 字节，但 5.1 的 `[Console]::In.ReadToEnd()` 按 GBK 解码。真实 Stop payload 含中文 `last_assistant_message` 时 `ConvertFrom-Json` 直接失败。纯 ASCII 的手造 payload 测不出来。
  - 修法：`[Console]::OpenStandardInput()` + `MemoryStream` + `[Encoding]::UTF8.GetString()` 按字节读。
- **脚本文件**：5.1 把无 BOM 的脚本当 ANSI 读，非 ASCII 字符导致解析失败并报出与真实原因无关的语法错误。只写 ASCII，或保证 BOM。
- **async hook 静默失败**：解析错误/运行错误无任何表面症状。5.1 不接受的语法在 pwsh 7 里能过（如字符串内嵌 `$([DateTimeOffset.Now.ToString('o'))`），用 7 解析检查会漏。
  - 定位：临时加 `Add-Content` 文件日志，查完删除。
- **测试必须原样复刻**：`echo '<含中文的真实JSON>' | bash.exe -lc 'powershell.exe -NoProfile -File "..."'`，不能用 pwsh 7 直接跑。

## Windows 原生命令

- `netstat`、`tasklist` 之类按系统代码页输出，直接按 UTF-8 解码得到乱码。读取前确认代码页，或改用 PowerShell 对应命令。

## 外发中文前先验

- Windows Git Bash 中，Python heredoc 的中文字符串经 `subprocess.run` 传给 `glab api -f`，可能在远端保存为乱码（2026-09-11 发 EAM Issue #17 标题踩到）。
- 做法：构造 ASCII-only JSON（Unicode 转义），确认本地反解标题精确匹配，再通过支持 JSON Content-Type 的方式发送；首张写入后立即回读标题再继续批量。
