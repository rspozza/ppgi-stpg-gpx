import os
import time

from ga4stpg.binary.combiner import crossover_1point, crossover_2points, crossover_uniform
from ga4stpg.binary.chromosome import random_binary
from ga4stpg.condition import BestKnownReached, BestSolutionKnowReached, Stagnation
from ga4stpg.customevol import GeneticEvolution as Evolution
from ga4stpg.customevol import GeneticPopulation as Population
from ga4stpg.binary.mutate import flip_onebit
from ga4stpg.normalization import normalize
from ga4stpg.pickers import random_picker
from ga4stpg.selector import roullete
from ga4stpg.tracker import DataTracker
from ga4stpg.util import STEIN_B, display, update_best, update_generation
from ga4stpg.graph import Graph
from ga4stpg.graph.reader import read_problem
from ga4stpg.evaluation import Eval


def simulation(simulation_name, params : dict, get_evol : callable):

    STPG = read_problem("data", "ORLibrary", params["dataset"])
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
