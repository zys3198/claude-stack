# 维护说明

本文件只在维护 `article-writing-guide` 时使用。主文件负责运行时路由；本文件只负责维护规则、证据源和变更记录。

主文件路径：`SKILL.md`

---

## 何时必须更新

| 触发信号 | 必做动作 |
|---|---|
| 新装或卸载写作类 skill / 插件 | 复核 `SKILL.md` §1 路由表 + `REFERENCE.md` 决策树 + `test-prompts.json` 样例 |
| 当前会话 system reminder 新增或删除 skill / agent / 工具名 | 先对照当前会话，再对照 `~/.claude/skills/` 与 `~/.claude/plugins/cache/` |
| 用户指出推荐过时、死引用、错归属、错默认路径 | 先查证据，再修正文案，再补 changelog |
| 路由决策改了阶段分类、主路径或 pipeline | 同步 `SKILL.md`、`REFERENCE.md`、`test-prompts.json` |
| 兄弟路由器（ai-coding-guide / learning-guide / frontend-guide）边界改动 | 复核 description 触发词与跨界交接条款 |

## 证据源

按以下顺序取证，不跳级：

1. **本地已证实**：当前会话可用清单（`Available skills` / `Available tools` / `Available agent types`）、`~/.claude/skills/`、`~/.claude/plugins/cache/`、当前仓库文件。历史摘要、memory、prior-session 内容不算可用性证据。
2. **官方可证实**：官方 README、官方 marketplace 元数据、官方插件说明。
3. **经验判断**：维护者推荐、默认建议、经验排序；必须显式标成推荐，不得写成硬事实。
4. **证据不足**：影响主推荐结论时停下来问用户；不影响时标"不确定"或直接删。

## 同步文件

每次维护至少检查以下文件是否一起更新：

- `SKILL.md`
- `REFERENCE.md`
- `references/MAINTENANCE.md`（本文件）
- `CHANGELOG.md`
- `test-prompts.json`

## 更新流程

1. 扫当前会话可用项和本地安装项
2. 先修 P0：死 skill / 错默认路径 / 错归属
3. 再修 P1：过满措辞、把推荐写成事实、边界断言不稳
4. 最后修 P2：主文件过重、信息重复、规则散落
5. 抽查 `test-prompts.json`（跑子代理回归或 dry_run）
6. 记录 changelog（格式见 `CHANGELOG.md` 头部）

## 维护纪律

- 主语统一为 Claude Code 当前环境
- `SKILL.md` 不塞维护历史（历史只进 `CHANGELOG.md`）
- `REFERENCE.md` 不抢主文件路由职责（主文件定一句话路由，REFERENCE 放决策树细节）
- 看见死引用或错归属，当场修，不拖到下次
- 路由表条目删除必须引用真实误路由事故或官方变更证据（见 `SKILL.md` 文末路由表门禁），防无证据漂移
- 漂移维护规则（§6）是主要日常：拿 available skills 列表交叉核对 §1 表，逐项跑 §4 规则7 存在性校验

## 变更记录

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-07-22 | 新建本文件 | v1.3.0 四域路由统一补维护文档，对齐 ai-coding-guide/references/MAINTENANCE.md 模式 |
| 2026-07-24 | description 补「不用于」条款（v1.3.3） | guide-skill-auditor 十查 #3：v1.3.1 只补正文 §0 不用于，description 漏补；description 是路由唯一信号 |
| 2026-07-31 | v1.4.4：description 补 what 句「本 skill 是中文技术写作域开工路由器」 | guide-skill-auditor 组合审查 #1 FAIL（description 缺 what）；详见 CHANGELOG [v1.4.4] |
