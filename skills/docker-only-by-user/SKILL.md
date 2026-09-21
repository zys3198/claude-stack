---
name: docker-only-by-user
description: 本机执行任何命令的去处：构建、测试、装依赖、跑脚本、格式化、生成产物、临时试代码、起服务一律放容器里，宿主机只做只读查看、git 操作与 docker 命令；含一次性容器模板、资源上限、代码来源指向、端口与独占资源归属
---

# 本机 Docker 使用约定

三条目的：

1. **限制占用**：单个容器不能吃光本机内存与进程数。
2. **只在容器内执行**：任何要执行的命令都放容器里，包括构建、测试、装依赖、跑脚本、格式化、生成产物、临时试代码、起服务。宿主机只做只读查看（读文件、列目录、查端口与进程）、git 操作与 docker 命令本身。
3. **安全性**：容器内进程不得提权；宿主机的独占资源（端口、容器、共享数据库）同一时刻只有一个使用者。

## 要执行命令时

宿主机不装工具链也不跑命令。按顺序选去处：

1. 项目里有对应服务：`docker compose -f deploy/docker-compose.local.yml run --rm <服务> <命令>`。
2. 项目里没有对应服务：起一个一次性容器。

```bash
docker run --rm \
  --memory 2g --memory-swap 2g --pids-limit 512 --cpus 2.0 \
  --security-opt no-new-privileges:true \
  -v "$(pwd)":/work -w /work \
  node:22-bookworm-slim \
  bash -lc "<命令>"
```

- 只读的活（看版本、读文件）挂载加 `:ro`：`-v "$(pwd)":/work:ro`。
- 命令要写文件时挂可写，产物落在工作树里，中间文件放 `.claude/tmp/`。
- 内存上限、进程数上限、CPU 上限与 `--security-opt no-new-privileges:true` 一个都不能省，取值按本机规格定。
- 一次性容器一律带 `--rm`，不留 `Exited` 状态的容器；常驻服务用 `docker compose up -d` 并登记台账。
- 需要新的工具链时装进镜像或一次性容器，不装到宿主机。

## 新项目接入

### 容器定义集中在一个入口目录

项目下建 `deploy/`，compose 文件、Dockerfile、nginx 配置、监控配置都放这里，仓库根不放容器定义。

代码来源用环境变量指向工作树，变量名按项目已有的前缀约定：

```yaml
services:
  backend:
    build:
      context: ${APP_CODE_ROOT:-..}/code/backend
```

一套容器同一时刻只服务一个会话。别人在用就先协商，协商不下来交给用户裁决。

### 每个服务写全资源字段

```yaml
services:
  example:
    mem_limit: ${APP_EXAMPLE_MEMORY_LIMIT:-512m}
    memswap_limit: ${APP_EXAMPLE_MEMORY_LIMIT:-512m}
    pids_limit: 256
    cpus: ${APP_EXAMPLE_CPU_LIMIT:-1.0}
    security_opt:
      - "no-new-privileges:true"
```

- `memswap_limit` 与 `mem_limit` 用同一个变量表达式。两者相等即完全禁用交换，内存超限时容器被终止；不相等时容器可以借交换空间顶着，上限形同虚设。
- 取值写成 `${VAR:-默认值}`，部署时按机器规格覆盖。
- 上限走顶层字段，不要写进 `deploy.resources.limits`。同一个服务里两者同时出现时，值必须逐字节相同才不报错；`pids_limit` 更严格，只要 `deploy.resources.limits` 在而里面没有同名项，`docker compose config` 就直接报 `can't set distinct values`。`deploy` 块只留 `reservations`。

### 端口只绑回环

发布到宿主机的端口一律写成 `127.0.0.1:${VAR:-port}:port`。端口配置要显式失败，不要顺延到下一个端口。

### 按需启动的服务用 profiles 分组

可选组件（缓存、消息队列、监控）挂 `profiles`，默认不启动，用到时命令行加 `--profile`。

### 容器内的自设上限要低于容器上限

redis 的 `--maxmemory`、JVM 堆上限这类容器内部的上限必须低于 `mem_limit`，否则容器会被整体终止，内部回收机制来不及起作用。

### 名称与端口登记到本机台账

容器名称、端口、独占资源写进 `~/.claude/session-hygiene.json`（跟着机器走，不进任何仓库）。占用前先看归属。

## 机械保证

`~/.claude/hooks/scripts/resource-guard.py` 挂在 `settings.json` 的 PreToolUse 上，拦截三类动作：compose 文件里新增的服务缺 `mem_limit` 或 `security_opt`；变更 `session-hygiene.json` 独占清单里正在运行、且本机另有活跃会话的容器；在宿主机上执行 pnpm、mvn、java、node 这类构建工具链。

判据细节、边界与已知覆盖不到的情形写在脚本头部注释里，要改判据就看那里。
