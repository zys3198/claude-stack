# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。第三方优先记 Claude Code 插件；无兼容插件时才记 `~/.claude/skills/<name>/` 裸 skill。**2026-08-13 起 cc-switch 不再管理 skills**，也不用 agent-skills CLI 跨工具同步。

套装按**仓库级**记一条，内部保留与裁剪写备注，不逐个开条目。自建 skill 见 [custom-setup.md](custom-setup.md)。插件启用状态另见 [tool-install.md](tool-install.md)。

历史变更在 [archive/skill-install.md](archive/skill-install.md)，默认不读。

## 第三方 skill 套件

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Matt Pocock skills | 在用 | `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/skills/` | https://github.com/mattpocock/skills | `/plugin install mattpocock-skills@mattpocock` | 主力套件，35 个 SKILL.md，分 engineering / in-progress / misc / productivity 四组。**2026-09-24 实测：`~/.claude/skills/` 下已无裸名副本**，旧「裸名 + 插件」双形态只剩插件形态；部分 skill 带 `disable-model-invocation: true`，模型调不动，要用户在提示符敲 `/mattpocock-skills:<名>` |
| archify | 已归档 | `~/.claude/archive-skills/archify/` | 待补 | 手工拷贝 | v2.17.0-dev.1，带 LICENSE 与 THIRD_PARTY_NOTICES，属第三方分发 |
| last30days | 在用 | `~/.claude/skills/last30days/` | https://github.com/mvanhorn/last30days-skill | 重新 clone 上游取 v3.25.0 | 3.0 MB，v3.25.0。**2026-09-25 由插件降级为裸 skill**：原插件 `last30days@last30days-skill` 与市场注册均已卸载移除。跳过上游 `assets/`（14 MB 演示素材）。带 `disable-model-invocation: true`，只走 `/last30days` 手动调用。**2026-09-25 本地化裁剪**：SKILL.md 2426 → 2067 行（258,163 → 200,078 B，-22.5%）。Setup Wizard（244 行）、topic lanes（83 行）、query modes（38 行）三块移入 `references/`，原位留指针；删重复的 `SKILL_DIR` 注释、BSD/macOS `mktemp` 注释。备份 `backups/skill-localize-2026-09-25/last30days/`；**2026-09-26：按 writing-for-agents 将 description 收窄为近 30 天多来源研究指针，权限字段保持** |
| impeccable | 在用 | `~/.claude/skills/impeccable/` | https://github.com/pbakaus/impeccable | 重新 clone 上游取 v4.4.0 | 2.2 MB，v4.4.0。**2026-09-25 由插件降级为裸 skill**：原插件与市场注册均已卸载移除。跳过上游 `plugin/hooks/`（裸装不带 hook）。带 `disable-model-invocation: true`，只走 `/impeccable` 手动调用。**2026-09-25 本地化评估：判定不改**——reference 按需加载不占常驻 token；native 分支（`ios.md`、`android.md`、`adapt.native.md`、`audit.native.md`）被 11 处以上交叉引用，删除只造死链；`degraded/` 是无 subagent 能力时的降级路径，与平台无关；**2026-09-26：按 writing-for-agents 将 description 收窄为界面设计、评审与迭代指针，权限字段保持** |
| motrix | 在用 | `~/.claude/skills/motrix/` | `@motrix/cli` 0.5.0 自带（https://github.com/motrixapp/cli） | `motrix skill install` | 4,390 B，单 SKILL.md，与 CLI 版本绑定。`skills/*` 默认忽略、未进白名单（第三方，不备份，恢复靠重跑安装命令）。驱动 Motrix 2.0 桌面端（MDXP over bridge，**不是** aria2 16800）。CLI 与桌面端见 [tool-install.md](tool-install.md)；**2026-09-26：按 writing-for-agents 将 description 收窄为下载任务操作入口，权限字段保持** |

## 说明

- 磁盘上不再存在的第三方套件（仓颉 cangjie-skill、first-principles pack、Superpowers、ECC）只在流水里留痕，不进本表。
- `~/.claude/skills/` 下当前 24 个目录：21 个自建（见 [custom-setup.md](custom-setup.md)），3 个第三方裸 skill（last30days、impeccable、motrix，见上表）。
