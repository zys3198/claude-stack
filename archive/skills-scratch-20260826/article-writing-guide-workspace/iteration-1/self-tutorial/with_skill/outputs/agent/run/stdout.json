**触发门禁**
```
article-writing-guide 相关？ YES —— 教程类写作需求，未点名具体 skill
目标 skill 在当前会话？ YES —— learning-guide / agent-reach / edit-article / article-writer 均在列
```

---

## 路由契约

**① 分类**
学习产物教程 + 边学边写。「给自己」三个字命中教程裁决线：**「给自己学会/作为学习产物」→ learning-guide；「面向读者发布」→ tutorial-maker**。故排除 tutorial-maker，主路径归 learning-guide，article-writing-guide 仅作写作域下游承接。

**② 主路径**
`learning-guide` 定学习路径（§3 边学边写「主路径归口」规则：先入 learning-guide 取主路径，写作域作下游执行承接，不重复展开）。

**③ 组合**
```
learning-guide（学习路径/心智模型）
  → agent-reach（收集 Java 权威材料：Oracle 官方文档、JavaGuide 等）
  → 对话中给增量初稿（不落盘）
  → 用户确认 → edit-article 落盘（无现稿则 article-writer 起草）
  → 审校 → 排版 →（如发布才跑 publish-final-check）
```

**④ 闸门**
- **写入闸门**：先对话预览增量初稿，明确确认后才落盘
- **写作纪律**：随预览交付依据表 + basis map，缺失标 `needs evidence`，不装成事实
- **信息价值过滤器**：只留「改变行为 / 反直觉 / 高频门槛 / 支撑主线」四类，砍掉查文档 30 秒可得的内容
- **JavaGuide 模式开关**：主题是 Java，如对齐 JavaGuide 风格可切（但主路径仍归 learning-guide）

**⑤ 下一步**
只做一次开工问询（一次一问，带推荐答案）：
- **归属**：推荐「我讲」协作流——我定学习路径结构、你边学边确认；想练学习组织能力可升「你练」。
- 再确认范围：完整边学边写链路，还是先只出 Java 学习路径。

要往下走，先回答一个问题：**这套教程最终是自己内化用，还是可能发布分享？** —— 决定要不要在链路末尾挂上发布闸。
