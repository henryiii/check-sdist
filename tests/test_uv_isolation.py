from __future__ import annotations

import io
import subprocess
import tarfile
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
