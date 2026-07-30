"""Netspion — Modular Ethical Hacking Suite for Kali Linux.

Entry point that initialises diagnostics, registers all sub-menus,
and starts the interactive shell.
"""

from __future__ import annotations

import platform

import cmd2
from cmd2 import CommandSet, with_default_category

import ActiveDirectory.ad as ad_cs
import Evasion.evasion as evasion
import Exploitation.exploitation as exploit
import InformationGathering.active_info as aig
import InformationGathering.passive_info as pig
import Osint.osint as osint
import Passwords.password_crack as pc
import PostExploitation.postexploitation as postex
import Reporting.reporting as report
import WebHacking.web as wh_cs
import Wifi.wifi as wifi
import utils.init as init
import utils.run_task as rt
import utils.string_format as sf
from utils.logger import setup_logger

PLATFORM_SYSTEM = platform.system()
RESULTS_PATH = str(rt.get_results_root() / "")


@with_default_category("Sub Menu Tools")
class SubMenuCommandSet(CommandSet):
    """Register every tool category as a shell command."""

    def do_web_hacking(self, _):
        "Web Hacking — scanners, fuzzers, nuclei, CMS detection"
        wh_cs.main()

    def do_password_crack(self, _):
        "Password Cracking — hashcat, john, hydra, crowbar"
        pc.main()

    def do_evasion(self, _):
        "Evasion — WAF detection, load balancers, AV bypass"
        evasion.main()

    def do_wifi_hacking(self, _):
        "Wi-Fi Hacking — aircrack, hostapd, captive portal, WPS"
        wifi.main()

    def do_ad_hacking(self, _):
        "Active Directory — impacket, bloodhound, certipy, relay"
        ad_cs.main()

    def do_active_info(self, _):
        "Active Info Gathering — Nmap scans, DNS, gitleaks"
        aig.main()

    def do_passive_info(self, _):
        "Passive Info Gathering — whois, theHarvester, OSINT"
        pig.main()

    def do_exploitation(self, _):
        "Exploitation — msfvenom, searchsploit, listeners"
        exploit.main()

    def do_post_exploitation(self, _):
        "Post-Exploitation — privesc, enumeration, tunneling"
        postex.main()

    def do_osint(self, _):
        "OSINT — amass, assetfinder, httpx, dnsenum, gau"
        osint.main()

    def do_reporting(self, _):
        "Reporting — generate reports from task logs"
        report.main()


@with_default_category("Main commands")
class NetspionShell(cmd2.Cmd):
    """Root shell with quick-launch tools and settings."""

    def __init__(self):
        super().__init__()
        self.port = "4444"
        self.addr = "127.0.0.1"
        self.default_category = "cmd2 Built-in Commands"

        self.intro = sf.text(
            "\nWelcome to Netspion. "
            "Use 'help' / 'help -v' / 'help <topic>'.\n"
        )
        self.prompt = sf.success("(netspion): ")

        self.add_settable(cmd2.Settable("port", str, "Default port", self))
        self.add_settable(cmd2.Settable("addr", str, "Default IP address", self))

        for key in ("debug", "allow_style", "always_show_hint", "echo",
                     "feedback_to_output", "max_completion_items", "quiet", "timing"):
            try:
                self.remove_settable(key)
            except Exception:
                pass

        self.poutput(sf.title("""
  _   _      _             _
 | \\ | |    | |           (_)
 |  \\| | ___| |_ ___ _ __  _  ___  _ __
 | . ` |/ _ \\ __/ __| '_ \\| |/ _ \\| '_ \\
 | |\\  |  __/ |_\\__ \\ |_) | | (_) | | | |
 |_| \\_|\\___|\\__|___/ .__/|_|\\___/|_| |_|
                    | |
                    |_|
"""))
        self.poutput(sf.info("RUNNING ON: ") + sf.success(f"{PLATFORM_SYSTEM} {platform.release()}"))
        self.poutput(sf.info("RESULTS:     ") + sf.success(RESULTS_PATH))
        self.poutput(sf.info("SUBMENUS:    ") + sf.success(
            "web_hacking, password_crack, evasion, wifi_hacking, "
            "ad_hacking, active_info, passive_info, exploitation, "
            "post_exploitation, osint, reporting"
        ))

    def do_netcat(self, _):
        "Start netcat listener on current port/addr"
        rt.runBackground(["nc", "-l", "-p", self.port, "-s", self.addr, "-v"])

    def do_httpsrv(self, _):
        "Start Python2 SimpleHTTPServer on current directory"
        rt.runBackground(["python2", "-m", "SimpleHTTPServer"])

    def do_smbsrv(self, _):
        "Start impacket SMB2 server"
        rt.runBackground([
            "impacket-smbserver", "-smb2support", "netspionSMB",
            str(rt.get_results_root() / "SMBServer"),
        ])

    def do_clear(self, _):
        "Clear the terminal screen"
        import subprocess, os as _os
        subprocess.run(["cmd", "/c", "cls"] if _os.name == "nt" else ["clear"], check=False)


def main():
    setup_logger(rt.get_results_root())
    init.main()
    NetspionShell().cmdloop()


if __name__ == "__main__":
    main()
