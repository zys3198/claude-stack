---
name: local-env-pitfalls
description: 写脚本、运行命令或派子代理前，查阅本机路径、编码、解析、门禁、工作树与容器坑位。
disable-model-invocation: true
---
# 工具链坑位清单

每一条都来自实际踩过的坑，带上当时的判据。细节与实例见 `references/`。

## 路径与引号

- **Git Bash 会改写以 `/` 开头的参数**：调用 Windows 工具时 `/ve`、`/d`、正则、URL 路径这类根相对值被自动翻译。优先用双斜杠前缀保护（容器内写 `//root/...`）；`MSYS_NO_PATHCONV=1` 是次选——加前缀会改变命令文本，使不带前缀的 allow 规则匹配不上，反而触发权限询问。
- **Bash 工具把命令包进 `bash -c "<双引号>"`**：heredoc 正文里的反引号和 `$(...)` 会被当命令替换执行，即便用了 `<<'EOF'`。大段含 `$`／反引号的内容走 native Write，不经 shell。
- **调 PowerShell 时变量被 Bash 吃成空值**：改用单引号包裹，或写成独立脚本文件再执行。
- **Windows 二进制要 Windows 风格路径**：MSYS 风格 `/c/Users/...` 会被判成全新安装，把身份配置重置。一律写 `C:/...`。

## 编码与输出

- **跑第三方 Python 工具先设 `PYTHONUTF8=1`**：Windows 上 `open()`／`read_text()` 默认走 GBK，读含非 ASCII 的 UTF-8 文件直接崩。这个环境变量一次治 `read_text`、`open`、stdout 全部同类问题，逐处打补丁是次选。
- **PowerShell hook 走的是 5.1，不是 pwsh 7**：stdin 按 GBK 解码毁 UTF-8 中文 payload；无 BOM 脚本按 ANSI 读；解析错误在 async hook 里静默无提示。测 PowerShell hook 必须原样复刻 Git Bash + 5.1 的调用链。
- **Windows 原生命令按系统代码页输出**：`netstat`、`tasklist` 的输出直接按 UTF-8 解码会得到乱码。

## 脚本与解析

- **超长内联命令会被解析器截断**：长 heredoc 和超长单行命令在 Git Bash 上会解析失败。超过一屏就写成文件再执行。
- **CMD 包装器不是原生可执行文件**：`npm`、`pnpm` 在 Windows 上是 `.cmd` 包装器，不能直接当可执行文件传给 `subprocess`。先单条验证调用方式，再写进脚本。
- **f-string 里不要复用外层引号**：Python 3.12 之前会直接语法错误。复杂条件先算成局部变量再插值。
- **批量编辑工具省略空的可选字段**：空的 `queries`、`handle` 之类传空值会解析失败，直接省略。
- **短文件的读取偏移量写多一位就返回空**：`offset` 只照抄工具返回的真实行号，心算、补零、按代码规模猜都会越界。文件不超过 2,000 行一律 `offset: 0` 配 `limit` 覆盖；首次收到「文件更短」后不再发非零 offset，改用内容检索或精确切片。
- **Grep 的 `glob` 禁嵌套花括号替代组**：`{docs/**/*.md,code/**/*.{yml,yaml}}` 这类写法会让搜索静默不执行，不报错。跨目录加跨扩展名的范围拆成多次独立调用，不反复试改表达式。
- **同一批里做过结构改动之后要重新定位**：行号已经位移，沿用旧行号的后续操作会落在错误位置。
- **Edit 锚点要含整行**：唯一 ≠ 安全。在某段**前**插入时 `old_string` 取该段完整首行或整段，`new_string` = 新内容 + 空行 + 原文照抄；**删整行**时锚点必须含该行自己的换行（`行内容\n`），只带前导换行（`\n行内容`）会把上下两行粘成一行；短锚点改完用 Read 复查该区域——Edit 返回 success 只代表匹配成功，不代表结构没坏。
- **带 `getpass` 的脚本不交给后台 job**：后台没有可交互终端，脚本卡在等密码处、输出为空，重复启动只堆积并发副本。密码不写进聊天或命令行参数。

## 门禁与守卫

- **被拦后原样重试，不改命令文本**：破坏性门按命令哈希记状态，换等价命令会重新拦。
- **分类器拒了就停手报告**：拒绝针对的是**结果**（这个产出能不能落地），不是这一条命令的写法——换命令文本、换工具、拆成两次重发都不改变结论，要改的是产出本身或等用户放行。
- **混合命令拆开**：Python 改文件与 `git` 命令混在一条 Bash 请求里会被判「无法确认 Git 目标」。
- **非代码文件被 Gate 拦时主动带四件套声明**，不等用户喊：调用者（无／交付物）、无重复（已搜过现有文件与索引）、数据文件性质（纯文本、无字段读写、无日期格式）、用户指令原文引用；完整判据见 [`references/guards.md`](references/guards.md)。

## 工作树与子代理

- **建工作树或克隆之前先扫同级目录**：确认 `git worktree list` 和同级检出里没有同一件事的副本。
- **会话主目录不是目标仓库时，命令必须显式绑定路径**：Maven 用 `-f <target>/pom.xml`，pnpm 用 `--dir <target>`，git 用 `-C <target>`，不依赖 shell 当前目录——否则会因缺 `pom.xml`／`package.json` 立即失败，或更糟：在错误的仓库上执行成功。
- **隔离工作树不继承 `node_modules`**：跑前端回归、类型检查或构建前先核实工作树根目录与 workspace 子包的依赖。缺失时会在模块加载阶段就失败，还没走到任何业务断言——据此判源码或合并结果有缺陷是错的。
- **工作树被 `core.worktree` 重定向会导致启动失败**：发现后先核对 `git config core.worktree`，不要反复更换隔离方式。
- **隔离工作树里动态生成的脚本可能被钩子拒绝**：钩子判定不可信即拒绝执行，改用原生文件编辑工具。
- **远程隔离看到的可能是另一份检出**：远程执行得出的结论必须回本地核对未提交状态。
- **子代理返回基准分支解析失败后先诊断前置条件**，不原样重试，也不靠改代理名称／模型／类型绕过。
- **子代理状态分三步核验**：启动结果、运行状态、完成通知各算一次，收到失败通知后停止引用旧状态。
- **shell 超时之后先确认子进程**：Windows 上超时不会终止已派生的 git 进程，它会继续持有锁文件。
- **Windows 上父进程退出不连带终止子进程**：自己启动的进程必须按 PID 精确终止，否则会占住端口和文件锁。
- **权限分类器可能拒绝 `git worktree remove`**：`git branch -d` 通常可以通过；删除工作树需要用户放行，或由人在终端自行执行。

## 容器

- **Docker API 版本**：本机 Engine 要求 ≥1.44，老的 docker-java 客户端默认发 1.32 会被拒 400，导致 Testcontainers 测试**静默跳过**（Maven exit 0 假成功）。判断可用性要看 surefire 是否 Skipped，不能只看 `docker version`。
- **资源守卫会 ask 的三种情况**：改动新增的 compose 服务缺 `mem_limit`／`security_opt`；动 `~/.claude/session-hygiene.json` 独占清单里的容器；在宿主机上执行构建工具链。

## 验证与统计

- **统计配置注入量前先验生效机制**：不能按「磁盘上有哪些文件」直接加总。skill 看 frontmatter 的 `disable-model-invocation`（为 true 完全不进 system prompt）；插件看实际注册状态，不看目录内容；hook 看是否真被调用。拿运行时实证（system prompt 里实际出现了哪些条目）与静态清单对照，不重合的部分就是要查的机制——按静态清单估会高估近一倍。
- **验证实际行为，不信任陈述的配置**：用户说「环境已配成某样」时，跑真实命令确认行为，不只看 config 文件字段。修完**验症状不验机制**——跑能触发症状的真实操作确认症状消失，别只查「我假设的中间机制是否变化」。判据是症状层面的可观测结果，不是机制层面的推测。
- **验收脚本的异常报告要留脱敏后的失败阶段、目标路径与异常类型**：只存一个泛化的 `Error`，事后分不清服务不可达、页面定位失效还是认证失败。

## 详细分类

| 文件 | 内容 |
|---|---|
| [`references/git-bash.md`](references/git-bash.md) | MSYS 路径转换、引号展开、junction 与符号链接、WSL 转发器、GitHub 镜像 |
| [`references/powershell.md`](references/powershell.md) | 只读自动变量、`-notmatch` 正则陷阱、查工具与端口、删文件 |
| [`references/encoding.md`](references/encoding.md) | GBK 三处根因、5.1 stdin 排查法、外发中文前验证 |
| [`references/docker.md`](references/docker.md) | 资源守卫三条规则、API 版本、内存上限 |
| [`references/guards.md`](references/guards.md) | 各门禁的拦法与配合方式 |
| [`references/subagents.md`](references/subagents.md) | 委派配置、状态三步核验、失败后诊断 |
