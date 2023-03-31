from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def sdist_files(source_dir: Path, isolated: bool) -> frozenset[str]:
    """Return the files that would be (are) placed in the SDist."""

    with tempfile.TemporaryDirectory() as outdir:
        cmd = [sys.executable, "-m", "build", "--sdist", "--outdir", outdir]
        if not isolated:
            cmd.append("--no-isolation")
        subprocess.run(cmd, check=True, cwd=source_dir)

        (outpath,) = Path(outdir).glob("*.tar.gz")

        with tarfile.open(outpath) as tar:
            prefixes = {n.split("/", maxsplit=1)[0] for n in tar.getnames()}
            if len(prefixes) != 1:
                msg = f"malformted SDist, contains multiple packages {prefixes}"
                raise AssertionError(msg)
            return frozenset(n.split("/", maxsplit=1)[1] for n in tar.getnames())


if __name__ == "__main__":
    print(*sorted(sdist_files(Path.cwd(), True)), sep="\n")
