# 参考文章目录

## 根目录：创作风格参考

根目录下的文章供 `article-writer` 学习叙事结构、排版和语气。

## good-samples/：低 AI 味范文

已验证的低 AI 味文章，`article-writer` 和 `humanizer` 共同引用。

文体分类：

| 文件 | 文体 | 参考要点 |
|------|------|---------|
| `internship-experience.md` | 面试指南 | 自然口语、建议递进、不报数不列表堆砌 |
| `mongodb-questions-01.md` | 技术面试题 | 问答节奏、概念解释不堆定义、引用官方文档但不照搬 |
| `mongodb-questions-02.md` | 技术面试题 | 索引类知识的场景化讲解，先说用途再说原理 |
| `mysql-questions-01.md` | 技术面试题 | 长文节奏控制、加粗精准、复杂概念分层拆解 |
| `project-experience-guide.md` | 面试指南 | 短篇幅高信息密度、每段只讲一件事 |
| `resume-guide.md` | 面试指南 | 结构化建议但不模板化、具体到可操作步骤 |

## 怎么让 AI 参考多篇文章

在 prompt 的"参考风格"字段，支持三种写法：

**单篇：**
```
参考风格：examples/good-samples/mysql-questions-01.md
```

**多篇：**
```
参考风格：examples/good-samples/internship-experience.md + examples/good-samples/resume-guide.md
```

**整个目录：**
```
参考风格：examples/good-samples/
```
AI 会读取目录下所有 `.md` 文件，综合学习多篇范文的文体特征。适合需要混合多种文体风格的场景（比如面试指南 + 技术讲解的组合）。

不指定参考风格时，AI 按默认写法输出，不主动读取范文。

## 维护说明

后续新增范文统一放到 `good-samples/`，`humanizer`（`~/.claude/skills/humanizer/examples` 和 `~/.codex/skills/humanizer/examples`）通过符号链接自动同步。
