import logging
import math
import multiprocessing
import time
import threading
import json

import logger
from bellman_ford import collect_negative_cycle
from const import precision, orderbook_depth
from process_cycle import process_cycle
from fetch import prefetch, fetch, binance

def write_log(deq, filename='log'):
    logging.basicConfig(filename=filename, level=logging.ERROR, format='%(message)s')
    message = ' '.join(map(str, deq)) + '\n'
    logging.error(message)

def run_timed(func, args, time):
    p = multiprocessing.Process(target=func, args=args)
    p.start()
    p.join(time)
    if (p.is_alive()):
        p.terminate()
        p.join()

def process_cycle_iter(exch, graph, monograph):
    while True:
        fetch(exch, graph)
        path = collect_negative_cycle(graph)
        if path != None:
            balance = 100
            logs = process_cycle(graph, monograph, path, exch, balance)
            logger.write(logs)
            with open("sample.json", "a") as outfile:
                json.dump(graph, outfile, indent=2)
            break
    return path

def search_for_cycles(exch, graph, monograph):
    #paths = []
    while(True):
        #paths.append(process_cycle_iter(exch, graph, monograph))
        process_cycle_iter(exch, graph, monograph)
    
if __name__ == '__main__':
    exch = binance()
    monograph, graph = prefetch(exch)
    process_cycle_iter(exch, graph, monograph)
    #run_timed(search_for_cycles, (exch, graph, monograph), 3600)

