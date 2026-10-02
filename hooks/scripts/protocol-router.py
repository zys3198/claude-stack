"""按动作与领域把协议推到模型眼前：本次涉及哪类事，对应协议在哪。

判据只有两张表，都写在本文件里；改路由只改表，不改流程。

输出一律是**事实陈述句**。官方明确警告：写成 out-of-band 的系统命令会触发
Claude 的提示注入防御，反而把这段文本表面化给用户看、当不成上下文。

两个事件分两张表，因为匹配依据和到达时机都不同：

| 事件 | 匹配依据 | 到达时机 |
|---|---|---|
| UserPromptSubmit | 用户输入的自然语言 | 任务起点——唯一能在「动手前」到达的非拦截通道 |
| PreToolUse | tool_name + tool_input | 工具结果旁；模型读到它时本次工具已经跑完 |

PreToolUse 因此只能影响同一类动作的后续几次，对一次性高风险动作（`git push`、
`rm -r`）太晚——那是 deny/ask 才拦得住的范围，本脚本刻意不管。

节流：按 session 记已提示过的协议，每份每会话只出一次。否则一次会话里编辑
20 个文件就是 20 条注入。并行会话各自独立，互不清空对方的状态。
"""

import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# 夹具测试用 CLAUDE_ASSET_ROOT 指向临时树，与 protocol-report.py 同一约定。
ROOT = os.path.abspath(os.environ.get("CLAUDE_ASSET_ROOT")
                       or os.path.join(os.path.expanduser("~"), ".claude"))
LOGFILE = os.path.join(ROOT, "hooks", "protocol-router.log")
# hooks/*_state.json 在 .gitignore 里，状态文件不会弄脏 ~/.claude 仓库。
STATE = os.path.join(ROOT, "hooks", "protocol_router_state.json")
KEEP_SESSIONS = 10
MAX_CHARS = 800

# 协议 key → (相对 ~/.claude 的路径, 一句话说它管什么)。触发词里出现的路径都取自这里。
PROTOCOLS = {
    "instruction-assets": (
        "docs/protocols/instruction-assets/instruction-assets.md",
        "指令资产（CLAUDE.md／AGENTS.md／SKILL.md／协议文档）的类型判定、唯一入口、元数据与维护判据",
    ),
    "memory": (
        "docs/protocols/memory/memory.md",
        "记忆的进退判据、frontmatter 字段与索引维护",
    ),
    "delegation": (
        "docs/protocols/delegation/delegation.md",
        "子代理派发的边界、契约字段与配置确认门禁",
    ),
    "ledger": (
        "docs/protocols/ledger/ledger.md",
        "安装资产的来源、位置、状态与恢复路径登记",
    ),
    "collaboration": (
        "docs/protocols/collaboration/collaboration.md",
        "该不该问用户、方案怎么给、改动范围与纠正的处理",
    ),
    "execution-env": (
        "docs/protocols/execution-env/execution-env.md",
        "构建、测试、跑脚本与起服务的容器流程与宿主机边界",
    ),
    "evidence": (
        "docs/protocols/evidence/evidence.md",
        "证据分级、三层完成判定与交付前检查",
    ),
    "expression": (
        "docs/protocols/expression/expression.md",
        "中文用词、符号选取与用户原文保留",
    ),
    "gate": (
        "docs/protocols/gate/gate.md",
        "R0–R4 影响等级、必须确认清单与授权范围字段",
    ),
    "task-notes": (
        "docs/protocols/task-notes/task-notes.md",
        "跨会话任务的状态记录字段与更新时机",
    ),
    "session-lifecycle": (
        "docs/session-lifecycle.md",
        "会话与资源回收、工作树收尾的护栏",
    ),
    "protocols-index": (
        "docs/protocols-index.md",
        "产物落点按可重建性分、命名三段制与维护条款",
    ),
}

# 表一：用户输入里的领域词。匹配的是自然语言，注定有漏有误——漏了等于没做，
# 误了只是多说一句，所以宁可宽一点。
PROMPT_ROUTES = (
    (re.compile(r"CLAUDE\.md|AGENTS\.md|SKILL\.md|skill\s*文档|指令资产|新增\s*skill|改写?\s*skill"), "instruction-assets"),
    (re.compile(r"记忆|memory|记住"), "memory"),
    (re.compile(r"子代理|派发|委派|并行|subagent|开几个\s*agent"), "delegation"),
    (re.compile(r"安装|卸载|插件|plugin|MCP|CLI"), "ledger"),
    (re.compile(r"删除|删掉|清掉|不可恢复|移除"), "collaboration"),
    (re.compile(r"跑测试|构建|编译|起服务|启动服务|容器|docker|pytest|gradle|mvn"), "execution-env"),
    (re.compile(r"报告|结论|交付|验收|证据"), "evidence"),
    (re.compile(r"写文档|措辞|提交信息|回复|文案"), "expression"),
    (re.compile(r"部署|发布|生产环境|推到远程|git\s+push|(?<![A-Za-z])(?:MR|PR)(?![A-Za-z])"), "gate"),
    (re.compile(r"接手|继续上次|跨会话|笔记|STATE\.md"), "task-notes"),
    (re.compile(r"收尾|清理|工作树|worktree|会话"), "session-lifecycle"),
    (re.compile(r"放哪|命名|归档|落点"), "protocols-index"),
)

# 表二：工具与参数。匹配的是结构化动作，不猜意图。
EDIT_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash", "PowerShell")
# Agent 在 v2.1.63 由 Task 改名；官方只承诺 settings 与 agent 定义认旧名，
# hook matcher 认不认没有明文，所以两个都收。
AGENT_TOOLS = ("Agent", "Task")

GATE_CMD = re.compile(r"git\s+push|git\s+fetch|git\s+pull|gh\s+pr|gh\s+mr")
DESTRUCTIVE_CMD = re.compile(r"rm\s+-[rRf]|git\s+worktree\s+remove|git\s+branch\s+-D|git\s+reset\s+--hard|git\s+clean")
ENV_CMD = re.compile(r"docker|docker-compose|npm|pnpm|yarn|pytest|gradle|\bmvn\b")
INSTALL_CMD = re.compile(r"claude\s+plugin|npm\s+(?:i|install)\s+-g|winget\s+install|scoop\s+install|choco\s+install|pipx\s+install")


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
    except OSError:
        pass


def dedupe(keys):
    return list(dict.fromkeys(keys))


def route_prompt(text):
    """用户输入命中的协议。返回 key 列表，可能多于一个。"""
    if not text:
        return []
    return dedupe([key for pattern, key in PROMPT_ROUTES if pattern.search(text)])


def route_tool(tool_name, tool_input):
    """本次工具调用命中的协议。返回 key 列表，可能多于一个。"""
    name = tool_name or ""
    tool_input = tool_input or {}
    keys = []
    if name in EDIT_TOOLS:
        keys.extend(_route_edit(tool_input))
    elif name in SHELL_TOOLS:
        keys.extend(_route_shell(str(tool_input.get("command") or "")))
    elif name in AGENT_TOOLS:
        keys.append("delegation")
    return dedupe(keys)


def _route_edit(tool_input):
    """按被写文件的路径判。三种工具给的字段名不同，与 protocol-report.py 同一套取法。"""
    path = ""
    for field in ("file_path", "notebook_path", "path"):
        value = tool_input.get(field)
        if isinstance(value, str) and value.strip():
            path = value
            break
    if not path:
        return []
    norm = path.replace("\\", "/").lower()
    base = norm.rsplit("/", 1)[-1]
    keys = []
    if base in ("claude.md", "agents.md", "skill.md") or "/docs/protocols" in norm:
        keys.append("instruction-assets")
    if "/memory/" in norm or base == "memory.md":
        keys.append("memory")
    if "/notes/" in norm:
        keys.append("task-notes")
    return keys


def _route_shell(command):
    keys = []
    if GATE_CMD.search(command):
        keys.append("gate")
    if DESTRUCTIVE_CMD.search(command):
        keys.append("collaboration")
    if ENV_CMD.search(command):
        keys.append("execution-env")
    if INSTALL_CMD.search(command):
        keys.append("ledger")
    return keys


def message(keys, event):
    """写成事实句：陈述涉及哪些协议、各管什么，不写成命令。"""
    lead = "本次请求涉及以下协议：" if event == "UserPromptSubmit" else "本次动作涉及以下协议："
    lines = [f"- `~/.claude/{PROTOCOLS[key][0]}` —— {PROTOCOLS[key][1]}" for key in keys]
    return (lead + "\n" + "\n".join(lines))[:MAX_CHARS]


def state_read():
    try:
        with open(STATE, encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def seen(session):
    return set(state_read().get(session) or ())


def remember(session, keys):
    """记下本会话已经提示过的协议，并把过老的会话清掉。

    ponytail: 按插入顺序留最近 KEEP_SESSIONS 个，不记真实时间戳——被误清的
    活跃会话最多重复提示一次，为准确的时间序维护额外字段不值当。
    """
    data = state_read()
    data[session] = sorted(set(data.get(session) or ()) | set(keys))
    for stale in list(data)[:-KEEP_SESSIONS]:
        data.pop(stale, None)
    try:
        with open(STATE, "w", encoding="utf-8") as handle:
            json.dump(data, handle)
    except OSError:
        pass


def emit(event, text):
    """hookEventName 必须与 additionalContext 同层：缺了它 Claude Code 会静默忽略。"""
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": event, "additionalContext": text},
    }, ensure_ascii=False))


def main():
    # stdin/stdout 要显式指定 UTF-8：本机默认编码是 GBK，表一全按中文词匹配，
    # 解成乱码后一个字都命中不了，而且不报错。
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return
    event = payload.get("hook_event_name") or ""
    session = payload.get("session_id") or ""
    if event == "UserPromptSubmit":
        keys = route_prompt(str(payload.get("prompt") or payload.get("user_prompt") or ""))
    elif event == "PreToolUse":
        keys = route_tool(payload.get("tool_name"), payload.get("tool_input"))
    else:
        return
    fresh = [key for key in keys if key not in seen(session)]
    if not fresh:
        return
    remember(session, fresh)
    log(f"{event} {' '.join(fresh)}")
    emit(event, message(fresh, event))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 路由器出错绝不能连累用户这次请求或工具调用
        log(f"未捕获异常：{exc!r}")
    sys.exit(0)
