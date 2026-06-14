from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}._base", "typing"]

from typing import Any, ClassVar

from ._base import BaseBackend

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["SetuptoolsBackend"]


def __dir__() -> list[str]:
    return __all__


class SetuptoolsBackend(BaseBackend):
    """SDist knowledge for the setuptools build backend."""

    # git_only_excludes is inherited (no-op); this is the future home for
    # reading MANIFEST.in / setup.cfg sdist instructions.
    build_backends: ClassVar[tuple[str, ...]] = (
        "setuptools.build_meta",
        "setuptools.build_meta.__legacy__",
    )

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
