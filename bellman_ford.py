import math

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
    # If the distance between the node and the neighbour is lower than the one I have now
    if d[neighbour] > d[node] + graph[node][neighbour]:
        # Record this lower distance
        d[neighbour] = d[node] + graph[node][neighbour]
        p[neighbour] = node
 
def retrace_negative_loop(p, start):
    arbitrageLoop = [start]
    if p[start] == None:
        return None
    next_node = start
    while True:
        #print(next_node)
        next_node = p[next_node]
        if next_node not in arbitrageLoop:
            arbitrageLoop.append(next_node)
        else:
            if next_node == start:
                arbitrageLoop.append(next_node)
                reversed_arbitrageLoop = arbitrageLoop[::-1]
                return reversed_arbitrageLoop
            return None


def bellman_ford(graph, source):
    d, p = initialize(graph, source)
    for _ in range(len(graph)-1): #Run this until is converges
        for u in graph:
            for v in graph[u]: #For each neighbour of u
                relax(u, v, graph, d, p) #Lets relax it


    # Step 3: check for negative-weight cycles
    for u in graph:
        for v in graph[u]:
            if d[v] < d[u] + graph[u][v]:
                return(retrace_negative_loop(p, source))
    return None
            
def collect_negative_cycle(graph, start='USDT'):
    #paths = []
    path = bellman_ford(graph, start)
    #if path not in paths and not None:
    #    paths.append(path)
    return path
