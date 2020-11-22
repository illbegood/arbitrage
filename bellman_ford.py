import ccxt
import math
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import cvxpy as cvx
import numpy as np
import re
import fetch


# Step 1: For each node prepare the destination and predecessor
def initialize(graph, source):
    d = {} # Stands for destination
    p = {} # Stands for predecessor
    for node in graph:
        d[node] = float('Inf') # We start admiting that the rest of nodes are very very far
        p[node] = None
    d[source] = 0 # For the source we know how to reach
    return d, p
 
def relax(node, neighbour, graph, d, p):
    fee = -math.log(1 - 0.001)
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph[node][neighbour]['weight'] + fee:
        # Record this lower distance
        d[neighbour]  = d[node] + graph[node][neighbour]['weight'] + fee
        p[neighbour] = node
 
def retrace_negative_loop(p, start):
	arbitrageLoop = [start]
	next_node = start
	while True:
		next_node = p[next_node]
		if next_node not in arbitrageLoop:
			arbitrageLoop.append(next_node)
		else:
			arbitrageLoop.append(next_node)
			arbitrageLoop = arbitrageLoop[arbitrageLoop.index(next_node):]
			return arbitrageLoop


def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for i in range(len(graph)-1): #Run this until is converges
        for u in graph:
            for v in graph[u]: #For each neighbour of u
                relax(u, v, graph, d, p) #Lets relax it


    # Step 3: check for negative-weight cycles
    for u in graph:
        for v in graph[u]:
        	if d[v] < d[u] + graph[u][v]['weight']:
        		return(retrace_negative_loop(p, source))
    return None


def collect_negative_cycle():
    binance = ccxt.binance({
    'apiKey': '!',
    'secret': '!', })
    
    paths = []
    graph = fetch_exchange('binance', binance)

    for key in graph:
        path = bellman_ford(graph, key)
        if path not in paths and not None:
            paths.append(path)

    for path in paths:
        if path == None:
            print("No opportunity here :(")
        else:
            print(path)
