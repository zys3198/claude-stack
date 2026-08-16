# 工具 / 插件安装台账

记录 CLI 工具、桌面软件、Claude Code 插件 marketplace 与插件启用状态。模板见 [README.md](README.md)。

---

## Claude Code 插件 marketplace（/plugin marketplace add）

| marketplace | 来源 | 状态 |
|---|---|---|
| claude-plugins-official | https://github.com/anthropics/claude-plugins-official | 启用中 |
| anthropic-agent-skills | https://github.com/anthropics/skills | 启用中 |
| mattpocock | https://github.com/mattpocock/skills | 启用中 |
| ecc | https://github.com/affaan-m/ECC | 启用中 |
| karpathy-skills | https://github.com/forrestchang/andrej-karpathy-skills | 启用中 |
| caveman | https://github.com/JuliusBrussee/caveman | 启用中 |
| ponytail | https://github.com/DietrichGebert/ponytail | 启用中 |
| open-code-review | https://github.com/alibaba/open-code-review | 启用中 |
| understand-anything | https://github.com/Egonex-AI/Understand-Anything | 启用中 |
| i-have-adhd | https://github.com/ayghri/i-have-adhd | marketplace 在，无启用插件 |
| better-harness | https://github.com/QoderAI/better-harness | 启用中 |
| minimalist-entrepreneur | https://github.com/slavingia/skills | 已加 marketplace，无启用插件 |

安装方法（通用）：
```
/plugin marketplace add <owner/repo>
/plugin install <plugin>@<marketplace>
```

## 当前启用插件（settings.json enabledPlugins，2026-08-07 快照）

- 官方：claude-code-setup / claude-md-management / code-review / code-simplifier / commit-commands / context7 / feature-dev / frontend-design / github / playwright / skill-creator / superpowers
- 三方：ecc / mattpocock-skills / ponytail / caveman / open-code-review / better-harness / andrej-karpathy-skills / understand-anything / example-skills / taste-skill / i-have-adhd

**坑**：cc-switch / claude-stack 装卸插件会丢 enabledPlugins 状态，装完立刻查 settings.json 还认不认（memory `ccswitch-plugin-integration-fragile`）。

## CLI 工具

### cc-switch
- 来源：https://github.com/farion1231/cc-switch
- 用途：Claude Code provider/配置切换 + skill 单系统同步
- 安装日期：待补
- 安装方法：桌面应用安装包（GitHub Releases）
- 装到哪：`~/.cc-switch/cc-switch.db`（settings.common_config_claude 会覆盖 ~/.claude/settings.json 公共配置——防降级见 skill `cc-switch-setting-sync`）
- 备注：切 provider 热切换可能丢 enabledPlugins/hooks/statusLine 字段。

### lean-ctx 本体
- 见 [mcp-install.md](mcp-install.md)（cargo 装二进制 + MCP 注册 + hooks）

### GitNexus / cloudcli
- 见 [mcp-install.md](mcp-install.md)（npm 全局/npx 形态）

### GitLab CLI（glab）
- 来源：https://gitlab.com/gitlab-org/cli（winget 包 `GLab.GLab`）
- 安装日期：2026-08-13
- 安装命令原文：`winget install --exact --id GLab.GLab --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity`
- 装到哪：`C:\Users\zys31\AppData\Local\Programs\glab\glab.exe`（用户 PATH 已包含该目录）
- 依赖：Windows Package Manager（winget）；GitLab 登录或 API Token 才能执行远端写操作
- 备注：已验证 `glab 1.113.0 (d628813)`；当前终端可能需重开后才能直接解析 `glab` 命令。

### OpenAI Codex CLI（已卸载）
- 来源：https://github.com/openai/codex（npm 包 `@openai/codex`）
- 卸载日期：2026-08-11
- 卸载命令原文：`codex logout`；`npm uninstall -g @openai/codex`
- 原安装位置：`C:\Users\zys31\AppData\Roaming\npm\node_modules\@openai\codex`、`C:\Users\zys31\.codex`
- 依赖：Node.js / npm
- 备注：Windows 核心已清理；同时删除未注册的 VS Code Codex 扩展内容、4 条定向 npm 缓存及 `C:\Users\zys31\AGENTS.md`。按用户选择保留 CC Switch 内 Codex 数据、不扫描 WSL；VS Code 占用的 0 文件扩展空目录保留。

### Kimi WebBridge（浏览器控制桥）
- 来源：https://cdn.kimi.com/webbridge（skill 文档指向官方帮助页 kimi.com/zh-cn/features/webbridge）
- 安装日期：2026-08-11
- 安装命令原文：`irm https://cdn.kimi.com/webbridge/install.ps1 | iex`
- 装到哪：守护进程 `C:\Users\zys31\.kimi-webbridge\bin\kimi-webbridge.exe`（日志 `...\.kimi-webbridge\logs\daemon.log`）；skill 注入 `~/.claude/skills/kimi-webbridge` 和 `~/.hermes/skills/kimi-webbridge`（均 v1.11.5）
- 依赖：需配浏览器扩展（两段式：守护进程 HTTP `127.0.0.1:10086` ↔ 浏览器扩展）；无扩展则 `extension_connected:false` 驱动不了浏览器
- 备注：二进制未签名、无版本元数据，来源非官方渠道可核实——用户知情后仍装。状态查询 `kimi-webbridge status`；启停 `kimi-webbridge start/stop`（skill 禁自动 stop/restart/uninstall）。
- 风险提示：守护进程常驻 + 用用户真实登录态控浏览器 + 往 AI runtime 写 skill，权限面大。

## 运行环境基线
- Node.js（`C:\Program Files\nodejs\node.exe`）
- Python 3.12（解释器名 `python312`；不设 PYTHONPATH）
- Rust/cargo（`~/.cargo/bin`，lean-ctx 依赖；MinGW64/MSVC 可能不可用，优先 pre-built）


## WSL Ubuntu 桌面组件

### Breeze Cursor Theme
- 来源：Ubuntu 26.04 官方仓库（`resolute-updates/universe`）
- 安装日期：2026-08-11
- 安装命令原文：`wsl.exe -d Ubuntu -u root -- apt-get install -y breeze-cursor-theme`
- 装到哪：WSL Ubuntu 系统包 `breeze-cursor-theme`；主题目录 `/usr/share/icons/breeze_cursors`
- 依赖：APT；本次仅新增该包
- 备注：当前用户通过 `gsettings` 设置 `org.gnome.desktop.interface cursor-theme` 为 `breeze_cursors`，大小 24。

## @deepseek-ai/dsh uninstall 2026-08-16
- action: uninstalled deepseek harness CLI (@deepseek-ai/dsh), full cleanup
- install cmd: npm i -g @deepseek-ai/dsh + npx @deepseek-ai/dsh web
- uninstall cmd: npm uninstall -g @deepseek-ai/dsh (removed 528 packages)
- cleaned: npm global pkg + bin links (dsh/dsh.cmd/dsh.ps1); entire C:\Users\zys31\.dsh\ (243 files: .credentials.yaml, sessions/storages, skills/agents/commands copies of ~/.claude, profiles with nested node_modules + web)
- kept: ~/.claude/skills original (69 dirs verified intact); npm/npx cache checked clean
- note: .dsh/skills(162) & .dsh/agents were independent copies not junctions; no dsh process running before delete
- 2026-08-16 residue sweep: removed persistent user env vars OPENCODE_GO_KEY + OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS (dsh opencode-go provider config); removed 5 TEMP dsh-* dirs (acl-locks + spill). settings.json ANTHROPIC_DEFAULT_*_MODEL_NAME deepseek/glm mappings KEPT (active Claude Code proxy config, not dsh residue). Verified gone.
