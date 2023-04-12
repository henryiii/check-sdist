from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from check_sdist.__main__ import compare
from check_sdist._compat import tomllib

DIR = Path(__file__).parent.resolve()

with DIR.joinpath("downstream.toml").open("rb") as f:
    packages = tomllib.load(f)["packages"]


@pytest.mark.parametrize(
    ("repo", "ref", "fail"), [(x["repo"], x["ref"], x.get("fail", 0)) for x in packages]
)
def test_packages(repo, ref, fail, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        ["git", "clone", f"https://github.com/{repo}", "--branch", ref], check=True
    )
    package_path = tmp_path / repo.split("/")[1]
    assert compare(package_path, isolated=True) == fail
