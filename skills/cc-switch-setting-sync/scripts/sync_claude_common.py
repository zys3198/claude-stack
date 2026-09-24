#!/usr/bin/env python3
"""Sync Claude settings.json provider-independent config into ccswitch DB.

USAGE:
  python sync_claude_common.py                 # live write (settings.json -> DB)
  python sync_claude_common.py --dry-run       # preview only, no DB write
  python sync_claude_common.py --check         # compare live common view with DB
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
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_FABLE_MODEL", "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",
    "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",
}

# 这些键不是公共配置；provider 切换注入它们会掩盖用户的公共值。
FORBIDDEN_ENV_KEYS = (
    "CLAUDE_CODE_EFFORT_LEVEL",
    "CLAUDE_CODE_MAX_CONTEXT_TOKENS",
)
SENSITIVE_PATH_MARKERS = ("API_KEY", "AUTH_TOKEN", "PASSWORD", "SECRET")
MISSING = object()
PROXY_BACKUP_APP = "claude"
AUTO_COMPACT_ENV_KEY = "CLAUDE_CODE_AUTO_COMPACT_WINDOW"
PROXY_SYNC_ENV_KEYS = (AUTO_COMPACT_ENV_KEY,) + FORBIDDEN_ENV_KEYS


def extract_common(config_text: str) -> str:
    """Parse settings.json, drop provider-specific fields, re-dump indented JSON.

    Drops: top-level `model`; env entries for ANTHROPIC_* (token/base_url/model mapping).
    These are injected by ccswitch on switch from the provider template + proxy rewrite.
    """
    data = json.loads(config_text)
    if not isinstance(data, dict):
        raise ValueError("settings.json root must be an object")
    data.pop("model", None)
    env = data.get("env")
    if isinstance(env, dict):
        data["env"] = {k: v for k, v in env.items() if k not in PROVIDER_ENV_KEYS}
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _collect_differences(live, db, path, differences, limit):
    """收集公共配置差异；限制条数，避免把整份配置注入会话。"""
    if len(differences) >= limit:
        return
    if isinstance(live, dict) and isinstance(db, dict):
        for key in sorted(set(live) | set(db)):
            child = f"{path}.{key}" if path else str(key)
            _collect_differences(
                live.get(key, MISSING), db.get(key, MISSING),
                child, differences, limit,
            )
        return
    if isinstance(live, list) and isinstance(db, list):
        if live != db:
            differences.append((path or "<root>", live, db))
        return
    if type(live) is not type(db) or live != db:
        differences.append((path or "<root>", live, db))


def _safe_value(path, value):
    if value is MISSING:
        return "<missing>"
    if any(marker in path.upper() for marker in SENSITIVE_PATH_MARKERS):
        return "<redacted>"
    return repr(value)


def format_differences(live_text, db_text, limit=20):
    """返回标准化公共配置差异；不比较 JSON 空白和键顺序。"""
    live = json.loads(live_text)
    db = json.loads(db_text)
    differences = []
    _collect_differences(live, db, "", differences, limit)
    if not differences:
        return []
    lines = [f"[MISMATCH] common config differs (showing up to {limit} paths)"]
    for path, live_value, db_value in differences:
        lines.append(
            f"  {path}: live={_safe_value(path, live_value)}; "
            f"db={_safe_value(path, db_value)}"
        )
    return lines


def _structure_errors(data, label):
    if not isinstance(data, dict):
        return [f"{label} root must be an object"]
    errors = []
    for key in ("env", "hooks", "permissions"):
        if key in data and not isinstance(data[key], dict):
            errors.append(f"{label}.{key} must be an object")
    hooks = data.get("hooks")
    if isinstance(hooks, dict):
        for event, groups in hooks.items():
            if not isinstance(groups, list):
                errors.append(f"{label}.hooks.{event} must be an array")
    permissions = data.get("permissions")
    if isinstance(permissions, dict):
        for key in ("allow", "deny", "ask"):
            if key in permissions and not isinstance(permissions[key], list):
                errors.append(f"{label}.permissions.{key} must be an array")
    return errors


def _target_env_values(config):
    env = config.get("env") if isinstance(config, dict) else {}
    if not isinstance(env, dict):
        env = {}
    return {key: env.get(key, MISSING) for key in PROXY_SYNC_ENV_KEYS}


def _format_proxy_differences(before, after):
    lines = []
    for key in PROXY_SYNC_ENV_KEYS:
        if before[key] == after[key]:
            continue
        path = f"proxy_live_backup.env.{key}"
        lines.append(
            f"  {path}: old={_safe_value(path, before[key])}; "
            f"new={_safe_value(path, after[key])}"
        )
    return lines


def prepare_proxy_backup(raw, live_common):
    """按 live 公共配置修正代理快照目标键，保留其余代理字段。"""
    snapshot = json.loads(raw)
    if not isinstance(snapshot, dict):
        raise ValueError("proxy_live_backup original_config root is not an object")
    live = json.loads(live_common)
    snapshot_env = snapshot.get("env")
    if not isinstance(snapshot_env, dict):
        raise ValueError("proxy_live_backup original_config.env is not an object")
    live_env = live.get("env") if isinstance(live.get("env"), dict) else {}
    before = _target_env_values(snapshot)
    desired_auto = live_env.get(AUTO_COMPACT_ENV_KEY, MISSING)
    if desired_auto is MISSING:
        snapshot_env.pop(AUTO_COMPACT_ENV_KEY, None)
    else:
        snapshot_env[AUTO_COMPACT_ENV_KEY] = desired_auto
    for key in FORBIDDEN_ENV_KEYS:
        snapshot_env.pop(key, None)
    after = _target_env_values(snapshot)
    new_raw = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    changed = (
        json.dumps(json.loads(raw), sort_keys=True)
        != json.dumps(json.loads(new_raw), sort_keys=True)
    )
    return new_raw, before, after, changed


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
    """权限列表按公共快照精确覆盖，避免旧规则通过并集合并复活。"""
    if not isinstance(snap_perm, dict):
        return live_perm
    merged = dict(live_perm or {})
    list_keys = {"allow", "deny", "ask"}
    for k in list_keys:
        if k in snap_perm:
            merged[k] = list(snap_perm[k])
        else:
            merged.pop(k, None)
    for k, value in snap_perm.items():
        if k not in list_keys:
            merged[k] = value
    return merged


def restore_settings(config_text: str, common_text: str) -> str:
    """Fix mode: merge DB common snapshot into a degraded settings.json.

    Common fields (statusLine/enabledPlugins/extraKnownMarketplaces/hooks/
    permissions/non-ANTHROPIC env) come from the snapshot; provider fields
    (top-level model, ANTHROPIC_* env) stay from the live config.
    """
    live = json.loads(config_text)
    snap = json.loads(common_text)
    shape_errors = _structure_errors(live, "settings.json") + _structure_errors(
        snap, "common snapshot"
    )
    if shape_errors:
        raise ValueError("; ".join(shape_errors))
    merged = dict(live)
    for k, v in snap.items():
        if k not in {"model", "hooks", "permissions", "env"}:
            merged[k] = v
    for k in ("statusLine", "enabledPlugins", "extraKnownMarketplaces"):
        if k in snap:
            merged[k] = snap[k]
    if "hooks" in snap or "hooks" in live:
        merged["hooks"] = merge_hooks(live.get("hooks", {}), snap.get("hooks", {}))
    if "permissions" in snap or "permissions" in live:
        merged["permissions"] = merge_permissions(live.get("permissions"), snap.get("permissions"))
    live_env = live.get("env", {})
    env = dict(live_env) if isinstance(live_env, dict) else {}
    for key in FORBIDDEN_ENV_KEYS:
        env.pop(key, None)
    snap_env = snap.get("env", {})
    if not isinstance(snap_env, dict):
        snap_env = {}
    for k, v in snap_env.items():
        if not k.startswith("ANTHROPIC_") and k not in FORBIDDEN_ENV_KEYS:
            env[k] = v
    merged["env"] = env
    return json.dumps(merged, ensure_ascii=False, indent=2) + "\n"


def backup_db(cur, path):
    now = datetime.datetime.now()
    ts = now.strftime('%Y%m%d_%H%M%S_%f')
    backup = {
        'ts': now.isoformat(),
        'settings': {r[0]: r[1] for r in cur.execute("SELECT key,value FROM settings")},
        'providers_claude': [dict(r) for r in cur.execute(
            "SELECT id,name,is_current,settings_config FROM providers WHERE app_type='claude'")],
        'proxy_live_backup': [dict(r) for r in cur.execute(
            "SELECT app_type,original_config,backed_up_at FROM proxy_live_backup")],
    }
    outdir = os.path.join(os.path.dirname(path), 'backups')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, f'sync-backup-{ts}.json')
    with open(outpath, 'x', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    return outpath


def validate(new_common):
    must_present = ['enabledPlugins', 'extraKnownMarketplaces', 'hooks', 'env']
    errors = []
    try:
        data = json.loads(new_common)
    except json.JSONDecodeError as exc:
        return [f"invalid common JSON: {exc}"]
    if not isinstance(data, dict):
        return ["common JSON root must be an object"]
    for marker in must_present:
        if marker not in data:
            errors.append(f"MISSING expected marker: {marker!r}")
    errors.extend(_structure_errors(data, "common"))
    env = data.get('env')
    if not isinstance(env, dict):
        env = {}
    for key in sorted(PROVIDER_ENV_KEYS):
        if key in env:
            errors.append(f"LEAKED provider-specific content: {key!r}")
    for key in FORBIDDEN_ENV_KEYS:
        if key in env:
            errors.append(f"FORBIDDEN common env key: {key!r}")
    return errors


def _read_only_connection(path):
    absolute = os.path.abspath(path).replace("\\", "/")
    return sqlite3.connect(
        f"file:{absolute}?mode=ro", uri=True, timeout=10
    )


def read_db_common(path):
    con = _read_only_connection(path)
    try:
        row = con.execute("SELECT value FROM settings WHERE key=?", (KEY,)).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def read_db_snapshots(path, live_common):
    con = _read_only_connection(path)
    try:
        con.execute("BEGIN")
        common_row = con.execute(
            "SELECT value FROM settings WHERE key=?", (KEY,)
        ).fetchone()
        if not common_row:
            return None, None
        proxy_row = con.execute(
            "SELECT original_config FROM proxy_live_backup WHERE app_type=?",
            (PROXY_BACKUP_APP,),
        ).fetchone()
        proxy_plan = prepare_proxy_backup(proxy_row[0], live_common) if proxy_row else None
        return common_row[0], proxy_plan
    finally:
        con.close()


def check_main(args):
    """只读比较 settings.json 公共视图与 DB 快照。"""
    with open(args.config, encoding='utf-8-sig') as f:
        config_text = f.read()
    try:
        live_common = extract_common(config_text)
    except ValueError as exc:
        print("[MISMATCH] invalid settings.json common config")
        print(f"  - {exc}")
        return 2
    errors = validate(live_common)
    if errors:
        print("[MISMATCH] settings.json cannot be synced as common config")
        for error in errors:
            print(f"  - {error}")
        return 2

    try:
        db_common, proxy_plan = read_db_snapshots(args.db, live_common)
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f"[ERROR] cannot read cc-switch DB: {exc}")
        return 1
    if db_common is None:
        print("[ERROR] no common_config_claude snapshot in DB")
        return 1
    differences = format_differences(live_common, db_common)
    proxy_differences = []
    if proxy_plan:
        _, before, after, _ = proxy_plan
        proxy_differences = _format_proxy_differences(before, after)
    if proxy_plan is None:
        print("[WARN] no claude proxy_live_backup row; proxy backup not checked")
    if not differences and not proxy_differences:
        if proxy_plan is None:
            return 2
        print("[MATCH] settings.json common config and proxy backup match")
        return 0
    if differences:
        print("\n".join(differences))
    if proxy_differences:
        print("[MISMATCH] proxy_live_backup target config differs")
        print("\n".join(proxy_differences))
    return 2


def restore_main(args):
    """Fix mode: merge DB common snapshot back into settings.json.

    Idempotent: NO-OP when live config already matches. Backs up the live
    file before writing. Returns process exit code.
    """
    with open(args.config, encoding='utf-8-sig') as f:
        config_text = f.read()
    try:
        common_text = read_db_common(args.db)
    except (OSError, sqlite3.Error) as exc:
        print(f"[FAIL] cannot read cc-switch DB: {exc}")
        return 1
    if common_text is None:
        print("[FAIL] no common_config_claude snapshot in DB; run sync first")
        return 1
    try:
        new_text = restore_settings(config_text, common_text)
    except (TypeError, ValueError) as exc:
        print(f"[FAIL] invalid settings or common snapshot: {exc}")
        return 1
    # 语义比较（键序/空白差异不算变化），避免每次运行都重写+备份
    if json.dumps(json.loads(new_text), sort_keys=True) == \
       json.dumps(json.loads(config_text), sort_keys=True):
        print("[NO-OP] settings.json already matches snapshot")
        return 0

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    bakdir = os.path.join(os.path.dirname(args.config), 'backups')
    os.makedirs(bakdir, exist_ok=True)
    bak = os.path.join(bakdir, f'settings.bak-restore-{ts}.json')
    with open(bak, 'x', encoding='utf-8') as f:
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
    ap.add_argument('--check', action='store_true',
                    help='read-only semantic comparison of settings.json and DB')
    ap.add_argument('--restore', action='store_true',
                    help='fix mode: merge DB snapshot back into settings.json')
    args = ap.parse_args()

    if args.check:
        sys.exit(check_main(args))

    if args.restore:
        sys.exit(restore_main(args))

    with open(args.config, encoding='utf-8-sig') as f:
        config_text = f.read()
    try:
        new_common = extract_common(config_text)
    except ValueError as exc:
        print("[FAIL] invalid settings.json common config:", exc)
        sys.exit(1)

    errs = validate(new_common)
    if errs:
        print("[FAIL] validation errors before write:")
        for e in errs:
            print("  -", e)
        print("\nRefusing to write. Check settings.json or adjust extract logic.")
        sys.exit(1)

    try:
        con = (
            _read_only_connection(args.db)
            if args.dry_run else sqlite3.connect(args.db, timeout=10)
        )
    except (OSError, sqlite3.Error) as exc:
        print(f"[FAIL] cannot open cc-switch DB: {exc}")
        sys.exit(1)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if not args.dry_run:
        cur.execute("BEGIN IMMEDIATE")

    cur.execute("SELECT value FROM settings WHERE key=?", (KEY,))
    row = cur.fetchone()
    old = row[0] if row else None
    common_differences = format_differences(new_common, old) if old is not None else []

    proxy_row = cur.execute(
        "SELECT original_config FROM proxy_live_backup WHERE app_type=?",
        (PROXY_BACKUP_APP,),
    ).fetchone()
    try:
        proxy_plan = prepare_proxy_backup(proxy_row[0], new_common) if proxy_row else None
    except (TypeError, ValueError) as exc:
        print(f"[FAIL] invalid claude proxy_live_backup row: {exc}")
        if not args.dry_run:
            con.rollback()
        con.close()
        sys.exit(1)
    proxy_differences = []
    proxy_changed = False
    if proxy_plan:
        _, before, after, proxy_changed = proxy_plan
        proxy_differences = _format_proxy_differences(before, after)

    print(f"settings.json: {args.config}")
    print(f"cc-switch.db : {args.db}")
    print(f"old len      : {len(old) if old else 0}")
    print(f"new len      : {len(new_common)}")
    if proxy_plan is None:
        print("[WARN] no claude proxy_live_backup row; common sync will not rebuild it.")
    if not common_differences and not proxy_changed and old is not None:
        if proxy_plan is None:
            print("[NO-OP] DB common config is in sync; proxy backup is missing.")
        else:
            print("[NO-OP] DB common config and proxy backup already in sync.")
        if not args.dry_run:
            con.rollback()
        con.close()
        return
    if common_differences:
        print("\n".join(common_differences))
    if proxy_differences:
        print("[MISMATCH] proxy_live_backup target config differs")
        print("\n".join(proxy_differences))

    if args.dry_run:
        print("[DRY-RUN] no write performed.")
        con.close()
        return

    try:
        bk = backup_db(cur, args.db)
        print(f"backup       : {bk}")
        if old is None:
            cur.execute("INSERT INTO settings(key,value) VALUES(?,?)", (KEY, new_common))
        else:
            cur.execute("UPDATE settings SET value=? WHERE key=?", (new_common, KEY))
        if proxy_plan and proxy_changed:
            cur.execute(
                "UPDATE proxy_live_backup SET original_config=? WHERE app_type=?",
                (proxy_plan[0], PROXY_BACKUP_APP),
            )
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise

    chk = cur.execute("SELECT value FROM settings WHERE key=?", (KEY,)).fetchone()
    common_ok = bool(chk) and chk[0] == new_common
    print(f"common readback: {'MATCH' if common_ok else 'MISMATCH!'}")
    proxy_ok = True
    if proxy_plan and proxy_changed:
        proxy_chk = cur.execute(
            "SELECT original_config FROM proxy_live_backup WHERE app_type=?",
            (PROXY_BACKUP_APP,),
        ).fetchone()
        proxy_ok = bool(proxy_chk) and proxy_chk[0] == proxy_plan[0]
        print(f"proxy readback : {'MATCH' if proxy_ok else 'MISMATCH!'}")
    ok = common_ok and proxy_ok
    con.close()
    print("[DONE]" if ok else "[ERROR] readback mismatch")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
