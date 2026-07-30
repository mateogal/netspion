from __future__ import annotations

import os
import shlex
import shutil
import subprocess

from utils import run_task as rt
from cmd2 import CommandSet, with_default_category


@with_default_category("Utils")
class UtilsCommandSet(CommandSet):
    def do_clear(self, arg):
        "Clear screen"
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "cls"], check=False)
        else:
            subprocess.run(["clear"], check=False)

    def do_check_processes(self, arg):
        "Show processes status"
        rt.showRunningProcs()

    def do_process_data(self, arg):
        "Show task output: process_data PID_OR_TASK_ID [--follow] [--lines N]"
        identifier, follow, lines = self._parse_log_args(arg)
        if identifier:
            rt.showProcessData(identifier, follow=follow, lines=lines)

    def do_process_errors(self, arg):
        "Show task errors: process_errors PID_OR_TASK_ID [--follow] [--lines N]"
        identifier, follow, lines = self._parse_log_args(arg)
        if identifier:
            rt.showProcessErrors(identifier, follow=follow, lines=lines)

    def do_exec_mode(self, arg):
        "Set/show execution mode: exec_mode [background|terminal] (aliases B/N)"
        value = str(arg).strip()
        if not value:
            print(f"Execution mode: {rt.get_execution_mode()}")
            return
        try:
            normalized = rt.set_execution_mode(value)
            print(f"Execution mode: {normalized}")
        except ValueError as exc:
            print(exc)

    def do_end_process(self, arg):
        "End a task gracefully: end_process PID_OR_TASK_ID"
        identifier = str(arg).strip()
        if not identifier:
            print("Usage: end_process PID_OR_TASK_ID")
            return
        rt.endProcess(identifier)

    @staticmethod
    def _parse_log_args(arg):
        try:
            tokens = shlex.split(str(arg))
        except ValueError as exc:
            print(f"Invalid arguments: {exc}")
            return None, False, 100
        if not tokens:
            print("A PID or task ID is required.")
            return None, False, 100
        identifier = tokens[0]
        follow = "--follow" in tokens
        lines = 100
        if "--lines" in tokens:
            try:
                position = tokens.index("--lines")
                lines = max(1, min(10000, int(tokens[position + 1])))
            except (ValueError, IndexError):
                print("--lines requires an integer between 1 and 10000.")
                return None, False, 100
        return identifier, follow, lines
