import ccxt
from fetch import fetch_exchange
from bellman_ford import bellman_ford

def collect_negative_cycle(graph):
    #binance = ccxt.binance({
    #'apiKey': 'y',
    #'secret': 'Y', })
    
    paths = []
    #graph = fetch_exchange('binance', binance)
    path = bellman_ford(graph, 'USDT')
    if path not in paths and not None:
        paths.append(path)
    return paths
