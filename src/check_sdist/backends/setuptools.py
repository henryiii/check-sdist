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

    def suggestion(  # pylint: disable=unused-argument
        self,
        pyproject: dict[str, Any],
        sdist_only: frozenset[str],
        git_only: frozenset[str],
    ) -> str | None:
        lines = []
        if git_only:
            lines.append(
                "  Files tracked by git are missing from the SDist. setuptools "
                "only ships what MANIFEST.in (and a few defaults) select; add "
                "them with `include`/`graft`, or adopt setuptools-scm, which "
                "ships every git-tracked file automatically."
            )
        if sdist_only:
            lines.append(
                "  Files in the SDist are not tracked by git. Commit them, drop "
                "them with `prune`/`exclude` in MANIFEST.in, or list them under "
                "[tool.check-sdist] sdist-only."
            )
        return "\n".join(lines) or None
