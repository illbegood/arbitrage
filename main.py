import logging
import math
import multiprocessing
import time
import threading
import json

import logger
#import json_io
#import csv_io
from bellman_ford import collect_negative_cycle
from trade import trade
from fetch import prefetch, fetch, create_monograph

def run_timed(func, args, time):
    p = multiprocessing.Process(target=func, args=args)
    p.start()
    p.join(time)
    if (p.is_alive()):
        p.terminate()
        p.join()

def process_cycle(monograph, graph):
    cycle = collect_negative_cycle(graph)
    if cycle != None:
        balance = 100
        logs = trade(graph, monograph, cycle, balance)
        logger.write(logs)
        #json_io.save(graph)
        #csv_io.save(graph)
        time.sleep(1)
    time.sleep(2)

def search_for_cycles(monograph, graph):
    #paths = []
    while(True):
        fetch(graph)
        process_cycle(monograph, graph)
    
if __name__ == '__main__':
    #monograph, graph = create_monograph(), json_io.load('data/json/sample.json')
    monograph, graph = prefetch()
    #process_cycle(monograph, graph)
    #monograph, graph = prefetch()
    search_for_cycles(monograph, graph)
    #run_timed(search_for_cycles, (monograph, graph), 3600)

