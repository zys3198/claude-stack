# task-notes 的触发 hook，两模式配对使用。
#
#   pre   —— PreCompact(matcher auto)：自动压缩次数 +1，不输出。
#   start —— SessionStart(matcher compact)：压缩完成后读计数，达到阈值就提醒模型。
#
# 为什么拆成两个事件：PreCompact 与 PostCompact 的输出去向是 userDisplayMessage，
# 只显示给用户，进不了模型上下文；能把文字送进模型上下文的时点是 SessionStart。
# PreCompact 先于 SessionStart 触发，所以由它记数、由 SessionStart 读同一份状态文件。
#
# 只数自动压缩：手动 /compact 是用户主动发起，用户知道自己在丢什么。
# 这两个 hook 装上之前的压缩次数不计——计数从装上那一刻开始。

import json
import os
import sys
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
STATE_DIR = CLAUDE / "task-notes-reminder"
LOGFILE = CLAUDE / "task-notes-reminder.log"

REMIND_AT = 3
KEEP_FILES = 50

REMINDER = "你该开始笔记模式了：调用 task-notes。"
NOTICE = "笔记模式已开启"


def log(message):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGFILE, "a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def payload():
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    start = raw.find("{")
    return json.loads(raw[start:]) if start >= 0 else {}


def state_file(session):
    return STATE_DIR / session


def read_count(session):
    try:
        return int(state_file(session).read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return 0


def bump(session):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    count = read_count(session) + 1
    state_file(session).write_text(f"{count}\n", encoding="utf-8")
    entries = []
    for path in STATE_DIR.iterdir():
        try:
            entries.append((path.stat().st_mtime, path))
        except OSError:
            # 并发会话正在删同一个文件，跳过即可
            continue
    for _, path in sorted(entries)[:-KEEP_FILES]:
        try:
            path.unlink()
        except OSError:
            continue
    return count


def emit(count):
    print(json.dumps({
        "systemMessage": NOTICE,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": REMINDER,
        },
    }, ensure_ascii=False))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    data = payload()
    session = str(data.get("session_id") or "")
    if not session:
        log(f"{mode} payload 缺 session_id，键={sorted(data)}")
        return
    if mode == "pre":
        log(f"{session} 自动压缩计数 → {bump(session)}")
        return
    if mode != "start":
        log(f"未知模式 {mode!r}")
        return
    count = read_count(session)
    if count < REMIND_AT:
        return
    log(f"{session} 已自动压缩 {count} 次，提醒模型")
    emit(count)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
