"""Shared helpers for writing task checks."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

FORBIDDEN_MODULES = {"os", "subprocess", "sys", "shutil", "socket", "ctypes", "importlib"}


def load_reference(checks_file: str):
    """Load the task's reference solution (used as an oracle for randomized checks)."""
    path = Path(checks_file).resolve().parent / "reference.py"
    spec = importlib.util.spec_from_file_location("reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_defines_function(source: str, name: str, n_params: int) -> None:
    tree = ast.parse(source)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert name in funcs, f"no top-level function named `{name}`"
    got = len(funcs[name].args.args)
    assert got == n_params, f"`{name}` takes {got} parameter(s), spec requires {n_params}"


def assert_defines_class(source: str, name: str, methods: list[str]) -> None:
    tree = ast.parse(source)
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    assert name in classes, f"no top-level class named `{name}`"
    defined = {n.name for n in classes[name].body if isinstance(n, ast.FunctionDef)}
    missing = [m for m in methods if m not in defined]
    assert not missing, f"`{name}` is missing method(s): {', '.join(missing)}"


def assert_no_forbidden_imports(source: str) -> None:
    tree = ast.parse(source)
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    bad = sorted(found & FORBIDDEN_MODULES)
    assert not bad, f"imports system modules not needed for this task: {', '.join(bad)}"


def assert_equal(got, expected, label: str) -> None:
    assert got == expected, f"{label}: expected {expected!r}, got {got!r}"
