from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "typing"]

from typing import Any, ClassVar

from ._base import pathspec_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["UvBackend"]


def __dir__() -> list[str]:
    return __all__


class UvBackend:
    """SDist knowledge for the uv build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("uv_build",)

    def git_only_excludes(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        settings = pyproject.get("tool", {}).get("uv", {}).get("build-backend", {})
        excludes = list(settings.get("source-exclude", []))
        if settings.get("default-excludes", True):
            excludes += ["__pycache__", "*.pyc", "*.pyo"]
        # uv excludes are unanchored unless prefixed with "/"; valid uv globs
        # can't contain gitignore's "!"/"#" specials, so the translation to
        # gitignore patterns is exact.
        patterns = [p if p.startswith("/") else f"**/{p}" for p in excludes]
        return pathspec_filter(patterns, files)

    def sdist_only_ignores(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any]
    ) -> Iterator[str]:
        # uv keeps a copy of the unmodified pyproject.toml in the SDist.
        yield "pyproject.toml.orig"
