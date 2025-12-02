See the [Scientific-Python Development Guide][skhep-dev-intro] for a detailed
description of best practices for developing packages.

[skhep-dev-intro]: https://learn.scientific-python.org/development/guides

# Quick development

The fastest way to start with development is to use nox. If you don't have nox,
you can use `pipx run nox` to run it without installing, or `pipx install nox`.
If you don't have pipx (pip for applications), then you can install with with
`pip install pipx` (the only case were installing an application with regular
pip is reasonable). If you use macOS, then pipx and nox are both in brew, use
`brew install pipx nox`.

To use, run `nox`. This will lint and test using every installed version of
Python on your system, skipping ones that are not installed. You can also run
specific jobs:

```console
$ nox -s lint   # Lint only
$ nox -s pylint # Slower linting via PyLint
$ nox -s tests  # Run tests
$ nox -s build  # Make an SDist and wheel
```

Nox handles everything for you, including setting up an temporary virtual
environment for each run.

# Setting up a development environment manually

You can set up a development environment by running:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
pip install -v -e .[dev]
```

If you have the
[Python Launcher for Unix](https://github.com/brettcannon/python-launcher), you
can instead do:

```bash
py -m venv .venv
py -m install -v -e .[dev]
```

# Post setup

You should prepare prek, which will help you by checking that commits pass
required checks:

```bash
pip install prek # or brew install prek on macOS
prek install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `prek` (changes only) or `prek -a` to check even
without installing the hook.

# Testing

Use pytest to run the unit checks:

```bash
pytest
```

# Coverage

Use pytest-cov to generate coverage reports:

```bash
pytest --cov=check-sdist
```
