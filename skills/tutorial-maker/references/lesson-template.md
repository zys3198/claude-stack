# 每课生成规范

## 课文件骨架（写入 `lessons/NN-<slug>.md`）

```markdown
# 第 N 课：<标题>

> 学完你能：<可观测目标，如"能说出所有权解决的 3 个问题">
> 前置：第 X 课 / 无

## 是什么 · 为什么需要它
一句话核心结论 + 它解决什么真实痛点。拒绝学术黑话。

## 讲解
按四步认知策略（来自 cram-engine 思想）：
1. **concrete-first**：先上一个具体例子/场景，让读者有抓手。
2. **chunking**：把概念拆成 2-4 个小块，逐块讲。
3. **elaboration**：每块展开——为何这样、边界、和已知概念的关系。
4. **generation**：抛一个"猜一下/想想"的小钩子，引向练习。

术语首次出现：课内定义，并链接 `glossary.md#<term>`。

## 你来试
1-2 道练习，从课内可解。至少一题要求读者**产出**（写/预测/解释），非纯选择。

<details>
<summary>答案 / 自查</summary>

逐题给答案 + 一句话为什么。陷阱题额外揭晓陷阱逻辑。
</details>

## 小结
3 句话 recap + 下一节预告（为什么下一步需要它）。
```

## 节奏偏好（读 `progress.md`）

- 继续 → 正常节奏
- 加速 → 精简版，generation 步骤可略
- 减速 → 每块多配一个例子
- 跳过 → 停止生成，进自审门
- "再讲一遍" → 换例子/换角度重讲，不重复原话

## 超长处理

单课超过 ~600 行 → 触发 `full-output-enforcement` 检查无占位符；仍超 → 提示拆成两课，回 `curriculum.yaml` 加课再生成。

## 大纲生成（阶段1）

从 `intake.md` 的北极星 + 本地材料出发，拆成 stages → lessons：

1. 每课只讲 ONE THING（teach 思想）。
2. 线性序：按依赖排，前置课在前。
3. 标 `must_know`：核心路径上的课。
4. 每课写 `objective`（可观测）+ `source_refs`（溯到 sources.md 锚点）。
5. 展示总数 + must_know 分布，停在审批门。

审批门允许：回车全做 / "先攻 must_know" / 指定跳过编号 / 改大纲。移除 must_know 课先警告。

## 每课生成（阶段2）

1. 读 `curriculum.yaml` 找第一个 `status: pending` 课。
2. 读 `sources.md` 对应 `source_refs` 拉材料。
3. 按骨架生成，遵循节奏偏好。
4. 术语首次出现同步登记到 `glossary.md`。
5. 写入 `lessons/NN-<slug>.md`，status → `generating`。
6. 跑自审门（见 review-gate.md）。
7. 过 → status `done`；不过 → `blocked` + 自审未过清单。
8. 每生成 3 课 → [暂停点4] 节奏检查。

## 收尾（全部 done 后）

生成 `README.md`（面向谁 / 学习路径 / 前置 / 怎么用 / 课索引）+ 检查 `glossary.md` 完整。未过自审的课在 README 标注"待修订"。
