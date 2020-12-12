import json
from datetime import datetime

JSON_PATH = "data/json/"
SAMPLE_PATH = JSON_PATH + 'sample.json'

def load(filepath = SAMPLE_PATH):
    with open(filepath, 'r') as f:
        graph = json.load(f)
        return graph

def save(graph, filepath = JSON_PATH + str(datetime.now()) + '.json'):
    with open(filepath, 'w+') as f:
        json.dump(graph, f, indent=2)
