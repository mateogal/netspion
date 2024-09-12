import cmd2, platform, os
import utils.run_task as rt
from cmd2 import with_default_category
import utils.string_format as sf
from utils.check_var import check_vars
from utils.utils_shell import UtilsCommandSet

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class WebHacking(cmd2.Cmd):
    intro = sf.text(
        "Netspion Web Hacking sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(netspion WebHacking): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/Web/"
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
        self.register_command_set(UtilsCommandSet())
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
            sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(self.resultsPath)
        )
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def do_find_subdomains_sf(self, arg):  # Subfinder
        "Subdomain Finder (SubFinder)"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(
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
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.runBackground(
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
        if check_vars(
            [
                {"name": "url", "value": self.url},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.runBackground(
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
        if check_vars(
            [
                {"name": "url", "value": self.url},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.runBackground(
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
        if check_vars(
            [
                {"name": "requesT_file", "value": self.request_file},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.newTerminal(
                [
                    "ffuf",
                    "-request",
                    self.request_file,
                    "-w",
                    self.wordlist,
                    "-o",
                    self.resultsPath
                    + f"ffuf_request_parameters{self.request_file}.json",
                ]
            )

    def do_web_vuln_exploit(self, arg):  # Web Vulnerabilities exploit
        "Exploit Web Vulnerabilities (Commix)"
        if check_vars(
            [
                {"name": "url", "value": self.url},
                {"name": "log_level", "value": self.log_level},
                {"name": "cookies", "value": self.cookies},
                {"name": "bodyData", "value": self.bodyData},
            ]
        ):
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
