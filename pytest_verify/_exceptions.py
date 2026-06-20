from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._descriptors import CheckDescriptor

# Check types whose scalar ``actual`` value (plus optional ``units``) is worth
# echoing back as ``, got <value>`` so a failure is diagnosable at a glance.
_SCALAR_ACTUAL_TYPES = frozenset(
    {"equal", "not_equal", "approx", "greater", "greater_equal", "less", "less_equal", "between"}
)


def _predicate(result: CheckDescriptor) -> str:
    """Return the verification statement without the ``Verify 'name' `` prefix."""
    name = result.get("name", "")
    description = result.get("description", "")
    prefix = f"Verify '{name}' "
    if description.startswith(prefix):
        return description[len(prefix):]
    return description


def _got_clause(result: CheckDescriptor) -> str:
    """Return a ``, got <value>`` suffix for checks that carry a scalar actual.

    Empty string for checks where echoing the raw actual would be noise
    (containers, identity, regex, instance, composite checks).
    """
    check_type = result.get("check_type")
    units = result.get("units") or ""
    if check_type in _SCALAR_ACTUAL_TYPES:
        return f", got {result.get('actual')}{units}"
    if check_type == "length":
        return f", got length {result.get('actual_length')}"
    if check_type in ("true", "false"):
        return f", got {bool(result.get('actual'))}"
    return ""


class ChecksFailedError(AssertionError):
    """Raised at fixture teardown when one or more soft checks failed.

    The message follows spec §7: a ``N of M checks failed`` header, then the
    failed checks (``✗``) before the passed checks (``✓``), each prefixed with
    its ``[seq]`` index in evaluation order and its name.
    """

    def __init__(self, results: list[CheckDescriptor]) -> None:
        self.results = results
        failed = [(i, r) for i, r in enumerate(results) if not r.get("passed")]
        passed = [(i, r) for i, r in enumerate(results) if r.get("passed")]

        def line(marker: str, idx: int, result: CheckDescriptor) -> str:
            name = result.get("name", "")
            return f"  {marker} [{idx}] {name} — {_predicate(result)}{_got_clause(result)}"

        lines: list[str] = [f"{len(failed)} of {len(results)} checks failed", ""]
        lines.extend(line("✗", idx, r) for idx, r in failed)
        if passed:
            lines.append("")
            lines.extend(line("✓", idx, r) for idx, r in passed)

        super().__init__("\n".join(lines))
