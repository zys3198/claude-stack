## 路由判断：**命中** guide-skill-auditor

**判断依据（§3 证据）**
- **审查对象判定**：learning-guide 是 router 型 guide skill——description 声明分发角色（「路由到 deep-learn、cram-engine 等」），正文按路由表分发下游，正是审计器定义的目标类型；「执行型 skill」才在范围外。
- **触发信号吻合**：用户点名的范畴词「等」就是十查第 3 项的 FAIL 判据；learning-guide 在审计器实证来源「本地四域」中（2026-08-07 踩坑实例）。
- 请求动作「审查 learning-guide」= 审计一个 router 型 guide 的 description+正文，无歧义。

**矛盾点（审计执行前必须先核实，不能直接下结论）**：审计器检查清单第 3 项证据记「learning-guide『路由到…等』2026-08-07 当日已修（v1.4.8）」，而你的描述仍含「等」——两者冲突。执行审计时需先读实际 SKILL.md 核实当前版本与 description 原文，再判 FAIL 与否（§3 证据门槛）。

## 命中后将执行的检查框架（本次不执行）

**第 0 步 定靶** — 读 learning-guide 全文+description，列声明域与兄弟域（deep-learn、cram-engine 及下游全表）。

**第 1 步 静态十查**（主疑点=第 3 项）：
1. description = what(角色定位) + when(触发词)，无流程摘要
2. 版本戳 `<!-- vX.Y.Z -->`
3. **「不用于」清单 + description 路由目标列表无范畴词** → 「路由到…等」的「等」= FAIL 条件
4. 触发门禁：3 行输出模板（YES/NO/fallback），位置在分类动作前
5. 路由表无范畴词兜底行 + 撞词行行内负向边界
6. 路由目标合法性：deep-learn、cram-engine 存在性 / 可直达性 / 归属（查会话列表→磁盘 `~/.claude/skills/`、plugins、cc-switch）
7. 默认值先于菜单 + 分支点问句化
8. 路由表门禁注释
9. 配套文件：test-prompts.json、CHANGELOG.md
10. 枚举信号表 + 低置信缺口清单

**第 2 步 动态基线** — description 含兄弟域高频词、路由表涉改 → **必跑**。造 3-5 边界场景：点名「用 deep-learn」、点名「cram-engine」、模糊学习请求、学习域边界外信号；派子代理裸跑（只给 description 不给正文）看第一跳，判 P0 误路由 / P0 幻觉 / 良性 fallback。子代理连挂 2 次→主会话人肉走查并落账标注。

**第 3 步 修复分级** — 若「等」字实锤且仅 description 列表部分 FAIL（「不用于」清单合规）→ **P1 本轮修**；若触发误路由实锤 → 升 P0 立即修。

**第 4 步 落账** — CHANGELOG 加版本条目 + MAINTENANCE 变更记录 + 未暴露缺陷区域注明「未动原因」。

**转介路径（不适用）**：仅当目标是执行型 skill 或非 router 型时转介；此处命中，无需转介。

下一步（2 分钟内可做）：确认后我读 learning-guide 实际文件，先核实 version 与 description 原文，解决上述矛盾点，再进入十查。
