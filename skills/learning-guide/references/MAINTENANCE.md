# 维护说明

本文件只在维护 `learning-guide` 时使用。主文件负责运行时路由；本文件只负责维护规则、证据源和变更记录。

主文件路径：`SKILL.md`

---

## 何时必须更新

| 触发信号 | 必做动作 |
|---|---|
| 新装或卸载学习/调研类 skill / 插件 | 复核 `SKILL.md` 路由表 + `test-prompts.json` 样例 |
| 当前会话 system reminder 新增或删除 skill / agent / 工具名 | 先对照当前会话，再对照 `~/.claude/skills/` 与 `~/.claude/plugins/cache/` |
| 用户指出推荐过时、死引用、错归属、错默认路径 | 先查证据，再修正文案，再补 changelog |
| 路由决策改了分类、主路径或 fallback | 同步 `SKILL.md`、`test-prompts.json` |
| 兄弟路由器（ai-coding-guide / article-writing-guide / frontend-guide）边界改动 | 复核 description「不用于」清单与「组合顺序」段 |

## 证据源

按以下顺序取证，不跳级：

1. **本地已证实**：当前会话可用清单（`Available skills` / `Available tools` / `Available agent types`）、`~/.claude/skills/`、`~/.claude/plugins/cache/`、当前仓库文件。历史摘要、memory、prior-session 内容不算可用性证据。
2. **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
3. **经验判断**：维护者推荐、默认建议、经验排序；必须显式标成推荐，不得写成硬事实。
4. **证据不足**：影响主推荐结论时停下来问用户；不影响时标"不确定"或直接删。

## 同步文件

每次维护至少检查以下文件是否一起更新：

- `SKILL.md`
- `references/MAINTENANCE.md`（本文件）
- `CHANGELOG.md`
- `test-prompts.json`

## 更新流程

1. 扫当前会话可用项和本地安装项
2. 先修 P0：死 skill / 错默认路径 / 错归属（如把学习请求路由给写作域）
3. 再修 P1：过满措辞、把推荐写成事实、边界断言不稳
4. 最后修 P2：主文件过重、信息重复、规则散落
5. 抽查 `test-prompts.json`（跑子代理回归或 dry_run）
6. 记录 changelog

## 维护纪律

- 主语统一为 Claude Code 当前环境
- `SKILL.md` 不塞维护历史（历史只进 `CHANGELOG.md`）
- 看见死引用或错归属，当场修，不拖到下次
- 路由表条目删除必须引用真实误路由事故或官方变更证据（见 `SKILL.md` 文末路由表门禁），防无证据漂移
- 子代理会话缺 learning-guide 时的降级行为是已知风险（2026-07-22 RED 基线：transformer 学习请求降级到 tutorial-maker），路由设计须让下游 skill 各自能兜底

## 变更记录

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-07-22 | 新建本文件 | v1.3.0 四域路由统一补维护文档，对齐 ai-coding-guide/references/MAINTENANCE.md 模式 |
| 2026-07-24 | 裁决规则 3 补 expose-unknowns 判级归属（v1.3.2） | 组合审查：expose-unknowns 双挂 ai-coding/learning 无 tie-breaker，按主域分界 |
