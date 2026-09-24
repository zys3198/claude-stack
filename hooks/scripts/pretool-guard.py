# PreToolUse 合并入口：product-guard 与 resource-guard 在同一个解释器里跑。
#
# 动机：两者原先各是一个 PreToolUse 钩子，每次工具调用要付两次 Python 启动成本。
# 合并后每个工具调用只起一个进程，判定逻辑仍由两个原脚本各自负责，本文件不改判据。
#
# 输出合并规则：任一 guard 判 deny 则整体 deny；否则任一判 ask 则整体 ask；
# 都不出声则本钩子也不出声。原脚本的 print 被捕获后解析，不直接透传给 Claude Code。
# 合并入口自身出错时写日志并放行，不阻塞工具调用。

import importlib.util
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGFILE = os.path.join(os.path.dirname(HERE), "pretool-guard.log")
GUARDS = ("product-guard.py", "resource-guard.py")


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
    except OSError:
        pass


class Capture:
    """替身 stdout：吞掉原脚本的 reconfigure，保留 print 内容供解析。"""

    def __init__(self):
        self._buffer = io.StringIO()

    def write(self, text):
        return self._buffer.write(text)

    def flush(self):
        pass

    def reconfigure(self, **_kwargs):
        pass

    def getvalue(self):
        return self._buffer.getvalue()


def load(filename):
    path = os.path.join(HERE, filename)
    name = "guard_" + filename.replace("-", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(module, raw):
    out = Capture()
    saved_out, saved_in = sys.stdout, sys.stdin
    sys.stdout, sys.stdin = out, io.StringIO(raw)
    try:
        module.main()
    except SystemExit:
        pass
    finally:
        sys.stdout, sys.stdin = saved_out, saved_in
    return out.getvalue()


def verdict(text):
    text = text.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    specific = payload.get("hookSpecificOutput")
    if not isinstance(specific, dict):
        return None
    decision = specific.get("permissionDecision")
    if decision not in ("deny", "ask"):
        return None
    reason = specific.get("permissionDecisionReason") or ""
    return decision, reason


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.read()
    found = []
    for filename in GUARDS:
        try:
            module = load(filename)
        except Exception as exc:
            log(f"load {filename} failed: {exc}")
            continue
        try:
            result = verdict(run(module, raw))
        except Exception as exc:
            log(f"run {filename} failed: {exc}")
            continue
        if result:
            found.append(result)
    if not found:
        sys.exit(0)
    decision = "deny" if any(item[0] == "deny" for item in found) else "ask"
    reason = "\n".join(item[1] for item in found if item[1])
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        },
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
