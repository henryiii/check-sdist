from __future__ import annotations

import pytest

from check_sdist import __version__
from check_sdist.__main__ import main


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])

    out, err = capsys.readouterr()
    assert out == f"check-sdist {__version__}\n"
    assert not err
