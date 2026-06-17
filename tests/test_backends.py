from __future__ import annotations

import pytest

from check_sdist._compat import tomllib
from check_sdist.backends import (
    SuggestingBackend,
    include_exclude_suggestion,
    load_backends,
    resolve_backend,
)
from check_sdist.backends.hatchling import HatchlingBackend
from check_sdist.backends.none import NoneBackend
from check_sdist.backends.pdm import PdmBackend
from check_sdist.backends.scikit_build_core import ScikitBuildCoreBackend
from check_sdist.backends.setuptools import SetuptoolsBackend

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path


def test_glob_backend_excludes_relative_to_source_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Glob-based backend excludes must resolve against source_dir, not cwd."""
    source_dir = tmp_path / "project"
    source_dir.mkdir()
    (source_dir / "junk.txt").touch()
    (source_dir / "keep.py").touch()

    # Run from an unrelated directory: cwd-relative globbing would never match
    # the excluded file living under source_dir.
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    pyproject = tomllib.loads(
        """
        [build-system]
        build-backend = "pdm.backend"

        [tool.pdm.build]
        excludes = ["junk.txt"]
        """
    )
    files = frozenset({"junk.txt", "keep.py"})

    backend = resolve_backend("auto", pyproject)
    result = backend.git_only_excludes(pyproject, files, source_dir)

    assert "junk.txt" not in result
    assert "keep.py" in result


def test_load_backends_contains_builtins() -> None:
    names = set(load_backends())
    assert {
        "none",
        "setuptools.build_meta",
        "flit_core.buildapi",
        "hatchling.build",
        "scikit_build_core.build",
        "pdm.backend",
        "poetry.core.masonry.api",
        "maturin",
    } <= names


def test_resolve_auto_defaults_to_setuptools() -> None:
    assert isinstance(resolve_backend("auto", {}), SetuptoolsBackend)


@pytest.mark.parametrize(
    "build_backend",
    ["setuptools.build_meta", "setuptools.build_meta.__legacy__"],
)
def test_resolve_setuptools_aliases(build_backend: str) -> None:
    pyproject = {"build-system": {"build-backend": build_backend}}
    assert isinstance(resolve_backend("auto", pyproject), SetuptoolsBackend)


def test_resolve_none_returns_none_backend() -> None:
    assert isinstance(resolve_backend("none", {}), NoneBackend)


def test_resolve_auto_unknown_falls_back_to_none() -> None:
    pyproject = {"build-system": {"build-backend": "mystery.backend"}}
    assert isinstance(resolve_backend("auto", pyproject), NoneBackend)


def test_resolve_unknown_explicit_raises() -> None:
    with pytest.raises(ValueError, match="Unknown backend: unknown"):
        resolve_backend("unknown", {})


def test_setuptools_scm_version_file() -> None:
    pyproject = tomllib.loads(
        """
        [tool.setuptools_scm]
        version_file = "src/example/_version.py"
        """
    )
    ignore = set(SetuptoolsBackend().sdist_only_ignores(pyproject))
    assert "src/example/_version.py" in ignore
    assert "*.egg-info" in ignore
    assert "setup.cfg" in ignore


def test_hatch_vcs_version_file() -> None:
    pyproject = tomllib.loads(
        """
        [tool.hatch.build.hooks.vcs]
        version-file = "src/example/_version.py"
        """
    )
    ignore = set(HatchlingBackend().sdist_only_ignores(pyproject))
    assert "src/example/_version.py" in ignore


def test_pdm_version_write_to() -> None:
    pyproject = tomllib.loads(
        """
        [tool.pdm.version]
        write_to = "foo/_version.py"
        """
    )
    ignore = set(PdmBackend().sdist_only_ignores(pyproject))
    assert "foo/_version.py" in ignore


def test_scikit_build_generate_paths() -> None:
    pyproject = tomllib.loads(
        """
        [[tool.scikit-build.generate]]
        path = "src/example/_version.py"

        [[tool.scikit-build.generate]]
        template = "unused-no-path"

        [[tool.scikit-build.generate]]
        path = "python/pkg/version.py"
        """
    )
    ignore = set(ScikitBuildCoreBackend().sdist_only_ignores(pyproject))
    assert "src/example/_version.py" in ignore
    assert "python/pkg/version.py" in ignore


def test_suggesting_backend_is_optional() -> None:
    """The suggestion hook is opt-in: NoneBackend does not provide it."""
    assert not isinstance(NoneBackend(), SuggestingBackend)
    assert isinstance(SetuptoolsBackend(), SuggestingBackend)
    assert isinstance(HatchlingBackend(), SuggestingBackend)


def test_include_exclude_suggestion_empty_returns_none() -> None:
    assert (
        include_exclude_suggestion(
            "tool.x.include", "tool.x.exclude", frozenset(), frozenset()
        )
        is None
    )


def test_include_exclude_suggestion_names_both_settings() -> None:
    git_only = include_exclude_suggestion(
        "tool.x.include", "tool.x.exclude", frozenset(), frozenset({"a.py"})
    )
    assert git_only is not None
    assert "missing from the SDist" in git_only
    assert "tool.x.include" in git_only
    assert "tool.x.exclude" in git_only

    sdist_only = include_exclude_suggestion(
        "tool.x.include", "tool.x.exclude", frozenset({"b.py"}), frozenset()
    )
    assert sdist_only is not None
    assert "tool.x.exclude" in sdist_only
    assert "sdist-only" in sdist_only


def test_setuptools_suggestion() -> None:
    backend = SetuptoolsBackend()

    git_only = backend.suggestion({}, frozenset(), frozenset({"data.txt"}))
    assert git_only is not None
    assert "MANIFEST.in" in git_only
    assert "setuptools-scm" in git_only

    sdist_only = backend.suggestion({}, frozenset({"junk.txt"}), frozenset())
    assert sdist_only is not None
    assert "sdist-only" in sdist_only

    assert backend.suggestion({}, frozenset(), frozenset()) is None


def test_hatchling_suggestion_names_its_settings() -> None:
    advice = HatchlingBackend().suggestion(
        {}, frozenset({"junk.txt"}), frozenset({"data.txt"})
    )
    assert advice is not None
    assert "tool.hatch.build.targets.sdist.include" in advice
    assert "tool.hatch.build.targets.sdist.exclude" in advice
