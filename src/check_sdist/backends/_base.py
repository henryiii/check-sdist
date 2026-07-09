from __future__ import annotations

__lazy_modules__ = ["pathlib", "pathspec", "typing"]

from pathlib import Path
from typing import Any, ClassVar, Protocol, runtime_checkable

import pathspec

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "Backend",
    "SuggestingBackend",
    "glob_filter",
    "include_exclude_suggestion",
    "pathspec_filter",
]


def __dir__() -> list[str]:
    return __all__


@runtime_checkable
class Backend(Protocol):
    """A build backend's knowledge of what belongs in its SDist.

    Backends are structural: a plugin just needs these attributes, it does not
    need to import or subclass anything from check-sdist. A backend that has no
    excludes returns ``files`` unchanged; one with no generated files yields
    nothing.
    """

    #: The build-system.build-backend strings this plugin claims, used for
    #: "auto" detection. A backend may claim several (e.g. setuptools).
    build_backends: ClassVar[tuple[str, ...]]

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        """Drop files the backend intentionally keeps out of the SDist."""

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        """Yield patterns expected in the SDist but absent from git."""


@runtime_checkable
class SuggestingBackend(Protocol):
    """Optional backend hook: advise the user how to resolve a mismatch.

    A backend may implement ``suggestion`` in addition to the :class:`Backend`
    protocol. When the SDist and git disagree, check-sdist calls it with the
    unresolved ``sdist_only`` and ``git_only`` sets and prints whatever text it
    returns. Return ``None`` (or an empty string) to stay silent.
    """

    def suggestion(
        self,
        pyproject: dict[str, Any],
        sdist_only: frozenset[str],
        git_only: frozenset[str],
    ) -> str | None:
        """Return advice for resolving the mismatch, or None for no advice."""


def glob_filter(
    patterns: list[str], files: frozenset[str], source_dir: Path
) -> frozenset[str]:
    """Filter out files based on glob patterns, relative to source_dir."""
    new_files = set(files)
    for pattern in patterns:
        results = {
            p.relative_to(source_dir).as_posix() for p in Path(source_dir).glob(pattern)
        }
        new_files -= results
    return frozenset(new_files)


def pathspec_filter(patterns: list[str], files: frozenset[str]) -> frozenset[str]:
    """Filter out files based on gitignore-style patterns."""
    spec = pathspec.GitIgnoreSpec.from_lines(patterns)
    return frozenset(p for p in files if not spec.match_file(p))


def include_exclude_suggestion(
    include_setting: str,
    exclude_setting: str,
    sdist_only: frozenset[str],
    git_only: frozenset[str],
) -> str | None:
    """Build a suggestion naming a backend's include/exclude settings.

    ``include_setting`` and ``exclude_setting`` are the dotted pyproject keys a
    user edits to add or drop files (e.g.
    ``"tool.hatch.build.targets.sdist.include"``). Returns None if there is
    nothing to suggest.
    """
    lines = []
    if git_only:
        lines.append(
            "  Files tracked by git are missing from the SDist. Add them to "
            f"{include_setting}, or check that {exclude_setting} is not dropping "
            "them."
        )
    if sdist_only:
        lines.append(
            "  Files in the SDist are not tracked by git. Commit them, drop them "
            f"via {exclude_setting}, or list them under [tool.check-sdist] "
            "sdist-only."
        )
    return "\n".join(lines) or None
