# pytest-verify

A pytest plugin providing **soft assertions** for test verification. Failed checks never stop
the test — all checks run to completion, and failures are reported together at test end.

## Installation

```bash
pip install pytest-verify
```

Requires Python 3.9+ and pytest 7+.

## Quick Start

Use the `verify` fixture in any test — no imports needed:

```python
def test_power_supply(verify):
    verify.approx(measured_voltage, 3.3, abs_tol=0.05, name="Vout", units="V")
    verify.greater(throughput, 100, name="Throughput", units="Mbps")
    verify.between(current, 0.1, 0.5, name="Icc", units="A")
```

If any check fails, the test continues running. At the end, all failures are
reported together in a single `ChecksFailedError`.

## Failure Output

When one or more checks fail, the test is reported as **failed** with a summary
listing the failed checks (`✗`) before the passed ones (`✓`), each with its index,
name, and an `expected … got …` detail:

```text
1 of 3 checks failed

  ✗ [1] Vout — expected 3.3V ± 0.05V, got 3.8V

  ✓ [0] PSU stable — True
  ✓ [2] Throughput — 120Mbps > 100Mbps
```

## Check Functions

### Equality & Approximation

| Function | Description |
|----------|-------------|
| `verify.equal(actual, expected, *, name, units=None)` | `actual == expected` |
| `verify.not_equal(actual, expected, *, name, units=None)` | `actual != expected` |
| `verify.approx(actual, expected, *, abs_tol=None, rel_tol=None, name, units=None)` | Approximate equality (at least one tolerance required) |

### Ordering & Range

| Function | Description |
|----------|-------------|
| `verify.greater(actual, threshold, *, name, units=None)` | `actual > threshold` |
| `verify.greater_equal(actual, threshold, *, name, units=None)` | `actual >= threshold` |
| `verify.less(actual, threshold, *, name, units=None)` | `actual < threshold` |
| `verify.less_equal(actual, threshold, *, name, units=None)` | `actual <= threshold` |
| `verify.between(actual, low, high, *, inclusive=True, name, units=None)` | Value within range |

### Boolean & Identity

| Function | Description |
|----------|-------------|
| `verify.is_true(actual, *, name)` | `bool(actual) is True` |
| `verify.is_false(actual, *, name)` | `bool(actual) is False` |
| `verify.is_none(actual, *, name)` | `actual is None` |
| `verify.is_not_none(actual, *, name)` | `actual is not None` |

### String & Container

| Function | Description |
|----------|-------------|
| `verify.contains(haystack, needle, *, name)` | `needle in haystack` |
| `verify.not_contains(haystack, needle, *, name)` | `needle not in haystack` |
| `verify.matches(actual, pattern, *, name)` | Regex search matches |

### Type, Collection & Conditional

| Function | Description |
|----------|-------------|
| `verify.is_instance(actual, expected_type, *, name)` | `isinstance(actual, expected_type)` |
| `verify.length(actual, expected, *, name)` | `len(actual) == expected` |
| `verify.all_satisfy(items, descriptor_factory, *, name)` | All items pass factory check |
| `verify.conditional(switch_value, *, cases, default=None, name)` | Branch-based check |
| `verify.fail(msg, *, name=None)` | Unconditional failure |

## Usage Examples

Most checks read like their table entry — `verify.equal(status, 200, name="Status")`.
The ones below take a little more setup.

### `conditional` — pick one branch by a switch value

Only the branch whose key matches `switch_value` is evaluated. Use `default` for the
no-match case. Keys can be ints, strings, or enums — they are normalized internally, so
`cases={0: ..., 1: ...}` and `cases={"0": ..., "1": ...}` behave the same.

```python
def test_output_by_mode(verify):
    verify.conditional(
        mode,                       # e.g. 0, 1, or 2
        name="Output voltage",
        cases={
            0: verify.approx(output, 0.0, abs_tol=0.01, name="Standby", units="V"),
            1: verify.approx(output, 3.3, abs_tol=0.1, name="Active", units="V"),
            2: verify.approx(output, 5.0, abs_tol=0.1, name="Boost", units="V"),
        },
        default=verify.fail(f"Unknown mode: {mode}"),
    )
```

### `all_satisfy` — apply one check to every item

The factory is called once per item to build a child check; the parent passes only if
**all** children pass.

```python
def test_all_channels(verify):
    verify.all_satisfy(
        channel_voltages,                                  # e.g. [3.31, 3.29, 3.30]
        lambda v: verify.between(v, 3.2, 3.4, name="Channel", units="V"),
        name="All channels within spec",
    )
```

### `is_instance` — type check

```python
verify.is_instance(response, dict, name="Response is a dict")
```

### `fail` — force a failure

Useful as the `default` branch of a `conditional`, or to mark an unreachable path.
`name` defaults to the message.

```python
verify.fail(f"Unexpected state: {state}")
```

## Module-Level API

For building descriptors outside of tests (e.g., in helper functions):

```python
from pytest_verify import verify

descriptor = verify.approx(3.28, 3.3, abs_tol=0.05, name="Vout")
result = verify.evaluate(descriptor)       # True / False
details = verify.evaluate_detailed(descriptor)  # [{passed, details, seq, t}]
```

## Reporter Integration

If `pytest-reporter` is installed, check results are automatically written to `item.stash`
for rich HTML rendering. No configuration needed — detection is automatic.

## License

MIT
