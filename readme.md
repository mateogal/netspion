# Dev Repository. This project is still in development. It will be released to a different repository.

# Information
> [!NOTE]
> This tool has only useful pre-defined techniques.
> You can use the SHELL directly for advanced/custom commands or techniques.

> [!IMPORTANT]
> **Python 3.10+ required**  
> You must install all the requirements to run the scripts without errors.  
``` pip install -r requirements.txt ```  

> [!NOTE]
> Tools used and required:
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

> [!TIP]
> Recommended additional tools:
> - [Maltego](https://www.maltego.com/)
> - [Burpsuite](https://portswigger.net/burp/communitydownload)
> - [Nessus](https://www.tenable.com/products/nessus/nessus-essentials)
> - [Fluxion](https://github.com/FluxionNetwork/fluxion)
> - [Bloodhound](https://github.com/SpecterOps/BloodHound)
> - [SysInternals](https://learn.microsoft.com/en-us/sysinternals/downloads/)
> - [Mimikatz](https://github.com/ParrotSec/mimikatz)
> - [Rubeus](https://github.com/GhostPack/Rubeus)
> - [Covenant](https://github.com/cobbr/Covenant)

# Useful commands

## Metasploit framework

### Module to check possible availables exploits in opened sessions

``` use post/multi/recon/local_exploit_suggester ```

### Module to generate payloads with webserver

``` use exploit/multi/script/web_delivery ```

### Module to run an listener

``` use exploit/multi/handler ```

### Module to exploit smb psexec

``` use exploit/windows/smb/psexec ```

## MSFVenom

### Generate custom payloads

``` msfvenom -p payload lhosts=XXX lport=XXXX ```