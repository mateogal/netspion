import cmd2, subprocess, platform, os
import utils.run_task as rt
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf
from utils.check_var import check_vars
from utils.utils_shell import UtilsCommandSet
import asyncio

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class ActiveIGShell(cmd2.Cmd):
    intro = sf.text(
        "Netspion Active Info-Gath Sub menu. Use 'help / help -v' for verbose / 'help <topic>' for details. \n"
    )
    prompt = sf.success("(netspion Active-IG): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/Active-IG/"
        self.network = ""
        self.domain = ""
        self.pkt_fragment = "No"

        self.add_settable(cmd2.Settable("network", str, "Target Network", self))
        self.add_settable(cmd2.Settable("domain", str, "Target Domain", self))
        self.add_settable(
            cmd2.Settable(
                "pkt_fragment",
                str,
                "Packet Fragment mode for NMAP (default: no)",
                self,
                choices=(["Yes", "No"]),
            )
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
        self.do_help("-v")

    def do_host_discover(self, arg):
        "Nmap Host Discovery"
        if check_vars([{"name": "network", "value": self.network}]):
            if self.pkt_fragment == "No":
                rt.runBackground(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sn",
                        "-PS",
                        self.network,
                        "-oA",
                        self.resultsPath + "hostDiscovery_" + self.network,
                        "--webxml",
                    ],
                    None,
                )
            else:
                mtu = str(input("MTU: "))
                if (mtu % 8) != 0:
                    print("Invalid MTU")
                    return
                rt.runBackground(
                    [
                        "nmap",
                        "-v",
                        "--reason",
                        "-sS",
                        "-p-",
                        "--mtu",
                        mtu,
                        self.network,
                        "-oA",
                        self.resultsPath + "mtu_hostDiscovery_" + self.network,
                        "--webxml",
                    ],
                    None,
                )

    def do_syn_port_scan(self, arg):
        "Nmap Port Scan (SYN)"
        if check_vars([{"name": "network", "value": self.network}]):
            rt.runBackground(
                [
                    "nmap",
                    "-v",
                    "--reason",
                    "-sS",
                    "-p-",
                    self.network,
                    "-oA",
                    self.resultsPath + "portScanSYN_" + self.network,
                    "--webxml",
                ],
                None,
            )

    def do_tcp_port_scan(self, arg):
        "Nmap Port Scan (TCP)"
        if check_vars([{"name": "network", "value": self.network}]):
            rt.runBackground(
                [
                    "nmap",
                    "-v",
                    "--reason",
                    "-sT",
                    "-p-",
                    self.network,
                    "-oA",
                    self.resultsPath + "portScanTCP_" + self.network,
                    "--webxml",
                ],
                None,
            )

    def do_udp_port_scan(self, arg):
        "Nmap Port Scan (UDP)"
        if check_vars([{"name": "network", "value": self.network}]):
            rt.runBackground(
                [
                    "nmap",
                    "-v",
                    "--reason",
                    "-sU",
                    "-p-",
                    self.network,
                    "-oA",
                    self.resultsPath + "portScanUDP_" + self.network,
                    "--webxml",
                ],
                None,
            )

    def do_aggressive_scan(self, arg):
        "Nmap Port Scan (Aggressive / All)"
        if check_vars([{"name": "network", "value": self.network}]):
            rt.runBackground(
                [
                    "nmap",
                    "-v",
                    "--reason",
                    "-A",
                    "-p-",
                    self.network,
                    "-oA",
                    self.resultsPath + "portScanAll_" + self.network,
                    "--webxml",
                ],
                None,
            )

    def do_nslookup_dig(self, arg):
        "Nslookup & DIG"
        if check_vars([{"name": "domain", "value": self.domain}]):
            asyncio.run(
                rt.runBackground(
                    ["nslookup", f"-q=any {self.domain}"],
                    self.resultsPath + self.domain + "/",
                )
            )
            asyncio.run(
                rt.runBackground(
                    ["dig", f"{self.domain} ANY +trace"],
                    self.resultsPath + self.domain + "/",
                )
            )


def main():
    ActiveIGShell().do_clear(1)
    ActiveIGShell().cmdloop()
