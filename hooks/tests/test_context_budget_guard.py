import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GUARD = Path(os.path.expanduser("~")) / ".claude" / "hooks" / "scripts" / "context-budget-guard.py"
PY = sys.executable
FAILED = []

spec = importlib.util.spec_from_file_location("context_budget_guard", GUARD)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def check(label, got, want):
    ok = got == want
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILED.append(label)
        print(f"      实得 {got!r}")
        print(f"      期望 {want!r}")


def run(payload):
    r = subprocess.run(
        [PY, str(GUARD)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        timeout=30,
    )
    return r.stdout.decode("utf-8", "replace").strip(), r.returncode


def assistant(usage):
    return json.dumps({"type": "assistant", "message": {"usage": usage}}).encode("utf-8")


def user():
    return json.dumps({"type": "user", "message": {"content": "hi"}}).encode("utf-8")


def transcript(usage_sum):
    # 造一条和等于 usage_sum 的 assistant 记录
    return b"\n".join([
        user(),
        assistant({"input_tokens": 1, "cache_read_input_tokens": usage_sum - 1}),
        user(),
    ])


# --- newest_usage：从尾部取最后一条带 usage 的 assistant ---
check(
    "四类 usage 字段求和",
    g.newest_usage(b"\n".join([user(), assistant({
        "input_tokens": 10,
        "cache_read_input_tokens": 20,
        "cache_creation_input_tokens": 30,
        "output_tokens": 40,
    })])),
    100,
)

check(
    "尾部截断行跳过，取上一条",
    g.newest_usage(b"\n".join([
        assistant({"input_tokens": 100, "cache_read_input_tokens": 200}),
        b'{"type":"assistant","message":{"usage":{"input_tokens":7',
    ])),
    300,
)

check(
    "尾部非 assistant 记录时继续往前找",
    g.newest_usage(b"\n".join([assistant({"input_tokens": 1}), user()])),
    1,
)

check(
    "缺 usage 的 assistant 记录被跳过",
    g.newest_usage(b"\n".join([
        assistant({"input_tokens": 5}),
        json.dumps({"type": "assistant", "message": {"content": []}}).encode("utf-8"),
    ])),
    5,
)

check(
    "全是坏行时返回 None",
    g.newest_usage(b"\n".join([b"not json", b"{}"])),
    None,
)

# --- context_size：走真实文件 ---
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "t.jsonl"
    path.write_bytes(transcript(12345))
    check("context_size 读文件得和", g.context_size(path), 12345)

    big = Path(tmp) / "big.jsonl"
    filler = b"\n".join([user() for _ in range(20000)])
    big.write_bytes(filler + b"\n" + assistant({"input_tokens": 999}) + b"\n" + user())
    check("尾部窗口外时向前扩窗直到命中", g.context_size(big), 999)

# --- 端到端：提醒只在跨线且涨过 REMIND_STEP 时出现 ---
session = f"test-{int(time.time())}-{os.getpid()}"
state_file = g.STATE_DIR / session
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "t.jsonl"

    path.write_bytes(transcript(g.REMIND_AT - 1000))
    out, code = run({"session_id": session, "transcript_path": str(path)})
    check("低于提醒线：无输出、退出码 0", (out, code), ("", 0))

    path.write_bytes(transcript(g.REMIND_AT + 2000))
    out, code = run({"session_id": session, "transcript_path": str(path)})
    body = out
    check("跨过提醒线：stdout 纯文本即注入内容", body.startswith("上下文已用约"), True)
    check("提醒文案带当前用量", f"约 {(g.REMIND_AT + 2000) // 1000}k" in body, True)

    out, _ = run({"session_id": session, "transcript_path": str(path)})
    check("同量再跑：节流生效不重复提醒", out, "")

    path.write_bytes(transcript(g.REMIND_AT + 2000 + g.REMIND_STEP - 1))
    out, _ = run({"session_id": session, "transcript_path": str(path)})
    check("涨幅未达 REMIND_STEP：仍不提醒", out, "")

    path.write_bytes(transcript(g.REMIND_AT + 2000 + g.REMIND_STEP + 1))
    out, _ = run({"session_id": session, "transcript_path": str(path)})
    check("涨幅达到 REMIND_STEP：再次提醒", out != "", True)

    out, _ = run({"session_id": "another-" + session, "transcript_path": str(path)})
    check("换会话：独立计数，照常提醒", out != "", True)
    (g.STATE_DIR / ("another-" + session)).unlink(missing_ok=True)

state_file.unlink(missing_ok=True)

# --- 真实 transcript：能算出正整数 ---
projects = Path(os.path.expanduser("~")) / ".claude" / "projects"
candidates = sorted(projects.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime)
if candidates:
    size = g.context_size(candidates[-1])
    check("真实 transcript 算出正整数", isinstance(size, int) and size > 0, True)
    print(f"      最新 transcript {candidates[-1].name} 用量 {size}")
else:
    check("找到真实 transcript", False, True)

print()
if FAILED:
    print(f"FAILED {len(FAILED)}: {FAILED}")
    sys.exit(1)
print("ALL PASS")
