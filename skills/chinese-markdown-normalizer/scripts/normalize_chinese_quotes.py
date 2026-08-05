#!/usr/bin/env python3
"""
Normalize quotes around Chinese text in Markdown-like files.

Examples:
  "内存友好" -> “内存友好”
  ”内存友好” -> “内存友好”
  '高可用'   -> ‘高可用’

The script avoids modifying fenced code blocks and inline code spans.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

DEFAULT_EXTENSIONS = {".md", ".markdown", ".mdx", ".txt"}

# Contains at least one CJK Unified Ideograph.
HAS_CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]")

# Match quoted segments on a single line.
# Double quotes: ASCII + Chinese curly quotes. We normalize to “...”.
# Single quotes: ASCII + Chinese curly single quotes. We normalize to ‘...’.
DOUBLE_QUOTED_RE = re.compile(r'(["“”])([^"\n“”]+)(["“”])')
SINGLE_QUOTED_RE = re.compile(r"(['‘’])([^'\n‘’]+)(['‘’])")
INLINE_CODE_RE = re.compile(r"(`+[^`]*`+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass
class FileResult:
    path: Path
    changed: bool
    replacements: int


def should_convert(content: str) -> bool:
    """Convert only quoted text that includes Chinese characters."""
    return bool(HAS_CJK_RE.search(content))


def replace_quotes_in_plain_text(text: str) -> Tuple[str, int]:
    count = 0

    def repl_double(match: re.Match[str]) -> str:
        nonlocal count
        inner = match.group(2)
        if should_convert(inner):
            normalized = f"“{inner}”"
            if normalized != match.group(0):
                count += 1
            return normalized
        return match.group(0)

    def repl_single(match: re.Match[str]) -> str:
        nonlocal count
        inner = match.group(2)
        if should_convert(inner):
            normalized = f"‘{inner}’"
            if normalized != match.group(0):
                count += 1
            return normalized
        return match.group(0)

    text = DOUBLE_QUOTED_RE.sub(repl_double, text)
    text = SINGLE_QUOTED_RE.sub(repl_single, text)
    return text, count


def replace_quotes_in_markdown_line(line: str) -> Tuple[str, int]:
    """Replace quotes in non-code parts of a markdown line."""
    parts = INLINE_CODE_RE.split(line)
    total = 0
    for i, part in enumerate(parts):
        # Odd indexes are inline code segments; keep unchanged.
        if i % 2 == 1:
            continue
        updated, n = replace_quotes_in_plain_text(part)
        parts[i] = updated
        total += n
    return "".join(parts), total


def normalize_text(text: str) -> Tuple[str, int]:
    lines = text.splitlines(keepends=True)
    in_fence = False
    total = 0
    output: List[str] = []

    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        updated, n = replace_quotes_in_markdown_line(line)
        output.append(updated)
        total += n

    return "".join(output), total


def iter_target_files(path: Path, exts: set[str]) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in exts:
            yield path
        return

    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() in exts:
            yield file


def process_file(file_path: Path, in_place: bool) -> FileResult:
    original = file_path.read_text(encoding="utf-8")
    normalized, replacements = normalize_text(original)
    changed = normalized != original

    if changed and in_place:
        file_path.write_text(normalized, encoding="utf-8")

    return FileResult(path=file_path, changed=changed, replacements=replacements)


def parse_exts(values: List[str] | None) -> set[str]:
    if not values:
        return set(DEFAULT_EXTENSIONS)
    normalized = set()
    for value in values:
        ext = value if value.startswith(".") else f".{value}"
        normalized.add(ext.lower())
    return normalized


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize quotes around Chinese text in files or directories "
            '(e.g. "中文"/”中文” -> “中文”).'
        )
    )
    parser.add_argument("target", help="File or directory path.")
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="File extension to include (repeatable). Example: --ext md --ext markdown",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write changes back to files. Without this flag, runs as preview only.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode. Equivalent to not using --in-place.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        parser.error(f"Target does not exist: {target}")

    exts = parse_exts(args.ext)
    in_place = args.in_place and not args.dry_run
    files = list(iter_target_files(target, exts))

    if not files:
        print("No matching files found.")
        return 0

    results = [process_file(path, in_place=in_place) for path in files]
    changed = [r for r in results if r.changed]
    total_replacements = sum(r.replacements for r in results)

    mode = "IN-PLACE" if in_place else "DRY-RUN"
    print(f"Mode: {mode}")
    print(f"Scanned files: {len(results)}")
    print(f"Changed files: {len(changed)}")
    print(f"Total quote replacements: {total_replacements}")

    for result in changed[:20]:
        print(f"- {result.path} ({result.replacements} replacements)")
    if len(changed) > 20:
        print(f"... and {len(changed) - 20} more files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
