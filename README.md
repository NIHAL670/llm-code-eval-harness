# llm-code-eval-harness

**A small, deterministic rubric grader for LLM-generated code.**

![CI](https://github.com/NIHAL670/llm-code-eval-harness/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/runtime_deps-none-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

This repository shows how I approach evaluating model-written code: a precise task spec, a reference solution, and an automated rubric where **every check maps to one requirement** — so a score explains *why* a response passed or failed, and the same response always gets the same grade.

> The tasks and sample responses here are original and were written for this demo. They are not taken from any client project or dataset.

---

## Example

```text
$ python -m evalkit grade tasks/lru_cache responses/lru_cache/b_get_no_refresh.py

lru_cache / b_get_no_refresh.py
------------------------------------------------------------------------
  ✔ interface                        interface    w=1    (critical)
  ✔ no_forbidden_imports             interface    w=0.5
  ✘ basic_sequence                   correctness  w=2    (critical)
      → key 2 should be evicted: expected -1, got 2
  ✔ eviction_order                   correctness  w=1.5
  ✘ get_refreshes_recency            correctness  w=2
      → get() must mark key as recently used; key 1 was wrongly evicted: expected 1, got -1
  ✔ update_refreshes_and_overwrites  correctness  w=1.5
  ✘ randomized_vs_reference          correctness  w=3
      → case #0 (capacity 4) step 32: get(7) expected 761, got -1
  ✔ capacity_one                     edge_case    w=0.5
  ✔ missing_key                      edge_case    w=0.5
  ✔ invalid_capacity_raises          robustness   w=1
  ✔ ops_200k_large_capacity          performance  w=2    (critical)
------------------------------------------------------------------------
  score 55%  ·  verdict FAIL
  FAIL — critical check failed. Failed: [basic_sequence] key 2 should be evicted: ...
```

The justification line is generated from the evidence, the way a human reviewer would write a pass/fail note.

## Calibration: does the rubric separate good answers from bad ones?

Each task ships with a reference solution and three sample responses written to represent common model failure modes. `python -m evalkit suite` grades them all:

| Task | Response | What it gets wrong | Score | Verdict |
|---|---|---|---|---|
| merge_intervals | `reference.py` | — | 100% | PASS |
| merge_intervals | `a_correct.py` | — | 100% | PASS |
| merge_intervals | `b_touching_bug.py` | `<` instead of `<=`: touching intervals not merged | 59% | FAIL |
| merge_intervals | `c_quadratic_mutates.py` | sorts caller's list in place; O(n²) rescans | 79% | FAIL |
| lru_cache | `reference.py` | — | 100% | PASS |
| lru_cache | `a_correct.py` | — | 100% | PASS |
| lru_cache | `b_get_no_refresh.py` | `get()` doesn't refresh recency | 55% | FAIL |
| lru_cache | `c_list_scan.py` | correct behaviour, but O(n) per operation | 87% | FAIL |

`c_list_scan.py` is the interesting case: it clears the 85% score threshold, but still fails because the prompt makes O(1) an explicit requirement, so the performance check is **critical**. A pure weighted average would have passed an answer that violates the spec.

## Design principles

| Principle | How it's implemented |
|---|---|
| **One check, one requirement** | Every check in `tasks/*/checks.py` cites the requirement it tests, so failures are actionable. |
| **Deterministic** | Randomized checks use fixed seeds; performance limits have a wide margin (correct solutions finish in ~0.6 s against an 8 s limit), so timing noise can't flip a verdict. A test asserts identical results across runs. |
| **Isolated** | Each runtime check executes in a fresh `python -I` subprocess with a timeout. A crash, infinite loop or leaked global state fails only that check. |
| **Targeted + broad** | Hand-written checks catch known failure modes; a seeded randomized comparison against the reference catches the rest. |
| **Critical vs weighted** | Hard requirements (interface, canonical behaviour, stated complexity) are critical; everything else contributes a weighted score. |
| **Spec defects ≠ model errors** | Each `task.md` has a *Spec decisions* table that pins down ambiguities (e.g. "do touching intervals merge?") so a correct answer can't fail on an unstated assumption. |
| **The grader is tested too** | `tests/` asserts the expected verdict **and the exact set of failing checks** for every sample, plus crash and syntax-error handling. |

## Repository layout

```
evalkit/
  rubric.py      # Check, CheckResult, Report (scoring, verdict, justification)
  grader.py      # runs static checks in-process, runtime checks in a sandboxed subprocess
  sandbox.py     # executes one check against one candidate, prints JSON
  helpers.py     # AST interface checks, forbidden-import check, reference loader
tasks/
  merge_intervals/   task.md · reference.py · checks.py
  lru_cache/         task.md · reference.py · checks.py
responses/           sample model responses per task
tests/               tests for the grader itself
```

## Usage

```bash
git clone https://github.com/NIHAL670/llm-code-eval-harness.git
cd llm-code-eval-harness

python -m evalkit suite                                   # grade every sample + calibration table
python -m evalkit grade tasks/merge_intervals path/to/answer.py
python -m evalkit grade tasks/merge_intervals path/to/answer.py --json   # machine-readable report

pip install pytest && python -m pytest -q                 # test the grader
```

No runtime dependencies beyond the Python standard library.

## Adding a task

1. Write `tasks/<name>/task.md` — the exact prompt plus a *Spec decisions* table.
2. Write `reference.py` and make sure it passes every check.
3. Write `checks.py`: a `CHECKS` list of `Check(id, category, description, fn, weight, critical, static, timeout_s)`.
4. Add sample responses that each fail for one known reason, and record the expected failing checks in `tests/test_grader.py`.

## Author

**Nihal Yadav** — AI Trainer (LLM evaluation & software engineering) · M.Tech AI & ML, IIT Delhi
[GitHub](https://github.com/NIHAL670) · [LinkedIn](https://linkedin.com/in/nihal-yadav-5131582b8)
