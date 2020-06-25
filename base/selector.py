from itertools import cycle, product
from random import choices
from operator import attrgetter
from evol import Population

def random_picker(population):
    while True:
        yield tuple(choices(population, k=2))

def best_vsothers(population):
    bestdocumented = population.documented_best

    if bestdocumented is None:
        yield from random_picker(population)

    container = cycle(population)

    for other in container:
        yield bestdocumented, other

def cartesian_product(population):
    container = product(population, repeat=2)

    for result in container:
        yield result


def roullete(individuals, n_parents=None):
    '''Selection based on fitness value

    :individuals: receive the list of individuals
    :n_parents: how many parents select
    :return: list of individuals
    '''
    if not n_parents:
        n_parents = len(individuals)

    fitnesses = [p.fitness for p in individuals]
    return choices(individuals, weights=fitnesses, k=n_parents)

def tournament(individuals, n_competitors=2, maximize=True, n_parents=None):
    '''Selection based on tournament between n competitors

    :individuals: receive the list of individuals
    :n=2:
    :maximize: type of the problem
    :n_parents: how many parents select
    :return: list of individuals
    '''
    if not n_parents:
        n_parents = len(individuals)

    assert n_competitors < len(individuals) // 4, f"you must set less than {(len(individuals) // 4)} competitors for {len(individuals)} individuals"

    contest = max if maximize else min

    selected = list()
    while len(selected) < n_parents:
        competitors = choices(individuals, k=n_competitors)
        selected.append(contest(competitors, key=attrgetter('fitness')))

    return selected