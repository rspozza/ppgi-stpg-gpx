
def normalize(population):

    max_fitness = max(p.fitness for p in population)
    for p in population:
        p.fitness = max_fitness - p.fitness