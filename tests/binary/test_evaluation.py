import unittest
from os import path

from ga4stpg.binary.coder import Coder
from ga4stpg.binary.evaluation import EvaluateBinary
from ga4stpg.graph import ReaderORLibrary
from ga4stpg.graph.algorithms import prim
from ga4stpg.graph.graph import UndirectedGraph as UGraph
from ga4stpg.graph.disjointsets import DisjointSets

class TestEvaluateBinary(unittest.TestCase):

    def setUp(self):
        filename = path.join('datasets', 'ORLibrary', 'steinb11.txt')
        self.stpg  = ReaderORLibrary().parser(filename)

    def test_basicEvaluateBinaryProperties(self):

        evaluator = EvaluateBinary(self.stpg)

        self.assertIsInstance(evaluator, EvaluateBinary)
        self.assertTrue(callable(evaluator))
        self.assertTrue(hasattr(evaluator, 'vertices_from_chromosome'))

        self.assertTrue(callable(evaluator.penality_function))
        self.assertEqual(evaluator.penality_function(1), 0)
        self.assertEqual(evaluator.penality_function(7), 6_000)

    def test_vertices_from_chromossome_all_nodes(self):

        stpg = self.stpg
        graph_vertices = set(self.stpg.graph.vertices)

        evaluator = EvaluateBinary(self.stpg)
        expected_lenght = stpg.nro_nodes - stpg.nro_terminals
        chromosome = '1' * expected_lenght

        evaluator_vertices = evaluator.vertices_from_chromosome(chromosome)

        self.assertEqual(graph_vertices, evaluator_vertices)


    def test_EvaluateMST(self):
        stpg  = self.stpg
        graph = self.stpg.graph

        expected_lenght = stpg.nro_nodes - stpg.nro_terminals
        chromosome = '1' * expected_lenght

        subtree = Coder(stpg).binary2treegraph(chromosome)


        evaluator = EvaluateBinary(stpg)

        evaluator_cost, qtd_partitions = evaluator(chromosome)

        dict_tree, prim_cost = prim(graph,1)


        self.assertIsInstance(subtree, UGraph)
        self.assertIsInstance(dict_tree, dict)
        self.assertIsInstance(qtd_partitions, int)
        self.assertEqual(qtd_partitions, 1)
        self.assertEqual(evaluator_cost, prim_cost)

    def test_EvaluateZeroChromossome(self):
        stpg  = self.stpg
        graph = self.stpg.graph
        nro_terminals = stpg.nro_terminals
        terminals = stpg.terminals

        disset = DisjointSets()
        for v in terminals:
            disset.make_set(v)

        edges_sum = 0
        done = set()
        for t in terminals:
            done.add(t)
            for v in graph.adjacent_to(t):
                if v in terminals and v not in done:
                    disset.union(t, v)
                    edges_sum += graph.weight(t, v)

        qtd_disjoint_sets = len(disset.get_disjoint_sets())

        expected_lenght = stpg.nro_nodes - stpg.nro_terminals
        chromosome = '0' * expected_lenght

        evaluator = EvaluateBinary(stpg)

        evaluator_cost, qtd_partitions = evaluator(chromosome)

        self.assertEqual(evaluator_cost, ((qtd_partitions - 1) * 1_000) + edges_sum)
        self.assertEqual(evaluator_cost, ((qtd_disjoint_sets - 1) * 1_000) + edges_sum)
        self.assertEqual(qtd_partitions, qtd_disjoint_sets)




if __name__ == "__main__" :
    unittest.main()