# In-Network Caching

This project implements the NetCache Protocol in the P4 language, making slight modifications to it as required, replicates the results obtained in the paper by testing the caching scheme on various stable Zipfian and Uniform workloads, as well as various dynamic workloads. The performance parameters evaluated include "throughput (queries resolved) / sec" and "key access latency". 

The project attempts to test if the protocol can be extended to run in the core network switches, instead of a single ToR switch. Tests are conducted to verify the following hypothesis:

1) When the caching scheme is implemented at a network level, a key should first get cached at the switch nearest to the server, followed by the next switch, a chain which continues till the key gets cached at the switch nearest to the client requesting it.

2) According to the NetCache scheme, the keys should get cached at the least common ancestor (LCA) switch with respect to the set of clients requesting the key. The data is expected to be cached, initially, at the switches along the path from the least common ancestor (LCA) of the nodes requesting the data key, to the server hosting the data. Later, once the data starts being served from the LCA switch, the rest of the switches are expected to evict the key from their caches.

## Project Setup and Instructions

The setup works only on Ubuntu 18.04, 20.04 and 22.04. It takes about 100 min to finish executing and requires about 13GB of disk space. It has been tested on Ubuntu 22.04.

<!-- ![Network Topology](https://github.com/rahulpriolkar/in-network-caching/blob/main/Mininet%20Topology.png?raw=true =200x200) -->
### Network Topology
<p align="center">
  <img src="https://github.com/rahulpriolkar/in-network-caching/blob/main/Mininet%20Topology.png?raw=true" height="450" width="600" text-align="center">
</p>

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

This will execute an experiment defined by the parameters sent in the send.py file. In this file's "run" function, one can change the workloads being used by commenting and un-commenting the appropriate lines, and choosing a execute_dynamic_workload / execute_stable_workload functions.

- Use execute_dynamic_workload for hot-in, hot-out, random workloads

- Use execute_stable_workload funcitons for zipfian, uniform workloads

The receiver stops automatically after a timeout value that can be set in the main's "sniff" function. It is set to 80s by default as the dynamic workloads take about 70s to execute 25,000 requests. The receiver writes the logs collected during the experiment only after it exits gracefully after the timeout. The logs will not be stored if the process is terminated early.

Note: If running a stable workload (zipf or uniform), then the receiver timeout can be reduced to about 50s, since these only issue 10,000 requests in about 40s.

The node logs will be stored in "h1_sent.txt" and "h1_received.txt" files.

Performance Parameter Evaluation: 

1) **Throughput per sec**: At a client node, execute "python3 stats.py <node_name>", eg: "python3 stats.py h1". This program will also output the frequency with which each key was accessed after the thoughput window is closed. This can be used figure out the popular and the unpopular keys.

2) **Latency of a key**: At a client node, execute "python3 stats.py <node_name> <key>", eg: "python3 stats.py h1 1". After the latency window is closed, this program also prints out the details of the responder ID for each time the <key> was requested i.e whether the request was resolved by the server (ID = 11), the switch S2 (ID = 1) or the switch S1 (ID = 0)
  
  
## Results
### Stable Workloads
  
  1) **Zipfian**: The caching scheme provides a higher and more consistent throughput (Fig. 9) than the one obtained without caching any keys (Fig. 10). The key access latency observed for a popular key (Fig. 11), confirms the hypothesis that the keys would get cached and served from the switches closest to the server, followed by the ones closer to the client. In this experiment, the key is first served from the server where the latencies achieved are north of 150ms. The key is then served from the switch S2, where the latency achieved is between 50 and 80ms. Finally as the key is served from S1, the average latency drops below 30 ms, with the exception of a few outliers.
The key access latency of an unpopular key (Fig. 12), lies in between 50-100ms, as opposed to the average latency of a key obtained without caching, which is about 400ms (Fig. 13). This difference in the two latencies, even though both are served from the server, is assumed to be because of higher load on the server in the latter case. The server load is lower with caching as the frequently requested keys are cached and served from the switches, resulting in lower latencies for the unpopular keys.
 <p align="center">
  <img width="582" alt="Zipfian Workloads" src="https://user-images.githubusercontent.com/43360749/210122874-22dce1f3-9a5e-412a-8dfd-bcb176daa2e7.png">
</p>
  
  2) **Uniform**: The caching scheme does not perform well with uniform distribution, as very few keys cross the count-min threshold. And the keys that become hot, do not stay hot for a long enough time to experience the benefits of the switch cache. Hence it is observed that the caching scheme (Fig. 16), performs just as bad as the one without caching (Fig.17), in terms of latency. On the other hand, it is observed that the throughput without caching (Fig. 15) is slightly higher and more consistent than the one with the caching scheme (Fig. 14). This result is against the expectation. One possible expla- nation for the reduced throughput could be the computational overhead of NetCache, with very few keys actually getting cached.
  
  <p align="center">
    <img width="584" alt="Uniform Workloads" src="https://user-images.githubusercontent.com/43360749/210122976-aaa0b257-ed7f-4ff8-8532-99833d9e6a44.png">
  </p>
  
### Dynamic Workloads
  
  1) **Hot-In**: The average throughput with the caching so- lution (Fig.18) is consistently higher (above 350 queries/sec) as compared to the one without caching (Fig. 19), which is around 300(queries/sec). The key access latencies for popular (Fig. 20) and unpopular keys (Fig. 21) with the caching
Fig. 19. Hot-In Workload Throughput (Without Caching) solution, and a key without the caching solution (Fig. 22) behaves similar to those seen in the zipfian stable workload. The steep drops in Fig. 18, at 20s, 30s, 40s, 60s is indicative of the drastic change in the workloads being introduced every 10s, with the bottom 10 cold keys being brought to the top.
  
  <p align="center">
    <img width="594" alt="Hot-In Workloads" src="https://user-images.githubusercontent.com/43360749/210123201-48dc156d-b3ee-4516-83e7-f039c600d2cf.png">
  </p>
  
  2) **Random**: The throughput with the caching scheme (Fig. 23), behaves in a very similar manner, consistently higher than the one without caching (Fig. 24). The absence of steep drops in throughput every 10s (Fig. 23), confirms that the Random workload is less drastic than the Hot-In workload.
The key access latency of a popular key with caching is seen in Fig. 25. The key which was initially hot was served at low latencies. It was later swapped with a cold key, between requests 4000 and 8000, where it was not requested. Finally it was swapped again with a hot key, and was continued to be served at low latencies.
The key access latencies of the unpopular key with caching (Fig. 26), and a key without the caching solutions (Fig. 27) behave similar those seen in the zipfian stable and the Hot-in workloads.
  
  <p align="center">
    <img width="574" alt="Random Workloads" src="https://user-images.githubusercontent.com/43360749/210123272-f464f2e5-7c6b-479e-b747-048941872c39.png">
  </p>

  3) **Hot-Out**: The Hot-out workload shows expected results, with a higher throughput achieved using the caching scheme, and the key access latencies behaving similar to that of the stable zipfian workload. This confirms that the Hot-Out workload is the least drastic as compared to the Hot-In and Random workloads.
  
  <p align="center">
    <img width="553" alt="Hot-Out Workloads" src="https://user-images.githubusercontent.com/43360749/210123352-cf5fc0fc-a9fd-4fcc-b3f4-a2bdcaf0a6fe.png">
  </p>
  
## Conclusion & Future Work
  The project involves fine tuning of several parameters for the caching scheme to work efficiently, which is done by manually checking various conditions like the size of the key space, type of workloads, the rate at which keys are requested etc. Unless the parameter fine tuning is automated, such a caching scheme is not scalable. The large number of variables also makes the caching scheme very difficult to debug, especially while conducting tests on large network topologies.

  From the experiments conducted, it can be concluded that the keys first get cached and are served from the switch closest to the server, followed by the ones closer to the client, until it is served from the switch one hop away from the client. (Hypothesis 1)
  
  Future work includes automating the parameter fine-tuning task and thoroughly testing and verifying hypothesis 2.
