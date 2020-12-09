import csv
import math
import ccxt
import time
import threading
import multiprocessing
import logging
import tabulate
from process_cycle import process_cycle
from bellman_ford import collect_negative_cycle
import logger
import fetch
from const import precision, orderbook_depth
   
def print_results(graph, path):
    if path == None:
        print("No opportunity here :(")
    else:
        print(path)
        graph_sum = 0
        table = []
        for i in range(len(path) - 1):
            weight = graph[path[i]][path[i + 1]]
            w_e = math.exp(-weight)
            table.append([w_e, 1/w_e, weight])
            graph_sum += weight
        print(tabulate.tabulate(table, headers=["CUR1_CUR2", "CUR2_CUR1", "LN(CUR1->CUR2)"]))
        print('total sum:')
        print(graph_sum)
        print('profit')
        print(math.exp(-graph_sum))

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
        fetch.fetch(exch, graph)
        path = collect_negative_cycle(graph)
        if path not in paths and path != None:
            paths.append(path)
            balance = 100
            process_cycle(graph, monograph, path, exch, balance)
        time.sleep(1)
import json  
if __name__ == '__main__':
    exch = fetch.binance()
    #monograph, graph = fetch.init(exch)
    #with open("sample.json", "a") as outfile:
    #    json.dump(graph, outfile)
    #quit()
    #run_timed(search_for_cycles, (exch, graph, monograph), 3600)
