import cmd2, subprocess, platform, os
import utils.run_task as rt
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf
from utils.check_var import check_vars

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class EvasionShell(cmd2.Cmd):
    intro = sf.text(
        "netspion Tools Evasion Sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(netspion Evasion): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/Evasion/"
        self.url = ""
        self.domain = ""
        self.wordlist = ""
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
        self.do_help("-v")

    def do_clear(self, arg):
        "Clear screen"
        subprocess.run(["clear"], shell=True)

    def do_lb_detector(self, arg):
        "Load Balancing Detector (AGGRESSIVE)"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(["lbd", self.domain])

    def do_waf_detector(self, arg):
        "WAF URL detector"
        if check_vars([{"name": "url", "value": self.url}]):
            rt.runBackground(
                ["wafw00f", self.url, "-o", self.resultsPath + "wafw00f.json"]
            )

    def do_csharp_bypass(self, arg):  # Open C# Antivirus Bypass script file
        "C# script to bypass Antivirus"
        self.do_edit("./EthicalHacking/Evasion/Windows_Exec_ByPass.cs")


def main():
    EvasionShell().do_clear(1)
    EvasionShell().cmdloop()
