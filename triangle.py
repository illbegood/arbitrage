def findNegativeTriangles(graph):
	result = []
	visited = set()
	for u in graph:
		visited.add(u)
		for v in graph[u]:
			if v not in visited:
				for w in graph[v]:
					if w not in visited and graph[w][u] in graph[w] and isNegative(graph, u, v, w):
						result.append([u, v, w])

def isNegative(graph, u, v, w):
	return graph[u][v] + graph[v][w] + graph[w][u] < 0