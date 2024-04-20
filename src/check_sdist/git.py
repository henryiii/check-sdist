from __future__ import annotations

import subprocess
from pathlib import Path


def git_files(source_dir: Path, recurse_submodules: bool = True) -> frozenset[str]:
    """Return the files that are tracked by git in the source directory."""

    cmd = ["git", "ls-files", "--cached"]
    if recurse_submodules:
        cmd.append("--recurse-submodules")
    return frozenset(
        subprocess.run(
            cmd,
            cwd=source_dir,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
    )


if __name__ == "__main__":
    print(*sorted(git_files(Path.cwd())), sep="\n")
