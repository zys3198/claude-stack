门禁先过一下：

```
域归属： 编码（指南维护）—— 交付物是 learning-guide 的审计结论+文件修改，不是学习成果/教程 → 不进学习域，不转介 learning-guide
ai-coding-guide 在当前会话？ YES
若域归属非编码 → 转介对应 router，不进 Step 1
```

注意一个关键区分：对象是 `learning-guide`，但**任务性质**是"审查+优化一个路由 skill"（Step 1 明确命中「审查/优化 guide skill → 路由指南维护」），不是去做学习任务，所以不落在学习域。

---

## 路由契约

**分类：** 路由指南维护

**主路径：** `guide-skill-auditor`（十查 + 基线测试 + 分级修复；当前会话直达，已验证在可调用清单中）

**组合：** `darwin-skill`（行为变化或量化优化时，当前会话可见）——用户说"顺便优化"，若审查发现行为/路由规则需要变更就上；纯缺陷小修则不必。不需横切 verify（非产品代码），不需 code-review agent。

**闸门：**
- 审计闸门：`guide-skill-auditor` 十查 + 基线测试（改前跑基线、改后重跑）
- 人工确认线：改动 ≥3 文件前，先列「改哪些文件 + 目标」确认（learning-guide 目录含 SKILL.md / references / test-prompts.json 等，很可能触发；CLAUDE.md §1.3）
- 复核：改动后跑审计验证 + 若属 ai-coding-guide 进化机制需同步变更记录

**下一步：** 问 1 个关键问题收口——**本次范围是「只出审计结论」还是「审计 + 落地修改」**（skill 内定的 AskUserQuestion：A 只评估给结论 / B 完整评估后改 / C 只给方案不改文件）。你确认后我再走 `guide-skill-auditor`，本次不做任何审查或改动。
