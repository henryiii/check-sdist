from __future__ import annotations

import json
from typing import Any

from .resources import resources


def get_schema(tool_name: str = "check-sdist") -> dict[str, Any]:
    "Get the stored complete schema for check-sdist settings."
    assert tool_name == "check-sdist", "Only check-sdist is supported."

    with resources.joinpath("check-sdist.schema.json").open(encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]
