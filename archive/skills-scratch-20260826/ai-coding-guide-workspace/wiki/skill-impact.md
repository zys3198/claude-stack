# Skill impact log

## 2026-08-31T07:26:55Z

- Candidate: `ai-coding-guide/2.4.0`
- Verdict: `accept`
- Applied: `false`
- Reason: all gates passed
- Gate result:
```json
{
  "at": "2026-08-31T07:26:55Z",
  "verdict": "accept",
  "applied": false,
  "baseline": 0.5,
  "candidate": 0.75,
  "checks": {
    "score_improved": true,
    "target": true,
    "guardrail": true,
    "holdout": true,
    "content": true,
    "base_match": true
  },
  "passed": true
}
```
- Skill diff:
```diff
--- active/ai-coding-guide/SKILL.md
+++ candidate/ai-coding-guide/2.4.0/SKILL.md
@@ -22,6 +22,15 @@
 - **model-invoked**：`prototype`、`diagnosing-bugs`、`research`、`tdd`、`domain-modeling`、`codebase-design`、`code-review`、`resolving-merge-conflicts`、`wizard`、`grilling`、`writing-for-agents`。模型可按任务自动调用；路由仍必须显示对应手动命令，用户明确想自己调用时才等待。
 - user-invoked skill 可以驱动 model-invoked skill，但不能自动调用另一个 user-invoked skill；本路由不把一串 Matt skill 静默展开。主流程由用户逐个手动推进：`/grill-with-docs` → `/to-spec` →（跨会话/并行/多人/需显式阻塞时 `/to-tickets`）→ `/implement`。各入口内部可按规则驱动 model-invoked skill；`implement` 在预先约定的 seam 按需驱动 `/tdd`，提交前必须完成 `/code-review`。
 - `implement` 的原始 skill 要求 commit；本地规则优先，commit 前仍必须展示范围和 `git diff --cached --stat`，得到用户确认后才能提交。
+
+## 路由输出硬约束
+
+路由请求先给最简可审计契约：`分类`、`主路径`、`组合`、`闸门`、`下一步`；按条件追加 `参与度` 与 `Matt提示`。
+
+- `分类` 使用 `references/routing.md` 标准分类原名，不用泛化标签替代。
+- 代码理解涉及调用链、影响范围或“谁调用谁”时，优先 `gitnexus`；不可用才回退 `lean-ctx`。
+- 路由指南维护主路径为 `guide-skill-auditor`；行为变化先补可验证 `eval`，再改正文。
+- 进入交付状态机时明确 `small/medium/large` 档位，未指定则提醒可选择或说明自判 `small`。
 
 ## 必须执行
```
## 2026-08-31T07:29:51Z

- Candidate: `ai-coding-guide/2.4.0`
- Verdict: `accept`
- Applied: `true`
- Reason: all gates passed
- Gate result:
```json
{
  "at": "2026-08-31T07:29:51Z",
  "verdict": "accept",
  "applied": true,
  "baseline": 0.5,
  "candidate": 0.75,
  "checks": {
    "score_improved": true,
    "target": true,
    "guardrail": true,
    "holdout": true,
    "content": true,
    "base_match": true
  },
  "passed": true
}
```
- Skill diff:
```diff
--- active/ai-coding-guide/SKILL.md
+++ candidate/ai-coding-guide/2.4.0/SKILL.md
@@ -22,6 +22,15 @@
 - **model-invoked**：`prototype`、`diagnosing-bugs`、`research`、`tdd`、`domain-modeling`、`codebase-design`、`code-review`、`resolving-merge-conflicts`、`wizard`、`grilling`、`writing-for-agents`。模型可按任务自动调用；路由仍必须显示对应手动命令，用户明确想自己调用时才等待。
 - user-invoked skill 可以驱动 model-invoked skill，但不能自动调用另一个 user-invoked skill；本路由不把一串 Matt skill 静默展开。主流程由用户逐个手动推进：`/grill-with-docs` → `/to-spec` →（跨会话/并行/多人/需显式阻塞时 `/to-tickets`）→ `/implement`。各入口内部可按规则驱动 model-invoked skill；`implement` 在预先约定的 seam 按需驱动 `/tdd`，提交前必须完成 `/code-review`。
 - `implement` 的原始 skill 要求 commit；本地规则优先，commit 前仍必须展示范围和 `git diff --cached --stat`，得到用户确认后才能提交。
+
+## 路由输出硬约束
+
+路由请求先给最简可审计契约：`分类`、`主路径`、`组合`、`闸门`、`下一步`；按条件追加 `参与度` 与 `Matt提示`。
+
+- `分类` 使用 `references/routing.md` 标准分类原名，不用泛化标签替代。
+- 代码理解涉及调用链、影响范围或“谁调用谁”时，优先 `gitnexus`；不可用才回退 `lean-ctx`。
+- 路由指南维护主路径为 `guide-skill-auditor`；行为变化先补可验证 `eval`，再改正文。
+- 进入交付状态机时明确 `small/medium/large` 档位，未指定则提醒可选择或说明自判 `small`。
 
 ## 必须执行
```
## 2026-08-31T08:34:44Z

- Candidate: `ai-coding-guide/2.4.1`
- Verdict: `reject`
- Applied: `false`
- Reason: failed: score_improved
- Gate result:
```json
{
  "at": "2026-08-31T08:34:44Z",
  "verdict": "reject",
  "applied": false,
  "baseline": 0.8,
  "candidate": 0.8,
  "checks": {
    "score_improved": false,
    "target": true,
    "guardrail": true,
    "holdout": true,
    "content": true,
    "base_match": true
  },
  "passed": false
}
```
- Skill diff:
```diff
--- active/ai-coding-guide/SKILL.md
+++ candidate/ai-coding-guide/2.4.1/SKILL.md
@@ -6,7 +6,7 @@
   routing, or needs structured, resumable, multi-stage delivery (or to resume an
   existing workflow). 本 skill 是 Claude Code
   编码域总入口路由器，负责编码任务与前端视觉请求的开工分诊和路径选择。中文触发：用哪个工具、X和Y区别/冲突吗、该用什么、怎么配合、哪个更好、刚装了X插件、X不能用了、重任务跨会话/分阶段交付、继续之前的任务、断点续跑、这篇文章/做法能不能优化进路由；页面/界面/UI/落地页/登录页的视觉方向与实现也走本路由（前端视觉子路径）。不用于：中文技术文章写改审（走
-  article-writing-guide）、学习调研（走 learning-guide）。<!-- v2.3.0 -->
+  article-writing-guide）、学习调研（走 learning-guide）。<!-- v2.4.1 -->
 ---
 # ai-coding-guide（编码域总入口系统）
 
@@ -28,7 +28,7 @@
 路由请求先给最简可审计契约：`分类`、`主路径`、`组合`、`闸门`、`下一步`；按条件追加 `参与度` 与 `Matt提示`。
 
 - `分类` 使用 `references/routing.md` 标准分类原名，不用泛化标签替代。
-- 代码理解涉及调用链、影响范围或“谁调用谁”时，优先 `gitnexus`；不可用才回退 `lean-ctx`。
+- 代码理解日常结构先用 `lean-ctx`；涉及调用链、影响范围或“谁调用谁”时用 `gitnexus-exploring`；同时问结构和调用链时按 `lean-ctx` → `gitnexus-exploring`；`gitnexus` 不可用才回退 `lean-ctx`。
 - 路由指南维护主路径为 `guide-skill-auditor`；行为变化先补可验证 `eval`，再改正文。
 - 进入交付状态机时明确 `small/medium/large` 档位，未指定则提醒可选择或说明自判 `small`。
```
