import cmd2, subprocess, platform, os
import utils.run_task as rt
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf
from utils.check_var import check_vars
from datetime import datetime

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class PasswordCrackingShell(cmd2.Cmd):
    intro = sf.text(
        "KerErr Tools Password Cracking Sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(kererr Pwd-Crack): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/KerErrTools/PasswordCrack/"
        self.encode = "*"
        self.hash_file = ""
        self.wordlist = ""
        self.add_settable(
            cmd2.Settable("encode", str, "Encode type [default: auto]", self)
        )
        self.add_settable(
            cmd2.Settable(
                "wordlist",
                str,
                "Wordlist file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
        self.add_settable(
            cmd2.Settable(
                "hash_file",
                str,
                "Hash file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
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

    def do_hashcat_bf(self, arg):
        "Hashcat brute force password crack"
        if check_vars(
            [
                {"name": "encode", "value": self.encode},
                {"name": "hash_file", "value": self.hash_file},
            ]
        ):
            if self.encode == "*":
                rt.runBackground(
                    [
                        "hashcat",
                        "-a",
                        "3",
                        self.hash_file,
                    ]
                )
            else:
                rt.runBackground(
                    [
                        "hashcat",
                        "-m",
                        self.encode,
                        "-a",
                        "3",
                        self.hash_file,
                    ]
                )

    def do_hashcat_wl(self, arg):
        "Hashcat wordlist file (dictionary) password crack"
        if check_vars(
            [
                {"name": "encode", "value": self.encode},
                {"name": "hash_file", "value": self.hash_file},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.runBackground(
                [
                    "hashcat",
                    "-m",
                    self.encode,
                    "-a",
                    "0",
                    self.hash_file,
                    self.wordlist,
                ]
            )

    def do_john_bf(self, arg):
        "JohnTheRipper brute force password crack"
        if check_vars(
            [
                {"name": "encode", "value": self.encode},
                {"name": "hash_file", "value": self.hash_file},
            ]
        ):
            rt.runBackground(["john", "--format=" + self.encode, self.hash_file])

    def do_john_wl(self, arg):
        "JohnTheRipper wordlist file (dictionary) password crack"
        if check_vars(
            [
                {"name": "encode", "value": self.encode},
                {"name": "hash_file", "value": self.hash_file},
                {"name": "wordlist", "value": self.wordlist},
            ]
        ):
            rt.runBackground(
                [
                    "john",
                    "--format=" + self.encode,
                    "--wordlist=",
                    self.wordlist,
                    self.hash_file,
                ]
            )


def main():
    PasswordCrackingShell().do_clear(1)
    PasswordCrackingShell().cmdloop()
