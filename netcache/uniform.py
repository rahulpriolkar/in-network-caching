import random

def uniform(min, max, size):
    workload = []
    for i in range(size):
        workload.append(random.randint(min, max))
    return workload
