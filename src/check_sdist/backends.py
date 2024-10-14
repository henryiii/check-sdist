from __future__ import annotations

from pathlib import Path
from typing import Any

import pathspec


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
        for pattern in exclude:
            results = {str(p.as_posix()) for p in Path().glob(pattern)}
            files = files - results
        return files
    if backend_resolved == "hatchling.build":
        exclude = (
            pyproject.get("tool", {})
            .get("hatch", {})
            .get("build", {})
            .get("targets", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        sdist_spec = pathspec.GitIgnoreSpec.from_lines(exclude)
        return frozenset(p for p in files if not sdist_spec.match_file(p))
    if backend_resolved == "scikit_build_core.build":
        exclude = (
            pyproject.get("tool", {})
            .get("scikit-build", {})
            .get("sdist", {})
            .get("exclude", [])
        )
        sdist_spec = pathspec.GitIgnoreSpec.from_lines(exclude)
        return frozenset(p for p in files if not sdist_spec.match_file(p))
    if backend_resolved == "pdm.backend":
        exclude = (
            pyproject.get("tool", {})
            .get("pdm", {})
            .get("build", {})
            .get("excludes", [])
        )
        for pattern in exclude:
            results = {str(p) for p in Path().glob(pattern)}
            files = files - results
        return files
    if backend_resolved == "poetry.core.masonry.api":
        exclude = [
            x if isinstance(x, str) else x["path"]
            for x in pyproject.get("tool", {}).get("poetry", {}).get("exclude", [])
            if isinstance(x, str) or "sdist" in x.get("format", ["sdist"])
        ]
        for pattern in exclude:
            results = {str(p) for p in Path().glob(pattern)}
            files = files - results
    if backend_resolved == "maturin":
        exclude = pyproject.get("tool", {}).get("maturin", {}).get("exclude", [])
        for pattern in exclude:
            results = {str(p) for p in Path().glob(pattern)}
            files = files - results
        return files
    if backend != "auto":
        msg = f"Unknown backend: {backend} - please add support in check_dist.backends"
        raise ValueError(msg)
    return files
