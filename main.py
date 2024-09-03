import cmd2, subprocess, platform, time
import utils.init as init
import utils.run_task as rt
import EthicalHacking.ActiveDirectory.ad as ad_cs
import EthicalHacking.Evasion.evasion as evasion
import EthicalHacking.WebHacking.web as wh_cs
import EthicalHacking.Passwords.password_crack as pc
import utils.string_format as sf
from cmd2 import CommandSet, with_default_category

import platform

PLATFORM_SYSTEM = platform.system()

RESULTS_PATH = "/tmp/KerErrTools/"

init.main()
time.sleep(3)


@with_default_category("Utils")
class SubMenu2CommandSet(CommandSet):
    def __init__(self):
        super().__init__()

    def do_clear(self, arg):
        "Clear screen"
        subprocess.run(["clear"], shell=True)

    def do_show_processes(self, arg):
        "Show current running processes"
        rt.showRunningProcs()

    def do_show_process_data(self, arg):
        "Show specific process output (Log Location: /tmp/KerErrTools/processes/)"
        rt.showProcessData(int(arg))

    def do_exec_mode(self, arg):
        "Set execution mode (N: run task in new terminal) / (B: run task in background)"
        self.mode = arg


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
        "Wifi Hacking tools sub menu"

        class WifiHacking(cmd2.Cmd):
            prompt = "(kererr Wifi-Hacking): "

        WifiHacking().cmdloop()

    def do_ad_hacking(self, arg):
        "Active Directory hacking tools sub menu"
        ad_cs.main()

    def do_active_info(self, arg):
        "Information Gathering Active hacking tools sub menu"

        class IGActive(cmd2.Cmd):
            prompt = "(kererr IG-Active): "

        IGActive().cmdloop()

    def do_passive_info(self, arg):
        "Information Gathering Passive hacking tools sub menu"

        class IGPassive(cmd2.Cmd):
            prompt = "(kererr IG-Passive): "

        IGPassive().cmdloop()


@with_default_category("Main commands")
class KerErrShell(cmd2.Cmd):
    delattr(cmd2.Cmd, "do_run_pyscript")
    delattr(cmd2.Cmd, "do_run_script")

    def __init__(self):
        super().__init__()
        self.do_clear(1)
        self.port = "4444"
        self.addr = "127.0.0.1"
        self.mode = "B"
        self.intro = sf.text(
            "Welcome to KerErr Tools custom Shell. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
        )
        self.prompt = sf.success("(kererr): ")
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
            sf.warning(
                """
 ____  __.          ___________               ___________           .__          
|    |/ _|__________\_   _____/_____________  \__    ___/___   ____ |  |   ______
|      <_/ __ \_  __ \    __)_\_  __ \_  __ \   |    | /  _ \ /  _ \|  |  /  ___/
|    |  \  ___/|  | \/        \|  | \/|  | \/   |    |(  <_> |  <_> )  |__\___ \ 
|____|__ \___  >__| /_______  /|__|   |__|      |____| \____/ \____/|____/____  >
        \/   \/             \/                                                \/ 
"""
            )
        )
        self.poutput(
            sf.info("RUNNING ON: ")
            + sf.success(PLATFORM_SYSTEM + platform.release() + platform.version())
        )
        self.poutput(
            sf.info("ALL RESULTS WILL BE STORED IN: ") + sf.success(RESULTS_PATH) + "\n"
        )
        self.do_help("-v")

    def do_netcat(self, arg):
        "Netcat TCP connection listener: netcat PORT ADDR"
        # rt.newTerminal(["nc", "-l", "-p", self.port, "-s", self.addr, "-v"])
        rt.runBackground(["nc", "-l", "-p", self.port, "-s", self.addr, "-v"])

    def do_httpsrv(self, arg):
        "SimpleHTTP Python2 server on current path"
        rt.newTerminal(["python2", "-m", "SimpleHTTPServer"])

    def do_smbsrv(self, arg):
        "SMB2 Server Impacket on /tmp/KerErrTools/SMBServer"
        rt.newTerminal(
            [
                "impacket-smbserver",
                "-smb2support",
                "KerErrSMB",
                "/tmp/KerErrTools/SMBServer/",
            ]
        )


KerErrShell().cmdloop()
