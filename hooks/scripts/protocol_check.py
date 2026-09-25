"""校验资产里能机械校验的八类判据。

只读，自己不阻断操作——阻断与否由调用方按退出码决定：
0 全过；1 有命中（只报告）；2 用法错误（argparse 自用）；
3 有命中，且命中落在阻断区（常驻区与原则区，见 BLOCK_SCOPE）。
单独运行：`python hooks/scripts/protocol_check.py`；跑夹具树加 `--root`，
只跑某几类加 `--only size,secret`。

写入事件走 `--file <路径>`：只跑与该路径相关的那几类，且只报该路径自己的问题。
再加 `--content <临时文件>` 时，判据跑在这份文本上，也就是「这次写入之后的样子」，
而不是盘上的现状——按现状判的话，引入违规的那次写入反而放行，已经违规的文件
又永远改不动。「路径 → 判据」的对应只在 relevant_checks() 一处给出，hook 是传输层、不含判据。

| 判据 | 判什么 | 判据出处 |
|---|---|---|
| 门禁 | gate.md 的固定字段表 vs authorization_scope.py | docs/protocols/gate.md |
| 记忆 | frontmatter 必填键、索引孤儿与死链 | docs/protocols/memory.md |
| 命名 | ASCII、日期写成 YYYY-MM-DD | docs/protocols-index.md「落点与命名」|
| 体积 | 根入口体量上限 20 KB | docs/protocols-index.md「体量硬触发」|
| 重复 | 同一段落出现在两个根入口 | rules/principles.md B4 |
| 密钥 | 高置信度密钥形态 | rules/principles.md C2 |
| 生命周期 | 自报的 updated 是否过期 | rules/principles.md C4 |
| 映射表 | 「资产 → 形态 → L0」表与磁盘双向对账 | rules/principles.md B6 |

判不了的项在输出末尾显式列出，不静默略过——清单见 UNJUDGEABLE。

源路径已删的项目，其记忆目录不再加载、也不会被召回，只计数不细查。
判定以 `~/.claude.json` 的 projects 映射为候选路径池：宿主只在目录被打开
过时登记，且不删条目，所以它是「曾有过的 cwd」的超集；未在其中、或路径
已不存在的，算已删。夹具树没有这份文件，故一律按仍在处理。
"""

import argparse
import fnmatch
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date

DEFAULT_ROOT = os.path.join(os.path.expanduser("~"), ".claude")

# 由 set_root() 重算。CLAUDE 是本次被检查的根，默认 ~/.claude。
CLAUDE = DEFAULT_ROOT
GATE = SCOPE_PY = PROJECTS = ""
FIXTURE = False
# 由 set_target() 重算。被写的那一个文件（normcase 后的绝对路径）；None 表示全量。
TARGET = None
# 由 set_preview() 重算。这次写入之后该文件的内容（normcase 路径 → 文本）；空表示读盘的现状。
PREVIEW = {}

MEMORY_TYPES = {"user", "feedback", "project", "reference"}

# 根入口：一次进上下文就是一整份的那类文件。体积、段落重复、生命周期三判据查它。
# 不含 references/：那是按分支单独取用的文档，共用的样板（如设计库各篇的组件词表）
# 是那类产物的固有形态，不是冗余。
ENTRY_GLOBS = (
    "CLAUDE.md",
    "rules/*.md",
    "skills/*/SKILL.md",
    "docs/protocols/*.md",
    "docs/protocols-index.md",
    "installing/*.md",
    "projects/*/memory/*.md",
)

# 阻断区：这两处的写入有命中就拒（票 09），其余区仍然只报告。
# 覆盖全库每一轮都要付的常驻成本——常驻指令与原则。按路径模式判、不按存在与否，
# 所以新写一个 rules/*.md 也在内。范围只此一处，改这里就是改阻断面。
BLOCK_SCOPE = ("CLAUDE.md", "rules/*.md")

# 密钥扫描面更宽：配置、脚本、参考文件都算。不含会话记录、缓存、备份，
# 也不含 secrets/（那是本机指定的密钥存放处，且已被 .gitignore 排除）。
SECRET_TARGETS = (
    "CLAUDE.md", "README.md", "long-complex-task-prompt.md", "keybindings.json",
    "settings.json", "settings.local.json", "settings.json.bak*",
    "rules", "skills", "hooks", "docs", "installing", "authorization",
    "external-configs", "tools", "statusline", "lib", "commands",
)

# 体积上限 20 KB 沿用既有两处判据，不另立数字：
# docs/protocols-index.md「体量硬触发」、install-ledger 的 ledger_check.py MAX_BYTES。
SIZE_LIMIT = 20 * 1024
# 段落重复的字数下限。实测：阈值 120 在 187 个根入口上只留 1 组真命中；
# 降到更低会把「## 用法」这类小节标题算成重复。
PARA_MIN = 120
# updated 过期线。本机没有既有出处，属新定的默认值，要调就改这里。
STALE_DAYS = 180

DATE_MARK = re.compile(
    r"(?:^|\n)[ \t]*(?:更新|最后更新|日期|updated|last[_ ]updated)[ \t]*[:：=][ \t]*"
    r"(\d{4}-\d{2}-\d{2})",
    re.I,
)

# 具名前缀 + 私钥块：几乎不会误报的形态。
SECRET_PREFIX = {
    "Anthropic key": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "OpenAI 风格 key": r"\bsk-[A-Za-z0-9]{32,}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "Google key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "Slack token": r"\bxox[baprs]-[A-Za-z0-9\-]{10,}",
    "私钥块": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}
# 键名 = 长随机值的形态。实测：不加长度与占位符过滤时，
# archive-skills 的 HTML 里 `token = relationshipTokenGeometry` 一类会误报 15 处。
SECRET_ASSIGN = re.compile(
    r"(?i)\b(api[_-]?key|apikey|secret[_-]?key|client[_-]?secret|access[_-]?token"
    r"|auth[_-]?token|password|passwd)\b\s*[:=]\s*[\"']?([A-Za-z0-9/+_\-]{32,})[\"']?"
)
PLACEHOLDER = re.compile(
    r"(your|xxx|example|placeholder|redacted|dummy|sample|test|foo|bar"
    r"|<|\$\{|\{|\.\.\.|PROXY_MANAGED|CHANGE_?ME)",
    re.I,
)

# 映射表判据：键是表里的标签，值是它在磁盘上的对应物。表是这份表的投影，
# 两边不等就是漂移——与 check_gate() 用同一套「脚本是源头、文档是投影」的做法。
MAP_ROWS = {
    "rules/principles.md": "rules/principles.md",
    "CLAUDE.md": "CLAUDE.md",
    "rules/*.md": "rules/*.md",
    "skill": "skills/*/SKILL.md",
    "docs/protocols/*.md": "docs/protocols/*.md",
    "memory": "projects/*/memory/*.md",
    "notes": None,          # 落在各项目仓库里，~/.claude 下没有对应物
    "hook": "hooks/scripts/*.py",
}

# 在仓库里、但不属映射表那八类运行时读物的顶层条目。每条写清是什么：
# 新出现一个既不在表内、也不在此列的顶层条目，就该被问一句「它归哪一类」。
EXEMPT = {
    ".gitignore": "仓库元文件",
    "README.md": "仓库说明",
    "keybindings.json": "平台按键配置",
    "long-complex-task-prompt.md": "一次性产出的长 prompt",
    "archive-skills": "归档（历史记录）",
    "skill-slim-audit-2026-09-21": "审计证据（记录）",
    "authorization": "授权登记（记录）",
    "installing": "台账（记录）",
    "external-configs": "外部工具配置副本（配置）",
    "tools": "自建工具（程序）",
    "statusline": "statusline 程序",
    "task-notes-reminder": "提醒程序的状态目录",
}

# 判不了的项。写在输出里，免得把「没有检查」当成「检查通过」。
UNJUDGEABLE = (
    "A1 协议 > 文字（同一内容写成散文还是字段表，都能过检查）",
    "A2 判据是否足够",
    "A4 命名好坏（ASCII 与日期格式之外的部分）",
    "C1 字段够不够",
    "指针措辞是否够强（判法是跑文档，不是静态检查）",
)

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".pytest_cache", ".ruff_cache"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".7z",
              ".exe", ".dll", ".so", ".woff", ".woff2", ".ttf", ".sqlite", ".db", ".mp4"}


def set_root(root):
    global CLAUDE, GATE, SCOPE_PY, PROJECTS, FIXTURE
    CLAUDE = os.path.abspath(root)
    GATE = os.path.join(CLAUDE, "docs", "protocols", "gate.md")
    SCOPE_PY = os.path.join(CLAUDE, "hooks", "scripts", "authorization_scope.py")
    PROJECTS = os.path.join(CLAUDE, "projects")
    FIXTURE = CLAUDE != os.path.abspath(DEFAULT_ROOT)


def set_target(path):
    """收窄到刚被写的那一个文件。全量模式下 TARGET 为 None。

    存路径原样的大小写：TARGET 会被并进根入口清单、也用来打印。存 normcase 后的小写
    形态会让同一次写入在清单里出现两次（`CLAUDE.md` 与 `claude.md`）。比较时两边都规范化。
    """
    global TARGET
    TARGET = os.path.normpath(os.path.abspath(path))


def in_target(path):
    """这个路径是不是本次被写的那一个。全量模式一律为真。"""
    if TARGET is None:
        return True
    return os.path.normcase(os.path.normpath(path)) == os.path.normcase(TARGET)


def set_preview(path, text):
    PREVIEW[os.path.normcase(os.path.normpath(os.path.abspath(path)))] = text


def preview_of(path):
    return PREVIEW.get(os.path.normcase(os.path.normpath(path)))


# 以下四个是票 09 的「阻断区」判据。方向是收紧：给 `CLAUDE.md` 与 `rules/*.md`
# 两处写入加要求，不改任何放行条件，不减任何既有判据，管辖范围不出这两个路径。
def in_any(path, patterns):
    """路径落不落在这份清单里。按模式判，不按存在与否——还没落盘的新文件也要算。

    目录项（`rules`）按前缀算，其余走 fnmatch。清单里带通配的项可能跨过 `/`
    （`rules/*.md` 也认 `rules/a/b.md`），这对「整块区域」的语义是对的。
    """
    rel_path = rel(path)
    for pat in patterns:
        pat = pat.rstrip("/")
        if fnmatch.fnmatch(rel_path, pat) or rel_path.startswith(pat + "/"):
            return True
    return False


def in_block_scope(path):
    """这次写入是不是落在阻断区（常驻区与原则区）。"""
    return in_any(path, BLOCK_SCOPE)


def entry_files():
    """根入口清单。收窄模式下被写的那一个即使还没落盘也算——新写的也是入口。"""
    files = set(expand(ENTRY_GLOBS))
    if TARGET is not None and in_any(TARGET, ENTRY_GLOBS):
        files.add(os.path.normpath(TARGET))
    return sorted(files)


def size_of(path):
    """文件体量。有预览时按预览算，否则读盘——非 UTF-8 内容一律按替换后的字节数。"""
    text = preview_of(path)
    if text is None:
        return os.path.getsize(path)
    return len(text.encode("utf-8"))


def relevant_checks(path):
    """写这个路径该跑哪几类判据。

    这张对应表是唯一出处：hook 只管把路径转达过来，自己不带任何判据。
    理由分别是——门禁判据的两个文件互校；记忆判据管 projects/*/memory/；
    命名判据管我们命名的目录名；体积/重复/生命周期只对根入口有意义；
    密钥扫描面更宽；映射表管仓库顶层条目的归类。
    体积、密钥两条按模式判（in_any），所以刚建、还没落盘的文件也算根入口。
    """
    rel_path = rel(path)
    labels = set()
    if path in (os.path.normpath(GATE), os.path.normpath(SCOPE_PY)):
        labels.add("门禁")
    if rel_path.startswith("projects/") and "/memory/" in rel_path:
        labels.add("记忆")
    if (rel_path.startswith(("docs/", "installing/"))
            or (rel_path.startswith("backups/") and rel_path.count("/") == 1)):
        labels.add("命名")
    if in_any(path, ENTRY_GLOBS):
        labels |= {"体积", "重复", "生命周期"}
    if in_any(path, SECRET_TARGETS):
        labels.add("密钥")
    if rel_path.split("/")[0] in repo_top_entries():
        labels.add("映射表")
    return labels


def rel(path):
    return os.path.relpath(path, CLAUDE).replace(os.sep, "/")


def read(path, limit=None):
    """读文本。本机存在非 UTF-8 文件名与内容，一律替换而不是抛错。

    有 --content 预览时读预览：判据要判「写完之后的样子」。
    """
    text = preview_of(path)
    if text is not None:
        return text if limit is None else text[:limit]
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read() if limit is None else f.read(limit)
    except OSError:
        return ""


def expand(patterns):
    """把 glob 清单展开成文件清单。元素可以是文件、目录或通配。

    一律 normpath：os.path.join 不归一化模式里的 `/`，而 glob 会把模式里那段
    原样留下，于是同一次展开里既有 `a\b` 也有 `a/b`，按前缀比对就会漏。
    """
    out = set()
    for pat in patterns:
        p = os.path.join(CLAUDE, pat)
        if os.path.isfile(p):
            out.add(os.path.normpath(p))
            continue
        for hit in glob.glob(p) + glob.glob(os.path.join(p, "**", "*"), recursive=True):
            if os.path.isfile(hit):
                out.add(os.path.normpath(hit))
    return sorted(out)


def paragraphs(path):
    """正文里的段落（空行分段）去掉空白后的样子。"""
    for block in re.split(r"\n\s*\n", read(path)):
        norm = re.sub(r"\s+", " ", block).strip()
        if norm:
            yield norm


def live_project_dirs():
    """源路径仍在的项目目录名（已小写）。夹具树没有 .claude.json，一律按仍在处理。"""
    claude_json = os.path.join(os.path.expanduser("~"), ".claude.json")
    if FIXTURE or not os.path.isfile(claude_json):
        return None
    try:
        with open(claude_json, encoding="utf-8") as f:
            known = json.load(f).get("projects", {})
    except (OSError, ValueError):
        return None
    return {encode_cwd(p) for p in known if os.path.isdir(p)}


def encode_cwd(path):
    """Claude Code 把 cwd 的 : \\ / . 四种字符一律换成 -。

    `~/.claude` -> `C--Users-zys31--claude`（点也变横线，所以是两个横线），
    这正是纯按分隔符替换会对不上的地方。
    """
    return re.sub(r"[:\\/.]", "-", path).lower()


def check_gate():
    """gate.md 的固定字段表与 authorization_scope.py 的 allowed 集合比对。

    字段的唯一来源是脚本，gate.md 的表是它的投影；两边不等就是漂移。
    """
    for p in (GATE, SCOPE_PY):
        if not os.path.isfile(p):
            return [f"缺 {rel(p)}"], "字段表缺失"

    section = re.search(r"^## 固定字段\s*$(.*?)(?=^## )", read(GATE), re.S | re.M)
    if not section:
        return ["gate.md 没找到「固定字段」一节"], "字段表缺失"
    doc_keys = re.findall(r"^\|\s*`(\w+)`\s*\|", section.group(1), re.M)

    allowed = re.search(r"allowed\s*=\s*\{([^}]*)\}", read(SCOPE_PY))
    if not allowed:
        return ["authorization_scope.py 没找到 allowed 集合"], "allowed 缺失"
    src_keys = re.findall(r'"(\w+)"', allowed.group(1))

    errors = []
    if not doc_keys:
        errors.append("gate.md 固定字段表没解析出任何键")
    if doc_keys and set(doc_keys) != set(src_keys):
        errors.append(
            f"字段表与脚本不一致：gate.md 多 {sorted(set(doc_keys) - set(src_keys))}、"
            f"少 {sorted(set(src_keys) - set(doc_keys))}"
        )
    summary = f"字段表 {len(doc_keys)} 键比对 authorization_scope.py" + (
        f"，{len(errors)} 处不符" if errors else "，全相符")
    return errors, summary


def frontmatter_problems(path):
    """一条记忆的 frontmatter 问题：围栏、name、description、metadata.type。"""
    text = read(path)
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
        return ["没找到任何 projects/*/memory/"], "没有记忆目录"

    live = live_project_dirs()
    errors, total, indexed, gone_dirs, gone_files = [], 0, 0, 0, 0
    for d in dirs:
        if (TARGET is not None
                and os.path.normcase(os.path.normpath(os.path.dirname(TARGET)))
                != os.path.normcase(os.path.normpath(d))):
            continue
        files = [
            f for f in glob.glob(os.path.join(d, "*.md"))
            if os.path.basename(f) != "MEMORY.md"
        ]
        if live is not None and os.path.basename(os.path.dirname(d)).lower() not in live:
            gone_dirs += 1
            gone_files += len(files)
            continue
        total += len(files)
        for f in files:
            if in_target(f):
                errors += frontmatter_problems(f)

        index = os.path.join(d, "MEMORY.md")
        if not os.path.isfile(index):
            # 空目录不必有索引；有记忆却没索引才是问题
            if files:
                errors.append(f"{os.path.basename(os.path.dirname(d))} 有 {len(files)} 条记忆但没有 MEMORY.md")
            continue
        links = {
            os.path.basename(x)
            for x in re.findall(r"\]\(([^)]*\.md)\)", read(index))
            if "/" not in x
        }
        orphans = sorted(os.path.basename(f) for f in files if os.path.basename(f) not in links)
        dead = sorted(x for x in links if not os.path.isfile(os.path.join(d, x)))
        project = os.path.basename(os.path.dirname(d))
        # 收窄时只报与这份有关的：它自己的登记，或（写的是索引时）整份索引的问题。
        writing_index = TARGET is not None and in_target(index)
        for o in orphans:
            if TARGET is None or writing_index or in_target(os.path.join(d, o)):
                errors.append(f"{project}「{o}」没进 MEMORY.md 索引")
        if TARGET is None or writing_index:
            for x in dead:
                errors.append(f"{project} 索引指向不存在的「{x}」")
        indexed += len(files) - len(orphans)
    summary = f"{total} 条记忆 · 已进索引 {indexed}" + (
        f" · {len(errors)} 处问题" if errors else " · frontmatter 与索引全相符")
    if gone_dirs:
        summary += f" · 另有已删项目的 {gone_dirs} 个目录 / {gone_files} 条只计数"
    return errors, summary


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
    for r in NAMING_ROOTS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(CLAUDE, r)):
            targets += [os.path.join(dirpath, n) for n in dirnames + filenames]
    backups = os.path.join(CLAUDE, "backups")
    if os.path.isdir(backups):
        targets += [os.path.join(backups, n) for n in os.listdir(backups)]

    errors = []
    for p in sorted(targets):
        if not in_target(p):
            continue
        for problem in name_problems(os.path.basename(p)):
            errors.append(f"{rel(p)} {problem}")
    summary = f"{len(targets)} 个名字（backups/ 顶层 · docs/ · installing/）" + (
        f"，{len(errors)} 处不符" if errors else "，全相符")
    return errors, summary


def check_size():
    """根入口的体量上限。整份文件一次进上下文，超限就是每轮都付这个代价。"""
    files = entry_files()
    errors = []
    for p in files:
        if not in_target(p):
            continue
        size = size_of(p)
        if size > SIZE_LIMIT:
            errors.append(f"{rel(p)} 体量 {size / 1024:.1f} KB，超过 {SIZE_LIMIT // 1024} KB 上限")
    summary = f"{len(files)} 个根入口（上限 {SIZE_LIMIT // 1024} KB）" + (
        f"，{len(errors)} 处超限" if errors else "，全在限内")
    return errors, summary


def check_dupe():
    """同一段落出现在两个根入口文件里——B4「一知识一源，其余指针」。

    只查根入口，不查 references/：判据是「这段知识该不该有两个源」，
    而参考文件本就按分支单独取用，几篇共享同一段样板不构成第二个源。
    """
    files, owners, blocks = entry_files(), {}, 0
    for p in files:
        for norm in paragraphs(p):
            if len(norm) < PARA_MIN:
                continue
            blocks += 1
            key = hashlib.sha256(norm.encode("utf-8")).hexdigest()
            owners.setdefault(key, []).append((rel(p), norm))
    errors = []
    for group in owners.values():
        where = sorted({r for r, _ in group})
        if len(where) < 2:
            continue
        # 收窄时要比对全量段落才能发现重复，但只报涉及被写文件的那几组。
        if TARGET is not None and not any(in_target(os.path.join(CLAUDE, r)) for r in where):
            continue
        errors.append(f"同一段落出现在 {len(where)} 个文件：{'、'.join(where)}｜{group[0][1][:60]}…")
    summary = f"{len(files)} 个根入口 · {blocks} 个段落（≥{PARA_MIN} 字）" + (
        f"，{len(errors)} 组重复" if errors else "，无重复")
    return errors, summary


def mask(value):
    return value[:12] + "…" if len(value) > 12 else value


def looks_like_key(value):
    """长随机值而不是占位符：要同时有数字和字母，且不含占位词。"""
    if PLACEHOLDER.search(value):
        return False
    return bool(re.search(r"\d", value)) and bool(re.search(r"[A-Za-z]", value))


def check_secret():
    """密钥不入库（C2）。只报高置信度形态，宁可漏也不误报。

    未知服务商的裸密钥判不了——那需要熵与上下文，静态检查只会造出一堆误报，
    所以只认具名前缀、私钥块，以及「键名 = 32 位以上且不像占位符」三种。
    """
    errors, files = [], expand(SECRET_TARGETS)
    for p in files:
        if not in_target(p):
            continue
        if os.path.splitext(p)[1].lower() in BINARY_EXT or size_of(p) > 2_000_000:
            continue
        text = read(p)
        for label, pattern in SECRET_PREFIX.items():
            for m in re.finditer(pattern, text):
                errors.append(f"{rel(p)} 命中{label}：{mask(m.group(0))}")
        for m in SECRET_ASSIGN.finditer(text):
            if looks_like_key(m.group(2)):
                errors.append(f"{rel(p)} 命中「{m.group(1)} = 长随机值」：{mask(m.group(2))}")
    summary = f"{len(files)} 个文件 · {len(SECRET_PREFIX) + 1} 类模式" + (
        f"，{len(errors)} 处命中" if errors else "，无命中")
    return errors, summary


def check_lifecycle():
    """C4：声明了 updated 的根入口是否过期；没声明的只计数。

    只认文件自报的日期字段，不拿 mtime 或 git 提交时间冒充 updated——那两个
    会被克隆、检出、格式化改写，判出来的「过期」不是作者的意图。
    """
    files, declared, errors = entry_files(), 0, []
    for p in files:
        if not in_target(p):
            continue
        m = DATE_MARK.search(read(p, limit=2000))
        if not m:
            continue
        declared += 1
        age = (date.today() - date.fromisoformat(m.group(1))).days
        if age > STALE_DAYS:
            errors.append(f"{rel(p)} 声明更新于 {m.group(1)}，已过期 {age} 天（上限 {STALE_DAYS} 天）")
    undeclared = len(files) - declared
    summary = (f"{len(files)} 个根入口 · {declared} 个声明了日期"
               + (f"，{len(errors)} 处过期" if errors else "，无过期")
               + f"｜另 {undeclared} 个未声明日期（无 owner/updated 字段，判不了）")
    return errors, summary


def table_labels():
    """principles.md「资产 → 形态 → L0」一节的标签列，去格式后的样子。"""
    text = read(os.path.join(CLAUDE, "rules", "principles.md"))
    section = re.search(r"^## 资产 → 形态 → L0\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not section:
        return None
    labels = []
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|", section.group(1), re.M):
        if row in ("资产", "---"):
            continue
        lab = re.sub(r"（.*?）", "", row.replace("`", "").replace("~/.claude/", ""))
        labels.append(lab.strip().rstrip("/"))
    return labels


def repo_top_entries():
    """仓库内的顶层条目：已跟踪 + 未跟踪但未被忽略。

    用 git 界定「资产」，平台数据与备份因被忽略而天然出局，不必另维护排除名单。
    夹具树不是仓库（且上层可能是仓库，git 会查到别处去），退回列顶层条目——
    那正是夹具要验的路径。
    """
    if not FIXTURE:
        try:
            done = subprocess.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=CLAUDE, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=60)
            if done.returncode == 0:
                return sorted({ln.split("/")[0] for ln in done.stdout.splitlines() if ln.strip()})
        except (OSError, subprocess.SubprocessError):
            pass
    return sorted(n for n in os.listdir(CLAUDE) if n not in (".git",))


def check_map():
    """B6：映射表与磁盘双向对账。

    表侧——表里每行都要能在磁盘上找到对应物；盘侧——仓库内每个顶层条目
    要么落在表内、要么在 EXEMPT 里写明是什么。新东西必须被归类，这正是这条判据的用处。
    """
    labels = table_labels()
    if labels is None:
        return ["rules/principles.md 没找到「资产 → 形态 → L0」一节"], "映射表缺失"

    # 表侧的问题（表与判据漂移、某一行在磁盘上找不到对应物）是整张表的事：全量跑都报，
    # 收窄时只有写 principles.md 本身才报。窄跑要回答的是「刚写的这个归哪一类」。
    whole_table = TARGET is None or in_target(os.path.join(CLAUDE, "rules", "principles.md"))

    errors = []
    if whole_table and set(labels) != set(MAP_ROWS):
        errors.append(
            f"映射表与判据漂移：表里多 {sorted(set(labels) - set(MAP_ROWS))}、"
            f"少 {sorted(set(MAP_ROWS) - set(labels))}"
        )
    row_paths = set()
    for label, pattern in MAP_ROWS.items():
        if not pattern:
            continue
        found = expand([pattern])
        if whole_table and not found:
            errors.append(f"映射表「{label}」一行在磁盘上找不到对应物（{pattern}）")
        row_paths |= set(found)

    covered = exempt = 0
    unclassified = []
    for name in repo_top_entries():
        if name in EXEMPT:
            exempt += 1
        elif any(p == os.path.join(CLAUDE, name) or p.startswith(os.path.join(CLAUDE, name) + os.sep)
                 for p in row_paths):
            covered += 1
        else:
            unclassified.append(name)
    for name in unclassified:
        # 收窄时只问被写文件所在的那一个顶层条目归哪一类。
        if TARGET is not None and name != rel(TARGET).split("/")[0]:
            continue
        errors.append(f"顶层条目「{name}」既不在映射表内，也没有豁免理由——它归哪一类加载形态？")
    summary = (f"{len(labels)} 行 · 仓库顶层 {covered + exempt + len(unclassified)} 项："
               f"归表 {covered}、豁免 {exempt}" + (f"、未归类 {len(unclassified)}" if unclassified else "，全归类"))
    return errors, summary


CHECKS = (
    ("门禁", check_gate),
    ("记忆", check_memory),
    ("命名", check_naming),
    ("体积", check_size),
    ("重复", check_dupe),
    ("密钥", check_secret),
    ("生命周期", check_lifecycle),
    ("映射表", check_map),
)
ONLY_KEYS = {
    "gate": "门禁", "memory": "记忆", "naming": "命名", "size": "体积",
    "dupe": "重复", "secret": "密钥", "lifecycle": "生命周期", "map": "映射表",
}


def main():
    parser = argparse.ArgumentParser(description="机械校验全局资产")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="被检查的根目录，默认 ~/.claude")
    parser.add_argument("--only", default="", help="只跑这几类，逗号分隔："
                        + ",".join(ONLY_KEYS))
    parser.add_argument("--file", default="", help="只查刚被写的这一个文件（写入事件用）")
    parser.add_argument("--content", default="", help="把 --file 当成具有这份文本（临时文件路径）")
    args = parser.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    unknown = only - set(ONLY_KEYS)
    if unknown:
        parser.error(f"未知判据 {sorted(unknown)}，可选 {sorted(ONLY_KEYS)}")
    # None = 全跑；集合 = 只跑这几类（可能是空集，那表示一类都不跑）
    selected = {ONLY_KEYS[k] for k in only} if only else None

    set_root(args.root)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    narrow, in_block = "", False
    if args.file:
        path = os.path.abspath(args.file)
        if not os.path.normcase(path).startswith(os.path.normcase(CLAUDE + os.sep)):
            parser.error(f"{args.file} 不在被检查的根 {CLAUDE} 内")
        if args.content:
            # newline="" 保住换行原样，体量判据才按真实字节数算。
            try:
                with open(args.content, encoding="utf-8", errors="replace", newline="") as f:
                    set_preview(path, f.read())
            except OSError as exc:
                parser.error(f"读不到 --content 的 {args.content}：{exc}")
        set_target(path)
        narrow = rel(path)
        in_block = in_block_scope(path)
        relevant = relevant_checks(path)
        selected = relevant if selected is None else (selected & relevant)

    all_errors, ran = [], []
    for label, fn in CHECKS:
        # selected 为 None 是全跑；空集是「该路径一类都不属」，两者不能混。
        if selected is not None and label not in selected:
            continue
        errors, summary = fn()
        all_errors += errors
        ran.append(label)
        if not narrow:
            print(f"{label:<8} {summary}")

    if narrow:
        # 收窄模式下不印摘要：数字来自全量的判据（重复、映射表）和只查一个文件的
        # 判据混在一起，摆出来反而误导。写清楚查了哪几类就够。
        print(f"被写 {narrow} · 判据 {'、'.join(ran) if ran else '（无，该路径不属任何一类）'}")

    print(f"{'判不了':<8} " + " · ".join(UNJUDGEABLE))
    if all_errors:
        print()
        for e in all_errors:
            print("  ✗", e)
        # 命中落在阻断区（常驻区与原则区）时给 3，调用方据此拒掉这次写入；
        # 其余各区的命中仍旧只报告——阻断范围只有 BLOCK_SCOPE 一处。
        if in_block:
            return 3
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
