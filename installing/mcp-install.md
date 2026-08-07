# MCP 安装台账

记录所有 MCP server 的安装信息。配置写在 `C:\Users\zys31\.claude.json` 顶层 `mcpServers` 字段（user scope，全项目生效）。settings.json/settings.local.json 无 MCP 配置。

模板见 [README.md](README.md)。

---

## 当前在用

### context7（实例名 a1b2c3d4-context7-mcp-001）
- 来源：https://github.com/upstash/context7 （npm 包 `@upstash/context7-mcp`）
- 安装日期：2026 年中（精确日待补）
- 安装方法：`claude mcp add context7 -- cmd /c npx -y @upstash/context7-mcp`（实例名后被改过，含随机前缀）
- 装到哪：`~/.claude.json` → `mcpServers["a1b2c3d4-context7-mcp-001"]`，配置体 `{"command":"cmd","args":["/c","npx","-y","@upstash/context7-mcp"]}`
- 依赖：Node/npx
- 备注：用途=查库/框架官方文档。同名插件版 `context7@claude-plugins-official` 也启用着（见 tool-install.md），两者并存。

### lean-ctx
- 来源：https://github.com/yvgude/lean-ctx
- 安装日期：2026-06 前后（2026-07-01 有 hook 修复记录）
- 安装方法：cargo 安装本体（二进制落 `~/.cargo/bin/lean-ctx.exe`），MCP 注册 `claude mcp add lean-ctx -- "C:/Users/zys31/.cargo/bin/lean-ctx.exe"`；另带 Claude Code hooks（PostToolUse 压缩等，见 settings.json）
- 装到哪：`~/.claude.json` → `mcpServers["lean-ctx"]`；配置 `C:\Users\zys31\.config\lean-ctx\config.toml`（shell allowlist 等安全门）；CLAUDE.md 尾部有 `<!-- lean-ctx -->` 注入段
- 依赖：Rust 工具链（或官方预编译二进制）
- 备注：用途=context 压缩（ctx_read/ctx_shell/ctx_search 替代原生工具）。Windows+Git Bash 下曾踩 `_lc: command not found`，已修（见 memory `lean-ctx-bashenv-fix`）。shell 命令受 allowlist 限制，新命令被拦用 `lean-ctx allow <cmd>` 加白。

### playwright-mcp（实例名 b2c3d4e5-playwright-mcp-002）
- 来源：https://github.com/microsoft/playwright-mcp （npm 包 `@playwright/mcp`）
- 安装日期：2026 年中（精确日待补）
- 安装方法：`claude mcp add playwright -- cmd /c npx @playwright/mcp@latest`
- 装到哪：`~/.claude.json` → `mcpServers["b2c3d4e5-playwright-mcp-002"]`，配置体 `{"command":"cmd","args":["/c","npx","@playwright/mcp@latest"]}`
- 依赖：Node/npx；首次跑会自动下浏览器
- 备注：用途=浏览器自动化/截图/填表/UI 调试。插件版 `playwright@claude-plugins-official` 也启用着，并存。

### gitnexus
- 来源：https://github.com/abhigyanpatwari/GitNexus （需核实——当前是从 npx 缓存目录直接指 .cmd，原安装命令待补）
- 安装日期：待补
- 安装方法：现为 `~/.claude.json` 里 command 直指 `C:\Users\zys31\AppData\Local\npm-cache\_npx\e46929201c1128dd\node_modules\.bin\gitnexus.cmd mcp`。**注意：指 npx 缓存目录不稳，缓存清了就没**。重装建议改为标准形式：`claude mcp add gitnexus -- cmd /c npx -y gitnexus mcp`（包名以官方 README 为准）
- 装到哪：`~/.claude.json` → `mcpServers["gitnexus"]`
- 依赖：Node/npx
- 备注：用途=代码库图谱/影响面分析（api_impact/trace/cypher 等）。配套 skill `gitnexus-exploring`。

### cloudcli-browser
- 来源：npm 包 `@cloudcli-ai/cloudcli`（browser-use 模块）；官方站待补
- 安装日期：待补
- 安装方法：`npm i -g @cloudcli-ai/cloudcli`，MCP 注册 `claude mcp add cloudcli-browser -- "C:\Program Files\nodejs\node.exe" "C:\Users\zys31\AppData\Roaming\npm\node_modules\@cloudcli-ai\cloudcli\dist-server\server\modules\browser-use\browser-use-mcp.js"`
- 装到哪：`~/.claude.json` → `mcpServers["cloudcli-browser"]`；npm 全局目录
- 依赖：Node；全局 npm 安装
- 备注：用途=云端浏览器会话（与本地 playwright-mcp 互补）。重装时注意 js 路径里的 npm 全局根随机器变。
