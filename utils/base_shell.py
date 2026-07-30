"""Base shell class to eliminate boilerplate duplication across sub-menus."""

from __future__ import annotations

import os
import platform
from pathlib import Path

import cmd2
from cmd2 import Settable

from utils import run_task as rt
from utils import string_format as sf
from utils.logger import get_logger, setup_logger
from utils.utils_shell import UtilsCommandSet


_BUILTIN_REMOVE = (
    "debug",
    "allow_style",
    "always_show_hint",
    "echo",
    "feedback_to_output",
    "max_completion_items",
    "quiet",
    "timing",
)


class BaseShell(cmd2.Cmd):
    """Shared base for all Netspion sub-shells.

    Subclasses set ``category`` and ``sub_dir`` in ``__init__``, then call
    ``super().__init__()``.
    """

    def __init__(
        self,
        category: str,
        description: str = "",
        auto_load_commands: bool = False,
    ):
        super().__init__(auto_load_commands=auto_load_commands)
        self._category = category
        self._description = description or category
        self.results_root = rt.get_results_root()

        # ── per-category results dir ──────────────────────────────────
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in category)
        self.resultsPath = str(self.results_root / safe / "")
        os.makedirs(self.resultsPath, exist_ok=True)

        # ── logging ───────────────────────────────────────────────────
        setup_logger(self.results_root)
        self._log = get_logger()

        # ── prompt / intro ────────────────────────────────────────────
        self.prompt = sf.success(f"(netspion {category}): ")
        self.intro = sf.text(
            f"Netspion {description or category}. "
            "Type help or ? to list commands.\n"
        )

        # ── common settables ──────────────────────────────────────────
        self.default_category = "cmd2 Built-in Commands"
        for key in _BUILTIN_REMOVE:
            try:
                self.remove_settable(key)
            except Exception:
                pass

        # ── utilities command set ─────────────────────────────────────
        try:
            self.register_command_set(UtilsCommandSet())
        except Exception:
            pass

        # ── banner ────────────────────────────────────────────────────
        self.poutput(
            sf.info("RUNNING ON: ")
            + sf.success(platform.system() + " " + platform.release())
        )
        self.poutput(
            sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(self.resultsPath)
        )

    def set_str(self, name: str, default: str = "", help_text: str = "") -> None:
        self.add_settable(Settable(name, str, help_text or name, self))
        setattr(self, name, default)

    def set_path(self, name: str, default: str = "", help_text: str = "") -> None:
        self.add_settable(
            Settable(name, str, help_text or name, self, completer=cmd2.Cmd.path_complete)
        )
        setattr(self, name, default)

    def set_int(self, name: str, default: str = "", help_text: str = "") -> None:
        self.add_settable(Settable(name, str, help_text or name, self))
        setattr(self, name, default)

    def run(self, command: list[str], save_path: str | None = None) -> rt.ProcessRecord:
        self._log.info("Running: %s", " ".join(command))
        return rt.runBackground(command, save_path or self.resultsPath)
