from __future__ import annotations

import nox

nox.needs_version = ">=2024.4.15"
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session
def lint(session: nox.Session) -> None:
    """
    Run the linter.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session
def pylint(session: nox.Session) -> None:
    """
    Run PyLint.
    """
    # This needs to be installed into the package environment, and is slower
    # than a pre-commit check
    session.install("-e.", "pylint")
    session.run("pylint", "src", *session.posargs)


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install("-e.[test]")
    session.run("pytest", *session.posargs)


@nox.session
def coverage(session: nox.Session) -> None:
    """
    Run tests and compute coverage.
    """

    session.posargs.append("--cov=check-sdist")
    tests(session)


@nox.session(default=False)
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")
