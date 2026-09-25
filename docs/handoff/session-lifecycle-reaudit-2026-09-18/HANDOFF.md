# 会话生命周期机制 —— 二次全面审计接手文档

下个会话的任务：对**修复后**的这套机制做第二轮全面审计体检。**只审计，先不改**——结论先给用户看。

上一轮审计发现了 1 个真实缺陷（收尾记录并发丢失）与 20 条问题，已全部处理并提交。这一轮的重点是**检验修复本身**，以及上一轮明确留下的空白。

---

## 一、先读什么

不要从这份文档了解机制行为，去读原始件：

| 想知道 | 读 |
|--------|-----|
| 机制做什么、怎么用、故障处理 | `~/.claude/docs/session-lifecycle.md`（210 行） |
| 规则文本（每次会话都加载） | `~/.claude/CLAUDE.md` 第 8 节，23 行 7 段 |
| 安装台账、设计取舍、删除安全边界、回退方式 | `~/.claude/installing/custom-setup.md` 的「会话生命周期机制」一节 |
| 实现 | `~/.claude/hooks/scripts/` 下四个脚本 |
| 用例与预期行为 | `~/.claude/hooks/scripts/selftest.py`，122 个用例 |
| 本轮修复改了什么 | `~/.claude` 仓库提交 `ad386cc`；修复前基线是 `ee3c520` |
| 上一轮审计的完整结论 | 上一轮只有对话记录，没有独立文件；要点已并入 `ad386cc` 的提交信息与本文第三节 |

```bash
cd ~/.claude
git show --stat ad386cc                            # 修复范围：9 文件，641 增 127 删
git show ee3c520:hooks/scripts/session-guard.py    # 修复前基线
```

远程是 `https://github.com/zys3198/claude-stack`，`ad386cc` 已推送。

当前脚本行数：`product-guard.py` 292、`session-guard.py` 394、`session-status.py` 366、`selftest.py` 483。

---

## 二、上一轮做了什么

审计覆盖七个维度（一致性、正确性、安全性、并发、容错、性能、可恢复性）与十个怀疑靶子，全部实测取证，产出一份 21 条结论清单。用户下令全部修复，已修并在本地提交后推送。

修复要点（细节看提交，不在此复制）：收尾记录文件加锁并在锁内重读、工作树名按第 8 节收紧、同一条命令里的多处 `git worktree add` 逐处校验、按 git 2.54 用法行登记带值选项、尊重 `-C` 与 `cd`、`EnterWorktree` 的 `path` 纳入校验、被忽略内容单列、会话枚举失败显式降级、判定基准统一到主检出根。

---

## 三、本轮修复改变了哪些行为契约（第二轮审计的主战场）

新行为就是新风险面。以下每条都是这一轮新写出来的，**需要独立检验**：

| 新行为 | 检验方向 |
|--------|----------|
| `session-handoff.lock`：`O_CREAT\|O_EXCL` 独占创建，等待上限 2 秒，30 秒视为陈旧自动接管 | 进程被杀留下的锁、时钟回拨、只读目录、极端时序下的创建竞争、锁文件被手工删掉、多用户权限 |
| `prune_handoff()` 改成无参 + 锁内重读 + 无需裁剪时不写文件 | 锁内重读期间抛错、`dropped == 0` 的判定、锁的释放路径 |
| `handle_end` 取不到锁时**照常追加**并写日志 | 这条降级会不会反过来被并发裁剪丢掉，也就是降级路径的保护强度 |
| `main_root()`：取 `git rev-parse --path-format=absolute --git-common-dir` 的上一级，取不到退回 `--show-toplevel` | submodule、bare repo、`--separate-git-dir`、`GIT_DIR`/`GIT_WORK_TREE` 环境变量、`.git` 是文件的情况 |
| `norm()` 三个脚本统一改 `os.path.realpath` | 路径不存在时、UNC 路径、超长路径、大小写、网络盘 |
| `worktree_adds()` 收集**每一处** `git worktree add` 逐处校验 | 匹配变多后误拒率上升；`--`、`--end-of-options`、选项值里含 `worktree add` 字符串 |
| `is_control()` 的控制符集合 | 是否漏了 `&>`、`<<<`、`n<`、换行分隔、`{ …; }`、`( … )`、命令替换 `$( )` 与反引号 |
| 命名规则收紧（kebab-case、`tmp`/`test`、纯日期、`agent-`/`worktree-` 前缀） | 会不会挡住正常使用；`HASH_WORD` 的 16 位十六进制串误伤；词数刻意不校验是否留下不一致 |
| `ignored_count()` 只对「可清理」候选跑 | 大仓库（`node_modules`）下一次 `--ignored` 的成本 |
| `active_sessions()` 返回 `None` | 所有调用点是否都处理了 `None`（`session-guard.py` 与 `session-status.py` 各一处） |
| `EnterWorktree` 的 `path` 校验 | 目标尚未建出时会被拒；harness 自己调用时会不会被误伤 |

---

## 四、上一轮明确保留未改的（有设计理由，不是遗漏）

1. **`~/.claude` 自己不受治理**，且**没有并发保护**。`session-guard.py` 对 `main_root == ~/.claude` 直接静默返回，理由是机制文件都在这里，扫它会刷屏。副作用：`~/.claude` 自身的未跟踪文件永远不进卫生检查，而这个仓库正是机制的家。**这条现在有了新证据**：本轮会话期间另一个会话在同一仓库里改 `.gitignore` 与 `installing/skill-install.md`、`installing/tool-install.md`。两个会话同时整文件写同一个脚本时，后写的静默覆盖先写的，git 不提醒。上一轮按原始设计保持了静默，**这一轮值得重新评估**。
2. **7 天裁剪仍会丢掉孤儿目录那类提醒**。工作树还在磁盘时实时扫描能顶上，孤儿目录没有兜底。现在只在 `session-guard.log` 里留一行。
3. **解释器间接调用放行**（`bash -c "…"`、`python -c "os.system(…)"`）。拦住要写 shell 解析器，且会与已测过的「引号内提到这串字放行」冲突。已在文档与台账写明这是边界。
4. **`netstat -ano -p TCP` 平台耦合**，只在这台机器用。

---

## 五、上一轮明确未验证的

- 子代理 `isolation: worktree` 创建的工作树是否真的绕过 `product-guard`（上一轮没有派发子代理，没有实测）
- `claude agents --json` 是否属于官方文档承诺的受支持接口（字段实测存在且可用，官方文档原文未查）
- 200 棵以上工作树的实测耗时（按斜率外推 `/dev-status` 约 18 秒、SessionStart 约 15 秒）
- Linux 上 `netstat` 分支的实际行为（按参数语义判读，未执行）
- 目录符号链接（上一轮只验了 junction；`realpath` 对两者都成立，但没有分别取证）

---

## 六、上一轮会话期间的异常观测

`~/.claude/session-guard.log` 只有一行：

```
2026-09-18 21:52:52 git status --porcelain 执行失败：[WinError 267] 目录名称无效。
```

这个格式只有修复后的 `session-guard.py:86` 才会产出，而该脚本的创建时间是 22:24:01。已核对：`file-history` 全部会话目录里没有别的会话改过这三个脚本的痕迹；`git show ee3c520` 的行号（24/186/232/276）与行数（317/154/322）与上一轮审计逐行对得上。**无法归因，未删除，留给第二轮判断。**

---

## 七、审计方法（上一轮怎么做的）

顺序：读原始件 → 静态核对行号 → 写实测探针 → 跑 → 出结论清单。用户特别要求「要实测确认，不要只读代码推断」。

上一轮的探针脚本全部写在 `$CLAUDE_JOB_DIR/tmp/`，随任务删除，**这一轮需要重写**。上一轮用过的探针形状，可照此重造：

- 并发丢失：多个独立 Python 进程，一组反复调真实裁剪函数、一组反复调真实 `handle_end`，统计标记记录的存活数
- 拦截边界：以真实 hook 入口（stdin 喂 JSON 给 `product-guard.py`）逐条跑命令，判定「拒绝/允许」，再用真实 git 验证该写法是否真的建出目录
- 降级：monkeypatch 模块级函数或伪造失败命令，跑真实 `main()`，对比分组结果
- 性能：造 0/25/70 棵工作树的沙箱仓库，分别计时
- 归档：用 `cmd /c mklink /J` 造 junction，验证 `abspath` 与 `realpath` 的差别

沙箱放 `$CLAUDE_JOB_DIR/tmp`（后台任务）或 `.claude/tmp/`（前台）。**注意**：Windows 上 git 的 objects 是只读的，`shutil.rmtree` 需要 `onerror` 里 `chmod`；重跑探针时换新目录比清理旧目录省事。

---

## 八、约束

- 全局 `~/.claude/CLAUDE.md` 全部规则，尤其：**禁止读写 `/tmp`**；中间产物放 `.claude/tmp/` 或 `$CLAUDE_JOB_DIR/tmp`；禁止用程序化方式改代码（heredoc / sed / python 脚本）；禁止用 Git 回滚代码
- `~/.claude` 仓库提交纪律：本地提交可以，**推送需要用户确认**（推的是 GitHub 上的 `claude-stack`，属外发）
- `~/.claude` 工作区里有**不属于本次工作**的改动（`.gitignore`、`installing/skill-install.md`、`installing/tool-install.md`，另一个会话写的），不要顺手提交
- 审计阶段不改代码。发现问题先出清单，逐条等用户定
- 若确要改，改完必须跑 `python ~/.claude/hooks/scripts/selftest.py`（122 个用例，退出码 0 为全过）
- 用户的表达规范：用两字及以上的完整词，禁止「不是…而是…」句式，禁止「落地/钉死/对齐」这类词，回答不许有总结段

---

## 九、建议使用的 skills

| 用途 | skill |
|------|-------|
| 把审计结论一条条逼问清楚 | `/mattpocock-skills:grilling` |
| 审查 `ee3c520..ad386cc` 这段修复 | `/mattpocock-skills:code-review` |
| 查并发与锁的残留缺陷 | `/mattpocock-skills:diagnosing-bugs` |
| 核对 Claude Code 官方行为（hook 触发范围与 matcher 语义、`claude agents --json` 字段与稳定性、子代理工作树命名、`EnterWorktree` 的 `path` 语义） | `claude-code-guide` 子代理 |
| 查证想法时读原始资料 | `/mattpocock-skills:research` |

---

## 十、这份文档

位于 `C:\Users\zys31\.claude\docs\handoff\session-lifecycle-reaudit-2026-09-18\HANDOFF.md`，在被审计的仓库里，随 `claude-stack` 进版本库。

原先选定的是 `C:\ZYS\Code\dtsf\.claude\docs\handoff\session-lifecycle-reaudit\HANDOFF.md`，后台任务的隔离保护拒绝了该路径（改动必须落在工作树里，而 dtsf 的 `.claude/` 属于共享检出）。需要挪到那里时，把它复制过去即可。

写完审计、或用户叫停之后，这份文档可以直接删。
