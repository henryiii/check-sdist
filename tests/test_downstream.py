from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Literal

import pytest

from check_sdist.__main__ import compare
from check_sdist._compat import tomllib
from check_sdist.sdist import get_uv

DIR = Path(__file__).parent.resolve()

with DIR.joinpath("downstream.toml").open("rb") as f:
    packages = tomllib.load(f)["packages"]


@pytest.mark.parametrize(
    "installer",
    [
        pytest.param(
            "uv", marks=pytest.mark.skipif(get_uv() is None, reason="uv not found")
        ),
        "pip",
    ],
)
@pytest.mark.parametrize(
    ("repo", "ref", "fail"), [(x["repo"], x["ref"], x.get("fail", 0)) for x in packages]
)
def test_packages(
    repo: str,
    ref: str,
    fail: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    installer: Literal["uv", "pip"],
):
    if repo.endswith("scikit-build") and sys.platform.startswith("win32"):
        pytest.skip(reason="Path too long on Windows (0.18)")

    monkeypatch.chdir(tmp_path)
    cmd = [
        "git",
        "clone",
        f"https://github.com/{repo}",
        "--depth=1",
        "--branch",
        ref,
        "--recurse-submodules",
    ]
    subprocess.run(cmd, check=True)
    package_path = tmp_path / repo.split("/")[1]
    assert compare(package_path, isolated=True, installer=installer) == fail
