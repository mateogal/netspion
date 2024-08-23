import cmd2, platform, subprocess
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf

PLATFORM_SYSTEM = platform.system()

@with_default_category("Main commands")
class ADHacking(cmd2.Cmd):
    intro = sf.text("KerErr Tools Active Directory Sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n")
    prompt = sf.success("(kererr AD-Hacking): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/KerErrTools/ActiveDirectory/"
        self.url = ""
        self.wordlist = ""
        self.add_settable(cmd2.Settable("url", str, "Domain URL", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist file path", self))
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

    def do_clear(self):
        "Clear screen"
        subprocess.run(["clear"], shell=True)


def main():
    ADHacking().do_clear()
    ADHacking().cmdloop()
