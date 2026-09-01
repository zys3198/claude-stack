按 article-writing-guide 做路由判断，仅输出契约，不执行任务。

---

## 开工路由判断

### 触发门禁（§0）
```
article-writing-guide 相关？ YES —— 写作需求未点名有效 skill
目标 skill 在当前会话？ javaguide-writer：NO（已删除）
若 NO → 最接近替代： article-writer（JavaGuide 模式）
```

### ① 分类
**起草-从零 + JavaGuide 模式**。你点名 `javaguide-writer` 属废弃 skill（功能已并入 `article-writer`），按 §0 废弃重定向切 JavaGuide 模式，不路由进虚空。

### ② 主路径
`article-writer`（**JavaGuide 模式**，执行规范见其 §6，含 §6.7 自检、§6.9 反例 11 条）。

### ③ 组合
JavaGuide 模式 pipeline（§3）：`article-writer`(JavaGuide 模式) → `multi-review-pipeline`(审校) → `plagiarism-audit`(查重，需贴源否则跳过) → `chinese-markdown-normalizer`(排版) → **`publish-final-check`**(发布闸，其 ③ 风格子项对照 `javaguide-style-guide` §1 M1-M10)。

### ④ 闸门（按顺序触发）
1. **触发门禁**：已过，javaguide-writer → article-writer JavaGuide 模式。
2. **开工问询**（§0）：先问「归属」——想练写作核心→你练 / 协作流（AI 给结构你定，写作域默认）→我讲 / 一次性文案→我动手；再问背景（给谁看/目的/篇幅/参考文章）。
3. **决策点先问**（§4.5）：文体（面试题解？专题讲解？）、读者（求职者/工作经验）、目的三要素，当前不全，须先问清。
4. **协作流默认**（§3）：写作域默认我讲（协作流）——结构方案 → 方向确认 → 全篇细骨架冻结 → 逐节初稿预览 → 确认后落盘。你说「直接写」才降级我动手。
5. **写作纪律**（强制）：正文预览须随附**依据表 + basis map**，依据缺失标 `needs evidence`。
6. **写入闸门**（§4）：初稿先对话预览，你明确确认后才落盘。
7. **跨阶段 CHECKPOINT**（§3 🔴）：若一次跑全链路（写+审+发），先确认范围。

### ⑤ 下一步
等你三件事后我才开工：
1. **归属**选哪个（推荐：我讲/协作流，面试文章适合先定结构再写）；
2. **背景**：读者水平、目的（面试冲刺/系统复习）、篇幅、有无参考；
3. **范围**：只起草，还是写+审+发布前检查全链路。

确认后我会用 `article-writer` JavaGuide 模式先出结构方案，不直接写正文。
