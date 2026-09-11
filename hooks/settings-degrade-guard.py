#!/usr/bin/env python3
"""SessionStart hook：只读检测 settings.json 是否相对 cc-switch 快照降级。

检测 marker：顶层关键字段、permissions.deny，以及关键 hook 绑定和 hook
命令总量。此 hook 不写、备份或替换 settings.json；发现问题时仅通过
SessionStart.additionalContext 告警。
"""
import json
import os
import sqlite3
from pathlib import Path

SETTINGS = os.path.expanduser("~/.claude/settings.json")
DB = os.path.expanduser("~/.cc-switch/cc-switch.db")
KEY = "common_config_claude"
MISSING_HOOK_TOLERANCE = 3  # live 缺失快照 hook 命令数超过此值 → 降级
CRITICAL_HOOK_MARKERS = (
    "git_guard.py", "secret_guard.py", "dep_gate.py", "verify_recorder.py",
)
OBSOLETE_HOOK_MARKERS = ("edited_tracker.py", "verify_gate.py")

def emit(guard_status, message):
    """SessionStart hook JSON 输出；正常时返回空串。"""
    if guard_status == "ok":
        return
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"settings-degrade-guard {guard_status}: {message}",
        },
    }, ensure_ascii=False)

def snapshot_hook_commands(snap):
    cmds = set()
    seen_groups = set()
    hooks = snap.get("hooks", {}) if isinstance(snap, dict) else {}
    if not isinstance(hooks, dict):
        return cmds
    for event, grps in hooks.items():
        if not isinstance(grps, list):
            continue
        for g in grps:
            if not isinstance(g, dict):
                continue
            group_key = (event, json.dumps(g, sort_keys=True, ensure_ascii=False))
            if group_key in seen_groups:
                continue
            seen_groups.add(group_key)
            matcher = g.get("matcher", "")
            hook_list = g.get("hooks", [])
            if not isinstance(hook_list, list):
                continue
            for h in hook_list:
                if isinstance(h, dict) and isinstance(h.get("command"), str):
                    if any(marker in h["command"] for marker in OBSOLETE_HOOK_MARKERS):
                        continue
                    cmds.add((event, matcher, h.get("type", ""), h["command"]))
    return cmds


def missing_critical_hooks(live_cmds, snap_cmds):
    missing = []
    live_bindings = set(live_cmds)
    for marker in CRITICAL_HOOK_MARKERS:
        expected = {binding for binding in snap_cmds if marker in binding[3]}
        if expected and expected - live_bindings:
            missing.append(marker)
    return missing

def is_degraded(live, snap):
    """live 相对快照是否降级。返回 (degraded: bool, reason: str)"""
    for k in ("statusLine", "enabledPlugins", "extraKnownMarketplaces"):
        if k in snap and k not in live:
            return True, f"missing {k!r}"
    live_permissions = live.get("permissions") if isinstance(live.get("permissions"), dict) else {}
    snap_permissions = snap.get("permissions") if isinstance(snap.get("permissions"), dict) else {}
    if snap_permissions.get("deny") and not live_permissions.get("deny"):
        return True, "missing permissions.deny"
    live_cmds = snapshot_hook_commands(live)
    snap_cmds = snapshot_hook_commands(snap)
    critical_missing = missing_critical_hooks(live_cmds, snap_cmds)
    if critical_missing:
        return True, f"missing critical hooks: {', '.join(critical_missing)}"
    missing = len(snap_cmds - live_cmds)
    if missing > MISSING_HOOK_TOLERANCE:
        return True, f"missing {missing} hooks (snapshot has {len(snap_cmds)})"
    return False, ""

def main():
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            live = json.load(f)
        if not isinstance(live, dict):
            print(emit("error", "settings.json 顶层结构不是对象，无法检测"))
            return
    except Exception as e:
        print(emit("error", f"read settings.json failed: {e}"))
        return

    if not os.path.isfile(DB):
        print(emit("warn", "cc-switch DB 不存在，跳过检测"))
        return

    try:
        db_uri = f"file:{Path(DB).as_posix()}?mode=ro"
        con = sqlite3.connect(db_uri, uri=True, timeout=5)
        row = con.execute("SELECT value FROM settings WHERE key=?", (KEY,)).fetchone()
        con.close()
        if not row:
            print(emit("warn", "cc-switch DB 无 common_config_claude 快照，跳过检测"))
            return
        snap = json.loads(row[0])
        if not isinstance(snap, dict):
            print(emit("warn", "cc-switch 快照顶层结构不是对象，跳过检测"))
            return
    except Exception as e:
        print(emit("warn", f"读 cc-switch DB 失败，跳过检测: {e}"))
        return

    degraded, reason = is_degraded(live, snap)
    if not degraded:
        return  # 静默

    print(emit("warn", f"检测到 settings.json 配置降级（{reason}）；只读检测未修改文件，请人工修复并确认后再同步。"))

if __name__ == "__main__":
    main()
