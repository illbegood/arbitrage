import ccxt
import math
from datetime import datetime
import numpy as np
import re

def fetch_exchange(exch_name, exch):
    graph = {}
    # load markets
    market = exch.load_markets(True)

    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_tickers()
        for symbol in exch_tickers.keys():
            try:
                node_to, node_from = symbol.split('/')
                try:
                    w_to = -math.log(1 / float(exch_tickers[symbol]['info']['askPrice']))
                    w_from = - math.log(float(exch_tickers[symbol]['info']['bidPrice']))
                    #precision = int(market[symbol]['precision']['amount'])
                    #fee = 1 - 0.001
                except:
                    w_to = float('inf')
                    w_from = float('inf')
                    precision = 1
                    fee = 0
                if node_from not in graph:
                    graph[node_from] = {}
                graph[node_from][node_to] = {'weight': w_to, 'd': 'direct'}
                if node_to not in graph:
                    graph[node_to] = {}
                graph[node_to][node_from] = {'weight': w_from, 'd': 'reverse'}
            except:
                print('symbol error')
    return graph

