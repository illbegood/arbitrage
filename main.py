import ccxt
import math
from fetch import fetch_exchange
from bellman_ford import bellman_ford

def collect_negative_cycle():
    binance = ccxt.binance({
    'apiKey': 'y',
    'secret': 'Y', })
    
    paths = []
    graph = fetch_exchange('binance', binance)
    path = bellman_ford(graph, 'USDT')
    if path not in paths and not None:
        paths.append(path)

    for path in paths:
        if path == None:
            print("No opportunity here :(")
        else:
            print(path)
            graph_sum = 0
            for i in range(len(path) - 1):
                print(math.exp(-graph[path[i]][path[i + 1]]['weight']))
                graph_sum += graph[path[i]][path[i + 1]]['weight']
            print('total sum:')
            print(graph_sum)
            print('profit')
            print(math.exp(-graph_sum))

collect_negative_cycle()
