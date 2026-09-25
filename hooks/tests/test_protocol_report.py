"""protocol-report.py 的外部行为测试：喂 hook payload，断言出声还是沉默。

直接 `python test_protocol_report.py`，与 hooks/tests/ 下其余测试同形。
只测「什么输入下出声、什么输入下沉默」，判据本身在 test_protocol_check.py 里测。
夹具用 tempfile 现搭，CLAUDE_ASSET_ROOT 指过去，不碰真的 ~/.claude。
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "protocol-report.py"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAILED = []
SPOKE = []

TABLE = """## 资产 → 形态 → L0

| 资产 | 加载形态 | L0 由谁提供 |
|---|---|---|
| `~/.claude/rules/principles.md`（本文件） | 常驻 | 文件自身 |
| `~/.claude/CLAUDE.md` | 常驻 | 路由表 |
| `rules/*.md` | 条件（带 `paths`）／常驻（不带） | 文件头 |
| skill | 按需 | `description` 字段 |
| `docs/protocols/*.md` | 不进上下文 | `protocols-index.md` 对应行 |
| memory | 召回 | `MEMORY.md` 索引行 |
| `notes/` | 不进上下文 | 目录名 |
| hook | 不进上下文（平台执行） | `settings.json` matcher |
"""

# 映射表的每一行都要在磁盘上找得到对应物，否则夹具自己就带着映射表违规。
TREE = {
    "CLAUDE.md": "# 常驻指令\n",
    "rules/principles.md": f"# 资产原则\n\n{TABLE}",
    "skills/demo/SKILL.md": "---\nname: demo\ndescription: 演示\n---\n\n正文。\n",
    "docs/protocols/index.md": "# 协议索引\n",
    "hooks/scripts/noop.py": "# 占位\n",
    "projects/demo/memory/note-one.md": (
        "---\nname: note-one\ndescription: 一条记忆\nmetadata:\n  type: feedback\n---\n\n正文。\n"
    ),
    "projects/demo/memory/MEMORY.md": "# 索引\n\n- [一条](note-one.md)\n",
}


def check(label, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else f"   ← {detail}"))
    if not cond:
        FAILED.append(label)


def build(root, spec):
    for rel, text in spec.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)


def feed(root, payload):
    """喂一次 payload，返回 (退出码, stdout+stderr)。"""
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    env = dict(os.environ, CLAUDE_ASSET_ROOT=str(root))
    p = subprocess.run([sys.executable, str(HOOK)], input=raw, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        FAILED.append(f"退出码非 0：{p.returncode}")
    if p.stdout.strip():
        SPOKE.append(p.stdout.strip())
    return p.returncode, out


def write_event(path, session="s1", tool="Write"):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return {"hook_event_name": "PostToolUse", "session_id": session, "tool_name": tool,
            "tool_input": {key: str(path)}}


def stop_event(session="s1"):
    return {"hook_event_name": "Stop", "session_id": session, "stop_hook_active": False}


def write_payload(path, content, session="s1"):
    """写入前的 payload：Write 带整份新内容。"""
    return {"hook_event_name": "PreToolUse", "session_id": session, "tool_name": "Write",
            "tool_input": {"file_path": str(path), "content": content}}


def edit_payload(path, old, new, session="s1"):
    """写入前的 payload：Edit 带 old/new，判据按复原后的样子算。"""
    return {"hook_event_name": "PreToolUse", "session_id": session, "tool_name": "Edit",
            "tool_input": {"file_path": str(path), "old_string": old, "new_string": new}}


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "assetroot"
        build(root, TREE)

        # ---------- 沉默 ----------
        _, out = feed(root, write_event(Path(temp) / "outside.md"))
        check("沉默·夹具外的路径不查", out.strip() == "", out)

        _, out = feed(root, {"hook_event_name": "PostToolUse", "session_id": "s1",
                             "tool_name": "Bash", "tool_input": {"command": "ls"}})
        check("沉默·没有 file_path", out.strip() == "", out)

        _, out = feed(root, {"hook_event_name": "PreToolUse", "session_id": "s1",
                             "tool_name": "Write", "tool_input": {"file_path": str(root / "CLAUDE.md")}})
        check("沉默·非本 hook 的事件", out.strip() == "", out)

        _, out = feed(root, "这不是 JSON")
        check("沉默·payload 非法 JSON 也不报错", out.strip() == "", out)

        clean = root / "docs" / "protocols" / "clean.md"
        clean.write_text("# 干净文档\n\n没有违规。\n", encoding="utf-8")
        _, out = feed(root, write_event(clean))
        check("沉默·查了但没命中", out.strip() == "", out)

        # ---------- 出声 ----------
        big = root / "docs" / "protocols" / "big.md"
        big.write_text("# 大文档\n\n" + "字" * 25_000, encoding="utf-8")
        _, out = feed(root, write_event(big))
        check("出声·刚写的文件超限", "additionalContext" in out and "超过 20 KB" in out, out)
        check("出声·点名是哪一个文件", "docs/protocols/big.md" in out, out)

        note = root / "projects" / "demo" / "memory" / "orphan.md"
        note.write_text("---\nname: orphan\ndescription: 没进索引\nmetadata:\n  type: feedback\n---\n\nx\n",
                        encoding="utf-8")
        _, out = feed(root, write_event(note, tool="NotebookEdit"))
        check("出声·NotebookEdit 的 notebook_path 也认", "没进 MEMORY.md 索引" in out, out)

        # ---------- Stop ----------
        _, out = feed(root, stop_event("别的会话"))
        check("沉默·Stop 而本会话没写过资产", out.strip() == "", out)

        _, out = feed(root, stop_event("s1"))
        check("出声·Stop 跑全量报告", "systemMessage" in out and "全量报告" in out, out)

        _, out = feed(root, stop_event("s1"))
        check("沉默·Stop 命中与上次相同不重复播报", out.strip() == "", out)

        big.write_text("# 大文档\n\n" + "字" * 26_000, encoding="utf-8")
        _, out = feed(root, write_event(big, session="s1"))
        _, out = feed(root, stop_event("s1"))
        check("出声·命中变了再报一次", "systemMessage" in out, out)

        # ---------- PreToolUse：只在阻断区拒 ----------
        huge = "# 常驻\n\n" + "字" * 25_000
        _, out = feed(root, write_payload(root / "CLAUDE.md", huge))
        check("阻断·常驻区写入超限被拒", '"permissionDecision": "deny"' in out and "超过 20 KB" in out, out)

        _, out = feed(root, write_payload(Path(root, "rules", "new.md"), huge))
        check("阻断·原则区新文件也拦（还没落盘）", '"permissionDecision": "deny"' in out, out)

        _, out = feed(root, edit_payload(Path(root, "rules", "principles.md"),
                                         "# 资产原则\n", "# 资产原则\n\n" + huge))
        check("阻断·Edit 按复原后的样子判", '"permissionDecision": "deny"' in out, out)

        _, out = feed(root, write_payload(root / "CLAUDE.md", "# 常驻指令\n\n合规。\n"))
        check("放行·合规写入不出声", out.strip() == "", out)

        _, out = feed(root, write_payload(Path(root, "docs", "protocols", "new.md"), huge))
        check("放行·其他区超限只报告不拦", '"permissionDecision"' not in out, out)

        _, out = feed(root, write_payload(Path(temp) / "outside.md", huge))
        check("放行·根之外的路径不判", out.strip() == "", out)

        _, out = feed(root, {"hook_event_name": "PreToolUse", "session_id": "s1",
                             "tool_name": "NotebookEdit",
                             "tool_input": {"notebook_path": str(Path(root, "rules", "nb.ipynb"))}})
        check("放行·NotebookEdit 判不出内容就不拦", out.strip() == "", out)

        # 盘上已经违规、这次写入是把它改好 → 放行，否则违规文件永远改不动
        broken = Path(root, "rules", "broken.md")
        broken.write_text("# 规则\n\n" + "字" * 25_000, encoding="utf-8")
        _, out = feed(root, edit_payload(broken, "字" * 25_000, "短。"))
        check("放行·修掉违规的那次写入", out.strip() == "", out)

        # ---------- 阻断面只有 BLOCK_SCOPE 那一处 ----------
        joined = "\n".join(SPOKE)
        check("阻断面·只有阻断区的三次被拒",
              joined.count('"permissionDecision": "deny"') == 3, joined[:300])
        check("阻断面·拒的输出带原因字段", '"permissionDecisionReason"' in joined, joined[:300])
        check("阻断面·每次喂 payload 退出码都是 0", not [f for f in FAILED if "退出码非 0" in f], FAILED)
        log_text = Path(root, "hooks", "protocol-report.log").read_text(encoding="utf-8", errors="replace")
        check("阻断面·日志留了 deny 证据", log_text.count("deny:") == 3, log_text[:300])

    if FAILED:
        print(f"\n{len(FAILED)} 项未过：")
        for f in FAILED:
            print("  -", f)
        return 1
    print("\nPASS protocol report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
