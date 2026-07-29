"""Safe process execution and supervision for Netspion.

All external tools should be started through this module.  Commands are argv
lists (never interpolated shell strings), output is written to per-task logs,
and a small JSON registry allows completed tasks to be inspected later.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from . import string_format as sf


DEFAULT_RESULTS_ROOT = Path(os.environ.get("NETSPION_RESULTS_DIR", "/tmp/netspion"))
PROCESS_DIR = DEFAULT_RESULTS_ROOT / "processes"
VALID_MODES = {"background", "terminal"}
_EXECUTION_MODE = "background"
_SENSITIVE_FLAGS = {
    "-p",
    "--password",
    "--passwd",
    "--hash",
    "--hashes",
    "-hashes",
    "--cookie",
    "--data",
}
_NTLM_RE = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")


@dataclass
class ProcessRecord:
    task_id: str
    pid: int
    command: list[str]
    mode: str
    started_at: str
    stdout_path: str
    stderr_path: str
    status: str = "running"
    returncode: int | None = None
    ended_at: str | None = None
    process_start_marker: str | None = None
    _process: subprocess.Popen | None = field(default=None, repr=False, compare=False)
    _stdout_handle: object | None = field(default=None, repr=False, compare=False)
    _stderr_handle: object | None = field(default=None, repr=False, compare=False)

    def public_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "pid": self.pid,
            "command": self.command,
            "mode": self.mode,
            "started_at": self.started_at,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "status": self.status,
            "returncode": self.returncode,
            "ended_at": self.ended_at,
            "process_start_marker": self.process_start_marker,
        }


# Kept public for backwards compatibility. Keys are operating-system PIDs.
PROCS: dict[int, ProcessRecord] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_command(command: Sequence[object]) -> list[str]:
    if isinstance(command, (str, bytes)) or not isinstance(command, Sequence):
        raise TypeError("command must be a non-empty argv sequence, not a shell string")
    argv = [os.fspath(part) if isinstance(part, os.PathLike) else str(part) for part in command]
    if not argv or not argv[0].strip():
        raise ValueError("command must contain an executable")
    if any("\x00" in part for part in argv):
        raise ValueError("command arguments cannot contain NUL bytes")
    return argv


def _redact_command(command: Sequence[str]) -> list[str]:
    redacted: list[str] = []
    hide_next = False
    for part in command:
        if hide_next:
            redacted.append("<redacted>")
            hide_next = False
            continue
        lowered = part.lower()
        if lowered in _SENSITIVE_FLAGS:
            redacted.append(part)
            hide_next = True
            continue
        if any(lowered.startswith(flag + "=") for flag in _SENSITIVE_FLAGS):
            redacted.append(part.split("=", 1)[0] + "=<redacted>")
            continue
        # NTLM material is often embedded in DOMAIN/user%:HASH strings.
        redacted.append(_NTLM_RE.sub("<redacted>", part))
    return redacted


def _safe_stem(executable: str) -> str:
    stem = Path(executable).name or "task"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)[:48]


def _task_paths(command: Sequence[str], save_path: str | os.PathLike | None) -> tuple[str, Path, Path]:
    directory = Path(save_path) if save_path else PROCESS_DIR
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        directory.chmod(0o700)
    except OSError:
        pass
    task_id = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{_safe_stem(command[0])}-{uuid.uuid4().hex[:8]}"
    return task_id, directory / f"{task_id}.out.log", directory / f"{task_id}.err.log"


def _metadata_path(record: ProcessRecord) -> Path:
    return Path(record.stdout_path).with_name(f"{record.task_id}.json")


def _write_metadata(record: ProcessRecord) -> None:
    path = _metadata_path(record)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record.public_dict(), indent=2), encoding="utf-8")
    temporary.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _linux_start_marker(pid: int) -> str | None:
    try:
        # Field 22 in /proc/<pid>/stat disambiguates PID reuse.
        return Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()[21]
    except (OSError, IndexError):
        return None


def _pid_matches(pid: int, marker: str | None) -> bool:
    if pid <= 0:
        return False
    if sys.platform.startswith("linux") and marker:
        return _linux_start_marker(pid) == marker
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _close_handles(record: ProcessRecord) -> None:
    for handle in (record._stdout_handle, record._stderr_handle):
        if handle and not handle.closed:
            handle.close()


def _refresh(record: ProcessRecord) -> ProcessRecord:
    if record.status != "running":
        return record
    if record._process is not None:
        returncode = record._process.poll()
        if returncode is None:
            return record
        record.returncode = returncode
    elif _pid_matches(record.pid, record.process_start_marker):
        return record
    else:
        # Return codes are not recoverable after restarting Netspion.
        record.returncode = record.returncode
    record.status = "completed" if record.returncode in (0, None) else "failed"
    record.ended_at = record.ended_at or _utc_now()
    _close_handles(record)
    _write_metadata(record)
    return record


def set_execution_mode(mode: str) -> str:
    """Set the process mode used by subsequent ``runBackground`` calls."""
    global _EXECUTION_MODE
    normalized = mode.strip().lower()
    aliases = {"b": "background", "n": "terminal", "new": "terminal", "t": "terminal"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in VALID_MODES:
        raise ValueError("mode must be 'background' (B) or 'terminal' (N)")
    _EXECUTION_MODE = normalized
    return normalized


def get_execution_mode() -> str:
    return _EXECUTION_MODE


def _popen_session_kwargs() -> dict:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _register_process(
    process: subprocess.Popen,
    command: list[str],
    mode: str,
    task_id: str,
    stdout_path: Path,
    stderr_path: Path,
    stdout_handle=None,
    stderr_handle=None,
) -> ProcessRecord:
    record = ProcessRecord(
        task_id=task_id,
        pid=process.pid,
        command=_redact_command(command),
        mode=mode,
        started_at=_utc_now(),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        process_start_marker=_linux_start_marker(process.pid),
        _process=process,
        _stdout_handle=stdout_handle,
        _stderr_handle=stderr_handle,
    )
    PROCS[process.pid] = record
    _write_metadata(record)
    print(
        f"Task: {record.task_id} || PID: {record.pid} || "
        f"Command: {shlex.join(record.command)} || {sf.info('STARTED')}"
    )
    print(f"Logs: {record.stdout_path} | {record.stderr_path}")
    return record


def _start_background(command: Sequence[object], save_path=None) -> ProcessRecord:
    argv = _validate_command(command)
    task_id, stdout_path, stderr_path = _task_paths(argv, save_path)
    stdout_handle = stdout_path.open("a", encoding="utf-8", errors="replace", buffering=1)
    stderr_handle = stderr_path.open("a", encoding="utf-8", errors="replace", buffering=1)
    try:
        process = subprocess.Popen(
            argv,
            stdout=stdout_handle,
            stderr=stderr_handle,
            stdin=subprocess.DEVNULL,
            text=True,
            **_popen_session_kwargs(),
        )
    except Exception:
        stdout_handle.close()
        stderr_handle.close()
        raise
    return _register_process(
        process, argv, "background", task_id, stdout_path, stderr_path, stdout_handle, stderr_handle
    )


def _terminal_command(script: str) -> list[str]:
    configured = os.environ.get("NETSPION_TERMINAL")
    candidates = [configured] if configured else [
        "qterminal",
        "x-terminal-emulator",
        "gnome-terminal",
        "konsole",
    ]
    terminal = next((candidate for candidate in candidates if candidate and shutil.which(candidate)), None)
    if not terminal:
        raise RuntimeError(
            "no supported terminal emulator found; set NETSPION_TERMINAL or use background mode"
        )
    name = Path(terminal).name
    if name == "gnome-terminal":
        return [terminal, "--", "bash", "-lc", script]
    return [terminal, "-e", "bash", "-lc", script]


def newTerminal(command: Sequence[object], savePath=None) -> ProcessRecord:
    """Run an argv command in a new terminal while preserving output logs."""
    argv = _validate_command(command)
    task_id, stdout_path, stderr_path = _task_paths(argv, savePath)
    command_text = shlex.join(argv)
    # Quoting is performed per argv element above; log paths are quoted independently.
    script = (
        "set -o pipefail; "
        f"{command_text} > >(tee -a {shlex.quote(str(stdout_path))}) "
        f"2> >(tee -a {shlex.quote(str(stderr_path))} >&2); "
        "rc=$?; printf '\\n[netspion] exit code: %s\\n' \"$rc\"; "
        "read -r -n 1 -p '[netspion] Press any key to close...'; exit \"$rc\""
    )
    launcher = _terminal_command(script)
    process = subprocess.Popen(
        launcher,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **_popen_session_kwargs(),
    )
    return _register_process(process, argv, "terminal", task_id, stdout_path, stderr_path)


def runBackground(command: Sequence[object], savePath=None) -> ProcessRecord:
    """Compatibility entry point honoring the selected execution mode."""
    if _EXECUTION_MODE == "terminal":
        return newTerminal(command, savePath)
    return _start_background(command, savePath)


def _load_registry() -> dict[int, ProcessRecord]:
    records = dict(PROCS)
    if not PROCESS_DIR.exists():
        return records
    for path in PROCESS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            record = ProcessRecord(**data)
            records.setdefault(record.pid, record)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    return records


def list_processes() -> list[ProcessRecord]:
    records = [_refresh(record) for record in _load_registry().values()]
    return sorted(records, key=lambda record: record.started_at, reverse=True)


def showRunningProcs() -> None:
    records = list_processes()
    if not records:
        print(sf.warning("No tasks have been registered."))
        return
    for record in records:
        color = sf.success if record.status == "running" else (sf.fail if record.status == "failed" else sf.info)
        print(
            f"Task: {record.task_id} || PID: {record.pid} || Mode: {record.mode} || "
            f"Status: {color(record.status.upper())} || Command: {shlex.join(record.command)}"
        )


def _find_record(identifier: int | str) -> ProcessRecord | None:
    value = str(identifier).strip()
    for record in list_processes():
        if str(record.pid) == value or record.task_id == value:
            return record
    return None


def _tail(path: str, lines: int = 100, follow: bool = False) -> None:
    log_path = Path(path)
    if not log_path.exists():
        print(sf.warning(f"Log file not created yet: {log_path}"))
        return
    with log_path.open("r", encoding="utf-8", errors="replace") as handle:
        content = handle.readlines()
        for line in content[-max(1, lines):]:
            print(line, end="")
        if not follow:
            return
        while True:
            line = handle.readline()
            if line:
                print(line, end="")
                continue
            time.sleep(0.25)


def showProcessData(identifier: int | str, follow: bool = False, lines: int = 100) -> None:
    record = _find_record(identifier)
    if not record:
        print(sf.fail(f"Process/task not found: {identifier}"))
        return
    try:
        _tail(record.stdout_path, lines=lines, follow=follow)
    except KeyboardInterrupt:
        print()


def showProcessErrors(identifier: int | str, follow: bool = False, lines: int = 100) -> None:
    record = _find_record(identifier)
    if not record:
        print(sf.fail(f"Process/task not found: {identifier}"))
        return
    try:
        _tail(record.stderr_path, lines=lines, follow=follow)
    except KeyboardInterrupt:
        print()


def endProcess(identifier: int | str, timeout: float = 5.0) -> bool:
    record = _find_record(identifier)
    if not record:
        print(sf.fail(f"Process/task not found: {identifier}"))
        return False
    _refresh(record)
    if record.status != "running" or not _pid_matches(record.pid, record.process_start_marker):
        print(sf.warning(f"Task is not running: {record.task_id}"))
        return False
    try:
        if os.name == "nt":
            if record._process is not None:
                record._process.terminate()
            else:
                os.kill(record.pid, signal.SIGTERM)
        else:
            os.killpg(record.pid, signal.SIGTERM)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and _pid_matches(record.pid, record.process_start_marker):
            time.sleep(0.1)
        if _pid_matches(record.pid, record.process_start_marker):
            if os.name == "nt" and record._process is not None:
                record._process.kill()
            elif os.name != "nt":
                os.killpg(record.pid, signal.SIGKILL)
        record.status = "terminated"
        record.ended_at = _utc_now()
        record.returncode = record._process.poll() if record._process else None
        _close_handles(record)
        _write_metadata(record)
        print(sf.info(f"Stopped task {record.task_id} (PID {record.pid})."))
        return True
    except (ProcessLookupError, PermissionError, OSError) as exc:
        print(sf.fail(f"Could not stop task {record.task_id}: {exc}"))
        return False


def normalCapture(command: Sequence[object], *, timeout: float | None = None) -> subprocess.CompletedProcess:
    """Run a non-interactive argv command and capture its output."""
    argv = _validate_command(command)
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)


def normalShell(command: Sequence[object], *, timeout: float | None = None) -> subprocess.CompletedProcess:
    """Run an argv command attached to the current terminal (despite the legacy name)."""
    argv = _validate_command(command)
    return subprocess.run(argv, text=True, timeout=timeout, check=False)


def progress(command: Sequence[object]) -> int:
    """Run a command without invoking a shell and return its exit code."""
    argv = _validate_command(command)
    process = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return process.wait()
