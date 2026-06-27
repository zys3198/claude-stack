#!/usr/bin/env python3
"""Sync Claude ~/.claude/settings.json provider-independent config into ccswitch DB.

USAGE:
  python sync_claude_common.py                 # live write
  python sync_claude_common.py --dry-run       # preview only, no DB write
  python sync_claude_common.py --config PATH   # custom settings.json path
  python sync_claude_common.py --db PATH       # custom cc-switch.db path
"""
import argparse, datetime, json, os, sqlite3, sys

DEFAULT_CONFIG = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".cc-switch", "cc-switch.db")
KEY = "common_config_claude"

# env keys prefixed ANTHROPIC_ are provider-specific (auth token, base_url,
# model mappings). ccswitch injects them on switch from the provider template.
# Keep provider-agnostic env (CLAUDE_CODE_*, ENABLE_TOOL_SEARCH, etc).
PROVIDER_ENV_PREFIX = "ANTHROPIC_"


def extract_common(json_text: str) -> str:
    """Drop provider-specific env keys; keep everything else as JSON.

    Strips BOM, parses JSON, removes env.* keys starting with ANTHROPIC_
    (AUTH_TOKEN / BASE_URL / DEFAULT_*_MODEL* / ANTHROPIC_MODEL — all injected
    by ccswitch on switch from the provider template). Returns re-serialized
    JSON (indent=2, ensure_ascii=False).
    """
    if json_text.startswith('﻿'):
        json_text = json_text[1:]
    d = json.loads(json_text)
    env = d.get('env')
    if isinstance(env, dict):
        for k in list(env.keys()):
            if k.startswith(PROVIDER_ENV_PREFIX):
                del env[k]
        if not env:
            del d['env']
    return json.dumps(d, ensure_ascii=False, indent=2)


def backup_db(cur, path):
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = {
        'ts': datetime.datetime.now().isoformat(),
        'settings': {r[0]: r[1] for r in cur.execute("SELECT key,value FROM settings")},
        'providers_claude': [dict(r) for r in cur.execute(
            "SELECT id,name,is_current,settings_config,meta FROM providers WHERE app_type='claude'")],
        'proxy_live_backup': [dict(r) for r in cur.execute(
            "SELECT app_type,backed_up_at,original_config FROM proxy_live_backup WHERE app_type='claude'")],
    }
    outdir = os.path.join(os.path.dirname(path), 'backups')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f'sync-backup-{ts}.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    return outpath


def validate(new_common):
    must_present = [
        '"hooks"',
        '"enabledPlugins"',
        '"permissions"',
        '"statusLine"',
    ]
    must_absent = [
        'ANTHROPIC_AUTH_TOKEN',
        'ANTHROPIC_BASE_URL',
        'ANTHROPIC_MODEL',
    ]
    errors = []
    for m in must_present:
        if m not in new_common:
            errors.append(f"MISSING expected marker: {m!r}")
    for m in must_absent:
        if m in new_common:
            errors.append(f"LEAKED provider-specific content: {m!r}")
    return errors


def main():
    ap = argparse.ArgumentParser(description="Sync Claude settings.json common config into ccswitch DB")
    ap.add_argument('--config', default=DEFAULT_CONFIG, help='path to claude settings.json')
    ap.add_argument('--db', default=DEFAULT_DB, help='path to cc-switch.db')
    ap.add_argument('--dry-run', action='store_true', help='preview only, no DB write')
    args = ap.parse_args()

    with open(args.config, encoding='utf-8-sig') as f:
        json_text = f.read()
    new_common = extract_common(json_text)

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
