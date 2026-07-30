"""Legacy scapy-based packet sniffer.

This module is kept for backwards compatibility.
It provides a simple interactive packet handler using scapy.

Usage:
    from Wifi.packet_handler import interactive_sniffer
    interactive_sniffer()
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from utils.logger import get_logger

RESULTS_PATH = "/tmp/sniffer/"


def handle_arp(packet: object) -> None:
    print("Handling ARP packet")


def handle_ip(packet: object) -> None:
    print("Handling IP packet")


def handle_packet(packet: object) -> None:
    try:
        layer = packet.getlayer(1)
        name = layer.name
    except Exception:
        print("Unknown packet")
        return

    match name:
        case "ARP":
            handle_arp(packet)
        case "IP":
            handle_ip(packet)
        case _:
            print("No handler for layer: %s", name)


def interactive_sniffer() -> None:
    from scapy.all import sniff, wrpcap

    log = get_logger()
    os.makedirs(RESULTS_PATH, exist_ok=True)
    pkt_filter = input("Filter [empty all]: ").strip() or None

    log.info("Starting sniffer with filter=%s to %s", pkt_filter, RESULTS_PATH)
    pkts = sniff(filter=pkt_filter, prn=handle_packet, timeout=300)
    wrpcap(str(Path(RESULTS_PATH) / "packet_handler.cap"), pkts)
    log.info("Captured %d packets", len(pkts))


if __name__ == "__main__":
    interactive_sniffer()
