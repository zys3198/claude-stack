#!/usr/bin/env python3
"""SessionStart hook：检测 settings.json 是否被 cc-switch 切换 provider 降级，自动恢复。

检测 marker：
  1. statusLine 缺失
  2. enabledPlugins 缺失
  3. extraKnownMarketplaces 缺失
  4. permissions.deny 缺失（安全边界变宽）
  5. hooks 缺失快照中 >3 个 hook command（覆盖「只丢 hooks」的部分降级）

恢复源：cc-switch DB 的 settings.common_config_claude（由
cc-switch-setting-sync skill 维护）。保留 live 的 provider 字段
（env 的 ANTHROPIC_* 与顶层 model）。hooks/permissions 为并集合并，
live 独有内容（新增 hook、新增 allow 规则）不会被抹掉。

输出约定（Claude Code SessionStart hook）：
  - 正常/无操作：静默（无输出）
  - 恢复成功：JSON 提示（hookSpecificOutput 会注入会话上下文）
  - 快照不可用或快照本身缺 marker：JSON 警告，不写文件
"""
import json
import os
import shutil
import sqlite3
import time

SETTINGS = os.path.expanduser("~/.claude/settings.json")
DB = os.path.expanduser("~/.cc-switch/cc-switch.db")
KEY = "common_config_claude"
MISSING_HOOK_TOLERANCE = 3  # live 缺失快照 hook 命令数超过此值 → 降级
CRITICAL_HOOK_MARKERS = (
    "git_guard.py", "secret_guard.py", "dep_gate.py", "gateguard-destructive.js",
    "edited_tracker.py", "verify_gate.py", "verify_recorder.py",
)

def emit(guard_status, message):
    """SessionStart hook JSON 输出；正常时返回空串。"""
    if guard_status == "ok":
        return
    return json.dumps({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "settingsGuard": f"{guard_status}: {message}",
        },
    }, ensure_ascii=False)

def snapshot_hook_commands(snap):
    cmds = set()
    hooks = snap.get("hooks", {}) if isinstance(snap, dict) else {}
    if not isinstance(hooks, dict):
        return cmds
    for event, grps in hooks.items():
        if not isinstance(grps, list):
            continue
        for g in grps:
            if not isinstance(g, dict):
                continue
            matcher = g.get("matcher", "")
            for h in g.get("hooks", []):
                if isinstance(h, dict) and isinstance(h.get("command"), str):
                    cmds.add((event, matcher, h.get("type", ""), h["command"]))
    return cmds


def missing_critical_hooks(live_cmds, snap_cmds):
    missing = []
    snapshot_commands = [binding[3] for binding in snap_cmds]
    live_commands = [binding[3] for binding in live_cmds]
    for marker in CRITICAL_HOOK_MARKERS:
        in_snapshot = any(marker in command for command in snapshot_commands)
        in_live = any(marker in command for command in live_commands)
        if in_snapshot and not in_live:
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

def merge_hooks(live_hooks, snap_hooks):
    """事件组合并：快照组在前（权威），live 独有组在后（新增 hook 保留）。"""
    live_hooks = live_hooks if isinstance(live_hooks, dict) else {}
    snap_hooks = snap_hooks if isinstance(snap_hooks, dict) else {}
    merged = {}
    for ev in sorted(set(snap_hooks) | set(live_hooks)):
        groups, seen = [], set()
        for g in (snap_hooks.get(ev, []) + live_hooks.get(ev, [])):
            key = json.dumps(g, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                groups.append(g)
        merged[ev] = groups
    return merged

def merge_permissions(live_perm, snap_perm):
    """allow/deny/ask 并集合并，快照在前。"""
    live_perm = live_perm if isinstance(live_perm, dict) else {}
    snap_perm = snap_perm if isinstance(snap_perm, dict) else {}
    if not snap_perm:
        return live_perm
    merged = dict(live_perm or {})
    for k in ("allow", "deny", "ask"):
        s = snap_perm.get(k, [])
        l = merged.get(k, [])
        if s or l:
            out = list(s)
            for x in l:
                if x not in out:
                    out.append(x)
            merged[k] = out
    return merged

def merge_restore(live, snap):
    """公共字段取快照，provider 字段保留 live。返回合并后的 dict。"""
    merged = dict(live)
    for k in ("statusLine", "enabledPlugins", "extraKnownMarketplaces"):
        if k in snap:
            merged[k] = snap[k]
    if "hooks" in snap or "hooks" in live:
        live_hooks = live.get("hooks") if isinstance(live.get("hooks"), dict) else {}
        snap_hooks = snap.get("hooks") if isinstance(snap.get("hooks"), dict) else {}
        merged["hooks"] = merge_hooks(live_hooks, snap_hooks)
    if "permissions" in snap or "permissions" in live:
        merged["permissions"] = merge_permissions(
            live.get("permissions"), snap.get("permissions"))
    live_env = live.get("env") if isinstance(live.get("env"), dict) else {}
    snap_env = snap.get("env") if isinstance(snap.get("env"), dict) else {}
    env = dict(live_env)
    for k, v in snap_env.items():
        if not k.startswith("ANTHROPIC_"):
            env.setdefault(k, v)
    merged["env"] = env
    return merged

def main():
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            live = json.load(f)
        if not isinstance(live, dict):
            print(emit("error", "settings.json 顶层结构不是对象，跳过恢复"))
            return
    except Exception as e:
        print(emit("error", f"read settings.json failed: {e}"))
        return

    if not os.path.isfile(DB):
        print(emit("warn", "cc-switch DB 不存在，跳过检测"))
        return

    try:
        con = sqlite3.connect(DB, timeout=5)
        row = con.execute("SELECT value FROM settings WHERE key=?", (KEY,)).fetchone()
        con.close()
        if not row:
            print(emit("warn", "cc-switch DB 无 common_config_claude 快照，跳过检测"))
            return
        snap = json.loads(row[0])
        if not isinstance(snap, dict):
            print(emit("warn", "cc-switch 快照顶层结构不是对象，跳过恢复"))
            return
    except Exception as e:
        print(emit("warn", f"读 cc-switch DB 失败，跳过检测: {e}"))
        return

    degraded, reason = is_degraded(live, snap)
    if not degraded:
        return  # 静默

    merged = merge_restore(live, snap)
    # 快照本身也缺 marker 时（恢复也无济于事）不写文件，只警告
    still_degraded, still_reason = is_degraded(merged, snap)
    if still_degraded:
        print(emit("warn",
            f"检测到降级({reason})但快照本身也缺字段({still_reason})，不写文件。"
            f"请修复 settings.json 后跑 cc-switch-setting-sync"))
        return

    bakdir = os.path.join(os.path.dirname(SETTINGS), "backups")
    os.makedirs(bakdir, exist_ok=True)
    ts = f"{time.strftime('%Y%m%d_%H%M%S')}-{os.getpid()}-{time.time_ns() % 1_000_000:06d}"
    bak = os.path.join(bakdir, f"settings.bak-guard-{ts}.json")
    tmp = f"{SETTINGS}.{os.getpid()}.tmp"
    try:
        shutil.copy2(SETTINGS, bak)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, SETTINGS)
    except Exception as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        print(emit("error", f"恢复 settings.json 失败: {e}"))
        return
    print(emit("restored",
        f"检测到配置降级（{reason}），已从 cc-switch 快照自动恢复，备份在 {bak}。"
        f"statusline 等配置下一个会话生效。"))

if __name__ == "__main__":
    main()
