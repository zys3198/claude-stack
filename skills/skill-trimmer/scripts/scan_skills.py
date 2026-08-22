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

import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
WORKSPACE = SKILLS_DIR.parent / "skill-trimmer-workspace"
ASSET_DIRS = ("scripts", "references", "assets")
STALE_DAYS = 180  # 零使用 + 超此天数未改 → 保鲜候选


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
        # 内容新鲜度取 SKILL.md，断链/无 md 回落目录，失败记 0
        try:
            mtime = skill_md.stat().st_mtime if has_md else entry.stat().st_mtime
        except OSError:
            mtime = 0.0
        rows.append({
            "dir": entry.name,
            "name": meta.get("name") or entry.name,
            "description": meta.get("description", ""),
            "is_symlink": is_link,
            "source": target if is_link else "direct",
            "has_assets": any((entry / d).is_dir() for d in ASSET_DIRS) if not unresolved else False,
            "last_modified": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d") if mtime else "",
            **({"unresolved": True} if unresolved else {}),
            **({"error": meta["error"]} if "error" in meta else {}),
        })
    return rows


def load_usage() -> Counter:
    """读 metrics/skill-usage.log 统计每 skill 使用次数（记账 hook 产出）。

    调用名剥最末段归一（plugin:ponytail:ponytail→ponytail、superpowers:brainstorming
    →brainstorming）与 frontmatter name 对齐；个别对不上归零可接受。缺失/坏行静默跳过。
    """
    usage = Counter()
    log = Path.home() / ".claude" / "metrics" / "skill-usage.log"
    if not log.is_file():
        return usage
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            name = json.loads(line).get("skill", "").rsplit(":", 1)[-1].strip()
        except (ValueError, AttributeError):
            continue
        if name:
            usage[name] += 1
    return usage


def to_contract(rows: list) -> dict:
    """把 scan 结果转成 review_server 的 inventory 契约（references/audit-contract.md）。

    契约要求稳定 skillId + contentHash：skillId 从 name+dir+source 派生（跨轮次不变），
    contentHash = 原始 SKILL.md bytes 的 sha256（决定上轮决定能否复用）。
    没有遥测的字段标「不可用」，不用 0 假装（skill-trimmer 红线）。
    """
    def stable_id(row: dict) -> str:
        basis = f"{row['name']}|{row['dir']}|{row.get('source', '')}"
        return "skill-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]

    skills = []
    for row in rows:
        unresolved = row.get("unresolved", False)
        entry = SKILLS_DIR / row["dir"] / "SKILL.md" if not unresolved else None
        content_hash = ""
        if entry is not None:
            try:
                content_hash = hashlib.sha256(entry.read_bytes()).hexdigest()
            except OSError:
                content_hash = ""
        skills.append({
            "skillId": stable_id(row),
            "name": row["name"],
            "summary": row["description"] or "暂无能力摘要",
            "entryPath": str(entry) if entry else "",
            "contentHash": content_hash,
            "sourceGroup": ("msys symlink (unresolved)" if unresolved
                            else (row["source"] if row["source"] else "direct")),
            "sourceLabel": row["source"] if row["source"] else "直接安装",
            "sourceConfidence": "inferred" if unresolved else "verified",
            "category": "其他与待分类",
            "specificUse": "AI 辅助分类",
            "managementPolicy": "reviewable",
            "managementReason": "",
            "ownershipTags": ["用户安装"],
            "hosts": ["Claude Code"],
            "rareCritical": False,
            "suggestedDecision": "undecided",
            "currentStartupTokens": 0,
            "shellStartupTokens": 0,
            "postCallTokens": 0,
            "tokenMeasurement": "不可用",
            "usageMeasurement": str(row.get("usage_count", 0)),
            "lastUsedMeasurement": row.get("last_modified") or "从未",
            "triggerTerms": [],
            "appliedProjects": [],
            "hostOverrideState": "unknown",
            "entryHealth": "ok" if not unresolved else "broken-symlink",
            "globalTier": "unknown",
        })
    return {
        "schemaVersion": 1,
        "auditId": f"audit-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "environmentId": "claude-code-win",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "installedInstances": {"value": len(rows), "measurement": "精确值"},
            "exposedEntries": {"value": len(rows), "measurement": "精确值"},
            "contentVariants": {"value": len(rows), "measurement": "精确值"},
            "uniqueNames": {"value": len({r["name"].casefold() for r in rows}), "measurement": "精确值"},
        },
        "projects": [],
        "plugins": [],
        "mcps": [],
        "skills": skills,
    }


def main() -> int:
    rows = scan()
    usage = load_usage()
    today = datetime.now().date()
    for r in rows:
        r["usage_count"] = usage.get(r["name"], 0)
        stale = False
        try:
            lm = datetime.strptime(r.get("last_modified") or "0001-01-01", "%Y-%m-%d").date()
            stale = r["usage_count"] == 0 and (today - lm).days > STALE_DAYS
        except ValueError:
            pass
        r["staleCandidate"] = stale
    WORKSPACE.mkdir(exist_ok=True)
    out = WORKSPACE / "inventory.json"
    out.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    review_out = WORKSPACE / "inventory-review.json"
    review_out.write_text(
        json.dumps(to_contract(rows), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    direct = sum(1 for r in rows if not r["is_symlink"])
    links = len(rows) - direct
    with_assets = sum(1 for r in rows if r["has_assets"])
    print(f"total={len(rows)}  direct={direct}  symlink={links}  with_assets={with_assets}")
    print(f"-> {out}")
    print(f"-> {review_out}  (review_server contract)")
    stale = [r["dir"] for r in rows if r.get("staleCandidate")]
    if stale:
        print(f"stale candidates (0 使用 + >{STALE_DAYS} 天未改): {', '.join(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
