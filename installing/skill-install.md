# Skill 安装台账（外部来源）

记录从外部装入的 skill / skill 套件。第三方优先记 Claude Code 插件；无兼容插件时才记 `~/.claude/skills/<name>/` 裸 skill。**2026-08-13 起 cc-switch 不再管理 skills**，也不用 agent-skills CLI 跨工具同步。

套装按**仓库级**记一条，内部保留与裁剪写备注，不逐个开条目。自建 skill 见 [custom-setup.md](custom-setup.md)。插件启用状态另见 [tool-install.md](tool-install.md)。

历史变更在 [archive/skill-install.md](archive/skill-install.md)，默认不读。

## 第三方 skill 套件

| 名称 | 状态 | 位置 | 出处 | 恢复 | 备注 |
|---|---|---|---|---|---|
| Matt Pocock skills（插件形态） | 停用 | `~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/` | https://github.com/mattpocock/skills | `/plugin enable mattpocock-skills@mattpocock` | 25 个 SKILL.md，分 engineering（18）/ productivity（7）两组；misc（4）与 in-progress（6）插件本就不加载。**2026-09-30 停用**：`enabledPlugins` 置 false，cache 与 marketplace clone（commit `84fdeff`）原样冻结，作本地副本的 fork 基线 |
| Matt Pocock skills（本地副本） | 在用 | 24 份，`~/.claude/skills/` 下的**真实目录**（2026-10-02 已摘除库外符号链接、复制回仓库内，该库副本同日出清） | 同上，v1.2.3（MIT） | 重装插件后复制，再按备注重做 `handoff` 的落点改动；或按 [archive/skill-install.md](archive/skill-install.md) 2026-09-30 条重做 | **2026-09-30 由插件形态转本地裸名**：改 `description` 并加 `version: 1.2.3`，25 份的正文与附属文件逐字节未动（唯一例外见本条末尾）；未带 35 个 `agents/openai.yaml`（CC 读不到）；11 个模型可见，14 个 `disable-model-invocation: true` 需手敲。**同日描述由直译改为改写**：英文触发词（`"diagnose"`/`"red-green-refactor"`/`"review since X"`/`"grill"`）与上游术语原词（深模块／接缝／深化点／曳光弹／统一语言）保留并就地加中文解释，否定句改肯定句，「代理」统一改「Agent」，模型可见与仅 `/` 菜单两类详略都写全。**2026-09-30 落点分叉，仅 `handoff` 一份**：正文的落点句与 `description` 由「系统临时目录」改指任务笔记目录，无任务笔记时仍退系统临时目录。依据是用户 2026-09-24 的裁定「持久资料不能放入临时目录」（[archive/custom-setup.md](archive/custom-setup.md)），handoff 与任务笔记的寿命分界写入 [../docs/protocols/task-notes.md](../docs/protocols/task-notes.md) 的「与相邻机制的区别」一节。**2026-10-01 落点再改**：会话目录弃用后改指 `notes/<任务名>/handoff/<日期>-<短名>.md`，见同条协议改动。复查上游 diff 时这一份除外。**2026-10-02 归档 `resolving-merge-conflicts`**：上游 changeset `remove-resolving-merge-conflicts` 判定该 skill 不再需要（agent 自己处理进行中的 merge/rebase 冲突，无替代品），按用户裁定跟随删除。真身曾移入 `archive-skills/`，**该目录 2026-10-02 已空，此副本无处可寻**；勘察确认本地与插件缓存 1.2.3 的正文逐字节相同，唯一差异是 `version` 字段与中文 description，无独有内容，故删除无损失。**2026-10-02 落点订正**：副本一度被改成指向 `~/.config/magpie/library/skills/` 的符号链接，当日已全部复制回 `~/.claude/skills/` 下的真实目录（详见 [../docs/protocols/ledger.md](../docs/protocols/ledger.md) 第八节）。这批副本是第三方，不在 git 白名单内，**没有 `.claude` 快照可回退**——退路是上面记的冻结插件 cache（1.2.3），改动前先与 cache 逐字 diff 取差异来源。**1.3 更新暂缓**：上游 `plugin.json` 仍为 1.2.3，main 上 14 个 changeset 待发，按用户裁定等正式发布再 port，待并清单见 [mattpocock-1.3-pending.md](mattpocock-1.3-pending.md) |
| impeccable | 在用 | `~/.claude/skills/impeccable/` | https://github.com/pbakaus/impeccable | 重新 clone 上游取 v4.4.0 | 2.2 MB，v4.4.0。**2026-09-25 由插件降级为裸 skill**：原插件与市场注册均已卸载移除。跳过上游 `plugin/hooks/`（裸装不带 hook）。带 `disable-model-invocation: true`，只走 `/impeccable` 手动调用。**2026-09-25 本地化评估：判定不改**——reference 按需加载不占常驻 token；native 分支（`ios.md`、`android.md`、`adapt.native.md`、`audit.native.md`）被 11 处以上交叉引用，删除只造死链；`degraded/` 是无 subagent 能力时的降级路径，与平台无关；**2026-09-26：按 writing-for-agents 将 description 收窄为界面设计、评审与迭代指针，权限字段保持** |

## 说明

- 磁盘上不再存在的第三方套件（仓颉 cangjie-skill、first-principles pack、Superpowers、ECC）只在流水里留痕，不进本表。
- `~/.claude/skills/` 下共 43 项，**全部为仓库内的真实目录**（2026-10-02 从 `~/.config/magpie/library/skills/` 的符号链接复制回来，该库不再充当真源）：17 个自建（见 [custom-setup.md](custom-setup.md)），2 个第三方裸 skill（last30days、impeccable，见上表），24 个 Matt Pocock 本地副本（见上表）。自建 18 项在 `.gitignore` 白名单内、有 git 快照；另 25 项（24 份 Matt Pocock 副本 + `impeccable`）是第三方、有意排除，退路见上表「恢复」列。2026-10-02 已清理完毕（4 份自建空壳 + 3 份归档物），`archive-skills/` 现为空目录。
- **2026-10-02 决定：24 份 Matt Pocock 副本保留，只登记状态不删。** 实测两处内容 0 个逐字节相同（24 份全有差异），插件 `enabledPlugins` 为 false，是磁盘双份不是运行时双载——没有双载风险。触发删除的条件：插件重新启用且本地副本不再需要独立于上游改动时。插件启用前先 `diff` 两处，取本地版差异来源，勿直接覆盖。
