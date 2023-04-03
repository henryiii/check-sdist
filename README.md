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
preinstall build dependencies), `--source-dir` to select a different source
directory to check, and `--inject-junk` to temporarily inject some common junk
files while running.

If you need the latest development version:

```console
$ pipx run --spec git+https://github.com/henryiii/check-sdist check-sdist
```

To use the pre-commit integration, put this in your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/henryiii/check-sdist
  rev: v0.1.0
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
  rev: v0.1.0
  hooks:
    - id: check-sdist-isolated
      args: [--inject-junk]
```

To configure, these options are supported in your `pyproject.toml` file:

```toml
[tool.check-sdist]
sdist-only = []
git-only = []
default-ignore = true
```

You can add `.gitignore` style lines here, and you can turn off the default
ignore list, which adds some default git-only files.
