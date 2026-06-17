# check-sdist

[![Actions Status][actions-badge]][actions-link]
[![codecov][codecov-badge]][codecov-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

Have you ever shipped broken SDists with missing files or possibly dirty SDists
with files that shouldn't have been there? Have you noticed that standards
compliant tools aren't making the same SDist that `flit build` is? Is hatchling
adding `.DSStore` files when you ship from your macOS? No matter what
build-backend you use, check-sdist can help!

Check-sdist builds an SDist and compares the contents with your Git repository
contents. It can even temporarily inject common junk files (like pycache files
or OS specific files) and help verify that those aren't getting bundled into
your SDist. If you are getting files you didn't expect or missing files you did
expect, consult your build backend's docs to see how to include or exclude
files.

### Quick start

To run with [pipx][]:

```console
$ pipx run check-sdist[uv]
```

Or, if you like [uv][] instead (faster):

```console
$ uvx check-sdist
```

You can add `--no-isolation` to disable build isolation (faster, but must
preinstall build dependencies), `--source-dir` to select a different source
directory to check, `--inject-junk` to temporarily inject some common junk files
while running, and `-v`/`--verbose` to also print the SDist contents. You can
select an installer for build to use with `--installer=`, choices are `uv`,
`pip`, or `uv|pip`, which will use uv if available (the default).

check-sdist exits 0 if the SDist matches git. Otherwise it returns a bitfield:
`1` if the SDist has files not tracked by git, `2` if it is missing files that
are tracked by git, and `3` if both.

If you need the latest development version:

```console
$ pipx run --spec git+https://github.com/henryiii/check-sdist check-sdist
$ uvx --from git+https://github.com/henryiii/check-sdist check-sdist
```

### Pre-commit integration

To use the [pre-commit](https://pre-commit.com) integration, put this in your
`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v1.4.0
  hooks:
    - id: check-sdist
      args: [--inject-junk]
      additional_dependencies: [] # list your build deps here
```

This requires your build dependencies, but in doing so, it can cache the
environment, making it quite fast. The installation is handled by pre-commit;
see [`pre-commit-uv`](https://pypi.org/p/pre-commit-uv) if you want to try to
optimize the initial setup. You can also use [`prek`](https://prek.j178.dev),
which is a Rust pre-commit compatible runner that uses uv. If uv is present
(including in your `additional_dependencies`), the build will be slightly
faster, as uv is used to do the build. If you don't mind slower runs and don't
want to require a build dependency listing:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v1.4.0
  hooks:
    - id: check-sdist-isolated
      args: [--inject-junk]
```

This one defaults to including `uv` in `additional_dependencies`; you shouldn't
have to specify anything else.

### Configuration

To configure, these options are supported in your `pyproject.toml` file:

```toml
[tool.check-sdist]
sdist-only = []
git-only = []
default-ignore = true
recurse-submodules = true
mode = "git"
build-backend = "auto"
```

You can add `.gitignore` style lines here, and you can turn off the default
ignore list, which adds some default git-only files.

By default, check-sdist recursively scans the contents of Git submodules, but
you can disable this behavior (e.g. to support older Git versions that don't
have this capability).

You can also select `mode = "all"`, which will instead check every file on your
system. Be prepared to ignore lots of things manually, like `*.pyc` files, if
you use this.

You can tell check-sdist to look for exclude lists for a specific build backend
with `build-backend`, or `"none"` to only use its own exclude list. Build
backends supported are `"setuptools.build_meta"`, `"flit_core.buildapi"`,
`"hatchling.build"`, `"scikit_build_core.build"`, `"pdm.backend"`, `"maturin"`,
and `"poetry.core.masonry.api"`. The default, `"auto"`, will try to detect the
build backend if `build-system.build-backend` is set to a known value.

check-sdist will ignore `*.dist-info` in SDists, since those are generated. If
the build backend is clearly setuptools and `default-ignore` is on, it will also
ignore `*.egg-info` and `setup.cfg`, as setuptools can generate this. If you've
wrapped your build backend, you'll need to add this to the `sdist-only` ignore
list manually.

If `default-ignore` is on, a few common generated file settings will be read and
included in `sdist-only`:

- setuptools-scm version file (modern `version_file` in pyproject.toml only,
  `write_to` is not supported)
- hatch-vcs version file (pyproject.toml only)
- pdm-backend version file
- scikit-build-core's `generate` feature

### Plugins

Every build backend is a plugin registered under the `check_sdist.backends`
entry-point group, keyed by its `build-system.build-backend` string. You can add
support for another backend (or override a built-in one) by shipping a small
class and registering it under that group. Once installed, `auto` detection will
pick it up, and the `build-backend` config option will accept its name too.

A backend is structural: it just needs to match the `Backend` protocol, so it
doesn't have to import or subclass anything from check-sdist. It must provide a
`build_backends` attribute (the `build-system.build-backend` strings it claims,
used for `auto` detection) and two methods:

```python
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any, ClassVar


class MyBackend:
    # build-system.build-backend strings this plugin claims (may be several)
    build_backends: ClassVar[tuple[str, ...]] = ("my_backend.api",)

    def git_only_excludes(
        self, pyproject: dict[str, Any], files: frozenset[str], source_dir: Path
    ) -> frozenset[str]:
        """Drop files the backend intentionally keeps out of the SDist."""
        return files

    def sdist_only_ignores(self, pyproject: dict[str, Any]) -> Iterator[str]:
        """Yield gitignore-style patterns expected in the SDist but absent from git."""
        yield from ()
```

Register it from your package's `pyproject.toml`:

```toml
[project.entry-points."check_sdist.backends"]
"my_backend.api" = "my_package._check_sdist:MyBackend"
```

A backend with no git-only excludes returns `files` unchanged; one with no
generated files yields nothing. check-sdist exports `glob_filter` and
`pathspec_filter` helpers from `check_sdist.backends` for the two common
filtering styles, but using them is optional.

### See also

- [check-manifest](https://github.com/mgedmin/check-manifest): A (currently)
  setuptools specific checker that can suggest possible ways to include/exclude
  files.
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/):
  Guidelines on which this package was designed.

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/henryiii/check-sdist/actions/workflows/ci.yml/badge.svg
[actions-link]:             https://github.com/henryiii/check-sdist/actions
[pypi-link]:                https://pypi.org/project/check-sdist/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/check-sdist
[pypi-version]:             https://img.shields.io/pypi/v/check-sdist
[codecov-badge]:            https://codecov.io/gh/henryiii/check-sdist/graph/badge.svg?token=noB2wxFVBr
[codecov-link]:             https://codecov.io/gh/henryiii/check-sdist
[pipx]:                     https://pipx.pypa.io
[uv]:                       https://docs.astral.sh/uv
<!-- prettier-ignore-end -->
