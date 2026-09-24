# 调用模板

用户手动敲这个 skill 时可以粘贴的提示词。原文整段搬自 `SKILL.md`。

## 默认模式

**创作：**
```text
请使用 article-writer skill 创作一篇关于 <主题> 的深度文章。
主题：<文章主题>
目标文体：<博客/技术方案/论文摘要/教程/测评/知识库面试题/工具推荐/面经/指南>
```

**优化：**
```text
请使用 article-writer skill 帮我优化/改写这篇文章。
素材来源：<粘贴内容或提供路径>
目标文体：<保持原文文体/改成XX文体>
优化重点：<加深技术深度/改善逻辑结构/去除AI味>
```

## JavaGuide 模式

**创作：**
```text
请使用 article-writer skill（JavaGuide 模式）创作一篇 JavaGuide AI 系列文章。
主题：<文章主题>
目标目录：<如 docs/ai/agent/xxx.md>
```

**优化：**
```text
请使用 article-writer skill（JavaGuide 模式）帮我优化这篇文章。
素材来源：<粘贴内容或提供路径>
```
