"""evalkit — a small, deterministic rubric grader for LLM-generated code."""

from .grader import grade
from .rubric import Check, CheckResult, Report

__all__ = ["grade", "Check", "CheckResult", "Report"]
