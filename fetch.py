import ccxt
import math
from datetime import datetime
import numpy as np
import re
from const import fee
import string
import random

def binance():
    letter = random.choice(string.ascii_letters)
    return ccxt.binance({
    'apiKey': letter,
    'secret': letter.swapcase(), })

def init(exch):
    return prefetch(exch)

def get_directions_and_weights(symbol, data):
    node_from, node_to = symbol.split('/')
    try:
        w_to = -math.log(1 / float(data['info']['askPrice'])) - math.log(1 - fee)
        w_from = -math.log(float(data['info']['bidPrice'])) - math.log(1 - fee)
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

def add_edges(symbol, data, monograph, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(symbol, data)
    update_monograph(monograph, node_from, node_to)
    update_digraph(digraph, node_from, node_to, w_from, w_to, False)

def update_edges(symbol, data, digraph):
    node_to, node_from, w_to, w_from = get_directions_and_weights(symbol, data)
    update_digraph(digraph, node_from, node_to, w_from, w_to)    

def prefetch(exch):
    monograph = {}
    digraph = {}
    exch.load_markets()
    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_bids_asks()
        for symbol, data in exch_tickers.items():
            try:
                add_edges(symbol, data, monograph, digraph)
            except:
                print('symbol error')
    return monograph, digraph
    

def fetch(exch, digraph):
    #exch.load_markets()
    exch = binance()
    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_bids_asks()
        for symbol, data in exch_tickers.items():
            try:
                update_edges(symbol, data, digraph)
            except:
                print('symbol error')

