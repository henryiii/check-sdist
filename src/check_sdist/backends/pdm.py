from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "pathlib", "typing"]

from typing import Any, ClassVar

from ._base import BaseBackend, glob_filter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["PdmBackend"]


def __dir__() -> list[str]:
    return __all__


class PdmBackend(BaseBackend):
    build_backends: ClassVar[tuple[str, ...]] = ("pdm.backend",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        exclude = (
            pyproject.get("tool", {})
            .get("pdm", {})
            .get("build", {})
            .get("excludes", [])
        )
        return glob_filter(exclude, files, source_dir)

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        # [tool.pdm.version]
        # write_to = "_version.py"
        write_to = (
            pyproject.get("tool", {})
            .get("pdm", {})
            .get("version", {})
            .get("write_to", None)
        )
        if write_to is not None:
            yield write_to
