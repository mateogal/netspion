from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import string_format as sf

_LOG: logging.Logger | None = None


def setup_logger(results_root: str | os.PathLike, level: int = logging.DEBUG) -> logging.Logger:
    global _LOG
    if _LOG is not None:
        return _LOG

    log_dir = Path(results_root)
    log_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    log_path = log_dir / "netspion.log"

    _LOG = logging.getLogger("netspion")
    _LOG.setLevel(level)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

    handler = RotatingFileHandler(str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(fmt)
    _LOG.addHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.setLevel(logging.INFO)
    _LOG.addHandler(console)

    try:
        log_path.chmod(0o600)
    except OSError:
        pass

    _LOG.info("Logger initialised at %s", log_path)
    return _LOG


def get_logger() -> logging.Logger:
    if _LOG is None:
        return setup_logger("/tmp/netspion")
    return _LOG


def log(msg: str, *args: object, level: int = logging.INFO) -> None:
    get_logger().log(level, msg, *args)
