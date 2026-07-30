"""Passive Information Gathering — whois, theHarvester, browser-based OSINT."""

from __future__ import annotations

import platform
import webbrowser

from cmd2 import with_default_category

import utils.run_task as rt
import utils.string_format as sf
from utils.base_shell import BaseShell
from utils.check_var import check_vars
from utils.validation import safe_filename

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class PassiveIGShell(BaseShell):
    def __init__(self):
        super().__init__("Passive-IG", "Passive Information Gathering")
        self.domain = ""
        self.limit = "500"
        self.add_settable(cmd2.Settable("domain", str, "Target Domain", self))
        self.add_settable(cmd2.Settable("limit", str, "theHarvester result limit", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def do_whois(self, arg):
        "WHOIS lookup"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(["whois", self.domain], self.resultsPath + safe_filename(self.domain) + "/")

    def do_theharvester(self, arg):
        "theHarvester OSINT"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "limit", "value": self.limit}]):
            rt.runBackground(["theHarvester", "-d", self.domain, "-l", self.limit, "-f", self.resultsPath + safe_filename(self.domain) + "/", "-b", "all"])

    def do_shodan(self, arg):
        "Open Shodan"
        webbrowser.open("https://www.shodan.io", new=2)

    def do_censys(self, arg):
        "Open Censys"
        webbrowser.open("https://search.censys.io", new=2)

    def do_google_db(self, arg):
        "Open Google Hacking Database"
        webbrowser.open("https://www.exploit-db.com/google-hacking-database", new=2)

    def do_archiveorg(self, arg):
        "Open Archive.org"
        webbrowser.open("https://archive.org", new=2)

    def do_dnsdumpster(self, arg):
        "Open DNSDumpster"
        webbrowser.open("https://dnsdumpster.com/", new=2)

    def do_internalallthings(self, arg):
        "Open InternalAllTheThings"
        webbrowser.open("https://swisskyrepo.github.io/InternalAllTheThings/", new=2)

    def do_hackerone(self, arg):
        "Open HackerOne Hacktivity"
        webbrowser.open("https://hackerone.com/hacktivity", new=2)

    def do_exploitdb(self, arg):
        "Open Exploit-DB"
        webbrowser.open("https://www.exploit-db.com", new=2)


def main():
    PassiveIGShell().cmdloop()
