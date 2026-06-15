from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import glob_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["MaturinBackend"]


def __dir__() -> list[str]:
    return __all__


class MaturinBackend:
    """SDist knowledge for the maturin build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("maturin",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = pyproject.get("tool", {}).get("maturin", {}).get("exclude", [])
        return glob_filter(exclude, files, source_dir)

    def sdist_only_ignores(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any]
    ) -> Iterator[str]:
        yield from ()
