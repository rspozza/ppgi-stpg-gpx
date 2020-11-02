import os
import time

from base.binary.combiner import crossover_1point, crossover_2points, crossover_uniform
from base.chromosome import random_binary
from base.condition import BestKnownReached, BestSolutionKnowReached, Stagnation
from base.customevol import SteinerEvolution as Evolution
from base.customevol import SteinerPopulation as Population
from base.mutate import flip_onebit
from base.normalization import normalize
from base.pickers import random_picker
from base.selector import roullete
from base.tracker import DataTracker
from base.util import STEIN_B, display, update_best, update_generation
from graph import Graph
from graph.reader import read_problem
from evaluation import Eval


def simulation(simulation_name, params : dict, get_evol : callable):

    STPG = read_problem("datasets", "ORLibrary", params["dataset"])
    lenght = STPG.nro_nodes - STPG.nro_terminals

    tracker = DataTracker(params['runtrial'], target=os.path.join("outputdata", simulation_name, STPG.name))

    population = (Population(chromosomes=[ random_binary(lenght) for _ in range(params["population_size"]) ],
                            eval_function=Eval(STPG),
                            maximize=True)
                            .evaluate()
                            .callback(normalize)
                            .callback(update_best))

    evol = get_evol(STPG, tracker, params)

    with Stagnation(interval=params["stagnation_interval"]), \
        BestSolutionKnowReached(global_optimum=params["global_optimum"], STPG=STPG):
        result = population.evolve(evol, n=params["n_iterations"])

    tracker.log_simulation(params, STPG, result)
    tracker.report()

    print(result.stoppedby)

    return result


def sim_binary_1pointcrossover(STPG, tracker, params):

    binary = (Evolution()
                .evaluate()
                .callback(normalize)
                .callback(update_best)
                .callback(tracker.log_evaluation)
                .select(selection_func=roullete)
                .crossover(combiner=crossover_1point, parent_picker=random_picker)
                .mutate(mutate_function=flip_onebit, probability=params['tx_mutation'])
                .callback(update_generation)
                .callback(display, every=100))

    return binary


def sim_binary_2pointcrossover(STPG, tracker, params):

    binary = (Evolution()
                .evaluate()
                .callback(normalize)
                .callback(update_best)
                .callback(tracker.log_evaluation)
                .select(selection_func=roullete)
                .crossover(combiner=crossover_2points, parent_picker=random_picker)
                .mutate(mutate_function=flip_onebit, probability=params['tx_mutation'])
                .callback(update_generation)
                .callback(display, every=100))

    return binary


def sim_binary_uniformcrossover(STPG, tracker, params):

    binary = (Evolution()
                .evaluate()
                .callback(normalize)
                .callback(update_best)
                .callback(tracker.log_evaluation)
                .select(selection_func=roullete)
                .crossover(combiner=crossover_uniform, parent_picker=random_picker, pbcrossover=params['pbcrossover'])
                .mutate(mutate_function=flip_onebit, probability=params['tx_mutation'])
                .callback(update_generation)
                .callback(display, every=100))

    return binary

if __name__ == "__main__":

    PARAMS = {
        'runtrial' : 0,
        'dataset' : 'steinb1.txt',
        'global_optimum'       : 82,
        'population_size'     : 100,
        'tx_mutation'         : 0.2,
        'n_iterations'        : 100,
        'stagnation_interval' : 1_000,
        'pbcrossover' : 0.5
    }

    for dataset, value in STEIN_B:
        print('='*10,'\n', dataset)
        PARAMS['dataset'] = dataset
        PARAMS['global_optimum'] = value
        for i in range(30):
            PARAMS['runtrial'] = i + 1
            simulation("20200711_binary_uniformcrossover", PARAMS, get_evol=sim_binary_uniformcrossover)

