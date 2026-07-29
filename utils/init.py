"""Startup checks for Netspion.

Startup is deliberately non-destructive: it never installs packages and does
not require a root shell.  Commands which need elevated privileges will fail
normally and leave an error log for the operator.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
from dataclasses import dataclass

from utils import string_format


PYTHON_MODULES = {
    "cmd2": "cmd2",
    "termcolor": "termcolor",
    "scapy": "scapy",
    "impacket": "impacket",
    "psycopg2-binary": "psycopg2",
}

EXTERNAL_TOOLS = (
    "aircrack-ng",
    "hostapd",
    "msfconsole",
    "theHarvester",
    "nmap",
    "whois",
    "reaver",
    "dnsmasq",
    "lighttpd",
    "cowpatty",
    "responder",
    "whatweb",
    "subfinder",
    "gobuster",
    "ffuf",
    "commix",
    "wafw00f",
    "hashcat",
    "john",
    "gitleaks",
)


@dataclass(frozen=True)
class DiagnosticReport:
    supported_os: bool
    running_as_root: bool
    missing_python: tuple[str, ...]
    missing_tools: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.supported_os and not self.missing_python


def diagnose() -> DiagnosticReport:
    return DiagnosticReport(
        supported_os=platform.system() == "Linux",
        running_as_root=getattr(os, "geteuid", lambda: 1)() == 0,
        missing_python=tuple(
            package
            for package, module in PYTHON_MODULES.items()
            if importlib.util.find_spec(module) is None
        ),
        missing_tools=tuple(tool for tool in EXTERNAL_TOOLS if shutil.which(tool) is None),
    )


def print_report(report: DiagnosticReport) -> None:
    os_status = "Linux supported" if report.supported_os else "unsupported OS (Linux required)"
    privilege_status = "root" if report.running_as_root else "unprivileged (recommended at startup)"
    print(string_format.info(f"Environment: {os_status}; privilege: {privilege_status}"))
    if report.missing_python:
        print(
            string_format.fail("Missing Python packages: ")
            + ", ".join(report.missing_python)
            + ". Install with: python -m pip install -r requirements.txt"
        )
    if report.missing_tools:
        print(
            string_format.warning("Unavailable optional tools: ")
            + ", ".join(report.missing_tools)
        )


def main() -> DiagnosticReport:
    """Run and print non-mutating startup diagnostics."""
    report = diagnose()
    print_report(report)
    return report
