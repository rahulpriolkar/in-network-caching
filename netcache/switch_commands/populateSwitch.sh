#!/bin/bash

simple_switch_CLI --thrift-port 9090 < commands_s1.cmd 
simple_switch_CLI --thrift-port 9091 < commands_s2.cmd 
simple_switch_CLI --thrift-port 9092 < commands_s3.cmd 
simple_switch_CLI --thrift-port 9093 < commands_s4.cmd 
simple_switch_CLI --thrift-port 9094 < commands_s5.cmd 
