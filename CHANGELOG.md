# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-20

### Changed

- `ChecksFailedError` message now follows the spec §7 format: an `N of M checks failed` header, then failed checks (`✗`) before passed checks (`✓`), each with its `[seq]` index, name, and a per-type detail clause — `expected … got …` for failures and a compact restatement for passes (see spec §7.1) — replacing the previous `FAILED checks:` / `PASSED checks:` lists.
- Check `description` strings now match the authoritative spec (§5): `approx` with both tolerances renders `== 3.3V ± 0.05V (abs) ± 1% (rel)` (labels only when both are present) and percentages drop a trailing `.0` (`1%`, not `1.0%`); `length` renders `Verify 'name' has length N` instead of `Verify len('name') == N`; `all_satisfy` appends the item count, e.g. `… satisfy condition (4 items)`.

### Fixed

- Standalone `verify.evaluate()` of an `is_instance` check now honours concrete subclasses (e.g. `is_instance(True, int)` passes), matching the expected type name against the actual object's MRO instead of only its exact type name. The `verify` fixture already evaluated this correctly via real `isinstance`.
- Soft-assert failures are no longer silently dropped when the test body also fails with a hard error (exception or `assert`). The original traceback is preserved and the failed-checks summary is appended as a report section. Previously the verdict hook only ran when the call phase passed, hiding soft failures behind any hard failure.

## [0.1.0] - 2026-04-04

### Added

- `verify` pytest fixture providing soft assertions that collect failures and report them at test end.
- 20 check functions: `equal`, `not_equal`, `approx`, `greater`, `greater_equal`, `less`, `less_equal`, `between`, `is_true`, `is_false`, `is_none`, `is_not_none`, `contains`, `not_contains`, `matches`, `is_instance`, `length`, `all_satisfy`, `conditional`, `fail`.
- Module-level `verify` instance (`from pytest_verify import verify`) for building unevaluated descriptors.
- `verify.evaluate()` and `verify.evaluate_detailed()` for standalone descriptor evaluation.
- `CheckDescriptor` TypedDict for fully typed, JSON-serializable check results.
- `ChecksFailedError` with formatted message listing failed and passed checks.
- Optional `pytest-reporter` integration via `item.stash` (auto-detected at session start).
- Full type annotations and `py.typed` marker for IDE autocompletion (PEP 561).
