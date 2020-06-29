
from evol.conditions import Condition
from evol.exceptions import StopEvolution

class IterationLimit(Condition):

    def __init__(self, limit : int):
        super().__init__(None)
        self.limit = limit

    def __call__(self, population : 'Population'):
        if population.generation >= self.limit:
            raise StopEvolution("max_generation_reached")


class Stagnation(Condition):

    def __init__(self, interval : int):
        self.interval = interval

    def __call__(self, population : 'Population'):
        generation = population.generation
        last_time_improvement = population.documented_best.last_improvement

        if (generation - last_time_improvement) > self.interval:
            raise StopEvolution("stagnation")

class BestKnownReached(Condition):

    def __init__(self, global_optimum : int):
        self.global_optimum = global_optimum

    def __call__(self, population : 'Population'):
        if population.documented_best \
           and population.documented_best.fitness == self.global_optimum:
           raise StopEvolution("BestKnowReached")
