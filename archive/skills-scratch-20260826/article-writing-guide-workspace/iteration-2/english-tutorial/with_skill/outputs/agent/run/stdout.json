按 article-writing-guide 完成开工路由判断，仅输出契约，不执行任务。

## 路由契约

**1. 分类**
- 跨阶段组合请求：英文单篇技术教程「起草」+「编辑」两阶段。
- 起草 = 从零单篇教程 → §1 ③（`article-writer` 默认通用模式，**非** `tutorial-maker`）。
- 编辑 = 结构调整/一般编辑 → §1 ④（`edit-article`）。
- 语言边界：英文文章 → 跳过 `human-writing` 与 `chinese-markdown-normalizer`（§0）。

**2. 主路径**
- `article-writer`（英文，默认模式）起草 Docker networking 教程。
- 然后 `edit-article` 做编辑。
- 教程裁决：「an English tutorial」是**单篇**非系列课，不转 `tutorial-maker`（那是对外系列/课程）；也未命中「自学边学边写」→ 不进 `learning-guide`。

**3. 组合（默认 pipeline 裁剪后）**
- 起草 `article-writer` → 编辑 `edit-article` →（可选）审校 `tech-article-review` 或 `multi-review-pipeline` →（若对外发布）`publish-final-check`。
- 可选配图：Docker networking 含网络拓扑图，`drawio-article-illustration` → `drawio-chart`。
- 查重 `plagiarism-audit`：需外部来源，无来源则跳过并标 `⚠️ 未查重`。

**4. 闸门（待确认项）**
- 触发门禁：article-writing-guide 相关 **YES**；`article-writer` / `edit-article` 均在本会话 ✓，可直接委派。
- 🔴 **CHECKPOINT**（§4 规则3）：跨阶段「写+编」→ 先确认跑**全链路** / 只起草 / 只编辑某层，不擅自定范围。
- 决策点先问（§4.5）：读者、目的、篇幅三要素未明确。
- 写作闸门（§0）：起草交付必须附**依据表 + basis map**（Docker networking 以官方文档为 evidence basis）。
- 写入闸门（§4 规则4）：先在对话给初稿预览，确认后才落盘。
- 「then edit it」未指明编辑层次（骨架/肉/皮）→ 按失败模式表先问。

**5. 下一步（等你确认后才动）**
- 请确认三点：① 范围（全链路 / 单点起草 / 单点编辑）；② 读者 + 目的 + 目标篇幅；③ 「edit it」指哪一层（结构调整 / 内容质量 / 纯文风）。
- 确认后：开工问询定归属（写作域默认我讲/协作流；你说「直接写」则降级我动手）→ `article-writer` 起草并给对话预览 → 确认落盘 → `edit-article`。

确认后我再开工。
