"""Active Information Gathering — Nmap scans, DNS, gitleaks."""

from __future__ import annotations

import os
import platform

import cmd2
from cmd2 import with_default_category

import utils.run_task as rt
import utils.string_format as sf
from utils.base_shell import BaseShell
from utils.check_var import check_vars
from utils.validation import safe_filename

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class ActiveIGShell(BaseShell):
    def __init__(self):
        super().__init__("Active-IG", "Active Information Gathering")
        self.network = ""
        self.domain = ""
        self.pkt_fragment = "No"
        self.git_repo = ""
        self.ports = "top-1000"
        self.rate = "1000"
        self.add_settable(cmd2.Settable("network", str, "Target network (192.168.1.0/24)", self))
        self.add_settable(cmd2.Settable("domain", str, "Target domain", self))
        self.add_settable(cmd2.Settable("pkt_fragment", str, "Nmap fragment mode", self, choices=["Yes", "No"]))
        self.add_settable(cmd2.Settable("git_repo", str, "Git repo path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("ports", str, "Port range or top-1000", self))
        self.add_settable(cmd2.Settable("rate", str, "Nmap rate limiting", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def _nmap_base(self, extra_args: list[str], suffix: str):
        if check_vars([{"name": "network", "value": self.network}]):
            safe = safe_filename(self.network)
            nmap_args = ["nmap", "-v", "--reason"]
            if self.rate:
                nmap_args.extend(["--min-rate", self.rate])
            nmap_args.extend(extra_args)
            if self.ports and self.ports != "top-1000":
                nmap_args.extend(["-p", self.ports])
            nmap_args.extend([self.network, "-oA", self.resultsPath + suffix + safe, "--webxml"])
            rt.runBackground(nmap_args)

    def do_host_discover(self, arg):
        "Nmap host discovery"
        if check_vars([{"name": "network", "value": self.network}]):
            safe = safe_filename(self.network)
            if self.pkt_fragment == "No":
                rt.runBackground(["nmap", "-v", "--reason", "-sn", "-PS", self.network, "-oA", self.resultsPath + "hostDiscovery_" + safe, "--webxml"])
            else:
                try:
                    mtu = int(input("MTU (multiple of 8): "))
                except ValueError:
                    print("Invalid MTU")
                    return
                if mtu < 8 or mtu > 65528 or mtu % 8 != 0:
                    print("Invalid MTU")
                    return
                rt.runBackground(["nmap", "-v", "--reason", "-sS", "-p-", "--mtu", str(mtu), self.network, "-oA", self.resultsPath + "mtu_hostDiscovery_" + safe, "--webxml"])

    def do_syn_port_scan(self, arg):
        "Nmap SYN scan (stealth + fast)"
        self._nmap_base(["-sS"], "portScanSYN_")

    def do_tcp_port_scan(self, arg):
        "Nmap TCP connect scan"
        self._nmap_base(["-sT"], "portScanTCP_")

    def do_udp_port_scan(self, arg):
        "Nmap UDP scan (slow)"
        self._nmap_base(["-sU"], "portScanUDP_")

    def do_aggressive_scan(self, arg):
        "Nmap aggressive (-A) full scan"
        self._nmap_base(["-A"], "portScanAll_")

    def do_service_scan(self, arg):
        "Nmap service/version detection (-sV)"
        self._nmap_base(["-sV", "--version-intensity", "9"], "serviceScan_")

    def do_os_detection(self, arg):
        "Nmap OS detection (-O)"
        self._nmap_base(["-O", "--osscan-guess"], "osDetect_")

    def do_vuln_scan(self, arg):
        "Nmap vulnerability scripts (--script vuln)"
        self._nmap_base(["-sV", "--script", "vuln"], "vulnScan_")

    def do_nse_all(self, arg):
        "Nmap all safe NSE scripts"
        self._nmap_base(["-sV", "--script", "safe"], "nseSafe_")

    def do_nse_smb(self, arg):
        "Nmap SMB-specific NSE scripts"
        self._nmap_base(["-sV", "--script", "smb-enum*"], "nseSMB_")

    def do_nse_http(self, arg):
        "Nmap HTTP-specific NSE scripts"
        self._nmap_base(["-sV", "--script", "http-*"], "nseHTTP_")

    def do_nslookup_dig(self, arg):
        "DNS lookup with nslookup + dig"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(["nslookup", "-q=any", self.domain], self.resultsPath + safe_filename(self.domain) + "/")
            rt.runBackground(["dig", self.domain, "ANY", "+trace"], self.resultsPath + safe_filename(self.domain) + "/")

    def do_gitleaks(self, arg):
        "GitLeaks secret scanner"
        if check_vars([{"name": "git_repo", "value": self.git_repo}]):
            repo = safe_filename(self.git_repo)
            rt.runBackground(["gitleaks", "detect", "-v", "-s", self.git_repo, "-r", f"{self.resultsPath}gitleaks_{repo}.json"])


def main():
    ActiveIGShell().cmdloop()
