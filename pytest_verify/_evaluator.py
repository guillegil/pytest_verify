from __future__ import annotations

import math
import re
import time
from typing import Any

from ._descriptors import CheckDescriptor


def _evaluate_single(descriptor: CheckDescriptor) -> bool:
    """Evaluate a single descriptor and return True if it passes."""
    check_type = descriptor["check_type"]

    if check_type == "equal":
        return descriptor["actual"] == descriptor["expected"]

    if check_type == "not_equal":
        return descriptor["actual"] != descriptor["expected"]

    if check_type == "approx":
        actual = descriptor["actual"]
        expected = descriptor["expected"]
        abs_tol = descriptor.get("abs_tol")
        rel_tol = descriptor.get("rel_tol")
        if abs_tol is not None and math.isclose(actual, expected, abs_tol=abs_tol, rel_tol=0):
            return True
        if rel_tol is not None and math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=0):
            return True
        return False

    if check_type == "greater":
        return descriptor["actual"] > descriptor["threshold"]

    if check_type == "greater_equal":
        return descriptor["actual"] >= descriptor["threshold"]

    if check_type == "less":
        return descriptor["actual"] < descriptor["threshold"]

    if check_type == "less_equal":
        return descriptor["actual"] <= descriptor["threshold"]

    if check_type == "between":
        actual = descriptor["actual"]
        low = descriptor["low"]
        high = descriptor["high"]
        if descriptor.get("inclusive", True):
            return low <= actual <= high
        return low < actual < high

    if check_type == "true":
        return bool(descriptor["actual"]) is True

    if check_type == "false":
        return bool(descriptor["actual"]) is False

    if check_type == "is_none":
        return descriptor["actual"] is None

    if check_type == "is_not_none":
        return descriptor["actual"] is not None

    if check_type == "contains":
        return descriptor["needle"] in descriptor["haystack"]

    if check_type == "not_contains":
        return descriptor["needle"] not in descriptor["haystack"]

    if check_type == "matches":
        return re.search(descriptor["pattern"], descriptor["actual"]) is not None

    if check_type == "is_instance":
        # The descriptor only stores the expected type's NAME (JSON-serializable),
        # not the type object — so we can't call isinstance() here. But the live
        # ``actual`` object is available, so we match the name against every class
        # in its MRO. This honours concrete subclasses (e.g. isinstance(True, int)).
        # The fixture path uses real isinstance() and so additionally handles ABC
        # virtual subclasses, which name-based MRO matching cannot resolve.
        actual = descriptor["actual"]
        expected_name = descriptor["expected_type"]
        return any(klass.__name__ == expected_name for klass in type(actual).__mro__)

    if check_type == "length":
        return descriptor["actual_length"] == descriptor["expected"]

    if check_type == "all_satisfy":
        child_checks: list[CheckDescriptor] = descriptor.get("child_checks", [])
        return all(_evaluate_single(c) for c in child_checks)

    if check_type == "conditional":
        key = str(descriptor["switch_value"])
        cases: dict[str, CheckDescriptor] = descriptor.get("cases", {})
        default: CheckDescriptor | None = descriptor.get("default")
        if key in cases:
            return _evaluate_single(cases[key])
        if default is not None:
            return _evaluate_single(default)
        return False

    if check_type == "guard":
        branches: list[dict] = descriptor.get("branches", [])
        matched: int | None = descriptor.get("matched_index")
        if matched is not None:
            return _evaluate_single(branches[matched]["check"])
        default = descriptor.get("default")
        if default is not None:
            return _evaluate_single(default)
        return False

    if check_type == "fail":
        return False

    raise ValueError(f"Unknown check_type: {check_type!r}")


def evaluate(*descriptors: CheckDescriptor) -> bool:
    """Evaluate one or more descriptors, returning ``True`` only if ALL pass.

    This is a pure function with no side effects — it does not mutate the
    descriptors or store results anywhere.
    """
    return all(_evaluate_single(d) for d in descriptors)


def evaluate_detailed(*descriptors: CheckDescriptor) -> list[dict[str, Any]]:
    """Evaluate descriptors and return detailed result dicts.

    Each result dict contains:
    - ``passed``: bool
    - ``details``: the original descriptor
    - ``seq``: 0-based sequence index
    - ``t``: timestamp of evaluation (seconds since epoch)
    """
    results: list[dict[str, Any]] = []
    for seq, d in enumerate(descriptors):
        passed = _evaluate_single(d)
        results.append({
            "passed": passed,
            "details": d,
            "seq": seq,
            "t": time.time(),
        })
    return results
