from __future__ import annotations

from pathlib import Path

from check_sdist.inject import inject_files, inject_junk_files


def test_inject_files(tmp_path: Path):
    with inject_files(tmp_path, ["a", "b", "c/", "d/e", "f/g/"]):
        assert {x.name for x in tmp_path.iterdir()} == {"a", "b", "c", "d", "f"}
        assert tmp_path.joinpath("a").is_file()
        assert tmp_path.joinpath("c").is_dir()
        assert tmp_path.joinpath("d/e").is_file()
        assert tmp_path.joinpath("f/g").is_dir()
    assert not set(tmp_path.iterdir())


def test_inject_junk_files(tmp_path: Path):
    with inject_junk_files(tmp_path):
        assert tmp_path.joinpath(".tox").is_dir()
        assert tmp_path.joinpath("tests").is_dir()
        assert tmp_path.joinpath("__pycache__").is_dir()
        assert tmp_path.joinpath("tests/__pycache__").is_dir()
    assert not set(tmp_path.iterdir())


def test_inject_junk_files_keep_dirs(tmp_path: Path):
    tmp_path.joinpath("tests/simple").mkdir(parents=True)
    with inject_junk_files(tmp_path):
        assert tmp_path.joinpath(".tox").is_dir()
        assert tmp_path.joinpath("tests/simple").is_dir()
        assert tmp_path.joinpath("tests/__pycache__").is_dir()
    assert {x.name for x in tmp_path.iterdir()} == {"tests"}
    assert {x.name for x in tmp_path.joinpath("tests").iterdir()} == {"simple"}
    assert not set(tmp_path.joinpath("tests/simple").iterdir())
