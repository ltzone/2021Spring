#!/usr/bin/env python

from re import error
from typing import Match
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

SWITCH_NUM = 3
HOST_NUM = 4
CONN_MAP = [
    ['h4', 's1'],
    ['s1', 's3', {"bw": 10}],
    ['s3', 'h3'],
    ['h1', 's1'],
    ['s1', 's2', {"bw": 10}],
    ['s2', 'h2']
]


class MyTopo(Topo):
    """
    a simulation for the following topology
        h4
        │
    h1──s1──s2──h2
        │
        s3
        │
        h3
    """

    def build(self, switch_num, host_num, conn_map, *args, **params):
        switches = []
        hosts = []

        for i in range(switch_num):
            switches.append(self.addSwitch(f's{i+1}'))
        for j in range(host_num):
            hosts.append(self.addHost(f'h{(j+1)}'))
        for conn in conn_map:
            try:
                a, b = conn[0], conn[1]
                node1 = switches[int(a[1])-1] if a[0] == 's' else hosts[int(a[1]) - 1]
                node2 = switches[int(b[1])-1] if b[0] == 's' else hosts[int(b[1]) - 1]
                link_options = conn[2] if len(conn) > 2 else {}
            except error:
                raise AttributeError("Invalid Host Map Elements")
            self.addLink(node1, node2, **link_options)




def perfTest():
    "Create and test a simple network"
    topo = MyTopo(switch_num=SWITCH_NUM, host_num=HOST_NUM, conn_map=CONN_MAP)
    net = Mininet(topo)
    net.start()

    for i in range(2,5):
        print( f"Testing TCP throughput between h1 and h{i}" )
        h1, hi = net.get( 'h1', f'h{i}')
        net.iperf( (h1, hi) )

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    perfTest()