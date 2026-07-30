"""Startup diagnostics for Netspion on Kali Linux.

Checks Python dependencies, external tools, and environment.
Connections that require elevated privileges will fail normally.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
from dataclasses import dataclass, field

from utils import string_format


PYTHON_MODULES = {
    "cmd2": "cmd2",
    "termcolor": "termcolor",
    "scapy": "scapy",
    "impacket": "impacket",
}

KALI_TOOLS = (
    # ── Information Gathering ──
    "nmap",
    "theHarvester",
    "whois",
    "dnsenum",
    "dnsrecon",
    "dig",
    "nslookup",
    "enum4linux",
    "gitleaks",
    # ── Web Hacking ──
    "gobuster",
    "ffuf",
    "subfinder",
    "nuclei",
    "httpx",
    "katana",
    "wpscan",
    "whatweb",
    "wafw00f",
    "commix",
    "sqlmap",
    "gau",
    "waybackurls",
    "amass",
    "assetfinder",
    "sublist3r",
    "findomain",
    # ── Exploitation ──
    "msfvenom",
    "msfconsole",
    "searchsploit",
    # ── Active Directory ──
    "impacket-secretsdump",
    "impacket-getTGT",
    "impacket-getST",
    "impacket-psexec",
    "impacket-wmiexec",
    "impacket-ntlmrelayx",
    "impacket-smbserver",
    "responder",
    "crackmapexec",
    "bloodhound-python",
    "certipy",
    "ldapdomaindump",
    "adidnsdump",
    "kerbrute",
    "smbclient",
    # ── Passwords ──
    "hashcat",
    "john",
    "hydra",
    "crowbar",
    "hashid",
    "hash-identifier",
    # ── WiFi ──
    "aircrack-ng",
    "airmon-ng",
    "airodump-ng",
    "aireplay-ng",
    "hostapd",
    "dnsmasq",
    "lighttpd",
    "reaver",
    "wash",
    # ── Post-Exploitation ──
    "wget",
    # ── Networking ──
    "nc",
)

WINDOWS_TOOLS = (
    "nmap",
    "whois",
    "hashcat",
    "john",
    "nc",
)


@dataclass(frozen=True)
class DiagnosticReport:
    missing_python: tuple[str, ...] = field(default_factory=tuple)
    missing_tools: tuple[str, ...] = field(default_factory=tuple)
    platform: str = ""
    running_as_root: bool = False

    @property
    def ready(self) -> bool:
        return not self.missing_python


def _get_expected_tools() -> tuple[str, ...]:
    system = platform.system()
    if system == "Linux":
        return tuple(t for t in KALI_TOOLS if not t.startswith("impacket-") and
                     t not in ("airmon-ng", "airodump-ng", "aireplay-ng"))
    if system == "Windows":
        return WINDOWS_TOOLS
    return ()


def _check_impacket_scripts() -> list[str]:
    """Impacket scripts install under ~/.local/bin or /usr/bin."""
    missing = []
    for script in ("impacket-secretsdump", "impacket-getTGT", "impacket-getST",
                   "impacket-psexec", "impacket-wmiexec", "impacket-ntlmrelayx",
                   "impacket-smbserver"):
        if not shutil.which(script):
            missing.append(script)
    return missing


def diagnose() -> DiagnosticReport:
    system = platform.system()
    return DiagnosticReport(
        platform=system,
        running_as_root=False,
        missing_python=tuple(
            pkg for pkg, mod in PYTHON_MODULES.items()
            if importlib.util.find_spec(mod) is None
        ),
        missing_tools=tuple(
            t for t in _get_expected_tools() if not shutil.which(t)
        ) + tuple(_check_impacket_scripts()),
    )


def print_report(report: DiagnosticReport) -> None:
    status = f"{report.platform}"
    if report.platform == "Linux":
        is_root = getattr(os, "geteuid", lambda: 1)() == 0
        status += " [root]" if is_root else " [user]"

    print(string_format.info(f"Platform: {status}"))
    print(string_format.info(f"Python modules: {len(PYTHON_MODULES)} required"))

    if report.missing_python:
        print(string_format.fail(
            "Missing Python packages: " + ", ".join(report.missing_python)
            + ". Run: pip install -r requirements.txt"
        ))

    total = len(KALI_TOOLS) + 7  # 7 impacket scripts
    present_count = total - len(report.missing_tools)
    print(string_format.info(f"External tools: {present_count}/{total} available"))

    if report.missing_tools:
        print(string_format.warning(
            "Optional tools not found: " + ", ".join(sorted(report.missing_tools)[:15])
            + ("..." if len(report.missing_tools) > 15 else "")
        ))
        print(string_format.warning(
            "Install with: sudo apt install <tool>  (Kali: most are pre-installed)"
        ))


def main() -> DiagnosticReport:
    report = diagnose()
    print_report(report)
    return report
