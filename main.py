import logging
import math
import multiprocessing
import time
import threading
from bellman_ford import collect_negative_cycle
from const import precision, orderbook_depth
from fetch import binance, init, fetch
from process_cycle import process_cycle

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

def search_for_cycles(exch, graph, monograph):
    paths = []
    while(True):
        fetch(exch, graph)
        path = collect_negative_cycle(graph)
        if path not in paths and path != None:
            paths.append(path)
            balance = 100
            logs = process_cycle(graph, monograph, path, exch, balance)
            write_log(logs)
        time.sleep(1)
    
if __name__ == '__main__':
    exch = binance()
    monograph, graph = init(exch)
    time.sleep(1)
    run_timed(search_for_cycles, (exch, graph, monograph), 3600)

