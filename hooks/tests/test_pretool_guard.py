# pretool-guard 合并入口的回归测试。
# 覆盖三条：两个原 guard 的判定在合并后仍然生效、合并结果按 deny 优先、
# 无判定时不出声。用法：python test_pretool_guard.py

import json
import os
import subprocess
import sys

PYTHON = sys.executable or "python"
GUARD = os.path.join(os.path.expanduser("~"), ".claude", "hooks", "scripts", "pretool-guard.py")
# cwd 取一个普通项目目录。取 ~/.claude 会命中 resource-guard 的
# 「执行 ~/.claude 下脚本不算宿主机工具链」例外，把工具链用例误判为放行。
CWD = os.environ.get("PRETOOL_TEST_CWD") or os.path.join(os.path.expanduser("~"), "Code", "lab-area")

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f"  {detail}" if not ok else ""))


def run(tool, tool_input):
    payload = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": tool_input,
        "cwd": CWD,
        "session_id": "test-pretool-guard",
    }, ensure_ascii=False)
    proc = subprocess.run(
        [PYTHON, GUARD], input=payload, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    return proc.stdout.strip()


def decision(stdout):
    if not stdout:
        return None, ""
    data = json.loads(stdout)
    specific = data.get("hookSpecificOutput", {})
    return specific.get("permissionDecision"), specific.get("permissionDecisionReason", "")


def expect_silent(name, tool, tool_input):
    out = run(tool, tool_input)
    check(name, out == "", f"预期静默，实际: {out[:200]}")


def expect(name, tool, tool_input, want):
    out = run(tool, tool_input)
    got, reason = decision(out)
    check(name, got == want, f"预期 {want}，实际 {got}（{reason[:160]}）")


def main():
    expect_silent("普通只读命令放行", "Bash", {"command": "git status --short"})
    expect_silent("docker ps 放行", "Bash", {"command": "docker ps"})
    expect("宿主机跑 node 被拦", "Bash", {"command": "node -e \"console.log(1)\""}, "deny")
    expect("宿主机跑 pnpm 被拦", "Bash", {"command": "pnpm build"}, "deny")
    expect("工作树建到别处被拦", "Bash", {"command": "git worktree add /tmp/x"}, "deny")
    expect("EnterWorktree 名字含 hash 被拦", "EnterWorktree", {"name": "agent-123456"}, "deny")
    expect_silent("EnterWorktree 合规名字放行", "EnterWorktree", {"name": "cc-system-slimming"})
    expect_silent("写入普通文件放行", "Write", {"file_path": "/tmp/a.txt", "content": "x"})

    print(f"\n通过 {sum(results)} 项，失败 {len(results) - sum(results)} 项")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
