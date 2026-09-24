# Docker

## 资源守卫（全局 hook `resource-guard.py`）

三条触发规则，命中返回 `permissionDecision: "ask"`：

- **改 `docker-compose*.yml` / `compose*.yml` 时，相对改动前新增的服务**必须同时写 `mem_limit` 与 `security_opt`。只查新增服务，历史老服务不重复报。走 Write/Edit/MultiEdit 能读改动前后内容精确比对；走 Bash 的 `sed -i`、`tee`、`>`/`>>`、`cp`、`mv`、heredoc 读不到，按目标文件名命中就提请确认。
- **对 `~/.claude/session-hygiene.json` 的 `exclusive` 清单容器做变更动作**，且该容器正在运行、本机另有活跃 Claude 会话时。清单每条要写 `container`、`service`、`project` 三字段才能命中三种写法。容器与端口按本机共享，不按项目隔离。
- **在宿主机上执行构建工具链**：`pnpm`、`npm`、`npx`、`yarn`、`bun`、`corepack`、`node`、`vite`、`tsc`、`vue-tsc`、`tsx`、`ts-node`、`webpack`、`mvn`、`mvnw`、`gradle`、`gradlew`、`java`、`javac`。要求名字处在命令起首位置，所以容器内的 `docker compose exec <服务> mvn test` 不拦。`python` 不在名单里——宿主机 python 只用于只读查看。

`wsl` 与 `powershell` 这类能塞 shell 文本的命令从工作树会话里发不出去（会话级守卫无法确认内部不执行 git），直接拒绝。`!` 前缀同样被拦，必须到 Claude Code 之外的普通终端执行。

判据实现见 `~/.claude/hooks/resource-guard.py`；断言套件 `~/.claude/hooks/tests/test_resource_guard.py`，127 条。耗时：普通命令 68 毫秒，heredoc 写文件 67 毫秒。判据二在子进程里替换独占清单、容器运行状态与活跃会话数三处读取，不照实机跑（照实机跑等于不测）。

## API 版本

- 本机 Docker Desktop 4.86 / Engine 29.7.2 要求 Docker API ≥1.44。testcontainers 1.21.2 携带的 docker-java 3.4.2 默认发 `/v1.32/...`，被 Engine 返回 400（响应体是零值 Info JSON）。
- 后果：`@Testcontainers(disabledWithoutDocker=true)` 测试**全部静默跳过**，Maven exit 0 假成功。看 `Tests run: N, Skipped: N` 才发现。
- 已修：`C:\Users\zys31\.docker-java.properties` 一行 `api.version=1.44`。
- **判断 Docker 可用性不能只看 `docker version`**，要看 surefire 是否 Skipped。同错两次即停，用 PowerShell `NamedPipeClientStream` 发原始 HTTP（`/v1.32/info` 400 vs `/v1.44/info` 200）定位协议层差异。

## 内存上限

- 容器级：compose 的 `mem_limit`。
- 整机级：`~/.wslconfig` 管整个 WSL2 虚拟机，改完必须 `wsl --shutdown` 才生效。校验：`docker info --format '{{.MemTotal}} {{.NCPU}}'`。2026-09-21 实测生效 `8327905280 8`（7.76 GiB / 8 核）。
- Docker Desktop 被 `wsl --shutdown` 带走后用 `docker desktop start` 拉回，docker 命令不受守卫限制。
