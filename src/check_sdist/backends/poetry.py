from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import glob_filter, include_exclude_suggestion

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["PoetryBackend"]


def __dir__() -> list[str]:
    return __all__


class PoetryBackend:
    """SDist knowledge for the poetry-core build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("poetry.core.masonry.api",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = [
            x if isinstance(x, str) else x["path"]
            for x in pyproject.get("tool", {}).get("poetry", {}).get("exclude", [])
            if isinstance(x, str) or "sdist" in x.get("format", ["sdist"])
        ]
        return glob_filter(exclude, files, source_dir)

    def sdist_only_ignores(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any]
    ) -> Iterator[str]:
        yield from ()

    def suggestion(  # pylint: disable=unused-argument
        self,
        pyproject: dict[str, Any],
        sdist_only: frozenset[str],
        git_only: frozenset[str],
    ) -> str | None:
        return include_exclude_suggestion(
            "tool.poetry.include",
            "tool.poetry.exclude",
            sdist_only,
            git_only,
        )
