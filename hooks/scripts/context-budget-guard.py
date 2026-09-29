# hook：上下文用量逼近 smart zone 终点时，提醒更新接续笔记。
#
# 当前挂 PostToolUse（见 installing/custom-setup.md 的位置列；改挂 UserPromptSubmit
# 也成立，本文件不依赖接线位置——事件名从 payload 里读）。
#
# 输出**必须**是 JSON 的 `hookSpecificOutput.additionalContext`，不能是裸 print。
# 2026-09-29 实测订正：除 UserPromptSubmit／UserPromptExpansion／SessionStart／
# PostModelSwitch 外，其余事件的纯文本 stdout 只写调试日志，既不进上下文也不
# 显示给用户。本脚本长期用 `print(reminder)`，于是每次判断都对、每次输出都丢，
# 静默失效。证据留痕见 installing/archive/custom-setup.md 同日一节。
#
# 用量来源：transcript 是 JSONL，每条 assistant 记录带 message.usage。
#   input_tokens + cache_read_input_tokens + cache_creation_input_tokens
#   + output_tokens 之和就是该次请求的上下文规模，取最后一条即当前值。
#   文档注明 transcript 异步写入，可能落后内存中的对话一两轮，取到的值偏低。
#
# 提醒线取 150k：smart zone 的终点，越过之后模型判断力下降，此时写的接续
# 笔记质量也跟着下降，所以提醒要落在线上而不是线上之后。
#
# 节流：同一会话把上次提醒时的用量记在状态文件里，涨过 REMIND_STEP 才再
#   提醒一次。没有这条，每次工具调用都会刷同一条提醒。

import json
import os
import sys
import time
from pathlib import Path

# 夹具测试用 CLAUDE_ASSET_ROOT 指向临时树，与 protocol-router.py 同一约定。
CLAUDE = Path(os.environ.get("CLAUDE_ASSET_ROOT")
              or Path(os.path.expanduser("~")) / ".claude")
STATE_DIR = CLAUDE / "context-budget"
LOGFILE = CLAUDE / "context-budget-guard.log"

REMIND_AT = 150_000
REMIND_STEP = 25_000
TAIL_BYTES = 1_048_576
KEEP_FILES = 50

USAGE_KEYS = (
    "input_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "output_tokens",
)


def log(message):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGFILE, "a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def payload():
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    start = raw.find("{")
    return json.loads(raw[start:]) if start >= 0 else {}


def newest_usage(blob):
    # 从尾部往前找最后一条带 usage 的 assistant 记录。
    # 窗口从中间截断时首行不完整，解析失败跳过即可。
    for line in reversed(blob.split(b"\n")):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "assistant":
            continue
        usage = (record.get("message") or {}).get("usage")
        if not usage:
            continue
        return sum(usage.get(key, 0) or 0 for key in USAGE_KEYS)
    return None


def context_size(path):
    total = os.path.getsize(path)
    window = min(total, TAIL_BYTES)
    while True:
        with open(path, "rb") as handle:
            handle.seek(total - window)
            blob = handle.read()
        size = newest_usage(blob)
        if size is not None:
            return size
        if window >= total:
            return None
        window = min(total, window * 4)


def remember(session, size):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / session).write_text(f"{size}\n", encoding="utf-8")
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


def last_reminder(session):
    try:
        return int((STATE_DIR / session).read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        return None


def reminder(size):
    return (
        f"上下文已用约 {size // 1000}k。{REMIND_AT // 1000}k 是 smart zone 终点，越过之后模型的判断力下降，"
        "此时写的接续笔记质量也跟着下降。\n"
        "如果本任务需要交接给下一个会话，现在更新接续文件：做到哪一步、为什么这么选、"
        "哪条路已经被否掉、下一步是什么。已有的 commit、diff、文档用路径引用。"
    )


def emit(event, size):
    """hookEventName 必须与 additionalContext 同层：缺了它 Claude Code 会静默忽略。"""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": reminder(size),
        },
    }, ensure_ascii=False))


def main():
    data = payload()
    session = str(data.get("session_id") or "")
    transcript = str(data.get("transcript_path") or "")
    if not session or not transcript:
        log(f"payload 缺字段，键={sorted(data)}")
        return
    size = context_size(transcript)
    if size is None or size < REMIND_AT:
        return
    previous = last_reminder(session)
    if previous is not None and size - previous < REMIND_STEP:
        return
    remember(session, size)
    emit(str(data.get("hook_event_name") or "PostToolUse"), size)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
