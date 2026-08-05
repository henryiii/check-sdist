from __future__ import annotations

__lazy_modules__ = ["typing"]

from typing import Any, ClassVar

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
        return files

    def sdist_only_ignores(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any]
    ) -> Iterator[str]:
        # uv keeps a copy of the unmodified pyproject.toml in the SDist.
        yield "pyproject.toml.orig"
