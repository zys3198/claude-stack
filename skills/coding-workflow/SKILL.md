---
name: coding-workflow
version: 1.9.0
description: 写功能、修 Bug、重构、审查 AI 代码或回退代码改动时使用。
---
# 编码工作流细则

CLAUDE.md §1 只保留路由与高代价确认线；本文件保留编码任务的执行、证据、容器和回退约束。小任务走最短路径，只有不确定性、架构/数据结构决策或多模块协同才进入 Plan。

## 1.0 编码硬约束

- 需要的库直接 import；出错处 fast-fail，异常向上抛。
- 回滚一律用文件编辑工具手动恢复，不用 Git 回滚。临时文件按 `CLAUDE.md` §8 的落点，不用 `/tmp`；大段脚本经 native Write 落盘，不做 shell 内联；成熟文件格式用现成 library 解析。
- 只改任务相关代码，不顺手重构、加抽象、加配置或处理无关死代码；每行改动都能追溯到用户要求。
- 不用 mock、假实现或 workaround 欺骗测试；实现后必须运行检查并迭代。Python 文件不加首行 docstring/shebang，注释用中文且只写 why。

## 本机执行与容器规则

构建、测试、安装依赖、跑脚本和起服务按 `docker-only` 执行；端口、独占资源、数据库目标和收尾按 [`references/worktree-and-resources.md`](references/worktree-and-resources.md) 核对。用户给出「启动本项目」「继续」等宽泛指令时，先查 `AGENTS.md`、`CLAUDE.md` 或 `README` 的 Commands 段；已有文档化流程就直接执行，没有才追问运行模式。

## 1.1 改前

- 多步或跨目录先逐项做环境预检：repo root、目标路径、文件编码、容器路径和复杂参数传递；每项只验证不执行，汇报 `root=… / 编码=utf-8 / 路径存在`，同方式连续失败两次即停。
- `git status` 干净才动手；项目已有分支约定优先。明确的小改动直接做，方案未知或协同复杂才 Plan；测试/lint 失败、方向被否定或连续两次偏离验收即重规划。
- 改动 ≥3 文件、跨目录、改全局配置或不可逆操作前，若用户尚未明确授权，先说明文件和目标并取得确认；已明确授权的范围直接执行，不重复询问；只读调查、范围定位和回退准备先完成，写入、外发、删除、提交、部署和权限变更按授权范围处理。
- 非平凡任务先读最小上下文，目标/约束/验收缺失先问；机械改动不反问。需求或架构未定时用 `mattpocock-skills:grilling` 澄清，并记录术语、决定和依据；在仓库内且要把结论落成 ADR 与术语表时，提示用户运行 `/mattpocock-skills:grill-with-docs`。区分 Prompt、Context、Harness，不让模型猜缺口。
- AI 负责整理、初稿、疑点和检查；人负责目标、边界、取舍和最终结论。安装任何依赖、Skill、插件、Agent、CLI 或 hook 前先确认全局/项目位置。
- 富格式文档先抽纯文本；外部调用/依赖/IO 写明重试、超时、熔断、降级或限流策略。

## 1.2 改中

- 计划沿用项目现有 workflow contract、规格和状态机；没有时只写最小计划。计划必须列「明确不做及理由」停止线、文件范围、验证方式和回退点；长任务每节落盘，数据结构/Schema/类型先于逻辑。
- 按接口归属实现，模块对外只暴露接口文件。提交只有用户明确要求时执行，一个逻辑变更一个 commit。

## 1.3 改后

- 按 import 链检查受影响模块，跑项目已有 lint/test/pre-commit；交付必须包含结果、改动范围、验证证据、未完成项和风险。
- 只构建通过只能说「构建通过」；功能通过必须有可重复的退出码、响应、日志或只读查询。字段在 Spec→Prompt→验收→测试→代码间保持一致；无实测写「待验证」。
- 自动检查优先于文字提醒；任务粒度服从反馈速率。Bug 先用 `mattpocock-skills:tdd` 或 `diagnosing-bugs` 建立失败证据，再经人工确认改实现并贴验收结果。性能结论附前后 SQL/EXPLAIN/P95，无实测标待验证。

## 1.3.1 验收相位

按独立相位执行：先写可观察的 QA 计划和预期，再由用户审计划与实现，照计划验收；发现问题登记为新工单，回执行相位修复。验收是否通过由用户拍板，Agent 不自宣通过。

## 1.4 AI 代码审查方法论

审查 AI 代码默认必审，先看测试再看代码；三维为正确性/边界、数据结构选型（无 benchmark 不下结论）、代码整洁度。审查范围、固定点、风险分级、报告顺序和 Agent 汇报核对清单见 [`references/code-review.md`](references/code-review.md)。

## 1.5 规范驱动产物

沿用宿主实际契约。需要规格时提示用户运行 `/mattpocock-skills:to-spec`；规划产物完成后标记完成，后续不把旧计划当现行指令。每条验收项必须一眼可判定。

## 1.5.1 深模块与接口归属

设计/重构模块形态时读 `mattpocock-skills:codebase-design`；要扫全库找深化点时提示用户运行 `/mattpocock-skills:improve-codebase-architecture`；接口归人、实现归 AI、测试负责诚实；一个模块一个目录。第一版跑通前不切模块——那时切是在猜。

## 1.5.2 新产品起步

产品意图用 `mattpocock-skills:grilling` 拷问清楚，落成项目根的 `PRODUCT.md`（意图、用户、首版范围、核心路径），后续每一步都读它；原型、规格、工单、实现分别走 `mattpocock-skills:prototype`、`to-spec`、`to-tickets`、`implement`，整条路线的入口是 `/mattpocock-skills:ask-matt`。

**视觉方向在写实现之前定**：出 2–3 套文字方向（气质、配色、排版、密度各一句）供用户选，选定的写进 `PRODUCT.md`。没有能点的原型、没有定下来的视觉方向就进实现，返工在实现阶段付，那里最贵。

验收通过后按 `mattpocock-skills:implement` 迭代，或交 `mattpocock-skills:handoff` 给另一个会话接手。

## 1.6 工作树与本地资源

一个任务一个工作树；并行写任务各自隔离；收工停进程、保留有改动的工作树并汇报分支/路径/未完成项。隔离、收尾、找回和功能分支归并见 [`references/worktree-and-resources.md`](references/worktree-and-resources.md)。

## 2. 调试工作流

数据库命名与保留字冲突先核对；本地 MySQL 无服务可回退 SQLite，生产环境禁止该回退。

## 3. Agent 调度

大型搜索、批量读取和互不依赖调查需要委派时按 `parallel-delegation`；编码切片、Verify 分级和实际 hooks 护栏见 [`references/agent-dispatch.md`](references/agent-dispatch.md)。

## 4. 止血与回退

AI 改动引入错误时停止继续改，用 `git diff` 定位并分析根因，按 §1.0 手动恢复后重新验证。连续 2–3 轮同方向失败时复盘已证伪假设并换方案。

版本和维护入口见 [`references/MAINTENANCE.md`](references/MAINTENANCE.md)；变更记录见 `~/.claude/docs/skills/coding-workflow/CHANGELOG.md`。
