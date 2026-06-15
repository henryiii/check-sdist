from __future__ import annotations

__lazy_modules__ = ["typing"]

from typing import Any, ClassVar

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["SetuptoolsBackend"]


def __dir__() -> list[str]:
    return __all__


class SetuptoolsBackend:
    """SDist knowledge for the setuptools build backend."""

    build_backends: ClassVar[tuple[str, ...]] = (
        "setuptools.build_meta",
        "setuptools.build_meta.__legacy__",
    )

    def git_only_excludes(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        # No excludes today; the future home for reading MANIFEST.in / setup.cfg.
        return files

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        yield "*.egg-info"
        yield "setup.cfg"

        # [tool.setuptools_scm]
        # version-file = "_version.py"
        version_file = (
            pyproject.get("tool", {})
            .get("setuptools_scm", {})
            .get("version_file", None)
        )
        if version_file is not None:
            yield version_file
