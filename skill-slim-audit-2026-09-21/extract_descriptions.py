"""只读提取：把 10 个 model-invoked skill 的 name+description 各导出一份，供第一跳命中对照。"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

NAMES = [
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

NEW_ROOT = Path("C:/Users/zys31/.claude/skills")
OLD_ROOT = Path("C:/Users/zys31/.claude/jobs/ec1c1363/tmp/backup-before-slim")
OUT = Path("C:/Users/zys31/.claude/jobs/ec1c1363/tmp/hit-test")


def desc_of(path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    out, grab = [], False
    for ln in lines[1:end]:
        if ln.startswith("description:"):
            grab = True
            out.append(ln[len("description:"):].strip())
        elif grab and (ln.startswith(" ") or ln.startswith("\t")):
            out.append(ln.strip())
        elif grab:
            break
    joined = " ".join(out)
    for mark in (">-", ">", "|"):
        if joined.startswith(mark):
            joined = joined[len(mark):]
    return " ".join(joined.split())


OUT.mkdir(parents=True, exist_ok=True)

for label, root in (("old", OLD_ROOT), ("new", NEW_ROOT)):
    blocks = []
    for n in NAMES:
        blocks.append(f"### {n}\n{desc_of(root / n / 'SKILL.md')}")
    (OUT / f"descriptions-{label}.md").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(f"descriptions-{label}.md 已写出，{len(blocks)} 条")
