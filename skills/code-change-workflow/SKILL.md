---
name: code-change-workflow
description: 代码改动全流程细则——改前/改中/改后清单、AI 代码审查方法论、调试工作流、Agent 调度与 Verify 分级、止血回退。当 ai-coding-guide 分类为「执行代码改动」、或用户直接要求改代码/修 bug/重构/审查 AI 代码/回退改动时加载。不用于：纯问答、文章写作、学习调研。
---

# 代码改动全流程细则

CLAUDE.md §1 只留路由与高代价确认线，本文件是完整流程。来源：CLAUDE.md 2026-07-29 瘦身迁出（§1.1-1.4 / §2 / §3 / §4 原文）。

## 1.1 改前

- `git status` 干净才动手。脏工作区先处理，不叠加。
- 新建分支：`feat/<name>` / `fix/<issue>`。项目无 Git 则 `git init` + `.gitignore`（试验场 lab-area 例外：不强制 init，按需）。
- Plan 按不确定性和协同范围而非文件数：方案未知/架构决策/数据结构变动/多模块协同才 Plan（具体执行见 §3）；改动明确（bug 修复、加字段、机械重命名）直接改。出错（测试失败/lint error/用户否定当前方向/连续 2 次同类偏离验收）立刻切回重规划。
- **改动确认线**：动 ≥3 文件 / 跨多目录 / 改全局配置 / 不可逆操作前，先 1-2 行说明「改哪些文件+目标」，确认再动手。避免润色错文件 / 放错目录 / 范围漂移。机械重命名、单文件 bug 不触发。
- **喂富格式文档先抽文本**：Word/PPT/Excel/PDF 喂模型前转纯文本或 `.md`。docx→`pandoc`，PDF→`pdftotext`/pdfplumber，xlsx→openpyxl 抽结构化文本。排版标记吃 token 且无信息增益。
- **需求有歧义的大任务先问盲区**：>3 节任务且需求有歧义时，先一次一个问题问清关键假设再动手，省返工。明确改动、单文件、有标杆可照抄时不触发。
- **反查真需求**：用户给的多是方案不是问题。信号=「实现 X」「加个 Y 字段」「做成 Z」而无痛点描述。动手前先问「为什么这么做？要解决什么场景？谁触发？」。常挖出更简解：能删/能复用/能不写。机械改动/明确 bug/已指名标杆文件不触发——别事事反问。
- **动手前先判级**：任务按「信息在不在手里 × 有没意识到」判四级——已知的已知（直接干）/ 已知的未知（主动抛问，结尾要「给出推理思路」）/ 未知的已知（团队约定、历史包袱——先让 AI 采访挖出来，事故主源）/ 未知的未知（先采访扫盲再进方案设计）。判了级按级出牌；判未知的未知却直接让 AI 出方案 = 没判。完整流程与反考见 `expose-unknowns` skill。
- **数据结构先于逻辑**：改功能/加字段先定数据结构、Schema、类型，再写逻辑。数据结构烂=代码全乱返工。AI 常先堆 if/else 后才凑结构，顺序反。
- **安装位置先问**：装任何东西（pip/npm 包、skill、plugin、agent、CLI 工具、hook）前，强制先问「装全局还是项目本地？装哪个目录？」，确认再装。默认不装全局（污染共享 namespace、影响所有项目），除非用户明说"装全局"。全局 = `~/.claude/`（plugins/agents/skills）、`pip --user`、`npm -g`、系统级；项目本地 = venv/node_modules/项目 `.claude/`。用户说"装一下 X"≠ 装全局——先问位置。

## 1.2 改中

- 若用户要求提交，一个逻辑变更一个 commit（conventional commits，指粒度非自动执行），方便 revert。执行仍受人工确认线约束。
- **标杆文件指名**：派活给 AI 必须指名参照项目里写得最好的范例文件，不写抽象规则。例："按 src/repositories/order_repository.py 的写法加 ProductRepository"。首次进入项目时，在 CLAUDE.md 或 memory 标出 5-10 个标杆文件（最佳 Route/Service/Repository/Model/Test）。LLM 复制具体范例比读抽象规则精确得多。
- **长任务落盘**：>3 节的任务（长文/课程/多文件重构）每节完成即 `Write` 到文件，对话只留指针。防 API 断连丢整段工作，断点可续。
- **故障对策清单**：新增外部调用/依赖/IO 时，必问失败对策——重试？超时？熔断？降级？限流？happy-path-only = 技术债。AI 常漏，写完主动 grep 新增的 `requests.`/`fetch`/`http.`/`connect`，确认每处有兜底。

## 1.3 改后

- 按 import 链推断受影响模块，跑 lint + test。方案未知/架构决策/多模块协同 → 见 §3 Agent 调度；机械重命名/明确改动走 §1.1 确认线即可。
- **字段对齐**：同一概念在 Spec→Prompt→验收标准→测试→代码 五环节用同一字段名。改完跑 import 链时顺手核对新增字段名与 Spec/接口契约一致，不一致即漂移，当场改。
- Bug 修复：先写 2-3 个失败测试重现 → 人工确认 → 改实现。至少列验收 checklist 贴结果。
- **AI 坏味道三查**（review AI 代码必查，任一命中即打回）：
  - 假绿测试：AI 为让测试过直接改断言逻辑（覆盖率 100% 但逻辑错）。查法：看测试是否真测业务行为，还是只凑绿。
  - 幻觉引用：引用不存在的 API/库/函数。查法：编译/类型检查先行（ruff/tsc/go build 等）+ grep 确认符号真实存在。
  - 幽灵代码：生成的函数/分支从没被调用。查法：grep 函数名确认有调用点，或靠 lint（ruff F841 / TS `noUnusedLocals` / pyflakes）报未使用。
- **注释只写 why 不写 what**：注释写代码无法表达的意图/决策/坑，不复述代码。废话注释（`# 循环用户`、`# 初始化变量`）删。显而易见的不注释。AI 高频犯：生成注释纯复述上一行代码。
- 性能优化：贴前后 SQL/EXPLAIN/P95。无实测写"待验证"。

## 1.4 AI 代码审查方法论

适用范围：AI 生成的代码（含 learning 模式骨架、vibe coding 产出、agent 批量改）。**AI 代码默认必审**，无「小到不用审」豁免——一行配置可搞挂整站。AI 擅长写「语法漂亮、逻辑自洽、语义错误」的代码，读着顺 ≠ 对。

**审查强度复用 §3 Verify 分级**：高（auth/DB schema/架构/安全）→ 三 agent adversarial 或 `ecc:santa-loop` 双审；中（功能改动）→ 单 reviewer + 自检；低（机械/重命名）→ 不额外 verify，走 tsc+lint+test。
**学习价值补充**：值得学的框架/工程代码，§3 高风险分支触发「亲自逐行 cr 一遍再合入」；纯业务/一次性脚本走 §3 常规分级。

**审查三维（必查）：**
1. **正确性与边界**：空集合/重复元素/类型不符/超阈值等边界走没走对路径。
2. **数据结构选型**：底层结构选对否？位宽是否按需升级？dict vs map vs 数组取舍有无数据支撑？**无 benchmark 不下选型结论**。
3. **代码整洁度**：封装语义化、注释到位（why not what）、clean code。

**审查动作清单**（与 §1.3 三查互补，三查已覆盖项不重复列出）：
- 关键设计决策有压测/benchmark 数据支撑（无数据 → 不接受结论，让 AI 跑）；边界条件（空集/重复/类型不符/超阈值）走代码路径核对一遍；底层结构选型与「为何不选另一种」能讲清（dict vs map、intset vs 数组等）
- 审查报告输出走输出完整性约束（见 CLAUDE.md §10）

**沟通技巧**：抛见解 + 问 AI「你的看法」；让 AI 用压测/可运行代码印证假设，不接受「应该/可能/大概」；自己先读先怀疑，再让 AI 印证。

**权限归属：** 单 reviewer = 询问确认；三 agent 对抗 = 必须确认。

**反模式**：「读着顺 → 合入」（AI 最擅长「看起来对」）；「AI 自己 review 自己」（无对照基线）；「靠 harness 自动验收代替人工闸门」。

## 2. 调试工作流

- DB 错误：命名列/表对照保留字列表检查（如 MySQL `window`）。冲突加反引号或改同义词。
- 本地开发 MySQL 连接失败/无服务 → SQLite 回退；生产环境禁。

## 3. Agent 调度

本节只定义进入 Plan 后的拆解、agent 与 verify 规则。Plan 触发条件见 §1.1。

- 分解 4-6 独立切片，`PLAN.md` 协调（文件范围/API 契约/共享类型/验证命令）。Plan 审批通过后执行。
- 独立任务并行派 agent（code-reviewer/security-reviewer）。依赖任务串行。
- **先串行后并行**：同类型串行 2 次无回退（未触发 §4 止血/git revert）且 review 无业务 Bug/安全漏洞/数据丢失/架构违规后再启用并行。
- **Verify 分级**（按风险不按文件数）：
  - 低（机械/重命名/格式）→ 不 verify，`tsc` + lint + test 过即可。
  - 中（功能改动）→ 单 reviewer agent。
  - 高（auth/DB schema/架构/安全敏感）→ 三 agent adversarial（找问题/求证/反驳），2/3 通过。
- 全部完成后集成测试。
- **Agent 使用**：subagent 跑自己模型+工具、更耗 token、继承当前 sandbox——审批请求看清是哪个 agent 发起。小改动（改 DTO 字段）别开多 agent，沟通成本 > 修改本身。只读探索用 `Explore`，通用多步用 `general-purpose`。
- **护栏靠 hooks 不靠自觉**：危险命令拦截（rm -rf / DROP TABLE / 密钥外泄）已由 ~/.claude/hooks 的 PreToolUse hooks 负责（见 ~/.claude/hooks/HOOKS_BACKUP.md），不靠"按场景授权"的人肉自觉。长链编排（>3 agent）用 PLAN.md 协调并设步数上限，超限即停，防 agent 无限烧。

## 4. 止血与回退

触发：AI 改动引入错误。`git reset --hard` 仍需确认，其余不受人工确认线约束。

1. 停——不继续改。
2. `git diff` 定位，判断是逻辑错还是连锁反应。
3. 回退（按优先级）：`git restore` → `git revert` → `git reset --hard HEAD~N`。
4. 分析根因后重做。不在坏代码上打补丁。
5. **连续 2-3 轮同方向打转，别"再试试"**：让它复盘——已知什么/哪些假设被证伪/下一步缺什么证据。再卡换提示词：`Prove to me this works. Compare the diff against main and show the evidence.`（拿证据，不止结论）；第一版能跑但绕时用 `Knowing everything you know now, scrap this approach and propose the simpler implementation.`（让它重想收干净）。
