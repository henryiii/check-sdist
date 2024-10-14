from __future__ import annotations

import inspect
import os
import subprocess
from pathlib import Path

import pytest

from check_sdist.__main__ import compare
from check_sdist.inject import inject_junk_files

DIR = Path(__file__).parent


def get_all_files(path: Path) -> frozenset[str]:
    with os.scandir(path) as it:
        return frozenset(it.name for it in it if not it.name.startswith(".coverage"))


def test_self_dir():
    start = get_all_files(DIR.parent)
    assert compare(DIR.parent, isolated=True) == 0
    end = get_all_files(DIR.parent)
    assert start == end


def test_self_dir_injected():
    start = get_all_files(DIR.parent)
    with inject_junk_files(DIR.parent):
        assert compare(DIR.parent, isolated=True) == 0
    end = get_all_files(DIR.parent)
    assert start == end


@pytest.fixture
def git_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], check=True)
    subprocess.run(["git", "config", "user.name", "CI"], check=True)
    return tmp_path


@pytest.mark.usefixtures("git_dir")
@pytest.mark.parametrize("backend", ["auto", "none"])
def test_hatchling(backend: str):
    Path("pyproject.toml").write_text(
        inspect.cleandoc(f"""
            [build-system]
            requires = ["hatchling"]
            build-backend = "hatchling.build"

            [project]
            name = "hatchling-test"
            version = "0.1.0"

            [tool.hatch]
            build.targets.sdist.exclude = ["ignore*", "some-file", "**/notme.txt"]

            [tool.check-sdist]
            build-backend = "{backend}"
        """)
    )
    Path(".gitignore").write_text(
        inspect.cleandoc("""
        some-ignored-file.txt
    """)
    )
    Path("ignore-me.txt").touch()
    Path("not-ignored.txt").touch()
    Path("some-file").touch()
    Path("some-dir").mkdir()
    Path("some-dir/notme.txt").touch()
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    Path("some-ignored-file.txt").touch()
    assert compare(Path(), isolated=True, verbose=True) == (
        0 if backend == "auto" else 2
    )


@pytest.mark.usefixtures("git_dir")
@pytest.mark.parametrize("backend", ["auto", "none"])
def test_flit_core(backend: str):
    Path("pyproject.toml").write_text(
        inspect.cleandoc(f"""
            [build-system]
            requires = ["flit-core"]
            build-backend = "flit_core.buildapi"

            [project]
            name = "flit-core-test"
            version = "0.1.0"
            description = "A test package"

            [tool.flit.sdist]
            include = ["not-ignored.txt", ".gitignore"]
            exclude = ["ignore*", "some-file", "**/notme.txt"]

            [tool.check-sdist]
            build-backend = "{backend}"
        """)
    )
    Path(".gitignore").write_text(
        inspect.cleandoc("""
        some-ignored-file.txt
    """)
    )
    Path("ignore-me.txt").touch()
    Path("not-ignored.txt").touch()
    Path("some-file").touch()
    Path("some-dir").mkdir()
    Path("some-dir/notme.txt").touch()
    Path("flit_core_test").mkdir()
    Path("flit_core_test/__init__.py").touch()
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    Path("some-ignored-file.txt").touch()
    assert compare(Path(), isolated=True, verbose=True) == (
        0 if backend == "auto" else 2
    )
