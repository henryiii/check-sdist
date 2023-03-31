from __future__ import annotations

import contextlib
from collections.abc import Generator, Sequence
from pathlib import Path

__all__ = ["inject_junk_files", "inject_files", "JUNK_FILES"]

JUNK_FILES = """
.coverage
.mypy_cache/
.pytest_cache/
.ruff_cache/
.tox/
.venv/
dist/
tests/__pycache__/
tests/any/__pycache__/
anything.egg-info/
__pycache__/
""".strip().splitlines()


@contextlib.contextmanager
def inject_files(source_dir: Path, files: Sequence[str]) -> Generator[None, None, None]:
    """This context manager will inject files into a directory, cleaned afterwards."""
    injected_files = []
    injected_directories = []

    for file in files:
        added_file = source_dir / (f"{file}/junk.py" if file.endswith("/") else file)
        if added_file.exists():
            continue

        # Record the missing directories
        parent_folder = added_file.parent
        while not parent_folder.is_dir():
            injected_directories.append(parent_folder)
            parent_folder = parent_folder.parent

        # Create the missing parent directories
        if not added_file.parent.exists():
            added_file.parent.mkdir(parents=True)

        injected_files.append(added_file)
        added_file.touch(exist_ok=False)
    try:
        yield
    finally:
        for injected in injected_files:
            injected.unlink()
        for injected in sorted(
            injected_directories, key=lambda x: len(str(x)), reverse=True
        ):
            injected.rmdir()


@contextlib.contextmanager
def inject_junk_files(source_dir: Path) -> Generator[None, None, None]:
    """This context manager will inject common junk files into a directory, cleaned afterwards."""
    with inject_files(source_dir, JUNK_FILES):
        yield
