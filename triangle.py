def findNegativeTriangles(graph):
	result = []
	visited = set()
	for u in graph:
		for v in graph[u]:
			if v not in visited:
				for w in graph[v]:
					if w not in visited and isNegative(graph, u, v, w):
						result.append([u, v, w])
		visited.add(u)

def isNegative(graph, u, v, w):
	return graph[u][v] + graph[v][w] + graph[w][u] < 0