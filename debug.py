import math

from fetch import prefetch
from trade import trade
from triangle import triangles
import logger

monograph, graph, restrictions = prefetch()
profits = []
_triangles_ = triangles(graph)
_triangles_ = list(filter(lambda x: 'USDT' in x or 'BTC' in x or 'ETH' in x, _triangles_))
for t in triangles(graph):
    logs = trade(graph, monograph, t, restrictions)
    logger.write(logs)

