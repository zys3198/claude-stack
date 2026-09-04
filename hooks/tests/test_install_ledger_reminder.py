# Self-check for install-ledger-reminder hook (run: python312 tests/test_install_ledger_reminder.py)
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(__file__)
HOOK = os.path.join(HERE, "..", "install-ledger-reminder.py")
LOG = os.path.join(os.path.expanduser("~"), ".claude", "installing", "auto-log.jsonl")

def run(event):
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps(event).encode(),
        capture_output=True, timeout=20,
    )
    out = p.stdout.decode("utf-8", "replace").strip()
    return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""

def ev(cmd, tool="Bash"):
    return {"hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": {"command": cmd}, "session_id": "selftest"}

before = os.path.getsize(LOG) if os.path.exists(LOG) else 0
hits = [
    "claude plugin install foo@bar",
    "claude mcp add myserver -- npx foo",
    "npm install -g typescript",
    "pipx install something",
    "pip install requests",
    "uv tool install ruff",
    "cargo install ripgrep",
    "winget install Git.Git",
    "npx skills add rohitg00/ai-engineering-from-scratch",
    "pip uninstall -y foo",
]
for c in hits:
    out = run(ev(c))
    assert out.startswith("install-ledger:"), f"miss: {c}"
quiet = ["git status", "ls -la", "python312 script.py", "npm run build", "pip show requests"]
for c in quiet:
    assert run(ev(c)) == "", f"false positive: {c}"

after = os.path.getsize(LOG) if os.path.exists(LOG) else 0
assert after > before, "log not appended"
last = open(LOG, encoding="utf-8").readlines()[-1]
assert "selftest" in last
# cleanup: drop selftest lines from log
lines = [l for l in open(LOG, encoding="utf-8").readlines() if "selftest" not in l]
open(LOG, "w", encoding="utf-8").writelines(lines)
print("ALL PASS:", len(hits), "hits,", len(quiet), "quiet, log append+cleanup ok")
