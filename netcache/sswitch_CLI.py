#!/usr/bin/env python3
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Antonin Bas (antonin@barefootnetworks.com)
#
#

import runtime_CLI
from runtime_CLI import UIn_Error

from functools import wraps
import os
import sys

from sswitch_runtime import SimpleSwitch
from sswitch_runtime.ttypes import *

import nnpy
import ipaddress
import struct

import bmpy_utils as utils

import time
from datetime import datetime
import numpy as np

def handle_bad_input(f):
    @wraps(f)
    @runtime_CLI.handle_bad_input
    def handle(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except InvalidMirroringOperation as e:
            error = MirroringOperationErrorCode._VALUES_TO_NAMES[e.code]
            print("Invalid mirroring operation (%s)" % error)
    return handle

class SimpleSwitchAPI(runtime_CLI.RuntimeAPI):
    @staticmethod
    def get_thrift_services():
        return [("simple_switch", SimpleSwitch.Client)]

    def __init__(self, pre_type, standard_client, mc_client, sswitch_client):
        runtime_CLI.RuntimeAPI.__init__(self, pre_type,
                                        standard_client, mc_client)
        self.sswitch_client = sswitch_client

    @handle_bad_input
    def do_set_queue_depth(self, line):
        "Set depth of one / all egress queue(s): set_queue_depth <nb_pkts> [<egress_port> [<priority>]]"
        args = line.split()
        self.at_least_n_args(args, 1)
        depth = self.parse_int(args[0], "nb_pkts")
        if len(args) > 2:
            port = self.parse_int(args[1], "egress_port")
            priority = self.parse_int(args[2], "priority")
            self.sswitch_client.set_egress_priority_queue_depth(port, priority, depth)
        elif len(args) == 2:
            port = self.parse_int(args[1], "egress_port")
            self.sswitch_client.set_egress_queue_depth(port, depth)
        else:
            self.sswitch_client.set_all_egress_queue_depths(depth)

    @handle_bad_input
    def do_set_queue_rate(self, line):
        "Set rate of one / all egress queue(s): set_queue_rate <rate_pps> [<egress_port> [<priority>]]"
        args = line.split()
        self.at_least_n_args(args, 1)
        rate = self.parse_int(args[0], "rate_pps")
        if len(args) > 2:
            port = self.parse_int(args[1], "egress_port")
            priority = self.parse_int(args[2], "priority")
            self.sswitch_client.set_egress_priority_queue_rate(port, priority, rate)
        elif len(args) == 2:
            port = self.parse_int(args[1], "egress_port")
            self.sswitch_client.set_egress_queue_rate(port, rate)
        else:
            self.sswitch_client.set_all_egress_queue_rates(rate)

    @handle_bad_input
    def do_mirroring_add(self, line):
        "Add mirroring session to unicast port: mirroring_add <mirror_id> <egress_port>"
        args = line.split()
        self.exactly_n_args(args, 2)
        mirror_id = self.parse_int(args[0], "mirror_id")
        egress_port = self.parse_int(args[1], "egress_port")
        config = MirroringSessionConfig(port=egress_port)
        self.sswitch_client.mirroring_session_add(mirror_id, config)

    @handle_bad_input
    def do_mirroring_add_mc(self, line):
        "Add mirroring session to multicast group: mirroring_add_mc <mirror_id> <mgrp>"
        args = line.split()
        self.exactly_n_args(args, 2)
        mirror_id = self.parse_int(args[0], "mirror_id")
        mgrp = self.parse_int(args[1], "mgrp")
        config = MirroringSessionConfig(mgid=mgrp)
        self.sswitch_client.mirroring_session_add(mirror_id, config)

    @handle_bad_input
    def do_mirroring_delete(self, line):
        "Delete mirroring session: mirroring_delete <mirror_id>"
        args = line.split()
        self.exactly_n_args(args, 1)
        mirror_id = self.parse_int(args[0], "mirror_id")
        self.sswitch_client.mirroring_session_delete(mirror_id)

    @handle_bad_input
    def do_mirroring_get(self, line):
        "Display mirroring session: mirroring_get <mirror_id>"
        args = line.split()
        self.exactly_n_args(args, 1)
        mirror_id = self.parse_int(args[0], "mirror_id")
        config = self.sswitch_client.mirroring_session_get(mirror_id)
        print(config)

    @handle_bad_input
    def do_get_time_elapsed(self, line):
        "Get time elapsed (in microseconds) since the switch started: get_time_elapsed"
        print(self.sswitch_client.get_time_elapsed_us())

    @handle_bad_input
    def do_get_time_since_epoch(self, line):
        "Get time elapsed (in microseconds) since the switch clock's epoch: get_time_since_epoch"
        print(self.sswitch_client.get_time_since_epoch_us())

def listen_for_digests(controller):
    sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
    socket = controller.client.bm_mgmt_get_info().notifications_socket
    socket = "ipc:///tmp/bmv2-0-notifications.ipc"
    sub.connect(socket)
    sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')
    
    while True:
        message = sub.recv()
        print(message)
        on_message_recv(message, controller)

def on_message_recv(msg, controller):
    _, _, ctx_id, list_id, buffer_id, num = struct.unpack("<iQiiQi", msg[:32])

    msg = msg[32:]
    offset = 4

    for m in range(num):
        key = struct.unpack("!H", msg[0:offset])
        print('key = ', str(key))
        msg = msg[offset:]

        # Perform Operation

    # For listening to the next digest message
    controller.client.bm_learning_ack_buffer(ctx_id, list_id, buffer_id)

db = {}
def load_db():
    global db
    file = open("../exercises/ProjectTestCustomHeaderCache/KeyVal.txt", "r+")
    for line in file:
        key, val = line.split()
        db[int(key)] = int(val)
    file.close()

def main():
    args = runtime_CLI.get_parser().parse_args()
    print(args)

    args.pre = runtime_CLI.PreType.SimplePreLAG

    services = runtime_CLI.RuntimeAPI.get_thrift_services(args.pre)
    services.extend(SimpleSwitchAPI.get_thrift_services())

    standard_client, mc_client, sswitch_client = runtime_CLI.thrift_connect(
        args.thrift_ip, args.thrift_port, services
    )
    
    runtime_CLI.load_json_config(standard_client, args.json)

    runtime_API = SimpleSwitchAPI(args.pre, standard_client, mc_client, sswitch_client);
    
    # set switch_ID
    switch_ID = args.thrift_port - 9090
    print("Switch ID = ", switch_ID)
    runtime_API.do_register_write("switch_ID 0 {}".format(switch_ID))

    cache_size = 32

    # clear cache
    for index in range(cache_size):
        runtime_API.do_register_write("cache 0 {}".format(index))

    runtime_API.do_table_clear("MyIngress.key_lookup")
    clear_query_statistics_module(runtime_API, cache_size)

    load_db()
    global db
    count = 0
    start = time.time()
    key_index_map = {}
    key_handle_map = {}

    log = {}

    hot_keys = set()
    prev_hot_key = -1
    while True:
        count += 1
        hot_key_val = int(runtime_API.do_register_read("hot_key 0"));


        value_to_cache = int(hot_key_val >> 16)
        hot_key = int(hot_key_val - value_to_cache*2**16)

        if hot_key == 0 or hot_key == prev_hot_key:
            pass
        else:
            #print("hot_key_val = ",hot_key_val)
            #print("hot_key = ", hot_key)
            #print("value_found = ", value_to_cache)

            #if(db[hot_key] != value_to_cache):
               # print("hot_key = ", hot_key)
               # print("db = ", db[hot_key], "value_found = ", value_to_cache)
               # print("value mismatch")
               # return

            current_time = datetime.utcnow()
            log[current_time] = hot_key

            #hot_keys.add(hot_key)
            prev_hot_key = hot_key    

            # find the least active key's index in the cache
            key_counter = runtime_API.do_register_read("keyCounter")
            key_counter = np.array(key_counter)
            min_index = np.argmin(key_counter) # index of the cache and the key counter, with min count

            # check if the key_map_index has the cache index already populated
            is_index_occupied = min_index in list(key_index_map.values())

            # evict key at min_index from table key_lookup
            if is_index_occupied:
                key_to_delete = list(key_index_map.keys())[list(key_index_map.values()).index(min_index)]
                handle_to_delete = key_handle_map[key_to_delete]
                runtime_API.do_table_delete("MyIngress.key_lookup {}".format(handle_to_delete))
                del key_handle_map[key_to_delete]
                del key_index_map[key_to_delete]

            # replace cache at idx[i] with new hot_key's val
            #runtime_API.do_register_write("cache {} {}".format(min_index, db[hot_key]))
            runtime_API.do_register_write("cache {} {}".format(min_index, value_to_cache))

            # add new hot_key => idx[i] rule to key_lookup table
            entry_handle = runtime_API.do_table_add("MyIngress.key_lookup MyIngress.key_match {} => {}".format(hot_key, min_index))
            key_handle_map[hot_key] = entry_handle
            key_index_map[hot_key] = min_index
        
        #print("current threshold: ", runtime_API.do_register_read("threshold_reg 0"))
        pkt_count = int(runtime_API.do_register_read("packet_counter 0"))
        if count % 800 == 0:
            print(pkt_count, int(pkt_count*0.025))
        new_threshold = int(pkt_count*0.025)
        runtime_API.do_register_write("threshold_reg 0 {}".format(new_threshold))

        if(time.time() - start > 5.5):
            count = 0
            #print(log)
            sub_start_time = time.time()
             
            # Clear Query Stats module
            hot_keys.clear()
            clear_query_statistics_module(runtime_API, cache_size)

            sub_end_time = time.time()
            print("sub time: ", sub_end_time-sub_start_time)

            print(time.time() - start)
            start = time.time()

def clear_query_statistics_module(runtime_API, cache_size):
    runtime_API.do_register_write("hot_key 0 0")

    # clear count min arrays
    for i in range(1024):
        runtime_API.do_register_write("countMinArr1 {} 0".format(i))
        runtime_API.do_register_write("countMinArr2 {} 0".format(i))
        runtime_API.do_register_write("countMinArr3 {} 0".format(i))
        runtime_API.do_register_write("countMinArr4 {} 0".format(i))

    # clear packet counter
    runtime_API.do_register_write("packet_counter 0 0")

    # clear key counters
    for i in range(cache_size):
        runtime_API.do_register_write("keyCounter {} 0".format(i))

if __name__ == '__main__':
    main()
