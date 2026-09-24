"""校验 installing/ 下的四张台账现状表。

只读，不挂 hook，不阻断操作。退出码 0 表示全过，1 表示有错。
判据见 references/ledger-protocol.md。
"""

import json
import os
import re
import sys

LEDGERS = ["custom-setup", "skill-install", "tool-install", "mcp-install"]
HEADER = ["名称", "状态", "位置", "出处", "恢复", "备注"]
STATES = {"在用", "停用", "已归档", "待核"}
MAX_BYTES = 20 * 1024

INSTALLING = os.path.join(os.path.expanduser("~"), ".claude", "installing")
ARCHIVE = os.path.join(INSTALLING, "archive")
SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def split_row(line):
    """拆一行 markdown 表格；\\| 是转义竖线，不当分隔符。"""
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s[1:-1] if s.endswith("|") else s[1:]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def is_sep(cells):
    return bool(cells) and all(c and set(c) <= set("-: ") for c in cells)


def tables(lines):
    """产出 (行号, 表头, 数据行)。表头是 |---| 上一行。"""
    i = 0
    while i < len(lines) - 1:
        head = split_row(lines[i])
        if head and is_sep(split_row(lines[i + 1]) or []):
            rows, j = [], i + 2
            while j < len(lines):
                r = split_row(lines[j])
                if r is None or not any(r):
                    break
                rows.append((j + 1, r))
                j += 1
            yield i + 1, head, rows
            i = j
        else:
            i += 1


def check(name):
    path = os.path.join(INSTALLING, name + ".md")
    if not os.path.isfile(path):
        return [f"{name}.md 不存在"], 0, 0, 0

    size = os.path.getsize(path)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    errors, pending, rowcount, found_table = [], 0, 0, False

    for lineno, head, rows in tables(lines):
        if head != HEADER:
            if "名称" in head and "状态" in head:
                errors.append(f"{name}.md:{lineno} 表头不是规定的 6 列，实际 {head}")
            continue
        found_table = True
        seen = {}
        for rno, cells in rows:
            if len(cells) != 6:
                errors.append(f"{name}.md:{rno} 列数 {len(cells)}，应为 6")
                continue
            rowcount += 1
            item, state = cells[0], cells[1]
            if not item:
                errors.append(f"{name}.md:{rno} 名称空的")
            elif item in seen:
                errors.append(f"{name}.md:{rno} 本表内名称重复「{item}」，首次在 {seen[item]} 行")
            else:
                seen[item] = rno
            if state not in STATES:
                errors.append(f"{name}.md:{rno} 状态「{state}」不在 {sorted(STATES)} 内")
            elif state == "待核":
                pending += 1

    if not found_table:
        errors.append(f"{name}.md 没找到符合的现状表")
    if size > MAX_BYTES:
        errors.append(f"{name}.md 体量 {size / 1024:.1f} KB，超过 {MAX_BYTES // 1024} KB 上限")

    return errors, rowcount, pending, size


def plugin_state_check():
    """插件表的 在用/停用 与 settings.json 的 enabledPlugins 逐项比对。"""
    ledger = os.path.join(INSTALLING, "tool-install.md")
    if not os.path.isfile(ledger) or not os.path.isfile(SETTINGS):
        return ["插件状态无法比对：缺 tool-install.md 或 settings.json"], 0
    with open(SETTINGS, encoding="utf-8") as f:
        enabled = json.load(f).get("enabledPlugins", {})
    with open(ledger, encoding="utf-8") as f:
        lines = f.read().splitlines()

    rows = {}
    for _, _, cells in tables(lines):
        for rno, c in cells:
            # 插件行的位置以 plugins/cache/ 开头；marketplace 行是 plugins/marketplaces/
            if len(c) == 6 and c[2].strip("`").startswith("plugins/cache/") and c[0] not in rows:
                rows[c[0]] = (rno, c[1])

    errors = []
    for key, on in sorted(enabled.items()):
        pname = key.split("@", 1)[0]
        want = "在用" if on else "停用"
        if pname not in rows:
            errors.append(f"tool-install.md 插件表缺「{pname}」（settings.json: {key} = {on}）")
        elif rows[pname][1] != want:
            errors.append(
                f"tool-install.md:{rows[pname][0]}「{pname}」写 {rows[pname][1]}，"
                f"settings.json 为 {on} → 应为 {want}"
            )
    known = {k.split("@", 1)[0] for k in enabled}
    for pname, (rno, state) in sorted(rows.items()):
        if pname not in known and state in ("在用", "停用"):
            errors.append(f"tool-install.md:{rno}「{pname}」不在 enabledPlugins 里，状态不该是 {state}")
    return errors, len(rows)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    all_errors, total_rows, total_pending, total_bytes = [], 0, 0, 0
    for name in LEDGERS:
        errors, rows, pending, size = check(name)
        all_errors += errors
        total_rows += rows
        total_pending += pending
        total_bytes += size
        flag = "OK" if not errors else f"{len(errors)} 处问题"
        print(f"{name + '.md':<20} {rows:>3} 行 · 待核 {pending} · {size / 1024:>5.1f} KB   {flag}")

    print(f"{'合计':<18} {total_rows:>3} 行 · 待核 {total_pending} · {total_bytes / 1024:>5.1f} KB")

    print()
    perrors, pcount = plugin_state_check()
    all_errors += perrors
    print(f"插件状态     {pcount} 行比对 enabledPlugins" + (f"，{len(perrors)} 处不符" if perrors else "，全相符"))

    if os.path.isdir(ARCHIVE):
        present = sorted(f[:-3] for f in os.listdir(ARCHIVE) if f.endswith(".md"))
        missing = [n for n in LEDGERS if n not in present]
        print(f"archive/ 有 {len(present)} 份流水" + (f"，缺 {missing}" if missing else "，四份齐"))
    else:
        print("archive/ 目录不存在")
        all_errors.append("archive/ 缺失")

    if all_errors:
        print()
        for e in all_errors:
            print("  ✗", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
