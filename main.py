import ccxt

from fetch import fetch_exchange
from bellman_ford import bellman_ford
import debug

def collect_negative_cycle():
    binance = ccxt.binance({
    'apiKey': 'y',
    'secret': 'Y', })
    
    paths = []
    graph = fetch_exchange('binance', binance)
    path = bellman_ford(graph, 'USDT')
    if path not in paths and not None:
        paths.append(path)
    #debug.print_results(graph, paths)
    #debug.write_graph_csv(graph, "test.csv")
    #debug.read_graph_scv("test.csv")
    debug.write_graph_csv(debug.read_graph_scv("in.csv"), "out.csv")
       

collect_negative_cycle()
