from os import path

from graph import Graph
from graph.reader import ReaderORLibrary

def read_problem(*filepath):

    filename = path.join(*filepath)
    reader = ReaderORLibrary()
    STPG = reader.parser(filename)
    STPG.graph = Graph(edges=STPG.graph)

    return STPG

def display(population):
    size = len(population)
    msg = f"Population {population.id} | size {size} | generation {population.generation}"
    print(msg)
