import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
REMINDER = CLAUDE / "hooks" / "scripts" / "task-notes-reminder.py"
SETTINGS = CLAUDE / "settings.json"
PY = sys.executable
FAILED = []

spec = importlib.util.spec_from_file_location("task_notes_reminder", REMINDER)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def check(label, got, want):
    ok = got == want
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILED.append(label)
        print(f"      实得 {got!r}")
        print(f"      期望 {want!r}")


def run(mode, payload):
    r = subprocess.run(
        [PY, str(REMINDER), mode],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=30,
    )
    return r.stdout.decode("utf-8", "replace").strip(), r.returncode


session = f"test-{int(time.time())}-{os.getpid()}"
state = g.STATE_DIR / session
state.unlink(missing_ok=True)

# --- pre 模式：只记数，不输出 ---
out, code = run("pre", {"session_id": session})
check("pre 无输出、退出码 0", (out, code), ("", 0))
check("pre 计数写进状态文件", g.read_count(session), 1)

out, code = run("pre", {"session_id": session})
check("pre 再跑继续累加", (out, code, g.read_count(session)), ("", 0, 2))

# --- start 模式：阈值前不提醒 ---
out, code = run("start", {"session_id": session})
check("压缩 2 次：不提醒", (out, code), ("", 0))

out, _ = run("pre", {"session_id": session})
check("第 3 次自动压缩入账", g.read_count(session), 3)

out, code = run("start", {"session_id": session})
body = json.loads(out) if out else {}
check("压缩 3 次：有输出、退出码 0", (bool(out), code), (True, 0))
check("channel 是 SessionStart", body.get("hookSpecificOutput", {}).get("hookEventName"), "SessionStart")
check("模型侧文案", body.get("hookSpecificOutput", {}).get("additionalContext"), g.REMINDER)
check("用户侧文案", body.get("systemMessage"), g.NOTICE)
check("提醒文案要求调用技能", ("调用" in g.REMINDER, "task-notes" in g.REMINDER), (True, True))

# --- 第 4 次之后继续提醒 ---
run("pre", {"session_id": session})
out, _ = run("start", {"session_id": session})
check("压缩 4 次：仍提醒", out != "", True)

# --- 会话隔离 ---
other = "another-" + session
out, _ = run("start", {"session_id": other})
check("未记数的会话：不提醒", out, "")
(g.STATE_DIR / other).unlink(missing_ok=True)

# --- 边界与异常输入 ---
out, code = run("start", {"session_id": ""})
check("缺 session_id：无输出、退出码 0", (out, code), ("", 0))

out, code = run("bogus", {"session_id": session})
check("未知模式：无输出、退出码 0", (out, code), ("", 0))

out, code = run("pre", {})
check("空 payload：无输出、退出码 0", (out, code), ("", 0))

with tempfile.TemporaryDirectory() as tmp:
    r = subprocess.run(
        [PY, str(REMINDER), "pre"],
        input=b"not json at all",
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=30,
    )
    check("非 JSON 输入：无输出、退出码 0", (r.stdout.decode().strip(), r.returncode), ("", 0))

# --- 状态文件剪枝 ---
STATE_DIR_MADE = g.STATE_DIR.exists()
check("状态目录已建", STATE_DIR_MADE, True)
kept = sorted(g.STATE_DIR.iterdir(), key=lambda p: p.stat().st_mtime)
check("状态文件数不超上限", len(kept) <= g.KEEP_FILES, True)

# --- settings.json 真接线 ---
settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
groups = settings["hooks"].get("PreCompact", [])
pre_cmds = [h["command"] for grp in groups for h in grp["hooks"]]
check("PreCompact 接了 pre 模式", any("task-notes-reminder.py\" pre" in c for c in pre_cmds), True)
check("PreCompact matcher 是 auto", [grp.get("matcher") for grp in groups], ["auto"])

groups = settings["hooks"].get("SessionStart", [])
pairs = [(grp.get("matcher"), h["command"]) for grp in groups for h in grp["hooks"]]
check(
    "SessionStart 接了 start 模式且 matcher 是 compact",
    any(m == "compact" and "task-notes-reminder.py\" start" in c for m, c in pairs),
    True,
)

state.unlink(missing_ok=True)

print()
if FAILED:
    print(f"FAILED {len(FAILED)}: {FAILED}")
    sys.exit(1)
print("ALL PASS")
