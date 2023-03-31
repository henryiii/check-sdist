from __future__ import annotations

import contextlib
import sys
from collections.abc import Generator, Sequence
from pathlib import Path

from .resources import resources

__all__ = ["inject_junk_files", "inject_files"]


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
    with resources.joinpath("junk-paths.txt").open("r", encoding="utf-8") as f:
        junk_files = [ln.strip() for ln in f]
    # Windows does not allow question marks in filenames
    if sys.platform.startswith("win"):
        junk_files = [ln for ln in junk_files if "?" not in ln]
    with inject_files(source_dir, junk_files):
        yield
