from __future__ import annotations

from typing import Any, Callable, Generator

import pytest

from ._descriptors import CheckDescriptor
from ._evaluator import _evaluate_single
from ._exceptions import ChecksFailedError
from ._stash import check_results_key
from ._verify import Verify

# Stash key to store the fixture instance on the test item so the
# ``pytest_runtest_makereport`` hook can inspect results after the call phase.
_verify_key: pytest.StashKey[_FixtureVerify] = pytest.StashKey()


class _FixtureVerify(Verify):
    """Fixture-scoped verify that evaluates checks immediately and collects results."""

    def __init__(self, item: pytest.Item, reporter_installed: bool) -> None:
        self._item = item
        self._reporter_installed = reporter_installed
        self._results: list[CheckDescriptor] = []

    # ------------------------------------------------------------------
    # Override every public method to evaluate + store
    # ------------------------------------------------------------------

    def _record(self, descriptor: CheckDescriptor) -> CheckDescriptor:
        """Evaluate, store, optionally stash, and return the descriptor."""
        descriptor["passed"] = _evaluate_single(descriptor)
        self._results.append(descriptor)
        if self._reporter_installed:
            stash_list = self._item.stash.setdefault(check_results_key, [])
            stash_list.append(descriptor)
        return descriptor

    def equal(self, actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
        return self._record(super().equal(actual, expected, name=name, units=units))

    def not_equal(self, actual: Any, expected: Any, *, name: str, units: str | None = None) -> CheckDescriptor:
        return self._record(super().not_equal(actual, expected, name=name, units=units))

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
        return self._record(
            super().approx(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol, name=name, units=units)
        )

    def greater(self, actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
        return self._record(super().greater(actual, threshold, name=name, units=units))

    def greater_equal(
        self, actual: Any, threshold: float, *, name: str, units: str | None = None
    ) -> CheckDescriptor:
        return self._record(super().greater_equal(actual, threshold, name=name, units=units))

    def less(self, actual: Any, threshold: float, *, name: str, units: str | None = None) -> CheckDescriptor:
        return self._record(super().less(actual, threshold, name=name, units=units))

    def less_equal(
        self, actual: Any, threshold: float, *, name: str, units: str | None = None
    ) -> CheckDescriptor:
        return self._record(super().less_equal(actual, threshold, name=name, units=units))

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
        return self._record(super().between(actual, low, high, inclusive=inclusive, name=name, units=units))

    def is_true(self, actual: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().is_true(actual, name=name))

    def is_false(self, actual: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().is_false(actual, name=name))

    def is_none(self, actual: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().is_none(actual, name=name))

    def is_not_none(self, actual: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().is_not_none(actual, name=name))

    def contains(self, haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().contains(haystack, needle, name=name))

    def not_contains(self, haystack: Any, needle: Any, *, name: str) -> CheckDescriptor:
        return self._record(super().not_contains(haystack, needle, name=name))

    def matches(self, actual: Any, pattern: str, *, name: str) -> CheckDescriptor:
        return self._record(super().matches(actual, pattern, name=name))

    def is_instance(self, actual: Any, expected_type: type, *, name: str) -> CheckDescriptor:
        descriptor = super().is_instance(actual, expected_type, name=name)
        # Evaluate using the real type object (more reliable than name comparison)
        descriptor["passed"] = isinstance(actual, expected_type)
        self._results.append(descriptor)
        if self._reporter_installed:
            stash_list = self._item.stash.setdefault(check_results_key, [])
            stash_list.append(descriptor)
        return descriptor

    def length(self, actual: Any, expected: int, *, name: str) -> CheckDescriptor:
        return self._record(super().length(actual, expected, name=name))

    def all_satisfy(
        self, items: Any, descriptor_factory: Callable[[Any], CheckDescriptor], *, name: str
    ) -> CheckDescriptor:
        return self._record(super().all_satisfy(items, descriptor_factory, name=name))

    def conditional(
        self,
        switch_value: Any,
        *,
        cases: dict[str, CheckDescriptor],
        default: CheckDescriptor | None = None,
        name: str,
    ) -> CheckDescriptor:
        return self._record(super().conditional(switch_value, cases=cases, default=default, name=name))

    def fail(self, msg: str, *, name: str | None = None) -> CheckDescriptor:
        return self._record(super().fail(msg, name=name))


# ======================================================================
# Plugin hooks
# ======================================================================

_reporter_installed: bool = False


def pytest_configure(config: pytest.Config) -> None:
    global _reporter_installed
    _reporter_installed = config.pluginmanager.has_plugin("pytest-reporter")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo,  # type: ignore[type-arg]
) -> Generator[None, pytest.TestReport, None]:
    """After the call phase, check for soft-assertion failures and convert to FAILED."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.passed:
        fv = item.stash.get(_verify_key, None)
        if fv is not None and any(not r.get("passed") for r in fv._results):
            report.outcome = "failed"
            report.longrepr = str(ChecksFailedError(fv._results))


@pytest.fixture()
def verify(request: pytest.FixtureRequest) -> _FixtureVerify:
    """Soft-assertion fixture that collects checks and fails at teardown."""
    item: pytest.Item = request.node  # type: ignore[assignment]
    fv = _FixtureVerify(item, _reporter_installed)
    item.stash[_verify_key] = fv
    return fv
