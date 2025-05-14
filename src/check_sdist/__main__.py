from __future__ import annotations

import argparse
import contextlib
import functools
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import pathspec

from . import __version__
from ._compat import tomllib
from .backends import backend_ignored_patterns
from .git import git_files
from .inject import inject_junk_files
from .resources import resources
from .sdist import get_uv, sdist_files


def select_installer(
    installer: Literal["pip", "uv", "uv|pip"],
) -> Literal["uv", "pip"]:
    """
    Select uv, pip, or uv if available, then pip ("uv|pip"). Returns uv, pip,
    or throws an error if uv was required and not available.
    """
    if "uv" in installer:
        if get_uv() is not None:
            return "uv"

        if installer == "uv":
            msg = "Can't find uv"
            raise ImportError(msg)

    return "pip"


def compare(
    source_dir: Path,
    *,
    isolated: bool,
    verbose: bool = False,
    installer: Literal["uv", "pip", "uv|pip"] = "uv|pip",
) -> int:
    """
    Compare the files in the SDist with the files tracked by git.

    Takes the source directory and a flag indicating whether the SDist should
    be built in an isolated environment.

    Return 0 if they match, 1 if the SDist has files that are not tracked by
    git, 2 if the SDist is missing files that are tracked by git, and 3 if both
    conditions are true.
    """

    installer = select_installer(installer)

    pyproject = {}
    config = {}
    pyproject_toml = source_dir.joinpath("pyproject.toml")
    with contextlib.suppress(FileNotFoundError), pyproject_toml.open("rb") as f:
        pyproject = tomllib.load(f)
        config = pyproject.get("tool", {}).get("check-sdist", {})

    sdist_only_patterns = config.get("sdist-only", [])
    git_only_patterns = config.get("git-only", [])
    default_ignore = config.get("default-ignore", True)
    recurse_submodules = config.get("recurse-submodules", True)
    mode = config.get("mode", "git")
    backend = config.get("build-backend", "auto")

    sdist = sdist_files(source_dir, isolated=isolated, installer=installer) - {
        "PKG-INFO"
    }
    if mode == "git":
        git = git_files(source_dir, recurse_submodules=recurse_submodules)
    elif mode == "all":
        git = frozenset(
            str(p.relative_to(source_dir)) for p in source_dir.rglob("*") if p.is_file()
        )
    else:
        msg = "Only 'all' and 'git' supported for 'mode'"
        raise ValueError(msg)

    if default_ignore:
        with resources.joinpath("default-ignore.txt").open("r", encoding="utf-8") as f:
            git_only_patterns.extend(f.read().splitlines())
        sdist_only_patterns.extend("*.dist-info")

    sdist_spec = pathspec.GitIgnoreSpec.from_lines(sdist_only_patterns)
    git_spec = pathspec.GitIgnoreSpec.from_lines(git_only_patterns)

    sdist_only = frozenset(p for p in sdist - git if not sdist_spec.match_file(p))
    git_only = frozenset(p for p in git - sdist if not git_spec.match_file(p))

    git_only = backend_ignored_patterns(backend, pyproject, git_only)

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


def main(sys_args: Sequence[str] | None = None, /) -> None:
    """Parse the command line arguments and call compare()."""

    make_parser = functools.partial(argparse.ArgumentParser)
    if sys.version_info >= (3, 14):
        make_parser = functools.partial(make_parser, color=True, suggest_on_error=True)

    parser = make_parser(
        prog=None if sys_args is None else "check-sdist",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
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
    parser.add_argument(
        "--installer",
        choices={"uv", "pip", "uv|pip"},
        default="uv|pip",
        help="Tool to use when installing packages for making the SDist",
    )
    args = parser.parse_args(sys_args)

    with contextlib.ExitStack() as stack:
        if args.inject_junk:
            stack.enter_context(inject_junk_files(args.source_dir))

    raise SystemExit(
        compare(
            args.source_dir,
            isolated=not args.no_isolation,
            verbose=args.verbose,
            installer=args.installer,
        )
    )


if __name__ == "__main__":
    main()
