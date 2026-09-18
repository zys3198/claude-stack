# 会话生命周期机制 —— 最终审计接手文档

下个会话的任务：对**第二轮修复之后**的机制做最终审计，确认可以收口。**只审计，先不改**——结论先给用户看。

前两轮各自发现了真实缺陷。这一轮的重点是**检验第二轮修复写出来的新行为**，以及前两轮都留给后续的空白项。上一轮已明确保留未改的，标题里独立列出，供你判断是否重开。

---

## 一、先读什么

不要从这份文档了解机制行为，去读原始件：

| 想知道 | 读 |
|--------|-----|
| 机制做什么、怎么用、故障处理 | `~/.claude/docs/session-lifecycle.md` |
| 规则文本（每次会话都加载） | `~/.claude/CLAUDE.md` 第 8 节 |
| 安装台账、设计取舍、删除安全边界、回退方式 | `~/.claude/installing/custom-setup.md` 的「会话生命周期机制」一节 |
| 实现 | `~/.claude/hooks/scripts/` 下四个脚本 |
| 用例与预期行为 | `~/.claude/hooks/scripts/selftest.py`，142 个用例 |
| 第二轮改了什么 | 提交 `622a09a`；合并 `eaa9752` |
| 第二轮审计的完整清单 | 上一轮对话记录；沉淀在本文第三节与 `622a09a` 的提交信息 |
| 第一轮审计发现与修复 | 提交 `ad386cc`；修复前基线 `ee3c520`；接手文档 `~/.claude/docs/handoff/session-lifecycle-reaudit/HANDOFF.md` |

```bash
cd ~/.claude
git show --stat 622a09a        # 第二轮修复范围：7 文件，280 增 78 删
git show ee3c520:hooks/scripts/session-guard.py    # 第一轮修复前的基线
git show 8296627:hooks/scripts/session-guard.py    # 第二轮修复前的基线
```

远程是 `https://github.com/zys3198/claude-stack`。分支 `session-lifecycle-fix`（HEAD `eaa9752`）已推送，远程 `main` 仍停在 `ad386cc`，**尚未合并**。

主检出 `~/.claude` 当前在 `main` = `eaa9752`，本地已生效。工作区另有别的会话留下的未提交改动，不要顺手提交。

当前脚本行数用 `wc -l hooks/scripts/*.py` 现取，不要引用旧数字。

---

## 二、状态

机制已部署生效：主检出三个脚本都含第二轮改动，真实 hook 已按新代码运行。自检 142 项在部署路径上跑过，退出码 0。

前两轮修复要点不在此复制，看提交。

---

## 三、第二轮修复改变了哪些行为契约（本轮主战场）

以下每条都是第二轮新写出来的，**需要独立检验**：

| 新行为 | 检验方向 |
|--------|----------|
| `lock_acquire()` 返回令牌字符串或 `None`，`lock_release(token)` 比对锁文件内容一致才删 | 读取内容与删除之间的 TOCTOU 窗口；锁文件被手工改写或清空时的行为；令牌碰撞概率（pid + 6 字节随机）；传入 `None`、空串、非字符串 |
| 降级追加改写 `~/.claude/session-handoff.d/<时间>-<pid>-<随机>.jsonl` | 溢出目录长期不裁剪时的增长；文件名碰撞；溢出文件被手工删改；`handoff_records()` 排序对 `pending[-1]` 的影响；`prune_handoff` 重写主文件与并发降级写入的交错 |
| `handoff_records()` 合并溢出目录并按 `ts` 排序 | 排序稳定性；`ts` 缺失或非数字的记录；主文件与溢出文件记录顺序打乱后的提示是否正确 |
| `prune_handoff()` 在 `dropped == 0` 但有溢出文件时也会重写主文件 | 「无需裁剪时不重写」的原始约束是否被削弱；重写期间的一致性 |
| `active_sessions()` 返回 `None` 表示枚举降级 | 所有调用点是否都处理；降级时同目录并发提示消失是否可接受；`session-status.py` 的 `handoff_rows()` 路径 |
| 锁文件修改时间在将来时按陈旧接管（`age < -30`） | 与「真正新鲜的锁」的边界；系统时钟抖动是否会造成误接管 |
| `is_git_token()`：命令名按最后一段判定，覆盖 `git`、`git.exe`、绝对路径 | `git` 出现在参数位置时是否误判；`GIT.EXE` 大小写；`git2`、`git-lfs`、`gitk` 是否被正确排除；UNC 路径形式 |
| `enter_path_reason()` 拆出独立函数，`check_enter_worktree` 在 `name` 与 `path` 同时给出时两个都校验 | 两者都非法时只报第一条是否足够；`path` 最后一段的名字仍然不校验（与第 8 节「禁用 hash 名」的差距） |
| `check_worktree_add()` 对非字符串 `command` 记日志后放行 | 其它工具挂在同一 matcher 上时的行为 |
| `commands/dev-clean.md` 新增「读到枚举失败立即停止」 | 这是给模型看的指令，不是代码。是否真的被遵守需要实测：造一个 `claude agents --json` 不可用的环境跑 `/dev-clean` |

---

## 四、前两轮都保留未改的（有设计理由，可重新评估）

1. **`~/.claude` 自己不受治理**：`session-guard.py` 对 `main_root == ~/.claude` 直接静默返回。第二轮实测把这条的原始理由推翻了——把 `~/.claude` 当普通仓库处理只产出一行「主检出 3 处未提交改动」，不刷屏（那里只有主检出、没有工作树）。该仓库正是机制的家，且实测期间另有会话在同时改它的文件。**这条值得优先重新评估。**
2. **`log()` 的并发写入无保护**：一轮实测 5 进程 × 120 行共 600 条，实际落盘 549 条，丢 51 条；真实 `session-guard.log` 里已有破损行。加锁会引出 `log` 与 `lock` 的相互调用，第二轮按「代价高于收益」保留。
3. **命令替换拼出命令名放行**（`$(echo git) worktree add …`）。已在文档与台账写明是边界。
4. **注释掉的命令被误拒**（`true # git worktree add <仓库外>`）。处理 shell 注释规则的风险高于收益。
5. **`HASH_WORD` 对 16 位数字串的误伤**（`build-2026091800000000` 被当作 hash 拒绝）。拒绝方向保守。
6. **`netstat -ano -p TCP` 平台耦合**，只在这台机器用。
7. **7 天裁剪仍会丢掉孤儿目录那类提醒**，工作树还在磁盘时靠实时扫描顶上。

---

## 五、本轮未验证的

- 溢出目录在**真实环境**从未触发过（`~/.claude/session-handoff.d/` 尚未创建），所有验证都在沙箱里
- `dev-clean.md` 的新指令是否真被模型遵守（需要造降级环境实测）
- 派一次带 `isolation: worktree` 的子代理，抓实时拦截日志。按全局 `CLAUDE.md` §2.5，需要先向用户展示子代理配置并获确认
- 200 棵以上工作树在其它负载条件下的耗时。本轮实测 220 棵时 SessionStart 11.67 秒、`/dev-status` 22.56 秒，hook 超时是 25 秒，余量不大；斜率受同时运行的探针干扰，数据不稳
- Linux 上的 `netstat` 分支行为

---

## 六、环境里的活体现象（审计时可能撞到）

- `C:/ZYS/Code/lab-area/.claude/worktrees/agent-abc03c771a0e516a4`：git 已注册、目录已删除（`git worktree list` 标 `prunable`）。**任何在 lab-area 开的会话，SessionStart 都会往 `~/.claude/session-guard.log` 写一行 `WinError 267`**。第二轮据此把「无法归因」那行日志定性为常规错误消息，触发源定位到此。它的分支名是 `worktree-agent-abc03c771a0e516a4`，说明 harness 创建子代理工作树确实不经过 `product-guard`
- `~/.claude/product-guard.log`：第二轮之前不存在，现在含 5 条探针触发的 `'list' object has no attribute 'replace'`（command 非字符串的旧路径）
- `~/.claude/session-guard.log`：5 条 `WinError 267`，其中 2 条由第二轮探针写入
- `~/.claude` 工作区常年有别的会话的未提交改动，第二轮期间出现过 `.gitignore`、`installing/` 两个台账、`skills/install-ledger/SKILL.md`

---

## 七、审计方法

顺序：读原始件 → 静态核对行号 → 写实测探针 → 跑 → 出结论清单。用户要求「要实测确认，不要只读代码推断」。

探针写在 `$CLAUDE_JOB_DIR/tmp/`（后台任务）或 `.claude/tmp/`（前台），随任务删除，**每一轮都要重写**。

两轮都用过的探针形状：

- 并发丢失：多个独立 Python 进程，一组反复调真实裁剪函数、一组反复调真实 `handle_end`，统计标记记录的存活数
- 拦截边界：以真实 hook 入口（stdin 喂 JSON 给 `product-guard.py`）逐条跑命令，判定「拒绝/允许」，再用真实 git 验证该写法是否真的建出目录。**只判 DENY/ALLOW 不够，必须跑真实 git 确认**
- 锁：真实调用 `lock_acquire` / `lock_release`，用 `os.utime` 伪造陈旧与将来的锁
- 降级：起一个占锁进程，再并发起多个真实 `handle_end`
- 追加原子性对比：`open('a')` 保持句柄、每次开关文件、`os.open` + `O_APPEND`、`os.lseek` + `write` 各跑一遍。**结论：Windows 上保持句柄不丢，每次开关会丢 8% 到 14%**
- 性能：造 0/25/70/150/220 棵工作树的沙箱仓库分别计时
- 归档：用 `cmd /c mklink /J` 与 `mklink /D` 造 junction 与符号链接，对比 `abspath` 与 `realpath`

沙箱注意事项：

- 沙箱放 `$CLAUDE_JOB_DIR/tmp`，**跑完主动清理**（220 棵工作树约 85 MB）
- Windows 上 git 的 objects 是只读的，`shutil.rmtree` 需要在 `onerror` 里 `chmod`
- 重跑探针时换新目录比清理旧目录省事
- **探针的 `subprocess` 传参下标容易写错**（`sys.argv[1]` 与 `sys.argv[2]` 混淆会导致子进程直接抛 `IndexError`，而主探针仍打印「丢失 0 条」这种假结果）。写完全部子进程后先确认每个都真的跑起来了
- **在链接工作树里跑 `selftest.py` 会让「约定位置之外」的用例失效**：沙箱建在工作树内，路径恰好落在主检出 `.claude/worktrees/` 下，会被判合规。`selftest.py` 现在用主检出根当越界样本，改动时别退回用 `SANDBOX`

---

## 八、约束

- 全局 `~/.claude/CLAUDE.md` 全部规则，尤其：**禁止读写 `/tmp`**；中间产物放 `.claude/tmp/` 或 `$CLAUDE_JOB_DIR/tmp`；禁止用程序化方式改代码（heredoc / sed / python 脚本）；禁止用 Git 回滚代码
- `~/.claude` 仓库提交纪律：本地提交可以，**推送需要用户确认**（推的是 GitHub 上的 `claude-stack`，属外发）；禁止推 `main`、禁止 force push
- 工作树放 `~/.claude/.claude/worktrees/<任务名>`，`main` 上有未推送提交时先合并进来再动
- 工作区里属于别的会话的改动不要顺手提交
- 审计阶段不改代码。发现问题先出清单，逐条等用户定
- 若确要改，改完必须跑 `python ~/.claude/hooks/scripts/selftest.py`（142 个用例，退出码 0 为全过），并在主检出路径上复跑一次
- 用户的表达规范：用两字及以上的完整词，禁止「不是…而是…」句式，禁止「落地/钉死/对齐」这类词，回答不许有总结段

---

## 九、建议使用的 skills

| 用途 | skill |
|------|-------|
| 把审计结论一条条逼问清楚 | `/mattpocock-skills:grilling` |
| 审查 `ad386cc..eaa9752` 这段修复 | `/mattpocock-skills:code-review` |
| 查并发、锁、追加原子性的残留缺陷 | `/mattpocock-skills:diagnosing-bugs` |
| 核对 Claude Code 官方行为（hook 超时与 matcher 语义、`claude agents --json` 的字段稳定性、子代理工作树命名、`EnterWorktree` 的 `path` 语义） | `claude-code-guide` 子代理 |
| 查证想法时读原始资料 | `/mattpocock-skills:research` |
| 实测清理链路是否守住降级 | `/dev-clean`、`/dev-status` |

---

## 十、这份文档

位于 `C:\Users\zys31\.claude\docs\handoff\session-lifecycle-final-audit\HANDOFF.md`，在被审计的仓库里，随 `claude-stack` 进版本库。

上一轮的接手文档在 `~/.claude/docs/handoff/session-lifecycle-reaudit/HANDOFF.md`，内容描述的是第二轮修复之前的状态，只作历史证据读。

写完审计、或用户叫停之后，这两份文档都可以直接删。
