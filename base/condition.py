
from evol.conditions import Condition
from evol.exceptions import StopEvolution

from graph import Graph
from graph.util import is_steiner_tree
from treetools import Converter

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
            raise StopEvolution("Stagnation")

class BestKnownReached(Condition):

    def __init__(self, global_optimum : int):
        self.global_optimum = global_optimum

    def __call__(self, population : 'Population'):
        if (population.documented_best
           and population.documented_best.cost == self.global_optimum):
           raise StopEvolution("BestKnowReached")


class BestSolutionKnowReached(Condition):

    def __init__(self, global_optimum : int, STPG : "SteinerTreeProblem" ):
        self.global_optimum = global_optimum
        self.STPG = STPG
        self.converter = Converter(STPG)

    def __call__(self, population : 'Population'):
        best_solution = population.documented_best
        if (best_solution is not None and best_solution.cost == self.global_optimum):

            if not isinstance(best_solution.chromosome, Graph) :
                best_solution = self.converter.binary2treegraph(best_solution)

            result, _ = is_steiner_tree(best_solution.chromosome, self.STPG)

            if result :
                raise StopEvolution("BestKnowReached")
