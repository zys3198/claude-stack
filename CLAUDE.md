# CLAUDE.md

## 0. 基本约定

**语言：**以中文回复。

**试验场：**`C:\ZYS\Code\lab-area`——专门试 skill/插件/hook/prompt，不污染其他项目。需要试验任何东西时去那里。

---

## 1. 代码改动全流程 [质量/安全]

### 1.0 项目定位

- 进入陌生项目或会话首个实质任务前，先 1-2 行明确「我的角色 + 这项目对我意义 + 当前目标」，写进 memory（user 类型）。主动问一句确认，不臆测。
- 重复项目/会话跳过。一次性脚本、临时查询、纯问答不触发（实质任务 = 产生代码改动/决策/交付物，排除读代码浏览/查资料）。

### 1.1 改前

- `git status` 干净才动手。脏工作区先处理，不叠加。
- 新建分支：`feat/<name>` / `fix/<issue>`。项目无 Git 则 `git init` + `.gitignore`（试验场 lab-area 例外：不强制 init，按需）。
- Plan 按不确定性和协同范围而非文件数：方案未知/架构决策/数据结构变动/多模块协同才 Plan（具体执行见 §3）；改动明确（bug 修复、加字段、机械重命名）直接改。出错（测试失败/lint error/用户否定当前方向/连续 2 次同类偏离验收）立刻切回重规划。
- **改动确认线**：动 ≥3 文件 / 跨多目录 / 改全局配置 / 不可逆操作前，先 1-2 行说明「改哪些文件+目标」，确认再动手。避免润色错文件 / 放错目录 / 范围漂移。机械重命名、单文件 bug 不触发。
- **喂富格式文档先抽文本**：Word/PPT/Excel/PDF 喂模型前转纯文本或 `.md`。docx→`pandoc`，PDF→`pdftotext`/pdfplumber，xlsx→openpyxl 抽结构化文本。排版标记吃 token 且无信息增益。
- **需求有歧义的大任务先问盲区**：>3 节任务且需求有歧义时，先一次一个问题问清关键假设再动手，省返工。明确改动、单文件、有标杆可照抄时不触发——别事事问。
- **反查真需求**：用户给的多是方案不是问题。信号=「实现 X」「加个 Y 字段」「做成 Z」而无痛点描述。动手前先问「为什么这么做？要解决什么场景？谁触发？」。常挖出更简解：能删/能复用/能不写。机械改动/明确 bug/已指名标杆文件不触发——别事事反问。
- **数据结构先于逻辑**：改功能/加字段先定数据结构、Schema、类型，再写逻辑。数据结构烂=代码全乱返工。AI 常先堆 if/else 后才凑结构，顺序反。

### 1.2 改中

- 若用户要求提交，一个逻辑变更一个 commit（conventional commits，指粒度非自动执行），方便 revert。执行仍受 §1.3 人工确认线约束。
- **标杆文件指名**：派活给 AI 必须指名参照项目里写得最好的范例文件，不写抽象规则。例："按 src/repositories/order_repository.py 的写法加 ProductRepository"。首次进入项目时，在 CLAUDE.md 或 memory 标出 5-10 个标杆文件（最佳 Route/Service/Repository/Model/Test）。LLM 复制具体范例比读抽象规则精确得多。
- **长任务落盘**：>3 节的任务（长文/课程/多文件重构）每节完成即 `Write` 到文件，对话只留指针。防 API 断连丢整段工作，断点可续。
- **故障对策清单**：新增外部调用/依赖/IO 时，必问失败对策——重试？超时？熔断？降级？限流？happy-path-only = 技术债。AI 常漏，写完主动 grep 新增的 `requests.`/`fetch`/`http.`/`connect`，确认每处有兜底。

### 1.3 改后

- 按 import 链推断受影响模块，跑 lint + test。方案未知/架构决策/多模块协同 → 见 §3 Agent 调度；机械重命名/明确改动走 §1.1 确认线即可。
- **字段对齐**：同一概念在 Spec→Prompt→验收标准→测试→代码 五环节用同一字段名。改完跑 import 链时顺手核对新增字段名与 Spec/接口契约一致，不一致即漂移，当场改。
- Bug 修复：先写 2-3 个失败测试重现 → 人工确认 → 改实现。至少列验收 checklist 贴结果。
- **AI 坏味道三查**（review AI 代码必查，任一命中即打回）：
  - 假绿测试：AI 为让测试过直接改断言逻辑（覆盖率 100% 但逻辑错）。查法：看测试是否真测业务行为，还是只凑绿。
  - 幻觉引用：引用不存在的 API/库/函数。查法：编译/类型检查先行（ruff/tsc/go build 等）+ grep 确认符号真实存在。
  - 幽灵代码：生成的函数/分支从没被调用。查法：grep 函数名确认有调用点，或靠 lint（ruff F841 / TS `noUnusedLocals` / pyflakes）报未使用。
- **注释只写 why 不写 what**：注释写代码无法表达的意图/决策/坑，不复述代码。废话注释（`# 循环用户`、`# 初始化变量`）删。显而易见的不注释。AI 高频犯：生成注释纯复述上一行代码。
- 性能优化：贴前后 SQL/EXPLAIN/P95。无实测写"待验证"。
- **人工确认线**：密钥修改/数据库迁移/文件删除/推送/commit——AI 不可自主执行。commit 前展示 `git diff --cached --stat`。

---

## 2. 调试工作流 [质量]

- DB 错误：命名列/表对照保留字列表检查（如 MySQL `window`）。冲突加反引号或改同义词。
- 本地开发 MySQL 连接失败/无服务 → SQLite 回退；生产环境禁。

---

## 3. Agent 调度 [质量]

本节只定义进入 Plan 后的拆解、agent 与 verify 规则。Plan 触发条件见 §1.1。

- 分解 4-6 独立切片，`PLAN.md` 协调（文件范围/API 契约/共享类型/验证命令）。Plan 审批通过后执行。
- 独立任务并行派 agent（code-reviewer/security-reviewer）。依赖任务串行。
- **先串行后并行**：同类型串行 2 次无回退（未触发 §4 止血/git revert）且 review 无业务 Bug/安全漏洞/数据丢失/架构违规后再启用并行。
- **Verify 分级**（按风险不按文件数）：
  - 低（机械/重命名/格式）→ 不 verify，`tsc` + lint + test 过即可。
  - 中（功能改动）→ 单 reviewer agent。
  - 高（auth/DB schema/架构/安全敏感）→ 三 agent adversarial（找问题/求证/反驳），2/3 通过。
- 全部完成后集成测试。
- **内置 agent**：`default`(通用兜底)/`worker`(执行修复)/`explorer`(只读探索)，需显式要求才 spawn，每个跑自己的模型+工具、更耗 token。subagent 继承当前 sandbox，审批请求看清是哪个 agent 发起。小改动（改 DTO 字段）别开多 agent，沟通成本 > 修改本身。
- **护栏靠 hooks 不靠自觉**：危险命令拦截（rm -rf / DROP TABLE / 密钥外泄）已由 ~/.claude/hooks 的 PreToolUse hooks 负责（见 §5 自定义 hook 备份），不靠"按场景授权"的人肉自觉。长链编排（>3 agent）用 PLAN.md 协调并设步数上限，超限即停，防 agent 无限烧。

---

## 4. 止血与回退 [安全/回滚]

触发：AI 改动引入错误。`git reset --hard` 仍需确认，其余不受人工确认线约束。

1. 停——不继续改。
2. `git diff` 定位，判断是逻辑错还是连锁反应。
3. 回退（按优先级）：`git restore` → `git revert` → `git reset --hard HEAD~N`。
4. 分析根因后重做。不在坏代码上打补丁。
5. **连续 2-3 轮同方向打转，别"再试试"**：让它复盘——已知什么/哪些假设被证伪/下一步缺什么证据。再卡换提示词：`Prove to me this works. Compare the diff against main and show the evidence.`（拿证据，不止结论）；第一版能跑但绕时用 `Knowing everything you know now, scrap this approach and propose the simpler implementation.`（让它重想收干净）。

---

## 5. 规则管理 [质量]

**放**：AI 反复犯的错。**不放**：已被 lint 强制的规则。
- hook 备份：`~/.claude/hooks/HOOKS_BACKUP.md`
- `CLAUDE.override.md`：临时覆盖用
- **GateGuard 拦非代码 Edit**：编辑 CLAUDE.md/.json 等配置被 Fact-Forcing Gate 拦时，声明「无代码 import/无公共函数/无数据文件读写」+ 引用户指令原文，重试即过。无需改 ECC_DISABLED_HOOKS。

---

## 6. 决策分层 [质量]

| 权限 | 范围 |
|------|------|
| 自主 | 代码风格、明显 bug、常规优化、类型定义 |
| 询问确认 | 技术选型、架构模式、命名 |
| 必须确认 | 技术栈变更、数据结构调整、关键业务分支 |

**默认技术栈**：前端任务默认 `shadcn/ui` + `npx shadcn@latest init`，不手动搭 UI 库；用户点名别的才换。

---

## 7. 上下文管理 & 防错闭环 [质量]

- 轮次 > 10 或连续 3 次 error → 提示用户压缩/`/compact`（AI 不能自触发）。
- 机械改动（重命名/单文件 bug/纯格式）→ 提示用户开新线程，不塞进已有长线程。
- Agent 犯新错误 → 写入 memory feedback（`~/.claude/projects/*/memory/`）。

---

## 8. MCP 接入 [质量/安全]

只读 MCP 默认接。写权限需单独审批。自建 MCP server 把用途写进 initialization `instructions`。

---

## 9. 平台 [质量]

- **Windows 11**。路径用 `pathlib`，命令通用于 Unix shell（容器/WSL）。平台特定代码加 `sys.platform == 'win32'` 注释。
- Symlink：Windows 下直接 copy，**不尝试 symlink**（常失败）。copy 也失败时报错，不静默跳过。
- PYTHONPATH：Windows 本地不设 PYTHONPATH（污染环境），需要时用 `python -c` 或 venv 隔离。
- 编码：文件读写强制 `encoding='utf-8'`；subprocess 输出加 `env={'PYTHONIOENCODING':'utf-8'}`（防 GBK 乱码）。
- Python 解释器用 `python312`。后台 MCP 用 `pythonw.exe` 免弹窗。
- Rust/编译工具链（MinGW64、MSVC）可能不可用。优先 pre-built 或 pip 安装。
- **Edit 预读只认原生 Read**：ctx_read 已读但 Edit 仍报「File has not been read」——ctx_read（MCP）不算。先原生 `Read` 再 Edit；ctx_edit 当前未装（ToolSearch 找不到），别指望。

---

## 10. 输出完整性 [强制]

长任务、完整文件、多组件交付前激活 `full-output-enforcement` skill。禁止占位符（`TODO`/`// ...`）、散文敷衍词（"for brevity"/"rest follows same pattern"）、结构偷工（骨架当完整实现）。规则细节以 skill 为准，不在此重复。
- 如果用户任务类型比较长、复杂，则使用下列提示词文件：
  @C:\Users\zys31\.claude\long-complex-task-prompt.md

---

## 11. 通用推理底线 [全局]

- 先给结论，再给关键依据；禁止结论前置、逻辑跳步、拍脑袋式判断。
- 先检查关键假设，再下判断；假设未证实要标风险点与影响。
- 事实判断优先依赖源码、官方文档、实测输出；证据不足必须明确写「不确定」与缺失证据。
- 对外只输出必要且可审计的推理产物：关键假设、证据、备选方案、排除依据、风险点、验证结果；不展开内部隐藏推理。
- 简单任务保持轻量，复杂任务再提升推理深度；优先收敛到可执行下一步，避免无意义穷举。

---

## 12. 证据门槛与内容来源 [强制]

回答确认性问题前查证据。确认性 = 有唯一可证伪答案的事实问题。
证据优先级：源码 > 官方文档 > 实测输出；第三方文章/博客不算决定性。
记忆默认 suspect。无证据/仅凭记忆 → 禁止确认，改去查。查不到 → 明说「不确定」。
用户质疑时不辩解不解释，贴更硬证据或承认不确定。
不适用：纯建议、风格选择、开放讨论。

涉及外部材料时先定来源：指定本地优先（禁网搜）、来源不明先问、不存在则明说缺失、本地优先于网搜。

---

## 13. 交互纪律

### 13.1 回复风格

- 探索性问题（怎么办/要不要/怎么想）→ 先 2-3 句给推荐 + 主要权衡，不直接实现。用户点头才动手。
- 直接问题直接答，不堆标题分节。
- 教程编写、学习内容编写、教学讲解 → 优先清晰和完整，不用 caveman 压缩表达；可适当展开，便于理解和学习。
- 动手前广播意图一句（门槛见 §1.1 确认线）；关键节点（发现/转向/卡点）一句简报；收尾 1-2 句（改了啥 + 下一步）。
- 引文件用 markdown 链接或 `path:line`，方便跳转。
- 不确定明说「不确定」（事实断言标准见 §12）。

### 13.2 任务跟踪

- 3+ 步任务 / 多文件改动 / 用户给编号清单 → `TaskCreate` 建任务，逐步标完成。
- 1-2 步、单文件、纯问答 → 不建。
- 开工即 `in_progress`，做完即 `completed`，不攒批。

---

<!-- CAVEMAN_START -->
## caveman 句型

句型=[事物][动作][原因]。[下一步]。`/caveman lite|full|ultra|wenyan` 切级，"normal mode" 关。
- 例外：教程编写、学习内容编写、教学讲解默认不用 caveman；以更完整、更易懂表达为先。

<!-- CAVEMAN_END -->

<!-- lean-ctx -->
<!-- lean-ctx-claude-v3 -->
## lean-ctx — Context Runtime

Always prefer lean-ctx MCP tools over native equivalents:
- `ctx_read` instead of `Read` / `cat` (cached, 10 modes, re-reads ~13 tokens)
- `ctx_shell` instead of `bash` / `Shell` (95+ compression patterns)
- `ctx_search` instead of `Grep` / `rg` (compact results)
- `ctx_tree` instead of `ls` / `find` (compact directory maps)
- Native Edit/StrReplace stay unchanged. If Edit requires Read and Read is unavailable, use `ctx_edit(path, old_string, new_string)` instead.
- Write, Delete, Glob — use normally.

Read modes: full (edit), map (overview), signatures (API), diff (post-edit), lines:N-M (range), auto.
Details live in the `lean-ctx` skill (loads on demand — keep this file lean).
<!-- /lean-ctx -->
