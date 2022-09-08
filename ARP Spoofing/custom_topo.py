#!/usr/bin/python
from mininet.topo import Topo


class CustomTopo(Topo):
    def __init__(self, hosts_count=3, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)
        switch = self.addSwitch("s1")
        hosts = []
        attacker = self.addHost(
            "attacker", mac="95:05:59:81:31:c2", ip=f"10.0.0.{hosts_count + 1}/24"
        )

        for id in range(1, hosts_count + 1):
            name = f"h{id}"
            mac = f"00:00:00:00:00:0{id}"
            ip = f"10.0.0.{id}/24"
            host = self.addHost(name, mac=mac, ip=ip)
            hosts.append(host)
            self.addLink(host, switch, bw=10, delay="50ms")
        self.addLink(attacker, switch, bw=10, delay="50ms")
        hosts.append(attacker)


topos = {"mytopo": (lambda: CustomTopo())}
