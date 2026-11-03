"""Rubric for the merge-intervals task. Each check maps to one requirement in task.md."""

import copy
import random

from evalkit.helpers import (
    assert_defines_function,
    assert_equal,
    assert_no_forbidden_imports,
    load_reference,
)
from evalkit.rubric import Check

PASS_THRESHOLD = 0.85
ref = load_reference(__file__)


# ---- interface -------------------------------------------------------------

def signature(src):
    assert_defines_function(src, "merge_intervals", 1)


def no_forbidden_imports(src):
    assert_no_forbidden_imports(src)


# ---- correctness -----------------------------------------------------------

def basic_overlap(m):
    assert_equal(m.merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]),
                 [[1, 6], [8, 10], [15, 18]], "basic example")


def unsorted_input(m):
    assert_equal(m.merge_intervals([[8, 10], [1, 3], [2, 6]]), [[1, 6], [8, 10]], "unsorted input")


def nested_intervals(m):
    assert_equal(m.merge_intervals([[1, 10], [2, 3], [4, 5]]), [[1, 10]], "nested intervals")


def randomized_vs_reference(m):
    rng = random.Random(1234)  # fixed seed → identical cases on every run
    for case in range(300):
        n = rng.randint(0, 25)
        ivs = []
        for _ in range(n):
            a = rng.randint(-50, 50)
            ivs.append([a, a + rng.randint(0, 15)])
        expected = ref.merge_intervals(copy.deepcopy(ivs))
        got = m.merge_intervals(copy.deepcopy(ivs))
        assert got == expected, f"random case #{case}: input {ivs} → expected {expected}, got {got}"


# ---- edge cases ------------------------------------------------------------

def empty_input(m):
    assert_equal(m.merge_intervals([]), [], "empty input")


def single_interval(m):
    assert_equal(m.merge_intervals([[4, 7]]), [[4, 7]], "single interval")


def touching_endpoints(m):
    assert_equal(m.merge_intervals([[1, 3], [3, 5]]), [[1, 5]], "touching intervals must merge (req. 2)")


def negative_and_point_intervals(m):
    assert_equal(m.merge_intervals([[-5, -1], [-1, -1], [0, 0]]), [[-5, -1], [0, 0]], "negatives / points")


# ---- robustness ------------------------------------------------------------

def does_not_mutate_input(m):
    data = [[5, 6], [1, 3], [2, 4]]
    snapshot = copy.deepcopy(data)
    m.merge_intervals(data)
    assert data == snapshot, f"input was modified (req. 3): now {data}, was {snapshot}"


def invalid_interval_raises(m):
    try:
        m.merge_intervals([[1, 2], [5, 3]])
    except ValueError:
        return
    raise AssertionError("start > end must raise ValueError (req. 5)")


def returns_list_of_lists(m):
    out = m.merge_intervals([[1, 2], [4, 5]])
    assert isinstance(out, list) and all(isinstance(iv, list) for iv in out), \
        f"must return list[list[int]], got {type(out).__name__} of {[type(iv).__name__ for iv in out]}"


# ---- performance -----------------------------------------------------------

def large_input_200k(m):
    rng = random.Random(99)
    ivs = []
    for _ in range(200_000):
        a = rng.randint(0, 10_000_000)
        ivs.append([a, a + rng.randint(0, 40)])
    out = m.merge_intervals(ivs)
    assert out == ref.merge_intervals(ivs), "wrong result on 200k-interval input"


CHECKS = [
    Check("signature", "interface", "Defines merge_intervals(intervals)", signature,
          weight=1, critical=True, static=True),
    Check("no_forbidden_imports", "interface", "No unnecessary system imports", no_forbidden_imports,
          weight=0.5, static=True),
    Check("basic_overlap", "correctness", "Canonical example", basic_overlap, weight=2, critical=True),
    Check("unsorted_input", "correctness", "Sorts by start before merging", unsorted_input, weight=1.5),
    Check("nested_intervals", "correctness", "Fully contained intervals", nested_intervals, weight=1),
    Check("randomized_vs_reference", "correctness", "300 seeded random cases vs reference", randomized_vs_reference,
          weight=3),
    Check("empty_input", "edge_case", "Empty list → []", empty_input, weight=0.5),
    Check("single_interval", "edge_case", "Single interval unchanged", single_interval, weight=0.5),
    Check("touching_endpoints", "edge_case", "[1,3] + [3,5] → [1,5]", touching_endpoints, weight=1.5),
    Check("negative_and_point_intervals", "edge_case", "Negative and zero-length intervals",
          negative_and_point_intervals, weight=0.5),
    Check("does_not_mutate_input", "robustness", "Caller's list is untouched", does_not_mutate_input, weight=1.5),
    Check("invalid_interval_raises", "robustness", "start > end raises ValueError", invalid_interval_raises,
          weight=1),
    Check("returns_list_of_lists", "robustness", "Output type is list[list[int]]", returns_list_of_lists,
          weight=0.5),
    Check("large_input_200k", "performance", "200k intervals within the time limit", large_input_200k,
          weight=2, critical=True, timeout_s=8),
]
