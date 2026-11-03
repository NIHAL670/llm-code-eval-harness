"""Rubric primitives: a check, its weight, and how results roll up into a score."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

Category = Literal["interface", "correctness", "edge_case", "robustness", "performance"]


@dataclass(frozen=True)
class Check:
    """One gradeable criterion.

    `run` receives the candidate module and must raise AssertionError (with a
    human-readable message) when the criterion is not met. Static checks get the
    candidate's source code instead, via `static=True`.
    """

    id: str
    category: Category
    description: str
    run: Callable
    weight: float = 1.0
    critical: bool = False
    static: bool = False
    timeout_s: float = 5.0


@dataclass
class CheckResult:
    id: str
    category: str
    description: str
    weight: float
    critical: bool
    passed: bool
    detail: str = ""
    duration_ms: int = 0


@dataclass
class Report:
    task: str
    candidate: str
    results: list[CheckResult] = field(default_factory=list)
    pass_threshold: float = 0.85

    @property
    def score(self) -> float:
        total = sum(r.weight for r in self.results)
        earned = sum(r.weight for r in self.results if r.passed)
        return round(earned / total, 4) if total else 0.0

    @property
    def critical_failures(self) -> list[CheckResult]:
        return [r for r in self.results if r.critical and not r.passed]

    @property
    def verdict(self) -> str:
        if self.critical_failures:
            return "FAIL"
        return "PASS" if self.score >= self.pass_threshold else "FAIL"

    def by_category(self) -> dict[str, tuple[int, int]]:
        out: dict[str, tuple[int, int]] = {}
        for r in self.results:
            passed, total = out.get(r.category, (0, 0))
            out[r.category] = (passed + int(r.passed), total + 1)
        return out

    def justification(self) -> str:
        """A short, evidence-based pass/fail justification, the way a reviewer would write it."""
        failed = [r for r in self.results if not r.passed]
        if not failed:
            return f"{self.verdict}: all {len(self.results)} checks passed."
        lead = "critical check failed" if self.critical_failures else f"score {self.score:.0%} vs threshold {self.pass_threshold:.0%}"
        if self.verdict == "PASS":
            lead = f"score {self.score:.0%} clears threshold {self.pass_threshold:.0%} despite minor failures"
        reasons = "; ".join(f"[{r.id}] {r.detail}" for r in failed[:3])
        more = f" (+{len(failed) - 3} more)" if len(failed) > 3 else ""
        return f"{self.verdict} — {lead}. Failed: {reasons}{more}"

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "candidate": self.candidate,
            "verdict": self.verdict,
            "score": self.score,
            "pass_threshold": self.pass_threshold,
            "justification": self.justification(),
            "by_category": {k: {"passed": p, "total": t} for k, (p, t) in self.by_category().items()},
            "checks": [r.__dict__ for r in self.results],
        }
