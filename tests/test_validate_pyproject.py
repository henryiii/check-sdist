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
