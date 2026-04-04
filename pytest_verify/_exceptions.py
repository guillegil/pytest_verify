from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._descriptors import CheckDescriptor


class ChecksFailedError(AssertionError):
    """Raised at fixture teardown when one or more soft checks failed.

    The message lists failed checks first, then passed checks, each prefixed
    with its ``[seq]`` index in evaluation order.
    """

    def __init__(self, results: list[CheckDescriptor]) -> None:
        self.results = results
        failed = [(i, r) for i, r in enumerate(results) if not r.get("passed")]
        passed = [(i, r) for i, r in enumerate(results) if r.get("passed")]

        lines: list[str] = []
        if failed:
            lines.append("FAILED checks:")
            for idx, r in failed:
                lines.append(f"  [{idx}] {r.get('description', r.get('name', ''))}")
        if passed:
            lines.append("PASSED checks:")
            for idx, r in passed:
                lines.append(f"  [{idx}] {r.get('description', r.get('name', ''))}")

        super().__init__("\n".join(lines))
