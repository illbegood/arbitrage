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
from fetch import binance, init, fetch

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

def _test(n):
    a = 0
    for i in range(n):
        a += math.tan(i)
    return a

def search_for_cycles(exch, graph, monograph):
    paths = []
    while(True):
        fetch(exch, graph)
        path = collect_negative_cycle(graph)
        if path not in paths and path != None:
            print_results(graph, path)
            paths.append(path)
            balance = 100
            orderbook_depth = 10
            precision = 8
            process_cycle(graph, monograph, path, exch, balance, orderbook_depth, precision)
            break
    print('total number of cycles detected:', len(paths))


start = time.time()


exch = binance()    
monograph, graph = init(exch)
run_timed(search_for_cycles, (exch, graph, monograph), 3600)

#run_timed(_test, (10000000,), 4)
#graph = read_graph_scv("in.csv")
#path = collect_negative_cycle(graph)
#print_results(graph, path)
end = time.time()
print(end - start)