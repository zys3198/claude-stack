**触发门禁**：article-writing-guide 相关？YES（你点名本 skill 定路由）。目标 skill 存在性：`tutorial-maker`、`learning-guide`、`article-writer`、`publish-final-check` 等均在本会话可用列表。YES。

---

**① 分类**
命中 §1 表「③ 起草-系统教程/课程」——"从零学 Redis + 系列教程 + 每课练习"。注意教程裁决：**面向读者发布** → `tutorial-maker`；**给自己学会/学习产物** → 转介 `learning-guide`。当前形态（系列课+练习+折叠答案）指向对外发布。

**② 主路径**
`tutorial-maker`（对外发布的系列教程/课程）。

**③ 组合**
- 前置：Redis 官方文档/权威资料收集（定版本基线、命令最新语义）→ `agent-reach` 或直取官方文档（轻量）
- 起草：`tutorial-maker` 落每课「讲解+练习+折叠答案」结构
- 审校：`tech-article-review`（逐课）或 `multi-review-pipeline`（全系列并行审）→ **`publish-final-check`**（发布闸，末环必跑）
- 排版/平台适配：`chinese-markdown-normalizer`；配图可选 `drawio-article-illustration`+`drawio-chart`

**④ 闸门**
1. **归属确认（首闸）**：对外发布 → tutorial-maker；自己学 → learning-guide。这是 §0 教程裁决的硬分流点
2. **骨架冻结**：先一次性出全系列 H2/H3 细骨架，冻结后才逐课生成正文
3. **写入闸门**：每课正文对话预览 → 用户确认 → 落盘
4. **平台渲染记账**：折叠答案若用 HTML `<details>/<summary>`，公众号不渲染 → 需先定目标平台
5. **版本锚定**：Redis 命令/配置随版本演进，大纲需锚定版本，避免教程写成过时事实

**⑤ 下一步**
先确认归属（面向读者发布 or 自己学）+ 目标平台 → 若对外发布，进 `tutorial-maker` 开工，第一产出为课程大纲方案（分几课、覆盖范围、每课练习设计原则）。

---

要我继续第 ⑤ 步——先确认归属和目标平台，还是直接进 `tutorial-maker` 出大纲？
