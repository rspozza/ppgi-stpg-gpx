from collections import defaultdict, deque
from operator import attrgetter
from random import choice

from graph import Graph
from graph.disjointsets import DisjointSets

def compose(red : Graph, blue : Graph):
    '''
    Parameters:
    ----------
        red, blue : Graph

    Return:
    -------
        g_union, g_common, g_star : Graph
    '''

    g_union  = Graph()
    g_common = Graph()
    g_star   = Graph()

    for v, u in red.gen_undirect_edges():
        g_union.add_edge(v,u)

        if not blue.has_edge(v,u):
            g_star.add_edge(v,u)

    for v, u in blue.gen_undirect_edges():
        g_union.add_edge(v,u)

        if red.has_edge(v,u):
            w = red.W(v,u)
            g_common.add_edge(v,u,weight=w)
        else:
            g_star.add_edge(v,u)


    return g_union, g_common, g_star

class Component:

    def __init__(self, node):
        self.edges = set()
        self.portal = set()
        self.cost = 0

    def add(self, v, u):
        self.edges.add((v, u))

class PX_FindTestCompare:
    '''
    Class: PX_FindTestCompare
        Find a partition in g_star graph.
        Test if a partition is recombinant.
        Compare each subtree in a partition and chose that with the smallest cost.
    '''
    def __init__(self, stpg):
        self.STPG = stpg

    def _merge(self, child : Graph, component : Component):

        for v, u in component.edges:
            child.add_edge(v,u, weight=self.STPG.graph.W(v,u))

    def __call__(self, red : Graph, blue : Graph):

        visited = set()
        partition_graph = {'red' : Component(), 'blue' : Component() }

        g_union, g_child, g_star = compose(red, blue)

        def belong_both(node):
            return red.has_node(node) and blue.has_node(node)

        def chase(node, red_component, blue_component):

            if node in visited:
                return

            else:
                visited.add(node)

                for v in g_star.adjacent_to(node):
                    if red.has_edge(node, v):
                        red_component.add(node, v)
                        red_component.cost += self.STPG.graph.W(node, v)

                    elif blue.has_edge(node, v):
                        blue_component.add(node, v)
                        blue_component.cost += self.STPG.graph.W(node, v)

                    chase(v, red_component, blue_component)

        for s in g_star.vertices:
            if belong_both(s) and (s not in visited):
                red_one = Component()
                blue_one = Component()

                chase(s, red_one, blue_one)

                if red_one.portal == blue_one.portal:
                    # ambas as partições possuem os mesmos vértices portais
                    if red_one.cost < blue_one.cost:
                        self._merge(g_child, red_one)

                    elif blue_one.cost < red_one.cost:
                        self._merge(g_child, blue_one)

                    # if blue_one.cost == red_one.cost
                    elif len(red_one.edges) < len(blue_one.edges):
                        self._merge(g_child, red_one)

                    # same cost and same number of edges
                    else :
                        self._merge(g_child, blue_one)

                else:
                # the components have different portals vertices
                # add to the graph partition
                    partition_graph['red'].edges.update(red_one.edges)
                    partition_graph['red'].cost += red_one.cost

                    partition_graph['blue'].edges.update(blue_one.edges)
                    partition_graph['blue'].cost += blue_one.cost

        if partition_graph['red'].cost < partition_graph['blue'].cost:
            self._merge(g_child, partition_graph['red'])

        elif partition_graph['blue'].cost < partition_graph['red'].cost:
            self._merge(g_child, partition_graph['blue'])

        elif len(partition_graph['red'].edges) < len(partition_graph['blue'].edges):
            self._merge(g_child, partition_graph['red'])

        else:
            self._merge(g_child, partition_graph['blue'])

        return g_child


if __name__ == "__main__":

    aa = Graph(edges={
        'A' : {'B' : 1, 'C' : 1},
        'B' : {'A' : 1, 'D' : 1, 'E' : 1},
        'D' : {'B' : 1},
        'C' : {'A' : 1},
        'E' : {'B' : 1, 'G' : 1},
        'G' : {'E' : 1, 'H' : 1},
        'H' : {'G' : 1}
    })

    bb = Graph(edges={
        'A' : {'B' : 1, 'C' : 1},
        'B' : {'A' : 1, 'D' : 1},
        'D' : {'B' : 1},
        'C' : {'A' : 1, 'F' : 1},
        'F' : {'C' : 1, 'G' : 1},
        'G' : {'F' : 1, 'H' : 1},
        'H' : {'G' : 1}
    })

    g_union, g_common, g_star = compose(aa, bb)

    first, second, previous = connected(g_union, aa, bb, 'A')
