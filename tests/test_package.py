from __future__ import annotations

import os
from pathlib import Path

from check_sdist.__main__ import compare
from check_sdist.inject import inject_junk_files

DIR = Path(__file__).parent


def get_all_files(path: Path) -> frozenset[str]:
    with os.scandir(path) as it:
        return frozenset(it.name for it in it if not it.name.startswith(".coverage"))


def test_self_dir():
    start = get_all_files(DIR.parent)
    assert compare(DIR.parent, True) == 0
    end = get_all_files(DIR.parent)
    assert start == end


def test_self_dir_injected():
    start = get_all_files(DIR.parent)
    with inject_junk_files(DIR.parent):
        assert compare(DIR.parent, True) == 0
    end = get_all_files(DIR.parent)
    assert start == end
