from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import BaseBackend, pathspec_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["HatchlingBackend"]


def __dir__() -> list[str]:
    return __all__


class HatchlingBackend(BaseBackend):
    """SDist knowledge for the hatchling build backend."""

    build_backends: ClassVar[tuple[str, ...]] = ("hatchling.build",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = (
            pyproject.get("tool", {})
            .get("hatch", {})
            .get("build", {})
            .get("targets", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return pathspec_filter(exclude, files)

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        # [tool.hatch.build.hooks.vcs]
        # version-file = "_version.py"
        version_file = (
            pyproject.get("tool", {})
            .get("hatch", {})
            .get("build", {})
            .get("hooks", {})
            .get("vcs", {})
            .get("version-file", None)
        )
        if version_file is not None:
            yield version_file
