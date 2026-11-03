"""Deterministic grader: runs every rubric check for a task against a candidate solution."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .rubric import CheckResult, Report

REPO_ROOT = Path(__file__).resolve().parent.parent
SANDBOX = Path(__file__).resolve().parent / "sandbox.py"


def load_task(task_dir: Path):
    spec = importlib.util.spec_from_file_location(f"checks_{task_dir.name}", task_dir / "checks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_static(check, source: str) -> tuple[bool, str]:
    try:
        check.run(source)
        return True, "ok"
    except AssertionError as exc:
        return False, str(exc) or "assertion failed"
    except SyntaxError as exc:
        return False, f"candidate does not parse: {exc.msg} (line {exc.lineno})"


def _run_isolated(check, task_dir: Path, candidate: Path) -> tuple[bool, str, int]:
    cmd = [sys.executable, "-I", str(SANDBOX), str(REPO_ROOT), str(task_dir), str(candidate), check.id]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=check.timeout_s)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {check.timeout_s:g}s", int(check.timeout_s * 1000)
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith("{")]
    if proc.returncode != 0 or not lines:
        err = (proc.stderr.strip().splitlines() or ["no output"])[-1]
        return False, f"candidate crashed: {err}", 0
    out = json.loads(lines[-1])
    return out["passed"], out["detail"], out["duration_ms"]


def grade(task_dir: str | Path, candidate: str | Path) -> Report:
    task_dir, candidate = Path(task_dir).resolve(), Path(candidate).resolve()
    task = load_task(task_dir)
    source = candidate.read_text()
    report = Report(task=task_dir.name, candidate=candidate.name,
                    pass_threshold=getattr(task, "PASS_THRESHOLD", 0.85))

    for check in task.CHECKS:
        if check.static:
            passed, detail = _run_static(check, source)
            duration = 0
        else:
            passed, detail, duration = _run_isolated(check, task_dir, candidate)
        report.results.append(CheckResult(
            id=check.id, category=check.category, description=check.description,
            weight=check.weight, critical=check.critical, passed=passed,
            detail=detail, duration_ms=duration,
        ))
    return report
