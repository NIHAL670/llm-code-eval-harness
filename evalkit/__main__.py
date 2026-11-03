"""Command-line entry point.

    python -m evalkit grade <task_dir> <candidate.py> [--json]
    python -m evalkit suite [--json]      # grade every sample response, print a calibration table
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .grader import REPO_ROOT, grade

MARK = {True: "PASS", False: "FAIL"}


def _print_report(report) -> None:
    print(f"\n{report.task} / {report.candidate}")
    print("-" * 72)
    for r in report.results:
        flag = "✔" if r.passed else "✘"
        crit = " (critical)" if r.critical else ""
        print(f"  {flag} {r.id:<32} {r.category:<12} w={r.weight:<4g}{crit}")
        if not r.passed:
            print(f"      → {r.detail}")
    print("-" * 72)
    print(f"  score {report.score:.0%}  ·  verdict {report.verdict}")
    print(f"  {report.justification()}")


def cmd_grade(args) -> int:
    report = grade(args.task, args.candidate)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_report(report)
    return 0 if report.verdict == "PASS" else 1


def cmd_suite(args) -> int:
    rows = []
    for task_dir in sorted((REPO_ROOT / "tasks").iterdir()):
        if not (task_dir / "checks.py").exists():
            continue
        candidates = [task_dir / "reference.py"] + sorted((REPO_ROOT / "responses" / task_dir.name).glob("*.py"))
        for cand in candidates:
            report = grade(task_dir, cand)
            rows.append(report)
            if not args.json:
                _print_report(report)

    if args.json:
        print(json.dumps([r.to_dict() for r in rows], indent=2))
        return 0

    print("\nCalibration summary")
    print("=" * 72)
    print(f"  {'task':<18}{'candidate':<30}{'score':>7}  verdict")
    for r in rows:
        print(f"  {r.task:<18}{r.candidate:<30}{r.score:>7.0%}  {r.verdict}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="evalkit", description="Deterministic rubric grader for LLM code responses")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grade", help="grade one candidate against one task")
    g.add_argument("task", type=Path)
    g.add_argument("candidate", type=Path)
    g.add_argument("--json", action="store_true")
    g.set_defaults(func=cmd_grade)

    s = sub.add_parser("suite", help="grade all sample responses")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_suite)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
