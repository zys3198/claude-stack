#!/usr/bin/env python3
"""Sync Claude settings.json provider-independent config into ccswitch DB.

USAGE:
  python sync_claude_common.py                 # live write (settings.json -> DB)
  python sync_claude_common.py --dry-run       # preview only, no DB write
  python sync_claude_common.py --restore       # fix mode (DB snapshot -> settings.json)
  python sync_claude_common.py --config PATH   # custom settings.json path
  python sync_claude_common.py --db PATH       # custom cc-switch.db path

--restore: merge DB common snapshot back into a degraded settings.json
(missing statusLine/enabledPlugins/hooks), keeping live provider fields
(ANTHROPIC_* env, model). Backs up settings.json before writing. Idempotent.
"""
import argparse, datetime, json, os, sqlite3, sys

DEFAULT_CONFIG = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".cc-switch", "cc-switch.db")
KEY = "common_config_claude"

# provider-specific env keys removed from common (injected by ccswitch + proxy)
PROVIDER_ENV_KEYS = {
    "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
    "ANTHROPIC_DEFAULT_FABLE_MODEL", "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",
    "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",
}


def extract_common(config_text: str) -> str:
    """Parse settings.json, drop provider-specific fields, re-dump indented JSON.

    Drops: top-level `model`; env entries for ANTHROPIC_* (token/base_url/model mapping).
    These are injected by ccswitch on switch from the provider template + proxy rewrite.
    """
    data = json.loads(config_text)
    data.pop("model", None)
    env = data.get("env")
    if isinstance(env, dict):
        data["env"] = {k: v for k, v in env.items() if k not in PROVIDER_ENV_KEYS}
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def merge_hooks(live_hooks, snap_hooks):
    """事件组合并：快照组在前（权威），live 独有组在后（新增 hook 保留）。"""
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
    """allow/deny/ask 并集合并，快照在前。deny 丢失=安全边界变宽，必须恢复。"""
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


def restore_settings(config_text: str, common_text: str) -> str:
    """Fix mode: merge DB common snapshot into a degraded settings.json.

    Common fields (statusLine/enabledPlugins/extraKnownMarketplaces/hooks/
    permissions/non-ANTHROPIC env) come from the snapshot; provider fields
    (top-level model, ANTHROPIC_* env) stay from the live config.
    """
    live = json.loads(config_text)
    snap = json.loads(common_text)
    merged = dict(live)
    for k in ("statusLine", "enabledPlugins", "extraKnownMarketplaces"):
        if k in snap:
            merged[k] = snap[k]
    if "hooks" in snap or "hooks" in live:
        merged["hooks"] = merge_hooks(live.get("hooks", {}), snap.get("hooks", {}))
    if "permissions" in snap or "permissions" in live:
        merged["permissions"] = merge_permissions(live.get("permissions"), snap.get("permissions"))
    env = dict(live.get("env", {}))
    for k, v in snap.get("env", {}).items():
        if not k.startswith("ANTHROPIC_"):
            env.setdefault(k, v)
    merged["env"] = env
    return json.dumps(merged, ensure_ascii=False, indent=2) + "\n"


def backup_db(cur, path):
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = {
        'ts': datetime.datetime.now().isoformat(),
        'settings': {r[0]: r[1] for r in cur.execute("SELECT key,value FROM settings")},
        'providers_claude': [dict(r) for r in cur.execute(
            "SELECT id,name,is_current,settings_config FROM providers WHERE app_type='claude'")],
    }
    outdir = os.path.join(os.path.dirname(path), 'backups')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f'sync-backup-{ts}.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    return outpath


def validate(new_common):
    must_present = ['enabledPlugins', 'extraKnownMarketplaces', 'hooks', 'env']
    must_absent = ['ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL',
                   'ANTHROPIC_DEFAULT_OPUS_MODEL']
    errors = []
    for m in must_present:
        if m not in new_common:
            errors.append(f"MISSING expected marker: {m!r}")
    for m in must_absent:
        if m in new_common:
            errors.append(f"LEAKED provider-specific content: {m!r}")
    return errors


def restore_main(args):
    """Fix mode: merge DB common snapshot back into settings.json.

    Idempotent: NO-OP when live config already matches. Backs up the live
    file before writing. Returns process exit code.
    """
    with open(args.config, encoding='utf-8-sig') as f:
        config_text = f.read()
    con = sqlite3.connect(args.db, timeout=10)
    row = con.execute("SELECT value FROM settings WHERE key=?", (KEY,)).fetchone()
    con.close()
    if not row:
        print("[FAIL] no common_config_claude snapshot in DB; run sync first")
        return 1
    new_text = restore_settings(config_text, row[0])
    # 语义比较（键序/空白差异不算变化），避免每次运行都重写+备份
    if json.dumps(json.loads(new_text), sort_keys=True) == \
       json.dumps(json.loads(config_text), sort_keys=True):
        print("[NO-OP] settings.json already matches snapshot")
        return 0

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bakdir = os.path.join(os.path.dirname(args.config), 'backups')
    os.makedirs(bakdir, exist_ok=True)
    bak = os.path.join(bakdir, f'settings.bak-restore-{ts}.json')
    with open(bak, 'w', encoding='utf-8') as f:
        f.write(config_text)

    tmp = args.config + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(new_text)
    os.replace(tmp, args.config)
    print(f"settings.json: {args.config}")
    print(f"backup       : {bak}")
    print(f"old len      : {len(config_text)}")
    print(f"new len      : {len(new_text)}")
    print("[DONE]")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Sync Claude settings.json common config into ccswitch DB")
    ap.add_argument('--config', default=DEFAULT_CONFIG, help='path to claude settings.json')
    ap.add_argument('--db', default=DEFAULT_DB, help='path to cc-switch.db')
    ap.add_argument('--dry-run', action='store_true', help='preview only, no DB write')
    ap.add_argument('--restore', action='store_true',
                    help='fix mode: merge DB snapshot back into settings.json')
    args = ap.parse_args()

    if args.restore:
        sys.exit(restore_main(args))

    with open(args.config, encoding='utf-8-sig') as f:
        config_text = f.read()
    new_common = extract_common(config_text)

    errs = validate(new_common)
    if errs:
        print("[FAIL] validation errors before write:")
        for e in errs:
            print("  -", e)
        print("\nRefusing to write. Check settings.json or adjust extract logic.")
        sys.exit(1)

    con = sqlite3.connect(args.db, timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT value FROM settings WHERE key=?", (KEY,))
    row = cur.fetchone()
    old = row[0] if row else None

    print(f"settings.json: {args.config}")
    print(f"cc-switch.db : {args.db}")
    print(f"old len      : {len(old) if old else 0}")
    print(f"new len      : {len(new_common)}")
    if old == new_common:
        print("[NO-OP] DB already in sync.")
        con.close()
        return

    if args.dry_run:
        print("[DRY-RUN] no write performed.")
        con.close()
        return

    bk = backup_db(cur, args.db)
    print(f"backup       : {bk}")
    cur.execute("UPDATE settings SET value=? WHERE key=?", (new_common, KEY))
    con.commit()

    cur.execute("SELECT value FROM settings WHERE key=?", (KEY,))
    chk = cur.fetchone()[0]
    ok = chk == new_common
    print(f"readback     : {'MATCH' if ok else 'MISMATCH!'} (len={len(chk)})")
    con.close()
    print("[DONE]" if ok else "[ERROR] readback mismatch")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
