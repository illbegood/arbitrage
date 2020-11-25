import ccxt
import math
from datetime import datetime
import numpy as np
import re

def init():
    binance = ccxt.binance({
    'apiKey': 'y',
    'secret': 'Y', })
    return prefetch(binance)

def get_directions_and_weights(symbol, data):
    node_to, node_from = symbol.split('/')
    try:
        w_to = -math.log(1 / float(data['info']['askPrice']))
        w_from = -math.log(float(data['info']['bidPrice']))
    except:
        w_to = float('inf')
        w_from = float('inf')
    return node_to, node_from, w_to, w_from

def update_monograph(monograph, node_from, node_to):
    if node_from not in monograph:
        monograph[node_from] = []
        monograph[node_from].append(node_to)
        
def update_digraph(digraph, node_from, node_to, w_from, w_to, lazy = True):
    if not lazy:
        if node_from not in digraph:
            digraph[node_from] = {}
        if node_to not in digraph:
            digraph[node_to] = {}
    digraph[node_from][node_to] = w_to
    digraph[node_to][node_from] = w_from

def add_edges(symbol, data, monograph, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(symbol, data)
    update_monograph(monograph, node_from, node_to)
    update_digraph(digraph, node_from, node_to, w_from, w_to, False)

def update_edges(symbol, data, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(symbol, data)
    update_digraph(digraph, node_from, node_to, w_from, w_to)    

def prefetch(exch):
    fee = 0.001
    monograph = {}
    digraph = {}
    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_tickers()
        for symbol, data in exch_tickers.items():
            #try:
            add_edges(symbol, data, monograph, digraph)
            #except:
                #print('symbol error')
    return monograph, digraph
    

def fetch(exch, digraph):
    fee = 0.001
    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_tickers()
        for symbol, data in exch_tickers.items():
            try:
                update_edges(symbol, data, digraph)
            except:
                print('symbol error')

