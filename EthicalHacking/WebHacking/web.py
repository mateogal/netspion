import subprocess
import os
from utils import string_format, run_task, check_var


def main(resultsPath):
    resultsPath = resultsPath + "Web/"
    os.makedirs(resultsPath, exist_ok=True)

    domain = url = wordlist = cookies = request_file = log_level = bodyData = ""

    while True:
        subprocess.run(["clear"], shell=True)
        print(string_format.title("WEB HACKING"))
        print(
            string_format.info("\n ALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        print(string_format.info("\nCurrent variables values:\n"))
        print("Domain:", string_format.text(domain))
        print("URL:", string_format.text(url))
        print("Wordlist Path:", string_format.text(wordlist))
        print("Cookies String:", string_format.text(cookies))
        print("Request File Path:", string_format.text(request_file))
        print("Log level:", string_format.text(log_level))
        print("Body Data:", string_format.text(bodyData))
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
            case 1:  # Find Subdomains
                if check_var([domain]):
                    run_task.newTerminal(
                        [
                            "subfinder",
                            "-d",
                            domain,
                            "-oJ",
                            resultsPath + "subfinder.json",
                        ]
                    )
                break

            case 3:  # GoBuster find directories
                if check_var([url, wordlist]):
                    run_task.newTerminal(["gobuster", "dir", "-u", url, "-w", wordlist])
                break

            case 4:  # Ffuf url
                if check_var([url, wordlist]):
                    run_task.newTerminal(
                        [
                            "ffuf",
                            "-u",
                            url,
                            "-w",
                            wordlist,
                            "-recursion",
                            "-o",
                            resultsPath + "ffuf_url_parameters.json",
                        ]
                    )
                break

            case 5:  # Ffuf request file
                if check_var([request_file, wordlist]):
                    run_task.newTerminal(
                        [
                            "ffuf",
                            "-request",
                            request_file,
                            "-w",
                            wordlist,
                            "-o",
                            resultsPath + "ffuf_request_parameters.json",
                        ]
                    )
                break

            case 6:  # Vuln Exploit Commix
                if check_var([url, log_level, cookies, bodyData]):
                    run_task.newTerminal(
                        [
                            "commix",
                            "-u",
                            url,
                            "--level",
                            log_level,
                            "--cookie=" + cookies,
                            "--data=" + bodyData,
                            "--output-dir=" + resultsPath,
                        ]
                    )
                break

            # Change variables
            case 97:
                print(string_format.warning("Empty field = current value \n"))
                domain = str(input("Domain: ") or domain)
                url = str(input("URL: ") or url)
                request_file = str(input("Request File Path: ") or request_file)
                cookies = str(input("Cookies String: ") or cookies)
                bodyData = str(input("Body Data: ") or bodyData)
                log_level = str(input("Log Level [1-3]: ") or log_level)
                wordlist = str(input("Wordlist path: ") or wordlist)
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
