
import time
from os import path

from base.chromosome import random_binary
from base.combiner import crossover_2points
from base.customevol import SteinerEvolution as Evolution
from base.customevol import SteinerPopulation as Population
from base.mutate import flip_onebit
from base.normalization import normalize
from base.selector import roullete
from graph import Graph
from graph.reader import read_problem
from treetools import Eval
from base.util import display, read_problem


def simulation(STPG, trial=0, output=None):

    population_size = 100
    lenght = STPG.nro_nodes - STPG.nro_terminals

    population = (Population(chromosomes=[random_binary(lenght) for _ in range(population_size)],
                            eval_function=Eval(STPG),
                            maximize=True)
                        .evaluate()
                        .callback(normalize))

    evo = (Evolution()
        .evaluate()
        .callback(normalize)
        .callback(update_best)
        .select(selection_func=roullete)
        .crossover(combiner=crossover_2points)
        .mutate(mutate_function=flip_onebit, probability=0.2)
        .callback(update_generation)
        .callback(display, every=100)
        )

    print("INIT EVOLUTION")
    result = population.evolve(evo, n=1000)

    return result

def test_forloop(STPG, trial=0, output=None):
    print("INIT EVOLUTION")

    population_size = 100
    lenght = STPG.nro_nodes - STPG.nro_terminals

    population = (Population(chromosomes=[random_binary(lenght) for _ in range(population_size)],
                            eval_function=Eval(STPG),
                            maximize=True)
                        .evaluate()
                        .callback(normalize))

    for _ in range(1000):
        population = (
            population
            .select(selection_func=roullete)
            .crossover(combiner=crossover_2points)
            .mutate(mutate_function=flip_onebit, probability=0.2)
            .evaluate()
            .callback(normalize))

    return population

def run_multitrials(filename, max_trial):

    STPG = read_problem("datasets", "ORLibrary", "steinb13.txt")
    for trial in range(max_trial):
        simulation(STPG, trial=trial)

if __name__ == "__main__":
    STPG = read_problem("datasets", "ORLibrary", "steinb13.txt")

    # pop = simulation(STPG)
