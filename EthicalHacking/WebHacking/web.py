import subprocess
import os
from utils import string_format, run_task

def main(resultsPath):
    resultsPath = resultsPath + "Web/"
    os.makedirs(resultsPath, exist_ok=True)

    while True:
        subprocess.run(["clear"], shell=True)
        print(string_format.title("WEB HACKING"))
        print(
            string_format.info("\n ALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        try:
            operation = int(
                input(
                    """
[1] Find Subdomains (Subfinder)
[2] Find Subdomains (GoBuster)
[3] Find URL Directories (GoBuster)
[4] Fuzzing URL Parameters
[5] Fuzzing Request Parameters
[6] Web Vuln Exploit (Commix)
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
            case 1: # Find Subdomains
                domain = str(input("Domain: "))
                run_task.newTerminal([
                    "subfinder",
                    "-d",
                    domain,
                    "-oJ",
                    resultsPath + "subfinder.json"
                ])
            
            case 3: # GoBuster find directories
                url = str(input("URL: "))
                wordlist = str(input("Wordlist path: "))
                run_task.newTerminal([
                    "gobuster",
                    "dir",
                    "-u",
                    url,
                    "-w",
                    wordlist
                ])

            case 4: # Ffuf url
                url = str(input("URL with FUZZ words [i.e http://127.0.0.1/FUZZ]: "))
                wordlist = str(input("Wordlist path: "))
                run_task.newTerminal([
                    "ffuf",
                    "-u",
                    url,
                    "-w",
                    wordlist,
                    '-recursion',
                    "-o",
                    resultsPath + "ffuf_url_parameters.json"
                ])
                break

            case 5: # Ffuf request file
                request = str(input("Request File path: "))
                wordlist = str(input("Wordlist path: "))
                run_task.newTerminal([
                    "ffuf",
                    "-request",
                    request,
                    "-w",
                    wordlist,
                    "-o",
                    resultsPath + "ffuf_request_parameters.json"
                ])
                break

            case 6: # Vuln Exploit Commix
                url = str(input("URL: "))
                cookies = str(input("Cookie String (optional): "))
                bodyData = str(input("Body data (optional): "))
                level = str(input("Scan level (1-3): "))
                run_task.newTerminal([
                    "commix",
                    "-u",
                    url,
                    "--level",
                    level,
                    "--cookie=" + cookies,
                    "--data=" + bodyData,
                    "--output-dir=" + resultsPath
                    
                ])
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