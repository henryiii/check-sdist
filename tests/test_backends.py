from __future__ import annotations

from check_sdist._compat import tomllib
from check_sdist.backends import backend_ignored_patterns

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_glob_backend_excludes_relative_to_source_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Glob-based backend excludes must resolve against source_dir, not cwd."""
    source_dir = tmp_path / "project"
    source_dir.mkdir()
    (source_dir / "junk.txt").touch()
    (source_dir / "keep.py").touch()

    # Run from an unrelated directory: the old code globbed the cwd and so
    # never matched the excluded file living under source_dir.
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    pyproject = tomllib.loads(
        """
        [build-system]
        build-backend = "pdm.backend"

        [tool.pdm.build]
        excludes = ["junk.txt"]
        """
    )
    files = frozenset({"junk.txt", "keep.py"})

    result = backend_ignored_patterns("auto", pyproject, files, source_dir)

    assert "junk.txt" not in result
    assert "keep.py" in result
