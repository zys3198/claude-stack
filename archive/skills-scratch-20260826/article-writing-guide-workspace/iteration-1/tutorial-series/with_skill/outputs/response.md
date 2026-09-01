触发门禁：

```
article-writing-guide 相关？ YES —— 请求是写作路由，且点名本 skill
目标 skill 在当前会话？ YES —— tutorial-maker 在 available skills 列表
若 NO → 最接近替代： （不适用）
```

---

## 五项路由契约

**分类**
写作域 · **起草-系统教程/课程（§1 表③）**——"系列教程 + 每课练习 + 折叠答案"是系列课形态，非单篇博客（不走 `article-writer`）、非选型/调研（不走 `lean-ctx`）。

**主路径**
`tutorial-maker` 🪨 —— §7 示例中「从零学 Redis 的系列教程」正是该表命中原话。
前置**教程裁决**：面向读者发布 → tutorial-maker；给自己学会 → 转介 `learning-guide`。

**组合**（跨阶段 → 触发 🔴 CHECKPOINT，先确认范围）
- 起草：`tutorial-maker`
- 审校：`tech-article-review`（逐段）或 `multi-review-pipeline`（多维度并行，二选一）
- 排版：`chinese-markdown-normalizer`
- 发布闸：`publish-final-check`（只放行不改）
- 配图（可选）：`drawio-article-illustration` → `drawio-chart`
- **「折叠答案」不入写作 pipeline**：属平台渲染特性，需平台记账——公众号不渲染 HTML 折叠，要提前定形式（`<details>` 折叠 vs 答案区放文末 vs 转 PNG）

**闸门**
1. 🔴 **CHECKPOINT**：跨阶段，先确认跑全链路 / 只起草 / 单点
2. **教程裁决**：对外发布 vs 自学（二选一决定 tutorial-maker / learning-guide）
3. **开工问询**（按序逐问）：归属（默认**我讲**协作流）→ 背景（读者 / 目标平台 / 总课时 / 单课练习形式与答案折叠方式）
4. **写入闸门**：先对话给骨架 + 每课初稿预览，确认后才落盘
5. **依据纪律**：Redis 命令行为以官方文档为权威证据，禁止凭记忆编造；练习答案必须可验证

**下一步**（不执行，仅收口）
回 3 个确认点即可开工：
1. 这套教程**对外发布**还是**给自己学会**？（裁决路由）
2. 目标平台是？（决定折叠答案的渲染形式）
3. 归属默认走**我讲（协作流）**——先结构方案 → 细骨架 → 冻结 → 逐课正文，可以吗？

确认后进入 `tutorial-maker` 起草。
