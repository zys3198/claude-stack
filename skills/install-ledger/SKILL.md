---
name: install-ledger
description: 安装台账：登记、核对、追溯 skill／插件／MCP／CLI／桌面工具的来源与安装状态。
---

# 安装台账治理

## 边界

本 skill 只写记录。安装、卸载、物理删除、恢复、移动工具与 skill，修改生产配置、权限或认证数据，以及 commit/push，按全局确认线单独走；已明确授权的范围直接执行，不重复询问。

## 台账分工

| 内容 | 台账 |
|---|---|
| 自建 skill、hook、statusline、全局定制 | `installing/custom-setup.md` |
| 裸 skill、外部仓库、skill 套件 | `installing/skill-install.md` |
| 插件 marketplace、CLI、桌面工具 | `installing/tool-install.md` |
| MCP 服务、MCP 二进制与注册命令 | `installing/mcp-install.md` |

## 现状表

每个台账 = **现状表**（`installing/<台账>.md`）+ **流水**（`installing/archive/<台账>.md`）。默认只读现状表；流水按名或按日期定位。

现状表固定 6 列，顺序固定：

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| 与磁盘或配置里一致 | 见下 | 磁盘路径，或配置键 | 第三方写仓库地址；自建写 `自建`；移植写 `移植自 <源>` | 见下 | 一句话；日期写 `YYYY-MM-DD`；需要背景写 `见流水 <日期>`；没有写 `—` |

- **状态** 只用 `在用` / `停用` / `已归档` / `待核`。已卸载和已删除的整行删掉，只在流水留痕。`待核` 是位置没能当场核实的落点，下次触发必须消解。
- **恢复** 写 `git`（在 `.gitignore` 白名单内）、`手工拷贝`（不在 git，迁移会丢）、或安装命令原文。出现 `手工拷贝` 就是有人要为迁移负责。

同表内名称不重复，一行一个资产。流水条目格式、归档规则、组织规则见 [`references/ledger-protocol.md`](references/ledger-protocol.md)。

## 执行流程

安装、恢复或卸载完成后，**同一轮**做完三件事：

1. **登记** — 现状表出现这一条（新行，或状态列已改），流水追加一段、5 个字段齐。
2. **同步** — `settings.json` 的变更先 dry-run 再同步 DB。`settings-sync-auto.py` 只挂 `PostToolUse(Edit|Write)`；`claude plugin install/uninstall/disable/enable` 这类 CLI 改的 `settings.json` **不触发自动同步**，要手动跑 `python ~/.claude/skills/cc-switch-setting-sync/scripts/sync_claude_common.py`，否则下次切 provider 时会被 DB 旧快照整条回滚。
3. **读回** — 状态列的值与运行时实测相符；不符时以实测改表。

归属不清或状态冲突时读 [`references/verification.md`](references/verification.md)。

## 输出格式

```text
结论：当前台账状态与关键问题
证据：来源 / 当前状态 / 验证方式
已修改：文件与最小差异
未完成：待补证据、待用户确认或未执行动作
验证：Git 状态、目标 diff 检查、实际状态核对
下一步：一个最小可执行动作
```
