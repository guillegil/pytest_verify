from __future__ import annotations

from typing import Any, Callable, Dict, List, Union

# Type aliases used across the package
Numeric = Union[int, float]
DescriptorFactory = Callable[[Any], "CheckDescriptor"]

# Re-exported for convenience; the canonical definition lives in _descriptors.py
# to avoid circular imports.  Importing CheckDescriptor here would create a cycle,
# so consumers should import it from _descriptors directly.
