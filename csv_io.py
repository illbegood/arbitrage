import csv
from datetime import datetime

CSV_PATH = 'data/csv/'
SAMPLE_PATH = CSV_PATH + 'sample.csv'

def save(graph, filepath = CSV_PATH + str(datetime.now()) + '.csv'):
    with open(filepath, 'w+', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([''] + list(graph))
        key_to_idx = {value: key for key, value in enumerate(graph)}
        for u in graph:
            l = [''] * len(graph)
            for (key, value) in graph[u].items():
                l[key_to_idx[key]] = value
            l[key_to_idx[u]] = 1
            writer.writerow([u] + l)

def load(filepath = SAMPLE_PATH):
    with open(filepath, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        graph = {i: {} for i in reader.__next__()[1:]}
        for row in reader:
            w = row[0]
            for u, v in zip(graph, row[1:]):
                if v != '' and w != u:
                    graph[w][u] = float(v)
    return graph
 