from scapy.all import *
import subprocess

subprocess.run(["clear"], shell=True)

resultsPath = "/tmp/sniffer/"

subprocess.run(["mkdir", resultsPath])
subprocess.run(["touch", resultsPath + "packet_handler.cap"])

pktFlt = str(input("Filter [empty all]: "))


def handle_packet(packet):
    layer = packet.getlayer(1)
    match layer.name:
        case "ARP":
            handle_arp(packet)

        case "IP":
            handle_ip(packet)

        case _:
            print("No layer")

    return


def handle_arp(packet):
    print("Handling ARP packet")
    return


def handle_ip(packet):
    print("Handling IP packet")
    return


pkts = sniff(filter=pktFlt, prn=handle_packet)
wrpcap(resultsPath + "packet_handler.cap", pkts)
