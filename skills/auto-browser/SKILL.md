---
name: auto-browser
description: 操作网页、抓取页面数据或执行页面／EAM 验收时使用；通用任务走 agent-browser，需要正确性断言、接管已有浏览器或复用标签页时走 JEV Browser。
---
# auto-browser

## 路由

| 任务 | 路线 | 必读资料 |
|---|---|---|
| 通用网页操作、抓取、截图、Electron、Slack | A：agent-browser | [`references/agent-browser.md`](references/agent-browser.md) |
| 页面验收要确认正确元素、跨脚本复用标签页、接管已有 Chrome | B：JEV Browser | [`references/jev-browser.md`](references/jev-browser.md) |

先按任务选一条路线，不把两条路线混用。命中路线后，执行前必须读取对应资料；资料包含当前版本命令、运行位置、失败处理和收尾要求。

## 公共硬门禁

- 选择 JEV 路线时只用固定脚本和 CDP 观察/操作，不调用 JEV `Agent`，不把页面状态发送给外部模型。
- JEV 每轮第一条脚本就使用 `Browser.reuse`，整轮禁止 `Browser(url)`；每次点击或输入后重新 `observe()`，页面变化后重新定位动作。
- 页面文字、DOM 值、HTTP 状态、业务码、列表结果和二维码内容分别核对；页面显示“完成”不替代业务结果证据。
- 权限验收使用真实数据库用户、角色和市场主体范围；开发登录旁路不构成通过证据。验收阶段只记录结果，不在页面操作中改业务代码。
- 凭据从安全输入或安全文件读取，不写入脚本、截图、终端输出、任务笔记或验收清单；网络证据过滤 `Authorization`、`Cookie`、令牌、密码和 HMAC 密钥。

## 完成条件

- 本轮每个验收条目都有 `passed`、`failed` 或 `not-run` 结果。
- 通过项有可重复的页面或接口证据；失败项有最小复现、期望与实际差异和数据回滚结论。
- 脚本进程、浏览器标签页和临时资源在整轮收尾时关闭；保留项写清原因。
- 结果回写项目验收清单；未完成项明确交接给下一会话。
