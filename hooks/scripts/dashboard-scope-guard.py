# dashboard-builder 的写入范围限制：只允许写 .dashboard/ 之下与它自己的记忆目录。
# 挂在 agents/dashboard-builder.md 的 frontmatter PreToolUse 上，只对该子代理生效；
# 不注册进 settings.json，因此对主会话与其他子代理都没有影响。
#
# 输出形状抄 pretool-guard.py：hookSpecificOutput.permissionDecision + 退出码 0。
# 本脚本自身出错时不出声放行，不阻塞工具调用——它拦的是越界写入，不是完整的安全边界。
import json
import os
import sys

MEM_DIR = os.path.join(os.path.expanduser("~"), ".claude", "agent-memory", "dashboard-builder")
EDIT_TOOLS = ("Write", "Edit", "MultiEdit")


def reason(target):
    return f"dashboard-builder 只写 .dashboard/ 与它自己的记忆，本次目标：{target}"


def allowed(target, cwd):
    """目标路径是否落在允许范围内。"""
    if not target:
        return False
    full = os.path.normcase(os.path.abspath(os.path.join(cwd, target)))
    if full.startswith(os.path.normcase(os.path.abspath(MEM_DIR)) + os.sep):
        return True
    # 路径里任意一层叫 .dashboard，且它下面还有东西（.dashboard 本身不是文件）
    parts = full.split(os.sep)
    return ".dashboard" in parts and parts.index(".dashboard") < len(parts) - 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.read()
    try:
        data = json.loads(raw or "{}")
    except ValueError:
        return
    if not isinstance(data, dict) or data.get("tool_name") not in EDIT_TOOLS:
        return
    target = (data.get("tool_input") or {}).get("file_path")
    if allowed(target, data.get("cwd") or os.getcwd()):
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason(target),
        },
    }, ensure_ascii=False))


def self_test():
    cwd = os.path.join("C:", os.sep, "proj")
    cases = [
        (".dashboard/t.html", True),
        (os.path.join(".dashboard", "sub", "t.html"), True),
        (os.path.join("sub", ".dashboard", "t.html"), True),
        (".dashboard", False),
        ("src/main.py", False),
        ("../outside.html", False),
        (None, False),
        (os.path.join(MEM_DIR, "MEMORY.md"), True),
        ("/etc/passwd", False),
    ]
    bad = [(p, want) for p, want in cases if allowed(p, cwd) is not want]
    for path, want in bad:
        print(f"FAIL {path!r} 期望 {want} 实得 {not want}")
    print(f"self-test {len(cases) - len(bad)}/{len(cases)} 通过")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        sys.exit(self_test())
    main()
