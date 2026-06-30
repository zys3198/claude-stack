#!/usr/bin/env python3
"""Sync Codex config.toml provider-independent config into ccswitch DB.

USAGE:
  python sync_codex_common.py                 # live write
  python sync_codex_common.py --dry-run       # preview only, no DB write
  python sync_codex_common.py --config PATH   # custom config.toml path
  python sync_codex_common.py --db PATH       # custom cc-switch.db path
"""
import argparse, datetime, json, os, re, sqlite3, sys

DEFAULT_CONFIG = os.path.join(os.path.expanduser("~"), ".codex", "config.toml")
DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".cc-switch", "cc-switch.db")
KEY = "common_config_codex"


def extract_common(toml_text: str) -> str:
    """Strip BOM + provider-specific lines; keep everything else.

    Drops: BOM, model_provider, model, model_*, [model_providers], [model_providers.custom] block.
    These are injected by ccswitch on switch from the provider template + proxy rewrite.
    """
    if toml_text.startswith('\ufeff'):
        toml_text = toml_text[1:]
    out, skip = [], False
    for ln in toml_text.splitlines():
        s = ln.strip()
        if re.match(r'^model_provider\s*=', s):
            continue
        if re.match(r'^model\s*=\s*"', s):
            continue
        if s == '[model_providers]':
            continue
        if s == '[model_providers.custom]':
            skip = True
            continue
        if skip:
            if s.startswith('['):
                skip = False
            else:
                continue
        out.append(ln)
    return '\n'.join(out).rstrip() + '\n'


def backup_db(cur, path):
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = {
        'ts': datetime.datetime.now().isoformat(),
        'settings': {r[0]: r[1] for r in cur.execute("SELECT key,value FROM settings")},
        'providers_codex': [dict(r) for r in cur.execute(
            "SELECT id,name,is_current,settings_config,meta FROM providers WHERE app_type='codex'")],
        'proxy_live_backup': [dict(r) for r in cur.execute(
            "SELECT app_type,backed_up_at,original_config FROM proxy_live_backup WHERE app_type='codex'")],
    }
    outdir = os.path.join(os.path.dirname(path), 'backups')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f'sync-backup-{ts}.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    return outpath


def validate(new_common):
    must_present = [
        'sandbox_mode', 'approval_policy', '[features]', '[hooks.state]',
        'projects.', '[mcp_servers.',
    ]
    must_absent = ['model_provider', 'model_providers.custom', 'experimental_bearer_token']
    errors = []
    for m in must_present:
        if m not in new_common:
            errors.append(f"MISSING expected marker: {m!r}")
    for m in must_absent:
        if m in new_common:
            errors.append(f"LEAKED provider-specific content: {m!r}")
    return errors


def main():
    ap = argparse.ArgumentParser(description="Sync Codex config.toml common config into ccswitch DB")
    ap.add_argument('--config', default=DEFAULT_CONFIG, help='path to codex config.toml')
    ap.add_argument('--db', default=DEFAULT_DB, help='path to cc-switch.db')
    ap.add_argument('--dry-run', action='store_true', help='preview only, no DB write')
    args = ap.parse_args()

    with open(args.config, encoding='utf-8-sig') as f:
        toml_text = f.read()
    new_common = extract_common(toml_text)

    errs = validate(new_common)
    if errs:
        print("[FAIL] validation errors before write:")
        for e in errs:
            print("  -", e)
        print("\nRefusing to write. Check config.toml or adjust extract logic.")
        sys.exit(1)

    con = sqlite3.connect(args.db, timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT value FROM settings WHERE key=?", (KEY,))
    row = cur.fetchone()
    old = row[0] if row else None

    print(f"config.toml : {args.config}")
    print(f"cc-switch.db: {args.db}")
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
