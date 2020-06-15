from random import sample, choice, random

def crossover_2points(parent_a, parent_b):
    length_a, length_b = len(parent_a), len(parent_b)
    assert length_a == length_b, "chromosomes doesn't have the same length"
    assert length_a > 0, "chromosome must have length greater than 0"
    points = sample(range(0, length_a), k=2)
    points.sort()
    p1, p2 = points

    return (parent_a[:p1] + parent_b[p1:p2] + parent_a[p2:])

def crossover_1point(parent_a, parent_b):
    length_a, length_b = len(parent_a), len(parent_b)
    assert length_a == length_b, "chromosomes doesn't have the same length"
    index = choice(range(0, length_a))
    return (parent_a[:index] + parent_b[index:])

def crossover_Npoints(parent_a, parent_b, n=2):
    length_a, length_b = len(parent_a), len(parent_b)
    assert length_a == length_b, "chromosomes doesn't have the same length"
    points = sample(range(0,length_a), k=n)

    raise NotImplementedError

def crossover_uniform(chromosome_a, chromosome_b, pbcrossover=0.5, **kwargs):

    assert len(chromosome_a) == len(chromosome_b), "chromosome must have the same length"

    # list comprehension
    chromosome = [ a if random() < pbcrossover else b
                        for a, b in zip(chromosome_a, chromosome_b) ]

    # desta forma se o chromosomo receber uma lista de números inteiros ele também vai funcionar
    if isinstance(chromosome_a, str) or isinstance(chromosome_b, str):
        chromosome = ''.join(chromosome)

    return chromosome


