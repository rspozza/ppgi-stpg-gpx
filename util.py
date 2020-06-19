from os import path

from graph import Graph
from graph.reader import ReaderORLibrary

STEIN_B = [
    ("steinb1.txt",   82), # 0
    ("steinb2.txt",   83),
    ("steinb3.txt",  138),
    ("steinb4.txt",   59),
    ("steinb5.txt",   61), # 4
    ("steinb6.txt",  122),
    ("steinb7.txt",  111),
    ("steinb8.txt",  104),
    ("steinb9.txt",  220), # 8
    ("steinb10.txt",  86),
    ("steinb11.txt",  88),
    ("steinb12.txt", 174),
    ("steinb13.txt", 165), # 12
    ("steinb14.txt", 235),
    ("steinb15.txt", 318), # 14
    ("steinb16.txt", 127), # 15
    ("steinb17.txt", 131), # 16
    ("steinb18.txt", 218), # 17
]

def read_problem(*filepath):

    filename = path.join(*filepath)
    reader = ReaderORLibrary()
    STPG = reader.parser(filename)

    return STPG

def display(population):
    size = len(population)
    msg = f"Population {population.id} | size {size} | generation {population.generation}"
    print(msg)
