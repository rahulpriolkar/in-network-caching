#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

from scapy.all import (
    bind_layers,
    BitField,
    Packet,
    Ether,
    IP,
    TCP,
    FieldLenField,
    FieldListField,
    IntField,
    IPOption,
    ShortField,
    get_if_list,
    sniff,
    conf
)
from scapy.layers.inet import _IPOption_HDR


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]

class CUSTOM(Packet):
    name = "custom"
    fields_desc = [BitField("ID", 0, 32), BitField("key", 0, 32), BitField("val", 0, 32), BitField("hit", 0, 32), BitField("responder_ID", 0, 32)]

def on_receive(l2_socket):
    def handle_pkt(packet):
        pkt = packet
        try:
            if((pkt[IP] and pkt[IP].ttl == 64) or len(pkt.payload.layers()) > 2):
                return
        except:
            return
        #print("ttl = ", pkt[IP].ttl, "layers= ", len(pkt.payload.layers()))
        print("received!")
        pkt.show()
        if IP in pkt:
            pkt = bytes(pkt)
            
            custom_pkt_bytes = pkt[len(pkt)-20:len(pkt)]

            ID = int.from_bytes(custom_pkt_bytes[0:4], "big")
            key = int.from_bytes(custom_pkt_bytes[4:8], "big")
            val = int.from_bytes(custom_pkt_bytes[8:12], "big")
            hit = int.from_bytes(custom_pkt_bytes[12:16], "big")
            responder_ID = int.from_bytes(custom_pkt_bytes[16:20], "big")
            print("ID = ", ID, "hit = ", hit, "key = ", key, "responder_ID = ", responder_ID)

            # Received query response
            if(hit == 1):
                global stats
                print("HIT! Received key = ", key)
                stats[ID] = {"key": key, "value": val, "endTime": datetime.utcnow(), "responderID": responder_ID }
                return

            global count
            global start_time
            global end_time
            global response_stats

            if(count == 1):
                start_time = time.time()
            #stats[ID] = {"key": key, "value": val, "endTime": datetime.utcnow()}
            count += 1
            if(count % 100 == 0):
                print(count)

            temp = packet[IP].dst
            packet[IP].dst = packet[IP].src
            packet[IP].src = temp

            packet[IP].ttl = 64

            packet[IP].remove_payload()
            packet = packet / CUSTOM(ID=ID, key=key, val=db[key], hit=1, responder_ID=11)
            response_stats[ID] = {"key": key, "value": db[key], "endTime": datetime.utcnow(), "responderID": responder_ID }
            #bind_layers(IP, CUSTOM)

            print("Responding to = ", key)
            l2_socket.send(packet)

    return handle_pkt;


count = 1
start_time = 1
end_time = 1
stats = {}
db = {}
response_stats = {}

def write_stats(iface, name):
    file = open("{}_received.txt".format(str(name)), "w+")
    for ID in stats.keys():
        file.write("{} {} {} {} {}\n".format(ID, stats[ID]["key"], stats[ID]["endTime"], stats[ID]["value"], stats[ID]["responderID"]))
    file.close()

    '''
    file = open("{}_sent.txt".format(str(name)), "w+")
    for ID in response_stats.keys():
        file.write("{} {} {} {} {}\n".format(ID, response_stats[ID]["key"], response_stats[ID]["endTime"], response_stats[ID]["value"], response_stats[ID]["responderID"]))
    file.close()
    '''

def load_db():
    global db
    file = open("KeyVal.txt", "r+")
    for line in file:
        key, val = line.split()
        db[int(key)] = int(val)
    file.close()

def main():
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]

    print("sniffing on %s" % iface)

    s = conf.L2socket(iface=iface)
    sys.stdout.flush()

    load_db()
    global db

    sniff(iface = iface, prn = on_receive(s), timeout=80)

    print("Stopped Sniffing")
    name = sys.argv[1]
    write_stats(iface, name)

if __name__ == '__main__':
    main()
