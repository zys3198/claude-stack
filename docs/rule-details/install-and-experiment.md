# 安装登记与隔离试验细则

来源：全局 `CLAUDE.md` §7.1 与 §7.2（2026-09-19 结构搬移，内容未改）。

## 安装登记

- **装后必登记**：安装或卸载任何 skill、MCP、插件、CLI/桌面第三方工具，或新建自建 skill/hook 后，当轮在 `~/.claude/installing/` 对应文件（`skill-install.md`、`mcp-install.md`、`tool-install.md`、`custom-setup.md`）新增记录，包含来源、日期、安装命令原文、安装位置、依赖和备注；目标是仅凭台账即可原样恢复。

## 隔离试验

- **隔离试验**：可脱离项目的 skill、prompt、脚本、hook 等试验统一放在独立试验目录；试验前新建独立子目录，所有产物只放入该子目录，完成后按全局 `CLAUDE.md` §1 删除确认线一次性清理。
