# JEV Browser 路线

需要正确性断言、跨脚本复用标签页或接管已有 Chrome 时读取本文件。固定脚本模式只用 JEV 通过 CDP 观察和操作页面，不调用 JEV `Agent`，不要求 TypeSafe 或文本模型密钥，也不把页面状态发送给外部模型。

## 执行流程

1. 读取项目验收清单和任务交接，列出本轮条目与完成条件。
2. 核对前端、后端、数据库和 CDP 浏览器状态。
3. 每轮重新查询 CDP 端点，设置 `BU_CDP_URL`；容器 IP 不复用上一轮的值。
4. 在 `$CLAUDE_JOB_DIR/tmp/` 写本轮脚本，全轮复用同一个标签页。
5. `observe(screenshot=False)` 取页面和动作表，按 `kind`、`label`、`value` 选动作，再用 `act(action, page, text=...)` 执行。
6. 每次点击或输入后重新 `observe()`；导航、弹窗或列表刷新后重新定位动作，不复用旧动作对象。
7. 页面文字、DOM 值、HTTP 状态、业务码、列表结果和二维码内容分别断言；页面显示“完成”不替代结果核对。
8. 截图、网络证据和日志脱敏后存项目规定的 `output/`，记录条目、步骤、期望、实际、证据路径和失败复现。

## 运行位置

项目有容器时优先在容器内执行：把包和脚本放进去，用 `uv run --no-sync python <脚本>.py`，`BU_CDP_URL` 指向容器网络里的 Chrome。容器内是 Linux，不需要 `PYTHONUTF8=1`。

没有容器时走宿主路径：

```bash
cd ~/.claude/tools/jev-ultrafast
PYTHONUTF8=1 BU_CDP_URL=http://localhost:9222 \
  uv run --no-sync python <脚本>.py
```

Windows 宿主必须设置 `PYTHONUTF8=1`：`browser.py` 用 `Path.read_text()` 读取 `snapshot.js`，默认 GBK 会导致 `UnicodeDecodeError`。临时探针浏览器可用 `docker run -d --rm -p 9222:9222 chromedp/headless-shell:latest`，用完停止。

## 最小形态

```python
from jev_ultrafast import Browser

browser = Browser.reuse("http://<目标>/")
try:
    page = browser.observe(screenshot=False)
    action = next(a for a in page["actions"]
                  if a["kind"] == "click" and "目标文案" in a.get("label", ""))
    browser.act(action, page)
    page = browser.observe(screenshot=False)
except Exception:
    ...  # 单条脚本失败不关 tab，留给下一条 reuse
```

## 标签页只能开一个

每轮第一条脚本就使用 `Browser.reuse`，整轮禁止 `Browser(url)`。未打补丁的 `Browser(url)` 每次都会创建新 target，且 `_remember(self.target)` 会覆盖 `TAB_FILE`，导致此前的 tab 无法被 `reuse` 找回。

`TAB_FILE` 位于 `$CLAUDE_JOB_DIR/tmp/.jev-page`，换 job 前要先收掉上一轮的 tab。脚本超时或最后一条脚本崩溃时，下一轮开始也要重新盘点孤儿页面。

只关闭本任务记下的 `targetId`，不要批量关闭，也不要按 URL 猜页面归属：列表里可能有用户手动打开的页面。

```python
from browser_harness.admin import ensure_daemon
from browser_harness.helpers import cdp

ensure_daemon()
for t in cdp("Target.getTargets")["targetInfos"]:
    if t.get("type") == "page":
        print(t["targetId"][:8], t.get("url", "")[:80])
cdp("Target.closeTarget", targetId="<本任务 targetId>")
```

daemon 单次 IPC 上限 5 秒。截图或长表达式可能超时，使用 `try/finally`，并靠下一条脚本的 `reuse` 收编上一条留下的 tab；整轮结束核对没有残留。挂起的 headless Chrome 容器同样要停止。

## 页面交互与验收

naive-ui 折叠面板、复选框和按钮需要真实鼠标事件；先取 `getBoundingClientRect()`，再派发 `mousePressed` 和 `mouseReleased`，不要依赖合成的 `element.click()`。每次页面变化后重新观察和定位。

权限验收使用真实数据库用户、角色和市场主体范围；开发登录旁路不构成通过证据。验收阶段只记录结果，不在页面操作中改业务代码；缺陷登记最小复现，回开发阶段处理。

本轮每个验收条目都要有 `passed`、`failed` 或 `not-run` 结果。通过项有可重复的页面或接口证据；失败项有最小复现、期望与实际差异和数据回滚结论；脚本、浏览器 tab 和临时资源在收尾时关闭或说明保留原因。
