from __future__ import annotations

from check_sdist._compat import tomllib
from check_sdist.sdist import default_sdist_ignore


def test_default_sdist_ignore_setuptools_scm_version_file() -> None:
    pyproject_str = """
    [tool.setuptools_scm]
    version_file = "src/example/_version.py"
    """
    pyproject = tomllib.loads(pyproject_str)

    ignore = set(default_sdist_ignore(pyproject))

    assert "src/example/_version.py" in ignore


def test_default_sdist_ignore_hatch_vcs_version_file() -> None:
    pyproject_str = """
    [tool.hatch.build.hooks.vcs]
    version-file = "src/example/_version.py"
    """
    pyproject = tomllib.loads(pyproject_str)

    ignore = set(default_sdist_ignore(pyproject))

    assert "src/example/_version.py" in ignore


def test_default_sdist_ignore_scikit_build_generate_paths() -> None:
    pyproject_str = """
    [[tool.scikit-build.generate]]
    path = "src/example/_version.py"

    [[tool.scikit-build.generate]]
    template = "unused-no-path"

    [[tool.scikit-build.generate]]
    path = "python/pkg/version.py"
    """
    pyproject = tomllib.loads(pyproject_str)

    ignore = set(default_sdist_ignore(pyproject))

    assert "src/example/_version.py" in ignore
    assert "python/pkg/version.py" in ignore


def test_default_sdist_ignore_autogen_with_setuptools_defaults() -> None:
    pyproject_str = """
    [build-system]
    build-backend = "setuptools.build_meta"

    [tool.setuptools_scm]
    version_file = "src/example/_version.py"
    """
    pyproject = tomllib.loads(pyproject_str)

    ignore = set(default_sdist_ignore(pyproject))

    assert "*.dist-info" in ignore
    assert "*.egg-info" in ignore
    assert "setup.cfg" in ignore
    assert "src/example/_version.py" in ignore
