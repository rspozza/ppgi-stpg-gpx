
import time
from copy import copy
from random import choices
from typing import Any, Callable, Generator, Iterable, List, Optional, Sequence, Union
from uuid import uuid4

from evol import Evolution, Individual
from evol.conditions import Condition
from evol.exceptions import StopEvolution
from evol.population import BasePopulation
from evol.step import EvolutionStep
from evol.utils import select_arguments


class SteinerIndividual(Individual):

    def __init__(self, chromosome: Any, fitness: Optional[float] = None):
        self.age = 0
        self.last_improvement = 0
        self.chromosome = chromosome
        self._fitness = fitness
        self._cost = fitness
        self.is_normal = False
        self.qtd_partitions = 0
        self.id = f"{str(uuid4())[:6]}"

    @property
    def fitness(self):
        return self._fitness

    @fitness.setter
    def fitness(self, value):
        self._fitness = value
        self.is_normal = True

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost = value
        self._fitness = value
        self.is_normal = False

    @property
    def is_connected(self):
        '''If the graph represented by the chromosome has only one partition,
        It means that it is connected.
        '''
        return self.qtd_partitions == 1

    def evaluate(self, eval_function: Callable[..., float], lazy: bool = False):
        """Evaluate the fitness of the individual.

        :param eval_function: Function that reduces a chromosome to a fitness.
        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        """
        if self._cost is None or not lazy:
            result = eval_function(self.chromosome)

            if isinstance(result, tuple) and len(result) == 2:
                self.cost, self.qtd_partitions = result
            elif isinstance(result, (int, float)):
                self.cost = result
            else:
                raise RuntimeError(f"Problem to understand the evaluation return {result}")


class SelectStep(EvolutionStep):

    def apply(self, population: 'SteinerPopulation') -> 'SteinerPopulation':
        return population.select(**self.kwargs)


class CrossoverStep(EvolutionStep):

    def apply(self, population: 'SteinerPopulation') -> 'SteinerPopulation':
        return population.crossover(**self.kwargs)


class GeneticEvolution(Evolution):

    def __copy__(self) -> 'SteinerEvolution':
        result = GeneticEvolution()
        result.chain = copy(self.chain)
        return result

    def select(self,
               selection_func: Callable,
               lazy: bool = False,
               name: Optional[str] = 'selection',
               **kwargs) -> 'Evolution':

        return self._add_step(SelectStep(name=name, selection_func=selection_func, **kwargs))

    def crossover(self,
                  combiner: Callable,
                  population_size: Optional[int] = None,
                  name: Optional[str] = 'crossover',
                  **kwargs) -> 'Evolution':

        return self._add_step(CrossoverStep(name=name, combiner=combiner, **kwargs))


class GeneticPopulation(BasePopulation):

    """Population of Individuals

    :param chromosomes: Iterable of initial chromosomes of the Population.
    :param eval_function: Function that reduces a chromosome to a fitness.
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :param generation: Generation of the Population. This is incremented after
        each breed call. Defaults to 0.
    :param intended_size: Intended size of the Population. The population will
        be replenished to this size by .breed(). Defaults to the number of
        chromosomes provided.
    :param checkpoint_target: Target for the serializer of the Population. If
        a serializer is provided, this target is ignored. Defaults to None.
    :param serializer: Serializer for the Population. If None, a new
        SimpleSerializer is created. Defaults to None.
    :param concurrent_workers: If > 1, evaluate individuals in {concurrent_workers}
        separate processes. If None, concurrent_workers is set to n_cpus. Defaults to 1.
    """

    def __init__(self,
                 chromosomes: Iterable,
                 eval_function: Callable[..., float],
                 maximize: bool = True,
                 generation: int = 0,
                 intended_size: Optional[int] = None,
                 checkpoint_target: Optional[str] = None,
                 serializer=None,
                 concurrent_workers: Optional[int] = 1):
        super().__init__(chromosomes=[],
                         eval_function=eval_function,
                         checkpoint_target=checkpoint_target,
                         concurrent_workers=concurrent_workers,
                         maximize=maximize,
                         generation=generation,
                         intended_size=0,
                         serializer=serializer)

        self.individuals = [SteinerIndividual(chromosome=chromosome) for chromosome in chromosomes]
        self.intended_size = intended_size or len(self.individuals)
        self.stoppedby = None
        self.runtime = 0.0

    def __copy__(self):
        result = self.__class__(chromosomes=[],
                                eval_function=self.eval_function,
                                maximize=self.maximize,
                                serializer=self.serializer,
                                intended_size=self.intended_size,
                                generation=self.generation,
                                concurrent_workers=1)  # Prevent new pool from being made
        result.individuals = [copy(individual) for individual in self.individuals]
        result.concurrent_workers = self.concurrent_workers
        result.pool = self.pool
        result.documented_best = self.documented_best
        result.id = self.id
        result.stoppedby = self.stoppedby
        return result

    def breed(self,
              parent_picker: Callable[..., Sequence[Individual]],
              combiner: Callable,
              population_size: Optional[int] = None,
              **kwargs) -> 'BasePopulation':
        """Create new individuals by combining existing individuals.

        This increments the generation of the Population.

        :param parent_picker: Function that selects parents from a collection of individuals.
        :param combiner: Function that combines chromosomes into a new
            chromosome. Must be able to handle the number of chromosomes
            that the combiner returns.
        :param population_size: Intended population size after breeding.
            If None, take the previous intended population size.
            Defaults to None.
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        # raise RuntimeWarning("offspring_generator instanciate with a Individual not a SteinerIndividual")
        # if population_size:
        #     self.intended_size = population_size
        # offspring = offspring_generator(parents=self.individuals,
        #                                 parent_picker=select_arguments(parent_picker),
        #                                 combiner=select_arguments(combiner),
        #                                 **kwargs)
        # self.individuals += list(islice(offspring, self.intended_size - len(self.individuals)))
        ####  self.generation += 1 ## generation should be counted here
        return self

    def evolve(self, evolution: 'Evolution', n: int = 1) -> 'BasePopulation':  # noqa: F821
        """Evolve the population according to an Evolution.

        :param evolution: Evolution to follow
        :param n: Times to apply the evolution. Defaults to 1.
        :return: Population
        """
        result = copy(self)
        start = time.perf_counter()
        try:
            for _ in range(n):
                Condition.check(result)
                for step in evolution:
                    result = step.apply(result)
            else :
                result.stoppedby = "IterationLimit"

        except StopEvolution as error :
            result.stoppedby = str(error)

        finally:
            result.runtime = time.perf_counter() - start

        # never put a return statement at finally block
        # altought you deserve everthing bad that to you
        return result

    def _update_documented_best(self):
        """Update the documented best"""
        current_best = self.current_best
        documented_best = self.documented_best
        if (    self.documented_best is None
            or (documented_best.cost > current_best.cost)):
            self.documented_best = copy(current_best)
            self.documented_best.last_improvement = self.generation

    def evaluate(self, lazy: bool = False) -> 'Population':
        """Evaluate the individuals in the population.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known. In
        most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the operations that need it
        (most notably in the survive operation).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :return: self
        """
        if self.pool:
            f = self.eval_function  # We cannot refer to self in the map
            scores = self.pool.map(lambda i: i.fitness if (i.fitness and lazy) else f(i.chromosome), self.individuals)
            for individual, fitness in zip(self.individuals, scores):
                individual.fitness = fitness
        else:
            for individual in self.individuals:
                individual.evaluate(eval_function=self.eval_function, lazy=lazy)
        #### self._update_documented_best()
        return self

    def select(self,
               selection_func : Callable,
               **kwargs) -> 'Population':
        selected  = selection_func(self.individuals, **kwargs)

        self.individuals = selected

        return self

    def crossover(self,
              combiner : Callable,
              parent_picker : Callable,
              population_size: Optional[int] = None,
              **kwargs) -> 'Population':

        if not population_size:
            population_size = self.intended_size

        pick = parent_picker(self.individuals)
        newpopulation = list()

        while len(newpopulation) < population_size:

            parents = [individual.chromosome for individual in next(pick) ]

            combined = combiner(*parents, **kwargs)

            if isinstance(combined, Generator):
                for child in combined:
                    newpopulation.append(SteinerIndividual(chromosome=child))
            else:
                newpopulation.append(SteinerIndividual(chromosome=combined))

        self._update_population(newpopulation)

        return self

    def _update_population(self, new_population : 'SteinerPopulation'):
        self.individuals = new_population
