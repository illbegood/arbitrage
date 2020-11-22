
import ccxt
import math
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import cvxpy as cvx
import numpy as np

def fetch_exchange(exch_name, exch):
    nodes = set()
    edges = []
    # load markets
    market = exch.load_markets(True)
    #huobi.load_markets(True)

    if (exch.has['fetchTickers']):
        exch_tickers = exch.fetch_tickers()
        for symbol in exch_tickers.keys():
            try:
                node_to, node_from = symbol.split('/')
                node_to += '.' + exch_name
                node_from += '.' + exch_name
                nodes.add(node_to)
                nodes.add(node_from)
                if (exch_name == 'binance'):
                    try:
                        w_to = -math.log(1 / float(exch_tickers[symbol]['info']['askPrice']))
                        w_from = - math.log(float(exch_tickers[symbol]['info']['askPrice']))
                        precision = int(market[symbol]['precision']['amount'])
                        fee = 1 - 0.001
                    except:
                        w_to = float('inf')
                        w_from = float('inf')
                        precision = 1
                        fee = 0
                else:
                    try:
                        w_to = -math.log(1 / float(exch_tickers[symbol]['ask']))
                        w_from = -math.log(float(exch_tickers[symbol]['ask']))
                        fee = 1 - 0.00026
                    except:
                        w_to = float('inf')
                        w_from = float('inf')
                        fee = 0
                edges.append((node_from, node_to, dict(c='buy', d='direct', weight=w_to, fee=fee, p=precision)))
                edges.append((node_to, node_from, dict(c='sell', d='reverse', weight=w_from, fee=fee, p=precision)))
            except:
                print('symbol error')
    return nodes, edges
