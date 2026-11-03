"""Tests for the grader itself: it must reach the expected verdict for every sample, for the
right reasons, and give identical results on repeated runs."""

from pathlib import Path

import pytest

from evalkit import grade

ROOT = Path(__file__).resolve().parent.parent

# (task, candidate, expected verdict, exact set of checks that must fail)
EXPECTED = [
    ("merge_intervals", "tasks/merge_intervals/reference.py", "PASS", set()),
    ("merge_intervals", "responses/merge_intervals/a_correct.py", "PASS", set()),
    ("merge_intervals", "responses/merge_intervals/b_touching_bug.py", "FAIL",
     # [-5,-1] and [-1,-1] also only touch, so the negatives check catches the same bug
     {"touching_endpoints", "negative_and_point_intervals", "randomized_vs_reference", "large_input_200k"}),
    ("merge_intervals", "responses/merge_intervals/c_quadratic_mutates.py", "FAIL",
     {"does_not_mutate_input", "large_input_200k"}),
    ("lru_cache", "tasks/lru_cache/reference.py", "PASS", set()),
    ("lru_cache", "responses/lru_cache/a_correct.py", "PASS", set()),
    ("lru_cache", "responses/lru_cache/b_get_no_refresh.py", "FAIL",
     {"basic_sequence", "get_refreshes_recency", "randomized_vs_reference"}),
    ("lru_cache", "responses/lru_cache/c_list_scan.py", "FAIL", {"ops_200k_large_capacity"}),
]


@pytest.mark.parametrize("task,candidate,verdict,failing", EXPECTED, ids=lambda x: str(x).split("/")[-1])
def test_expected_verdict_and_failure_reasons(task, candidate, verdict, failing):
    report = grade(ROOT / "tasks" / task, ROOT / candidate)
    failed = {r.id for r in report.results if not r.passed}
    assert report.verdict == verdict, report.justification()
    assert failed == failing, f"unexpected failing checks: {sorted(failed)}"


def test_reference_solutions_score_100():
    for task_dir in (ROOT / "tasks").iterdir():
        if (task_dir / "checks.py").exists():
            report = grade(task_dir, task_dir / "reference.py")
            assert report.score == 1.0, f"{task_dir.name}: reference fails {report.justification()}"


def test_grading_is_deterministic():
    task = ROOT / "tasks" / "lru_cache"
    cand = ROOT / "responses" / "lru_cache" / "b_get_no_refresh.py"
    a, b = grade(task, cand), grade(task, cand)
    assert [(r.id, r.passed, r.detail) for r in a.results] == [(r.id, r.passed, r.detail) for r in b.results]
    assert a.score == b.score and a.verdict == b.verdict


def test_crashing_candidate_fails_cleanly(tmp_path):
    bad = tmp_path / "crash.py"
    bad.write_text("def merge_intervals(intervals):\n    raise RuntimeError('boom')\n")
    report = grade(ROOT / "tasks" / "merge_intervals", bad)
    assert report.verdict == "FAIL"
    assert all(not r.passed for r in report.results if not r.id.startswith(("signature", "no_forbidden")))


def test_unparseable_candidate_fails_interface(tmp_path):
    bad = tmp_path / "syntax.py"
    bad.write_text("def merge_intervals(intervals)\n    return []\n")
    report = grade(ROOT / "tasks" / "merge_intervals", bad)
    sig = next(r for r in report.results if r.id == "signature")
    assert not sig.passed and "does not parse" in sig.detail
    assert report.verdict == "FAIL"
