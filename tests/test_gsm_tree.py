import unittest
import inspect
import networkx as nx

from inventory import gsm_tree







class TestRelabelNodes(unittest.TestCase):
	def test_figure_6_12(self):
		"""Test that relabel_nodes()  correctly relabels network
		in Figure 6.12.
		"""

		# Network from Figure 6.12.
		G = nx.DiGraph()
		G.add_nodes_from(range(1, 8))
		G.add_edge(1, 2)
		G.add_edge(1, 3)
		G.add_edge(3, 5)
		G.add_edge(4, 5)
		G.add_edge(5, 6)
		G.add_edge(5, 7)
		new_G, new_labels = gsm_tree.relabel_nodes(G, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = nx.DiGraph()
		correct_G.add_nodes_from(range(1, 8))
		correct_G.add_edge(2, 1)
		correct_G.add_edge(2, 3)
		correct_G.add_edge(3, 6)
		correct_G.add_edge(4, 6)
		correct_G.add_edge(6, 5)
		correct_G.add_edge(6, 7)
		correct_labels = {1: 2, 2: 1, 3: 3, 4: 4, 5: 6, 6: 5, 7: 7}

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))
		self.assertDictEqual(new_labels, correct_labels)


class TestFindLargerAdjacentNodes(unittest.TestCase):
	def test_figure_6_12(self):
		"""Test that find_larger_adjacent_nodes() works for relabeled network
		in Figure 6.12.
		"""

		# Network from Figure 6.12.
		G = nx.DiGraph()
		G.add_nodes_from(range(1, 8))
		G.add_edge(1, 2)
		G.add_edge(1, 3)
		G.add_edge(3, 5)
		G.add_edge(4, 5)
		G.add_edge(5, 6)
		G.add_edge(5, 7)
		new_G, _ = gsm_tree.relabel_nodes(G, start_index=1)
		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries
		correct_larger_adjacent = {1: 2, 2: 3, 3: 6, 4: 6, 5: 6, 6: 7}
		correct_downstream = {1: False, 2: True, 3: True, 4: True, 5: False, 6: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)
