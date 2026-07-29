"""Small validation helpers for values used in paths and privileged commands."""

from __future__ import annotations

import re


_INTERFACE_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,32}$")


def safe_filename(value: object, fallback: str = "target", limit: int = 96) -> str:
    """Return a value that cannot escape its intended results directory."""
    text = str(value).strip()
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return (cleaned or fallback)[:limit]


def valid_interface(value: object) -> bool:
    return bool(_INTERFACE_RE.fullmatch(str(value).strip()))
