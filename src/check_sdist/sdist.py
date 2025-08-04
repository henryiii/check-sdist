from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Literal

__all__ = ["get_uv", "sdist_files"]


def get_uv() -> str | None:
    """
    Find uv and return the arguments to use it.
    """
    try:
        # pylint: disable-next=import-outside-toplevel
        import uv  # noqa: PLC0415

        return uv.find_uv_bin()
    except ModuleNotFoundError:
        return shutil.which("uv")


def sdist_files(
    source_dir: Path, *, isolated: bool, installer: Literal["uv", "pip"]
) -> frozenset[str]:
    """Return the files that would be (are) placed in the SDist."""

    with tempfile.TemporaryDirectory() as outdir:
        if installer == "pip":
            cmd = [
                sys.executable,
                "-m",
                "build",
                "--sdist",
                "--outdir",
                outdir,
                f"--installer={installer}" if isolated else "--no-isolation",
            ]
        else:
            uv = get_uv()
            assert uv is not None, "uv must be found to reach this point!"
            cmd = [
                uv,
                "build",
                "--sdist",
                "--python",
                sys.executable,
                "--out-dir",
                outdir,
            ]

        subprocess.run(cmd, check=True, cwd=source_dir)

        (outpath,) = Path(outdir).glob("*.tar.gz")

        with tarfile.open(outpath) as tar:
            prefixes = {n.split("/", maxsplit=1)[0] for n in tar.getnames()}
            if len(prefixes) != 1:
                msg = f"malformed SDist, contains multiple packages {prefixes}"
                raise AssertionError(msg)
            return frozenset(
                t.name.split("/", maxsplit=1)[1]
                for t in tar.getmembers()
                if t.isfile() or t.issym()
            )


if __name__ == "__main__":
    print(*sorted(sdist_files(Path.cwd(), isolated=True, installer="pip")), sep="\n")
