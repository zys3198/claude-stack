"""只读测量：对比改造前后全部 21 个自建 SKILL.md 的 description 与正文规模。"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

MODEL_INVOKED = [
    "dev-status-by-user",
    "dev-clean-by-user",
    "bidirectional-steelman-by-user",
    "toolchain-pitfalls-by-user",
    "parallel-delegation-by-user",
    "docker-only-by-user",
    "install-ledger-by-user",
    "task-notes-by-user",
    "article-writer-by-user",
    "coding-workflow-by-user",
]

USER_INVOKED = [
    "skill-trimmer-by-user",
    "skill-auditor-by-user",
    "instruction-engineering-by-user",
    "content-to-note-by-user",
    "improver-skill-by-user",
    "drawio-chart-by-user",
    "drawio-article-illustration-by-user",
    "company-discovery-evaluation-by-user",
    "cc-switch-setting-sync-by-user",
    "ai-product-development-by-user",
    "awesome-design-md-by-user",
]

NEW_ROOT = Path("C:/Users/zys31/.claude/skills")
OLD_ROOT = Path(sys.argv[1])


def parse(path):
    """返回 (description 有效字符数, 正文行数)。"""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    fm, body = lines[1:end], lines[end + 1:]

    desc_lines, grab = [], False
    for ln in fm:
        if ln.startswith("description:"):
            grab = True
            desc_lines.append(ln[len("description:"):])
        elif grab and (ln.startswith(" ") or ln.startswith("\t")):
            desc_lines.append(ln)
        elif grab:
            grab = False
    desc = " ".join(desc_lines)
    desc_eff = "".join(ch for ch in desc if not ch.isspace())
    for mark in (">-", ">", "|"):
        desc_eff = desc_eff.replace(mark, "")
    return len(desc_eff), len([b for b in body if b.strip()])


def section(title, names):
    print(f"\n=== {title} ===")
    print(f"{'skill':<38}{'desc旧':>7}{'desc新':>7}{'Δ':>7}   {'行旧':>6}{'行新':>6}{'Δ':>7}")
    tot = [0] * 6
    for s in names:
        old = parse(OLD_ROOT / s / "SKILL.md")
        new = parse(NEW_ROOT / s / "SKILL.md")
        dd, dl = new[0] - old[0], new[1] - old[1]
        print(f"{s:<38}{old[0]:>7}{new[0]:>7}{dd:>+7}   {old[1]:>6}{new[1]:>6}{dl:>+7}")
        tot[0] += old[0]; tot[1] += new[0]; tot[2] += dd
        tot[3] += old[1]; tot[4] += new[1]; tot[5] += dl
    print("-" * 82)
    print(f"{'小计':<38}{tot[0]:>7}{tot[1]:>7}{tot[2]:>+7}   {tot[3]:>6}{tot[4]:>6}{tot[5]:>+7}")
    return tot


a = section("model-invoked（12 个中自建 10 个，description 常驻）", MODEL_INVOKED)
b = section("user-invoked（11 个，description 不常驻）", USER_INVOKED)
print("-" * 82)
print(f"{'总计':<38}{a[0]+b[0]:>7}{a[1]+b[1]:>7}{a[2]+b[2]:>+7}   "
      f"{a[3]+b[3]:>6}{a[4]+b[4]:>6}{a[5]+b[5]:>+7}")
