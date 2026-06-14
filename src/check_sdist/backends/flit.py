from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import BaseBackend, glob_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["FlitBackend"]


def __dir__() -> list[str]:
    return __all__


class FlitBackend(BaseBackend):
    """SDist knowledge for the flit-core build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("flit_core.buildapi",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = (
            pyproject.get("tool", {})
            .get("flit", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return glob_filter(exclude, files, source_dir)
