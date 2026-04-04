from __future__ import annotations

from typing import Any, Callable

from ._descriptors import (
    CheckDescriptor,
    build_all_satisfy,
    build_approx,
    build_between,
    build_conditional,
    build_contains,
    build_equal,
    build_fail,
    build_greater,
    build_greater_equal,
    build_is_false,
    build_is_instance,
    build_is_none,
    build_is_not_none,
    build_is_true,
    build_length,
    build_less,
    build_less_equal,
    build_matches,
    build_not_contains,
    build_not_equal,
)
from ._evaluator import evaluate as _evaluate
from ._evaluator import evaluate_detailed as _evaluate_detailed


class Verify:
    """Soft-assertion builder.

    When used as the **module-level** ``verify`` instance, methods return
    unevaluated :class:`CheckDescriptor` dicts (no ``passed`` field).

    When wrapped by the pytest fixture, the fixture evaluates each descriptor
    immediately after construction and sets the ``passed`` field.
    """

    # ------------------------------------------------------------------
    # Equality & approximation
    # ------------------------------------------------------------------

    def equal(self, actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
        """Check that *actual* equals *expected*.

        Args:
            actual: The value under test.
            expected: The expected value.
            name: Human-readable label for the check.
            units: Optional unit suffix (e.g. ``"V"``, ``"A"``).

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_equal(actual, expected, name=name, units=units)

    def not_equal(self, actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
        """Check that *actual* does not equal *expected*.

        Args:
            actual: The value under test.
            expected: The value that *actual* must differ from.
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_not_equal(actual, expected, name=name, units=units)

    def approx(
        self,
        actual: Any,
        expected: Any,
        *,
        abs_tol: float | None = None,
        rel_tol: float | None = None,
        name: str,
        units: str | None = None,
    ) -> CheckDescriptor:
        """Check that *actual* is approximately equal to *expected*.

        At least one of *abs_tol* or *rel_tol* must be provided.

        Args:
            actual: The value under test.
            expected: The expected value.
            abs_tol: Absolute tolerance.
            rel_tol: Relative tolerance (fraction, e.g. 0.01 = 1%).
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.

        Raises:
            ValueError: If neither *abs_tol* nor *rel_tol* is provided.
        """
        return build_approx(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol, name=name, units=units)

    # ------------------------------------------------------------------
    # Ordering & range
    # ------------------------------------------------------------------

    def greater(self, actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
        """Check that *actual* > *threshold*.

        Args:
            actual: The value under test.
            threshold: The lower bound (exclusive).
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_greater(actual, threshold, name=name, units=units)

    def greater_equal(
        self, actual: Any, threshold: float, *, name: str, units: str | None = None
    ) -> CheckDescriptor:
        """Check that *actual* >= *threshold*.

        Args:
            actual: The value under test.
            threshold: The lower bound (inclusive).
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_greater_equal(actual, threshold, name=name, units=units)

    def less(self, actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
        """Check that *actual* < *threshold*.

        Args:
            actual: The value under test.
            threshold: The upper bound (exclusive).
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_less(actual, threshold, name=name, units=units)

    def less_equal(self, actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
        """Check that *actual* <= *threshold*.

        Args:
            actual: The value under test.
            threshold: The upper bound (inclusive).
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_less_equal(actual, threshold, name=name, units=units)

    def between(
        self,
        actual: Any,
        low: float,
        high: float,
        *,
        inclusive: bool = True,
        name: str,
        units: str | None = None,
    ) -> CheckDescriptor:
        """Check that *actual* is between *low* and *high*.

        Args:
            actual: The value under test.
            low: Lower bound.
            high: Upper bound.
            inclusive: If ``True`` (default), bounds are inclusive.
            name: Human-readable label for the check.
            units: Optional unit suffix.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_between(actual, low, high, inclusive=inclusive, name=name, units=units)

    # ------------------------------------------------------------------
    # Boolean & identity
    # ------------------------------------------------------------------

    def is_true(self, actual: Any, *, name: str) -> CheckDescriptor:
        """Check that ``bool(actual)`` is ``True``.

        Args:
            actual: The value under test.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_is_true(actual, name=name)

    def is_false(self, actual: Any, *, name: str) -> CheckDescriptor:
        """Check that ``bool(actual)`` is ``False``.

        Args:
            actual: The value under test.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_is_false(actual, name=name)

    def is_none(self, actual: Any, *, name: str) -> CheckDescriptor:
        """Check that *actual* is ``None``.

        Args:
            actual: The value under test.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_is_none(actual, name=name)

    def is_not_none(self, actual: Any, *, name: str) -> CheckDescriptor:
        """Check that *actual* is not ``None``.

        Args:
            actual: The value under test.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_is_not_none(actual, name=name)

    # ------------------------------------------------------------------
    # String & container
    # ------------------------------------------------------------------

    def contains(self, haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
        """Check that *needle* is in *haystack*.

        Args:
            haystack: The container to search.
            needle: The item to search for.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_contains(haystack, needle, name=name)

    def not_contains(self, haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
        """Check that *needle* is **not** in *haystack*.

        Args:
            haystack: The container to search.
            needle: The item to search for.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_not_contains(haystack, needle, name=name)

    def matches(self, actual: Any, pattern: str, *, name: str) -> CheckDescriptor:
        """Check that *actual* matches the regular-expression *pattern*.

        Args:
            actual: The string to test.
            pattern: A regex pattern (searched with ``re.search``).
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_matches(actual, pattern, name=name)

    # ------------------------------------------------------------------
    # Type / collection / conditional
    # ------------------------------------------------------------------

    def is_instance(self, actual: Any, expected_type: type, *, name: str) -> CheckDescriptor:
        """Check that *actual* is an instance of *expected_type*.

        Args:
            actual: The value under test.
            expected_type: The expected type.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_is_instance(actual, expected_type, name=name)

    def length(self, actual: Any, expected: int, *, name: str) -> CheckDescriptor:
        """Check that ``len(actual)`` equals *expected*.

        Args:
            actual: The sized object under test.
            expected: The expected length.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_length(actual, expected, name=name)

    def all_satisfy(
        self, items: Any, descriptor_factory: Callable[[Any], CheckDescriptor], *, name: str
    ) -> CheckDescriptor:
        """Check that every item in *items* satisfies *descriptor_factory*.

        The factory is invoked immediately for each item, and the resulting
        child descriptors are stored in the returned descriptor.

        Args:
            items: An iterable of items.
            descriptor_factory: A callable that receives one item and returns
                a :class:`CheckDescriptor`.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_all_satisfy(items, descriptor_factory, name=name)

    def conditional(
        self,
        switch_value: Any,
        *,
        cases: dict[str, CheckDescriptor],
        default: CheckDescriptor | None = None,
        name: str,
    ) -> CheckDescriptor:
        """Conditionally evaluate a check based on *switch_value*.

        The ``switch_value`` is stringified and looked up in *cases*.
        If no match is found, *default* is used.  If no default is provided
        and no case matches, the check fails.

        Args:
            switch_value: Value to match against *cases* keys.
            cases: Mapping of string keys to descriptors.
            default: Fallback descriptor when no case matches.
            name: Human-readable label for the check.

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_conditional(switch_value, cases=cases, default=default, name=name)

    def fail(self, msg: str, *, name: str | None = None) -> CheckDescriptor:
        """Unconditionally failing check.

        Args:
            msg: Failure message.
            name: Optional label (defaults to *msg*).

        Returns:
            A :class:`CheckDescriptor` dict.
        """
        return build_fail(msg, name=name)

    # ------------------------------------------------------------------
    # Evaluation helpers (module-level API)
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(*descriptors: CheckDescriptor) -> bool:
        """Evaluate descriptors without side effects.

        Returns:
            ``True`` only if **all** descriptors pass.
        """
        return _evaluate(*descriptors)

    @staticmethod
    def evaluate_detailed(*descriptors: CheckDescriptor) -> list[dict]:
        """Evaluate descriptors and return detailed result dicts.

        Each result contains ``passed``, ``details``, ``seq``, and ``t``.
        """
        return _evaluate_detailed(*descriptors)
