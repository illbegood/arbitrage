import math
from const import fee, quote_assets, base_url, orderbook_depth
import string
import random
import requests
    
def split_symbol(symbol):
    if symbol[-3:] in quote_assets:
        return symbol[:-3], symbol[-3:]
    return symbol[:-4], symbol[-4:]

def binance_fetch_tickers():
    url = base_url + '/api/v3/ticker/bookTicker'
    response = requests.get(url).json()
    tickers = list(map(lambda x: [split_symbol(x['symbol']), float(x['askPrice']), float(x['bidPrice'])], response))
    return tickers
    
def binance_fetch_orderbook(symbol):
    url = base_url + "/api/v3/depth"
    orderbook = requests.get(url, {'symbol': symbol, 'limit' : orderbook_depth}).json()
    return orderbook

def get_directions_and_weights(nodes, ask_price, bid_price):
    node_from, node_to = nodes[0], nodes[1]
    try:
        w_to = math.log(ask_price / math.log(1 - fee))
        w_from = math.log(1 / (bid_price * (1 - fee)))
    except:
        w_to = float('inf')
        w_from = float('inf')
    return node_to, node_from, w_to, w_from

def update_monograph(monograph, node_from, node_to):
    if node_from not in monograph:
        monograph[node_from] = []
    if node_to not in monograph[node_from]:
        monograph[node_from].append(node_to)
        
def update_digraph(digraph, node_from, node_to, w_from, w_to, lazy = True):
    if not lazy:
        if node_from not in digraph:
            digraph[node_from] = {}
        if node_to not in digraph:
            digraph[node_to] = {}
    if w_to != float('inf'):
        digraph[node_from][node_to] = w_to
    if w_from != float('inf'):
        digraph[node_to][node_from] = w_from

def add_edges(nodes, ask_price, bid_price, monograph, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(nodes, ask_price, bid_price)
    update_monograph(monograph, node_from, node_to)
    update_digraph(digraph, node_from, node_to, w_from, w_to, False)

def update_edges(nodes, ask_price, bid_price, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(nodes, ask_price, bid_price)
    update_digraph(digraph, node_from, node_to, w_from, w_to)

def prefetch():
    monograph = {}
    digraph = {}
    exch_tickers = binance_fetch_tickers()
    for nodes, ask_price, bid_price in exch_tickers:
        add_edges(nodes, ask_price, bid_price, monograph, digraph)
    return monograph, digraph

def fetch(digraph):
    exch_tickers = binance_fetch_tickers()
    for nodes, ask_price, bid_price in exch_tickers:
        update_edges(nodes, ask_price, bid_price, digraph)

