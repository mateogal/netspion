# This project is still in development

# Netspion
**Netspion** is a tool with useful pre-defined techniques for ethical hacking, it includes:  
- Information Gathering
- Active Directory hacking
- Web Hacking
- Wifi Hacking
- Evasion techniques
- Post exploitation

You can run custom commands directly in the shell inside **Netspion**.

> [!IMPORTANT]
> **Python 3.10+ required**  
> You must install all the requirements to run the scripts without errors.  
``` pip install -r requirements.txt ```  

> [!IMPORTANT]
> Tools used and required (aAll credits to respective owners):
> - [Metasploit](https://www.metasploit.com/)
> - [SQLMap](https://sqlmap.org/)
> - [Nmap](https://nmap.org)
> - [Aircrack-ng](https://www.aircrack-ng.org)
> - [TheHarvester](https://github.com/laramies/theHarvester)
> - [Hashcat](https://hashcat.net/hashcat/)
> - [JohnTheRipper](https://www.openwall.com/john/)
> - Whois / Nslookup / DIG
> - [Lighttpd](https://www.lighttpd.net/)
> - [Impacket](https://github.com/fortra/impacket)
> - [Responder](https://github.com/lgandx/Responder)
> - [Subfinder](https://github.com/projectdiscovery/subfinder)
> - [WhatWeb](https://github.com/urbanadventurer/WhatWeb)
> - [GoBuster](https://github.com/OJ/gobuster)
> - [Ffuf](https://github.com/ffuf/ffuf)
> - [Commix](https://github.com/commixproject/commix)
> - [Wafw00f](https://github.com/EnableSecurity/wafw00f)
> - [LoadBalancing detector](https://github.com/craig/ge.mine.nu/blob/master/lbd/lbd.sh)

> [!TIP]
> Recommended additional tools/websites (all credits to respective owners):
> - [Maltego](https://www.maltego.com/)
> - [Burpsuite](https://portswigger.net/burp/communitydownload)
> - [Nessus](https://www.tenable.com/products/nessus/nessus-essentials)
> - [Fluxion](https://github.com/FluxionNetwork/fluxion)
> - [Bloodhound](https://github.com/SpecterOps/BloodHound)
> - [SysInternals](https://learn.microsoft.com/en-us/sysinternals/downloads/)
> - [Mimikatz](https://github.com/ParrotSec/mimikatz)
> - [Rubeus](https://github.com/GhostPack/Rubeus)
> - [Covenant](https://github.com/cobbr/Covenant)
> - [SecList](https://github.com/danielmiessler/SecLists)
> - [OWASP ZAProxy](https://github.com/zaproxy/zaproxy)
> - [Nikto](https://github.com/sullo/nikto)
> - [Nuclei](https://github.com/projectdiscovery/nuclei)
> - [Git Leaks](https://github.com/gitleaks/gitleaks)
> - [The Fat Rat](https://github.com/screetsec/TheFatRat)
> - [Local Tunnel](https://github.com/localtunnel/localtunnel)

# Useful commands

## Metasploit framework

### Module to check possible availables exploits in opened sessions

``` use post/multi/recon/local_exploit_suggester ```

### Module to generate payloads with webserver

``` use exploit/multi/script/web_delivery ```

### Module to run an listener

``` use exploit/multi/handler ```

### Module to scan TCP ports

``` use auxiliary/scanner/portscan/tcp ```

### Module to exploit smb psexec

``` use exploit/windows/smb/psexec ```

### Route traffic to session
``` route add DST_IP DST_MASK SESSION_NUMBER```

## MSFVenom

### Generate custom payloads

``` msfvenom -p payload lhosts=XXX lport=XXXX ```

## Meterpreter

### Port Forwarding
``` portfw add -l LOCAL_PORT -p REMOTE_PORT -r REMOTE_IP ```