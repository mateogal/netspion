import cmd2, platform, os, webbrowser
import utils.run_task as rt
from cmd2 import with_default_category
import utils.string_format as sf
from utils.check_var import check_vars
from utils.utils_shell import UtilsCommandSet

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class PassiveIGShell(cmd2.Cmd):
    intro = sf.text(
        "Netspion Passive Info-Gath Sub menu. Use 'help / help -v' for verbose / 'help <topic>' for details. \n"
    )
    prompt = sf.success("(netspion Passive-IG): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/Passive-IG/"
        self.domain = ""
        self.limit = "500"

        self.add_settable(cmd2.Settable("domain", str, "Target Domain", self))
        self.add_settable(
            cmd2.Settable(
                "limit", str, "Limit theHarvester search results (default: 500)", self
            )
        )

        self.register_command_set(UtilsCommandSet())
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

    def do_shodan(self, arg):
        "Open Shodan Website (GUI needed)"
        webbrowser.open("www.shodan.io", new=2)

    def do_google_db(self, arg):
        "Open Google Hacking Database Website (GUI needed)"
        webbrowser.open("https://www.exploit-db.com/google-hacking-database", new=2)

    def do_censys(self, arg):
        "Open Censys Website (GUI needed)"
        webbrowser.open("search.censys.io", new=2)

    def do_archiveorg(self, arg):
        "Open Archive.org Website (GUI needed)"
        webbrowser.open("archive.org", new=2)

    def do_dnsdumpster(self, arg):
        "Open DNSDumpster Website (GUI needed)"
        webbrowser.open("https://dnsdumpster.com/", new=2)

    def do_internalallthings(self, arg):
        "Open InternalAllTheThings Website (GUI needed)"
        webbrowser.open("https://swisskyrepo.github.io/InternalAllTheThings/", new=2)

    def do_whois(self, arg):
        "WHOIS"
        if check_vars([{"name": "domain", "value": self.domain}]):
            rt.runBackground(
                ["whois", self.domain], self.resultsPath + self.domain + "/"
            )

    def do_theharvester(self, arg):
        "TheHarvester OSINT"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "limit", "value": self.limit},
            ]
        ):
            rt.runBackground(
                [
                    "theHarvester",
                    "-d",
                    self.domain,
                    "-l",
                    self.limit,
                    "-f",
                    self.resultsPath + self.domain + "/",
                    "-b",
                    "all",
                ]
            )


def main():
    PassiveIGShell().do_clear(1)
    PassiveIGShell().cmdloop()
