from __future__ import annotations

from pathlib import Path
from typing import Any

import pathspec

__all__ = ["backend_ignored_patterns"]


def __dir__() -> list[str]:
    return __all__


def glob_filter(patterns: list[str], files: frozenset[str]) -> frozenset[str]:
    """
    Filter out files based on glob patterns.
    """
    new_files = set(files)
    for pattern in patterns:
        results = {str(p.as_posix()) for p in Path().glob(pattern)}
        new_files -= results
    return frozenset(new_files)


def pathspec_filter(patterns: list[str], files: frozenset[str]) -> frozenset[str]:
    """
    Filter out files based on gitignore-style patterns.
    """
    spec = pathspec.GitIgnoreSpec.from_lines(patterns)
    return frozenset(p for p in files if not spec.match_file(p))


def backend_ignored_patterns(
    backend: str, pyproject: dict[str, Any], files: frozenset[str]
) -> frozenset[str]:
    """
    Return the ignored patterns for the given backend. If the generator is
    "none", then no patterns are ignored. If the generator is "auto", then the
    value is read from the pyproject.toml file. Any recognized backend can also
    be specified directly.
    """

    if backend == "none":
        return files

    backend_resolved = (
        pyproject.get("build-system", {}).get(
            "build-backend", "setuptools.build_meta.__legacy__"
        )
        if backend == "auto"
        else backend
    )

    if backend_resolved == "flit_core.buildapi":
        exclude = (
            pyproject.get("tool", {})
            .get("flit", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return glob_filter(exclude, files)
    if backend_resolved == "hatchling.build":
        exclude = (
            pyproject.get("tool", {})
            .get("hatch", {})
            .get("build", {})
            .get("targets", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return pathspec_filter(exclude, files)
    if backend_resolved == "scikit_build_core.build":
        exclude = (
            pyproject.get("tool", {})
            .get("scikit-build", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        return pathspec_filter(exclude, files)
    if backend_resolved == "pdm.backend":
        exclude = (
            pyproject.get("tool", {})
            .get("pdm", {})
            .get("build", {})
            .get("excludes", [])
        )
        return glob_filter(exclude, files)
    if backend_resolved == "poetry.core.masonry.api":
        exclude = [
            x if isinstance(x, str) else x["path"]
            for x in pyproject.get("tool", {}).get("poetry", {}).get("exclude", [])
            if isinstance(x, str) or "sdist" in x.get("format", ["sdist"])
        ]
        return glob_filter(exclude, files)
    if backend_resolved == "maturin":
        exclude = pyproject.get("tool", {}).get("maturin", {}).get("exclude", [])
        return glob_filter(exclude, files)
    if backend != "auto":
        msg = f"Unknown backend: {backend} - please add support in check_dist.backends"
        raise ValueError(msg)
    return files
