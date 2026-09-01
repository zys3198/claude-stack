4 份文件已产出到 `docs/ai-context/`。梳理完成。

**产出结构**
```
docs/ai-context/
  CLAUDE.md        壳草稿（@AGENTS.md 导入 + Claude Code 特定内容）
  AGENTS.md        内容源草稿（知识索引 + 模块说明）
  analysis-report.md  分析报告（模块切分/真实链路/债务观察/待确认问题）
  modules/core-AGENTS.md  核心模块领域说明
```

**梳理出的关键事实（这是 AI 之前会「胡言乱语」的根源）**
- `src/main.go:2` 调用 `startServer()`，但全库无此函数定义 → 项目当前**无法编译**，README 声称的「HTTP 入口」跑不起来。
- `src/db.go` 的 `connect()`、`src/handler.go` 的 `handler()` 均无调用方，是死代码桩。
- README 与代码**脱节**：无 HTTP server（未导入 net/http）、无真实 DB、handler 返回固定字符串。

**已标注「未验证」（无负责人可问，按 skill 规则处理）**
- 运行意图类结论（`startServer` 是否本应存在、README 是否仍为目标、是否补全还是删桩）在 analysis-report.md §6 列为 4 个待确认问题。

**下一步（2 分钟内）**：请你确认 §6 问题清单（尤其 `startServer` 的去留），确认后我按你的判断更新草稿；或者直接按 §7 落地指引把 AGENTS.md / CLAUDE.md / src/AGENTS.md 移到实际位置。
