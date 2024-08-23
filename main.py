import subprocess
import time
import utils.init as init

subprocess.run(["clear"], shell=True)
init.main()
time.sleep(3)

import platform
import os
import click


import EthicalHacking as et
import utils.string_format as sf


PLATFORM_SYSTEM = platform.system()

RESULTS_PATH = "/tmp/KerErrTools/"

while True:
    try:
        subprocess.run(["clear"], shell=True)
        print(sf.title("KerErr Tools"))
        print(
            sf.info("\nRUNNING ON: ")
            + sf.success(PLATFORM_SYSTEM + platform.release() + platform.version())
        )
        print(sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(RESULTS_PATH))
        operation = int(
            input(
                """
[1] Information Gathering / Active Info
[2] Information Gathering / Passive Info
[3] Information Gathering / Auto Search Metasploit Vulnerabilites from MSF Database
[4] SysAdmin / Open Backup Script editor
[5] SysAdmin / Open Network Interfaces Check editor
[6] SysAdmin / Open HA Configuration editor
[7] Wifi Hacking
[8] Active Directory Hacking
[9] Web Hacking
[10] Evasion & Detection Tools
[98] Custom command (SHELL)
[99] Exit

Select operation: """
            )
        )
        subprocess.run(["clear"], shell=True)
        match operation:
            case 1:
                et.active_info.main(RESULTS_PATH)
            case 2:
                et.passive_info.main(RESULTS_PATH)
            case 3:
                et.autosrc_msfvulns.main(RESULTS_PATH)
            case 4:
                click.launch("./SysAdmin/backups.py")
            case 5:
                click.launch("./SysAdmin/control_red.ps1")
            case 6:
                click.launch("./SysAdmin/HA-configuration.sh")
            case 7:
                et.wifi.main(RESULTS_PATH)
            case 8:
                et.ad.main(RESULTS_PATH)
            case 9:
                et.web.main(RESULTS_PATH)
            case 10:
                et.evasion.main(RESULTS_PATH)
            case 99:
                break
            case _:
                print("Invalid option")
    except:
        print("Invalid option")
