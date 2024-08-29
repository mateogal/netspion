import cmd2, subprocess, platform, os
import utils.run_task as rt
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf


PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class WebHacking(cmd2.Cmd):
    intro = sf.text(
        "KerErr Tools Web Hacking sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(kererr WebHacking): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/KerErrTools/Web/"
        self.url = ""
        self.domain = ""
        self.wordlist = ""
        self.cookies = ""
        self.request_file = ""
        self.log_level = ""
        self.bodyData = ""
        self.add_settable(cmd2.Settable("url", str, "Domain URL", self))
        self.add_settable(
            cmd2.Settable(
                "wordlist",
                str,
                "Wordlist file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
        self.add_settable(cmd2.Settable("domain", str, "Domain", self))
        self.add_settable(
            cmd2.Settable(
                "request_file",
                str,
                "Request file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
        self.add_settable(cmd2.Settable("log_level", str, "Log Level", self))
        self.add_settable(cmd2.Settable("bodyData", str, "Body Data", self))
        self.add_settable(cmd2.Settable("cookies", str, "Cookies", self))
        self.default_category = "cmd2 Built-in Commands"
        self.remove_settable("debug")
        self.remove_settable("allow_style")
        self.remove_settable("always_show_hint")
        self.remove_settable("echo")
        self.remove_settable("feedback_to_output")
        self.remove_settable("max_completion_items")
        self.remove_settable("quiet")
        self.remove_settable("timing")
        self.poutput(
            sf.info("RUNNING ON: ")
            + sf.success(PLATFORM_SYSTEM + platform.release() + platform.version())
        )
        self.poutput(
            sf.info("ALL RESULTS WILL BE STORED IN: ")
            + sf.success(self.resultsPath)
            + "\n"
        )
        os.makedirs(self.resultsPath, exist_ok=True)

    def do_clear(self, arg):
        "Clear screen"
        subprocess.run(["clear"], shell=True)

    def do_find_subdomains_sf(self, arg):  # Subfinder
        "Subdomain Finder (SubFinder)"
        if self.domain == "":
            self.poutput("Domain required")
            return
        rt.newTerminal(
            [
                "subfinder",
                "-d",
                self.domain,
                "-oJ",
                "-o",
                self.resultsPath + f"subfinder{self.domain}.json",
            ]
        )

    def do_find_subdomains_gb(self, arg):  # GoBuster
        "Subdomain Finder (GoBuster)"
        if self.domain == "" or self.wordlist == "":
            self.poutput("Domain and wordlist required")
            return
        rt.newTerminal(
            [
                "gobuster",
                "dns",
                "-d",
                self.domain,
                "-w",
                self.wordlist,
                "-o",
                self.resultsPath + f"gobuster_{self.domain}.txt",
            ]
        )

    def do_find_url_directories(self, arg):  # URL directories Finder
        "URL directories finder (GoBuster)"
        if self.url == "" or self.wordlist == "":
            self.poutput("URL and wordlist required")
            return
        rt.newTerminal(
            [
                "gobuster",
                "dir",
                "-u",
                self.url,
                "-w",
                self.wordlist,
                "-o",
                self.resultsPath + f"gobuster_{self.url}.txt",
            ]
        )

    def do_fuzzing_url_params(self, arg):  # URL params fuzz
        "URL parameters fuzz (Ffuf)"
        if self.url == "" or self.wordlist == "":
            self.poutput("URL and wordlist required")
            return
        rt.newTerminal(
            [
                "ffuf",
                "-u",
                self.url,
                "-w",
                self.wordlist,
                "-recursion",
                "-o",
                self.resultsPath + f"ffuf_url_parameters{self.url}.json",
            ]
        )

    def do_fuzzing_req_file(self, arg):  # Fuzzing from request file
        "Request file fuzz (Ffuf)"
        if self.request_file == "" or self.wordlist == "":
            self.poutput("Request file and wordlist required")
            return
        rt.newTerminal(
            [
                "ffuf",
                "-request",
                self.request_file,
                "-w",
                self.wordlist,
                "-o",
                self.resultsPath + f"ffuf_request_parameters{self.request_file}.json",
            ]
        )

    def do_web_vuln_exploit(self, arg):  # Web Vulnerabilities exploit
        "Exploit Web Vulnerabilities (Commix)"
        if (
            self.url == ""
            or self.log_level == ""
            or self.cookies == ""
            or self.bodyData == ""
        ):
            self.poutput("URL, Log Level, Cookies and Body Data required")
            return
        rt.newTerminal(
            [
                "commix",
                "-u",
                self.url,
                "--level",
                self.log_level,
                "--cookie=" + self.cookies,
                "--data=" + self.bodyData,
                "--output-dir=" + self.resultsPath,
            ]
        )


def main():
    WebHacking().do_clear(1)
    WebHacking().cmdloop()
