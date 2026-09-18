# 会话生命周期机制 —— 审计接手文档

下个会话的任务：对这套机制做多维度审计与体检。**只审计，先不改**——结论先给我看。

---

## 一、先读什么

不要从这份文档了解机制行为，去读原始件：

| 想知道 | 读 |
|--------|-----|
| 机制做什么、怎么用、故障处理 | `~/.claude/docs/session-lifecycle.md` |
| 规则文本（每次会话都加载） | `~/.claude/CLAUDE.md` 第 8 节，18 行 |
| 安装台账、设计取舍、删除安全边界、回退方式 | `~/.claude/installing/custom-setup.md` 的「会话生命周期机制」一节 |
| 实现 | `~/.claude/hooks/scripts/` 下三个脚本 |
| 用例与预期行为 | `~/.claude/hooks/scripts/selftest.py`，69 个用例 |
| 改动历史 | `~/.claude` 仓库提交 `39ca46b`、`d8f1e74`、`5b4a138` |

---

## 二、这套机制是什么

三个 hook 挂在 `~/.claude/settings.json`（用户级，所有项目生效）：

- **SessionStart** → `session-guard.py start`：报告当前仓库卫生状况，干净时静默
- **SessionEnd** → `session-guard.py end`：往 `~/.claude/session-handoff.jsonl` 写收尾记录
- **PreToolUse**（matcher `Bash|EnterWorktree`）→ `product-guard.py`：拦截越界或 hash 命名的工作树创建

两个手动命令：`/dev-status`（只读总览）、`/dev-clean`（逐条确认后清理）。

**核心设计承诺：机制自身不删除任何东西。** 三个脚本里没有任何删除调用，唯一出现 `git worktree remove` 的地方是 `dev-clean.md` 的指令文本。

---

## 三、当前状态（2026-09-18 实测）

**仓库侧**（`~/.claude`，分支 `main`，远程 `claude-stack`）：

- 三个提交 `39ca46b` / `d8f1e74` / `5b4a138` **未推送**
- 机制相关文件全部已提交，工作区干净
- 脚本行数：`product-guard.py` 154、`session-guard.py` 317、`session-status.py` 322、`selftest.py` 286

**被治理的仓库侧**（`C:/ZYS/Code/dtsf`）：

- 活跃会话 3 个，工作树 12 个：在用 2、有改动 5、可清理 4、游离 1、孤儿目录 7
- stash 18 条，最老 22 天
- 主检出未提交改动 1 处

**已知未完成**：dtsf 那 18 个工作树、18 条 stash、7 个孤儿目录一批都没处理，用户此前选的是「先出清单，我逐条定」，清单给过，还没定。

---

## 四、审计靶子：我怀疑有问题但没验证的

按怀疑程度排序。

### 1. `prune_handoff` 的读-改-写竞争，可能丢记录

`session-guard.py` 的 `handle_start` 每次都调 `prune_handoff(handoff_records())`：整体读入全部收尾记录、筛掉 7 天前的、**整份重写**。

两个会话错开几毫秒时：A 读完文件 → B 结束并追加一条 → A 整份写回 → **B 那条没了**。SessionStart 在 `compact` / `resume` 时也会触发，窗口比想的宽。要审计：验证是否真会丢，以及是否该改成只做追加或加锁。

### 2. 7 天裁剪会静默丢掉未处理的改动提醒

`HANDOFF_KEEP_DAYS = 7`。一条「某工作树留有 3 处未提交改动」的记录，7 天后自动消失，而那 3 处改动可能还在磁盘上。提醒消失等于责任转移给用户却没告诉他。

### 3. `~/.claude` 自己这个仓库不受治理

`session-guard.py` 里对 `repo_root == ~/.claude` 直接静默返回。理由是机制文件都在这、扫它会刷屏。副作用：`~/.claude` 自己那 12 个未跟踪文件永远不会被卫生检查提到，而它正是机制的家。

### 4. 日志与状态文件的并发写入

`product-guard.log`、`session-guard.log` 用 `open(a)` 追加，无锁。多个会话同时跑 hook 时是否会出现交错或丢行，没测过。`session-hygiene.json`、`session-handoff.jsonl` 同理。

### 5. 拦截覆盖的真实边界

`product-guard.py` 只挂在 `Bash` 和 `EnterWorktree` 上。这些路径完全不经过它：

- `isolation: worktree` 的子代理工作树（harness 建的，`agent-<hash>` 命名）——已知拦不到，靠 `/dev-status` 的孤儿目录暴露
- `WorktreeCreate` hook 接管创建的情形
- 其他工具或 MCP 里间接创建工作树
- 嵌套 shell：`bash -c "git worktree add /bad"`（拆词后没有独立 `worktree` 词，会放行）

要审计：这些漏口是否可接受，还是该补。

### 6. `repo_root` 失败的拒绝策略是否过严

非 git 目录里对 `git worktree add` 一律拒绝。`git -C <别的仓库> worktree add ...` 从非仓库 cwd 执行时会被误拒。实际影响多大没评估。

### 7. `/dev-clean` 的判定条件

「可清理」= `git status --porcelain` 为空 **且** 当前没有会话的 cwd 落在该目录下。要审计：空白工作区但 `.gitignore` 覆盖了大量文件时会怎样；子模块、嵌套仓库、符号链接目录会不会产生误判。

### 8. `claude agents --json` 的失败模式

会话枚举失败时 `active_sessions()` 返回空列表，`/dev-status` 会把所有工作树显示成「无人占用」。虽然删除还要过零改动这一关，但展示层是错的。要审计：这个降级是否该显式报错。

### 9. 平台耦合

已知 Windows 专用：`session-status.py` 的端口查询用 `netstat -ano -p TCP`（Linux 上参数不合法）；`os.path.normcase` 在 POSIX 上是恒等函数（行为正确但语义不同）；hook 输出必须显式 UTF-8，否则 GBK 破坏中文 JSON。用户只在这台机器用，跨平台是否要管由用户定。

### 10. 性能边界

实测：SessionStart 1.63 秒、`/dev-status` 2.01 秒（dtsf，12 个工作树）。要审计：仓库有几百个工作树时会怎样；`claude agents --json` 在会话很多时的耗时；`session-guard` 对每个工作树跑一次 `git status` 的复杂度是线性的。

---

## 五、审计维度建议

按这七个维度各出一份结论，能查到什么写什么，查不到就写「未验证」：

1. **一致性** —— `CLAUDE.md` §8 规则文本、脚本实际行为、`session-lifecycle.md` 文档、台账四处是否还对得上
2. **正确性** —— 每段判定逻辑的输入输出是否如注释所说；边界与异常
3. **安全性** —— 删除路径是否真的不可达；有无绕过；误删的最坏后果
4. **并发** —— 多会话同时触发 hook 的竞争、丢失更新、部分写入
5. **容错** —— 每个外部依赖失败时的行为（git 缺失、`claude` 命令缺失、权限不足、磁盘满、超时）
6. **性能** —— 各脚本耗时随规模的增长
7. **可恢复性** —— 机制自身损坏后能否照台账原样恢复

---

## 六、必须遵守的约束

- 全局 `~/.claude/CLAUDE.md` 的全部规则，尤其：**禁止读写 `/tmp`**；中间产物放 `.claude/tmp/` 或 `$CLAUDE_JOB_DIR/tmp`；禁止用程序化方式改代码（heredoc / sed / python 脚本）
- `~/.claude` 仓库的提交纪律：本地提交可以，**推送需要用户确认**（推的是 GitHub 上的 `claude-stack`，属外发）
- 审计阶段不改代码。发现问题先出清单。
- 若确要改，改完必须跑 `python ~/.claude/hooks/scripts/selftest.py`（69 个用例，退出码 0 为全过）
- 用户的表达规范：用两字及以上的完整词，禁止「不是…而是…」句式，禁止「落地/钉死/对齐」这类黑话，回答不许有总结段

---

## 七、建议使用的 skills

| 用途 | skill |
|------|-------|
| 把审计结论一条条逼问清楚 | `/mattpocock-skills:grilling` |
| 审查 `39ca46b..HEAD` 这段改动 | `/mattpocock-skills:code-review` |
| 查上面第 1 条那个并发缺陷 | `/mattpocock-skills:diagnosing-bugs` |
| 核对 Claude Code 官方行为（hook 触发范围、`claude agents --json` 字段与稳定性、子代理工作树命名） | `claude-code-guide` 子代理 |
| 查证想法时读原始资料 | `/mattpocock-skills:research` |
| 需要重述复杂概念时 | `/mattpocock-skills:wait-what` |

---

## 八、这份文档

写完审计、或用户叫停之后，这份文档可以直接删（它不属于机制本体）。它当前位于 `~/.claude/docs/`，是 `claude-stack` 仓库里唯一一份一次性文档。

`~/.claude` 仓库里有若干**不属于本次工作**的未跟踪文件与未提交改动（`skills/`、`statusline/`、`session-hygiene.json` 等），不要顺手提交。
