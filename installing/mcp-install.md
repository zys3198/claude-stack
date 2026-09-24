# MCP 安装台账

记录 MCP 服务的二进制、注册命令与运行配置。注册点有三处，**互不相通，分别核**：

- `~/.claude.json → mcpServers`（Claude Code 自己的）
- `~/.mcporter/mcporter.json`（mcporter 的，user scope）
- `~/.config/mcporter/config.json`（mcporter 的另一份，远程 URL）

历史变更在 [archive/mcp-install.md](archive/mcp-install.md)，默认不读。

## 当前注册

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| headroom | 在用 | `~/.claude.json → mcpServers.headroom` | 待补 | 见流水 2026-09-05 | **Claude Code 侧唯一注册的 MCP**，stdio。与 `ANTHROPIC_BASE_URL=127.0.0.1:8787` 是同一条链路的两端 |
| douyin | 在用 | `~/.mcporter/mcporter.json → mcpServers.douyin` | douyin-mcp-server | 见流水 2026-09-20 | 指向 `C:/Users/zys31/pipx/venvs/douyin-mcp-server/Scripts/douyin-mcp-server.exe`。**不在 `~/.claude.json`**，Claude Code 里调不到，只有 mcporter 能拉起 |
| exa | 待核 | `~/.config/mcporter/config.json → mcpServers.exa` | https://mcp.exa.ai/mcp | 待补 | 远程 URL 形态，无本地二进制。2026-06-08 起未动，是否仍在用未核实 |

## 二进制在盘但无注册

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| chroma-mcp | 待核 | `~/.local/bin/chroma-mcp.exe` | 待补 | — | 三处注册点都没找到它 |
| douyin-mcp-server | 待核 | `~/.local/bin/douyin-mcp-server.exe` | 待补 | — | 与 pipx venv 里那份可能重复，需比对后再定去留 |

## 已卸载（仅留痕）

chrome-devtools、lean-ctx、cloudcli-browser、playwright-mcp、context7（MCP 形态）均已卸载，细节见流水。注意 context7 的**插件形态**仍在用，见 [tool-install.md](tool-install.md)。
