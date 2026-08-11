# MCP 安装台账

记录所有 MCP server 的安装信息。配置写在 `C:\Users\zys31\.claude.json` 顶层 `mcpServers` 字段（user scope，全项目生效）。settings.json/settings.local.json 无 MCP 配置。

模板见 [README.md](README.md)。

---

## 当前在用


### lean-ctx
- 来源：https://github.com/yvgude/lean-ctx
- 安装日期：2026-06 前后（2026-07-01 有 hook 修复记录）
- 安装方法：cargo 安装本体（二进制落 `~/.cargo/bin/lean-ctx.exe`），MCP 注册 `claude mcp add lean-ctx -- "C:/Users/zys31/.cargo/bin/lean-ctx.exe"`；另带 Claude Code hooks（PostToolUse 压缩等，见 settings.json）
- 装到哪：`~/.claude.json` → `mcpServers["lean-ctx"]`；配置 `C:\Users\zys31\.config\lean-ctx\config.toml`（shell allowlist 等安全门）；CLAUDE.md 尾部有 `<!-- lean-ctx -->` 注入段
- 依赖：Rust 工具链（或官方预编译二进制）
- 备注：用途=context 压缩（ctx_read/ctx_shell/ctx_search 替代原生工具）。Windows+Git Bash 下曾踩 `_lc: command not found`，已修（见 memory `lean-ctx-bashenv-fix`）。shell 命令受 allowlist 限制，新命令被拦用 `lean-ctx allow <cmd>` 加白。
- **Codex 侧集成（2026-08-08）**：`lean-ctx onboard` + `lean-ctx init --agent codex` 把 lean-ctx 注册到 Codex（`~/.codex/config.toml` 的 `[mcp_servers.lean-ctx]`）。onboard 同时装了 `~/.codex/hooks.json`（SessionStart/PreToolUse/PostToolUse/SessionEnd）、`~/.codex/AGENTS.md`、`~/.codex/LEAN-CTX.md`。**关键限制**：Codex 注册 MCP server（5 个只读 resources 可读）但不注入 function tools（ctx_read/ctx_shell 不在工具集），压缩走 CLI 回退。**CLI 不受 PathJail 限制**（2026-08-08 预验：`lean-ctx read ~/.codex/MIGRATION_HANDOFF.md` 成功，ctx_shell 的 allow_paths 只管 MCP 工具不管 CLI）。原样装回：`lean-ctx onboard` 选 Codex + `lean-ctx init --agent codex`。详见 [[codex-migration-phase1-done]]。
- **重装（2026-08-09）**：doctor 报 3 问题（data dir split 两处 stats.json / MCP pin 非标准 LEAN_CTX_DATA_DIR / stale ANTHROPIC_BASE_URL 致 401），根因=旧版 `.config` vs `.local/share` 路径坑延续。按官方 getting-started 重装：`lean-ctx uninstall --keep-binary --yes`（全清配置/数据/hooks/skill，保留 3.9.18 二进制）-> `lean-ctx init --global`（shell hook + 24 aliases）-> `lean-ctx init --agent claude`（MCP + hooks + SKILL.md + CLAUDE.md 托管块 v9）-> `lean-ctx doctor --fix`（补 Cursor/Copilot/Augment/Hermes/VS Code hooks+rules）。结果 37/37 通过。**3.9.18 布局统一**：env.sh + shell-hook.bash 都在 `~/.config/lean-ctx`，`.bashrc` source 路径正确；MCP 不再 pin `LEAN_CTX_DATA_DIR`（只 command + instructions）；`.bashenv` 留空（`init --global` 不写，`_lc` 由 `.bashrc` 的 shell-hook.bash 提供，`type _lc` = 函数，链路通）。旧 `_lc: command not found` 坑未复现。备份 `C:\Users\zys31\lean-ctx-backup-20260809\`（stats.json x2、config.toml、.bashrc、.bashenv、doctor-final.txt）。Codex 侧（`~/.codex/`）已不存在，重装未涉及。原样装回：`lean-ctx uninstall --keep-binary --yes && lean-ctx init --global && lean-ctx init --agent claude && lean-ctx doctor --fix`。详见 memory `lean-ctx-bashenv-fix`（已更新）。


### gitnexus
- 来源：https://github.com/abhigyanpatwari/GitNexus （2026-08-11 核实：其 skills 与本机 9 个 gitnexus-* 吻合）
- 安装日期：待补
- 安装方法：现为 `~/.claude.json` 里 command 直指 `C:\Users\zys31\AppData\Local\npm-cache\_npx\e46929201c1128dd\node_modules\.bin\gitnexus.cmd mcp`。**注意：指 npx 缓存目录不稳，缓存清了就没**。重装建议改为标准形式：`claude mcp add gitnexus -- cmd /c npx -y gitnexus mcp`（npm 包名 `gitnexus`；`npx gitnexus analyze` 会自动安装配套 skill）
- 装到哪：`~/.claude.json` → `mcpServers["gitnexus"]`
- 依赖：Node/npx
- 备注：用途=代码库图谱/影响面分析（api_impact/trace/cypher 等）。配套 skill `gitnexus-exploring`。

## 已卸载

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
