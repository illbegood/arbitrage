def findNegativeTriangles(graph):
	result = []
	visited = []
	for u in graph:
		for v in graph[u]:
			if v not in visited:
				for w in graph[v]:
					if w not in visited and u in graph[w] and isNegative(graph, u, v, w):
						result.append([u, v, w])
		visited.append(u)

def isNegative(graph, u, v, w):
	return graph[u][v] + graph[v][w] + graph[w][u] < 0

def triangles(graph):
    result = []
    visited = []
    for u in graph:
        for v in graph[u]:
            if v not in visited:
                for w in graph[v]:
                    if w not in visited and u in graph[w]:
                        result.append([u, v, w, u])
        visited.append(u)
    return result