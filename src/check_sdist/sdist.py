from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def sdist_files(source_dir: Path, isolated: bool, buildsystem: str) -> frozenset[str]:
    """Return the files that would be (are) placed in the SDist."""
    if buildsystem not in BUILD_SYSTEMS:
        msg = (
            f"No check for build system '{buildsystem}' implemented. Available "
            "systems are: '" + "', '".join(BUILD_SYSTEMS) + "'."
        )
        raise NotImplementedError(msg)
    return BUILD_SYSTEMS[buildsystem](source_dir, isolated)


def _sdist_files_build(source_dir: Path, isolated: bool):
    """Create subprocess command for build."""
    with tempfile.TemporaryDirectory() as outdir:
        cmd = [sys.executable, "-m", "build", "--sdist", "--outdir", outdir]
        return _run(source_dir, isolated, cmd, outdir)


def _sdist_files_flit(source_dir: Path, isolated: bool):
    """Create subprocess command for flit."""
    cmd = [sys.executable, "-m", "flit", "build"]
    outdir = os.path.join(source_dir, "dist")
    return _run(source_dir, isolated, cmd, outdir)


def _run(source_dir: Path, isolated: bool, cmd: list, outdir: str):
    """Run build command and return file list."""
    if not isolated:
        cmd.append("--no-isolation")
    subprocess.run(cmd, check=True, cwd=source_dir)

    (outpath,) = Path(outdir).glob("*.tar.gz")

    with tarfile.open(outpath) as tar:
        prefixes = {n.split("/", maxsplit=1)[0] for n in tar.getnames()}
        if len(prefixes) != 1:
            msg = f"malformted SDist, contains multiple packages {prefixes}"
            raise AssertionError(msg)
        return frozenset(
            t.name.split("/", maxsplit=1)[1]
            for t in tar.getmembers()
            if t.isfile() or t.issym()
        )


BUILD_SYSTEMS = {
    "build": _sdist_files_build,
    "flit": _sdist_files_flit,
}


if __name__ == "__main__":
    print(*sorted(sdist_files(Path.cwd(), True)), sep="\n")
