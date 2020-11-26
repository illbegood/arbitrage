import csv
import math
import ccxt
import time
from process_cycle import process_cycle

def write_graph_csv(graph, filepath):
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([''] + list(graph))
        key_to_idx = {value: key for key, value in enumerate(graph)}
        for u in graph:
            l = [''] * len(graph)
            for (key, value) in graph[u].items():
                l[key_to_idx[key]] = value['weight']
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
                    graph[w][u] = {'weight': float(v), 'd': 'direct'}
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
from fetch import init, fetch

def search_for_cycles(time_interval, graph):
    start_time = time.time()
    time_now = time.time()
    paths = []
    while(time_now - start_time <= time_interval):
        fetch(binance, graph)
        path = collect_negative_cycle(graph)
        if path not in paths and path != None:
            print_results(graph, path)
            paths.append(path)
        time.sleep(0.3)
        time_now = time.time()
    print('total number of cycles detected:', len(paths))

    
monograph, graph = init()
time_interval = 3600
search_for_cycles(time_interval, graph)

#graph = read_graph_scv("in.csv")
#path = collect_negative_cycle(graph)
#print_results(graph, path)

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

