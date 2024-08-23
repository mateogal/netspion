import cmd2, subprocess
import utils.run_task as rt


class KerErrShell(cmd2.Cmd):
    intro = "Welcome to KerErr Tools custom Shell. Type help or ? to list commands and help/? COMMAND to show COMMAND help. \n"
    prompt = "(kererr): "

    def __init__(self):
        super().__init__()
        self.url = ""
        self.wordlist = ""
        self.add_settable(cmd2.Settable("url", str, "Domain URL", self))
        self.add_settable(cmd2.Settable("wordlist", str, "Wordlist file path", self))

    def do_clear(self, arg):
        "Clear screen"
        subprocess.run(["clear"], shell=True)

    def do_netcat(self, arg):
        "Netcat connection listener: netcat PORT IP_ADDR"
        port = arg.split()[0]
        addr = arg.split()[1]
        rt.newTerminal(["nc", "-l", "-p", port, "-s", addr, "-v"])

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

    def do_web_hacking(self, arg):
        "Web Hacking tools sub menu"

        class WebHacking(cmd2.Cmd):
            prompt = "(kererr Web-Hacking): "

        WebHacking().cmdloop()

    def do_wifi_hacking(self, arg):
        "Wifi Hacking tools sub menu"

        class WifiHacking(cmd2.Cmd):
            prompt = "(kererr Wifi-Hacking): "

        WifiHacking().cmdloop()

    def do_ad_hacking(self, arg):
        "Active Directory hacking tools sub menu"

        class ADHacking(cmd2.Cmd):
            prompt = "(kererr AD-Hacking): "

        ADHacking().cmdloop()

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


def main():
    KerErrShell().cmdloop()
