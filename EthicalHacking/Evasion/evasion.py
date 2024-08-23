import subprocess
import os
import webbrowser
from utils import string_format, run_task

def main(resultsPath):
    resultsPath = resultsPath + "Evasion/"
    os.makedirs(resultsPath, exist_ok=True)

    while True:
        print(string_format.title("EVASION & DETECTION TOOLS"))
        print(
            string_format.info("\n ALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        try:
            operation = int(
                input(
                    """
[1] Load Balancing Detector
[2] WAF Detector
[3] WAF Bypass Tools
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
            case 1: # LB detector
                
                break
            case 2: # WAF Detector
                url = str(input("URL: "))
                run_task.newTerminal([
                    "wafw00f",
                    url,
                    "-o",
                    resultsPath + "wafw00f.json"
                ])
                break
            case 3: # WAF Bypass tools
                webbrowser.open("https://waf-bypass.com/")
                break
            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG\n")
                command = str(input("Command: "))
                run_task.normalShell(command)

            case 99:
                break

            case _:
                print("No option available")
        input("\nPress enter to continue ")
        subprocess.run(["clear"], shell=True)