import subprocess
import os


def main(resultsPath):
    resultsPath = resultsPath + "ActiveInfo/"
    os.makedirs(resultsPath, exist_ok=True)
    while True:
        print("Information Gathering / Active Information\n")
        print("ALL RESULTS WILL BE STORED IN " + resultsPath)
        operation = int(
            input(
                """
[1] Nmap Host Discovery
[2] Nmap Port Scan (SYN)
[3] Nmap Port Scan (TCP)
[4] Nmap Port Scan (UDP)
[5] Nmap Aggressive scan
[6] Nmap SMB Enumeration
[7] Nmap SNMP Enumeration
[8] Nslookup & DIG
[9] Nmap Port Scan (Packet Fragment)
[10] Nmap Port Scan (Decoy)
[11] Nmap Port Scan (IP Spoof)
[98] Custom command (SHELL)
[99] Exit

Select operation: """
            )
        )
        print("\n")
        match operation:
            case 1:
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sn",
                        "-PS",
                        network,
                        "-oA",
                        resultsPath + "hostDiscovery",
                        "--webxml",
                    ]
                )

            case 2:
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sS",
                        "-p-",
                        network,
                        "-oA",
                        resultsPath + "portScanSYN",
                        "--webxml",
                    ]
                )

            case 3:
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sT",
                        "-p-",
                        network,
                        "-oA",
                        resultsPath + "portScanTCP",
                        "--webxml",
                    ]
                )

            case 4:
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sU",
                        "-p-",
                        network,
                        "-oA",
                        resultsPath + "portScanUDP",
                        "--webxml",
                    ]
                )

            case 5:
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-A",
                        "-p-",
                        network,
                        "-oA",
                        resultsPath + "osAndServicesScan",
                        "--webxml",
                    ]
                )

            case 6:
                subprocess.run(["ls /usr/share/nmap/scripts/smb*"], shell=True)
                network = str(input("\nNetwork/IP: "))
                script = str(input("Script name: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sS",
                        "--script=" + script,
                        network,
                        "-oA",
                        resultsPath + "smbEnum",
                        "--webxml",
                    ]
                )

            case 7:
                subprocess.run(["ls /usr/share/nmap/scripts/snmp*"], shell=True)
                network = str(input("\nNetwork/IP: "))
                script = str(input("Script name: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sS",
                        "--script=" + script,
                        network,
                        "-oA",
                        resultsPath + "snmpEnum",
                        "--webxml",
                    ]
                )

            case 8:
                domain = str(input("Domain: "))
                nslookupResult = subprocess.run(
                    ["nslookup", "-q=any", domain], capture_output=True, text=True
                )
                print(nslookupResult.stdout)
                f = open(resultsPath + domain + "_nslookup", "w")
                print(nslookupResult.stdout, file=f)
                f.close()
                digResult = subprocess.run(
                    ["dig", domain, "ANY", "+trace"], capture_output=True, text=True
                )
                print(digResult.stdout)
                f = open(resultsPath + domain + "_dig", "w")
                print(digResult.stdout, file=f)
                f.close()

            case 9:
                mtu = str(input("MTU: "))
                if (mtu % 8) != 0:
                    print("Invalid MTU")
                    break
                network = str(input("Network/IP: "))
                subprocess.run(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sS",
                        "-p-",
                        "--mtu",
                        mtu,
                        network,
                        "-oA",
                        resultsPath + "portScanSYN",
                        "--webxml",
                    ]
                )

            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG\n")
                command = str(input("Command: "))
                subprocess.run([command], shell=True)

            case 99:
                break

            case _:
                print("No option available")

        input("\nPress enter to continue ")
        subprocess.run(["clear"], shell=True)
