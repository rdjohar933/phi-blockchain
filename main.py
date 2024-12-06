from multiprocessing.pool import Pool

import blockchain_api
import multiprocessing


if __name__ == '__main__':

    initial_port = 5000
    number_of_instances = 3
    processes = []
    with Pool(number_of_instances) as pool:
        pool.map(blockchain_api.main, range(initial_port + 1, initial_port + number_of_instances+1))