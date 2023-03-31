from __future__ import annotations

import argparse
import contextlib
from pathlib import Path

import pathspec

from ._compat import tomllib
from .git import git_files
from .inject import inject_junk_files
from .resources import resources
from .sdist import sdist_files


def compare(source_dir: Path, isolated: bool, verbose: bool = False) -> int:
    """
    Compare the files in the SDist with the files tracked by git.

    Takes the source directory and a flag indicating whether the SDist should
    be built in an isolated environment.

    Return 0 if they match, 1 if the SDist has files that are not tracked by
    git, 2 if the SDist is missing files that are tracked by git, and 3 if both
    conditions are true.
    """

    sdist = sdist_files(source_dir, isolated) - {"PKG-INFO"}
    git = git_files(source_dir)

    config = {}
    pyproject_toml = source_dir.joinpath("pyproject.toml")
    with contextlib.suppress(FileNotFoundError), pyproject_toml.open("rb") as f:
        pyproject = tomllib.load(f)
        config = pyproject.get("tool", {}).get("check-sdist", {})

    sdist_only_patterns = config.get("sdist-only", [])
    git_only_patterns = config.get("git-only", [])
    default_ignore = config.get("default-ignore", True)

    if default_ignore:
        with resources.joinpath("default-ignore.txt").open("r", encoding="utf-8") as f:
            git_only_patterns.extend(f.read().splitlines())

    sdist_spec = pathspec.GitIgnoreSpec.from_lines(sdist_only_patterns)
    git_spec = pathspec.GitIgnoreSpec.from_lines(git_only_patterns)

    sdist_only = frozenset(p for p in sdist - git if not sdist_spec.match_file(p))
    git_only = frozenset(p for p in git - sdist if not git_spec.match_file(p))

    if verbose:
        print("SDist contents:")
        print(*(f"  {x}" for x in sorted(sdist)), sep="\n")
        print()

    if sdist_only or git_only:
        print("SDist does not match git")
        print()
        print("SDist only:")
        print(*(f"  {x}" for x in sorted(sdist_only)), sep="\n")
        print()
        print("Git only:")
        print(*(f"  {x}" for x in sorted(git_only)), sep="\n")
        print()
        return bool(sdist_only) + 2 * bool(git_only)

    print("SDist matches git")
    return 0


def main() -> None:
    """Parse the command line arguments and call compare()."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path.cwd(),
        help="The source directory to check (default: current directory)",
    )
    parser.add_argument(
        "--no-isolation",
        action="store_true",
        help="Do not build the SDist in an isolated environment",
    )
    parser.add_argument(
        "--inject-junk",
        action="store_true",
        help="Temporarily inject common junk files into the source directory",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print out SDist contents too",
    )
    args = parser.parse_args()

    with contextlib.ExitStack() as stack:
        if args.inject_junk:
            stack.enter_context(inject_junk_files(args.source_dir))

    raise SystemExit(compare(args.source_dir, not args.no_isolation, args.verbose))


if __name__ == "__main__":
    main()
