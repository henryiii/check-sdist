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

from ._base import Backend, BaseBackend, glob_filter, pathspec_filter

__all__ = [
    "Backend",
    "BaseBackend",
    "glob_filter",
    "load_backends",
    "pathspec_filter",
    "resolve_backend",
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
        eps = importlib.metadata.entry_points().get(GROUP, [])
    return {ep.name: ep.load()() for ep in eps}


def resolve_backend(selector: str, pyproject: dict[str, Any]) -> Backend | None:
    """Resolve the check-sdist ``build-backend`` selector to a Backend.

    ``"none"`` returns None (skip backend logic). ``"auto"`` matches the
    project's ``build-system.build-backend`` and returns None if unrecognized.
    Any other value selects a registered backend by name (or declared alias),
    raising ValueError if unknown.
    """
    if selector == "none":
        return None

    backends = load_backends()

    if selector == "auto":
        build_backend = pyproject.get("build-system", {}).get(
            "build-backend", DEFAULT_BUILD_BACKEND
        )
        for backend in backends.values():
            if build_backend in backend.build_backends:
                return backend
        return None

    if selector in backends:
        return backends[selector]
    for backend in backends.values():
        if selector in backend.build_backends:
            return backend

    msg = f"Unknown backend: {selector} - please add support in check_sdist.backends"
    raise ValueError(msg)
