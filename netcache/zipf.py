import numpy as np
from matplotlib import pyplot as plt
import random
import sys

#np.set_printoptions(threshold=sys.maxsize)
#a = 1.01
#n = 2500
#s = np.random.zipf(a, size=n)
#unique, counts = np.unique(s, return_counts=True)
#print(np.asarray((counts)).T)
#print(s)

def Zipf(a: np.float64, min: np.uint64, max: np.uint64, size=None):
    """
    Generate Zipf-like random variables,
    but in inclusive [min...max] interval
    """
    if min == 0:
        raise ZeroDivisionError("")

    v = np.arange(min, max+1) # values to sample
    p = 1.0 / np.power(v, a)  # probabilities
    p /= np.sum(p)            # normalized
    
    '''
    temp = p[0:10]
    temp = temp[::-1]
    p = np.concatenate([p[10:], temp])
    print("p", p)

    for i in range(18):
        cold_key_count = 10
        temp = p[-cold_key_count:]
        temp = temp[::-1]
        p = np.concatenate([temp, p[:-cold_key_count]])
    '''


    return np.random.choice(v, size=size, replace=True, p=p)

min = np.uint64(1)
max = np.uint64(200)

q = Zipf(1.2, min, max, 10000)
print(q)

h, bins = np.histogram(q, bins = int(max-min+1),range=(min-0.5,max+0.5))
print(h)
print(bins)

plt.hist(q, bins = bins)
plt.title("Zipf")
plt.xlabel("key")
plt.ylabel("Request Count")
plt.show()
