# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。第三方优先记 Claude Code 插件；无兼容插件时才记 `~/.claude/skills/<name>/` 裸 skill。**2026-08-13 起 cc-switch 不再管理 skills**，也不用 agent-skills CLI 跨工具同步。

套装按**仓库级**记一条，内部保留与裁剪写备注，不逐个开条目。自建 skill 见 [custom-setup.md](custom-setup.md)。插件启用状态另见 [tool-install.md](tool-install.md)。

历史变更在 [archive/skill-install.md](archive/skill-install.md)，默认不读。

## 第三方 skill 套件

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Matt Pocock skills（插件形态） | 停用 | `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/` | https://github.com/mattpocock/skills | `/plugin enable mattpocock-skills@mattpocock` | 25 个 SKILL.md，分 engineering（18）/ productivity（7）两组；misc（4）与 in-progress（6）插件本就不加载。**2026-09-30 停用**：`enabledPlugins` 置 false，cache 与 marketplace clone（commit `84fdeff`）原样冻结，作本地副本的 fork 基线 |
| Matt Pocock skills（本地副本） | 在用 | `~/.claude/skills/` 下 25 个裸目录 | 同上，v1.2.3（MIT） | 重装插件后复制；或按 [archive/skill-install.md](archive/skill-install.md) 2026-09-30 条重做 | **2026-09-30 由插件形态转本地裸名**：改 `description` 并加 `version: 1.2.3`，25 份的正文与附属文件逐字节未动（唯一例外见本条末尾）；未带 35 个 `agents/openai.yaml`（CC 读不到）；11 个模型可见，14 个 `disable-model-invocation: true` 需手敲。**同日描述由直译改为改写**：英文触发词（`"diagnose"`/`"red-green-refactor"`/`"review since X"`/`"grill"`）与上游术语原词（深模块／接缝／深化点／曳光弹／统一语言）保留并就地加中文解释，否定句改肯定句，「代理」统一改「Agent」，模型可见与仅 `/` 菜单两类详略都写全。**2026-09-30 落点分叉，仅 `handoff` 一份**：正文的落点句与 `description` 由「系统临时目录」改指当前任务的会话目录 `notes/<任务名>/<日期>-s<序号>/HANDOFF.md`，无任务笔记时仍退系统临时目录。依据是用户 2026-09-24 的裁定「持久资料不能放入临时目录」（[archive/custom-setup.md](archive/custom-setup.md)），handoff 与任务笔记的寿命分界写入 [../docs/protocols/task-notes.md](../docs/protocols/task-notes.md) 的「与相邻机制的区别」一节。复查上游 diff 时这一份除外 |
| archify | 已归档 | `~/.claude/archive-skills/archify/` | 待补 | 手工拷贝 | v2.17.0-dev.1，带 LICENSE 与 THIRD_PARTY_NOTICES，属第三方分发 |
| impeccable | 在用 | `~/.claude/skills/impeccable/` | https://github.com/pbakaus/impeccable | 重新 clone 上游取 v4.4.0 | 2.2 MB，v4.4.0。**2026-09-25 由插件降级为裸 skill**：原插件与市场注册均已卸载移除。跳过上游 `plugin/hooks/`（裸装不带 hook）。带 `disable-model-invocation: true`，只走 `/impeccable` 手动调用。**2026-09-25 本地化评估：判定不改**——reference 按需加载不占常驻 token；native 分支（`ios.md`、`android.md`、`adapt.native.md`、`audit.native.md`）被 11 处以上交叉引用，删除只造死链；`degraded/` 是无 subagent 能力时的降级路径，与平台无关；**2026-09-26：按 writing-for-agents 将 description 收窄为界面设计、评审与迭代指针，权限字段保持** |

## 说明

- 磁盘上不再存在的第三方套件（仓颉 cangjie-skill、first-principles pack、Superpowers、ECC）只在流水里留痕，不进本表。
- `~/.claude/skills/` 下当前 49 个目录：24 个原有（其中 2 个第三方裸 skill 为 last30days、impeccable，见上表；其余自建见 [custom-setup.md](custom-setup.md)），25 个为 2026-09-30 从 Matt Pocock 插件转入的本地副本（见上表）。
