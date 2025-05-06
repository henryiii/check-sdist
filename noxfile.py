from __future__ import annotations

from pathlib import Path

import nox

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml()


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
    test_grp = nox.project.dependency_groups(PYPROJECT, "test")
    session.install("-e.", *test_grp)
    session.run("pytest", "-nauto", *session.posargs, env={"COVERAGE_CORE": "sysmon"})


@nox.session(default=False)
def coverage(session: nox.Session) -> None:
    """
    Run tests and compute coverage.
    """

    session.posargs.extend(
        [
            "--cov",
            "--cov-config=pyproject.toml",
            "--cov-report=xml",
            "--cov-report=term-missing",
        ]
    )
    tests(session)


@nox.session(default=False)
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")


@nox.session(tags=["gen"])
def generate_schema(session: nox.Session) -> None:
    """
    Generate a schema file.
    """

    deps = nox.project.load_toml("scripts/generate_schema.py")["dependencies"]
    session.install(*deps)
    out = session.run("python", "scripts/generate_schema.py", silent=True)
    path = Path("src/check_sdist/resources/check-sdist.schema.json")
    path.write_text(out)
