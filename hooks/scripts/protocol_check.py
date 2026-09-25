"""校验协议文档里能机械校验的几项：门禁、记忆、命名。

只读，不挂 hook，不阻断操作。退出码 0 表示全过，1 表示有错。
判据见 docs/protocols/gate.md、docs/protocols/memory.md，
命名一项见 docs/protocols-index.md 的「落点与命名」一节。
任务笔记与委派两份的「校验」列是 `—`：前者的产物是项目仓库里自由形态的
扫描稿，后者是 prompt 模板、磁盘上无待验产物，都不存在可判的固定形态。

源路径已删的项目，其记忆目录不再加载、也不会被召回，只计数不细查。
判定以 `~/.claude.json` 的 projects 映射为候选路径池：宿主只在目录被打开
过时登记，且不删条目，所以它是「曾有过的 cwd」的超集；未在其中、或路径
已不存在的，算已删。
"""

import glob
import json
import os
import re
import sys

CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
GATE = os.path.join(CLAUDE, "docs", "protocols", "gate.md")
SCOPE_PY = os.path.join(CLAUDE, "hooks", "scripts", "authorization_scope.py")
PROJECTS = os.path.join(CLAUDE, "projects")
CLAUDE_JSON = os.path.join(os.path.expanduser("~"), ".claude.json")

MEMORY_TYPES = {"user", "feedback", "project", "reference"}


def encode_cwd(path):
    """Claude Code 把 cwd 的 : \\ / . 四种字符一律换成 -。

    `~/.claude` -> `C--Users-zys31--claude`（点也变横线，所以是两个横线），
    这正是纯按分隔符替换会对不上的地方。
    """
    return re.sub(r"[:\\/.]", "-", path).lower()


def live_project_dirs():
    """源路径仍在的项目目录名（已小写），用于认出已删项目的记忆。"""
    if not os.path.isfile(CLAUDE_JSON):
        return set()
    with open(CLAUDE_JSON, encoding="utf-8") as f:
        known = json.load(f).get("projects", {})
    return {encode_cwd(p) for p in known if os.path.isdir(p)}


def check_gate():
    """gate.md 的固定字段表与 authorization_scope.py 的 allowed 集合比对。

    字段的唯一来源是脚本，gate.md 的表是它的投影；两边不等就是漂移。
    """
    for p in (GATE, SCOPE_PY):
        if not os.path.isfile(p):
            return [f"缺 {p}"], 0

    with open(GATE, encoding="utf-8") as f:
        gate = f.read()
    section = re.search(r"^## 固定字段\s*$(.*?)(?=^## )", gate, re.S | re.M)
    if not section:
        return ["gate.md 没找到「固定字段」一节"], 0
    doc_keys = re.findall(r"^\|\s*`(\w+)`\s*\|", section.group(1), re.M)

    with open(SCOPE_PY, encoding="utf-8") as f:
        src = f.read()
    allowed = re.search(r"allowed\s*=\s*\{([^}]*)\}", src)
    if not allowed:
        return ["authorization_scope.py 没找到 allowed 集合"], 0
    src_keys = re.findall(r'"(\w+)"', allowed.group(1))

    errors = []
    if not doc_keys:
        errors.append("gate.md 固定字段表没解析出任何键")
    if doc_keys and set(doc_keys) != set(src_keys):
        errors.append(
            f"字段表与脚本不一致：gate.md 多 {sorted(set(doc_keys) - set(src_keys))}、"
            f"少 {sorted(set(src_keys) - set(doc_keys))}"
        )
    return errors, len(doc_keys)


def frontmatter_problems(path):
    """一条记忆的 frontmatter 问题：围栏、name、description、metadata.type。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    name = os.path.basename(path)
    if not text.startswith("---"):
        return [f"{name} 缺 `---` 围栏开头"]
    block = re.match(r"---\s*\n(.*?)\n---\s*$", text, re.S | re.M)
    if not block:
        return [f"{name} 缺 `---` 围栏结尾"]

    body, errors = block.group(1), []
    for key in ("name", "description"):
        if not re.search(rf"^{key}:\s*\S", body, re.M):
            errors.append(f"{name} 缺 `{key}`")
    kind = re.search(r"^\s+type:\s*(\S+)", body, re.M)
    if not kind:
        errors.append(f"{name} 缺 `metadata.type`")
    elif kind.group(1) not in MEMORY_TYPES:
        errors.append(f"{name} 的 type「{kind.group(1)}」不在 {sorted(MEMORY_TYPES)} 内")
    return errors


def check_memory():
    """每个 projects/*/memory/：frontmatter 齐全，且 MEMORY.md 覆盖全部记忆文件。

    索引是召回的唯一入口，没进索引的记忆等于不存在。源路径已删的项目不进
    这列——那些记忆不会再被加载，挑它的 frontmatter 是白费力气，只计数。
    """
    dirs = sorted(glob.glob(os.path.join(PROJECTS, "*", "memory")))
    if not dirs:
        return ["没找到任何 projects/*/memory/"], 0, 0, 0, 0

    live = live_project_dirs()
    errors, total, indexed, gone_dirs, gone_files = [], 0, 0, 0, 0
    for d in dirs:
        files = [
            f for f in glob.glob(os.path.join(d, "*.md"))
            if os.path.basename(f) != "MEMORY.md"
        ]
        if os.path.basename(os.path.dirname(d)).lower() not in live:
            gone_dirs += 1
            gone_files += len(files)
            continue
        total += len(files)
        for f in files:
            errors += frontmatter_problems(f)

        index = os.path.join(d, "MEMORY.md")
        if not os.path.isfile(index):
            # 空目录不必有索引；有记忆却没索引才是问题
            if files:
                errors.append(f"{os.path.basename(os.path.dirname(d))} 有 {len(files)} 条记忆但没有 MEMORY.md")
            continue
        with open(index, encoding="utf-8") as f:
            links = {
                os.path.basename(x)
                for x in re.findall(r"\]\(([^)]*\.md)\)", f.read())
                if "/" not in x
            }
        orphans = sorted(os.path.basename(f) for f in files if os.path.basename(f) not in links)
        dead = sorted(x for x in links if not os.path.isfile(os.path.join(d, x)))
        project = os.path.basename(os.path.dirname(d))
        for o in orphans:
            errors.append(f"{project}「{o}」没进 MEMORY.md 索引")
        for x in dead:
            errors.append(f"{project} 索引指向不存在的「{x}」")
        indexed += len(files) - len(orphans)
    return errors, total, indexed, gone_dirs, gone_files


NAMING_ROOTS = ("docs", "installing")
DATE8 = re.compile(r"(?<!\d)(\d{8})(?!\d)")
DATE_OTHER = re.compile(r"(?<!\d)(\d{4})[-_](\d{2})[-_](\d{2})(?!\d)")


def name_problems(name):
    """名字里的问题：非 ASCII，或日期词不是 YYYY-MM-DD。"""
    problems = []
    if any(ord(c) > 127 for c in name):
        problems.append("含非 ASCII 字符")
    for m in DATE8.finditer(name):
        problems.append(f"日期「{m.group(1)}」不是 YYYY-MM-DD")
    for m in DATE_OTHER.finditer(name):
        if m.group(0) != "-".join(m.groups()):
            problems.append(f"日期「{m.group(0)}」不是 YYYY-MM-DD")
    return problems


def check_naming():
    """我们自己命名的目录与文件：名字 ASCII，日期词写成 YYYY-MM-DD。

    backups/ 只查顶层——里面装的是被备份内容的快照，名字不由我们定；
    由我们命名的只有那一个个备份目录本身。
    """
    targets = []
    for rel in NAMING_ROOTS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(CLAUDE, rel)):
            targets += [os.path.join(dirpath, n) for n in dirnames + filenames]
    backups = os.path.join(CLAUDE, "backups")
    if os.path.isdir(backups):
        targets += [os.path.join(backups, n) for n in os.listdir(backups)]

    errors = []
    for p in sorted(targets):
        for problem in name_problems(os.path.basename(p)):
            errors.append(f"{os.path.relpath(p, CLAUDE).replace(os.sep, '/')} {problem}")
    return errors, len(targets)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    gate_errors, key_count = check_gate()
    mem_errors, mem_total, mem_indexed, gone_dirs, gone_files = check_memory()
    name_errors, name_total = check_naming()

    print(
        f"{'门禁':<8} 字段表 {key_count} 键比对 authorization_scope.py"
        + (f"，{len(gate_errors)} 处不符" if gate_errors else "，全相符")
    )
    print(
        f"{'记忆':<8} {mem_total} 条记忆 · 已进索引 {mem_indexed}"
        + (f" · {len(mem_errors)} 处问题" if mem_errors else " · frontmatter 与索引全相符")
    )
    if gone_dirs:
        print(f"{'':<8} 另有已删项目的 {gone_dirs} 个目录 / {gone_files} 条"
              f"（合计 {mem_total + gone_files} 条），不再被加载，只计数")
    print(
        f"{'命名':<8} {name_total} 个名字（backups/ 顶层 · docs/ · installing/）"
        + (f"，{len(name_errors)} 处不符" if name_errors else "，全相符")
    )

    errors = gate_errors + mem_errors + name_errors
    if errors:
        print()
        for e in errors:
            print("  ✗", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
