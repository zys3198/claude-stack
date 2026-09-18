# 会话生命周期机制的自检，覆盖 product-guard / session-guard / session-status。
# 用法：python selftest.py
#
# 在脚本同级目录建一个临时 git 仓库当沙箱，跑完自删。全部通过时退出码为 0。

import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import contextlib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = Path(__file__).resolve().parent
SANDBOX = SCRIPTS / "selftest-sandbox"
REPO = SANDBOX / "repo"
TREES = REPO / ".claude" / "worktrees"

PASS = []
FAIL = []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail and not ok else ""))


def force_rmtree(path):
    def handler(func, p, exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=handler)


def git(args, cwd):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def build_sandbox():
    if SANDBOX.exists():
        subprocess.run(["git", "-C", str(REPO), "worktree", "prune"], capture_output=True)
        force_rmtree(SANDBOX)
    TREES.mkdir(parents=True)
    git(["init", "-q", "-b", "main"], REPO)
    git(["config", "user.email", "t@t"], REPO)
    git(["config", "user.name", "t"], REPO)
    (REPO / ".gitignore").write_text(".claude/\n", encoding="utf-8")
    (REPO / "README.md").write_text("seed\n", encoding="utf-8")
    git(["add", "-A"], REPO)
    git(["commit", "-qm", "seed"], REPO)

    git(["worktree", "add", "-q", str(TREES / "sample-hold"), "-b", "br-hold"], REPO)
    (TREES / "sample-hold" / "wip.txt").write_text("x\n", encoding="utf-8")
    git(["worktree", "add", "-q", str(TREES / "sample-clean"), "-b", "br-clean"], REPO)

    (TREES / "stale-orphan-dir").mkdir()
    (TREES / "stale-orphan-dir" / "leftover.txt").write_text("y\n", encoding="utf-8")

    (REPO / "loose-note.md").write_text("residue\n", encoding="utf-8")

    handoff = SANDBOX / "handoff.jsonl"
    other = {"ts": 9.9e9, "repo": "C:/Other/RepoSample", "cwd": "C:/Other/RepoSample",
             "dirty": 7, "session_id": "o", "reason": "other", "branch": "main",
             "worktree": False}
    here = {"ts": 9.9e9, "repo": git(["rev-parse", "--show-toplevel"], REPO).strip(),
            "cwd": str(REPO), "dirty": 2, "session_id": "h", "reason": "other",
            "branch": "main", "worktree": False}
    handoff.write_text(json.dumps(other) + "\n" + json.dumps(here) + "\n", encoding="utf-8")
    return handoff


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeOut(io.StringIO):
    def reconfigure(self, **kwargs):
        pass


def run_hook(mod, fn_name, payload):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        getattr(mod, fn_name)(payload)
    return buf.getvalue()


def test_product_guard():
    pg = load("product-guard")
    for gone in ("check_new_file", "ROOT_DOC_EXT", "repo_root"):
        check(f"product-guard 已移除 {gone}", not hasattr(pg, gone))
    check("product-guard 不再 import subprocess", not hasattr(pg, "subprocess"))
    for kept in ("WORKTREE_ADD", "WORKTREE_PATH", "AGENT_HASH", "HASH_WORD", "check_name"):
        check(f"product-guard 保留 {kept}", hasattr(pg, kept))

    def run(cmd):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pg.check_worktree_add(cmd)
        return buf.getvalue()

    cases = [
        ("拒绝仓库外工作树", "git worktree add C:/ZYS/Code/foo-bar", False),
        ("拒绝游离相对路径", "git worktree add ../outsider", False),
        ("放行约定位置", "git worktree add .claude/worktrees/eam-qr-code", True),
        ("放行反斜杠写法", "git worktree add .claude\\worktrees\\eam-qr-code", True),
        ("放行带 -b 的约定位置", "git worktree add -b feat .claude/worktrees/oa-sync", True),
        ("拒绝 agent hash 名", "git worktree add .claude/worktrees/agent-a42cf3b9896e155cb", False),
        ("拒绝 worktree-agent 名", "git worktree add .claude/worktrees/worktree-agent-a42cf3b9", False),
        ("拒绝长 hash 名", "git worktree add .claude/worktrees/task-0a1b2c3d4e5f60718293", False),
        ("放行只读命令", "git status --porcelain", True),
        ("放行 worktree list", "git worktree list --porcelain", True),
        ("放行 worktree remove", "git -C repo worktree remove .claude/worktrees/x", True),
        ("放行普通命令", "ls -la", True),
        ("放行引号内提到该命令", """echo 'git worktree add C:/ZYS/Code/outsider'""", True),
        ("拒绝带引号的仓库外路径", 'git worktree add "C:/ZYS/Code/outsider"', False),
    ]
    for name, cmd, allow in cases:
        out = run(cmd)
        check(name, (out == "") if allow else ("deny" in out), f"cmd={cmd} out={out[:60]}")

    def run_tool(payload):
        buf = FakeOut()
        stdin, sys.stdin = sys.stdin, io.StringIO(json.dumps(payload))
        try:
            with contextlib.redirect_stdout(buf):
                pg.main()
        except SystemExit:
            pass
        finally:
            sys.stdin = stdin
        return buf.getvalue()

    out = run_tool({"tool_name": "EnterWorktree",
                    "tool_input": {"name": "agent-a42cf3b9896e155cb"}})
    check("拒绝 EnterWorktree 的 hash 名", "deny" in out, out[:120])
    out = run_tool({"tool_name": "EnterWorktree", "tool_input": {"name": "eam-qr-code"}})
    check("放行 EnterWorktree 的语义名", out == "", out[:120])
    out = run_tool({"tool_name": "EnterWorktree", "tool_input": {}})
    check("放行无名字的 EnterWorktree", out == "", out[:120])


def test_session_guard():
    sg = load("session-guard")
    for gone in ("AUTOCLEAN", "SCAN_LIMIT", "idle_seconds", "stash_summary",
                 "IDLE_SECONDS", "STASH_WARN_AT", "WORKTREE_MARK", "SESSIONS_DIR"):
        check(f"session-guard 已移除 {gone}", not hasattr(sg, gone))
    captured = {}
    real_run = sg.subprocess.run

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd

        class R:
            returncode = 0
            stdout = "[]"

        return R()

    sg.subprocess.run = fake_run
    sg.active_sessions()
    sg.subprocess.run = real_run
    check("会话信号走受支持接口", captured.get("cmd") == ["claude", "agents", "--json"],
          str(captured.get("cmd")))

    handoff = build_sandbox()
    sg.HANDOFF = handoff
    sg.active_sessions = lambda: []

    root = git(["rev-parse", "--show-toplevel"], REPO).strip()

    out = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("开发前提示出现", "会话卫生" in out, out)
    check("报出无会话占用的脏工作树", "1 个无会话占用的工作树留有未提交改动" in out, out)
    check("报出本仓库遗留改动", "上次会话在 repo 留有 2 处改动" in out, out)
    check("不引用别的仓库遗留", "RepoSample" not in out and "7 处改动" not in out, out)
    check("未承诺自动清理", "自动清理" not in out and "已清理" not in out, out)

    check("干净工作树仍在磁盘", (TREES / "sample-clean").is_dir())
    check("脏工作树仍在磁盘", (TREES / "sample-hold").is_dir())

    sg.active_sessions = lambda: [
        {"pid": 1, "session_id": "other", "cwd": str(REPO), "status": "busy",
         "kind": "background", "started_at": 0},
    ]
    out_busy = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("同目录并发提示出现", "当前目录另有 1 个会话在用" in out_busy, out_busy)
    sg.active_sessions = lambda: []

    sg.active_sessions = lambda: [
        {"pid": 2, "session_id": "holder", "cwd": str(TREES / "sample-hold"),
         "status": "busy", "kind": "background", "started_at": 0},
    ]
    out_held = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("被占用工作树不计入散落", "工作树留有未提交改动" not in out_held, out_held)
    sg.active_sessions = lambda: []

    out_nosess = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("会话枚举为空时不崩溃", "会话卫生" in out_nosess, out_nosess)

    out_other = run_hook(sg, "handle_start", {"cwd": str(SANDBOX), "session_id": "me"})
    check("非 git 目录静默", out_other == "", out_other)

    out_claude = run_hook(sg, "handle_start",
                          {"cwd": str(Path.home() / ".claude"), "session_id": "me"})
    check("~/.claude 静默", out_claude == "", out_claude)

    out_end = run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-hold"),
                                          "session_id": "me", "reason": "other"})
    msg = json.loads(out_end)["systemMessage"]
    check("结束提示报出改动数", "留有 1 处未提交改动" in msg, msg)
    check("结束提示不提自动清理", "自动清理" not in msg, msg)

    out_end2 = run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-clean"),
                                           "session_id": "me", "reason": "other"})
    msg2 = json.loads(out_end2)["systemMessage"]
    check("干净工作树指向 /dev-clean", "/dev-clean" in msg2, msg2)

    recs = [json.loads(x) for x in handoff.read_text(encoding="utf-8").splitlines() if x.strip()]
    check("收尾记录写入", len(recs) >= 4, str(len(recs)))
    check("收尾记录带 repo 字段", all("repo" in r for r in recs), "")

    status = load("session-status")
    scatter = status.root_scatter(root)
    check("状态脚本报出仓库根散落文件",
          scatter is not None and any("loose-note.md" in r for r in scatter), str(scatter))

    orphans = status.orphan_dirs(root)
    check("状态脚本报出孤儿目录", [o["name"] for o in orphans] == ["stale-orphan-dir"], str(orphans))
    check("孤儿目录带同名分支信息", bool(orphans) and orphans[0]["branches"] == [], str(orphans))

    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "session-status.py"), root],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    check("总览脚本退出码为 0", r.returncode == 0, r.stderr[-300:])
    text = r.stdout
    check("总览含仓库根散落段", "仓库根散落" in text, text[-400:])
    check("总览含工作树四分类", "[可清理]" in text and "[有改动]" in text, "")
    check("总览含孤儿目录段", "[孤儿目录]" in text and "stale-orphan-dir" in text, text[-400:])


def cleanup():
    if not REPO.exists():
        return
    subprocess.run(["git", "-C", str(REPO), "worktree", "prune"], capture_output=True)
    force_rmtree(SANDBOX)


try:
    build_sandbox()
    test_product_guard()
    test_session_guard()
finally:
    cleanup()

print()
print(f"通过 {len(PASS)} 项，失败 {len(FAIL)} 项")
if FAIL:
    for f in FAIL:
        print(f"  失败：{f}")
    sys.exit(1)
