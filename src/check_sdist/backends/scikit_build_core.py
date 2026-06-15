from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import pathspec_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["ScikitBuildCoreBackend"]


def __dir__() -> list[str]:
    return __all__


class ScikitBuildCoreBackend:
    """SDist knowledge for the scikit-build-core build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("scikit_build_core.build",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = (
            pyproject.get("tool", {})
            .get("scikit-build", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return pathspec_filter(exclude, files)

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        # [[tool.scikit-build.generate]]
        # path = "_version.py"
        for entry in (
            pyproject.get("tool", {}).get("scikit-build", {}).get("generate", [])
        ):
            path = entry.get("path", None)
            if path is not None:
                yield path
