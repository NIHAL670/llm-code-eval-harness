"""Rubric for the LRU-cache task. Each check maps to one requirement in task.md."""

import random

from evalkit.helpers import (
    assert_defines_class,
    assert_equal,
    assert_no_forbidden_imports,
    load_reference,
)
from evalkit.rubric import Check

PASS_THRESHOLD = 0.85
ref = load_reference(__file__)


# ---- interface -------------------------------------------------------------

def interface(src):
    assert_defines_class(src, "LRUCache", ["__init__", "get", "put"])


def no_forbidden_imports(src):
    assert_no_forbidden_imports(src)


# ---- correctness -----------------------------------------------------------

def basic_sequence(m):
    c = m.LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert_equal(c.get(1), 1, "get(1) after two puts")
    c.put(3, 3)  # evicts key 2
    assert_equal(c.get(2), -1, "key 2 should be evicted")
    c.put(4, 4)  # evicts key 1
    assert_equal(c.get(1), -1, "key 1 should be evicted")
    assert_equal(c.get(3), 3, "get(3)")
    assert_equal(c.get(4), 4, "get(4)")


def eviction_order(m):
    c = m.LRUCache(3)
    for k in (1, 2, 3):
        c.put(k, k * 10)
    c.put(4, 40)
    assert_equal(c.get(1), -1, "oldest key (1) must be evicted first")
    assert_equal([c.get(k) for k in (2, 3, 4)], [20, 30, 40], "remaining keys")


def get_refreshes_recency(m):
    c = m.LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.get(1)      # 1 becomes most recently used
    c.put(3, 3)   # must evict 2, not 1
    assert_equal(c.get(1), 1, "get() must mark key as recently used; key 1 was wrongly evicted")
    assert_equal(c.get(2), -1, "key 2 should have been evicted")


def update_refreshes_and_overwrites(m):
    c = m.LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 100)  # update: new value, now most recently used
    c.put(3, 3)    # must evict 2
    assert_equal(c.get(1), 100, "updated value / recency of key 1")
    assert_equal(c.get(2), -1, "key 2 should have been evicted after key 1 was updated")


def randomized_vs_reference(m):
    rng = random.Random(2024)
    for case in range(60):
        cap = rng.randint(1, 6)
        cand, oracle = m.LRUCache(cap), ref.LRUCache(cap)
        for step in range(120):
            k = rng.randint(0, 10)
            if rng.random() < 0.5:
                v = rng.randint(0, 999)
                cand.put(k, v)
                oracle.put(k, v)
            else:
                got, exp = cand.get(k), oracle.get(k)
                assert got == exp, f"case #{case} (capacity {cap}) step {step}: get({k}) expected {exp}, got {got}"


# ---- edge cases ------------------------------------------------------------

def capacity_one(m):
    c = m.LRUCache(1)
    c.put(1, 1)
    c.put(2, 2)
    assert_equal(c.get(1), -1, "capacity 1: key 1 evicted")
    assert_equal(c.get(2), 2, "capacity 1: key 2 kept")


def missing_key(m):
    c = m.LRUCache(2)
    assert_equal(c.get(42), -1, "missing key on empty cache")


# ---- robustness ------------------------------------------------------------

def invalid_capacity_raises(m):
    for bad in (0, -1):
        try:
            m.LRUCache(bad)
        except ValueError:
            continue
        raise AssertionError(f"LRUCache({bad}) must raise ValueError")


# ---- performance -----------------------------------------------------------

def ops_200k_large_capacity(m):
    rng = random.Random(7)
    c = m.LRUCache(50_000)
    for _ in range(200_000):
        k = rng.randint(0, 100_000)
        if rng.random() < 0.6:
            c.put(k, k)
        else:
            c.get(k)


CHECKS = [
    Check("interface", "interface", "Defines LRUCache with __init__/get/put", interface,
          weight=1, critical=True, static=True),
    Check("no_forbidden_imports", "interface", "No unnecessary system imports", no_forbidden_imports,
          weight=0.5, static=True),
    Check("basic_sequence", "correctness", "Canonical put/get/evict sequence", basic_sequence,
          weight=2, critical=True),
    Check("eviction_order", "correctness", "Evicts the least recently used key", eviction_order, weight=1.5),
    Check("get_refreshes_recency", "correctness", "get() marks key most recently used", get_refreshes_recency,
          weight=2),
    Check("update_refreshes_and_overwrites", "correctness", "put() on existing key updates value and recency",
          update_refreshes_and_overwrites, weight=1.5),
    Check("randomized_vs_reference", "correctness", "60 seeded random op sequences vs reference",
          randomized_vs_reference, weight=3),
    Check("capacity_one", "edge_case", "Capacity of 1", capacity_one, weight=0.5),
    Check("missing_key", "edge_case", "Missing key returns -1", missing_key, weight=0.5),
    Check("invalid_capacity_raises", "robustness", "capacity <= 0 raises ValueError", invalid_capacity_raises,
          weight=1),
    Check("ops_200k_large_capacity", "performance", "200k ops at capacity 50k within the time limit",
          ops_200k_large_capacity, weight=2, critical=True, timeout_s=8),
]
