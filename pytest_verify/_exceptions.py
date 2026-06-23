from __future__ import annotations

from typing import TYPE_CHECKING

from ._descriptors import approx_tolerance
from ._evaluator import _evaluate_single

if TYPE_CHECKING:
    from ._descriptors import CheckDescriptor

# Comparison operators rendered for the ordering checks.
_ORDER_OPS = {"greater": ">", "greater_equal": ">=", "less": "<", "less_equal": "<="}


def _value(value: object, units: str | None) -> str:
    """Render a value with its optional unit suffix (e.g. ``3.3V``)."""
    return f"{value}{units or ''}"


def _range(result: CheckDescriptor, units: str | None) -> str:
    """Render a ``between`` range with inclusive ``[]`` or exclusive ``()`` brackets."""
    low = _value(result["low"], units)
    high = _value(result["high"], units)
    return f"[{low}, {high}]" if result.get("inclusive", True) else f"({low}, {high})"


def _detail(result: CheckDescriptor, passed: bool) -> str:
    """Render the per-type ``expected … got …`` (failed) or compact (passed) clause.

    Follows the spec §7 table. ``passed`` selects which rendering to produce; for
    composite checks (``conditional``) it is the parent verdict, which equals the
    matched child's verdict.
    """
    check_type = result.get("check_type")
    units = result.get("units")

    if check_type == "equal":
        actual, expected = _value(result["actual"], units), _value(result["expected"], units)
        return f"{actual} == {expected}" if passed else f"expected {expected}, got {actual}"

    if check_type == "not_equal":
        actual, expected = _value(result["actual"], units), _value(result["expected"], units)
        return f"{actual} ≠ {expected}" if passed else f"expected ≠ {expected}, got {actual}"

    if check_type == "approx":
        actual = _value(result["actual"], units)
        expected = _value(result["expected"], units)
        tol = approx_tolerance(result.get("abs_tol"), result.get("rel_tol"), units)
        target = f"{expected} {tol}"
        return f"{actual} == {target}" if passed else f"expected {target}, got {actual}"

    if check_type in _ORDER_OPS:
        op = _ORDER_OPS[check_type]
        actual = _value(result["actual"], units)
        threshold = _value(result["threshold"], units)
        return f"{actual} {op} {threshold}" if passed else f"expected {op} {threshold}, got {actual}"

    if check_type == "between":
        actual = _value(result["actual"], units)
        rng = _range(result, units)
        return f"{actual} ∈ {rng}" if passed else f"expected {rng}, got {actual}"

    if check_type == "true":
        return "True" if passed else f"expected True, got {bool(result['actual'])}"

    if check_type == "false":
        return "False" if passed else f"expected False, got {bool(result['actual'])}"

    if check_type == "is_none":
        return "None" if passed else f"expected None, got {result['actual']!r}"

    if check_type == "is_not_none":
        return "not None" if passed else f"expected not None, got {result['actual']!r}"

    if check_type == "contains":
        needle = repr(result["needle"])
        return f"contains {needle}" if passed else f"expected to contain {needle}, got {result['haystack']!r}"

    if check_type == "not_contains":
        needle = repr(result["needle"])
        return (
            f"does not contain {needle}"
            if passed
            else f"expected to not contain {needle}, got {result['haystack']!r}"
        )

    if check_type == "matches":
        pattern = result["pattern"]
        return f"matches /{pattern}/" if passed else f"expected to match /{pattern}/, got {result['actual']!r}"

    if check_type == "is_instance":
        expected_type = result["expected_type"]
        if passed:
            return f"instance of {expected_type}"
        return f"expected instance of {expected_type}, got {type(result['actual']).__name__}"

    if check_type == "length":
        expected = result["expected"]
        if passed:
            return f"length {expected}"
        return f"expected length {expected}, got length {result['actual_length']}"

    if check_type == "all_satisfy":
        children: list[CheckDescriptor] = result.get("child_checks", [])
        total = len(children)
        if passed:
            return f"all {total} items pass"
        failed = sum(1 for c in children if not _evaluate_single(c))
        return f"expected all {total} to pass, got {failed} failed"

    if check_type == "conditional":
        switch = result["switch_value"]
        matched = result.get("matched_case")
        cases: dict[str, CheckDescriptor] = result.get("cases", {})
        child = cases.get(matched) if matched is not None else result.get("default")
        if child is None:
            return f"[{_mode(switch)} → no match]"
        return f"[{_mode(switch)} → {child.get('name', '')}] — {_detail(child, passed)}"

    if check_type == "guard":
        branches: list[dict] = result.get("branches", [])
        matched = result.get("matched_index")
        if matched is not None:
            label = branches[matched]["label"]
            child = branches[matched]["check"]
        elif result.get("default") is not None:
            label = "default"
            child = result["default"]
        else:
            return "[→ no match]"
        return f"[→ {label}] — {_detail(child, passed)}"

    if check_type == "fail":
        return f"FAIL: {result.get('msg', '')}"

    # Fallback for any unknown check type: the canonical description, prefix-stripped.
    name = result.get("name", "")
    description = result.get("description", "")
    prefix = f"Verify '{name}' "
    return description[len(prefix):] if description.startswith(prefix) else description


def _mode(switch: object) -> str:
    return f"mode={switch}"


class ChecksFailedError(AssertionError):
    """Raised at fixture teardown when one or more soft checks failed.

    The message follows spec §7: a ``N of M checks failed`` header, then the
    failed checks (``✗``) before the passed checks (``✓``), each prefixed with
    its ``[seq]`` index in evaluation order, its name, and a per-type
    ``expected … got …`` (failed) or compact (passed) detail clause.
    """

    def __init__(self, results: list[CheckDescriptor]) -> None:
        self.results = results
        failed = [(i, r) for i, r in enumerate(results) if not r.get("passed")]
        passed = [(i, r) for i, r in enumerate(results) if r.get("passed")]

        def line(marker: str, idx: int, result: CheckDescriptor, is_passed: bool) -> str:
            name = result.get("name", "")
            # conditional/guard render `name [… → child] — …`, attaching their
            # bracket clause directly to the name without the `— ` separator.
            sep = " " if result.get("check_type") in ("conditional", "guard") else " — "
            return f"  {marker} [{idx}] {name}{sep}{_detail(result, is_passed)}"

        lines: list[str] = [f"{len(failed)} of {len(results)} checks failed", ""]
        lines.extend(line("✗", idx, r, False) for idx, r in failed)
        if passed:
            lines.append("")
            lines.extend(line("✓", idx, r, True) for idx, r in passed)

        super().__init__("\n".join(lines))
