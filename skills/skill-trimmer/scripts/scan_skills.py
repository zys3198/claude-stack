#!/usr/bin/env python3
"""枚举本机 skill 清单（skill-trimmer 第 1 步）。

只读。扫 ~/.claude/skills/ 下两种形态：
  - 直管目录（实体文件）
  - 软链（指向 cc-switch 源，删链接不删源，可恢复）
每个 skill 抽出 name / description / 来源 / 是否软链(含 junction) / 有无资产目录。
结果写 skill-trimmer-workspace/inventory.json（skill 目录旁）。

Windows 兼容：pathlib + utf-8。本机软链多为 junction（目录联接），
os.path.islink() 认不出，须用「realpath 是否偏离 abspath」判定——
junction 与 symlink 通吃。只读 link 目标，不创建不解 link。
"""

import json
import os
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
WORKSPACE = SKILLS_DIR.parent / "skill-trimmer-workspace"
ASSET_DIRS = ("scripts", "references", "assets")


def parse_frontmatter(skill_md: Path) -> dict:
    """手解析 YAML frontmatter 的 name/description，不引第三方 yaml。

    description 可能跨行（折叠标量），只取第一行非空内容做触发面参考——
    判定触发面宽窄仍需读全文，本字段仅供分组。
    """
    info = {"name": "", "description": ""}
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        info["error"] = f"read fail: {e}"
        return info
    if not text.startswith("---"):
        return info
    lines = text.splitlines()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:") and not info["name"]:
            info["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:") and not info["description"]:
            info["description"] = line.split(":", 1)[1].strip()[:200]
    return info


def scan() -> list:
    rows = []
    if not SKILLS_DIR.is_dir():
        return rows
    for entry in sorted(SKILLS_DIR.iterdir(), key=lambda p: p.name.lower()):
        s = str(entry)
        # lexists 连「指向不存在目标的符号链接」也认，is_dir 会漏掉断链
        is_dir_entry = entry.is_dir() or os.path.islink(s)
        if not is_dir_entry:
            continue
        # junction/symlink 通吃：realpath 偏离 abspath 即是链接（islink 认不出 junction）
        abspath = os.path.abspath(s)
        realpath = os.path.realpath(abspath)
        is_link = realpath.lower() != abspath.lower()
        target = realpath if is_link else ""
        # 真符号链接（非 junction）在 WinPython 下 realpath 可能解成 msys /c/... → 无法读目标
        unresolved = is_link and not os.path.isdir(realpath)
        skill_md = entry / "SKILL.md"
        try:
            has_md = skill_md.is_file()
        except OSError:
            has_md = False
        if not has_md and not unresolved:
            continue  # 普通目录但没 SKILL.md，不是 skill
        meta = parse_frontmatter(skill_md) if has_md else {"name": "", "description": ""}
        rows.append({
            "dir": entry.name,
            "name": meta.get("name") or entry.name,
            "description": meta.get("description", ""),
            "is_symlink": is_link,
            "source": target if is_link else "direct",
            "has_assets": any((entry / d).is_dir() for d in ASSET_DIRS) if not unresolved else False,
            **({"unresolved": True} if unresolved else {}),
            **({"error": meta["error"]} if "error" in meta else {}),
        })
    return rows


def main() -> int:
    rows = scan()
    WORKSPACE.mkdir(exist_ok=True)
    out = WORKSPACE / "inventory.json"
    out.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    direct = sum(1 for r in rows if not r["is_symlink"])
    links = len(rows) - direct
    with_assets = sum(1 for r in rows if r["has_assets"])
    print(f"total={len(rows)}  direct={direct}  symlink={links}  with_assets={with_assets}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
