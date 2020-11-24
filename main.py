import ccxt
from fetch import fetch_exchange
from bellman_ford import bellman_ford
from debug import write_graph_csv, read_graph_scv, print_results

def collect_negative_cycle():
    binance = ccxt.binance({
    'apiKey': 'y',
    'secret': 'Y', })
    
    paths = []
    #graph = fetch_exchange('binance', binance)
    graph = read_graph_scv("out.csv")
    path = bellman_ford(graph, 'USDT')
    if path not in paths and not None:
        paths.append(path)
    #print_results(graph, paths)
    print_results(graph, paths)
    #read_graph_scv("test.csv")
    #write_graph_csv(read_graph_scv("in.csv"), "out.csv")
       

collect_negative_cycle()
