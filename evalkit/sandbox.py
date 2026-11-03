"""Runs ONE check against ONE candidate in a fresh interpreter, then prints a JSON result.

Invoked by the grader as:  python -I evalkit/sandbox.py <repo_root> <task_dir> <candidate.py> <check_id>

Running every check in its own process means a crash, infinite loop or global-state
leak in the candidate can only ever fail that single check, which keeps grading
reproducible.
"""

import importlib.util
import json
import sys
import time
import traceback


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    repo_root, task_dir, candidate_path, check_id = sys.argv[1:5]
    sys.path.insert(0, repo_root)
    sys.setrecursionlimit(10_000)

    checks = _load(f"{task_dir}/checks.py", "task_checks")
    check = next(c for c in checks.CHECKS if c.id == check_id)

    start = time.perf_counter()
    try:
        candidate = _load(candidate_path, "candidate")
        check.run(candidate)
        passed, detail = True, "ok"
    except AssertionError as exc:
        passed, detail = False, str(exc) or "assertion failed"
    except Exception as exc:  # candidate raised something unexpected
        tb = traceback.extract_tb(exc.__traceback__)
        where = f" (line {tb[-1].lineno})" if tb else ""
        passed, detail = False, f"raised {type(exc).__name__}: {exc}{where}"
    duration_ms = int((time.perf_counter() - start) * 1000)

    print(json.dumps({"passed": passed, "detail": detail, "duration_ms": duration_ms}))


if __name__ == "__main__":
    main()
