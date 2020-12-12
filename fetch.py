import math
import binance
from const import FEE

def create_monograph():
    monograph = {}
    exch_tickers = binance.fetch_tickers()
    for nodes in exch_tickers:
        monograph_add_edge(monograph, nodes[0][0], nodes[0][1])
    return monograph

def monograph_add_edge(monograph, node_from, node_to):
    if node_from not in monograph:
        monograph[node_from] = []
    #not sure it's needed
    if node_to not in monograph[node_from]:
        monograph[node_from].append(node_to)

def get_weights(ask_price, bid_price):
    try:
        w_to = math.log(ask_price / (1 - FEE))
        w_from = math.log(1 / (bid_price * (1 - FEE)))
    except:
        w_to = float('inf')
        w_from = float('inf')
    return w_to, w_from
    
def edge_set_weight(digraph, node_from, node_to, w):
    if w == float('inf') and node_to in digraph[node_from]:
        del digraph[node_from][node_to]
    else:
        digraph[node_from][node_to] = w

def add_edges(nodes, ask_price, bid_price, monograph, digraph):
    node_from, node_to = nodes[0], nodes[1]
    monograph_add_edge(monograph, node_from, node_to)
    if node_from not in digraph:
        digraph[node_from] = {}
    if node_to not in digraph:
        digraph[node_to] = {}
    w_to, w_from = get_weights(ask_price, bid_price)
    edge_set_weight(digraph, node_from, node_to, w_from)
    edge_set_weight(digraph, node_to, node_from, w_to)

def update_weights(nodes, ask_price, bid_price, digraph):
    node_from, node_to = nodes[0], nodes[1]
    w_to, w_from = get_weights(ask_price, bid_price)
    edge_set_weight(digraph, node_from, node_to, w_from)
    edge_set_weight(digraph, node_to, node_from, w_to)

def prefetch():
    monograph = {}
    digraph = {}
    exch_tickers = binance.fetch_tickers()
    for nodes, ask_price, bid_price in exch_tickers:
        add_edges(nodes, ask_price, bid_price, monograph, digraph)
    return monograph, digraph

def fetch(digraph):
    exch_tickers = binance.fetch_tickers()
    for nodes, ask_price, bid_price in exch_tickers:
        update_weights(nodes, ask_price, bid_price, digraph)




