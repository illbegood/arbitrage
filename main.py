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
from trade import trade
from fetch import prefetch, fetch

def run_timed(func, args, time):
    p = multiprocessing.Process(target=func, args=args)
    p.start()
    p.join(time)
    if (p.is_alive()):
        p.terminate()
        p.join()

def process_cycle_iter(graph, monograph):
    while True:
        fetch(graph)
        path = collect_negative_cycle(graph)
        if path != None:
            balance = 100
            logs = process_cycle(graph, monograph, path, balance)
            logger.write(logs)
            #with open("sample.json", "a") as outfile:
            #    json.dump(graph, outfile, indent=2)
            #break
    return path

def search_for_cycles(exch, graph, monograph):
    #paths = []
    while(True):
        #paths.append(process_cycle_iter(exch, graph, monograph))
        process_cycle_iter(exch, graph, monograph)
    
if __name__ == '__main__':
    monograph, graph = prefetch()
    #process_cycle_iter(exch, graph, monograph)
    run_timed(process_cycle_iter, (graph, monograph), 3600)

