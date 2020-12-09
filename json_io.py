import json
import datetime

#def read(filepath):
#    return json.load(filepath)

def write(graph):
    filepath = "../data/json/" + str(datetime.datetime.now())
    with open(filepath, "w") as outfile:
                json.dump(graph, outfile, indent=2)
