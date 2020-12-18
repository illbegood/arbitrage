import math
from tabulate import tabulate


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
        print(tabulate(table, headers=[
              "CUR1_CUR2", "CUR2_CUR1", "LN(CUR1->CUR2)"]))
        print('total sum:')
        print(graph_sum)
        print('profit')
        print(math.exp(-graph_sum))


def triangles(graph):
    result = []
    visited = set()
    for u in graph:
        for v in graph[u]:
            if v not in visited:
                for w in graph[v]:
                    if w not in visited and u in graph[w]:
                        result.append([u, v, w])
        visited.add(u)
    return result

from fetch import prefetch
from trade import trade
from triangle import triangles
import logger

monograph, graph, restrictions = prefetch()
profits = []
for t in triangles(graph):
    logs = trade(graph, monograph, t, restrictions)
    logger.write(logs)
    for tpl in logs:
        if 'expected_profit: ' in tpl:
            profits.append(tpl[1])
print(sum(profits)/len(profits))

