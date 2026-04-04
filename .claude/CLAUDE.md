# CLAUDE.md — pytest-verify

## Project Overview

`pytest-verify` is a pytest plugin that provides soft assertions for test verification. It is the **judge** — the only plugin that determines pass/fail for check-based assertions. It works standalone and optionally integrates with `pytest-reporter` for rich HTML rendering.

**Specification:** The authoritative spec lives in Notion under "Pytest Verify" (child of "Pytest Reporter"). Always consult the spec for schema details, edge cases, and design decisions.

## Architecture

```
pytest-verify (this plugin)          pytest-reporter (separate plugin)
┌──────────────────────────┐         ┌────────────────────────────────┐
│ verify fixture (scope:   │         │ step(check=descriptor)         │
│   test)                  │         │   → reads descriptor           │
│   .approx()              │         │   → creates procedure substep  │
│   .between()             │ item.   │   → NO evaluation              │
│   .greater()             │ stash   │                                │
│   ...                    │ ────►   │ Reads item.stash for           │
│                          │         │ verification card rendering    │
│ Evaluates immediately    │         │                                │
│ Stores results internally│         │ Observes outcome via           │
│ Raises ChecksFailedError │         │ pytest_runtest_makereport      │
│   at teardown            │         │                                │
└──────────────────────────┘         └────────────────────────────────┘
         │                                        │
         │  Neither plugin imports the other.     │
         │  Communication: item.stash only.       │
         └────────────────────────────────────────┘
```

## Core Principles

- **verify fixture is the primary API.** It evaluates checks immediately, stores results, returns descriptor dicts, and raises `ChecksFailedError` at teardown. No imports needed — it's a pytest fixture.
- **verify module is the secondary API.** `from pytest_verify import verify` provides the same functions but returns unevaluated descriptors. Used standalone or for building descriptors to pass to `verify.evaluate()`.
- **Soft assertions.** Failed checks never stop the test. All checks run to completion. Failures are collected and raised as a single `ChecksFailedError` at teardown.
- **Pure data descriptors.** All check functions return plain dicts matching the CheckDescriptor schema. Descriptors are JSON-serializable.
- **No dependency on pytest-reporter.** The plugin works standalone. Reporter detection happens at `pytest_configure` via plugin manager query. If detected, results are also written to `item.stash`.

## Package Structure

```
pytest_verify/
├── __init__.py              # Exports: verify module instance, Verify class, CheckDescriptor
├── py.typed                 # PEP 561 marker — REQUIRED
├── _verify.py               # Verify class implementation
├── _descriptors.py          # CheckDescriptor TypedDict, descriptor builder functions
├── _evaluator.py            # evaluate() and evaluate_detailed() logic
├── _fixture.py              # pytest fixture registration, teardown logic
├── _stash.py                # Stash key definition, reporter detection
├── _exceptions.py           # ChecksFailedError
└── _types.py                # Shared type aliases
```

## Key Types

```python
# CheckDescriptor — returned by every verify.* call
class CheckDescriptor(TypedDict, total=False):
    check_type: str          # Required: "approx", "equal", "between", etc.
    name: str                # Required: human-readable label
    description: str         # Required: pre-formatted verification statement
    passed: bool             # Present only when returned from fixture (evaluated)
    actual: Any              # Check-type-specific
    expected: Any            # Check-type-specific
    abs_tol: float | None    # approx only
    rel_tol: float | None    # approx only
    units: str | None        # Optional unit label for numeric checks
    threshold: float         # greater/less only
    low: float               # between only
    high: float              # between only
    inclusive: bool           # between only
    # ... other check-type-specific fields
```

## Fixture Behavior

### `verify` fixture (scope: test)

1. **On each `verify.*()` call:**
   - Build descriptor dict from arguments
   - Evaluate the check (run the comparison)
   - Set `passed` field on descriptor
   - Append to internal results list
   - If reporter detected: write to `item.stash[check_results_key]`
   - Return the descriptor dict

2. **At teardown (fixture finalizer):**
   - If any result has `passed: False` → raise `ChecksFailedError`
   - `ChecksFailedError` message format: failed checks first, then passed, with `[seq]` indices

3. **Reset:** Fresh instance per test. No state bleeds between tests.

### Reporter Detection (§8 of spec)

```python
# In pytest_configure:
reporter_installed = config.pluginmanager.has_plugin("pytest-reporter")
# Store on plugin instance, check before each stash write
```

### Stash Key Convention (shared with pytest-reporter §15.1)

```python
from pytest import StashKey
check_results_key = StashKey[list]()
```

## IDE Autocompletion — CRITICAL REQUIREMENT

**Every public interface must be fully typed.** Users must get autocompletion on `verify.` in PyCharm/VS Code.

Implementation requirements:
- `Verify` class with explicit method signatures (not `**kwargs`)
- All parameters typed with `float`, `str`, `Any`, `int`, etc.
- Return type `CheckDescriptor` on all check methods
- `CheckDescriptor` as a TypedDict (not a plain dict)
- `py.typed` marker in package root
- Docstrings on all public methods
- Use `from __future__ import annotations` for `X | None` syntax on Python 3.9

## Function Catalog (20 functions)

### Equality & Approximation
| Function | check_type | Key fields |
|----------|-----------|------------|
| `verify.equal(actual, expected, *, name, units=None)` | `"equal"` | actual, expected |
| `verify.not_equal(actual, expected, *, name, units=None)` | `"not_equal"` | actual, expected |
| `verify.approx(actual, expected, *, abs_tol=None, rel_tol=None, name, units=None)` | `"approx"` | actual, expected, abs_tol, rel_tol |

### Ordering & Range
| Function | check_type | Key fields |
|----------|-----------|------------|
| `verify.greater(actual, threshold, *, name, units=None)` | `"greater"` | actual, threshold |
| `verify.greater_equal(actual, threshold, *, name, units=None)` | `"greater_equal"` | actual, threshold |
| `verify.less(actual, threshold, *, name, units=None)` | `"less"` | actual, threshold |
| `verify.less_equal(actual, threshold, *, name, units=None)` | `"less_equal"` | actual, threshold |
| `verify.between(actual, low, high, *, inclusive=True, name, units=None)` | `"between"` | actual, low, high, inclusive |

### Boolean & Identity
| Function | check_type |
|----------|-----------|
| `verify.is_true(actual, *, name)` | `"true"` |
| `verify.is_false(actual, *, name)` | `"false"` |
| `verify.is_none(actual, *, name)` | `"is_none"` |
| `verify.is_not_none(actual, *, name)` | `"is_not_none"` |

### String & Container
| Function | check_type |
|----------|-----------|
| `verify.contains(haystack, needle, *, name)` | `"contains"` |
| `verify.not_contains(haystack, needle, *, name)` | `"not_contains"` |
| `verify.matches(actual, pattern, *, name)` | `"matches"` |

### Type / Collection / Conditional
| Function | check_type | Notes |
|----------|-----------|-------|
| `verify.is_instance(actual, expected_type, *, name)` | `"is_instance"` | Store type as string in descriptor |
| `verify.length(actual, expected, *, name)` | `"length"` | Stores `actual_length` in descriptor |
| `verify.all_satisfy(items, descriptor_factory, *, name)` | `"all_satisfy"` | Factory callable invoked at call time, not stored |
| `verify.conditional(switch_value, *, cases, default=None, name)` | `"conditional"` | Only matched branch evaluated |
| `verify.fail(msg, *, name=None)` | `"fail"` | Always fails. name defaults to msg |

## Evaluation Logic

### `verify.evaluate(*descriptors) -> bool`
- Pure function, no side effects
- Returns `True` only if ALL descriptors pass
- Each descriptor evaluated independently

### `verify.evaluate_detailed(*descriptors) -> list[dict]`
- Returns list of evaluated result dicts with `passed`, `details`, `seq`, `t` fields
- Matches schema from pytest-reporter §15.3

### Evaluation rules by check_type:
- `equal`: `actual == expected`
- `not_equal`: `actual != expected`
- `approx`: `math.isclose(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol)` — at least one tolerance required, passes if either satisfied
- `greater`: `actual > threshold`
- `greater_equal`: `actual >= threshold`
- `less`: `actual < threshold`
- `less_equal`: `actual <= threshold`
- `between` (inclusive): `low <= actual <= high`
- `between` (exclusive): `low < actual < high`
- `true`: `bool(actual) is True`
- `false`: `bool(actual) is False`
- `is_none`: `actual is None`
- `is_not_none`: `actual is not None`
- `contains`: `needle in haystack`
- `not_contains`: `needle not in haystack`
- `matches`: `re.search(pattern, actual) is not None`
- `is_instance`: `isinstance(actual, expected_type)`
- `length`: `len(actual) == expected`
- `all_satisfy`: all child checks pass
- `conditional`: resolve matched case → evaluate child → parent passes if child passes
- `fail`: always False

## Description Formatting

The `description` field is generated by the assertion engine. Format conventions:

- `verify.approx(v, 3.3, abs_tol=0.05, name="Vout", units="V")` → `"Verify 'Vout' == 3.3V ± 0.05V"`
- `verify.between(v, 0.1, 0.5, name="I", units="A")` → `"Verify 'I' ∈ [0.1A, 0.5A]"`
- `verify.between(v, 0.1, 0.5, inclusive=False, name="I")` → `"Verify 'I' ∈ (0.1, 0.5)"`
- `verify.greater(v, 100, name="T", units="Mbps")` → `"Verify 'T' > 100Mbps"`
- `verify.is_true(v, name="Alive")` → `"Verify 'Alive' is True"`
- `verify.conditional(mode, name="M")` → `"Verify 'M' [mode=1]"`
- `verify.fail("msg")` → `"FAIL: msg"`

When `units` is `None`, values appear without suffix: `"Verify 'Vout' == 3.3 ± 0.05"`

## Coding Standards

- Python 3.9+ (use `from __future__ import annotations` for union syntax)
- PEP 8 with 100 character lines
- Type hints on all public APIs — this is non-negotiable for IDE autocompletion
- Docstrings (Google style) on all public methods
- pytest for testing (test the plugin itself with pytest)
- No external dependencies beyond pytest
- All descriptors must be JSON-serializable

## File Boundaries

- Safe to edit: `pytest_verify/`, `tests/`
- Never touch: `venv/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `*.egg-info/`

## Testing Strategy

- Test each check function: correct descriptor shape, correct `check_type`, correct `description` format
- Test evaluation logic: each check_type passes when it should, fails when it should
- Test `evaluate(*args)`: multiple descriptors, all-pass, any-fail
- Test `evaluate_detailed`: correct result schema
- Test fixture lifecycle: results collected, `ChecksFailedError` raised at teardown, message format
- Test reporter detection: stash written when reporter present, skipped when absent
- Test `units` parameter: present in description, absent when None
- Test `conditional`: case matching, default fallback, no-match-no-default
- Test `all_satisfy`: all pass, some fail, empty list
- Test `fail()`: always fails, name defaults to msg

## Common Pitfalls

- **Don't forget `py.typed` marker.** Without it, mypy/Pylance won't recognize the package as typed.
- **`name` is required on all checks** (except `fail` where it defaults to `msg`). Raise `TypeError` if missing.
- **`approx` needs at least one tolerance.** Raise `ValueError` if neither `abs_tol` nor `rel_tol` provided.
- **`all_satisfy` callable is invoked at call time.** The resulting `child_checks` list is stored, not the callable.
- **`conditional` cases keys are stringified.** `switch_value` is converted to string for lookup: `str(switch_value)`.
- **`is_instance` stores type as string.** The descriptor contains `"expected_type": "dict"`, not the actual type object.
- **Fixture vs module:** The fixture evaluates and stores. The module just builds descriptors. Don't mix up which does what.
- **Stash writes are conditional.** Only write to `item.stash` if reporter is detected at session start.