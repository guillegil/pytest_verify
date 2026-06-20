"""Unit tests for the ``ChecksFailedError`` message format (spec §7).

The normative structure is asserted here: the ``N of M checks failed`` header,
the ``✗``/``✓`` markers, the ``[seq]`` index, the check name, and failed-before-passed
ordering. The exact ``expected … got …`` wording is intentionally NOT pinned — it is
rendered uniformly from each descriptor's canonical ``description``.
"""

from pytest_verify._descriptors import build_between, build_equal, build_greater
from pytest_verify._exceptions import ChecksFailedError


def _evaluated(builder, *args, passed, **kwargs):
    d = builder(*args, **kwargs)
    d["passed"] = passed
    return d


class TestChecksFailedErrorMessage:
    def test_header_counts_failed_over_total(self):
        results = [
            _evaluated(build_equal, 1, 1, name="A", passed=True),
            _evaluated(build_equal, 1, 2, name="B", passed=False),
            _evaluated(build_equal, 3, 3, name="C", passed=True),
        ]
        msg = str(ChecksFailedError(results))
        assert msg.startswith("1 of 3 checks failed")

    def test_failed_marker_and_index_and_name(self):
        results = [
            _evaluated(build_equal, 1, 1, name="Pass1", passed=True),
            _evaluated(build_greater, 1, 5, name="Fail1", passed=False),
        ]
        msg = str(ChecksFailedError(results))
        assert "✗ [1] Fail1" in msg
        assert "✓ [0] Pass1" in msg

    def test_failed_listed_before_passed(self):
        results = [
            _evaluated(build_equal, 1, 1, name="GoodOne", passed=True),
            _evaluated(build_between, 9, 0, 1, name="BadOne", passed=False),
        ]
        msg = str(ChecksFailedError(results))
        assert msg.index("BadOne") < msg.index("GoodOne")

    def test_failed_detail_shows_actual_value(self):
        results = [_evaluated(build_greater, 3, 100, name="Throughput", units="Mbps", passed=False)]
        msg = str(ChecksFailedError(results))
        # The actual measured value must appear so the failure is diagnosable.
        assert "got 3Mbps" in msg

    def test_no_old_section_headers(self):
        results = [_evaluated(build_equal, 1, 2, name="X", passed=False)]
        msg = str(ChecksFailedError(results))
        assert "FAILED checks:" not in msg
        assert "PASSED checks:" not in msg
