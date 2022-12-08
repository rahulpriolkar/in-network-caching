import numpy as np
import random
import matplotlib.pyplot as plt
from distributions import Zipf
import constants

def display(distribution):
    min = np.uint64(constants.KEY_MIN)
    max = np.uint64(constants.KEY_MAX)

    q = distribution

    h, bins = np.histogram(q, bins = int(max-min+1),range=(min-0.5,max+0.5))
    #print(h)
    #print(bins)

    plt.hist(q, bins = bins)
    plt.title("Zipf")
    plt.xlabel("key")
    plt.ylabel("Request Count")
    plt.show()

def get_probability_distribution_from_key_ranking(key_ranking, p_prime=[]):
    if len(p_prime) > 0:
        p = np.array([0.0]*len(key_ranking))
        for index in range(len(key_ranking)):
            p[key_ranking[index]-1] = p_prime[index]

    else:
        p = 1.0 / np.power(key_ranking, constants.A)  # probabilities
        p /= np.sum(p)            # normalized

    return p

def hot_in(key_ranking, iterations=4, cold_key_count=10):
    workloads = []
    
    p = get_probability_distribution_from_key_ranking(key_ranking)
    p_prime = p

    distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
    workloads.append(distribution)
    #display(distribution)

    for i in range(iterations):
        cold_keys = key_ranking[-cold_key_count:]
        key_ranking = np.concatenate([cold_keys[::-1], key_ranking[:-cold_key_count]])
        #print(key_ranking)

        p = get_probability_distribution_from_key_ranking(key_ranking, p_prime)

        #print(p)

        distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
        workloads.append(distribution)
        #display(distribution)

    return workloads

def hot_out(key_ranking, iterations=4, cold_key_count=10):
    workloads = []
    
    p = get_probability_distribution_from_key_ranking(key_ranking)
    p_prime = p

    distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
    workloads.append(distribution)
    #display(distribution)

    for i in range(iterations):
        # rotate
        hot_keys = key_ranking[:cold_key_count]
        key_ranking = np.concatenate([key_ranking[cold_key_count:], hot_keys[::-1]])
        #print(key_ranking)
        
        p = get_probability_distribution_from_key_ranking(key_ranking, p_prime)

        distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
        workloads.append(distribution)
        #display(distribution)

    return workloads


def random_workload(key_ranking, iterations=4, cold_key_count=5, M=15):
    workloads = []
    
    p = get_probability_distribution_from_key_ranking(key_ranking)
    p_prime = p
    print(p)

    distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
    workloads.append(distribution)
    #display(distribution)
    
    for i in range(iterations):
        hot_key_ranks_to_swap = random.sample(range(constants.KEY_MIN, constants.KEY_MIN + M), cold_key_count)
        cold_key_ranks_to_swap = random.sample(range(constants.KEY_MAX - M, constants.KEY_MAX), cold_key_count)

        #print(hot_key_ranks_to_swap)
        #print(cold_key_ranks_to_swap)
        
        #swap hot and cold keys
        for key_index in range(len(hot_key_ranks_to_swap)):
            hot_key = hot_key_ranks_to_swap[key_index]
            cold_key = cold_key_ranks_to_swap[key_index]

            key_ranking[hot_key], key_ranking[cold_key] = key_ranking[cold_key], key_ranking[hot_key]
            #p[hot_key], p[cold_key] = p[cold_key], p[hot_key]

        p = get_probability_distribution_from_key_ranking(key_ranking, p_prime)
        #print(key_ranking)
        #print(p)

        distribution = Zipf(a=constants.A, min=constants.KEY_MIN, max=constants.KEY_MAX, size=constants.SIZE, p=p)
        workloads.append(distribution)
        #display(distribution)

    return workloads

if __name__ == "__main__":
    key_ranking = np.arange(1, 200+1)
    #hot_in(key_ranking, iterations=4, cold_key_count=10)
    #hot_out(key_ranking, iterations=4, cold_key_count=10)
    random_workload(key_ranking, iterations=4, cold_key_count=5, M=15)
