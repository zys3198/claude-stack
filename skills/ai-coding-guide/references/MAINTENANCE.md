# 维护说明（路由层）

本文件只在更新 ai-coding-guide 路由层时使用。`routing.md` 负责运行时路由；本文件只负责维护规则、证据源和变更记录。

---

## 何时必须更新

| 触发信号 | 必做动作 |
|---|---|
| 新装或卸载 skill / 插件 | 复核 `routing.md` 推荐路径、`references/ecosystems.md` 生态说明、`evals/` 用例 |
| 当前会话 system reminder 新增或删除 skill / agent / 工具名 | 先对照当前会话，再对照 `~/.claude/skills/` 与 `settings.json` enabledPlugins |
| 用户指出推荐过时、死引用、错归属、错默认路径 | 先查证据，再修正文案，再补 changelog |
| 路由决策改了 A/B/C 选项或 fallback | 同步 `routing.md`、`ecosystems.md`、`evals/` |
| 新增或删除「必须 / 默认 / 官方 / 已装」类断言 | 复核证据等级，并把不确定项降级或删除 |

## 证据源

按以下顺序取证，不跳级：

1. **本地已证实**：当前会话可用清单（`Available skills` / `Available tools` / `Available agent types`）、`~/.claude/skills/`、`settings.json` enabledPlugins、当前仓库文件。历史摘要、memory、prior-session 内容不算可用性证据。
2. **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
3. **经验判断**：维护者推荐、默认建议、经验排序；必须显式标成推荐，不得写成硬事实。
4. **证据不足**：影响主推荐结论时停下来问用户；不影响时标「不确定」或直接删。

## 同步文件

每次维护至少检查以下文件是否一起更新：

- `SKILL.md`（description 触发词 = Step 1 信号表浓缩）
- `references/routing.md`（分诊主体）
- `references/routing-classification-details.md`（低频分类细节）
- `references/frontend-visual.md`（前端视觉子路径）
- `references/ecosystems.md`（生态 + 迁移闸门 + 黑名单）
- `references/MAINTENANCE.md`（本文件）
- `evals/`（路由行为回归用例）

## 更新流程

1. 扫当前会话可用项和本地安装项
2. 先修 P0：死 skill / 死命令 / 死路径 / 错默认路径 / 错归属
3. 再修 P1：过满措辞、把推荐写成事实、数量和边界断言不稳
4. 最后修 P2：主文件过重、信息重复、规则散落
5. 行为修正先补 RED 用例（`evals/`），再改正文
6. 记录 changelog

## 维护纪律

- 主语统一为当前环境
- 路由文件不塞维护历史
- `ecosystems.md` 不抢 `routing.md` 路由职责
- 看见死引用或错归属，当场修，不拖到下次
- 分类观察期：定期复盘 Step 2 各分类实际触发次数，零触发或仅误触发的降级/删除，防分类膨胀
- **路由表门禁**：删除任何分类/条目前必须引用真实误路由事故或官方变更证据，否则保持原样（防无证据漂移）

<!-- 吸收精简自 ai-coding-guide v1.9.0 references/MAINTENANCE.md，2026-08-18：audit.ps1/TEST-RESULTS 引用删（未随迁），同步文件列表改新骨架 -->
