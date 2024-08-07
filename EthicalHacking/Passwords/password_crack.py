import platform
import subprocess

OUTPUT_LOCATION = "/tmp/PasswordCrack/"
subprocess.run(["mkdir", OUTPUT_LOCATION])

PLATFORM_SYSTEM = platform.system()

subprocess.run(["clear"], shell=True)
print("Running on:", PLATFORM_SYSTEM, platform.release(), platform.version())

type = url = file = ""

while True:
    print("ALL RESULTS WILL BE STORED IN " + OUTPUT_LOCATION)
    operation = int(
        input(
            """
[1] Hashcat Brute Force
[2] Hashcat Dictionary
[3] JohnTheRipper Brute Force
[4] JohnTheRipper Dictionary
[9] Custom command (SHELL)
[0] Exit
Select operation: """
        )
    )
    subprocess.run(["clear"], shell=True)
    match operation:
        case 1:
            encode = str(input("Hashcat Encode type code [default:auto]: "))
            file = str(input("Hash file path: "))
            if encode:
                subprocess.run(["hashcat", "-m", encode, "-a", "3", file])
            else:
                subprocess.run(["hashcat", "-a", "3", file])
        case 2:
            encode = str(input("Hashcat Encode type code [default:auto]: "))
            file = str(input("Hash file path: "))
            dictionary = str(input("Dictionary file path: "))
            if encode:
                subprocess.run(["hashcat", "-m", encode, "-a", "0", file, dictionary])
            else:
                subprocess.run(["hashcat", "-a", "0", file, dictionary])
        case 3:
            encode = str(input("JohnTheRipper Encode type [default:auto]: "))
            file = str(input("Hash file path: "))
            if encode:
                subprocess.run(["john", "--format=" + encode, file])
            else:
                subprocess.run(["john", file])
        case 4:
            break
        case 9:
            print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
            print("YOU NEED TO MAKE YOUR OWN LOG\n")
            command = str(input("Command: "))
            subprocess.run([command], shell=True)
        case 0:
            break

    input("\nPress any key to continue ")
    subprocess.run(["clear"], shell=True)
