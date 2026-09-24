from __future__ import annotations

import copy
import json
import sys
import tempfile
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wikiskill import WikiSkillError, command_gate, command_propose, evaluate_report, write_json, workspace


def block(status: str, *, score: float | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "status": status,
        "observed": f"observed {status}",
        "evidence": [f"run:{status}"],
    }
    if score is not None:
        result["score"] = score
    return result


def report(*, candidate_score: float = 0.7, status: str = "passed") -> dict[str, object]:
    result = {
        "schema_version": 1,
        "baseline": block("passed", score=0.5),
        "candidate": block(status, score=candidate_score),
        "target": block("passed"),
        "guardrail": block("passed"),
        "holdout": block("passed"),
        "comparison": {
            "same_cases": True,
            "same_model": True,
            "same_runs": True,
            "same_timeout": True,
            "same_grader": True,
        },
    }
    return result


def expect_error(action) -> None:
    try:
        action()
    except WikiSkillError:
        return
    raise AssertionError("expected WikiSkillError")


def main() -> None:
    verdict, passed = evaluate_report(report())
    assert passed
    assert verdict["status"] == "passed"

    missing_evidence = copy.deepcopy(report())
    del missing_evidence["candidate"]["evidence"]
    expect_error(lambda: evaluate_report(missing_evidence))

    blocked = report(status="blocked")
    verdict, passed = evaluate_report(blocked)
    assert not passed
    assert verdict["status"] == "blocked"

    not_run = report(status="not-run")
    verdict, passed = evaluate_report(not_run)
    assert not passed
    assert verdict["status"] == "not-run"

    not_improved = report(candidate_score=0.5)
    verdict, passed = evaluate_report(not_improved)
    assert not passed
    assert verdict["status"] == "failed"

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        result = workspace(root)
        active = result["active"] / "demo"
        active.mkdir(parents=True)
        (active / "SKILL.md").write_text("baseline\n", encoding="utf-8")
        (active / "PURPOSE.md").write_text("baseline purpose\n", encoding="utf-8")

        seed = root / "candidate.md"
        seed.write_text("candidate\n", encoding="utf-8")
        command_propose(
            Namespace(
                root=str(root),
                skill_id="demo",
                version="v1",
                skill_file=str(seed),
                purpose="candidate purpose",
                purpose_file=None,
                pattern_id=["pattern-1"],
            )
        )
        report_path = root / "report.json"
        write_json(report_path, report())
        active_before = (active / "SKILL.md").read_text(encoding="utf-8")
        output = command_gate(
            Namespace(root=str(root), candidate="demo/v1", report=str(report_path), apply=False)
        )
        assert output["status"] == "passed"
        assert not output["applied"]
        assert (active / "SKILL.md").read_text(encoding="utf-8") == active_before

        blocked_path = root / "blocked.json"
        write_json(blocked_path, report(status="blocked"))
        output = command_gate(
            Namespace(root=str(root), candidate="demo/v1", report=str(blocked_path), apply=True)
        )
        assert output["status"] == "blocked"
        assert not output["applied"]
        assert (active / "SKILL.md").read_text(encoding="utf-8") == active_before

        output = command_gate(
            Namespace(root=str(root), candidate="demo/v1", report=str(report_path), apply=True)
        )
        assert output["status"] == "passed"
        assert output["applied"]
        assert (active / "SKILL.md").read_text(encoding="utf-8") == "candidate\n"

    print("test_wikiskill: passed")


if __name__ == "__main__":
    main()
