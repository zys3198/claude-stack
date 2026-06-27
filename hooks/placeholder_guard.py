import sys, json, re

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PLACEHOLDER_PATTERNS = [
    (r"(?<![\w])TODO\b(?![_\w])", "TODO"), (r"(?<![\w])FIXME\b", "FIXME"),
    (r"(?<![\w])HACK\b", "HACK"), (r"(?<![\w])XXX\b", "XXX"),
    (r"\braise\s+NotImplementedError\b", "raise NotImplementedError"),
    (r"\bthrow\s+new\s+NotImplementedException\b", "throw NotImplementedException"),
    (r"//\s*\.\.\.", "// ... (注释省略)"), (r"#\s*\.\.\.(?!\.)", "# ... (注释省略)"),
    (r"/\*[\s\S]*?(?:omitted|rest follows|省略|其余同理|后续同|余略|此处省略)[\s\S]*?\*/", "/* 块注释省略 */"),
    (r"for\s+brevity", "for brevity"),
    (r"remaining\s+(?:follows?\s+same|code\s+(?:is\s+)?similar|sections?\s+similar)", "remaining follows same pattern"),
    (r"implement\s+this\s+(?:method|function|later)", "implement this later"),
    (r"<insert\s+here\s*>", "<insert here>"), (r"\.\.\.\s*\(?more\s+here\)?", "... (more here)"),
    (r"其余同理", "其余同理"), (r"后续同上", "后续同上"), (r"此处省略", "此处省略"),
    (r"余(?:略|下省略)", "余略"), (r"占位(?:符)?", "占位符"), (r"待(?:补充|实现|完善)", "待补充/实现"),
]
COMPILED = [(re.compile(p), name) for p, name in PLACEHOLDER_PATTERNS]
DOC_EXT = (".md", ".markdown", ".txt", ".rst", ".adoc", ".org")

def scan(text):
    hits = []
    for rx, name in COMPILED:
        m = rx.search(text)
        if m:
            line = text[:m.start()].count("\n") + 1
            hits.append((name, line, m.group(0)))
    return hits

try:
    _raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    _i = _raw.find("{")
    data = json.loads(_raw[_i:]) if _i >= 0 else {}
except Exception:
    sys.exit(0)

tool = data.get("tool_name", "")
ti = data.get("tool_input", {}) or {}
path = (ti.get("file_path") or ti.get("notebook_path") or "").lower()
if path.endswith(DOC_EXT):
    sys.exit(0)

chunks = []
if tool == "Write":
    c = ti.get("content", "")
    if c: chunks.append(c)
elif tool == "Edit":
    c = ti.get("new_string", "")
    if c: chunks.append(c)
elif tool == "MultiEdit":
    for e in ti.get("edits", []) or []:
        c = e.get("new_string", "")
        if c: chunks.append(c)
elif tool == "NotebookEdit":
    c = ti.get("new_source", "")
    if c: chunks.append(c)
elif tool == "apply_patch":
    c = ti.get("command", "")
    if c:
        for line in c.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                chunks.append(line[1:])

all_hits = []
for chunk in chunks:
    all_hits.extend(scan(chunk))
if not all_hits:
    sys.exit(0)

def deny(msg):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": msg}}, ensure_ascii=False))
    sys.exit(0)

shown = all_hits[:5]
lines = "\n".join(f"  - 行 {ln}: [{tag}] -> {repr(snip)[:60]}" for tag, ln, snip in shown)
msg = (f"placeholder_guard BLOCKED: 写入内容含占位符/残桩/省略词,违反 CLAUDE.md §10 完整性强制.\n  文件: {path or '(未指定)'}\n  命中 {len(all_hits)} 处:\n{lines}\n  -> 补全真实实现,删除 TODO/省略/for brevity 等.\n  -> 真正无法实现的部分,显式 raise NotImplementedError 并说明理由.")
deny(msg)