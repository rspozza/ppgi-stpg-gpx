
def normalize(population):

    max_cost = max(p.cost for p in population)
    for p in population:
        p.fitness = max_cost - p.cost