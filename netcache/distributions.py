import numpy as np
import random

def uniform(min, max, size):
    workload = []
    for i in range(size):
        workload.append(random.randint(min, max))
    return workload

def Zipf(a: np.float64, min: np.uint64, max: np.uint64, size=None, p=np.array([])):
    if min == 0:
        raise ZeroDivisionError("")

    v = np.arange(min, max+1) # values to sample

    if p.size == 0:
        p = 1.0 / np.power(v, a)  # probabilities
        p /= np.sum(p)            # normalized

    return np.random.choice(v, size=size, replace=True, p=p)
