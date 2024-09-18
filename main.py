import cmd2, platform, time
import utils.init as init
import utils.run_task as rt
import ActiveDirectory.ad as ad_cs
import Evasion.evasion as evasion
import WebHacking.web as wh_cs
import Wifi.wifi as wifi
import Passwords.password_crack as pc
import InformationGathering.active_info as aig
import utils.string_format as sf
import InformationGathering.passive_info as pig
from cmd2 import CommandSet, with_default_category

import platform

PLATFORM_SYSTEM = platform.system()

RESULTS_PATH = "/tmp/netspion/"

init.main()
time.sleep(3)


@with_default_category("Sub Menu Tools")
class SubMenuCommandSet(CommandSet):
    def __init__(self):
        super().__init__()

    def do_web_hacking(self, arg):
        "Web Hacking tools sub menu"
        wh_cs.main()

    def do_password_crack(self, arg):
        "Password cracking tools sub menu"
        pc.main()

    def do_evasion(self, arg):
        "Evasion tools sub menu"
        evasion.main()

    def do_wifi_hacking(self, arg):
        "Wifi Hackings tools sub menu"
        wifi.main()

    def do_ad_hacking(self, arg):
        "Active Directory hacking tools sub menu"
        ad_cs.main()

    def do_active_info(self, arg):
        "Information Gathering Active hacking tools sub menu"
        aig.main()

    def do_passive_info(self, arg):
        "Information Gathering Passive hacking tools sub menu"
        pig.main()


@with_default_category("Main commands")
class NetspionShell(cmd2.Cmd):
    delattr(cmd2.Cmd, "do_run_pyscript")
    delattr(cmd2.Cmd, "do_run_script")

    def __init__(self):
        super().__init__()
        self.do_clear(1)
        self.port = "4444"
        self.addr = "127.0.0.1"
        self.mode = "B"
        self.intro = sf.text(
            "\nWelcome to Netspion custom shell. Use 'help / help -v' for verbose / 'help <topic>' for details. \n"
        )
        self.prompt = sf.success("(netspion): ")
        self.add_settable(cmd2.Settable("port", str, "Port", self))
        self.add_settable(cmd2.Settable("addr", str, "IP Address", self))
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
            sf.title(
                """
  _   _      _             _             
 | \ | |    | |           (_)            
 |  \| | ___| |_ ___ _ __  _  ___  _ __  
 | . ` |/ _ \ __/ __| '_ \| |/ _ \| '_ \ 
 | |\  |  __/ |_\__ \ |_) | | (_) | | | |
 |_| \_|\___|\__|___/ .__/|_|\___/|_| |_|
                    | |                  
                    |_|                  
"""
            )
        )
        self.poutput(
            sf.info("RUNNING ON: ")
            + sf.success(PLATFORM_SYSTEM + platform.release() + platform.version())
        )
        self.poutput(
            sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(RESULTS_PATH)
        )

    def do_netcat(self, arg):
        "Netcat TCP connection listener: netcat PORT ADDR"
        rt.runBackground(["nc", "-l", "-p", self.port, "-s", self.addr, "-v"], None)

    def do_httpsrv(self, arg):
        "SimpleHTTP Python2 server on current path"
        rt.runBackground(["python2", "-m", "SimpleHTTPServer"], None)

    def do_smbsrv(self, arg):
        "SMB2 Server Impacket on /tmp/netspion/SMBServer"
        rt.runBackground(
            [
                "impacket-smbserver",
                "-smb2support",
                "netspionSMB",
                "/tmp/netspion/SMBServer/",
            ],
            None,
        )


NetspionShell().cmdloop()
