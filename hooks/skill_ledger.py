#!/usr/bin/env python3
"""记录 Skill 工具调用到 metrics/skill-usage.log（腾讯知识底座文「注入即记账」）。

PostToolUse hook，matcher "Skill"。stdin 收 hook JSON，过滤后追加一行 JSONL：
{"ts","session_id","skill","args"}。任何异常静默 exit(0)，绝不阻塞主流程。
plugin:/namespace: 前缀原样记录，归一交给 scan_skills.py 单点处理。
"""

import sys, json
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".claude" / "metrics" / "skill-usage.log"

def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace")
        i = raw.find("{")
        data = json.loads(raw[i:]) if i >= 0 else {}
    except Exception:
        return 0
    if data.get("hook_event_name") != "PostToolUse":
        return 0
    ti = data.get("tool_input") or {}
    skill = (ti.get("skill") or "").strip()
    if data.get("tool_name") != "Skill" or not skill:
        return 0
    line = json.dumps({
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "session_id": data.get("session_id", ""),
        "skill": skill,
        "args": ti.get("args", ""),
    }, ensure_ascii=False)
    try:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        return 0
    return 0

if __name__ == "__main__":
    sys.exit(main())
