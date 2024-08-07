import platform
import subprocess

OUTPUT_LOCATION = "/tmp/SQLMap-Auto/"
subprocess.run(["mkdir", OUTPUT_LOCATION])

PLATFORM_SYSTEM = platform.system()

subprocess.run(["clear"], shell=True)
print("Running on:", PLATFORM_SYSTEM, platform.release(), platform.version())

type = url = file = ""


def runCheck(command):
    if type == "u" or type == "U":
        subprocess.run(
            [
                "sqlmap",
                "-u",
                url,
                "--risk",
                "3",
                "--batch",
                "--random-agent",
                command,
                "--output-dir=" + OUTPUT_LOCATION,
            ]
        )
    elif type == "f" or type == "F":
        subprocess.run(
            [
                "sqlmap",
                "-l",
                file,
                "--risk",
                "3",
                "--batch",
                "--random-agent",
                command,
                "--output-dir=" + OUTPUT_LOCATION,
            ]
        )
    else:
        print("Wrong scan type")


while True:
    print("ALL RESULTS WILL BE STORED IN " + OUTPUT_LOCATION)
    operation = int(
        input(
            """
[1] Set URL scan or File scan
[2] SQLi retrieve DBMS current user
[3] SQLi enum DBMS users passwords hashes (default dictionary hashes)
[4] SQLi list databases
[5] SQLi list tables
[6] SQLi list columns
[7] SQLi dump database info
[8] SQLi prompt for and interactive SQL shell
[9] Custom command (SHELL)
[0] Exit
Select operation: """
        )
    )
    subprocess.run(["clear"], shell=True)
    match operation:
        case 1:
            type = str(input("URL or File [u/f]: "))
            if type == "f" or type == "F":
                file = str(input("File location: "))
            elif type == "u" or type == "U":
                url = str(input("URL:"))
            else:
                print("Wrong type")
        case 2:
            command = "--current-user"
            runCheck(command)
        case 3:
            command = "--passwords"
            runCheck(command)
        case 4:
            command = "--dbs"
            runCheck(command)
        case 5:
            command = "--tables"
            runCheck(command)
        case 6:
            command = "--columns"
            runCheck(command)
        case 7:
            bd = str(input("Database name: "))
            command = [["-D"], [bd], ["--dump-all"]]
            runCheck(command)
        case 8:
            command = "--sql-shell"
            runCheck(command)
        case 9:
            print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
            print("YOU NEED TO MAKE YOUR OWN LOG\n")
            command = str(input("Command: "))
            subprocess.run([command], shell=True)
        case 0:
            break

    input("\nPress any key to continue ")
    subprocess.run(["clear"], shell=True)
