# 把 Claude Code 迁到 WSL2 以启用沙盒的评估

> 2026-09-25 归档：本文件原在 `~/.claude/docs/wsl2-sandbox-migration.md`。文内路径是当时实况，未随之后的搬迁改写。

评估日期 2026-09-21。依据：Claude Code 官方文档《Configure the sandboxed Bash tool》与微软 WSL 官方文档《Advanced settings configuration in WSL》，以及本机实测。

## 结论

可行，本机前置条件已具备（已有两个 WSL2 发行版）。但这条路**达不到「随便执行命令都不怕」的全部含义**：只要 agent 还需要用 docker，它就握着宿主 root 的等价物，这一点沙盒堵不住。能达到的是——agent 在 WSL 里的文件系统写入与网络外发被操作系统级强制约束，并且关掉 WSL 的 Windows 程序互操作之后，没有绕回宿主的旁路。

## 为什么 Docker 达不到这个效果

沙盒约束的是**命令及其子进程**能写哪些路径、能连哪些域名，由操作系统强制。容器约束的是**放进容器里的进程**。agent 跑在宿主机上，它在宿主机上敲的命令不经过任何容器，所以容器加固得再好也不保护宿主机。

「让 agent 进容器」这条看似直接的路有死结：agent 要操作 docker 就必须把 `/var/run/docker.sock` 挂进容器，而官方文档明确写「allowing access to `/var/run/docker.sock` effectively grants access to the host system through the Docker socket」。挂进去等于把宿主 root 交给容器，隔离反而不存在了。

## 本机现状（实测）

- Claude Code 2.1.278，Windows 原生进程；`C:\Users\zys31\.claude\settings.json` 里没有任何 `sandbox` 配置项
- WSL2 发行版两个，版本都是 2：`docker-desktop`、`Ubuntu`（读自注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss`）
- 仓库在 `C:\ZYS\Code\dtsf`，在 WSL2 里是 `/mnt/c/ZYS/Code/dtsf`；配置树在 `C:\Users\zys31\.claude`
- 官方文档：沙盒内建于 Claude Code，支持 macOS、Linux、WSL2，**不支持 Windows 原生**；WSL1 也不支持（bubblewrap 需要只有 WSL2 才有的内核特性）

## 沙盒约束什么

- **文件系统写入**：默认只能写当前工作目录、会话临时目录，以及用 `--add-dir`、`/add-dir`、`permissions.additionalDirectories` 加进来的目录。用 `sandbox.filesystem.allowWrite`、`denyWrite`、`denyRead`、`allowRead` 调整。存在一批受保护路径无法豁免，唯一关掉的办法是 `sandbox.filesystem.disabled`（会关掉整个文件系统层）。
- **网络**：域名白名单，流量走沙盒代理，遇到新域名要批准。`sandbox.network.allowedDomains` 可预先放行，`deniedDomains` 始终拦截，`strictAllowlist` 锁定白名单。
- **凭据**：`protect` 直接挡住凭据；`mask` 给沙盒内命令看一个占位符，出网时代理换回真值，命令与它的日志里从不出现真值。
- **适用面**：Bash、PowerShell、Monitor 工具及其子进程。
- `sandbox.failIfUnavailable: true` 可把「依赖缺失就降级为无沙盒运行」改成启动硬失败。默认是只警告然后无沙盒运行。

## 三个必须同时满足的条件

1. **Claude Code 在 Ubuntu 里跑**。原生 Windows 不支持沙盒，这是硬前提。
2. **装 `bubblewrap` 与 `socat`**。bubblewrap 强制文件系统隔离，socat 是网络代理的中继。Ubuntu 24.04 及以上还要看 `sysctl kernel.apparmor_restrict_unprivileged_userns`：返回 `0` 或报键不存在可以直接用，返回 `1` 要给 `bwrap` 加一条 AppArmor 规则放开 user namespace。
3. **堵死回宿主的旁路**。WSL2 会把 `cmd.exe`、`powershell.exe`、`/mnt/c` 下的 Windows 可执行文件通过 Unix socket 交给宿主执行。官方给的堵法是装可选的 seccomp 过滤器（`npm install -g @anthropic-ai/sandbox-runtime`）。但那个过滤器同时会挡掉 `/var/run/docker.sock`，而放行它按官方原话等于交出宿主访问权。**更干净的做法是在 WSL 层关掉互操作**：

```ini
# /etc/wsl.conf
[interop]
enabled=false
appendWindowsPath=false

[automount]
enabled=false
```

`[interop] enabled` 默认 `true`，设为 `false` 之后 WSL 不再支持拉起 Windows 进程；`appendWindowsPath=false` 不再把 Windows 的 PATH 拼进来。这样 Windows 可执行文件根本进不来，也不必装 seccomp 过滤器，docker socket 保持可用。改完要重启发行版才生效（官方说法是子系统完全停止后约 8 秒，`wsl --terminate Ubuntu` 或 `wsl --shutdown` 是快路径）。

## 仓库与配置树放哪

**仓库必须放进 WSL2 的 Linux 文件系统**，例如 `/home/<用户名>/Code/dtsf`，不要用 `/mnt/c`。两个理由：仓库放在 `/mnt/c` 时沙盒的文件系统边界等于没设（Windows 盘整个可写，agent 可以改宿主机上任何文件）；而且 DrvFs 的 I/O 比 Linux 原生文件系统慢一个量级，`git status`、依赖安装、构建都会明显变慢。两处都要用的场景用 git 同步，不要共享目录。

**配置树同理，建议在 WSL 里用一份独立的 `~/.claude`**，而不是软链到 `/mnt/c/Users/zys31/.claude`。现在 Windows 版 `settings.json` 里每个 hook 都写死了 Windows 解释器路径（`C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe`，另有 `powershell.exe`、`C:/ZYS/Software/Git/usr/bin/bash.exe`，statusline 用 `node`），软链过去会全部失效；把它们改成 Linux 形式又会把 Windows 版弄坏。两份配置无法同时成立。

## 迁移步骤

1. 在 Ubuntu 里装 Node 与 Claude Code 原生二进制
2. `sudo apt-get install bubblewrap socat`
3. 写 `/etc/wsl.conf` 关掉 interop 与 Windows 盘自动挂载，重启发行版
4. 把仓库克隆到 Linux 文件系统
5. 在 WSL 里重建 `~/.claude`：`settings.json`、skills、hooks、memory，hooks 里的解释器路径改成 Linux 形式
6. 跑 `/sandbox`，Dependencies 页应无缺项，Config 页可看到受保护路径清单
7. 实测边界：写工作目录外的路径应被拒；访问白名单外的域名应被拒；`/mnt/c` 不存在；在沙盒里执行 `cmd.exe` 应失败

## 代价

- 配置分叉：Windows 版与 WSL 版两套 `~/.claude`，改一处不会同步到另一处
- hooks 与 skills 的路径要重写一遍
- 记忆与会话历史两边不共享
- 关掉 interop 之后，WSL 里用不了 `explorer.exe`、`code .`、`docker.exe` 这类 Windows 程序
- 内存上限互相挤压：`~/.wslconfig` 的 8GB 同时罩着 Ubuntu 与 docker-desktop，agent 自身也要占一部分
- Docker Desktop 的 WSL 集成不受影响，Ubuntu 里可以直接用 `docker` 命令，容器仍跑在 `docker-desktop` 发行版里

## 沙盒挡不住什么

- **docker socket 等于宿主 root**。agent 只要能执行 `docker`，就能起一个挂载宿主路径的容器，沙盒的文件系统边界在这条路上不起作用。这是「还要用 docker」这个前提的固有代价，不是配置问题。想堵只能让 agent 所在的发行版不接 docker socket。
- 网络白名单只约束沙盒内进程走代理这条路；agent 通过 docker 起的容器用自己的网络栈。
- 沙盒只覆盖 Bash、PowerShell、Monitor 工具及其子进程，不覆盖其他工具。

## 回退

Windows 原生那份配置完全不改，随时可用；WSL 版是新增的一份。回退就是不再进 Ubuntu 跑 Claude Code，并删掉发行版里的 `~/.claude`。`/etc/wsl.conf` 把 `enabled` 改回 `true` 再重启发行版即可恢复互操作。

## 待核实

- Ubuntu 的版本（决定要不要加那条 AppArmor 规则）：`wsl -d Ubuntu -e cat /etc/os-release`
- 是否已装 bubblewrap、socat、node：`wsl -d Ubuntu -e dpkg -l bubblewrap socat nodejs`
- 不装 seccomp 过滤器、改用 `[interop] enabled=false` 时，沙盒里是否真的拉不起 Windows 程序（要实测，不能只看文档）
- 沙盒默认是否放行 `/var/run/docker.sock`；不放行时的正确配置项与代价
- `/sandbox` 面板在 WSL2 上的实际依赖检测结果
