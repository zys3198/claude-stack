# 状态文件 Schema

四个文件在 `.tutorial-maker/`，是流水线脊柱。起步模板在 [templates/](../templates/)。

## intake.md

grill 式逐问访谈的产物。字段：

```markdown
## 主题
<一句话>

## 受众
- level: zero | beginner | mixed
- persona: <谁，从零到什么程度>
- assumed: <假设读者已具备的；from-zero = 空>

## 范围
- in scope: ...
- out of scope: ...

## 北极星
学完整套课，读者能 <可观测能力>。

## 约束
篇幅 / 风格 / 禁 jargon / 语气。

## 本地材料
见 sources.md。
```

intake 不足（受众/北极星空）→ 继续 grill，不进大纲生成。

## curriculum.yaml

流水线核心操作对象。

```yaml
topic: <主题>
audience:
  level: zero
  assumed: []
stages:
  - id: s1
    title: <阶段名>
    lessons:
      - id: "01"
        slug: <dash-case>
        title: <课标题>
        must_know: true
        prereq: []          # v1 线性，多为前一课；字段留 v2 DAG
        objective: <可观测，禁"理解">
        source_refs: [sources.md#<anchor>]
        status: pending      # pending | generating | done | blocked
        review: null         # 自审结果对象或 null
```

- `objective` 强制可观测。
- `source_refs` 是 §13 溯源锚点，指 sources.md 条目。
- 大纲审批门通过后才进生成；改大纲直接改此文件。

## sources.md

§13 防臆造的执行点。两类源 + gaps：

```markdown
## 本地材料（优先）
- [rust-book-4]: ./notes/rust-ch4.md — <一句话摘要>

## 命名权威源（v1 仅命名不抓取，v2 联网取 + citation）
- [git-docs]: https://git-scm.com/docs — Git 官方手册

## 溯源
- 所有权三规则 → [rust-book-4]
- commit 基本用法 → [git-docs]
- 生命周期标注 → 缺失

## gaps（v1 不补，明示缺失）
- 生命周期标注语法
```

- 每条事实溯到【本地材料】或【命名权威源】锚点，否则进 gaps。
- **本地材料优先**（§13）；无本地材料时，常识性事实溯到命名权威源，不进 gaps。
- 仅当某特定细节在本地材料和命名权威源都查不到（或 v1 权威源未抓取无法确认）才进 gaps。
- v1 **不联网抓取**：命名权威源只命名不读内容；缺特定细节就标 gaps，不臆造。gaps 清单是 v2 联网补查入口。
- 本地材料路径无效 → 标红警告，不阻塞。

## progress.md

resume 的唯一真相源。

```markdown
## 当前
<阶段> · 第 NN 课 <status>

## 课状态
- 01 done ✓
- 02 blocked（自审：练习答案可两种解读）
- 03 generating
- 04-12 pending

## 自审未过清单
- 02: <检查项> — <修复点> — 待 regen

## 节奏
作者 03 课后说"减速" → 每课多配一例

## regen 历史
- 02: regen 1 次（仍 blocked）
```

- 每次状态变更即更新（done/blocked/generating）。
- regen 次数计入，达 2 次仍 blocked → 标顽固点。
- `.old` 文件每课只留最近 1 份。
