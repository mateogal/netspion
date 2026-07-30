"""Password cracking module — hashcat, john, hydra, crowbar, hash-id."""

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
class PasswordCrackingShell(BaseShell):
    def __init__(self):
        super().__init__("Pwd-Crack", "Password cracking & brute-force")
        self.encode = "*"
        self.hash_file = ""
        self.wordlist = ""
        self.user = ""
        self.target = ""
        self.service = "ssh"
        self.port = "22"
        self.add_settable(cmd2.Settable("encode", str, "Hash type (-m) [* = auto]", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist file path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("hash_file", str, "Hash file path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("user", str, "Username for brute-force", self))
        self.add_settable(cmd2.Settable("target", str, "Target IP", self))
        self.add_settable(cmd2.Settable("service", str, "Service for hydra (ssh,rdp,ftp,smb,http-post-form,...)", self))
        self.add_settable(cmd2.Settable("port", str, "Target port", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    # ── Hashcat ───────────────────────────────────────────────────────

    def do_hashcat_bf(self, arg):
        "Hashcat brute force"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            cmd = ["hashcat", "-a", "3"]
            if self.encode != "*":
                cmd.extend(["-m", self.encode])
            cmd.append(self.hash_file)
            rt.runBackground(cmd)

    def do_hashcat_wl(self, arg):
        "Hashcat wordlist attack"
        if check_vars([{"name": "hash_file", "value": self.hash_file}, {"name": "wordlist", "value": self.wordlist}]):
            cmd = ["hashcat"]
            if self.encode != "*":
                cmd.extend(["-m", self.encode])
            cmd.extend(["-a", "0", self.hash_file, self.wordlist])
            rt.runBackground(cmd)

    def do_hashcat_rules(self, arg):
        "Hashcat wordlist + rules"
        if check_vars([{"name": "hash_file", "value": self.hash_file}, {"name": "wordlist", "value": self.wordlist}]):
            cmd = ["hashcat"]
            if self.encode != "*":
                cmd.extend(["-m", self.encode])
            cmd.extend(["-a", "0", self.hash_file, self.wordlist, "-r", "/usr/share/hashcat/rules/best64.rule"])
            rt.runBackground(cmd)

    def do_hashcat_show(self, arg):
        "Show cracked hashes"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            cmd = ["hashcat", "--show"]
            if self.encode != "*":
                cmd.extend(["-m", self.encode])
            cmd.append(self.hash_file)
            rt.runBackground(cmd)

    # ── John ──────────────────────────────────────────────────────────

    def do_john_bf(self, arg):
        "JohnTheRipper brute force"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            cmd = ["john"]
            if self.encode != "*":
                cmd.append("--format=" + self.encode)
            cmd.append(self.hash_file)
            rt.runBackground(cmd)

    def do_john_wl(self, arg):
        "JohnTheRipper wordlist"
        if check_vars([{"name": "hash_file", "value": self.hash_file}, {"name": "wordlist", "value": self.wordlist}]):
            cmd = ["john"]
            if self.encode != "*":
                cmd.append("--format=" + self.encode)
            cmd.extend([f"--wordlist={self.wordlist}", self.hash_file])
            rt.runBackground(cmd)

    def do_john_show(self, arg):
        "Show cracked passwords"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            rt.runBackground(["john", "--show", self.hash_file])

    # ── Hydra (online brute-force) ────────────────────────────────────

    def do_hydra_bf(self, arg):
        "Hydra online brute-force"
        if check_vars([{"name": "target", "value": self.target}, {"name": "user", "value": self.user}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground([
                "hydra", "-l", self.user, "-P", self.wordlist,
                "-o", self.resultsPath + f"hydra_{safe_filename(self.target)}_{self.service}.txt",
                self.target, self.service,
            ])

    def do_hydra_userlist(self, arg):
        "Hydra with userlist + passlist"
        if check_vars([{"name": "target", "value": self.target}, {"name": "wordlist", "value": self.wordlist}]):
            usr_file = input("Username list path: ").strip()
            rt.runBackground([
                "hydra", "-L", usr_file, "-P", self.wordlist,
                "-o", self.resultsPath + f"hydra_{safe_filename(self.target)}_{self.service}.txt",
                self.target, self.service,
            ])

    # ── Crowbar ───────────────────────────────────────────────────────

    def do_crowbar_rdp(self, arg):
        "Crowbar RDP brute-force"
        if check_vars([{"name": "target", "value": self.target}, {"name": "user", "value": self.user}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground([
                "crowbar", "-b", "rdp", "-s", f"{self.target}/{self.port}",
                "-u", self.user, "-C", self.wordlist,
            ])

    def do_crowbar_ssh(self, arg):
        "Crowbar SSH brute-force (key-based)"
        if check_vars([{"name": "target", "value": self.target}, {"name": "user", "value": self.user}]):
            key_file = input("Private key file path: ").strip()
            rt.runBackground([
                "crowbar", "-b", "ssh", "-s", f"{self.target}/{self.port}",
                "-u", self.user, "-k", key_file,
            ])

    # ── Hash identification ───────────────────────────────────────────

    def do_hashid(self, arg):
        "Identify hash type (hashid)"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            rt.runBackground(["hashid", "-m", "-j", self.hash_file])

    def do_hash_identifier(self, arg):
        "Identify hash type (hash-identifier)"
        if check_vars([{"name": "hash_file", "value": self.hash_file}]):
            rt.runBackground(["hash-identifier", self.hash_file])


def main():
    PasswordCrackingShell().cmdloop()
