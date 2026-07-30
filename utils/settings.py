"""Persistent configuration for Netspion.

Settings are stored as JSON in the results root directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from utils import run_task as rt
from utils.logger import get_logger


_CONFIG: dict[str, Any] = {}
_CONFIG_PATH: Path | None = None


def _config_path() -> Path:
    global _CONFIG_PATH
    if _CONFIG_PATH is None:
        _CONFIG_PATH = rt.get_results_root() / "config.json"
    return _CONFIG_PATH


def load() -> dict[str, Any]:
    global _CONFIG
    path = _config_path()
    if path.exists():
        try:
            _CONFIG = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _CONFIG = {}
    else:
        _CONFIG = {}
    return _CONFIG


def save() -> None:
    path = _config_path()
    temp = path.with_suffix(".json.tmp")
    try:
        temp.write_text(json.dumps(_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)
        try:
            path.chmod(0o600)
        except OSError:
            pass
    except OSError as exc:
        get_logger().warning("Could not save config: %s", exc)


def get(key: str, default: Any = None) -> Any:
    return _CONFIG.get(key, default)


def set_key(key: str, value: Any) -> None:
    _CONFIG[key] = value
    save()
