# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。第三方优先记 Claude Code 插件；无兼容插件时才记 `~/.claude/skills/<name>/` 裸 skill。**2026-08-13 起 cc-switch 不再管理 skills**，也不用 agent-skills CLI 跨工具同步。

套装按**仓库级**记一条，内部保留与裁剪写备注，不逐个开条目。自建 skill 见 [custom-setup.md](custom-setup.md)。插件启用状态另见 [tool-install.md](tool-install.md)。

历史变更在 [archive/skill-install.md](archive/skill-install.md)，默认不读。

## 第三方 skill 套件

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Matt Pocock skills | 在用 | `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/skills/` | https://github.com/mattpocock/skills | `/plugin install mattpocock-skills@mattpocock` | 主力套件，35 个 SKILL.md，分 engineering / in-progress / misc / productivity 四组。**2026-09-24 实测：`~/.claude/skills/` 下已无裸名副本**，旧「裸名 + 插件」双形态只剩插件形态；部分 skill 带 `disable-model-invocation: true`，模型调不动，要用户在提示符敲 `/mattpocock-skills:<名>` |
| archify | 已归档 | `~/.claude/archive-skills/archify/` | 待补 | 手工拷贝 | v2.17.0-dev.1，带 LICENSE 与 THIRD_PARTY_NOTICES，属第三方分发 |

## 说明

- 磁盘上不再存在的第三方套件（仓颉 cangjie-skill、first-principles pack、Superpowers、ECC）只在流水里留痕，不进本表。
- `~/.claude/skills/` 下当前 21 个目录全部为自建，见 [custom-setup.md](custom-setup.md)。
