# In-Network Caching

The setup works only on Ubuntu 18.04, 20.04 and 22.04. It takes about 100 min to finish executing and requires about 13GB of disk space. It has been tested on Ubuntu 22.04.

![Network Topology](https://github.com/rahulpriolkar/in-network-caching/blob/main/Mininet%20Topology.png?raw=true)

Once the setup has finished
1) cd into the ~/project/tutorials/exercises/netcache directory and execute "make run". This will start the mininet instance.
2) Once the topology is created, cd into "switch_commands" and execute "./populate_switch.sh" and "cd ..". This will add the populate the routing tables.

3) Now open two separate terminals and cd into ~/project/tutorials/simple_switch" and execute "python3 sswitch_CLI.py --thrift-port 9090" and "python3 sswitch_CLI.py --thrift-port 9091" from each. This will start the control planes for the switches S1 and S2 respectively. The control planes will monitor each switch for hot key reports.

4) Now, head over to the mininet prompt, and execute "xterm <node_name>". replace node name with a h1, h2 ... h10
5) On the Xterm terminals execute "./receive.py <node_name>", this will make the node listen for requests, and act as a server.
6) From another xterm, execute "./send.py <server_IP_address> <client_node_name>"
  => eg: if h10 was the server and h1 was the client you would execute "./receive.py h10" on the server and "./send.py 10.4.0.2 h1" on the client.
  => For each client node, in this case h1, another recieve process has to be run i.e "./receive h1" so that it can listen to the responses from the server.
  
  Note: Start both the receive processes first, and then the send process.

This will execute an experiment defined by the parameters sent in the send.py file. In this file's "run" function, one can change the workloads being used by commenting and un-commenting the appropriate lines, and choosing a execute_dynamic_workload / execute_stable_workload funcitons.
=> Use execute_dynamic_workload for hot-in, hot-out, random workloads
=> Use execute_stable_workload funcitons for zipfian, uniform workloads

The receiver stops automatically after a timeout value that can be set in the main's "sniff" function. It is set to 80s by default as the dynamic workloads take about 70s to execute 25,000 requests. The receiver writes the logs collected during the experiment only after it exits gracefully after the timeout. The logs will not be stored if the process is terminated early.

Note: If running a stable workload (zipf or uniform), then the receiver timeout can be reduced to about 50s, since these only issue 10,000 requests in about 40s.

The node logs will be stored in "h1_sent.txt" and "h1_received.txt" files.

Check Performance Parameters: 
=> To check the throughput per sec at a client node, execute "python3 stats.py <node_name>", eg: "python3 stats.py h1". This program will also output the frequency with which each key was accessed after the thoughput window is closed. This can be used figure out the popular and the unpopular keys.

=> To check the latency of a key execute "python3 stats.py <node_name> <key>", eg: "python3 stats.py h1 1". After the latency window is closed, this program also prints out the details of the responder ID for each time the <key> was requested i.e whether the request was resolved by the server (ID = 11), the switch S2 (ID = 1) or the switch S1 (ID = 0)
