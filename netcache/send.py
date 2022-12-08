#!/usr/bin/env python3
import random
import socket
import sys
import time
from datetime import datetime

import netifaces as ni
from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp, bind_layers, BitField, Packet
from scapy.all import *

import numpy as np

from distributions import uniform, Zipf
from dynamic_workloads import hot_in, hot_out, random_workload

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class CUSTOM(Packet):
    name = "custom"
    fields_desc = [BitField("ID", 0, 32), BitField("key", 0, 32), BitField("val", 0, 32), BitField("hit", 0, 32), BitField("responder_ID", 0, 32)]

def send_request(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, ID, key):
    #print("sending on interface %s to %s" % (iface, str(dst_addr)))
    pkt = Ether(src=host_mac, dst=dst_mac)
    pkt = pkt / IP(src=host_ip, dst=dst_ip) / CUSTOM(ID=ID, key=key, hit=0)
    bind_layers(IP, CUSTOM)
    #pkt.show()
    l2_socket.send(pkt)

stats = {}

def execute_stable_workload(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, node, workload, stats):
    ID = 0
    for index in range(len(workload)):
        key = int(workload[index])

        # Stats
        stats[ID] = {"key": key, "startTime": datetime.utcnow()}
         
        send_request(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, ID, key)

        ID += 1

        if(ID % 50 == 0):
            time.sleep(0.1)

def execute_dynamic_workload(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, node, workloads, stats, iterations):
    ID = 0
    workload_ID = 0
    while workload_ID < iterations:
        print("Strting workload")
        workload = workloads[workload_ID]
        
        workload_start_time = time.time()
        for index in range(len(workload)):
            if time.time()-workload_start_time > 10:
                break

            key = int(workload[index])

            # Stats
            stats[ID] = {"key": key, "startTime": datetime.utcnow()}
             
            send_request(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, ID, key)

            ID += 1

            if(ID % 50 == 0):
                time.sleep(0.1)

        workload_ID += 1


def run(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, node):
    global stats

    size = 10000
    cold_key_count = 10
    iterations = 7
    key_ranking = np.arange(1, 200+1)

    #workloads = random_workload(key_ranking, iterations)
    #workloads = hot_in(key_ranking, iterations, cold_key_count)
    workloads = hot_out(key_ranking, iterations, cold_key_count)

    #workload = uniform(1, 200, 10000)
    #workload = Zipf(1.2, 1, 200, 10000)

    start = time.time()

    execute_dynamic_workload(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, node, workloads, stats, iterations)
    #execute_stable_workload(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, node,workload, stats)

    write_stats(node)

def generate_workload(a=1.2, min=np.uint64(1), max=np.uint64(200), size=10000):
    return Zipf(a, min, max, size)

def write_stats(node):
    file = open("{}_sent.txt".format(node), "w+")
    for ID in stats.keys():
        file.write("{} {} {}\n".format(ID, stats[ID]["key"], stats[ID]["startTime"]))
    file.close()

def main():

    if len(sys.argv) < 2:
        print('pass 2 arguments: <destination> <node_name>')
        exit(1)

    iface = get_if()
    host_mac = get_if_hwaddr(iface)
    dst_mac = '08:00:00:00:0a:aa'
    host_ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
    dst_ip = socket.gethostbyname(sys.argv[1])

    l2_socket = conf.L2socket(iface=iface)

    start_time = time.time()
    
    run(l2_socket, iface, host_mac, dst_mac, host_ip, dst_ip, sys.argv[2])

    print('DONE!')
    print('Time = ', time.time() - start_time)
    return

if __name__ == '__main__':
    main()
