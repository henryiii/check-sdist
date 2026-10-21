from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tarfile
import types
from pathlib import Path

import pytest

import check_sdist.sdist as sdist_mod


@pytest.fixture
def fake_uv_build(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Stub out uv discovery and the uv build invocation, capturing the command.

    The fake build writes a minimal SDist into the requested out dir so that
    sdist_files() can parse it as usual.
    """
    captured: dict[str, list[str]] = {}

    def fake_run(
        cmd: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[bytes]:
        captured["cmd"] = cmd
        outdir = Path(cmd[cmd.index("--out-dir") + 1])
        with tarfile.open(outdir / "pkg-1.0.tar.gz", "w:gz") as tar:
            info = tarfile.TarInfo("pkg-1.0/example.py")
            tar.addfile(info, io.BytesIO(b""))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(sdist_mod, "get_uv", lambda: "/fake/uv")
    # check_sdist.sdist shares this module object, so patching run() here
    # replaces the call it makes.
    monkeypatch.setattr(subprocess, "run", fake_run)
    return captured


def test_uv_isolated_omits_no_build_isolation(
    fake_uv_build: dict[str, list[str]], tmp_path: Path
) -> None:
    files = sdist_mod.sdist_files(tmp_path, isolated=True, installer="uv")

    assert "--no-build-isolation" not in fake_uv_build["cmd"]
    assert "example.py" in files


def test_uv_no_isolation_adds_no_build_isolation(
    fake_uv_build: dict[str, list[str]], tmp_path: Path
) -> None:
    sdist_mod.sdist_files(tmp_path, isolated=False, installer="uv")

    assert "--no-build-isolation" in fake_uv_build["cmd"]


def test_get_uv_prefers_uv_module(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_uv = types.ModuleType("uv")
    fake_uv.find_uv_bin = lambda: "/module/uv"  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "uv", fake_uv)

    assert sdist_mod.get_uv() == "/module/uv"


def test_get_uv_falls_back_to_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "uv", None)
    monkeypatch.setattr(shutil, "which", lambda _: "/path/uv")

    assert sdist_mod.get_uv() == "/path/uv"


def test_malformed_sdist_multiple_prefixes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(
        cmd: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[bytes]:
        outdir = Path(cmd[cmd.index("--out-dir") + 1])
        with tarfile.open(outdir / "pkg-1.0.tar.gz", "w:gz") as tar:
            for name in ("pkg-1.0/a.py", "other-1.0/b.py"):
                tar.addfile(tarfile.TarInfo(name), io.BytesIO(b""))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(sdist_mod, "get_uv", lambda: "/fake/uv")
    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(AssertionError, match="multiple packages"):
        sdist_mod.sdist_files(tmp_path, isolated=True, installer="uv")
