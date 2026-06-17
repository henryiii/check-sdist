from __future__ import annotations

__lazy_modules__ = [
    f"{__spec__.parent}._base",
    "functools",
    "importlib.metadata",
    "sys",
    "typing",
]

import functools
import importlib.metadata
import sys
from typing import Any

from ._base import (
    Backend,
    SuggestingBackend,
    glob_filter,
    pathspec_filter,
    vcs_suggestion,
)

__all__ = [
    "Backend",
    "SuggestingBackend",
    "glob_filter",
    "load_backends",
    "pathspec_filter",
    "resolve_backend",
    "vcs_suggestion",
]

GROUP = "check_sdist.backends"
DEFAULT_BUILD_BACKEND = "setuptools.build_meta.__legacy__"


def __dir__() -> list[str]:
    return __all__


@functools.cache
def load_backends() -> dict[str, Backend]:
    """Map entry-point name (a build-backend string) to a Backend instance."""
    if sys.version_info >= (3, 10):
        eps = importlib.metadata.entry_points(group=GROUP)
    else:  # 3.9 has no group= kwarg; entry_points() returns a dict by group
        eps = importlib.metadata.entry_points().get(GROUP, [])  # pylint: disable=no-member
    return {ep.name: ep.load()() for ep in eps}


def resolve_backend(selector: str, pyproject: dict[str, Any]) -> Backend:
    """Resolve the check-sdist ``build-backend`` selector to a Backend.

    ``"none"`` selects the no-op default backend (no backend-specific logic).
    ``"auto"`` matches the project's ``build-system.build-backend``, falling
    back to ``"none"`` if unrecognized. Any other value selects a registered
    backend by name (or declared alias), raising ValueError if unknown.
    """
    backends = load_backends()

    if selector == "auto":
        build_backend = pyproject.get("build-system", {}).get(
            "build-backend", DEFAULT_BUILD_BACKEND
        )
        for backend in backends.values():
            if build_backend in backend.build_backends:
                return backend
        return backends["none"]

    if selector in backends:
        return backends[selector]
    for backend in backends.values():
        if selector in backend.build_backends:
            return backend

    msg = f"Unknown backend: {selector} - request addition in check_sdist.backends or make a plugin"
    raise ValueError(msg)
