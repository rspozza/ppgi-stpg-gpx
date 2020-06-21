import random
from itertools import compress, filterfalse
from evol import Individual

from base.customevol import SteinerIndividual
from graph import Graph, SteinerTreeProblem
from graph.disjointsets import DisjointSets
from graph.priorityqueue import PriorityQueue

def vertices_from_binary_chromosome(chromosome, terminals, nro_vertices):

    non_terminals = (v for v in range(1, nro_vertices+1) if v not in terminals)

    vertices = set(v for v, g in zip(non_terminals, chromosome) if int(g)).union(terminals)

    return vertices


def evaluate_binary(chromosome, STPG : SteinerTreeProblem, penality):

    GRAPH = STPG.graph
    terminals = STPG.terminals
    nro_vertices = STPG.nro_nodes

    ## identifica todos os vértices da solução candidata (terminais e não terminais)
    vertices = vertices_from_binary_chromosome(chromosome, terminals, nro_vertices)

    # instânciando variáveis e funções auxiliares
    queue = PriorityQueue()
    dones = set()

    # adiciona uma aresta se os vértices extremos da aresta
    # estão contidos no conjunto vertices
    # mantém essas arestas em uma fila de prioridades para
    # formar uma MST baseado no algoritmo de Kruskal
    # (o trabalho de Kapsalis utilizava o algoritmo de Prim)
    for v in vertices:
        dones.add(v)
        for u in GRAPH.adjacent_to(v):
            if (u in vertices) and (u not in dones):
                weight = GRAPH.weight(v,u)
                queue.push(weight, (v, u, weight))

    ## Monta a MST baseado no algoritmo de Kruskal
    DS = DisjointSets()
    for v in vertices:
        DS.make_set(v)

    total_cost = 0
    while queue:
        v, u, weight = queue.pop()
        if DS.find(v) != DS.find(u):
            total_cost  += weight
            DS.union(v, u)
        # Repare que não construimos a MST mas apenas
        # definimos os conjuntos disjuntos.

    # a quantidade de partições se refere a
    # quantidade de parents distintos temos no conjunto disjunto.
    qtd_partition = len(DS.get_disjoint_sets())

    total_cost += penality(qtd_partition)

    return total_cost, qtd_partition


def evaluate_treegraph(chromosome, STPG : SteinerTreeProblem, penality):

        GRAPH = STPG.graph

        total_cost = 0
        qtd_partition = 0
        DS = DisjointSets()

        for v, u in chromosome.gen_undirect_edges():
            if v not in DS:
                DS.make_set(v)
            if u not in DS:
                DS.make_set(u)
            if DS.find(v) == DS.find(u):
                print("FOI IDENTIFICADO UM CICLO EM UMA DAS SOLUÇÕES")
            DS.union(v,u)
            total_cost +=  GRAPH.weight(v, u)

        qtd_partition = len(DS.get_disjoint_sets())

        total_cost += penality(qtd_partition)

        return total_cost, qtd_partition


class Eval:

    def __init__(self, STPG : SteinerTreeProblem):
        self.STPG = STPG

    def penality(self, k):
        return (k-1) * 100

    def __call__(self, chromosome, **kwargs):
        return self.eval(chromosome, **kwargs)

    def eval(self, chromosome, **kwargs):
        if isinstance(chromosome, Graph) :
            return evaluate_treegraph(chromosome, self.STPG, self.penality)
        elif isinstance(chromosome, (str, list, tuple)):
            return evaluate_binary(chromosome, self.STPG, self.penality)
        else:
            raise TypeError(f"Chromosome type could not be handled {type(chromosome)}")


class Converter:

    def __init__(self, STPG : SteinerTreeProblem):
        self.STPG = STPG

    def treegraph2binary(self, individual : Individual):
        '''Converts from TreeChromosome to a BinaryChromosome'''

        subgraph = individual.chromosome
        terminals = set(self.STPG.terminals)
        nro_vertices = self.STPG.nro_nodes

        genes = ['0'] * nro_vertices # all vertices in the instance problem

        # vertices in the subgraph (partial solution)
        # include terminals and non-terminals
        for v in subgraph.vertices:
            genes[v-1] = '1'

        # choosing only the non_terminals positions
        genes = (gene for node, gene in enumerate(genes, start=1) if node not in terminals)

        return SteinerIndividual(''.join(genes))

    def binary2treegraph(self, individual : Individual):
        '''Converts from BinaryChromosome to TreeChromosome'''

        GRAPH = self.STPG.graph
        terminals = self.STPG.terminals
        nro_vertices = self.STPG.nro_nodes
        chromosome = individual.chromosome

        queue = PriorityQueue()
        disjointset = DisjointSets()
        subgraph = Graph()
        dones = set()

        # todos os vértices esperados na solução parcial
        vertices = vertices_from_binary_chromosome(chromosome, terminals, nro_vertices)

        # adiciona uma aresta se os vértices extremos da aresta
        # estão contidos no conjunto vertices
        # mantém essas arestas em uma fila de prioridades para
        # formar uma MST baseado no algoritmo de Kruskal
        for v in vertices:
            dones.add(v)
            disjointset.make_set(v) # para construir a MST
            subgraph.add_node(v) # garantir a inserção de um vértice isolado
            for u in GRAPH.adjacent_to(v):
                if (u in vertices) and (u not in dones):
                    weight = GRAPH.weight(v, u)
                    queue.push(weight, (v, u, weight))

        while queue:
            v, u, weight = queue.pop()
            if disjointset.find(v) != disjointset.find(u):
                subgraph.add_edge(v, u, weight=weight)
                disjointset.union(v, u)

        return SteinerIndividual(subgraph)
