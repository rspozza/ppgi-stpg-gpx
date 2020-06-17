import time
from os import path

from base.chromosome import random_binary
from base.combiner import crossover_2points
from base.condition import IterationLimit, Stagnation
from base.customevol import SteinerEvolution as Evolution
from base.customevol import SteinerPopulation as Population
from base.mutate import flip_onebit
from base.normalization import normalize
from base.selector import roullete
from graph import Graph
from graph.reader import ReaderORLibrary
from pxsimpliest import SimpliestPX
from treetools import Converter, Eval
from util import display, read_problem

PARAMS = {
    'dataset' : 'steinb1.txt',
    'best_known_cost' : 82,
    'population_size' : 100,
    'n_iterations' : 25,
    'stagnation_interval' : 1_000,
}


def simulation(params : dict, trial=0, output=None):

    STPG = read_problem("datasets", "ORLibrary", params["dataset"])

    population_size = params["population_size"]
    lenght = STPG.nro_nodes - STPG.nro_terminals

    converter = Converter(STPG)

    population = (Population(chromosomes=[random_binary(lenght) for _ in range(population_size)],
                            eval_function=Eval(STPG),
                            maximize=True)
                        .evaluate()
                        .callback(normalize))

    binary = (Evolution()
                .select(selection_func=roullete)
                .crossover(combiner=crossover_2points)
                .mutate(mutate_function=flip_onebit, probability=0.2)
                .evaluate()
                .callback(normalize)
                .callback(display, every=100))

    treegraph = (Evolution()
                .select(selection_func=roullete)
                .crossover(combiner=SimpliestPX(STPG)) # .mutate(mutate_function=flip_onebit, probability=0.2)
                .evaluate()
                .callback(normalize)
                .callback(display, every=100))

    hybridi = (Evolution()
                .repeat(binary, n=200)
                .map(converter.binary2treegraph)
                .evaluate()
                .repeat(treegraph, n=200)
                .map(converter.treegraph2binary)
                .evaluate())

    # with IterationLimit(limit=params["n_iterations"]), \
    #     Stagnation(interval=params["stagnation_interval"]):
    #     result = population.evolve(hybridi, n=params["n_iterations"])

    result = population.evolve(hybridi, n=params["n_iterations"])

    return result

if __name__ == "__main__":

    simulation(PARAMS)
