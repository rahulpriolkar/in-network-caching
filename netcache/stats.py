from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import re
import sys
import operator

def convert_str_time_to_datetime(time):
    time_elements = re.split(r'-| |:|\.', time)
    time_elements = list(map(lambda t: int(t), time_elements))    
    return datetime(time_elements[0], time_elements[1], time_elements[2], time_elements[3], time_elements[4], time_elements[5], time_elements[6])

def read_file_into_obj(filename):
    obj = {}
    file = open(filename)
    for line in file:
        line = line.split()
        ID = line[0]
        time = line[2] + " " + line[3]

        obj[ID] = { "time": convert_str_time_to_datetime(str(time)), "key": line[1] }

        if(len(line) >= 5):
            obj[ID]["value"] = line[4]
        if(len(line) >= 6):
            obj[ID]["responderID"] = line[5]

    file.close()
    return obj

def plot_key_latency(key_stats):
    x = []
    y = []
    z = []

    print(key_stats)
    
    for stats_obj in key_stats:
        for key in stats_obj.keys():
            if key != "responderID":
                x.append(int(key))
                y.append(int(stats_obj[key].microseconds) / 1000)
                z.append(int(stats_obj["responderID"]))


    colors = ['red', 'green', 'yellow']
    c = []
    for num in z:
        if num == 11:
            c.append(colors[2])
        else:
            c.append(colors[num])

    fig, ax = plt.subplots()
    plt.plot(x, y)

    plt.xlabel("Request ID")
    plt.ylabel("Latency (ms)")
    

    x_labels = []
    for i in range(len(x)):
        if(i % 200 == 0):
            x_labels.append(x[i])

    plt.show()

def plot_throughput_per_sec(throughput_sec_arr):
    x = []
    for i in range(len(throughput_sec_arr)):
        x.append(i)
    y = throughput_sec_arr

    plt.xlabel("Time (seconds)")
    plt.ylabel("Throughput(Queries resolved / sec)")
    plt.plot(x, y)
    plt.show()

def show_key_access_statistics(sent):
    freq = {}
    for ID in sent.keys():
        key = sent[ID]["key"]
        if key in freq:
            freq[key] += 1
        else:
            freq[key] = 1

    freq_sorted = dict(sorted(freq.items(), key=operator.itemgetter(1), reverse=True))

    print(freq_sorted)
    return freq_sorted

def calculate_key_latency(sent, received, display_key="1001"):
    ID_latency = {}
    key_stats = {} 
    for ID in sent.keys():
        if ID in received:
            ID_latency[ID] = received[ID]["time"] - sent[ID]["time"]
            
            key = received[ID]["key"]
            if key not in key_stats:
                key_stats[key] = []

            key_stats[key].append({ "{}".format(ID): ID_latency[ID], "responderID": received[ID]["responderID"]})

    print(key_stats[display_key])
    plot_key_latency(key_stats[display_key])

    return key_stats

def calculate_responder_IDs(node, key):
    responder_IDs = []

    received_filename = "{}_received.txt".format(node)
    file = open(received_filename)
    for line in file:
        line = line.split()
        if(key == line[1]):
            responder_IDs.append([line[0], line[5]])
    print("responder IDs => ", responder_IDs)
    return responder_IDs

def calculate_throughput(sent, received):
    sent_time_arr = []
    received_time_arr = []

    for ID in sent.keys():
        sent_time_arr.append(sent[ID]["time"])
    for ID in received.keys():
        received_time_arr.append(received[ID]["time"])
    
    sent_time_arr.sort()
    received_time_arr.sort()
    start_time = sent_time_arr[0]

    throughput_sec_arr = []
    current_time = received_time_arr[0]
    i = 0
    while i < len(received_time_arr):
        current_time += timedelta(seconds=1)
        temp = 0
        while(i < len(received_time_arr) and received_time_arr[i] < current_time):
           temp += 1 
           i += 1
        throughput_sec_arr.append(temp)

    print(throughput_sec_arr)
    plot_throughput_per_sec(throughput_sec_arr)

    return throughput_sec_arr

if __name__ == "__main__":

    node = sys.argv[1]

    sent_filename = "{}_sent.txt".format(node)
    received_filename = "{}_received.txt".format(node)

    sent = read_file_into_obj(sent_filename)
    received = read_file_into_obj(received_filename)

    if(len(sys.argv) == 3):
        key = sys.argv[2]
        calculate_key_latency(sent, received, key)
        calculate_responder_IDs(node, key)
    if(len(sys.argv) == 2):
        show_key_access_statistics(sent)
        calculate_throughput(sent, received)
