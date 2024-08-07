import subprocess
import os
from utils import string_format, run_task

def main(resultsPath):
    resultsPath = resultsPath + "Web/"
    os.makedirs(resultsPath, exist_ok=True)

    while True:
        print(string_format.title("WEB HACKING"))
        print(
            string_format.info("\n ALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        try:
            operation = int(
                input(
                    """
[1] Find Subdomains
[97] Manually set variables
[98] Custom Command (SHELL)
[99] Exit

Select operation: """
                )
            )
        except:
            operation = 0
        print(" \n")
        match operation:
            case 1: ## Find Subdomains
                domain = str(input("Domain: "))
                run_task.newTerminal([
                    "subfinder",
                    "-d",
                    domain
                ])
            
            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG\n")
                command = str(input("Command: "))
                run_task.normalShell(command)

            case 99:
                break

            case _:
                print("No option available")