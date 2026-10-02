"""protocol-router.py 的外部行为测试：喂 hook payload，断言出声还是沉默。

直接 `python test_protocol_router.py`，与 hooks/tests/ 下其余测试同形。
夹具用 tempfile 现搭，CLAUDE_ASSET_ROOT 指过去，不碰真的 ~/.claude——
真正要防的是节流状态写进真实仓库。

几处刻意走 subprocess 而不是直接调函数：

- 本机 stdin 默认 GBK，而表一全按中文词匹配，解码不对就一个字都命中不了、
  还不报错。所以「出声」那几条必须用**纯中文触发词**，用 `CLAUDE.md` 测不出来
  ——ASCII 部分错码后照样匹配得上。
- 节流状态跨进程存活，只有真跑两次进程才测得出。
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "protocol-router.py"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAILED = []


def check(label, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else f"   ← {detail}"))
    if not cond:
        FAILED.append(label)


def feed(root, payload):
    """喂一次 payload，返回 stdout+stderr。"""
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    env = dict(os.environ, CLAUDE_ASSET_ROOT=str(root))
    p = subprocess.run([sys.executable, str(HOOK)], input=raw, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        FAILED.append(f"退出码非 0：{p.returncode}")
    return (p.stdout or "") + (p.stderr or "")


def prompt_event(text, session):
    return {"hook_event_name": "UserPromptSubmit", "session_id": session, "prompt": text}


def tool_event(name, session, **tool_input):
    return {"hook_event_name": "PreToolUse", "session_id": session,
            "tool_name": name, "tool_input": tool_input}


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "assetroot"
        (root / "hooks").mkdir(parents=True)

        # ---------- 沉默 ----------
        out = feed(root, prompt_event("今天天气不错", "quiet"))
        check("沉默·输入里没有领域词", out.strip() == "", out)

        out = feed(root, tool_event("Bash", "quiet", command="ls -la"))
        check("沉默·无关命令", out.strip() == "", out)

        out = feed(root, tool_event("Read", "quiet", file_path=str(root / "CLAUDE.md")))
        check("沉默·不在表里的工具", out.strip() == "", out)

        out = feed(root, {"hook_event_name": "PostToolUse", "session_id": "quiet",
                          "tool_name": "Bash", "tool_input": {"command": "git push"}})
        check("沉默·非本 hook 的事件", out.strip() == "", out)

        out = feed(root, "这不是 JSON")
        check("沉默·payload 非法 JSON 也不报错", out.strip() == "", out)

        # ---------- UserPromptSubmit：中文触发词（GBK 回归线）----------
        out = feed(root, prompt_event("把这条记到记忆里", "prompt-cn"))
        check("出声·纯中文触发词命中", "memory.md" in out, out)
        check("出声·输出带 hookEventName", '"hookEventName": "UserPromptSubmit"' in out, out)
        check("出声·写成事实句不带命令式", "本次请求涉及以下协议" in out, out)

        # ---------- UserPromptSubmit：其余领域 ----------
        out = feed(root, prompt_event("帮我改一下这个 skill 文档", "prompt-skill"))
        check("出声·skill 文档归指令资产", "instruction-assets.md" in out, out)

        out = feed(root, prompt_event("开三个子代理并行做", "prompt-agent"))
        check("出声·派子代理", "delegation.md" in out, out)

        out = feed(root, prompt_event("把这个没用的目录删掉", "prompt-del"))
        check("出声·不可恢复删除", "collaboration.md" in out, out)

        out = feed(root, prompt_event("帮我写个交付报告", "prompt-report"))
        check("出声·交付报告", "evidence.md" in out, out)

        # 同一句话命中两份协议时两份都要给
        out = feed(root, prompt_event("装个插件然后跑测试", "prompt-two"))
        check("出声·一句话命中两份协议都给",
              "ledger.md" in out and "execution-env.md" in out, out)

        # ---------- PreToolUse：编辑类 ----------
        out = feed(root, tool_event("Write", "tool-mem",
                                    file_path=r"C:\ZYS\x\projects\demo\memory\a.md"))
        check("工具·记忆目录写入", "memory.md" in out, out)

        out = feed(root, tool_event("Edit", "tool-claude",
                                    file_path=r"C:\ZYS\x\CLAUDE.md"))
        check("工具·CLAUDE.md 写入", "instruction-assets.md" in out, out)

        out = feed(root, tool_event("Write", "tool-case",
                                    file_path=r"C:\ZYS\x\Claude.MD"))
        check("工具·路径大小写不敏感", "instruction-assets.md" in out, out)

        out = feed(root, tool_event("Write", "tool-proto",
                                    file_path=r"C:\ZYS\x\docs/protocols/gate/gate.md"))
        check("工具·协议文档写入也算指令资产", "instruction-assets.md" in out, out)

        out = feed(root, tool_event("Write", "tool-notes",
                                    file_path=r"C:\ZYS\x\notes\demo\STATE.md"))
        check("工具·任务笔记目录", "task-notes.md" in out, out)

        # ---------- PreToolUse：命令类 ----------
        out = feed(root, tool_event("Bash", "cmd-git", command="git push origin main"))
        check("工具·远程 Git 写操作", "gate.md" in out, out)

        out = feed(root, tool_event("Bash", "cmd-rm", command="rm -rf build"))
        check("工具·不可恢复删除", "collaboration.md" in out, out)

        out = feed(root, tool_event("Bash", "cmd-docker", command="docker build -t x ."))
        check("工具·容器流程", "execution-env.md" in out, out)

        out = feed(root, tool_event("Bash", "cmd-install", command="npm i -g typescript"))
        check("工具·全局装包同时命中环境与台账",
              "execution-env.md" in out and "ledger.md" in out, out)

        out = feed(root, tool_event("PowerShell", "cmd-ps", command="git push"))
        check("工具·PowerShell 与 Bash 同待遇", "gate.md" in out, out)

        # ---------- PreToolUse：子代理（新名与旧名）----------
        out = feed(root, tool_event("Agent", "agent-new", description="x", prompt="y"))
        check("工具·派子代理（v2.1.63 后的 Agent）", "delegation.md" in out, out)

        out = feed(root, tool_event("Task", "agent-old", description="x", prompt="y"))
        check("工具·派子代理（旧名 Task 仍认）", "delegation.md" in out, out)

        # ---------- 节流 ----------
        first = feed(root, prompt_event("把这条记到记忆里", "throttle"))
        second = feed(root, prompt_event("还有一条也记到记忆", "throttle"))
        check("节流·同会话同协议只出一次",
              "memory.md" in first and second.strip() == "", (first, second))

        third = feed(root, prompt_event("顺便把工作树清理一下", "throttle"))
        check("节流·同会话换协议照常出声", "session-lifecycle.md" in third, third)

        other = feed(root, prompt_event("把这条记到记忆里", "throttle-other"))
        check("节流·换会话重新出声", "memory.md" in other, other)

        # ---------- 落盘证据 ----------
        state = json.loads((root / "hooks" / "protocol_router_state.json").read_text(encoding="utf-8"))
        check("状态·按会话分账，最近两个会话都在",
              {"throttle", "throttle-other"} <= set(state), sorted(state))
        # 上面已经喂过 20 个会话，过老的必须被挤出去，否则状态文件无限增长。
        check("状态·满 10 个会话后挤掉最早的",
              len(state) == 10 and "prompt-cn" not in state, sorted(state))
        check("状态·同会话多份协议都记下",
              {"memory", "session-lifecycle"} <= set(state.get("throttle", [])), state.get("throttle"))

        log_text = (root / "hooks" / "protocol-router.log").read_text(encoding="utf-8", errors="replace")
        check("日志·留了命中证据",
              "UserPromptSubmit memory" in log_text and "PreToolUse gate" in log_text, log_text[:300])

    if FAILED:
        print(f"\n{len(FAILED)} 项未过：")
        for f in FAILED:
            print("  -", f)
        return 1
    print("\nPASS protocol router")
    return 0


if __name__ == "__main__":
    sys.exit(main())
