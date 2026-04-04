"""pytest-verify — soft assertions for pytest.

Usage as a **pytest fixture** (primary API)::

    def test_example(verify):
        verify.approx(3.28, 3.3, abs_tol=0.05, name="Vout", units="V")
        verify.greater(100, 50, name="Throughput", units="Mbps")

Usage as a **module** (secondary API)::

    from pytest_verify import verify

    desc = verify.approx(3.28, 3.3, abs_tol=0.05, name="Vout", units="V")
    assert verify.evaluate(desc)
"""
from __future__ import annotations

from ._descriptors import CheckDescriptor
from ._verify import Verify

__all__ = ["CheckDescriptor", "Verify", "verify"]

#: Module-level ``Verify`` instance.  Returns unevaluated descriptors.
verify: Verify = Verify()
