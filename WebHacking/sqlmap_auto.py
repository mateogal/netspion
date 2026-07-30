"""Legacy standalone SQLMap automation.

This module provides an interactive SQLMap automation script.
It is kept for backwards compatibility and can be launched from the
web hacking sub-shell.

Usage:
    from WebHacking.sqlmap_auto import interactive_sqlmap
    interactive_sqlmap()
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys

from utils import run_task as rt

OUTPUT_LOCATION = "/tmp/SQLMap-Auto/"
PLATFORM_SYSTEM = platform.system()


def run_check(scan_type: str, url: str, file_path: str, command: str | list[str]) -> None:
    if isinstance(command, str):
        command_list = command.split()
    else:
        command_list = list(command)

    if scan_type.lower() == "u":
        argv = ["sqlmap", "-u", url, "--risk", "3", "--batch", "--random-agent",
                *command_list, "--output-dir=" + OUTPUT_LOCATION]
    elif scan_type.lower() == "f":
        argv = ["sqlmap", "-l", file_path, "--risk", "3", "--batch", "--random-agent",
                *command_list, "--output-dir=" + OUTPUT_LOCATION]
    else:
        print("Wrong scan type")
        return

    rt.normalShell(argv, timeout=1800)


def interactive_sqlmap() -> None:
    os.makedirs(OUTPUT_LOCATION, exist_ok=True)
    print(f"Running on: {PLATFORM_SYSTEM} {platform.release()} {platform.version()}")
    scan_type = ""
    url = ""
    file_path = ""

    while True:
        print(f"ALL RESULTS WILL BE STORED IN {OUTPUT_LOCATION}")
        operation = input("""
[1] Set URL scan or File scan
[2] SQLi retrieve DBMS current user
[3] SQLi enum DBMS users passwords hashes
[4] SQLi list databases
[5] SQLi list tables
[6] SQLi list columns
[7] SQLi dump database info
[8] SQLi prompt for interactive SQL shell
[9] Custom command (SHELL)
[0] Exit
Select operation: """)

        try:
            operation = int(operation)
        except ValueError:
            print("Invalid option")
            continue

        if operation == 1:
            scan_type = input("URL or File [u/f]: ").strip()
            if scan_type.lower() == "f":
                file_path = input("File location: ").strip()
            elif scan_type.lower() == "u":
                url = input("URL: ").strip()
            else:
                print("Wrong type")
        elif operation == 2:
            run_check(scan_type, url, file_path, "--current-user")
        elif operation == 3:
            run_check(scan_type, url, file_path, "--passwords")
        elif operation == 4:
            run_check(scan_type, url, file_path, "--dbs")
        elif operation == 5:
            run_check(scan_type, url, file_path, "--tables")
        elif operation == 6:
            run_check(scan_type, url, file_path, "--columns")
        elif operation == 7:
            bd = input("Database name: ").strip()
            run_check(scan_type, url, file_path, [["-D"], [bd], ["--dump-all"]])
        elif operation == 8:
            run_check(scan_type, url, file_path, "--sql-shell")
        elif operation == 9:
            print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
            cmd = input("Command: ").strip()
            subprocess.run(cmd, shell=True, check=False)
        elif operation == 0:
            break
        else:
            print("Invalid option")

        input("\nPress any key to continue ")


if __name__ == "__main__":
    interactive_sqlmap()
