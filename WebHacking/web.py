"""Web Hacking module — scanners, fuzzers, CMS checks, nuclei, httpx."""

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
class WebHacking(BaseShell):
    def __init__(self):
        super().__init__("WebHacking", "Web application attacks")
        self.url = ""
        self.domain = ""
        self.wordlist = ""
        self.cookies = ""
        self.request_file = ""
        self.log_level = ""
        self.bodyData = ""
        self.threads = "50"
        self.add_settable(cmd2.Settable("url", str, "Target URL", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist file path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("domain", str, "Target domain", self))
        self.add_settable(cmd2.Settable("request_file", str, "Request file path", self, completer=cmd2.Cmd.path_complete))
        self.add_settable(cmd2.Settable("log_level", str, "Log level", self))
        self.add_settable(cmd2.Settable("bodyData", str, "POST body data", self))
        self.add_settable(cmd2.Settable("cookies", str, "Cookies", self))
        self.add_settable(cmd2.Settable("threads", str, "Thread count", self))
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    # ── Subdomain discovery ───────────────────────────────────────────

    def do_find_subdomains_sf(self, arg):
        "Subdomain finder (SubFinder)"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(["subfinder", "-d", self.domain, "-oJ", "-o", self.resultsPath + f"subfinder_{safe_filename(self.domain)}.json"])

    def do_find_subdomains_gb(self, arg):
        "Subdomain finder (GoBuster DNS)"
        if check_vars([{"name": "domain", "value": self.domain}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground(["gobuster", "dns", "-d", self.domain, "-w", self.wordlist, "-o", self.resultsPath + f"gobuster_dns_{safe_filename(self.domain)}.txt"])

    def do_find_url_directories(self, arg):
        "URL directory/file brute force (GoBuster dir)"
        if check_vars([{"name": "url", "value": self.url}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground(["gobuster", "dir", "-u", self.url, "-w", self.wordlist, "-o", self.resultsPath + f"gobuster_url_{safe_filename(self.url)}.txt"])

    def do_fuzzing_url_params(self, arg):
        "URL parameter fuzzing (Ffuf)"
        if check_vars([{"name": "url", "value": self.url}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground(["ffuf", "-u", self.url, "-w", self.wordlist, "-recursion", "-o", self.resultsPath + f"ffuf_url_{safe_filename(self.url)}.json"])

    def do_fuzzing_req_file(self, arg):
        "Request file fuzzing (Ffuf)"
        if check_vars([{"name": "request_file", "value": self.request_file}, {"name": "wordlist", "value": self.wordlist}]):
            rt.runBackground(["ffuf", "-request", self.request_file, "-w", self.wordlist, "-o", self.resultsPath + f"ffuf_req_{safe_filename(self.request_file)}.json"])

    # ── Vuln scanners ─────────────────────────────────────────────────

    def do_nuclei(self, arg):
        "Nuclei vulnerability scanner"
        if check_vars([{"name": "url", "value": self.url}]):
            extra = ["-t", "~/nuclei-templates/"] if os.path.isdir(os.path.expanduser("~/nuclei-templates")) else []
            rt.runBackground(["nuclei", "-u", self.url, "-o", self.resultsPath + f"nuclei_{safe_filename(self.url)}.txt", *extra])

    def do_nuclei_tech(self, arg):
        "Nuclei technology detection"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["nuclei", "-u", self.url, "-id", "tech-detect", "-o", self.resultsPath + f"nuclei_tech_{safe_filename(self.url)}.txt"])

    def do_httpx(self, arg):
        "httpx HTTP probe (pipe from file)"
        path = str(arg).strip()
        target = path if path else self.url
        if not target:
            print("Usage: httpx <urls_file> or set url")
            return
        rt.runBackground(["httpx", "-silent", "-title", "-status-code", "-web-server", "-content-length", "-o", self.resultsPath + "httpx_results.txt"], self.resultsPath)

    def do_katana(self, arg):
        "Katana web crawler"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["katana", "-u", self.url, "-d", "2", "-o", self.resultsPath + f"katana_{safe_filename(self.url)}.txt"])

    def do_wpscan(self, arg):
        "WPScan WordPress vulnerability scanner"
        if check_vars([{"name": "url", "value": self.url}]):
            extra = ["--random-user-agent", "-e", "vp,vt,tt"]
            if self.cookies:
                extra.extend(["--cookie", self.cookies])
            rt.runBackground(["wpscan", "--url", self.url, *extra, "-o", self.resultsPath + f"wpscan_{safe_filename(self.url)}.txt"])

    def do_commix(self, arg):
        "Commix command injection tester"
        if check_vars([{"name": "url", "value": self.url}]):
            extra = []
            if self.log_level:
                extra.extend(["--level", self.log_level])
            if self.cookies:
                extra.extend(["--cookie", self.cookies])
            if self.bodyData:
                extra.extend(["--data", self.bodyData])
            rt.runBackground(["commix", "-u", self.url, *extra, "--output-dir=" + self.resultsPath])

    # ── CMS / tech detection ──────────────────────────────────────────

    def do_whatweb(self, arg):
        "WhatWeb technology detection"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["whatweb", "-v", self.url, "--log-verbose=" + self.resultsPath + f"whatweb_{safe_filename(self.url)}.txt"])

    def do_waf_detector(self, arg):
        "WAF detection (wafw00f)"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["wafw00f", self.url, "-o", self.resultsPath + "wafw00f.json"])

    # ── JS / secrets ──────────────────────────────────────────────────

    def do_gitleaks(self, arg):
        "GitLeaks secret scanner (git repo)"
        path = str(arg).strip() or self.request_file
        if not path or not os.path.isdir(path):
            print("Usage: gitleaks <git_repo_path> or set request_file")
            return
            safe = safe_filename(path)
            rt.runBackground(["gitleaks", "detect", "-v", "-s", path, "-r", f"{self.resultsPath}gitleaks_{safe}.json"])

    def do_jsanalyze(self, arg):
        "Analyze JavaScript files from URL"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(["katana", "-u", self.url, "-d", "1", "-o", self.resultsPath + "katana_js.txt"])
            print("Use: cat katana_js.txt | grep '\\.js$' | while read u; do curl -s \"$u\" | grep -i 'api\\|token\\|secret\\|key'; done")


def main():
    WebHacking().cmdloop()
