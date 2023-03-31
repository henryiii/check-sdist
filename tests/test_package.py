from __future__ import annotations

from pathlib import Path

from check_sdist.__main__ import compare

DIR = Path(__file__).parent


def test_self_dir():
    assert compare(DIR.parent, True) == 0
