---
name: publish-final-check
description: Use when 用户要在中文技术文章发布前做最终把关，问“发布前过一遍”“能不能发了”“终检”“最后检查”“publish check”“发之前看下”“文章写完了”，或 article-writing-guide pipeline 进入末环；只出 PASS/FAIL 报告，不改文章。
---

# Publish Final Check（发布前强制关卡）

发布前最后一道闸。不审"写得好不好"（multi-review-pipeline/tech-article-review 的事），只审"**能不能发**"——有没有硬伤让你发出去后悔。

## 0. 定位与边界

| 项 | 本 skill | 其他 skill |
|----|---------|-----------|
| 目的 | 发布放行关卡 | 审校/改稿 |
| 输出 | PASS/FAIL + 必改清单 | 评审意见/改后文章 |
| 改不改 | **不改**，只报告 | 多维度改/逐段改 |
| 拦截 | MUST FAIL 强制拦 | 不拦，建议为主 |

**铁律**：只终检 + 出报告，不改文章。要改 → 委派 `multi-review-pipeline` 或对应 skill。

## 1. 输入

### 必给
- **成稿**：Markdown 文件路径（绝对路径）

### 查重子项必给
- **参考源**（三选一）：
  - URL 列表（如 `https://mp.weixin.qq.com/s/xxx`）
  - 本地文件路径（如 `docs/ai/rag/rag-basis.md`）
  - 粘贴文本片段
- 无参考源 → ① STOP，反问"请贴参考源，或明确声明无参考源"
- 用户明确"无参考源" → 跳过①，报告标 `⚠️ 未查重`

### 可选
- **目标平台**：公众号 / 博客 / docs/ai 投稿 → 决定④子项细化
- **JavaGuide 模式标记**：是 → ③对照 javaguide-style-guide 全套；否 → ③只跑 AI 味扫描

**输入样例**：
```
成稿：C:/ZYS/Code/JavaGuide/my-submission/todo/xxx.md
参考源：
  - https://xxx.com/article-a
  - docs/ai/agent/skills.md
目标平台：docs/ai 投稿
JavaGuide 模式：是
```

## 2. 四子项 checklist（可插拔数组）

每项：`{id, 级别, 子项, 检查内容, 执行, FAIL动作}`。增删项改本节数组，不改流程。

### 子项 ① 查重（只比贴源）

| 级别 | 检查内容 | 执行 | FAIL 动作 |
|------|---------|------|----------|
| MUST | 对照用户贴的参考源，无"原创措辞搬运"（比喻/结构/表达直接搬） | 委派 `plagiarism-audit`（**只比贴源，不主动搜全网**） | 列必改段 + 改写方向 |
| MUST | 区分"技术事实描述"（允许相似）vs"原创措辞搬运"（必改） | 同上 | 误判段标 ❓待人工 |
| SHOULD | JavaGuide 铁律"只可参考不可抄袭"——参考要点 OK，措辞/结构/举例必须原创 | 同上 | 警告 |

**无源处理**：MUST 无法执行 → ① STOP 反问；用户声明无源 → 跳过，标 `⚠️ 未查重`，不拦发布。

### 子项 ② 事实/链接校验

| 级别 | 检查内容 | 执行 | FAIL 动作 |
|------|---------|------|----------|
| MUST | 外链无死链 | 自检（能 HEAD/GET 则请求；沙箱无网络 → 标"待人工核"不 FAIL） | 列死链 + 替换/归档建议 |
| MUST | 图注编号与正文引用一致（图1/图2…） | 自检（grep 编号） | 列不一致处 |
| MUST | 代码块语言标签齐全（无裸 ``` 块） | 自检（grep） | 列裸块位置 |
| SHOULD | 关键版本号/依赖名/API 名准确（对照官方文档） | 委派 agent 查（无网则标待核） | 警告 + 给正确值 |
| SHOULD | 代码示例无明显语法/笔误 | 自检 | 警告 |

### 子项 ③ 风格/AI 味

| 级别 | 检查内容 | 执行 | FAIL 动作 |
|------|---------|------|----------|
| MUST | JavaGuide 模式：对照 `javaguide-style-guide` §1 M1-M10 MUST + §2 量化阈值逐条验 | 读 javaguide-style-guide，按 M1-M10 + 阈值表判定 | 列未达标项 + 阈值 |
| MUST | 无机器味收尾段（"本文介绍了...希望对大家有帮助"） | **自检**（关键词扫描：综上所述/总而言之/值得注意的是/本文介绍/希望对大家） | 列改写建议 |
| SHOULD | 禁 AI 味过渡词（首先/其次/由此可见/综上所述/总而言之/值得注意的是） | **自检**（grep 黑名单） | 警告 + 列位置 |
| SHOULD | 段落长短交错，无连续 3 段等长（字符数差 <30%） | 自检（按 javaguide-style-guide §2 阈值） | 警告 |

**注意**：③ **不委派 `human-writing`**——它是交互式多轮改写 skill，不适合"只扫不改"。AI 味用自检关键词黑名单（上两行），深度去 AI 味改写另起 human-writing。非 JavaGuide 文章跳过第一行，只跑后三行。

### 子项 ④ 发布面

| 级别 | 检查内容 | 执行 | FAIL 动作 |
|------|---------|------|----------|
| MUST | 标题存在且非空 | 自检 | FAIL |
| MUST | 无残留写作占位：grep `待实跑` / `待补` / `needs evidence` / `<!--发布前待补`，正文和注释块都扫 | 自检（grep） | 列位置；填实料或按占位预案压缩删除后重跑 |
| SHOULD | 有摘要/导语（首段或显式 description） | 自检 | 警告 |
| SHOULD | SEO：标题含核心关键词，正文 H2 含长尾 | 自检 | 警告 + 建议 |
| SHOULD | 封面图存在（公众号/博客发布时） | 自检 | 警告 |
| SHOULD | 公众号适配（目标=公众号 时）：代码块不超宽、图有 alt、无外链引流违规 | 自检 | 警告 |

## 3. 执行流程

```
1. 收成稿 + 参考源 + 目标平台 + JavaGuide 标记
2. 四子项并行执行（① 无源先 STOP 反问）
3. 聚合结果，按 MUST/SHOULD 分级
4. 出报告：
   - 任一 MUST FAIL → 🔴 FAIL + 必改清单
   - MUST 全 PASS，SHOULD 有 FAIL → 🟡 PASS WITH WARNINGS + 建议清单
   - 全 PASS → 🟢 PASS
5. 不自动改文章。用户拿报告决定改不改、用哪个 skill 改。
```

**并行失败兜底**：某子项执行 exception/超时 → 该子项标 `⚠️ 未完成（原因）`，**不阻塞其他子项**，报告注明"建议重跑该子项"。不因单点崩致全关卡失败。

## 4. 输出报告格式

```markdown
# Publish Final Check 报告

**文件**：xxx.md
**目标平台**：docs/ai 投稿
**JavaGuide 模式**：是
**结论**：🔴 FAIL / 🟡 PASS WITH WARNINGS / 🟢 PASS

## 必改清单（MUST）
- [ ] ①查重：第3段"XX比喻"与参考源 B 高度重合 → 改写方向：换比喻+加判断
- [ ] ②事实：第5行 https://... 待人工核（沙箱无网）
- [ ] ③风格：M5 量化工程感未达标（全文仅 1 处具体数字，需 ≥3）→ 补 P99/版本号
- [ ] ③风格：M9 收尾"综上所述"（AI 味词）→ 删或改判断句

## 建议清单（SHOULD）
- ⚠️ ③风格：S6 第2节连续 3 段等长 → 长短交错
- ⚠️ ④发布：标题缺核心关键词 → 建议含"RAG"

## 未查项
- ①查重：⚠️ 未查重（用户声明无参考源）
```

## 5. 委派规则（不重写）

- 查重 → `plagiarism-audit`（只比贴源，禁主动搜）
- 风格判定 → 读 `javaguide-style-guide` §1 M1-M10 + §2 阈值
- AI 味 → **自检关键词黑名单**（不委派 human-writing，交互式不适用）
- 链接/编号/标签 → 自检（grep/HEAD，无网标待核）
- 改文章 → 用户拿报告后另起 `multi-review-pipeline` 或对应 skill

## 6. 与审校 skill 区分

- `tech-article-review`（逐段审）/`multi-review-pipeline`（并行审+改） = **审 + 改**，发布前任意阶段用。
- 本 skill = **发布闸**，全链路最后一步，只放行不改。
- 典型顺序：`multi-review-pipeline`（改完）→ `chinese-markdown-normalizer`（排好版）→ **`publish-final-check`（放行）**。

## 7. 演进

- checklist 增删改 §2 数组即可。
- 演进记录入 `article-writing-guide/CHANGELOG.md`（本 skill 不另建 CHANGELOG，演进耦合在路由 skill 总日志）。
- 新增子项（如"国际化/无障碍"）→ 加子项 ⑤，不破坏流程。
- MUST/SHOULD 级别调整需在 CHANGELOG 说明理由。
- 版本：0.2.0（2026-06-12 修"柏验"错别字→查重、修 polisher 委派语义、加输入示例与失败兜底）。
