from __future__ import annotations

from typing import Any, List, Optional, TypedDict


class CheckDescriptor(TypedDict, total=False):
    """Plain-data descriptor returned by every ``verify.*`` call.

    All fields except ``check_type``, ``name``, and ``description`` are
    check-type-specific and may or may not be present depending on the
    check that produced the descriptor.
    """

    # --- always present ---
    check_type: str
    name: str
    description: str

    # --- set after evaluation (fixture path) ---
    passed: bool

    # --- check-type-specific ---
    actual: Any
    expected: Any
    abs_tol: float | None
    rel_tol: float | None
    units: str | None
    threshold: float
    low: float
    high: float
    inclusive: bool
    haystack: Any
    needle: Any
    pattern: str
    expected_type: str
    actual_length: int
    child_checks: list[CheckDescriptor]
    switch_value: Any
    cases: dict[str, CheckDescriptor]
    default: CheckDescriptor | None
    matched_case: str | None
    msg: str


# ---------------------------------------------------------------------------
# Descriptor builder helpers
# ---------------------------------------------------------------------------

def _units_suffix(units: str | None) -> str:
    return units if units else ""


def _format_percent(rel_tol: float) -> str:
    """Render a relative tolerance as a percent string, dropping a trailing ``.0``.

    ``0.01`` -> ``"1"``, ``0.015`` -> ``"1.5"``. The ``g`` format also rounds away
    IEEE 754 artifacts from the ``* 100`` (e.g. ``0.007 * 100`` -> ``"0.7"``).
    """
    return f"{rel_tol * 100:.10g}"


def build_equal(actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "equal",
        "name": name,
        "description": f"Verify '{name}' == {expected}{u}",
        "actual": actual,
        "expected": expected,
        "units": units,
    }
    return desc


def build_not_equal(actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "not_equal",
        "name": name,
        "description": f"Verify '{name}' != {expected}{u}",
        "actual": actual,
        "expected": expected,
        "units": units,
    }
    return desc


def build_approx(
    actual: Any,
    expected: Any,
    *,
    abs_tol: float | None = None,
    rel_tol: float | None = None,
    name: str,
    units: str | None = None,
) -> CheckDescriptor:
    if abs_tol is None and rel_tol is None:
        raise ValueError("approx requires at least one of abs_tol or rel_tol")
    u = _units_suffix(units)
    # The (abs)/(rel) labels disambiguate only when both tolerances are present;
    # with a single tolerance the bare "\u00b1 value" is unambiguous (spec \u00a75.1).
    if abs_tol is not None and rel_tol is not None:
        tol_str = f"\u00b1 {abs_tol}{u} (abs) \u00b1 {_format_percent(rel_tol)}% (rel)"
    elif abs_tol is not None:
        tol_str = f"\u00b1 {abs_tol}{u}"
    else:
        tol_str = f"\u00b1 {_format_percent(rel_tol)}%"
    desc: CheckDescriptor = {
        "check_type": "approx",
        "name": name,
        "description": f"Verify '{name}' == {expected}{u} {tol_str}",
        "actual": actual,
        "expected": expected,
        "abs_tol": abs_tol,
        "rel_tol": rel_tol,
        "units": units,
    }
    return desc


def build_greater(actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "greater",
        "name": name,
        "description": f"Verify '{name}' > {threshold}{u}",
        "actual": actual,
        "threshold": threshold,
        "units": units,
    }
    return desc


def build_greater_equal(actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "greater_equal",
        "name": name,
        "description": f"Verify '{name}' >= {threshold}{u}",
        "actual": actual,
        "threshold": threshold,
        "units": units,
    }
    return desc


def build_less(actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "less",
        "name": name,
        "description": f"Verify '{name}' < {threshold}{u}",
        "actual": actual,
        "threshold": threshold,
        "units": units,
    }
    return desc


def build_less_equal(actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
    u = _units_suffix(units)
    desc: CheckDescriptor = {
        "check_type": "less_equal",
        "name": name,
        "description": f"Verify '{name}' <= {threshold}{u}",
        "actual": actual,
        "threshold": threshold,
        "units": units,
    }
    return desc


def build_between(
    actual: Any,
    low: float,
    high: float,
    *,
    inclusive: bool = True,
    name: str,
    units: str | None = None,
) -> CheckDescriptor:
    u = _units_suffix(units)
    if inclusive:
        description = f"Verify '{name}' \u2208 [{low}{u}, {high}{u}]"
    else:
        description = f"Verify '{name}' \u2208 ({low}{u}, {high}{u})"
    desc: CheckDescriptor = {
        "check_type": "between",
        "name": name,
        "description": description,
        "actual": actual,
        "low": low,
        "high": high,
        "inclusive": inclusive,
        "units": units,
    }
    return desc


def build_is_true(actual: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "true",
        "name": name,
        "description": f"Verify '{name}' is True",
        "actual": actual,
    }
    return desc


def build_is_false(actual: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "false",
        "name": name,
        "description": f"Verify '{name}' is False",
        "actual": actual,
    }
    return desc


def build_is_none(actual: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "is_none",
        "name": name,
        "description": f"Verify '{name}' is None",
        "actual": actual,
    }
    return desc


def build_is_not_none(actual: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "is_not_none",
        "name": name,
        "description": f"Verify '{name}' is not None",
        "actual": actual,
    }
    return desc


def build_contains(haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "contains",
        "name": name,
        "description": f"Verify '{name}' contains {needle!r}",
        "haystack": haystack,
        "needle": needle,
    }
    return desc


def build_not_contains(haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "not_contains",
        "name": name,
        "description": f"Verify '{name}' does not contain {needle!r}",
        "haystack": haystack,
        "needle": needle,
    }
    return desc


def build_matches(actual: Any, pattern: str, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "matches",
        "name": name,
        "description": f"Verify '{name}' matches /{pattern}/",
        "actual": actual,
        "pattern": pattern,
    }
    return desc


def build_is_instance(actual: Any, expected_type: type, *, name: str) -> CheckDescriptor:
    type_name = expected_type.__name__
    desc: CheckDescriptor = {
        "check_type": "is_instance",
        "name": name,
        "description": f"Verify '{name}' is instance of {type_name}",
        "actual": actual,
        "expected_type": type_name,
    }
    return desc


def build_length(actual: Any, expected: int, *, name: str) -> CheckDescriptor:
    desc: CheckDescriptor = {
        "check_type": "length",
        "name": name,
        "description": f"Verify '{name}' has length {expected}",
        "actual": actual,
        "expected": expected,
        "actual_length": len(actual),
    }
    return desc


def build_all_satisfy(
    items: Any,
    descriptor_factory: Any,
    *,
    name: str,
) -> CheckDescriptor:
    child_checks: list[CheckDescriptor] = [descriptor_factory(item) for item in items]
    desc: CheckDescriptor = {
        "check_type": "all_satisfy",
        "name": name,
        "description": f"Verify all items in '{name}' satisfy condition ({len(child_checks)} items)",
        "child_checks": child_checks,
    }
    return desc


def build_conditional(
    switch_value: Any,
    *,
    cases: dict[str, CheckDescriptor],
    default: CheckDescriptor | None = None,
    name: str,
) -> CheckDescriptor:
    key = str(switch_value)
    matched_case: str | None = key if key in cases else None
    desc: CheckDescriptor = {
        "check_type": "conditional",
        "name": name,
        "description": f"Verify '{name}' [mode={switch_value}]",
        "switch_value": switch_value,
        "cases": cases,
        "default": default,
        "matched_case": matched_case,
    }
    return desc


def build_fail(msg: str, *, name: str | None = None) -> CheckDescriptor:
    resolved_name = name if name is not None else msg
    desc: CheckDescriptor = {
        "check_type": "fail",
        "name": resolved_name,
        "description": f"FAIL: {msg}",
        "msg": msg,
    }
    return desc
