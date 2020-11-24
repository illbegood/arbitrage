import csv
import math

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

def print_results(graph, paths):
    for path in paths:
        if path == None:
            print("No opportunity here :(")
        else:
            print(path)
            graph_sum = 0
            table = []
            for i in range(len(path) - 1):
                weight = graph[path[i]][path[i + 1]]['weight']
                w_e = math.exp(-weight)
                table.append([w_e, 1/w_e, weight])
                graph_sum += weight
            print(tabulate(table, headers=["CUR1_CUR2", "CUR2_CUR1", "LN(CUR1_CUR2)"]))
            print('total sum:')
            print(graph_sum)
            print('profit')
            print(math.exp(-graph_sum))
            
from bellman_ford import collect_negative_cycle
from fetch import binance_graph

graph = binance_graph()
#graph = read_graph_scv("out.csv")
paths = collect_negative_cycle(graph)
print_results(graph, paths)


