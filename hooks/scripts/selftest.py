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
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = Path(__file__).resolve().parent
SANDBOX = SCRIPTS / "selftest-sandbox"
REPO = SANDBOX / "repo"
OTHER = SANDBOX / "other-repo"
TREES = REPO / ".claude" / "worktrees"
OTHER_TREES = OTHER / ".claude" / "worktrees"

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
        leftover = TREES / "linked-orphan"
        if leftover.is_dir():
            os.rmdir(leftover)
        subprocess.run(["git", "-C", str(REPO), "worktree", "prune"], capture_output=True)
        force_rmtree(SANDBOX)
    TREES.mkdir(parents=True)
    git(["init", "-q", "-b", "main"], REPO)
    git(["config", "user.email", "t@t"], REPO)
    git(["config", "user.name", "t"], REPO)
    (REPO / ".gitignore").write_text(".claude/\nignored/\n", encoding="utf-8")
    (REPO / "README.md").write_text("seed\n", encoding="utf-8")
    git(["add", "-A"], REPO)
    git(["commit", "-qm", "seed"], REPO)

    OTHER_TREES.mkdir(parents=True)
    git(["init", "-q", "-b", "main"], OTHER)
    git(["config", "user.email", "t@t"], OTHER)
    git(["config", "user.name", "t"], OTHER)
    (OTHER / ".gitignore").write_text(".claude/\n", encoding="utf-8")
    git(["add", "-A"], OTHER)
    git(["commit", "-qm", "seed"], OTHER)

    git(["worktree", "add", "-q", str(TREES / "sample-hold"), "-b", "br-hold"], REPO)
    (TREES / "sample-hold" / "wip.txt").write_text("x\n", encoding="utf-8")
    git(["worktree", "add", "-q", str(TREES / "sample-clean"), "-b", "br-clean"], REPO)

    (TREES / "sample-ignored").mkdir()
    git(["worktree", "add", "-q", str(TREES / "sample-ignored"), "-b", "br-ignored"], REPO)
    (TREES / "sample-ignored" / "ignored").mkdir()
    (TREES / "sample-ignored" / "ignored" / "cache.bin").write_text("y\n", encoding="utf-8")

    (TREES / "stale-orphan-dir").mkdir()
    (TREES / "stale-orphan-dir" / "leftover.txt").write_text("y\n", encoding="utf-8")

    (SANDBOX / "link-target").mkdir()
    (SANDBOX / "link-target" / "payload.txt").write_text("z\n", encoding="utf-8")
    subprocess.run(["cmd", "/c", "mklink", "/J", str(TREES / "linked-orphan"),
                    str(SANDBOX / "link-target")], capture_output=True)

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


def read_jsonl(path):
    if not Path(path).is_file():
        return []
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def test_product_guard():
    pg = load("product-guard")
    for gone in ("add_target", "check_new_file", "ROOT_DOC_EXT", "repo_root_old",
                 "unquoted", "WORKTREE_ADD", "WORKTREE_PATH"):
        check(f"product-guard 已移除 {gone}", not hasattr(pg, gone))
    for kept in ("worktree_adds", "is_git_token", "name_reason", "is_control", "leading_cd",
                 "git_invocation", "enter_path_reason", "AGENT_HASH", "HASH_WORD",
                 "OPTS_WITH_VALUE", "NAME_OK"):
        check(f"product-guard 保留 {kept}", hasattr(pg, kept))
    check("product-guard 只按 git 用法登记带值选项",
          pg.OPTS_WITH_VALUE == {"-b", "-B", "--reason"}, str(pg.OPTS_WITH_VALUE))

    def run(cmd, cwd=None):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pg.check_worktree_add(cmd, str(cwd or REPO))
        return buf.getvalue()

    cases = [
        ("放行约定位置", "git worktree add .claude/worktrees/eam-qr-code", True),
        ("放行反斜杠写法", "git worktree add .claude\\worktrees\\eam-qr-code", True),
        ("放行带 -b 的约定位置", "git worktree add -b feat .claude/worktrees/oa-sync", True),
        ("放行绝对路径落在约定位置",
         f"git worktree add {TREES / 'sample-extra'}", True),
        ("拒绝仓库外绝对路径", "git worktree add C:/ZYS/Code/foo-bar", False),
        ("拒绝相对上跳", "git worktree add ../outsider", False),
        ("拒绝路径穿越", "git worktree add .claude/worktrees/../../outside-x", False),
        ("拒绝穿越到绝对路径",
         "git worktree add .claude/worktrees/../../../../ZYS/Code/evil", False),
        ("拒绝字符串藏在 -b 参数里",
         "git worktree add C:/ZYS/Code/outsider -b .claude/worktrees/x", False),
        ("拒绝字符串藏在注释里",
         "git worktree add C:/ZYS/Code/outsider # .claude/worktrees/", False),
        ("拒绝 .claude 下的别处", "git worktree add .claude/scratch", False),
        ("拒绝 worktrees-old", "git worktree add .claude/worktrees-old/x", False),
        ("拒绝目标就是 worktrees 本身", "git worktree add .claude/worktrees", False),
        ("拒绝 agent hash 名", "git worktree add .claude/worktrees/agent-a42cf3b9896e155cb", False),
        ("拒绝 worktree-agent 名", "git worktree add .claude/worktrees/worktree-agent-a42cf3b9", False),
        ("拒绝长 hash 名", "git worktree add .claude/worktrees/task-0a1b2c3d4e5f60718293", False),
        ("放行只读命令", "git status --porcelain", True),
        ("放行 worktree list", "git worktree list --porcelain", True),
        ("放行 worktree remove", "git -C repo worktree remove .claude/worktrees/x", True),
        ("放行普通命令", "ls -la", True),
        ("放行引号内提到该命令", """echo 'git worktree add C:/ZYS/Code/outsider'""", True),
        ("拒绝带引号的仓库外路径", 'git worktree add "C:/ZYS/Code/outsider"', False),
        ("拒绝保留名 tmp", "git worktree add .claude/worktrees/tmp", False),
        ("拒绝保留名 test", "git worktree add .claude/worktrees/test", False),
        ("拒绝八位纯日期名", "git worktree add .claude/worktrees/20260918", False),
        ("拒绝带横线纯日期名", "git worktree add .claude/worktrees/2026-09-18", False),
        ("拒绝 agent- 前缀", "git worktree add .claude/worktrees/agent-foo", False),
        ("拒绝 worktree- 前缀", "git worktree add .claude/worktrees/worktree-foo", False),
        ("拒绝下划线命名", "git worktree add .claude/worktrees/fix_login", False),
        ("拒绝大写命名", "git worktree add .claude/worktrees/EamQr", False),
        ("放行带数字的 kebab 名", "git worktree add .claude/worktrees/fix2-abc", True),
        ("拒绝同命令里后续子句越界创建",
         "git worktree add .claude/worktrees/decoy && git worktree add C:/ZYS/Code/evil", False),
        ("拒绝分号后越界创建",
         "git worktree add .claude/worktrees/decoy ; git worktree add ../evil", False),
        ("拒绝重定向被当成目标路径", "git worktree add .claude/worktrees/ok 2>&1 | head -3", True),
        ("拒绝无路径的 worktree add", "git worktree add -h 2>&1 | head -40", False),
        ("放行 --lock 写法", "git worktree add --lock .claude/worktrees/ok-name", True),
        ("放行 --track 写法", "git worktree add --track .claude/worktrees/ok-name", True),
        ("放行 --lock 带 --reason", "git worktree add --lock --reason why .claude/worktrees/ok-name", True),
        ("放行 -C 指向本仓库",
         f"git -C {REPO} worktree add {TREES / 'via-c'}", True),
        ("拒绝 -C 指向别处再越界",
         f"git -C {OTHER} worktree add ../evil", False),
        ("放行 -C 到别仓库的约定位置",
         f"git -C {OTHER} worktree add {OTHER_TREES / 'cross-ok'}", True),
        ("放行 cd 之后建在约定位置",
         f"cd {REPO} && git worktree add {TREES / 'via-cd'}", True),
        ("拒绝 git.exe 形式的命令名", "git.exe worktree add ../outsider-exe", False),
        ("拒绝带引号的 git 绝对路径",
         '"C:/Program Files/Git/cmd/git.exe" worktree add ../outsider-abs', False),
        ("拒绝正斜杠绝对路径的 git",
         "C:/ZYS/Software/Git/cmd/git.exe worktree add ../outsider-slash", False),
        ("放行名字像 git 但后面不是 worktree add 的写法",
         "git version && ls .claude/worktrees/git", True),
    ]
    for name, cmd, allow in cases:
        out = run(cmd)
        check(name, (out == "") if allow else ("deny" in out), f"cmd={cmd} out={out[:80]}")

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
    out = run_tool({"tool_name": "EnterWorktree", "tool_input": {"name": "tmp"}})
    check("拒绝 EnterWorktree 的保留名", "deny" in out, out[:120])
    out = run_tool({"tool_name": "EnterWorktree", "tool_input": {"name": "eam-qr"}})
    check("放行 EnterWorktree 的两词名", out == "", out[:120])
    out = run_tool({"tool_name": "EnterWorktree",
                    "tool_input": {"path": str(TREES / "sample-clean")}})
    check("放行约定位置内的 EnterWorktree path", out == "", out[:120])
    # 越界目标用主检出根：沙箱本身可能建在工作树里，那样它就在约定位置之内，
    # 拿它当越界样本会被判合规
    outside = Path.home() / ".claude"
    out = run_tool({"tool_name": "EnterWorktree", "tool_input": {"path": str(outside)}})
    check("拒绝约定位置外的 EnterWorktree path", "deny" in out, out[:120])
    out = run_tool({"tool_name": "EnterWorktree",
                    "tool_input": {"name": "eam-qr-code", "path": str(outside)}})
    check("name 合规但 path 越界时仍拒绝", "deny" in out, out[:120])
    out = run_tool({"tool_name": "EnterWorktree",
                    "tool_input": {"name": "eam-qr-code", "path": str(TREES / "sample-clean")}})
    check("name 与 path 都合规时放行", out == "", out[:120])

    out = run_tool({"tool_name": "Bash",
                    "tool_input": {"command": ["git", "worktree", "add", "../evil"]}})
    check("command 不是字符串时放行且不抛异常", out == "", out[:120])
    out = run_tool({"tool_name": "Bash", "tool_input": {"command": 12}})
    check("command 是数字时放行且不抛异常", out == "", out[:120])


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
    sg.HANDOFF_DIR = SANDBOX / "handoff.d"
    sg.LOCK = SANDBOX / "handoff.lock"
    sg.LOGFILE = SANDBOX / "guard.log"
    sg.active_sessions = lambda: []

    root = git(["rev-parse", "--show-toplevel"], REPO).strip()

    out = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("开发前提示出现", "会话卫生" in out, out)
    check("报出无会话占用的脏工作树", "1 个无会话占用的工作树留有未提交改动" in out, out)
    check("报出本仓库遗留改动", "上次会话在 repo 留有 2 处改动" in out, out)
    check("不引用别的仓库遗留", "RepoSample" not in out and "7 处改动" not in out, out)
    check("未承诺自动清理", "自动清理" not in out and "已清理" not in out, out)
    check("裁剪之后没有残留锁文件", not sg.LOCK.exists(), str(sg.LOCK))

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

    sg.active_sessions = lambda: None
    out_degraded = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("会话枚举失败时显式报告降级", "活跃会话枚举失败" in out_degraded, out_degraded)
    check("会话枚举失败时不报无主的散落工作树",
          "无会话占用的工作树" not in out_degraded, out_degraded)
    sg.active_sessions = lambda: []

    sg.active_sessions = lambda: [{"pid": 3, "cwd": str(REPO), "status": "busy"}]
    out_nokey = run_hook(sg, "handle_start", {"cwd": str(REPO), "session_id": "me"})
    check("会话字段缺失时不崩溃", "会话卫生" in out_nokey, out_nokey)
    sg.active_sessions = lambda: []

    # 沙箱建在机制自己的仓库里，git 会向上找到那个仓库，
    # 所以非 git 目录要用仓库之外的空目录来试
    outside_repo = Path(tempfile.gettempdir()) / f"session-guard-{os.urandom(4).hex()}"
    outside_repo.mkdir()
    try:
        out_other = run_hook(sg, "handle_start", {"cwd": str(outside_repo), "session_id": "me"})
        check("非 git 目录静默", out_other == "", out_other)
    finally:
        outside_repo.rmdir()

    out_claude = run_hook(sg, "handle_start",
                          {"cwd": str(Path.home() / ".claude"), "session_id": "me"})
    check("机制自己的仓库按普通仓库汇报", "会话卫生" in out_claude, out_claude)

    out_wt = run_hook(sg, "handle_start",
                      {"cwd": str(TREES / "sample-hold"), "session_id": "me"})
    check("在工作树里开会话仍按主检出汇报",
          "上次会话在 repo 留有 2 处改动" in out_wt, out_wt)
    check("在工作树里开会话主检出改动数正确", "主检出 1 处未提交改动" in out_wt, out_wt)

    out_end = run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-hold"),
                                          "session_id": "me", "reason": "other"})
    msg = json.loads(out_end)["systemMessage"]
    check("结束提示报出改动数", "留有 1 处未提交改动" in msg, msg)
    check("结束提示不提自动清理", "自动清理" not in msg, msg)
    check("结束之后没有残留锁文件", not sg.LOCK.exists(), str(sg.LOCK))

    out_end2 = run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-clean"),
                                           "session_id": "me", "reason": "other"})
    msg2 = json.loads(out_end2)["systemMessage"]
    check("干净工作树指向 /dev-clean", "/dev-clean" in msg2, msg2)

    recs = read_jsonl(handoff)
    check("收尾记录写入", len(recs) >= 4, str(len(recs)))
    check("收尾记录带 repo 字段", all("repo" in r for r in recs), "")

    run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-hold"),
                                "session_id": "wt", "reason": "other"})
    last = read_jsonl(handoff)[-1]
    check("工作树里的收尾记录 repo 指向主检出",
          os.path.normcase(os.path.realpath(last["repo"]))
          == os.path.normcase(os.path.realpath(root)), last["repo"])
    check("工作树里的收尾记录保留自身 cwd",
          os.path.normcase(os.path.realpath(last["cwd"]))
          == os.path.normcase(os.path.realpath(str(TREES / "sample-hold"))), last["cwd"])

    test_prune_handoff(sg, handoff)


def test_prune_handoff(sg, handoff):
    now = time.time()
    fresh = {"ts": now, "repo": str(REPO), "cwd": str(REPO), "dirty": 1,
             "session_id": "fresh", "reason": "other", "branch": "main", "worktree": False}
    aged = {"ts": now - 8 * 86400, "repo": str(REPO), "cwd": str(REPO), "dirty": 4,
            "session_id": "aged", "reason": "other", "branch": "main", "worktree": False}
    aged_clean = {"ts": now - 9 * 86400, "repo": str(REPO), "cwd": str(REPO), "dirty": 0,
                  "session_id": "aged-clean", "reason": "other", "branch": "main",
                  "worktree": False}
    concurrent = {"ts": now, "repo": str(REPO), "cwd": str(REPO), "dirty": 6,
                  "session_id": "concurrent", "reason": "other", "branch": "main",
                  "worktree": False}
    handoff.write_text(
        "\n".join(json.dumps(r) for r in (fresh, aged, aged_clean)) + "\n", encoding="utf-8")

    sg.handoff_records()
    with open(handoff, "a", encoding="utf-8") as f:
        f.write(json.dumps(concurrent) + "\n")

    sg.prune_handoff()
    ids = {r.get("session_id") for r in read_jsonl(handoff)}
    check("裁剪不丢并发追加的记录", "concurrent" in ids, str(sorted(ids)))
    check("裁剪保留未过期记录", "fresh" in ids, str(sorted(ids)))
    check("裁剪丢弃过期记录", "aged" not in ids, str(sorted(ids)))
    check("裁剪丢弃过期且无改动的记录", "aged-clean" not in ids, str(sorted(ids)))
    log_text = sg.LOGFILE.read_text(encoding="utf-8") if sg.LOGFILE.is_file() else ""
    check("过期且有改动的记录被记入日志", "dirty=4" in log_text, log_text[:200])

    before = len(read_jsonl(handoff))
    sg.prune_handoff()
    check("无需裁剪时不重写文件", len(read_jsonl(handoff)) == before, str(before))

    sg.LOCK.write_text("stale", encoding="utf-8")
    old = time.time() - 3600
    os.utime(sg.LOCK, (old, old))
    held_before = len(read_jsonl(handoff))
    out = run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-clean"),
                                      "session_id": "stale-lock", "reason": "other"})
    check("陈旧锁不会挡住收尾记录", len(read_jsonl(handoff)) == held_before + 1, out[:120])
    check("陈旧锁之后锁文件已清掉", not sg.LOCK.exists(), str(sg.LOCK))

    # 锁令牌：被接管之后，原持有者释放时不能删掉接管者的锁
    if sg.LOCK.exists():
        sg.LOCK.unlink()
    token_a = sg.lock_acquire()
    old = time.time() - 3600
    os.utime(sg.LOCK, (old, old))
    token_b = sg.lock_acquire()
    sg.lock_release(token_a)
    check("接管之后原持有者不会删掉新锁", sg.LOCK.exists(), str(sg.LOCK))
    check("接管者拿到的是新令牌",
          bool(token_a) and bool(token_b) and token_a != token_b, f"{token_a} / {token_b}")
    sg.lock_release(token_b)
    check("接管者释放后锁文件清掉", not sg.LOCK.exists(), str(sg.LOCK))

    # 锁文件修改时间在将来时按陈旧处理，否则锁会永久卡住裁剪与追加
    sg.LOCK.write_text("future", encoding="utf-8")
    far = time.time() + 3600
    os.utime(sg.LOCK, (far, far))
    token_f = sg.lock_acquire()
    check("锁时间在将来时按陈旧接管", bool(token_f), str(token_f))
    sg.lock_release(token_f)

    # 降级追加改走溢出文件，不写共享主文件
    sg.LOCK.write_text("held-by-other", encoding="utf-8")
    far = time.time() + 3600
    os.utime(sg.LOCK, (far, far))
    sg.LOCK_STALE_SECONDS = 1e9
    before = len(read_jsonl(handoff))
    run_hook(sg, "handle_end", {"cwd": str(TREES / "sample-clean"),
                                "session_id": "overflow-one", "reason": "other"})
    sg.LOCK_STALE_SECONDS = 30.0
    overflow = sorted(sg.HANDOFF_DIR.glob("*.jsonl"))
    check("降级追加写进溢出文件", len(overflow) == 1, str(overflow))
    check("降级时不写主文件", len(read_jsonl(handoff)) == before, str(before))
    ids = {r.get("session_id") for r in sg.handoff_records()}
    check("读取时带上溢出文件里的记录", "overflow-one" in ids, str(sorted(ids)))

    sg.LOCK.unlink()
    sg.prune_handoff()
    ids = {r.get("session_id") for r in read_jsonl(handoff)}
    check("裁剪把溢出记录并回主文件", "overflow-one" in ids, str(sorted(ids)))
    check("裁剪之后溢出文件清空", not list(sg.HANDOFF_DIR.glob("*.jsonl")),
          str(list(sg.HANDOFF_DIR.glob("*.jsonl"))))


def test_session_status():
    st = load("session-status")
    # 不写这一行会去读真实的 ~/.claude/session-handoff.jsonl，
    # 断言就跟着机器上的实际内容走
    st.HANDOFF = SANDBOX / "handoff-status.jsonl"
    st.HANDOFF_DIR = SANDBOX / "handoff-status.d"
    root = git(["rev-parse", "--show-toplevel"], REPO).strip()

    prefix = st.worktree_prefix(root)
    inside = os.path.normcase(os.path.realpath(os.path.join(root, ".claude", "worktrees", "x")))
    older = os.path.normcase(os.path.realpath(os.path.join(root, ".claude", "worktrees-old", "x")))
    check("工作树前缀按路径边界判定",
          inside.startswith(prefix) and not older.startswith(prefix), f"{inside} / {older}")

    scatter = st.root_scatter(root)
    check("状态脚本报出仓库根散落文件",
          scatter is not None and any("loose-note.md" in r for r in scatter), str(scatter))

    orphans = st.orphan_dirs(root)
    names = [o["name"] for o in orphans]
    check("状态脚本报出孤儿目录", names == ["stale-orphan-dir"], str(orphans))
    check("孤儿目录带同名分支信息", bool(orphans) and orphans[0]["branches"] == [], str(orphans))
    check("孤儿目录跳过符号链接",
          (TREES / "linked-orphan").is_dir() and "linked-orphan" not in names, str(names))

    ignored_tree = TREES / "sample-ignored"
    check("被忽略内容不计入改动数", st.change_count(ignored_tree) == 0,
          str(st.change_count(ignored_tree)))
    check("被忽略内容能被单独数出来", st.ignored_count(ignored_tree) == 1,
          str(st.ignored_count(ignored_tree)))

    real_run = st.subprocess.run

    def failing(cmd, **kwargs):
        if isinstance(cmd, list) and cmd and cmd[0] == "claude":
            raise FileNotFoundError("claude")
        return real_run(cmd, **kwargs)

    st.subprocess.run = failing
    result = st.active_sessions()
    st.subprocess.run = real_run
    check("枚举失败时返回 None 而不是空列表", result is None, str(result))

    text = run_status(st, root, sessions=[{"pid": 9, "cwd": str(ignored_tree),
                                           "kind": "background", "status": "idle",
                                           "startedAt": int(time.time() * 1000)}])
    check("在用工作树归入在用", "[在用] 1" in text, text[-600:])
    tail = text.split("[可清理]")[-1] if "[可清理]" in text else ""
    check("被占用时不列入可清理", "sample-ignored" not in tail, tail[:300])

    text2 = run_status(st, root, sessions=[])
    check("无会话时可清理含被忽略内容标注",
          "另有 1 项被忽略内容" in text2, text2[-800:])
    check("可清理带出删除范围提示",
          "删除会一并删掉那些文件" in text2, text2[-400:])

    text3 = run_status(st, root, sessions=None)
    check("枚举失败时打印降级告警", "活跃会话 枚举失败" in text3, text3[:400])
    check("降级时提示不要据此删除", "不要据此删除" in text3, text3[:400])


def test_handoff_ts_guard():
    # 收尾记录可能被手工编辑，时间戳缺字段或类型不对时，
    # 计数照常、明细跳过，不能让整个状态汇总崩掉
    st = load("session-status")
    root = git(["rev-parse", "--show-toplevel"], REPO).strip()
    handoff = SANDBOX / "handoff-ts.jsonl"
    st.HANDOFF = handoff
    st.HANDOFF_DIR = SANDBOX / "handoff-ts.d"
    handoff.write_text(
        json.dumps({"ts": time.time(), "repo": root, "cwd": str(REPO), "dirty": 3}) + "\n"
        + json.dumps({"repo": root, "cwd": str(REPO), "dirty": 5}) + "\n"
        + json.dumps({"ts": "2026-01-01", "repo": root, "cwd": str(REPO), "dirty": 2}) + "\n",
        encoding="utf-8")

    text = run_status(st, root, sessions=[])
    check("缺时间戳的记录不让状态汇总崩溃", "上次会话留下的未提交改动 3 条" in text, text[-500:])
    # 有效时间戳那条的改动数是 3，缺字段与非法字段两条分别是 5 和 2；
    # 后两个数字出现在明细里就说明跳过逻辑没生效
    check("缺时间戳与非数值时间戳的记录都不打印明细",
          "3 处" in text and "2 处" not in text and "5 处" not in text, text[-400:])


def test_guard_global_options():
    # git 的全局选项里吃下一个词的项，取值不能被当成子命令位置
    pg = load("product-guard")
    root = git(["rev-parse", "--show-toplevel"], REPO).strip()
    outside = str(Path(SANDBOX) / "outside-wt")

    def denied(command):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pg.check_worktree_add(command, root)
        return "permissionDecision" in buf.getvalue()

    for command, label in (
        (f"git --git-dir .git worktree add {outside}", "--git-dir 空格形式"),
        (f"git -c core.x=1 worktree add {outside}", "-c 带值"),
        (f"git --work-tree=. worktree add {outside}", "--work-tree 等号形式"),
        (f"git --namespace=x worktree add {outside}", "--namespace 等号形式"),
    ):
        check(f"全局选项后仍判出越界：{label}", denied(command), command)

    for command, label in (
        (f"git --git-dir .git worktree add .claude/worktrees/ok", "--git-dir 加合规目标"),
        (f"git -c core.x=1 worktree add .claude/worktrees/ok", "-c 加合规目标"),
        ("git --git-dir=.git status", "加选项的只读命令"),
    ):
        check(f"全局选项不误拒：{label}", not denied(command), command)

    # heredoc 的正文是数据。提交消息里出现命令字样时不能当成执行
    message = ("说明：下面这行是文档正文，git worktree add " + outside + " 只是举例\n"
               + f"cat <<'MSG' 用的结束标记是 MSG\n")
    command = "git commit -q -F - <<'MSG'\n" + message + "MSG"
    check("提交消息正文里的命令字样不被当成执行", not denied(command), command[:200])
    check("heredoc 之外的真实越界命令仍然拦住",
          denied(f"cat <<'EOF'\n说明文字\nEOF\ngit worktree add {outside}"), "")


def run_status(st, root, sessions):
    st.active_sessions = (lambda: sessions) if sessions is not None else (lambda: None)
    st.sys.argv = ["session-status.py", root]
    buf = FakeOut()
    saved = sys.stdout
    sys.stdout = buf
    try:
        st.main()
    finally:
        sys.stdout = saved
    return buf.getvalue()


def cleanup():
    if not REPO.exists():
        return
    junction = TREES / "linked-orphan"
    if junction.is_dir():
        os.rmdir(junction)
    subprocess.run(["git", "-C", str(REPO), "worktree", "prune"], capture_output=True)
    subprocess.run(["git", "-C", str(OTHER), "worktree", "prune"], capture_output=True)
    force_rmtree(SANDBOX)


try:
    build_sandbox()
    test_product_guard()
    test_session_guard()
    test_session_status()
    test_handoff_ts_guard()
    test_guard_global_options()
finally:
    cleanup()

print()
print(f"通过 {len(PASS)} 项，失败 {len(FAIL)} 项")
if FAIL:
    for f in FAIL:
        print(f"  失败：{f}")
    sys.exit(1)
