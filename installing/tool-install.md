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
| taste-skill | 本地目录 `C:\ZYS\Code\lab-area\taste-skill`（上游实为公开项目 https://github.com/leonxlnx/taste-skill，plugin.json 实锤；本地目录只是副本） | 已加 marketplace，启用状态见 settings.json |

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

### OpenAI Codex CLI（已卸载）
- 来源：https://github.com/openai/codex（npm 包 `@openai/codex`）
- 卸载日期：2026-08-11
- 卸载命令原文：`codex logout`；`npm uninstall -g @openai/codex`
- 原安装位置：`C:\Users\zys31\AppData\Roaming\npm\node_modules\@openai\codex`、`C:\Users\zys31\.codex`
- 依赖：Node.js / npm
- 备注：Windows 核心已清理；同时删除未注册的 VS Code Codex 扩展内容、4 条定向 npm 缓存及 `C:\Users\zys31\AGENTS.md`。按用户选择保留 CC Switch 内 Codex 数据、不扫描 WSL；VS Code 占用的 0 文件扩展空目录保留。

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
