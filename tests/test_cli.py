from __future__ import annotations

import pytest

from check_sdist import __version__
from check_sdist.__main__ import main

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path


def test_version(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit):
        main(["--version"])

    out, err = capsys.readouterr()
    assert out == f"check-sdist {__version__}\n"
    assert not err


def test_inject_junk_present_during_compare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """--inject-junk must inject before compare() runs, not after."""
    present = None

    def fake_compare(source_dir: Path, **_: object) -> int:
        nonlocal present
        present = source_dir.joinpath("__pycache__").is_dir()
        return 0

    monkeypatch.setattr("check_sdist.__main__.compare", fake_compare)

    with pytest.raises(SystemExit):
        main(["--inject-junk", "--source-dir", str(tmp_path)])

    assert present is True
    assert not tmp_path.joinpath("__pycache__").exists()
