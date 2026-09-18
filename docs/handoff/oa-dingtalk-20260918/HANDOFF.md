# OA 钉钉集成验收 —— 接续交接（2026-09-18）

面向下一个会话：环境、凭证、绑定、事件链路都已就位，**不要重新配置**，直接从「未完成任务」一节接着跑。

## 1. 环境现状（已经跑起来了，可直接用）

| 项 | 值 |
|---|---|
| 工作树 | `C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance` |
| 分支 | `oa-finance`，HEAD `07b5fc05`，与 `origin/oa-finance` 同步（无未推送提交） |
| 工作区 | 干净，仅两个未跟踪目录 `code/frontend/soybean-admin/prototype/` 与 `.impeccable/`（早前界面设计产物，未纳入提交） |
| Compose 项目 | `deploy`，从工作树的 `deploy/` 目录发起 |
| 端口 | 3306 MySQL、9540 后端、80 nginx、9527 Vite 开发服务器、8866 paddleocr、18081 finance-invoice-ocr |
| 容器状态 | 全部 healthy，`deploy-backend-java-1` 已是含本次修复的镜像 |

重启后端（会重读 `env_file`，改环境变量后必须用它，普通 `up -d` 不生效）：

```bash
cd "C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance/deploy"
docker compose -f docker-compose.local.yml -f docker-compose.dingtalk-local.yml up -d --force-recreate backend-java
```

重建镜像（改了后端代码时）：

```bash
cd "C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance/deploy"
docker compose -f docker-compose.local.yml -f docker-compose.dingtalk-local.yml build backend-java
```

Vite 开发服务器 9527 若已停，重启命令：

```bash
cd "C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance/code/frontend/soybean-admin" && pnpm dev
```

## 2. 凭证与配置（已就位，不要再动）

- 钉钉凭据在 `deploy/.env.dingtalk.local`（被 `.gitignore` 忽略，不入库），由 `deploy/docker-compose.dingtalk-local.yml` 经 `env_file` 注入。**不要打印该文件内容。**
- 绑定级 AppSecret 变量名规则：`DTSF_DINGTALK_<绑定编码大写>_APP_SECRET`，后端用 `System::getenv` 取值。
- 钉钉后台三项已确认：事件订阅为 Stream 模式、应用凭证已取得、AgentId 已写入绑定。
- 登录账号：`admin_mgr`，口令走 `DTSF_DEFAULT_PASSWORD`（未设置时的默认值，见 `AuthService.java`；本机未设置该变量）。登录脚本 `login.py` 自动解验证码。
- 钉钉侧未确认：应用权限页里免登与工作通知两项的名称（用户未能找到对应条目，不影响通讯录与事件链路）。

## 3. 已完成并已验证（不要重跑）

| 项 | 证据位置 |
|---|---|
| Stream 长连接建立 | 后端日志 `钉钉 Stream 长连接已建立: bindingCode=OA_MAIN`；绑定接口 `streamConnected=true` |
| 连接测试 | `ok=true`、`tokenAcquired=true`、`directoryReadable=true` |
| 全量同步 | 部门 5 条、人员 4 条全部新增，待激活 4，冲突 0 |
| 事件自动入队（AT-21 核心） | `oa_dingtalk_directory_events` 1 条 `org_dept_modify` 状态 `completed`；`oa_dingtalk_department_sync_batches.trigger_type=event`；部门映射名同步为钉钉侧新名 |
| 绑定配置 | `OA_MAIN` 四个能力开关全开、AgentId 已写入、`secretConfigured=true` |

代码改动见提交 `15185480`（Stream 长连接替换 HTTP 回调）与 `07b5fc05`（事件实体标识字段匹配修复）。文档改动见 `docs/04-management/OA钉钉集成功能使用说明.md` 与 `docs/04-management/OA钉钉集成前端改善设计.md`。

## 4. 未完成任务

用例编号对应 `docs/04-management/OA钉钉集成功能使用说明.md` 的 AT-01～AT-39。

| 任务 | 用例 | 前置 | 阻塞点 |
|---|---|---|---|
| A 恢复页面核验手段 | — | 无 | `agent-browser` 守护进程两次挂起（`open` 调用超时），界面用例目前无工具核验。先 `agent-browser close --all` 终止守护进程再重建会话；仍不可用则改为让用户手工点页面，逐条给核对清单 |
| B 企业绑定段 | AT-14～AT-20、AT-22～AT-26（12 条） | 依赖 A | AT-22 需另建两个绑定：一个引用未注入的变量名，一个引用值错误的 AppSecret（错误值写进 `.env.dingtalk.local` 后重建容器） |
| C 通讯录激活段 | AT-27～AT-32（6 条） | 依赖 A | 已有 4 名待激活人员、5 条 `enabled` 部门映射 |
| D 页签判权 | AT-13（1 条） | 需另备一个只具备 `oa:dingtalk:sync` 的账号 | 账号未准备 |
| E 工作通知段 | AT-05～AT-08、AT-33～AT-37（9 条） | 需业务侧先触发消息产生投递数据 | 投递队列表当前为空；会真发钉钉消息给真实员工，开跑前必须确认允许的收件人范围 |
| F 免登段 | AT-01～AT-04（4 条） | 需在钉钉客户端内操作，且需先把一名员工激活并绑定本地账号 | 依赖 C 先跑完 |
| G 免打扰与移动协同 | AT-09～AT-12（4 条） | 依赖消息链路可投递 | 同 E |
| H 薪酬钉钉记录 | AT-38～AT-39（2 条） | 当前考勤记录 0 条、原始快照 0 条 | 需先跑出考勤同步数据并构造已确认考勤终态的薪酬期间 |
| I 收尾 | — | 全部跑完 | 手册 §9 验收结论记录与缺陷登记；停自启进程、清理工作树 |

依赖链：A 挡 B 与 C 共 18 条界面用例；C 挡 F；E 与 G 共用消息链路可合并成一批；H 自成一段；D 只等一个账号。

建议顺序：A → B → C → D → E/G → F → H → I。

## 5. 已知缺陷（收尾时写进手册 §9）

| 编号 | 现象 | 复现 | 状态 |
|---|---|---|---|
| 待登记 | 缺少必填参数时返回 HTTP 500 而非 400 | `GET /api/oa/dingtalk-messages/templates` 与 `/outbox` 不带 `bindingCode` | 未修 |
| 已修 | 通讯录事件被误判为缺少实体标识 | 钉钉事件体字段是小驼峰 `deptId`，原实现按 `DeptId` 精确匹配 | 提交 `07b5fc05` |

## 6. 边界（必须遵守）

- 只推 `oa-finance` 功能分支；`main`、`develop` 禁止推送；不要合入 `develop`。
- MR `!96` 仍是 opened，不要自行合并或关闭。
- 不要触碰仓库里的 18 条 stash；不要动工作树 `C:/ZYS/Code/dtsf-oa-dingtalk-qa`。
- 报告只写 HTTP 状态、业务码、存在性与聚合计数；不得输出 Token、AppSecret、AES Key、手机号、钉钉用户标识。
- 发钉钉消息属对外发送，批量发送前必须让用户确认收件人范围。

## 7. 现成工具（已放在本目录，直接可用）

| 文件 | 用途 |
|---|---|
| `login.py` | 登录取 token，自动解图片验证码，用法 `python login.py admin_mgr <口令> session.json` |
| `apicheck.py` | 批量只读接口探测，用法 `python apicheck.py session.json` |
| `binding_state.py` | 打印绑定列表关键字段（含 `streamConnected`、`secretConfigured`） |
| `set_binding_switches.py` | 改能力开关，用法 `python set_binding_switches.py session.json 开关名=true ...` |
| `set_agent_id.py` | 写 AgentId 到绑定 |
| `dingtalk_directory_check.py` | 连接测试与全量同步，用法 `python ... session.json test|sync` |
| `setup_dingtalk_binding.py` | 建市场主体与绑定（AT-22 造第二个绑定时可改编码复用） |
| `dbq.sh` | 只读 SQL，用法 `bash dbq.sh "SELECT ..."`，密码从 `deploy/.env` 读取不打印 |

所有 Python 脚本都禁用系统代理（`ProxyHandler({})`），否则访问 127.0.0.1 会被代理拦成 403。

## 8. 建议调用的 skills

- `code-change-workflow`：本轮还要改后端代码（AT-22 造错误密钥绑定、缺陷修复）时按它的流程走。
- `agent-browser`：任务 A 要用它恢复页面核验；先 `agent-browser skills get core` 取当前版本用法。
- `dev-status`：新会话开工前用它看清活跃会话、工作树、端口与容器归属，避免和别的会话抢端口。
- `dev-clean`：收尾时清掉无会话占用的空工作树。

## 9. 参考产物

- 验收手册与用例：`docs/04-management/OA钉钉集成功能使用说明.md`（§4 功能说明、§6 直连接口、§8 数据清单、§9 验收结论记录）
- 前端设计文档：`docs/04-management/OA钉钉集成前端改善设计.md`
- 本轮提交：`15185480`、`07b5fc05`（分支 `oa-finance`）
- 本机环境事实（端口、凭据注入方式、账号口令来源）：`~/.claude/projects/C--ZYS-Code-dtsf/memory/dingtalk-local-acceptance-instance-20260918.md`
