import sys, json, os, subprocess

# PostToolUse hook: settings.json 被编辑/写入后，自动同步公共配置进 cc-switch DB。
# 非 settings.json 命中时毫秒级退出；命中时调 sync_claude_common.py（自带 NO-OP 幂等）。

PYTHON = "C:/Users/zys31/AppData/Local/Programs/Python/Python312/python.exe"
SYNC = "C:/Users/zys31/.claude/skills/cc-switch-setting-sync/scripts/sync_claude_common.py"
TARGET = os.path.normcase(os.path.abspath(os.path.expanduser("~/.claude/settings.json")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    i = raw.find("{")
    data = json.loads(raw[i:]) if i >= 0 else {}
except Exception:
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
fp = ti.get("file_path") or ""
if not fp:
    sys.exit(0)
try:
    if os.path.normcase(os.path.abspath(fp)) != TARGET:
        sys.exit(0)
except Exception:
    sys.exit(0)

try:
    r = subprocess.run(
        [PYTHON, SYNC],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    out = (r.stdout or "").strip().splitlines()
    tail = out[-1] if out else ""
    note = "settings.json 已自动同步 cc-switch DB（NO-OP）" if "NO-OP" in (r.stdout or "") else f"settings.json 已自动同步 cc-switch DB: {tail}"
    if r.returncode != 0:
        note = f"settings-sync 失败(rc={r.returncode})，可手动跑 sync_claude_common.py 或 --restore 修复"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": note,
        }
    }, ensure_ascii=False))
except Exception:
    pass
sys.exit(0)
