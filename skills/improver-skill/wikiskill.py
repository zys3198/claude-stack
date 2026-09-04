from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----", re.DOTALL),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:sk-|ghp_|gho_|github_pat_|xox[baprs]-|AIza|ya29\.)[A-Za-z0-9._-]{8,}"),
]
SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class WikiSkillError(Exception):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe(value: str, label: str) -> str:
    if not isinstance(value, str) or not SAFE_COMPONENT.fullmatch(value):
        raise WikiSkillError(f"invalid {label}: {value!r}")
    return value


def redact(value: Any) -> tuple[Any, int]:
    if isinstance(value, str):
        result = value
        count = 0
        for pattern in SECRET_PATTERNS:
            result, replacements = pattern.subn("[REDACTED]", result)
            count += replacements
        return result, count
    if isinstance(value, list):
        result = []
        count = 0
        for item in value:
            clean, item_count = redact(item)
            result.append(clean)
            count += item_count
        return result, count
    if isinstance(value, dict):
        result = {}
        count = 0
        for key, item in value.items():
            clean_key, key_count = redact(str(key))
            clean, item_count = redact(item)
            result[clean_key] = clean
            count += key_count + item_count
        return result, count
    return value, 0


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WikiSkillError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WikiSkillError(f"invalid JSON in {path}: {exc.msg}") from exc


def read_json_input(value: str) -> Any:
    if value != "-":
        return read_json(Path(value))
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise WikiSkillError(f"invalid JSON from stdin: {exc.msg}") from exc


def read_text_input(value: str) -> str:
    return sys.stdin.read() if value == "-" else Path(value).read_text(encoding="utf-8")


def write_text(path: Path, text: str, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        try:
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        except FileExistsError as exc:
            raise WikiSkillError(f"immutable file already exists: {path}") from exc
        return
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def write_json(path: Path, value: Any, *, exclusive: bool = False) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n", exclusive=exclusive)


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def paths(root: Path) -> dict[str, Path]:
    return {
        "raw": root / "raw" / "traces",
        "patterns": root / "wiki" / "patterns",
        "logs": root / "wiki" / "logs.md",
        "impact": root / "wiki" / "skill-impact.md",
        "active": root / "skills" / "active",
        "candidates": root / "skills" / "candidates",
    }


def workspace(root: Path) -> dict[str, Path]:
    result = paths(root)
    for key in ("raw", "patterns", "active", "candidates"):
        result[key].mkdir(parents=True, exist_ok=True)
    if not result["logs"].exists():
        write_text(result["logs"], "# WikiSkill evolution log\n\n", exclusive=True)
    if not result["impact"].exists():
        write_text(result["impact"], "# Skill impact log\n\n", exclusive=True)
    return result


def trace_file(result: dict[str, Path], trace_id: str) -> Path:
    return result["raw"] / f"{safe(trace_id, 'trace id')}.json"


def candidate_parts(value: str) -> tuple[str, str]:
    parts = value.split("/")
    if len(parts) != 2:
        raise WikiSkillError("candidate must be SKILL_ID/VERSION")
    return safe(parts[0], "skill id"), safe(parts[1], "version")


def active_dir(result: dict[str, Path], skill_id: str) -> Path:
    return result["active"] / safe(skill_id, "skill id")


def candidate_dir(result: dict[str, Path], candidate: str) -> Path:
    skill_id, version = candidate_parts(candidate)
    return result["candidates"] / skill_id / version


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    result = workspace(root)
    output: dict[str, Any] = {"root": str(root), "layers": ["raw", "wiki", "skills"]}
    if not args.skill_id:
        return output
    skill_id = safe(args.skill_id, "skill id")
    if not args.skill_file:
        raise WikiSkillError("--skill-file is required with --skill-id")
    skill = Path(args.skill_file).read_text(encoding="utf-8")
    purpose = args.purpose or "Seed Skill; evolve through WikiSkill gating."
    clean_skill, skill_redactions = redact(skill)
    clean_purpose, purpose_redactions = redact(purpose)
    if not clean_skill.strip():
        raise WikiSkillError("seed Skill is empty")
    if skill_redactions or purpose_redactions:
        raise WikiSkillError("seed Skill or PURPOSE contains secret-like values; refusing to write")
    target = active_dir(result, skill_id)
    if (target / "SKILL.md").exists():
        raise WikiSkillError(f"active Skill already exists: {skill_id}")
    write_text(target / "SKILL.md", clean_skill, exclusive=True)
    write_text(target / "PURPOSE.md", clean_purpose.rstrip() + "\n", exclusive=True)
    write_json(
        target / "metadata.json",
        {"skill_id": skill_id, "source": "seed", "created_at": now(), "skill_hash": digest(clean_skill)},
        exclusive=True,
    )
    output["active_skill"] = skill_id
    return output


def command_record(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    result = workspace(root)
    payload = read_json_input(args.input)
    clean_payload, redactions = redact(payload)
    requested_id = args.trace_id or (clean_payload.get("trace_id") if isinstance(clean_payload, dict) else None)
    trace_id = requested_id or digest(json.dumps(clean_payload, ensure_ascii=False, sort_keys=True))[:16]
    envelope = {
        "trace_id": safe(trace_id, "trace id"),
        "recorded_at": now(),
        "source": args.source,
        "redactions": redactions,
        "payload": clean_payload,
    }
    path = trace_file(result, trace_id)
    write_json(path, envelope, exclusive=True)
    return {"trace_id": trace_id, "path": str(path), "redactions": redactions}


def pattern_text(pattern: dict[str, str], trace_ids: list[str]) -> str:
    lines = [
        f"# {pattern['title']}",
        "",
        f"- id: `{pattern['id']}`",
        f"- kind: `{pattern['kind']}`",
        f"- updated: `{now()}`",
        "",
        "## Summary",
        pattern["summary"],
        "",
        "## Root cause",
        pattern["root_cause"],
        "",
        "## Recommendation",
        pattern["recommendation"],
        "",
        "## Evidence",
    ]
    lines.extend(f"- [Raw trace](../../raw/traces/{trace_id}.json)" for trace_id in trace_ids)
    return "\n".join(lines) + "\n"


def command_maintain(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    result = workspace(root)
    analysis = read_json_input(args.analysis)
    if isinstance(analysis, dict) and isinstance(analysis.get("patterns"), list):
        items = analysis["patterns"]
    else:
        items = [analysis]
    fallback = [safe(item, "trace id") for item in (args.trace_id or [])]
    pattern_ids: list[str] = []
    all_traces: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            raise WikiSkillError("Maintainer input must be a pattern object or contain patterns list")
        pattern_id = safe(str(item.get("id", "")), "pattern id")
        raw_trace_ids = item.get("trace_ids", [])
        if not isinstance(raw_trace_ids, list):
            raise WikiSkillError(f"pattern {pattern_id} trace_ids must be a list")
        trace_ids = list(dict.fromkeys(fallback + [safe(str(value), "trace id") for value in raw_trace_ids]))
        if not trace_ids:
            raise WikiSkillError(f"pattern {pattern_id} has no trace_ids")
        for trace_id in trace_ids:
            if not trace_file(result, trace_id).exists():
                raise WikiSkillError(f"pattern {pattern_id} references missing trace: {trace_id}")
        pattern = {
            "id": pattern_id,
            "kind": str(item.get("kind", "mixed")),
            "title": str(item.get("title", pattern_id)),
            "summary": str(item.get("summary", "")),
            "root_cause": str(item.get("root_cause", "")),
            "recommendation": str(item.get("recommendation", "")),
        }
        if not all(pattern[key].strip() for key in ("title", "summary", "root_cause", "recommendation")):
            raise WikiSkillError(f"pattern {pattern_id} has empty required text")
        clean_pattern, redactions = redact(pattern)
        if redactions:
            raise WikiSkillError(f"pattern {pattern_id} contains secret-like values; refusing to write")
        target = result["patterns"] / f"{pattern_id}.md"
        text = pattern_text(clean_pattern, trace_ids)
        if target.exists():
            append_text(target, f"\n---\n\n## Maintainer update {now()}\n\n{text}")
        else:
            write_text(target, text, exclusive=True)
        pattern_ids.append(pattern_id)
        all_traces.extend(trace_ids)
    append_text(
        result["logs"],
        f"## {now()}\n\n- Maintainer patterns: {', '.join(f'`{item}`' for item in pattern_ids)}\n- Traces: {', '.join(f'`{item}`' for item in dict.fromkeys(all_traces))}\n\n",
    )
    return {"patterns": pattern_ids, "log": str(result["logs"])}


def command_propose(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    result = workspace(root)
    skill_id = safe(args.skill_id, "skill id")
    version = safe(args.version, "version")
    pattern_ids = [safe(item, "pattern id") for item in args.pattern_id]
    if args.skill_file == "-" and args.purpose_file == "-":
        raise WikiSkillError("--skill-file and --purpose-file cannot both read stdin")
    skill = read_text_input(args.skill_file)
    purpose = read_text_input(args.purpose_file) if args.purpose_file else args.purpose
    clean_skill, skill_redactions = redact(skill)
    clean_purpose, purpose_redactions = redact(purpose)
    if not clean_skill.strip() or not clean_purpose.strip():
        raise WikiSkillError("Skill and PURPOSE must be non-empty")
    if skill_redactions or purpose_redactions:
        raise WikiSkillError("candidate contains secret-like values; refusing to write")
    target = result["candidates"] / skill_id / version
    if target.exists():
        raise WikiSkillError(f"candidate already exists: {skill_id}/{version}")
    active = active_dir(result, skill_id) / "SKILL.md"
    target.mkdir(parents=True)
    write_text(target / "SKILL.md", clean_skill, exclusive=True)
    write_text(target / "PURPOSE.md", clean_purpose.rstrip() + "\n", exclusive=True)
    metadata = {
        "candidate": f"{skill_id}/{version}",
        "skill_id": skill_id,
        "version": version,
        "pattern_ids": pattern_ids,
        "created_at": now(),
        "status": "pending",
        "base_skill_hash": digest(active.read_text(encoding="utf-8")) if active.exists() else None,
        "skill_hash": digest(clean_skill),
        "gates": [],
    }
    write_json(target / "candidate.json", metadata, exclusive=True)
    return {"candidate": metadata["candidate"], "path": str(target), "status": "pending"}


def score(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise WikiSkillError(f"{label} must be a finite number")
    return float(value)


def flag(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise WikiSkillError(f"{label} must be boolean")
    return value


def evaluate_report(report: Any) -> tuple[dict[str, Any], bool]:
    if not isinstance(report, dict):
        raise WikiSkillError("gate report must be a JSON object")
    baseline = score(report.get("baseline"), "baseline")
    candidate = score(report.get("candidate"), "candidate")
    checks = {
        "score_improved": candidate > baseline,
        "target": flag(report.get("target"), "target"),
        "guardrail": flag(report.get("guardrail"), "guardrail"),
        "holdout": flag(report.get("holdout"), "holdout"),
    }
    return {"baseline": baseline, "candidate": candidate, "checks": checks}, all(checks.values())


def command_gate(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    result = workspace(root)
    candidate = candidate_dir(result, args.candidate)
    if not candidate.is_dir():
        raise WikiSkillError(f"candidate not found: {args.candidate}")
    metadata = read_json(candidate / "candidate.json")
    skill_id, version = candidate_parts(args.candidate)
    if metadata.get("skill_id") != skill_id or metadata.get("version") != version:
        raise WikiSkillError("candidate metadata does not match candidate path")
    verdict, passed = evaluate_report(read_json_input(args.report))
    active_file = active_dir(result, skill_id) / "SKILL.md"
    purpose_file = candidate / "PURPOSE.md"
    candidate_file = candidate / "SKILL.md"
    before = active_file.read_text(encoding="utf-8") if active_file.exists() else ""
    after = candidate_file.read_text(encoding="utf-8")
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"active/{skill_id}/SKILL.md",
            tofile=f"candidate/{args.candidate}/SKILL.md",
        )
    )
    diff, _ = redact(diff)
    current_base_hash = digest(before) if active_file.exists() else None
    checks = verdict["checks"]
    checks["content"] = bool(after.strip() and purpose_file.read_text(encoding="utf-8").strip())
    checks["base_match"] = metadata.get("base_skill_hash") == current_base_hash
    verdict["passed"] = bool(passed and all(checks.values()))
    applied = False
    timestamp = now()
    if verdict["passed"] and args.apply:
        target = active_dir(result, skill_id)
        target.mkdir(parents=True, exist_ok=True)
        write_text(target / "SKILL.md", after)
        write_text(target / "PURPOSE.md", purpose_file.read_text(encoding="utf-8"))
        write_json(
            target / "metadata.json",
            {"skill_id": skill_id, "source_candidate": args.candidate, "applied_at": timestamp, "skill_hash": digest(after)},
        )
        applied = True
    entry = {"at": timestamp, "verdict": "accept" if verdict["passed"] else "reject", "applied": applied, **verdict}
    metadata.setdefault("gates", []).append(entry)
    metadata["status"] = "accepted" if applied else ("passed" if verdict["passed"] else "rejected")
    write_json(candidate / "candidate.json", metadata)
    reasons = [name for name, passed_check in checks.items() if not passed_check]
    append_text(
        result["impact"],
        "\n".join(
            [
                f"## {timestamp}",
                "",
                f"- Candidate: `{args.candidate}`",
                f"- Verdict: `{entry['verdict']}`",
                f"- Applied: `{str(applied).lower()}`",
                f"- Reason: {'all gates passed' if not reasons else 'failed: ' + ', '.join(reasons)}",
                "- Gate result:",
                "```json",
                json.dumps(entry, ensure_ascii=False, indent=2),
                "```",
                "- Skill diff:",
                "```diff",
                diff.rstrip(),
                "```",
                "",
            ]
        ),
    )
    return {"candidate": args.candidate, "verdict": entry["verdict"], "applied": applied, "checks": checks}


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Lightweight local WikiSkill")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create Raw/Wiki/Skills workspace")
    init.add_argument("root")
    init.add_argument("--skill-id")
    init.add_argument("--skill-file")
    init.add_argument("--purpose")
    init.set_defaults(handler=command_init)

    record = commands.add_parser("record", help="write one immutable redacted Raw Trace")
    record.add_argument("root")
    record.add_argument("--input", default="-", help="JSON file, or - for stdin")
    record.add_argument("--trace-id")
    record.add_argument("--source", default="manual")
    record.set_defaults(handler=command_record)

    maintain = commands.add_parser("maintain", help="append one Maintainer pattern batch")
    maintain.add_argument("root")
    maintain.add_argument("--analysis", required=True, help="one pattern object or JSON with patterns list; - for stdin")
    maintain.add_argument("--trace-id", action="append", help="fallback trace id")
    maintain.set_defaults(handler=command_maintain)

    propose = commands.add_parser("propose", help="store isolated candidate Skill")
    propose.add_argument("root")
    propose.add_argument("--skill-id", required=True)
    propose.add_argument("--version", required=True)
    propose.add_argument("--skill-file", required=True, help="Skill file, or - for stdin")
    purpose = propose.add_mutually_exclusive_group(required=True)
    purpose.add_argument("--purpose")
    purpose.add_argument("--purpose-file")
    propose.add_argument("--pattern-id", action="append", required=True)
    propose.set_defaults(handler=command_propose)

    gate = commands.add_parser("gate", help="apply lightweight manual gate")
    gate.add_argument("root")
    gate.add_argument("--candidate", required=True, help="SKILL_ID/VERSION")
    gate.add_argument("--report", required=True, help="JSON: baseline, candidate, target, guardrail, holdout; - for stdin")
    gate.add_argument("--apply", action="store_true", help="apply only when every gate passes")
    gate.set_defaults(handler=command_gate)
    return root


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = args.handler(args)
    except (OSError, WikiSkillError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
