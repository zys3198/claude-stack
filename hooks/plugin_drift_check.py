#!/usr/bin/env python3
"""SessionStart hook：插件台账漂移检测（pi skill-sync-watch 移植，2026-08-28）。

对照 settings.json enabledPlugins 与 baseline 快照（enabled/disabled 双集合，
2026-08-28 二版：初版只记 keys，漏掉 true<->false 翻转，复核时修复）：
  - baseline 之外新增 enabled → 上游新增/手动开启（只报告不纳入）
  - baseline 之内消失/被禁   → 移除（可能是有意裁剪，提示确认）
  - enabled<->disabled 翻转  → 禁用/启用（提示确认）
  - enabled 但插件缓存缺失   → 破损 enable（幂等软检查，skills-dir 除外）

只报告不自动修复（pi 治理哲学：纳入须人确认）。无漂移时静默。

baseline 存于 ~/.claude/installing/plugin-drift-baseline.json，首轮自动建。
旧版 baseline（无 disabled 键）视为 schema 过期，自动重建。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

SETTINGS = os.path.expanduser("~/.claude/settings.json")
PLUGINS_DIR = os.path.expanduser("~/.claude/plugins/cache")
BASELINE = os.path.expanduser("~/.claude/installing/plugin-drift-baseline.json")


def plugin_states():
    """enabledPlugins -> (enabled_set, disabled_set)。value=true 才算启用。"""
    try:
        with open(SETTINGS, "r", encoding="utf-8") as f:
            raw = json.load(f).get("enabledPlugins", {}) or {}
    except Exception:
        return set(), set()
    enabled = {name for name, flag in raw.items() if flag}
    disabled = {name for name, flag in raw.items() if not flag}
    return enabled, disabled


def installed_marketplace_plugins():
    """缓存中已安装的 <plugin>@<marketplace> 集合（skills-dir 插件不在 cache）。"""
    out = set()
    try:
        if not os.path.isdir(PLUGINS_DIR):
            return out
        for mp in os.listdir(PLUGINS_DIR):
            mp_dir = os.path.join(PLUGINS_DIR, mp)
            if not os.path.isdir(mp_dir):
                continue
            for pl in os.listdir(mp_dir):
                out.add(f"{pl}@{mp}")
    except Exception:
        pass
    return out


def load_baseline():
    try:
        with open(BASELINE, "r", encoding="utf-8") as f:
            b = json.load(f)
        if not isinstance(b, dict) or "disabled" not in b:
            return None  # 旧版/损坏 baseline，重建
        return set(b.get("enabled", [])), set(b.get("disabled", []))
    except Exception:
        return None


def save_baseline(enabled, disabled):
    try:
        os.makedirs(os.path.dirname(BASELINE), exist_ok=True)
        with open(BASELINE, "w", encoding="utf-8") as f:
            json.dump(
                {"enabled": sorted(enabled), "disabled": sorted(disabled)},
                f, ensure_ascii=False, indent=1,
            )
        return True
    except Exception:
        return False


def report(lines):
    return json.dumps({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "[plugin-drift-check]\n" + "\n".join(lines),
        },
    }, ensure_ascii=False)


def main():
    enabled, disabled = plugin_states()
    baseline = load_baseline()
    if baseline is None:
        save_baseline(enabled, disabled)
        return ""  # 首轮/重建只写 baseline，静默

    base_enabled, base_disabled = baseline
    installed = installed_marketplace_plugins()
    lines = []

    added = sorted(enabled - base_enabled - base_disabled)
    if added:
        lines.append("插件台账新增（确认保留请更新 baseline）:")
        lines += [f"  + {n}" for n in added]
    removed = sorted((base_enabled | base_disabled) - enabled - disabled)
    if removed:
        lines.append("插件台账移除（可能是有意裁剪）:")
        lines += [f"  - {n}" for n in removed]
    turned_on = sorted(enabled & base_disabled)
    if turned_on:
        lines.append("插件重新启用:")
        lines += [f"  > {n}" for n in turned_on]
    turned_off = sorted(disabled & base_enabled)
    if turned_off:
        lines.append("插件被禁用:")
        lines += [f"  x {n}" for n in turned_off]
    broken = sorted(n for n in enabled - installed if not n.endswith("@skills-dir"))
    if broken:
        lines.append("enabled 但缓存缺失（可能 enable 失效）:")
        lines += [f"  ! {n}" for n in broken]
    return report(lines) if lines else ""


if __name__ == "__main__":
    print(main())
