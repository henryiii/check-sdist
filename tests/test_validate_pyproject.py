from __future__ import annotations

import pytest
import validate_pyproject.api


def test_validate_pyproject_defaults():
    example = {
        "tool": {
            "check-sdist": {
                "sdist-only": [],
                "git-only": [],
                "default-ignore": True,
                "recurse-submodules": True,
            }
        }
    }
    validator = validate_pyproject.api.Validator()
    assert validator(example) is not None


def test_validate_pyproject_extra_key():
    example: dict[str, object] = {
        "tool": {
            "check-sdist": {
                "sdists-only": [],
            }
        }
    }
    validator = validate_pyproject.api.Validator()
    with pytest.raises(validate_pyproject.error_reporting.ValidationError):
        validator(example)


@pytest.mark.parametrize(
    "backend",
    [
        "auto",
        "none",
        "flit_core.buildapi",
        "hatchling.build",
        "scikit_build_core.build",
        "pdm.backend",
        "poetry.core.masonry.api",
        "maturin",
    ],
)
def test_validate_pyproject_build_backend(backend: str):
    """The schema must accept the build-backend strings the code matches on."""
    example = {"tool": {"check-sdist": {"build-backend": backend}}}
    validator = validate_pyproject.api.Validator()
    assert validator(example) is not None


def test_validate_pyproject_invalid_value():
    example = {
        "tool": {
            "check-sdist": {
                "sdist-only": [1],
            }
        }
    }
    validator = validate_pyproject.api.Validator()
    with pytest.raises(validate_pyproject.error_reporting.ValidationError):
        validator(example)
