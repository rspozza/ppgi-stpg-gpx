import os
import time

from base.chromosome import random_binary
from base.combiner import crossover_2points
from base.condition import IterationLimit, Stagnation
from base.customevol import SteinerEvolution as Evolution
from base.customevol import SteinerPopulation as Population
from base.mutate import flip_onebit
from base.normalization import normalize
from base.selector import roullete
from base.tracker import DataTracker
from base.util import display, update_best, update_generation
from graph import Graph
from graph.reader import read_problem
from pxsimpliest import SimpliestPX
from treetools import Converter, Eval

PARAMS = {
    'runtrial' : 0,
    'dataset' : 'steinb1.txt',
    'globaloptimum'       : 82,
    'population_size'     : 100,
    'tx_mutation'         : 0.2,
    'n_iterations'        : 2,
    'iteration_binary'    : 250,
    'iteration_treegraph' : 250,
    'stagnation_interval' : 1_000,
}


def simulation(simulation_name, params : dict):

    STPG = read_problem("datasets", "ORLibrary", params["dataset"])
    lenght = STPG.nro_nodes - STPG.nro_terminals
    converter = Converter(STPG)
    tracker = DataTracker(params['runtrial'], target=os.path.join("outputdata", simulation_name, STPG.name))

    population = (Population(chromosomes=[ random_binary(lenght) for _ in range(params["population_size"]) ],
                            eval_function=Eval(STPG),
                            maximize=True)
                            .evaluate()
                            .callback(normalize)
                            .callback(update_best)
                            )

    binary = (Evolution()
                .evaluate()
                .callback(normalize)
                .callback(update_best)
                .callback(tracker.log_evaluation)
                .select(selection_func=roullete)
                .crossover(combiner=crossover_2points)
                .mutate(mutate_function=flip_onebit, probability=0.2)
                .callback(update_generation)
                .callback(display, every=100)
                )

    treegraph = (Evolution()
                .evaluate()
                .callback(normalize)
                .callback(update_best)
                .callback(tracker.log_evaluation)
                .select(selection_func=roullete)
                .crossover(combiner=SimpliestPX(STPG)) # .mutate(mutate_function=flip_onebit, probability=0.2)
                .callback(update_generation)
                .callback(display, every=100)
                )

    hybridi = (Evolution()
                .repeat(binary, n=200)
                .map(converter.binary2treegraph)
                .repeat(treegraph, n=200)
                .map(converter.treegraph2binary)
                )

    with IterationLimit(limit=101), \
        Stagnation(interval=params["stagnation_interval"]):
        result = population.evolve(hybridi, n=params["n_iterations"])

    # result = population.evolve(hybridi, n=params["n_iterations"])

    tracker.log_simulation(params, STPG, result)
    tracker.report()

    print(result.stoppedby)

    return result

if __name__ == "__main__":

    simulation("test", PARAMS)
