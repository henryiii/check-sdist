from __future__ import annotations

__lazy_modules__ = ["typing"]

from typing import Any, ClassVar

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["NoneBackend"]


def __dir__() -> list[str]:
    return __all__


class NoneBackend:
    """The default backend: no backend-specific SDist knowledge.

    Used when no backend is selected or "auto" detection finds no match. It
    claims no ``build-backend`` strings, so it never wins auto detection; it is
    only reached as an explicit "none" selection or the fallback.
    """

    build_backends: ClassVar[tuple[str, ...]] = ()

    def git_only_excludes(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        return files

    def sdist_only_ignores(  # pylint: disable=unused-argument
        self, pyproject: dict[str, Any]
    ) -> Iterator[str]:
        yield from ()
