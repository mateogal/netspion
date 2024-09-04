import subprocess
import webbrowser
import os


def main(resultsPath):
    resultsPath = resultsPath + "PassiveInfo/"
    os.makedirs(resultsPath, exist_ok=True)
    while True:
        print("Information Gathering / Passive Information\n")
        print("ALL RESULTS WILL BE STORED IN " + resultsPath)
        operation = int(
            input(
                """
[1] Open Shodan
[2] Open Google Hacking Database
[3] Open Censys
[4] Open Archive.org
[5] Open DNSDumpster
[6] Open InternalAllTheThings
[7] Whois
[8] TheHarvester
[98] Custom command (SHELL)
[99] Exit

Select operation: """
            )
        )
        print("\n")
        match operation:
            case 1:
                webbrowser.open("www.shodan.io", new=2)

            case 2:
                webbrowser.open(
                    "https://www.exploit-db.com/google-hacking-database", new=2
                )

            case 3:
                webbrowser.open("search.censys.io", new=2)

            case 4:
                webbrowser.open("archive.org", new=2)

            case 5:
                webbrowser.open("https://dnsdumpster.com/", new=2)

            case 6:
                webbrowser.open(
                    "https://swisskyrepo.github.io/InternalAllTheThings/", new=2
                )

            case 7:
                domain = str(input("Domain: "))
                whoisResult = subprocess.run(
                    ["whois", domain], capture_output=True, text=True
                )
                print(whoisResult.stdout)
                f = open(resultsPath + domain + "_whois", "w")
                print(whoisResult.stdout, file=f)
                f.close()

            case 8:
                domain = str(input("Domain: "))
                limit = str(input("Limit: "))
                file = str(input("File output name: "))
                subprocess.run(
                    [
                        "theHarvester",
                        "-d",
                        domain,
                        "-l",
                        limit,
                        "-f",
                        resultsPath + file,
                        "-b",
                        "all",
                    ]
                )

            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG")
                command = str(input("Command: "))
                subprocess.run([command], shell=True)

            case 99:
                break

            case _:
                print("No option available")

        input("\nPress enter to continue ")
        subprocess.run(["clear"], shell=True)
