import subprocess
import platform
import time
import importlib

with open("requirements.txt") as file:
    for module in file:
        module = module.strip()
        try:
            importlib.import_module(module)
        except:
            print(
                "Missing python modules. Please install them using: pip install -r requirements.txt"
            )
            exit()

from utils import run_task
from utils import string_format

PLATFORM_SYSTEM = platform.system()
DEPENDENCIES_LIST = [
    "libpq-dev",
    "aircrack-ng",
    "hostapd",
    "metasploit-framework",
    "theHarvester",
    "nmap",
    "whois",
    "qterminal",
    "reaver",
    "dnsmasq",
    "bloodhound",
    "lighttpd",
    "php-cgi",
    "cowpatty",
    "responder"
]


def checkOS():
    if PLATFORM_SYSTEM != "Linux":
        print("This program must run on Linux OS !!!")
        exit()

    if run_task.normalCapture(["cat", "/etc/debian_version"]).returncode == 0:
        PKG_INSTALLER = "apt install -y"
        PKG_CHECK = "dpkg -s"

    elif run_task.normalCapture(["cat", "/etc/SuSE-release"]).returncode == 0:
        PKG_INSTALLER = "zypper install"

    elif run_task.normalCapture(["cat", "/etc/redhat-release"]).returncode == 0:
        PKG_INSTALLER = "yum -y install"

    else:
        print("No package manager found")
        exit()

    return PKG_INSTALLER, PKG_CHECK


def checkDependencies(PKG_INSTALLER, PKG_CHECK):
    print(string_format.warning("CHECKING ALL NECESSARY DEPENDENCIES"))
    time.sleep(2)
    missing_dep = []
    error = string_format.fail(" not installed")
    success = string_format.success(" already installed")

    for dependency in DEPENDENCIES_LIST:

        command = f"{PKG_CHECK} {dependency}"
        task = run_task.progress(command)

        if task == 1:
            print(dependency.upper().ljust(20) + error.rjust(50))
            missing_dep.append(dependency)

        else:
            print(dependency.upper().ljust(20) + success.rjust(50))

    if len(missing_dep) != 0:
        print("\nMissing dependencies: ", missing_dep)
        opc = str(input("Do you want to install all missing dependencies? [Y/n]: "))

        if opc == "Y" or opc == "y":
            installDependencies(PKG_INSTALLER, missing_dep)

        else:
            print("You must install all dependencies")
            exit()

    else:
        print(string_format.success("\nAll dependencies are satisfied"))


def installDependencies(PKG_INSTALLER, missing_dep):
    print(string_format.warning("\nINSTALLING ALL NECESSARY DEPENDENCIES\n"))
    exitCode = 1
    for dependency in missing_dep:
        command = f"{PKG_INSTALLER} {dependency}"
        task = run_task.normalShell(command)

        if task.returncode == 0:
            print(string_format.success(dependency + " successfully installed"))
        else:
            print(string_format.fail(dependency + " failed to install"))
            exitCode = 0

    if not exitCode:
        print(
            string_format.warning(
                "\nPLEASE MANUALLY CHECK FAILED DEPENDENCIES OR RUN INSTALLER AGAIN"
            )
        )
        exit()


def checkRoot():
    current_user = subprocess.run(["whoami"], capture_output=True, text=True)
    current_user = (current_user.stdout).strip()
    if current_user != "root":
        print("Must be run as root")
        exit()


def main():
    PKG_INSTALLER, PKG_CHECK = checkOS()
    checkDependencies(PKG_INSTALLER, PKG_CHECK)
    checkRoot()
