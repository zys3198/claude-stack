---
name: install-ledger
description: 已归档（2026-09-27）。正文并入 docs/protocols/ledger.md，校验脚本移到 hooks/scripts/ledger_check.py；本文件只作触发重定向。
disable-model-invocation: true
user-invocable: false
---

# 已归档：install-ledger

2026-09-27 按「并入协议」归档：本 Skill 的正文（边界、台账分工、现状表 6 列、执行流程、输出格式）与 `references/{ledger-protocol,verification}.md` 三合一进 `~/.claude/docs/protocols/ledger.md`；`scripts/ledger_check.py` 移到 `~/.claude/hooks/scripts/ledger_check.py`。归档理由是 `.claude/docs/protocols/` 是协议正文唯一的家，skill 层只留治理与触发面，机器判据集中在 `hooks/scripts/`。

**触发词**：安装台账、登记一下、台账核对、台账现状表、装完卸完登记。命中本文件只说明它已归档——未经用户明确同意不恢复、不复制、不执行。

- **改用**：`~/.claude/docs/protocols/ledger.md`；校验跑 `python ~/.claude/hooks/scripts/ledger_check.py`。
- **归档位置**：`~/.claude/backups/skill-consolidation-2026-09-27/install-ledger/`（`SKILL.md`、`references/` 两份、`scripts/ledger_check.py`；`SKILL.md` md5 `ff2813c38ead0591bc17ae123572dd51`）。本目录下残留的 `references/`、`scripts/` 是未被删的原件，内容已全部并入新落点，未再被引用。
- **恢复方式**：用该备份整目录覆盖 `~/.claude/skills/install-ledger/`，并把 `hooks/scripts/ledger_check.py` 移回 `scripts/`；只在用户明确要求时执行。
- **观察截止**：2026-11-26（60 天）。
