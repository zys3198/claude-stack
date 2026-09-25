# MCP 安装台账

> 已归档（2026-09-24 现状表与流水分家）：本文件是**流水**，默认不读，追溯时按名或日期定位；现状表见 [`../mcp-install.md`](../mcp-install.md)。文中 `[X.md](X.md)` 形式的链接指向本目录内的同名流水。

记录所有 MCP server 的安装信息。配置写在 `C:\Users\zys31\.claude.json` 顶层 `mcpServers` 字段（user scope，全项目生效）。settings.json/settings.local.json 无 MCP 配置。

模板见 [README.md](README.md)。

---

## 当前在用

（2026-09-21 实测口径：`mcporter list` 返回 `2 server(s)`，全 healthy；`~/.claude.json` 顶层 `mcpServers` 只剩 headroom 一条。）

### headroom（stdio，user scope）
- 来源：https://github.com/headroomlabs-ai/headroom（PyPI `headroom-ai[all]`）；本体安装与 8787 代理链路见 [tool-install.md](tool-install.md)「headroom-ai 0.37.0（2026-09-05）」
- 注册位置：`C:\Users\zys31\.claude.json` → `mcpServers["headroom"]`
- 注册体（2026-09-21 读回）：`{"type":"stdio","command":"C:\\Users\\zys31\\.local\\bin\\headroom.EXE","args":["mcp","serve"],"env":{}}`
- 工具面：3 个（`mcporter list` 实测）
- 依赖：uv tool 安装的 `headroom.exe`；本条只登记 MCP 注册，与 `ANTHROPIC_BASE_URL` 指向 8787 的代理改造是两件事
- 备注：`~/.claude.json` 顶层 `mcpServers` 是 user scope，全项目生效；`settings.json` / `settings.local.json` 无 MCP 配置（2026-09-21 复查仍成立）

### douyin / douyin-mcp-server（mcporter home scope，2026-09-20 注册）
- 来源：https://github.com/yzfly/douyin-mcp-server （PyPI 包 `douyin-mcp-server`，pipx 安装，版本 1.2.1）
- 安装日期：包本身早于本记录（pipx 已装）；注册日期 2026-09-20
- 注册命令原文：`mcporter config add douyin --command "C:/Users/zys31/pipx/venvs/douyin-mcp-server/Scripts/douyin-mcp-server.exe" --scope home`
- 装到哪：`C:\Users\zys31\.mcporter\mcporter.json`（home scope），完整为 `{"mcpServers":{"douyin":{"command":"C:/Users/zys31/pipx/venvs/douyin-mcp-server/Scripts/douyin-mcp-server.exe"}}}`
- 依赖：Node/npm 提供的 `mcporter`（0.13.8）；pipx 包 `douyin-mcp-server`（venv 在 `C:\Users\zys31\pipx\venvs\douyin-mcp-server`）；`recognize_audio_*` 与 `extract_douyin_text` 需要环境变量 `DASHSCOPE_API_KEY`
- 工具面（5 个）：`get_douyin_download_link`、`extract_douyin_text`、`parse_douyin_video_info`、`recognize_audio_file`、`recognize_audio_url`
- 验证：2026-09-21 复跑 `mcporter list` → `douyin (5 tools, 12.1s)` healthy
- 备注：shared link 解析依赖 `https://www.iesdouyin.com/share/video/{id}` 页面的 `window._ROUTER_DATA`，2026-09-20 实测该页面已不再返回 `videoInfoRes`，`parse_douyin_video_info` 与 `get_douyin_download_link` 因此报 `'videoInfoRes'` KeyError。另一处缺陷：两个工具理论上不需要密钥，但构造函数仍调用 `create_asr_instance`，未设 `DASHSCOPE_API_KEY` 时直接抛 `未设置 DASHSCOPE_API_KEY`。本次实际提取改走浏览器路线（agent-browser 读取页面 + CDN 音频轨 + 本地 FunASR），详见 `exp/2026-09-20-douyin-content-notes/`
- **2026-09-24 复测（结论未变）**：`mcporter list` 仍报 `douyin (5 tools)` healthy，但 `mcporter call douyin.parse_douyin_video_info share_link=…` 实测返回 `未设置 DASHSCOPE_API_KEY`；`DASHSCOPE_API_KEY` 在 shell、`HKCU\Environment`、`~/.agent-reach/` 均无。healthy 只代表握手成功，**不代表工具可用**。`content-to-note` SKILL.md 抖音段已按此标注为不可用，未来审计勿据 healthy 反推可用。

## 已卸载

### chrome-devtools（2026-09-07 卸载）
- 来源：npm 包 `chrome-devtools-mcp`
- 安装方法：`claude mcp add --scope user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@1.8.0`
- 装到哪：`C:\Users\zys31\.claude.json` → `mcpServers["chrome-devtools"]`
- 卸载命令：`claude mcp remove chrome-devtools`
- 依赖：Node.js / npm / Chrome
- 备注：已从 user config 移除；由 agent-browser Skill 替代，未注册 agent-browser MCP。

### lean-ctx（2026-09-05 卸载）
- 来源：https://github.com/yvgude/lean-ctx
- 安装日期：2026-06 前后（2026-07-01 有 hook 修复记录）
- 安装方法：cargo 安装本体（二进制落 `~/.cargo/bin/lean-ctx.exe`），MCP 注册 `claude mcp add lean-ctx -- "C:/Users/zys31/.cargo/bin/lean-ctx.exe"`；另带 Claude Code hooks（PostToolUse 压缩等，见 settings.json）
- 装到哪：`~/.claude.json` → `mcpServers["lean-ctx"]`；配置 `C:\Users\zys31\.config\lean-ctx\config.toml`（shell allowlist 等安全门）；CLAUDE.md 尾部有 `<!-- lean-ctx -->` 注入段
- 依赖：Rust 工具链（或官方预编译二进制）
- 备注：用途=context 压缩（ctx_read/ctx_shell/ctx_search 替代原生工具）。Windows+Git Bash 下曾踩 `_lc: command not found`，已修（见 memory `lean-ctx-bashenv-fix`）。shell 命令受 allowlist 限制，新命令被拦用 `lean-ctx allow <cmd>` 加白。
- **Codex 侧集成（2026-08-08）**：`lean-ctx onboard` + `lean-ctx init --agent codex` 把 lean-ctx 注册到 Codex（`~/.codex/config.toml` 的 `[mcp_servers.lean-ctx]`）。onboard 同时装了 `~/.codex/hooks.json`（SessionStart/PreToolUse/PostToolUse/SessionEnd）、`~/.codex/AGENTS.md`、`~/.codex/LEAN-CTX.md`。**关键限制**：Codex 注册 MCP server（5 个只读 resources 可读）但不注入 function tools（ctx_read/ctx_shell 不在工具集），压缩走 CLI 回退。**CLI 不受 PathJail 限制**（2026-08-08 预验：`lean-ctx read ~/.codex/MIGRATION_HANDOFF.md` 成功，ctx_shell 的 allow_paths 只管 MCP 工具不管 CLI）。详见 [[codex-migration-phase1-done]]。
- **重装（2026-08-09）**：doctor 报 3 问题（data dir split 两处 stats.json / MCP pin 非标准 LEAN_CTX_DATA_DIR / stale ANTHROPIC_BASE_URL 致 401），根因=旧版 `.config` vs `.local/share` 路径坑延续。按官方 getting-started 重装：`lean-ctx uninstall --keep-binary --yes`（全清配置/数据/hooks/skill，保留 3.9.18 二进制）-> `lean-ctx init --global`（shell hook + 24 aliases）-> `lean-ctx init --agent claude`（MCP + hooks + SKILL.md + CLAUDE.md 托管块 v9）-> `lean-ctx doctor --fix`（补 Cursor/Copilot/Augment/Hermes/VS Code hooks+rules）。结果 37/37 通过。**3.9.18 布局统一**：env.sh + shell-hook.bash 都在 `~/.config/lean-ctx`，`.bashrc` source 路径正确；MCP 当前仍固定 `LEAN_CTX_DATA_DIR=C:\Users\zys31\.config\lean-ctx`（以 `.claude.json` 运行态为准，2026-09-01 核验）；`.bashenv` 留空（`init --global` 不写，`_lc` 由 `.bashrc` 的 shell-hook.bash 提供，`type _lc` = 函数，链路通）。旧 `_lc: command not found` 坑未复现。备份 `C:\Users\zys31\lean-ctx-backup-20260809\`（stats.json x2、config.toml、.bashrc、.bashenv、doctor-final.txt）。Codex 侧（`~/.codex/`）已不存在，重装未涉及。
- **卸载（2026-09-05）**：原因=杀软报木马隔离主 exe + 工具已退役（token 优化职责由 rtk hook 接管）。已清理：settings.json 8 处 hook + 7 条 mcp__lean-ctx__ 权限；`~/.claude.json` mcpServers.lean-ctx + 统计残留；CLAUDE.md 注入段；目录 `~/.claude/skills/lean-ctx`、`~/.config/lean-ctx`；二进制 `~/.cargo/bin/lean-ctx.exe`（杀软隔离）+ `lean-ctx.old.exe`。cc-switch 已同步（9746→7236，readback MATCH）。改前备份：`~/.claude/backups/lean-ctx-cleanup-20260905/`（**2026-09-21 实测该目录已不存在，恢复路径失效**）。旧 exe sha256（溯源用）：`43ae494333296731bb2ebd342be6b6a1d46d87eb364b294fd63da774fa9168bc`。三配置文件 grep lean-ctx 零残留。token 优化替代方案：rtk PreToolUse hook。原样装回（如杀软结论为误报且要恢复）：`cargo install lean-ctx` + `lean-ctx init --global && lean-ctx init --agent claude && lean-ctx doctor --fix` + 重跑 cc-switch 同步。

### cloudcli-browser（2026-08-09 卸载）
- 来源：npm 包 `@cloudcli-ai/cloudcli`（browser-use 模块）；官方站待补
- 安装日期：待补
- 安装方法：`npm i -g @cloudcli-ai/cloudcli`，MCP 注册 `claude mcp add cloudcli-browser -- "C:\Program Files\nodejs\node.exe" "C:\Users\zys31\AppData\Roaming\npm\node_modules\@cloudcli-ai\cloudcli\dist-server\server\modules\browser-use\browser-use-mcp.js"`
- 装到哪：`~/.claude.json` -> `mcpServers["cloudcli-browser"]`（**已移除**）；npm 全局目录
- 依赖：Node；全局 npm 安装
- 备注：用途=云端浏览器会话（与本地 playwright-mcp 互补）。重装时注意 js 路径里的 npm 全局根随机器变。
- **卸载（2026-08-09）**：用户要求删除。执行 `claude mcp remove cloudcli-browser`，从 user config 移除（修改 `~/.claude.json`）。npm 全局包 `@cloudcli-ai/cloudcli` 仍在（如需彻底清理：`npm uninstall -g @cloudcli-ai/cloudcli`）。原样装回见上方"安装方法"。

### playwright-mcp / b2c3d4e5-playwright-mcp-002（2026-08-09 卸载）
- 来源：https://github.com/microsoft/playwright-mcp （npm 包 `@playwright/mcp`）
- 安装日期：2026 年中（精确日待补）
- 安装方法：`claude mcp add playwright -- cmd /c npx @playwright/mcp@latest`
- 装到哪：`~/.claude.json` → `mcpServers["b2c3d4e5-playwright-mcp-002"]`，配置体 `{"command":"cmd","args":["/c","npx","@playwright/mcp@latest"]}`
- 依赖：Node/npx；首次跑会自动下浏览器
- 备注：用途=浏览器自动化/截图/填表/UI 调试。插件版 `playwright@claude-plugins-official` 也启用着，并存。
- **卸载（2026-08-09）**：与插件版 `plugin:playwright:playwright` 功能重复，且两实例共享 Chrome user data 目录（`mcp-chrome-a1a17c3`）导致并发抢锁冲突（browser_close 报 "Browser is already in use"）。删 user scope 实例、保留插件版。执行 `claude mcp remove b2c3d4e5-playwright-mcp-002`。原样装回见上方"安装方法"。

### context7 / a1b2c3d4-context7-mcp-001（2026-08-09 卸载）
- 来源：https://github.com/upstash/context7 （npm 包 `@upstash/context7-mcp`）
- 安装日期：2026 年中（精确日待补）
- 安装方法：`claude mcp add context7 -- cmd /c npx -y @upstash/context7-mcp`（实例名后被改过，含随机前缀）
- 装到哪：`~/.claude.json` → `mcpServers["a1b2c3d4-context7-mcp-001"]`，配置体 `{"command":"cmd","args":["/c","npx","-y","@upstash/context7-mcp"]}`
- 依赖：Node/npx
- 备注：用途=查库/框架官方文档。同名插件版 `context7@claude-plugins-official` 也启用着（见 tool-install.md），两者并存。
- **卸载（2026-08-09）**：与插件版 `plugin:context7:context7` 功能重复（resolve-library-id 实测两实例返回完全一致），清理冗余 user scope 实例、保留插件版。执行 `claude mcp remove a1b2c3d4-context7-mcp-001`。原样装回见上方"安装方法"。

### douyin / douyin-mcp-server（2026-09-20 注册）
- 条目已上移至上方「当前在用」（2026-09-21 整理）。曾误置于本节，实际为在用状态，`mcporter list` 实测 healthy。
