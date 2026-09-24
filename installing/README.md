# installing/ — 三方工具与自建设施台账

目的：**任何 skill / MCP / 插件 / CLI 装完，或自建 skill / hook / 配置改完，必须在对应台账登记一条**。重装机器、换环境、回滚时，拿着这些表就能原样装回。

字段含义、流水格式、归档规则见 [`install-ledger/references/ledger-protocol.md`](../skills/install-ledger/references/ledger-protocol.md)；归属判定见 [`verification.md`](../skills/install-ledger/references/verification.md)。本文件只做入口。

## 文件分工

| 文件 | 记什么 |
|---|---|
| `custom-setup.md` | **自建** skill / hook / statusline / 全局配置 |
| `skill-install.md` | 外部 skill / skill 套件 |
| `tool-install.md` | 插件 marketplace、插件、CLI 工具、运行环境 |
| `mcp-install.md` | MCP 服务、二进制与注册命令 |
| `archive/` | 四本台账的流水，**默认不读**，追溯时按名或日期定位 |

每个台账 = 一张现状表（本目录的 `<台账>.md`）+ 一份流水（`archive/<台账>.md`）。改一次登记要同时动这两处。

## 校验

```bash
python ~/.claude/skills/install-ledger/scripts/ledger_check.py
```

只读。检查列数与顺序、状态枚举、表内名称唯一、单表体量、`archive/` 是否齐全。
