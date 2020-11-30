import csv
import math
import ccxt
import time
import threading
import multiprocessing
from process_cycle import process_cycle

def write_graph_csv(graph, filepath):
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([''] + list(graph))
        key_to_idx = {value: key for key, value in enumerate(graph)}
        for u in graph:
            l = [''] * len(graph)
            for (key, value) in graph[u].items():
                l[key_to_idx[key]] = value
            l[key_to_idx[u]] = 1
            writer.writerow([u] + l)

def read_graph_scv(filepath):
    with open(filepath, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        graph = {i: {} for i in reader.__next__()[1:]}
        for row in reader:
            w = row[0]
            for u, v in zip(graph, row[1:]):
                if v != '' and w != u:
                    graph[w][u] = float(v)
    return graph
    

from tabulate import tabulate

def print_results(graph, path):
    #for path in paths:
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
        print(tabulate(table, headers=["CUR1_CUR2", "CUR2_CUR1", "LN(CUR1->CUR2)"]))
        print('total sum:')
        print(graph_sum)
        print('profit')
        print(math.exp(-graph_sum))
            
from bellman_ford import collect_negative_cycle
from fetch import binance, init, fetch

def run_process(func, args):
    func(args)

def run_timed(func, args, time):
    p = multiprocessing.Process(target=run_process, args=(func, args))
    p.start()
    p.join(time)
    if (p.is_alive()):
        p.terminate()
        p.join()

def _test(n):
    a = 1
    for i in range(n):
        a += math.tan(i)
    return a

def search_for_cycles(graph, monograph):
    binance = ccxt.binance({
        'apiKey': 'l',
        'secret': 'L', })
    paths = []
    while(True):
        fetch(binance, graph)
        path = collect_negative_cycle(graph)
        if path not in paths and path != None:
            print_results(graph, path)
            paths.append(path)
            balance = 100
            orderbook_depth = 10
            precision = 8
            process_cycle(graph, monograph, path, binance, balance, orderbook_depth, precision)
            break
    print('total number of cycles detected:', len(paths))


from time import sleep

start = time.time()
#exch = binance()    
#monograph, graph = init(exch)
#run_timed(search_for_cycles, (graph, monograph), 3600)
#search_for_cycles(graph, monograph)
run_timed(_test, (20000000), 1)

#graph = read_graph_scv("in.csv")
#path = collect_negative_cycle(graph)
#print_results(graph, path)
end = time.time()
print(end - start)
'''
if path != None:
    binance = ccxt.binance({
        'apiKey': 'y',
        'secret': 'Y', })
    balance = 100
    orderbook_depth = 10
    precision = 8
    process_cycle(graph, path, binance, balance, orderbook_depth, precision)
'''