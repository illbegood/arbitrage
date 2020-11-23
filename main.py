import ccxt
import math


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

def collect_negative_cycle():
    binance = ccxt.binance({
    'apiKey': 'y',
    'secret': 'Y', })
    
    paths = []
    from fetch import fetch_exchange
    graph = fetch_exchange('binance', binance)
    from bellman_ford import bellman_ford
    path = bellman_ford(graph, 'USDT')
    if path not in paths and not None:
        paths.append(path)
    print_results(graph, paths)
       

collect_negative_cycle()
