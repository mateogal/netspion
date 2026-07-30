"""OSINT module — enhanced reconnaissance with Amass, AssetFinder, httpx, etc."""

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
class OsintShell(BaseShell):
    def __init__(self):
        super().__init__("OSINT", "Advanced OSINT & Reconnaissance")
        self.domain = ""
        self.wordlist = ""
        self.threads = "10"
        self.add_settable(cmd2.Settable("domain", str, "Target domain", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist path", self, completer=BaseShell.path_complete))
        self.add_settable(cmd2.Settable("threads", str, "Thread count (default 10)", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def do_amass(self, arg):
        "Amass subdomain enumeration (passive + active)"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "amass", "enum", "-passive", "-d", self.domain,
                "-o", self.resultsPath + f"amass_{safe_filename(self.domain)}.txt",
            ])

    def do_amass_intel(self, arg):
        "Amass open-source intel gathering"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "amass", "intel", "-d", self.domain,
                "-o", self.resultsPath + f"amass_intel_{safe_filename(self.domain)}.txt",
            ])

    def do_assetfinder(self, arg):
        "AssetFinder subdomain enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "assetfinder", "--subs-only", self.domain,
            ], self.resultsPath)

    def do_httpx(self, arg):
        "httpx HTTP probing (pipe from subdomain list)"
        path = str(arg).strip()
        target = path if path else self.domain
        if not target:
            print("Usage: httpx <subdomains_file> or set domain")
            return
        rt.runBackground([
            "httpx", "-silent", "-title", "-status-code", "-content-length",
            "-o", self.resultsPath + f"httpx_{safe_filename(target)}.txt",
        ], self.resultsPath)

    def do_dns_enum(self, arg):
        "dnsenum DNS enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "dnsenum", "--enum", "-f", self.wordlist if self.wordlist else "/usr/share/wordlists/dnsmap.txt",
                self.domain, "-o", self.resultsPath + f"dnsenum_{safe_filename(self.domain)}.xml",
            ])

    def do_dns_recon(self, arg):
        "dnsrecon DNS enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "dnsrecon", "-d", self.domain, "-t", "std",
                "--csv", self.resultsPath + f"dnsrecon_{safe_filename(self.domain)}.csv",
            ])

    def do_sublist3r(self, arg):
        "Sublist3r subdomain enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "sublist3r", "-d", self.domain,
                "-o", self.resultsPath + f"sublist3r_{safe_filename(self.domain)}.txt",
            ])

    def do_findomain(self, arg):
        "Findomain subdomain enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "findomain", "-t", self.domain,
                "-o", self.resultsPath + f"findomain_{safe_filename(self.domain)}.txt",
            ])

    def do_enum4linux(self, arg):
        "enum4linux SMB/CIFS enumeration"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "enum4linux", "-a", self.domain,
            ], self.resultsPath)

    def do_gau(self, arg):
        "GAU — Get All URLs from Wayback/etc"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "gau", "--o", self.resultsPath + f"gau_{safe_filename(self.domain)}.txt", self.domain,
            ])

    def do_waybackurls(self, arg):
        "Wayback Machine URL extractor"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground([
                "waybackurls", self.domain,
            ], self.resultsPath)

    def do_shodan(self, arg):
        "Open Shodan.io"
        webbrowser.open("https://www.shodan.io", new=2)

    def do_censys(self, arg):
        "Open Censys.io"
        webbrowser.open("https://search.censys.io", new=2)

    def do_dehashed(self, arg):
        "Open DeHashed (breach data search)"
        webbrowser.open("https://dehashed.com", new=2)

    def do_full_recon(self, arg):
        "Run full recon suite: amass + assetfinder + sublist3r + dnsenum + httpx"
        if check_vars([{"name": "domain", "value": self.domain}]):
            domain_safe = safe_filename(self.domain)
            print(sf.info("Starting full reconnaissance suite..."))
            rt.runBackground(["amass", "enum", "-passive", "-d", self.domain, "-o", f"{self.resultsPath}amass_{domain_safe}.txt"])
            rt.runBackground(["assetfinder", "--subs-only", self.domain], self.resultsPath)
            rt.runBackground(["sublist3r", "-d", self.domain, "-o", f"{self.resultsPath}sublist3r_{domain_safe}.txt"])
            rt.runBackground(["dnsenum", "--enum", self.domain, "-o", f"{self.resultsPath}dnsenum_{domain_safe}.xml"])
            rt.runBackground(["gau", "--o", f"{self.resultsPath}gau_{domain_safe}.txt", self.domain])
            print(sf.success("Reconnaissance tasks launched. Use check_processes to monitor."))


def main():
    OsintShell().cmdloop()
