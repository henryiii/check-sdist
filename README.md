# check-sdist

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/henryiii/check-sdist/workflows/CI/badge.svg
[actions-link]:             https://github.com/henryiii/check-sdist/actions
[pypi-link]:                https://pypi.org/project/check-sdist/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/check-sdist
[pypi-version]:             https://img.shields.io/pypi/v/check-sdist

<!-- prettier-ignore-end -->

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

To run:

```console
$ pipx run check-sdist[uv]
```

You can add `--no-isolation` to disable build isolation (faster, but must
preinstall build dependencies), `--source-dir` to select a different source
directory to check, and `--inject-junk` to temporarily inject some common junk
files while running. You can select an installer for build to use with
`--installer=`, choices are `uv`, `pip`, or `uv|pip`, which will use uv if
available (the default).

If you need the latest development version:

```console
$ pipx run --spec git+https://github.com/henryiii/check-sdist check-sdist
```

### Pre-commit integration

To use the [pre-commit](https://pre-commit.com) integration, put this in your
`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v0.1.3
  hooks:
    - id: check-sdist
      args: [--inject-junk]
      additional_dependencies: [] # list your build deps here
```

This requires your build dependencies, but in doing so, it can cache the
environment, making it quite fast. If you don't mind slower runs and don't want
to require build dependency listing:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v0.1.3
  hooks:
    - id: check-sdist-isolated
      args: [--inject-junk]
```

### Configuration

To configure, these options are supported in your `pyproject.toml` file:

```toml
[tool.check-sdist]
sdist-only = []
git-only = []
default-ignore = true
recurse-submodules = true
```

You can add `.gitignore` style lines here, and you can turn off the default
ignore list, which adds some default git-only files.

By default, check-sdist recursively scans the contents of Git submodules, but
you can disable this behavior (e.g. to support older Git versions that don't
have this capability).

### See also

- [check-manifest](https://github.com/mgedmin/check-manifest): A (currently)
  setuptools specific checker that can suggest possible ways to include/exclude
  files.
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/):
  Guidelines on which this package was designed.
