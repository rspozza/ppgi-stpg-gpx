import os

from ga4stpg.binary import random_binary
from ga4stpg.binary.crossover import cx1_point, cx2_points, uniform
from ga4stpg.binary.evaluation import EvaluateBinary
from ga4stpg.binary.mutate import flip_onebit
from ga4stpg.binary.coder import Coder
from ga4stpg.condition import (BestKnownReached,
                               BestSteinerTreeReachead,
                               Stagnation)
from ga4stpg.customevol import GeneticEvolution as Evolution
from ga4stpg.customevol import GeneticPopulation as Population
from ga4stpg.graph import Graph
from ga4stpg.graph.reader import read_problem
from ga4stpg.normalization import normalize
from ga4stpg.pickers import random_picker
from ga4stpg.selector import roullete
from ga4stpg.tracker import DataTracker
from ga4stpg.util import STEIN_B, display, update_best, update_generation


def simulation(simulation_name, params : dict, get_evol : callable):

    STPG = read_problem("datasets", "ORLibrary", params["dataset"])
    lenght = STPG.nro_nodes - STPG.nro_terminals

    tracker = DataTracker(params['runtrial'], target=os.path.join("data", simulation_name, STPG.name))

    population = (Population(chromosomes=[ random_binary(lenght) for _ in range(params["population_size"]) ],
                            eval_function=EvaluateBinary(STPG),
                            maximize=True)
                            .evaluate()
                            .callback(normalize)
                            .callback(update_best))

    evol = get_evol(STPG, tracker, params)

    # with Stagnation(interval=params["stagnation_interval"]), \
    with BestSteinerTreeReachead(global_optimum=params["global_optimum"],
                                STPG=STPG,
                                decoder=Coder(STPG).binary2treegraph,
                                ):
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
                .crossover(combiner=cx1_point, parent_picker=random_picker)
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
                .crossover(combiner=cx2_points, parent_picker=random_picker)
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
                .crossover(combiner=uniform, parent_picker=random_picker, pbcrossover=params['pbcrossover'])
                .mutate(mutate_function=flip_onebit, probability=params['tx_mutation'])
                .callback(update_generation)
                .callback(display, every=100))

    return binary

if __name__ == "__main__":

    PARAMS = {
        'runtrial' : 0,
        'dataset' : 'steinb1.txt',
        'global_optimum'       : 82,
        'population_size'     : 50,
        'tx_mutation'         : 0.2,
        'n_iterations'        : 4_000,
        'stagnation_interval' : 500,
        'pbcrossover' : 0.9
    }

    for dataset, value in STEIN_B[2:3]:
        print('='*10,'\n', dataset)
        PARAMS['dataset'] = dataset
        PARAMS['global_optimum'] = value
        for i in range(30):
            PARAMS['runtrial'] = i + 1
            simulation("teste", PARAMS, get_evol=sim_binary_1pointcrossover)
