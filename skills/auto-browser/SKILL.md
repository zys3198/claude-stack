---
name: auto-browser
description: 操作网页、抓取页面数据或执行页面／EAM 验收时使用；通用任务走 agent-browser，需要正确性断言、接管已有浏览器或复用标签页时走 JEV Browser。
---

# auto-browser

两条路线按任务选，不是替代关系：

| 任务 | 路线 |
|---|---|
| 通用网页操作、抓取、截图、Electron、Slack | A：agent-browser |
| 页面验收要确认「确实点到了正确元素」、跨脚本复用标签页、接管已有 Chrome | B：JEV Browser |

## 路线 A：agent-browser

先取用法。CLI 自带随版本更新的正文，不要凭记忆写命令：

```bash
agent-browser skills get core            # 工作流、常见模式、排错
agent-browser skills get core --full     # 附完整命令参考
agent-browser skills list                # 当前版本装了哪些子 skill
```

### Windows 三个坑（实测）

1. **管道会挂死**。daemon 首次启动时继承当次命令的 stdout 句柄且不释放，`agent-browser … | cat` 让读端永远等不到 EOF（输出其实早打印完了）。
   → 一律**重定向到文件再读**。重定向实测零开销（161–170ms）。
2. 直接调原生 exe（约 165 ms），**不经过 Git Bash 的 `sh → node → exe` 包装**（约 400 ms）：
   `%APPDATA%\npm\node_modules\agent-browser\bin\agent-browser-win32-x64.exe`，或 `.cmd` 入口。
3. **每个 namespace 的第一条命令必须重定向**，否则 daemon 带着坏句柄活下来污染后续。中招后 `agent-browser doctor --fix`，并清掉对应 user-data-dir 的 Chrome。

批量用 `batch` 摊薄启动开销（3 条约 212 ms）。

## 路线 B：JEV Browser

固定脚本模式：**不调用 JEV `Agent`**，不要求 TypeSafe 或文本模型密钥，不把页面状态发送给外部模型。脚本拥有验收步骤和断言，JEV 只负责通过 CDP 观察和操作页面。

### 执行流程

1. 读项目验收清单和任务交接，列出本轮要执行的条目与完成条件。
2. 核对前端、后端、数据库和 CDP 浏览器状态。
3. 取当前 CDP 端点设 `BU_CDP_URL`；容器 IP 会变，每轮重新查询，不要复用上一轮的过期值。
4. 在 `$CLAUDE_JOB_DIR/tmp/` 写本轮脚本，全轮复用同一个标签页。
5. `observe(screenshot=False)` 取页面和动作表，按 `kind`、`label`、`value` 选动作，再 `act(action, page, text=...)` 执行。
6. 每次点击或输入后重新 `observe()`；页面导航、弹窗或列表刷新后重新定位动作，不复用旧的动作对象。
7. 页面文字、DOM 值、HTTP 状态、业务码、列表结果和二维码内容各自独立断言；页面显示「完成」不替代结果核对。
8. 截图、网络证据和日志脱敏后存项目规定的 `output/`，记录条目、步骤、期望、实际、证据路径和失败复现。

### 在哪运行

按项目规则优先容器：把包和脚本放进去，在容器内 `uv run --no-sync python <脚本>.py`，`BU_CDP_URL` 指向容器网络里的 Chrome。容器内是 Linux，**不需要** `PYTHONUTF8=1`。

没有容器时走宿主路径（2026-09-24 实测通过）：

```bash
cd ~/.claude/tools/jev-ultrafast
PYTHONUTF8=1 BU_CDP_URL=http://localhost:9222 \
  uv run --no-sync python <脚本>.py
```

- **`PYTHONUTF8=1` 必需**。`browser.py` 用 `Path.read_text()` 读 `snapshot.js`，Windows 默认走 GBK 解码，抛 `UnicodeDecodeError`。上游只在 Linux 容器跑过，宿主必须带这个变量。
- 临时探针浏览器：`docker run -d --rm -p 9222:9222 chromedp/headless-shell:latest`，用完 `docker stop`。

### 最小形态

```python
from jev_ultrafast import Browser

browser = Browser.reuse("http://<目标>/")   # 不要用 Browser(url)
try:
    page = browser.observe(screenshot=False)
    action = next(a for a in page["actions"]
                  if a["kind"] == "click" and "目标文案" in a.get("label", ""))
    browser.act(action, page)
    page = browser.observe(screenshot=False)
except Exception:
    ...  # 单条脚本失败不关 tab，留给下一条 reuse
```

### 标签页只能开一个

未打补丁的 `Browser(url)` 每次无条件 `Target.createTarget`（`browser.py:41`），一条脚本一个页面；`background=True` 创建，不抢焦点，不会自己冒出来被发现。

**比多开更糟的是失联**：`__init__` 和 `reuse` 都走 `_open()`，而 `_open()` 结尾 `_remember(self.target)` 会**覆盖** `TAB_FILE`。所以一条脚本写了 `Browser(url)`，此前那个 tab 的 id 就被冲掉，`reuse` 再也找不回来——一条违规脚本 = 一个不可恢复的孤儿。

规则：

- **每一轮的第一条脚本就用 `Browser.reuse`，整轮只用它**，`Browser(url)` 一次都不写。
- 跨 job 接不上：`TAB_FILE` 是 `$CLAUDE_JOB_DIR/tmp/.jev-page`，换 job 路径就变，读不到旧 id。换 job 前先用下方清单把上一轮的 tab 收掉。
- 最后一条脚本崩了 `finally` 可能没跑到，tab 会在下一轮变成孤儿。每轮开始前也数一遍，不要只在收尾数。

### 标签页清单与收尾

```python
from browser_harness.admin import ensure_daemon
from browser_harness.helpers import cdp

ensure_daemon()
for t in cdp("Target.getTargets")["targetInfos"]:
    if t.get("type") == "page":
        print(t["targetId"][:8], t.get("url", "")[:80])
cdp("Target.closeTarget", targetId="<本任务 targetId>")
```

只关自己记下的 targetId。清单里混着用户手动开的页面，所以不能批量关、也不能按 URL 猜——列出来人工认，只关认得出是本任务的。

daemon 单次 IPC 上限 5 秒：截图或长表达式会超时，超时后 `finally` 可能来不及执行。用 `try/finally` 兜底，靠下一条脚本的 `reuse` 收编上一个 tab，一轮结束用清单核对没有残留。挂着的 headless Chrome 容器同理——用完就停。

### 点 naive-ui 组件要用真鼠标事件

折叠面板、复选框、按钮只认真实指针事件序列，合成 `element.click()` 不触发折叠展开。先 `evaluate` 取 `getBoundingClientRect()`，再在 rect 中心派发一对事件：

```python
def click_at(browser, x, y):
    browser.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
    browser.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
```

目标藏在折叠区里就先点开表头——点中按钮才算找到。`browser.evaluate(expr)` 只收表达式，传不了 `arguments`：要一次回多个值时把 JS 包成 IIFE 返回对象。

### 验收约束

- 权限验收使用真实数据库用户、角色和市场主体范围；开发登录旁路不构成权限通过证据。
- 验收阶段只记录结果，不在页面操作中改业务代码；发现缺陷登记最小复现，回开发阶段处理。

### 完成标准

- 本轮指定的每个验收条目都有「通过、失败或未执行」结果。
- 通过项有可重复的页面或接口证据；失败项有最小复现、期望与实际差异和数据回滚结论。
- 脚本进程、浏览器标签页和临时资源在整轮收尾时关闭；保留的标签页写清保留原因。
- 结果已回写项目验收清单；未完成项明确交接给下一会话。

## 公共约束

- 凭据从安全输入或安全文件读取，不写入脚本、截图、终端输出、任务笔记或验收清单。
- 网络证据过滤 `Authorization`、`Cookie`、令牌、密码和 HMAC 密钥。
