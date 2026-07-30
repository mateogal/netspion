from __future__ import annotations

from typing import Any

from . import string_format as sf


def check_vars(var_list: list[dict[str, Any]]) -> bool:
    empty = [v["name"] for v in var_list if not v.get("value")]
    if empty:
        print(sf.fail(f"Required variable(s) empty: {', '.join(empty)}"))
        return False
    return True
