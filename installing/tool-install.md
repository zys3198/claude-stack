# 工具安装台账（插件 / CLI / 桌面）

记录插件、CLI 工具、桌面软件与运行环境基线。第三方 skill 套件见 [skill-install.md](skill-install.md)，MCP 见 [mcp-install.md](mcp-install.md)，自建见 [custom-setup.md](custom-setup.md)。

历史变更在 [archive/tool-install.md](archive/tool-install.md)，默认不读。

## 插件 marketplace（6）

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| claude-plugins-official | 在用 | `~/.claude/plugins/marketplaces/claude-plugins-official/` | Anthropic | 待补 | 官方市场，含 context7、github 等 |
| mattpocock | 在用 | `~/.claude/plugins/marketplaces/mattpocock/` | https://www.aihero.dev | `/plugin marketplace add https://www.aihero.dev` | 主力套件来源 |
| ponytail | 在用 | `~/.claude/plugins/marketplaces/ponytail/` | https://github.com/DietrichGebert | `/plugin marketplace add https://github.com/DietrichGebert` | — |
| caveman | 已卸载 | — | https://github.com/JuliusBrussee | `/plugin marketplace add https://github.com/JuliusBrussee/caveman` | 2026-09-25 随插件一并移除 |
| last30days-skill | 在用 | `~/.claude/plugins/marketplaces/last30days-skill/` | https://github.com/mvanhorn | `/plugin marketplace add https://github.com/mvanhorn` | — |
| impeccable | 在用 | `~/.claude/plugins/marketplaces/impeccable/` | Paul Bakaus | 待补 | 插件本体已停用 |

## 插件（7）

启用状态以 `settings.json → enabledPlugins` 为准。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| mattpocock-skills | 在用 | `plugins/cache/mattpocock/mattpocock-skills/` | mattpocock | `/plugin install mattpocock-skills@mattpocock` | 见 [skill-install.md](skill-install.md) |
| ponytail | 在用 | `plugins/cache/ponytail/ponytail/` | ponytail | `/plugin install ponytail@ponytail` | SessionStart 注入 5,299 字符 |
| context7 | 在用 | `plugins/cache/claude-plugins-official/context7/` | claude-plugins-official | `/plugin install context7@claude-plugins-official` | 提供 context7 MCP 工具 |
| last30days | 停用 | `plugins/cache/last30days-skill/last30days/` | last30days-skill | `/plugin install last30days@last30days-skill` | 2026-09-25 停用。装了一个月只有 1 次调用记录（2026-09-24 由 deepseek-v4.1-flash 会话发起）。成本：listing 272 B/轮 + SessionStart 注入 221 B/会话 |
| caveman | 已卸载 | — | caveman | 先 `/plugin marketplace add https://github.com/JuliusBrussee/caveman` 再 `/plugin install caveman@caveman` | 2026-09-25 卸载（2026-09-24 起已无注入）。效果已并入 `CLAUDE.md` §5.1/§5.2 |
| github | 停用 | `plugins/cache/claude-plugins-official/github/` | claude-plugins-official | `/plugin install github@claude-plugins-official` | `enabledPlugins` 为 false |
| impeccable | 停用 | `plugins/cache/impeccable/impeccable/` | impeccable | `/plugin install impeccable@impeccable` | `enabledPlugins` 为 false |

## CLI 工具

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Claude Code | 在用 | `~/.local/bin/claude.exe` | Anthropic | — | `claude.exe.old.*` 为升级残留 |
| headroom | 在用 | `~/.local/bin/headroom.exe` | 0.37.0 | 见流水 2026-09-05 | `ANTHROPIC_BASE_URL` 指向它的 8787 |
| cc-switch | 在用 | `~/.cc-switch/`（配置目录） | 待补 | 手工拷贝 | GUI，不在 PATH |
| uv / uvx | 在用 | `~/.local/bin/uv.exe` | — | — | 另有 `uvw.exe` |
| node / npx | 在用 | `C:/Program Files/nodejs/` | — | — | — |
| agent-browser | 在用 | `AppData/Roaming/npm/agent-browser` | — | — | 0.38.1（2026-09-18 升级） |
| glab | 在用 | `AppData/Local/Programs/glab/glab` | — | — | GitLab CLI |
| cloudflared | 在用 | `C:/Program Files (x86)/cloudflared/` | — | — | 2026-09-05 核验 |
| pdftotext（Poppler） | 在用 | `/mingw64/bin/pdftotext` | — | — | MSYS2 版，非 Windows 安装包 |
| yt-dlp | 在用 | `~/.local/bin/yt-dlp.exe` | — | — | content-to-note 配套 |
| bili / twitter / xhs / rdt / snip | 在用 | `~/.local/bin/` | — | — | content-to-note 配套 |
| agent-reach | 在用 | `~/.local/bin/agent-reach.exe` | — | — | 1.5.0（2026-09-02） |
| browser-act | 在用 | `~/.local/bin/browser-act.exe` | — | — | — |
| iii | 在用 | `~/.local/bin/iii.exe` | 待补 | — | — |

## 运行环境基线

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Python 3.12 | 在用 | `AppData/Local/Programs/Python/Python312/` | — | — | **hook 固定用这个解释器**，换版本要改 `settings.json` |
| Python 3.11 / 3.14 | 在用 | `~/.local/bin/` | uv 装 | — | — |
| uv 托管环境 | 在用 | `~/.local/bin/` | — | — | bili / twitter / xhs 等由 uv 装 |
| WSL Ubuntu 桌面组件 | 在用 | Brewze Cursor Theme | — | 见流水 | — |

## 待核

下次触发本台账时必须消解成 `在用` / `停用` / `已归档`。

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Go | 待核 | 未在 PATH 与常见路径找到 | — | 见流水 2026-09-07 | 2026-09-07 记录为 1.27.0 |
| lean-ctx | 待核 | 未找到 | — | 见流水 | 另有 Codex 侧 shell 别名引用 `LEAN_CTX_AGENT` |
| GitNexus | 待核 | 未找到 | — | 见流水 | — |
| loopforge-cli | 待核 | 未找到 | — | 见流水 2026-09-17 | — |
| Better Harness | 待核 | 未找到 | — | 见流水 2026-09-19 | 流水记为已卸载 |
| Herdr | 待核 | 未找到 | — | 见流水 2026-09-21 | 流水记为实测已不在本机 |
