"""资产判据的传输层：把刚写的路径转达给检查器，把结论转达回去。

判据一条都不在这里——八类全在 protocol_check.py，改判据只改那一处。
只在常驻区与原则区（`CLAUDE.md`、`rules/*.md`）阻断，其余区仍然只报告；
阻断面由检查器的 BLOCK_SCOPE 决定，这里只按它的退出码行动，不自己判。

| 事件 | 动作 | 出声条件 |
|---|---|---|
| PreToolUse | 查「这次写完之后的样子」（退出码 3） | 命中落在阻断区 → 拒这次写入 |
| PostToolUse | 只查被写的那个文件 | 该文件有命中 |
| Stop | 跑全量只读报告 | 本会话写过资产，且命中与上次不同 |

沉默是默认：路径不在 ~/.claude 内、无命中、检查器自身出错，都不出声。
检查器的错误不往上抛——它坏了不该连累写文件，也不该拦住用户想写的文件。
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "protocol_check.py")
# 被查的根，与检查器的 --root 同一用途：夹具测试用 CLAUDE_ASSET_ROOT 指向临时树。
ROOT = os.path.abspath(os.environ.get("CLAUDE_ASSET_ROOT")
                       or os.path.join(os.path.expanduser("~"), ".claude"))
LOGFILE = os.path.join(ROOT, "hooks", "protocol-report.log")
# hooks/*_state.json 在 .gitignore 里，状态文件不会弄脏 ~/.claude 仓库。
STATE = os.path.join(ROOT, "hooks", "protocol_report_state.json")
TIMEOUT = 60
MAX_CHARS = 4000


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
    except OSError:
        pass


def state_read():
    try:
        with open(STATE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def state_write(**fields):
    try:
        with open(STATE, "w", encoding="utf-8") as handle:
            json.dump(state_read() | fields, handle)
    except OSError:
        pass


def run_checker(args):
    """跑检查器，返回 (退出码, 输出)。起不来就当作检查器出错。"""
    try:
        done = subprocess.run(
            [sys.executable, CHECK, "--root", ROOT] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT,
        )
        return done.returncode, (done.stdout or "") + (done.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"检查器没跑起来：{exc}")
        return None, ""


def written_path(payload):
    """这次工具调用写的文件。Write/Edit 是 file_path，NotebookEdit 是 notebook_path。"""
    tool_input = payload.get("tool_input") or {}
    for key in ("file_path", "notebook_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def under_root(path):
    return os.path.normcase(os.path.abspath(path)).startswith(os.path.normcase(ROOT + os.sep))


def emit(event, text):
    """写给谁看决定用哪个字段：写文件时报给模型（它当场能改），回合结束报给用户。"""
    if event == "PostToolUse":
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": event, "additionalContext": text},
        }, ensure_ascii=False))
    else:
        print(json.dumps({"systemMessage": text}, ensure_ascii=False))


def proposed_text(payload, path):
    """这次写入之后该文件的内容；判不出来返回 None。

    Write 直接给整份内容；Edit 按 old/new 复原，MultiEdit 逐条复原。复原不准也不要紧：
    old_string 对不上时，Edit 本身就会失败，根本写不进去。NotebookEdit 不认内容。
    """
    tool_input = payload.get("tool_input") or {}
    content = tool_input.get("content")
    if isinstance(content, str):
        return content
    edits = tool_input.get("edits")
    if not isinstance(edits, list):
        edits = [tool_input]
    try:
        with open(path, encoding="utf-8", errors="replace", newline="") as handle:
            text = handle.read()
    except OSError:
        return None
    for edit in edits:
        old, new = edit.get("old_string"), edit.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or not old:
            return None
        text = text.replace(old, new, -1 if edit.get("replace_all") else 1)
    return text


def deny(reason):
    """拒绝这次工具调用。形状沿用 product-guard.py 的既有 deny 契约。"""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=False))


def pre_tool_use(payload):
    """写入前判定：命中落在阻断区就拒。判的是「这次写完之后的样子」。

    只有检查器的退出码 3 才拒（3 = 命中在阻断区）。其余情况一律放行：
    拦不住是小事，误拦会挡掉用户正要写的文件，检查器自己坏了更不该拦。
    """
    path = written_path(payload)
    if not path or not under_root(path):
        return
    text = proposed_text(payload, path)
    if text is None:
        return
    try:
        fd, temp = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    except OSError as exc:
        log(f"预览文件写不出来：{exc}")
        return
    try:
        code, out = run_checker(["--file", path, "--content", temp])
    finally:
        try:
            os.unlink(temp)
        except OSError:
            pass
    if code != 3:
        return
    rel_path = os.path.relpath(path, ROOT).replace(os.sep, "/")
    findings = [line.strip() for line in out.splitlines() if line.strip().startswith("✗")]
    reason = (f"资产判据拦下这次写入：{rel_path}\n" + "\n".join(findings)
              + "\n\n这条只在常驻区与原则区拦。改到没有命中再写。")
    log(f"deny: {rel_path}｜{' · '.join(findings)[:400]}")
    deny(reason[:MAX_CHARS])


def post_tool_use(payload):
    path = written_path(payload)
    if not path or not under_root(path) or not os.path.isfile(path):
        return
    code, out = run_checker(["--file", path])
    state_write(session=payload.get("session_id") or "")
    if code not in (1, 3):
        return
    emit("PostToolUse", f"资产判据（刚写 {os.path.relpath(path, ROOT)}）\n{out.strip()[:MAX_CHARS]}")


def stop(payload):
    """全量只读报告。本会话没写过常驻资产就不跑——那样报告与上次一模一样。

    ponytail: 全量一次约 2.6 秒（其中密钥扫描 2.5 秒，2670 个文件）。
    按整会话缓存结果；要做到「每次 Stop 都精确实时」得给密钥扫描建增量索引。
    """
    state = state_read()
    if not state.get("session") or state["session"] != (payload.get("session_id") or ""):
        return
    code, out = run_checker([])
    if code not in (1, 3):
        return
    digest = hashlib.sha256(out.encode("utf-8")).hexdigest()
    if digest == state.get("digest"):
        return
    state_write(digest=digest)
    emit("Stop", f"资产判据 全量报告\n{out.strip()[:MAX_CHARS]}")


def main():
    # stdin 也要显式指定 UTF-8：本机默认编码是 GBK，含中文的 payload 会被解成乱码。
    # 乱码不报错——Write 路会把乱码当内容写进预览（体量涨 1.5 倍），
    # Edit 路的 old_string 与按 UTF-8 读到的文件内容对不上，复原直接失效。
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
    if event == "PreToolUse":
        pre_tool_use(payload)
    elif event == "PostToolUse":
        post_tool_use(payload)
    elif event == "Stop":
        stop(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # 传输层出错只记日志，绝不阻断工具调用或结束
        log(f"未捕获异常：{exc!r}")
    sys.exit(0)
