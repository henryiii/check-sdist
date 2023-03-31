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

To run:

```console
$ pipx run check-sdist
```

You can add `--no-isolation` to disable build isolation (faster, but must
preinstall build deps), `--source-dir` to select a different source dir to
check, and `--inject-junk` to temporarily inject some common junk files while
running.

To use the development version:

```console
$ pipx run --spec git+https://github.com/henryiii/check-sdist check-sdist
```

To use the pre-commit integration, use this in your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v0.1.0
  hooks:
    - id: check-sdist
      args: [--inject-junk]
      additional_dependencies: [] # list your build deps here
```

Or, slower, but doesn't require build dependency listing:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v0.1.0
  hooks:
    - id: check-sdist-isolated
      args: [--inject-junk]
```

To configure, these options are provided for your pyproject.toml file:

```toml
[tool.check-sdist]
sdist-only = []
git-only = []
default-ignore = true
```

You can add .gitignore style lines here, and you can turn off the default ignore
list, which adds some default `git-only` files.
