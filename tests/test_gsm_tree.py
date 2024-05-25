import unittest
import math
import copy

from stockpyl.demand_source import DemandSource
import stockpyl.helpers as helpers
import stockpyl.gsm_tree as gsm_tree
import stockpyl.gsm_helpers as gsm_helpers
from stockpyl.instances import load_instance
from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import SupplyChainNode
from tests.instances_gsm_tree import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_tree   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestRelabelNodes(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRelabelNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRelabelNodes', 'tear_down_class()')

	def test_figure_6_12(self):
		"""Test that relabel_nodes() correctly relabels network in Figure 6.12.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_12()')

		instance = load_instance("figure_6_12")

		new_G = gsm_tree.relabel_nodes(instance, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = SupplyChainNetwork()
		correct_G.add_node(SupplyChainNode(2, name=None, network=correct_G, original_label=1, larger_adjacent_node=3, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(1, name=None, network=correct_G, original_label=2, larger_adjacent_node=2, larger_adjacent_node_is_downstream=False))
		correct_G.add_node(SupplyChainNode(3, name=None, network=correct_G, original_label=3, larger_adjacent_node=6, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(4, name=None, network=correct_G, original_label=4, larger_adjacent_node=6, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(6, name=None, network=correct_G, original_label=5, larger_adjacent_node=7, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(5, name=None, network=correct_G, original_label=6, larger_adjacent_node=6, larger_adjacent_node_is_downstream=False))
		correct_G.add_node(SupplyChainNode(7, name=None, network=correct_G, original_label=7, larger_adjacent_node=None, larger_adjacent_node_is_downstream=None))
		correct_G.add_edges_from_list([(2, 1), (2, 3), (3, 6), (4, 6), (6, 5), (6, 7)])

		for n in new_G.nodes:
			self.assertSetEqual(set(n.predecessor_indices()), set(correct_G.nodes_by_index[n.index].predecessor_indices()))
			self.assertSetEqual(set(n.successor_indices()), set(correct_G.nodes_by_index[n.index].successor_indices()))
			self.assertEqual(n.original_label, correct_G.nodes_by_index[n.index].original_label)
			self.assertEqual(n.larger_adjacent_node, correct_G.nodes_by_index[n.index].larger_adjacent_node)
			self.assertEqual(n.larger_adjacent_node_is_downstream, correct_G.nodes_by_index[n.index].larger_adjacent_node_is_downstream)

	def test_figure_6_12_already_correct(self):
		"""Test that relabel_nodes() correctly relabels network
		in Figure 6.12 even though they are already correct, with force_relabel=
		True.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_12_already_correct()')

		orig_G = load_instance("figure_6_12")
		orig_G.reindex_nodes({1: 3, 2: 2, 3: 4, 4: 5, 5: 7, 6: 6, 7: 8})

		new_G = gsm_tree.relabel_nodes(orig_G, force_relabel=True, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = SupplyChainNetwork()
		correct_G.add_node(SupplyChainNode(2, name=None, network=correct_G, original_label=3, larger_adjacent_node=3, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(1, name=None, network=correct_G, original_label=2, larger_adjacent_node=2, larger_adjacent_node_is_downstream=False))
		correct_G.add_node(SupplyChainNode(3, name=None, network=correct_G, original_label=4, larger_adjacent_node=6, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(4, name=None, network=correct_G, original_label=5, larger_adjacent_node=6, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(6, name=None, network=correct_G, original_label=7, larger_adjacent_node=7, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(5, name=None, network=correct_G, original_label=6, larger_adjacent_node=6, larger_adjacent_node_is_downstream=False))
		correct_G.add_node(SupplyChainNode(7, name=None, network=correct_G, original_label=8, larger_adjacent_node=None, larger_adjacent_node_is_downstream=None))
		correct_G.add_edges_from_list([(2, 1), (2, 3), (3, 6), (4, 6), (6, 5), (6, 7)])

		for n in new_G.nodes:
			self.assertSetEqual(set(n.predecessor_indices()), set(correct_G.nodes_by_index[n.index].predecessor_indices()))
			self.assertSetEqual(set(n.successor_indices()), set(correct_G.nodes_by_index[n.index].successor_indices()))
			self.assertEqual(n.original_label, correct_G.nodes_by_index[n.index].original_label)
			self.assertEqual(n.larger_adjacent_node, correct_G.nodes_by_index[n.index].larger_adjacent_node)
			self.assertEqual(n.larger_adjacent_node_is_downstream, correct_G.nodes_by_index[n.index].larger_adjacent_node_is_downstream)

	def test_example_6_5(self):
		"""Test that relabel_nodes() correctly relabels network in Example 6.13.
		"""

		print_status('TestRelabelNodes', 'test_example_6_5()')

		new_G = gsm_tree.relabel_nodes(load_instance("example_6_5"), start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = SupplyChainNetwork()
		correct_G.add_node(SupplyChainNode(1, name=None, network=correct_G, original_label=1, larger_adjacent_node=3, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(2, name=None, network=correct_G, original_label=2, larger_adjacent_node=3, larger_adjacent_node_is_downstream=False))
		correct_G.add_node(SupplyChainNode(3, name=None, network=correct_G, original_label=3, larger_adjacent_node=4, larger_adjacent_node_is_downstream=True))
		correct_G.add_node(SupplyChainNode(4, name=None, network=correct_G, original_label=4, larger_adjacent_node=None, larger_adjacent_node_is_downstream=None))
		correct_G.add_edges_from_list([(1, 3), (3, 2), (3, 4)])

		for n in new_G.nodes:
			self.assertSetEqual(set(n.predecessor_indices()), set(correct_G.nodes_by_index[n.index].predecessor_indices()))
			self.assertSetEqual(set(n.successor_indices()), set(correct_G.nodes_by_index[n.index].successor_indices()))
			self.assertEqual(n.original_label, correct_G.nodes_by_index[n.index].original_label)
			self.assertEqual(n.larger_adjacent_node, correct_G.nodes_by_index[n.index].larger_adjacent_node)
			self.assertEqual(n.larger_adjacent_node_is_downstream, correct_G.nodes_by_index[n.index].larger_adjacent_node_is_downstream)

	def test_figure_6_14(self):
		"""Test that relabel_nodes() correctly relabels network in Figure 6.14.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_14()')

		orig_G = load_instance("figure_6_14")
		new_G = gsm_tree.relabel_nodes(orig_G, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = copy.deepcopy(new_G)
		correct_labels = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}
		correct_larger_adjacent = {1: 2, 2: 3, 3: 5, 4: 5, 5: 6, 6: 10, 7: 10, 8: 10, 9: 10, 10: None}
		correct_downstream = {k: True for k in correct_G.node_indices}
		correct_downstream[10] = None
		correct_G.reindex_nodes(correct_labels)
		for n in orig_G.nodes:
			correct_node = correct_G.nodes_by_index[correct_labels[n.index]]
			correct_node.original_label = n.index
			correct_node.larger_adjacent_node = correct_larger_adjacent[correct_node.index]
			correct_node.larger_adjacent_node_is_downstream = correct_downstream[correct_node.index]

		for n in new_G.nodes:
			self.assertSetEqual(set(n.predecessor_indices()), set(correct_G.nodes_by_index[n.index].predecessor_indices()))
			self.assertSetEqual(set(n.successor_indices()), set(correct_G.nodes_by_index[n.index].successor_indices()))
			self.assertEqual(n.original_label, correct_G.nodes_by_index[n.index].original_label)
			self.assertEqual(n.larger_adjacent_node, correct_G.nodes_by_index[n.index].larger_adjacent_node)
			self.assertEqual(n.larger_adjacent_node_is_downstream, correct_G.nodes_by_index[n.index].larger_adjacent_node_is_downstream)

	def test_figure_6_14_alt_indices(self):
		"""Test that relabel_nodes() correctly relabels network in Figure 6.14 when
		the indices are different so that the network requires reindexing. (The original
		network does not.)
		"""

		print_status('TestRelabelNodes', 'test_figure_6_14()')

		orig_G = load_instance("figure_6_14")
		orig_G.reindex_nodes({1: 4, 2: 3, 3: 9, 4: 1, 5: 10, 6: 8, 7: 7, 8: 2, 9: 5, 10: 6})

		new_G = gsm_tree.relabel_nodes(orig_G, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = copy.deepcopy(orig_G)
		correct_labels = {4: 1, 3: 2, 9: 3, 1: 4, 10: 5, 8: 6, 7: 7, 2: 8, 5: 9, 6: 10}
		correct_larger_adjacent = {1: 2, 2: 3, 3: 5, 4: 5, 5: 6, 6: 10, 7: 10, 8: 10, 9: 10, 10: None}
		correct_downstream = {k: True for k in correct_G.node_indices}
		correct_downstream[10] = None
		correct_G.reindex_nodes(correct_labels)
		for n in orig_G.nodes:
			correct_node = correct_G.nodes_by_index[correct_labels[n.index]]
			correct_node.original_label = n.index
			correct_node.larger_adjacent_node = correct_larger_adjacent[correct_node.index]
			correct_node.larger_adjacent_node_is_downstream = correct_downstream[correct_node.index]

		for n in new_G.nodes:
			self.assertSetEqual(set(n.predecessor_indices()), set(correct_G.nodes_by_index[n.index].predecessor_indices()))
			self.assertSetEqual(set(n.successor_indices()), set(correct_G.nodes_by_index[n.index].successor_indices()))
			self.assertEqual(n.original_label, correct_G.nodes_by_index[n.index].original_label)
			self.assertEqual(n.larger_adjacent_node, correct_G.nodes_by_index[n.index].larger_adjacent_node)
			self.assertEqual(n.larger_adjacent_node_is_downstream, correct_G.nodes_by_index[n.index].larger_adjacent_node_is_downstream)

	def test_problem_6_9(self):
		"""Test that relabel_nodes() correctly relabels network in Problem 6.9.
		"""

		print_status('TestRelabelNodes', 'test_problem_6_9()')

		orig_G = load_instance("problem_6_9")
		new_G = gsm_tree.relabel_nodes(orig_G, start_index=0)

		# Build correct relabeled network, and list of correct labels.
		correct_G = copy.deepcopy(orig_G)
		correct_labels = {1: 0, 2: 1, 3: 3, 4: 2, 5: 4, 6: 5}
		correct_larger_adjacent = {0: 3, 1: 3, 3: 4, 4: 5, 2: 3, 5: None}
		correct_downstream = {0: False, 1: False, 2: True, 3: True, 4: False, 5: None}
		correct_G.reindex_nodes(correct_labels)
		for n in orig_G.nodes:
			correct_node = correct_G.nodes_by_index[correct_labels[n.index]]
			correct_node.original_label = n.index
			correct_node.larger_adjacent_node = correct_larger_adjacent[correct_node.index]
			correct_node.larger_adjacent_node_is_downstream = correct_downstream[correct_node.index]

	def test_bad_index(self):
		"""Test that reindex_nodes() correctly raises an exception if an index is not a positive integer.
		"""

		print_status('TestRelabelNodes', 'test_bad_index()')

		orig_G = load_instance("figure_6_14")

		with self.assertRaises(ValueError):
			orig_G.reindex_nodes({1: 4.5, 2: 3, 3: 9, 4: 1, 5: 10, 6: 8, 7: 7, 8: 2, 9: 5, 10: 6})
			orig_G.reindex_nodes({1: -4, 2: 3, 3: 9, 4: 1, 5: 10, 6: 8, 7: 7, 8: 2, 9: 5, 10: 6})



class TestIsCorrectlyLabeled(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsCorrectlyLabeled', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsCorrectlyLabeled', 'tear_down_class()')

	def test_correct(self):
		"""Test that is_correctly_labeled() works for if network is labeled
		correctly.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_correct()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_12"), start_index=1)

		is_correct = gsm_tree.is_correctly_labeled(new_G)

		self.assertEqual(is_correct, True)

	def test_nonconsecutive(self):
		"""Test that is_correctly_labeled() works for if network labels are
		non-consecutive integers.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_nonconsecutive()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_12"), start_index=1)
		new_G.reindex_nodes({1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 7, 7: 8})

		is_correct = gsm_tree.is_correctly_labeled(new_G)

		self.assertEqual(is_correct, False)

	def test_more_than_1_adj(self):
		"""Test that is_correctly_labeled() works for if some node has more than
		one adjacent node with a greater index.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_more_than_1_adj()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_12"), start_index=1)
		new_G.reindex_nodes({1: 0, 2: 1, 3: 2, 4: 3, 5: 5, 6: 4, 7: 6})

		is_correct = gsm_tree.is_correctly_labeled(new_G)

		self.assertEqual(is_correct, False)

	def test_no_adj(self):
		"""Test that is_correctly_labeled() works for if some node has no
		adjacent node with a greater index.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_no_adj()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_12"), start_index=1)
		new_G.reindex_nodes({1: 1, 2: 0, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6})

		is_correct = gsm_tree.is_correctly_labeled(new_G)

		self.assertEqual(is_correct, False)

class TestFindLargerAdjacentNodes(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestFindLargerAdjacentNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestFindLargerAdjacentNodes', 'tear_down_class()')

	def test_figure_6_12(self):
		"""Test that _find_larger_adjacent_nodes() works for relabeled network
		in Figure 6.12.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_figure_6_12()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_12"), start_index=1)
		larger_adjacent, downstream = gsm_tree._find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 2, 2: 3, 3: 6, 4: 6, 5: 6, 6: 7}
		correct_downstream = {1: False, 2: True, 3: True, 4: True, 5: False, 6: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_example_6_5(self):
		"""Test that _find_larger_adjacent_nodes() works for network in Example 6.5.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_example_6_5()')

		larger_adjacent, downstream = gsm_tree._find_larger_adjacent_nodes(load_instance("example_6_5"))

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 3, 2: 3, 3: 4}
		correct_downstream = {1: True, 2: False, 3: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_figure_6_14(self):
		"""Test that _find_larger_adjacent_nodes() works for network in Figure 6.14.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_14"), start_index=1)
		larger_adjacent, downstream = gsm_tree._find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 2, 2: 3, 3: 5, 4: 5, 5: 6, 6: 10, 7: 10, 8: 10, 9: 10}
		correct_downstream = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_problem_6_9(self):
		"""Test that _find_larger_adjacent_nodes() works for network in Problem 6.9.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(load_instance("problem_6_9"))
		larger_adjacent, downstream = gsm_tree._find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {0: 3, 1: 3, 2: 3, 3: 4, 4: 5}
		correct_downstream = {0: False, 1: False, 2: True, 3: False, 4: False}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)


class TestLongestPaths(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLongestPaths', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLongestPaths', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that _largest_paths() works for network in Example 6.5.
		"""

		print_status('TestLongestPaths', 'test_example_6_5()')

		tree = load_instance("example_6_5")
		longest_lengths = gsm_tree._longest_paths(tree)

		# Build correct dictionary.
		correct_longest_lengths = {1: 3, 2: 5, 3: 4, 4: 5}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)

	def test_figure_6_14(self):
		"""Test that _largest_paths() works for network in Figure 6.14.
		"""

		print_status('TestLongestPaths', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_14"), start_index=1)
		longest_lengths = gsm_tree._longest_paths(new_G)

		# Build correct dictionary.
		correct_longest_lengths = {1: 2, 2: 5, 3: 7, 4: 4, 5: 9, 6: 12, 7: 6, 8: 4, 9: 3, 10: 14}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)

	def test_problem_6_9(self):
		"""Test that _largest_paths() works for network in Problem 6.9.
		"""

		print_status('TestLongestPaths', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(load_instance("problem_6_9"))
		longest_lengths = gsm_tree._longest_paths(new_G)

		# Build correct dictionary.
		correct_longest_lengths = {0: 38, 1: 38, 2: 3, 3: 31, 4: 10, 5: 2}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)


class TestNetDemand(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNetDemand', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNetDemand', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that _net_demand() works for network in Example 6.5.
		"""

		print_status('TestNetDemand', 'test_example_6_5()')

		instance = load_instance("example_6_5")
		net_means, net_standard_deviations = gsm_tree._net_demand(instance)

		# Build correct dictionaries.
		correct_net_means = {k.index: 0 for k in instance.nodes}
		correct_net_standard_deviations = {1: math.sqrt(2), 2: 1, 3: math.sqrt(2),
										   4: 1}

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)

	def test_figure_6_14(self):
		"""Test that _net_demand() works for network in Figure 6.14.
		"""

		print_status('TestNetDemand', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_14"), start_index=1)
		net_means, net_standard_deviations = gsm_tree._net_demand(new_G)

		# Build correct dictionaries.
		correct_net_means = {k.index: 0 for k in new_G.nodes}
		correct_net_standard_deviations = {k.index: 10 for k in new_G.nodes}

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)

	def test_problem_6_9(self):
		"""Test that _net_demand() works for network in Problem 6.9.
		"""

		print_status('TestNetDemand', 'test_problem_6_9()')

		instance = load_instance("problem_6_9")
		new_G = gsm_tree.relabel_nodes(instance)
		net_means, net_standard_deviations = gsm_tree._net_demand(new_G)

		# Build correct dictionaries.
		correct_net_means = {0: 22.0, 1: 15.3}
		correct_net_standard_deviations = {0: 4.1, 1: 6.2}
		for k in range(2, 6):
			correct_net_means[k] = 22.0 + 15.3
			correct_net_standard_deviations[k] = math.sqrt(4.1**2 + 6.2**2)

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)


class TestConnectedSubgraphNodes(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestConnectedSubgraphNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestConnectedSubgraphNodes', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that _connected_subgraph_nodes() works for network in Example 6.5.
		"""

		print_status('TestConnectedSubgraphNodes', 'test_example_6_5()')

		connected_nodes = gsm_tree._connected_subgraph_nodes(load_instance("example_6_5"))

		# Build correct dictionaries.
		correct_connected_nodes = {1: {1}, 2: {2}, 3: {1, 2, 3}, 4: {1, 2, 3, 4}}

		self.assertDictEqual(connected_nodes, correct_connected_nodes)

	def test_figure_6_14(self):
		"""Test that _connected_subgraph_nodes() works for network in Figure 6.14.
		"""

		print_status('TestConnectedSubgraphNodes', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(load_instance("figure_6_14"), start_index=1)
		connected_nodes = gsm_tree._connected_subgraph_nodes(new_G)

		# Build correct dictionaries.
		correct_connected_nodes = {1: {1}, 2: {1, 2}, 3: {1, 2, 3}, 4: {4},
								   5: {1, 2, 3, 4, 5}, 6: {1, 2, 3, 4, 5, 6},
								   7: {7}, 8: {8}, 9: {9}, 10: set(range(1, 11))}

		self.assertDictEqual(connected_nodes, correct_connected_nodes)

	def test_problem_6_9(self):
		"""Test that _connected_subgraph_nodes() works for network in Problem 6.9.
		"""

		print_status('TestConnectedSubgraphNodes', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(load_instance("problem_6_9"))
		connected_nodes = gsm_tree._connected_subgraph_nodes(new_G)

		# Build correct dictionaries.
		correct_connected_nodes = {0: {0}, 1: {1}, 2: {2}, 3: {0, 1, 2, 3},
								   4: {0, 1, 2, 3, 4}, 5: {0, 1, 2, 3, 4, 5}}

		self.assertDictEqual(connected_nodes, correct_connected_nodes)


class TestGSMToSSM(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGSMToSSM', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGSMToSSM', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that GSM_to_SSM() works for network in Example 6.5.
		"""

		print_status('TestGSMToSSM', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		SSM_tree = gsm_tree.gsm_to_ssm(tree)

		correct_SSM_tree = SupplyChainNetwork()
		correct_SSM_tree.add_node(SupplyChainNode(1, shipment_lead_time=3, echelon_holding_cost=1))
		correct_SSM_tree.add_node(SupplyChainNode(2, shipment_lead_time=1, echelon_holding_cost=1, demand_source=DemandSource(type='N', mean=0, standard_deviation=1)))
		correct_SSM_tree.add_node(SupplyChainNode(3, shipment_lead_time=1, echelon_holding_cost=1))
		correct_SSM_tree.add_node(SupplyChainNode(4, shipment_lead_time=1, echelon_holding_cost=1, demand_source=DemandSource(type='N', mean=0, standard_deviation=1)))
		correct_SSM_tree.add_edge(1, 3)
		correct_SSM_tree.add_edge(3, 2)
		correct_SSM_tree.add_edge(3, 4)

		self.assertTrue(SSM_tree.deep_equal_to(correct_SSM_tree))

	def test_figure_6_14(self):
		"""Test that GSM_to_SSM() works for network in Figure 6.14.
		"""

		print_status('TestGSMToSSM', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		SSM_tree = gsm_tree.gsm_to_ssm(tree)

		correct_SSM_tree = SupplyChainNetwork()
		correct_SSM_tree.add_node(SupplyChainNode(1, 'Raw_Material', correct_SSM_tree, shipment_lead_time=2, echelon_holding_cost=0.01))
		correct_SSM_tree.add_node(SupplyChainNode(2, 'Process_Wafers', correct_SSM_tree, shipment_lead_time=3, echelon_holding_cost=0.02))
		correct_SSM_tree.add_node(SupplyChainNode(3, 'Package_Test_Wafers', correct_SSM_tree, shipment_lead_time=2, echelon_holding_cost=0.01))
		correct_SSM_tree.add_node(SupplyChainNode(4, 'Imager_Base', correct_SSM_tree, shipment_lead_time=4, echelon_holding_cost=0.06))
		correct_SSM_tree.add_node(SupplyChainNode(5, 'Imager_Assembly', correct_SSM_tree, shipment_lead_time=2, echelon_holding_cost=0.02))
		correct_SSM_tree.add_node(SupplyChainNode(6, 'Ship_to_Final_Assembly', correct_SSM_tree, shipment_lead_time=3, echelon_holding_cost=0.01))
		correct_SSM_tree.add_node(SupplyChainNode(7, 'Camera', correct_SSM_tree, shipment_lead_time=6, echelon_holding_cost=0.20))
		correct_SSM_tree.add_node(SupplyChainNode(8, 'Circuit_Board', correct_SSM_tree, shipment_lead_time=4, echelon_holding_cost=0.08))
		correct_SSM_tree.add_node(SupplyChainNode(9, 'Other_Parts', correct_SSM_tree, shipment_lead_time=3, echelon_holding_cost=0.04))
		correct_SSM_tree.add_node(SupplyChainNode(10, 'Build_Test_Pack', correct_SSM_tree, shipment_lead_time=2, echelon_holding_cost=0.05, \
			demand_source=DemandSource(type='N', mean=0, standard_deviation=10)))
		correct_SSM_tree.add_edges_from_list([(1, 2), (2, 3), (3, 5), (4, 5), (5, 6), (7, 10), (6, 10), (8, 10), (9, 10)])

		self.assertTrue(SSM_tree.deep_equal_to(correct_SSM_tree))

	def test_problem_6_9(self):
		"""Test that GSM_to_SSM() works for network in Problem 6.9.
		"""

		print_status('TestGSMToSSM', 'test_problem_6_9()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_9"))

		SSM_tree = gsm_tree.gsm_to_ssm(tree)

		correct_SSM_tree = SupplyChainNetwork()
		correct_SSM_tree.add_node(SupplyChainNode(1, shipment_lead_time=7, echelon_holding_cost=130 * 0.2 / 365, demand_source=DemandSource(type='N', mean=22.0, standard_deviation=4.1)))
		correct_SSM_tree.add_node(SupplyChainNode(2, shipment_lead_time=7, echelon_holding_cost=50 * 0.2 / 365, demand_source=DemandSource(type='N', mean=15.3, standard_deviation=6.2)))
		correct_SSM_tree.add_node(SupplyChainNode(3, shipment_lead_time=21, echelon_holding_cost=65 * 0.2 / 365))
		correct_SSM_tree.add_node(SupplyChainNode(4, shipment_lead_time=3, echelon_holding_cost=5 * 0.2 / 365))
		correct_SSM_tree.add_node(SupplyChainNode(5, shipment_lead_time=8, echelon_holding_cost=12.5 * 0.2 / 365))
		correct_SSM_tree.add_node(SupplyChainNode(6, shipment_lead_time=2, echelon_holding_cost=7.5 * 0.2 / 365))
		correct_SSM_tree.add_edges_from_list([(6, 5), (5, 3), (4, 3), (3, 1), (3, 2)])

		self.assertTrue(SSM_tree.deep_equal_to(correct_SSM_tree))


class TestPreprocessTree(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPreprocessTree', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPreprocessTree', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that preprocess_tree() works for network in Example 6.5.
		"""

		print_status('TestPreprocessTree', 'test_example_6_5()')

		tree = load_instance("example_6_5")
		new_tree = gsm_tree.preprocess_tree(tree)

		# Build correct tree.
		correct_tree = SupplyChainNetwork()
		correct_tree.max_max_replenishment_time = 5
		node1 = SupplyChainNode(1, network=correct_tree, 
			processing_time=2,
			external_inbound_cst=1,
			external_outbound_cst=gsm_tree.BIG_INT,
			local_holding_cost=1,
			supply_type='U',
			demand_bound_constant=1,
#			original_label=1,
			net_demand_mean=0,
			net_demand_standard_deviation=math.sqrt(2),
#			larger_adjacent_node=3,
#			larger_adjacent_node_is_downstream=True,
			max_replenishment_time=3
		)
		correct_tree.add_node(node1)
		node3 = SupplyChainNode(3, network=correct_tree,
			processing_time=1,
			external_inbound_cst=0,
			external_outbound_cst=gsm_tree.BIG_INT,
			local_holding_cost=2,
			demand_bound_constant=1,
#			original_label=3,
			net_demand_mean=0,
			net_demand_standard_deviation=math.sqrt(2),
#			larger_adjacent_node=4,
#			larger_adjacent_node_is_downstream=True,
			max_replenishment_time=4
		)
		correct_tree.add_successor(node1, node3)
		node2 = SupplyChainNode(2, network=correct_tree,
			processing_time=1,
			external_inbound_cst=0,
			external_outbound_cst=0,
			local_holding_cost=3,
			demand_source=DemandSource(type='N', mean=0, standard_deviation=1),
			demand_bound_constant=1,
#			original_label=2,
			net_demand_mean=0,
			net_demand_standard_deviation=1,
#			larger_adjacent_node=3,
#			larger_adjacent_node_is_downstream=False,
			max_replenishment_time=5
		)
		correct_tree.add_successor(node3, node2)
		node4 = SupplyChainNode(4, network=correct_tree, 
			processing_time=1,
			external_inbound_cst=0,
			external_outbound_cst=1,
			local_holding_cost=3,
			demand_source=DemandSource(type='N', mean=0, standard_deviation=1),
			demand_bound_constant=1,
#			original_label=4,
			net_demand_mean=0,
			net_demand_standard_deviation=1,
#			larger_adjacent_node=4,
#			larger_adjacent_node_is_downstream=True,
			max_replenishment_time=5
		)
		correct_tree.add_successor(node3, node4)

		self.assertTrue(new_tree.deep_equal_to(correct_tree))

	def test_figure_6_14(self):
		"""Test that preprocess_tree() works for network in Figure 6.14.
		"""

		print_status('TestPreprocessTree', 'test_figure_6_14()')

		tree = load_instance("figure_6_14")
		new_tree = gsm_tree.preprocess_tree(tree)

		# Build correct tree.
		correct_tree = SupplyChainNetwork()
		correct_tree.max_max_replenishment_time = 14
		correct_tree.add_node(SupplyChainNode(1, 'Raw_Material', network=correct_tree,
							  processing_time=2,
							  local_holding_cost=0.01,
#							  supply_type='U',
							  external_inbound_cst=0,
							  external_outbound_cst=gsm_tree.BIG_INT,
							  demand_bound_constant=1.6448536269514722,
							  net_demand_mean=0,
							  net_demand_standard_deviation=10,
#							  larger_adjacent_node=2,
#							  larger_adjacent_node_is_downstream=True,
							  max_replenishment_time=2))
		correct_tree.add_node(SupplyChainNode(2, 'Process_Wafers', network=correct_tree,
							  processing_time=3,
							local_holding_cost=0.03,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=3,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=5))
		correct_tree.add_node(SupplyChainNode(3, 'Package_Test_Wafers', network=correct_tree,
							  processing_time=2,
							local_holding_cost=0.04,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=5,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=7))
		correct_tree.add_node(SupplyChainNode(4, 'Imager_Base', network=correct_tree,
							  processing_time=4,
							local_holding_cost=0.06,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=5,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=4))
		correct_tree.add_node(SupplyChainNode(5, 'Imager_Assembly', network=correct_tree,
							  processing_time=2,
							local_holding_cost=0.12,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=6,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=9))
		correct_tree.add_node(SupplyChainNode(6, 'Ship_to_Final_Assembly', network=correct_tree,
							  processing_time=3,
							local_holding_cost=0.13,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=10,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=12))
		correct_tree.add_node(SupplyChainNode(7, 'Camera', network=correct_tree,
							  processing_time=6,
							local_holding_cost=0.20,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=10,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=6))
		correct_tree.add_node(SupplyChainNode(8, 'Circuit_Board', network=correct_tree,
							  processing_time=4,
							local_holding_cost=0.08,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=10,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=4))
		correct_tree.add_node(SupplyChainNode(9, 'Other_Parts', network=correct_tree,
							  processing_time=3,
							local_holding_cost=0.04,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							demand_bound_constant=1.6448536269514722,
							net_demand_mean=0,
							net_demand_standard_deviation=10,
#							larger_adjacent_node=10,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=3))
		correct_tree.add_node(SupplyChainNode(10, 'Build_Test_Pack', network=correct_tree,
							  processing_time=2,
							local_holding_cost=0.50,
							external_inbound_cst=0,
							external_outbound_cst=2,
							demand_bound_constant=1.6448536269514722,
							demand_source=DemandSource(type='N', mean=0, standard_deviation=10),
							net_demand_mean=0,
							net_demand_standard_deviation=10,
							max_replenishment_time=14))
		correct_tree.add_edges_from_list([(1, 2), (2, 3), (3, 5), (4, 5), (5, 6), (6, 10), (7, 10), (8, 10), (9, 10)])

		self.assertTrue(new_tree.deep_equal_to(correct_tree))

	def test_problem_6_7(self):
		"""Test that preprocess_tree() works for network in Problem 6.7.
		"""

		print_status('TestPreprocessTree', 'test_problem_6_7()')

		tree = load_instance("problem_6_7")
		new_tree = gsm_tree.preprocess_tree(tree)

		# Build correct tree.
		correct_tree = SupplyChainNetwork()
		correct_tree.max_max_replenishment_time = 5
		correct_tree.add_node(SupplyChainNode(3, 'Forming', network=correct_tree,
							processing_time=1,
							local_holding_cost=2,
							demand_bound_constant=4,
							external_inbound_cst=1,
							external_outbound_cst=gsm_tree.BIG_INT,
							net_demand_mean=45,
						  	net_demand_standard_deviation=10,
							max_replenishment_time=2))
		correct_tree.add_node(SupplyChainNode(2, 'Firing', network=correct_tree,
							processing_time=1,
							local_holding_cost=3,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
							net_demand_mean=45,
						  	net_demand_standard_deviation=10,
							max_replenishment_time=3))
		correct_tree.add_node(SupplyChainNode(1, 'Glazing', network=correct_tree,
							processing_time=2,
							local_holding_cost=4,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=0,
							demand_source=DemandSource(type='N', mean=45, standard_deviation=10),
							net_demand_mean=45,
						  	net_demand_standard_deviation=10,
							max_replenishment_time=5))
		correct_tree.add_edges_from_list([(2, 1), (3, 2)])

		self.assertTrue(new_tree.deep_equal_to(correct_tree))

	def test_problem_6_9(self):
		"""Test that preprocess_tree() works for network in Problem 6.9.
		"""

		print_status('TestPreprocessTree', 'test_problem_6_9()')

		tree = load_instance("problem_6_9")
		new_tree = gsm_tree.preprocess_tree(tree)

		# Build correct tree.
		correct_tree = SupplyChainNetwork()
		correct_tree.max_max_replenishment_time = 38
		correct_tree.add_node(SupplyChainNode(1, network=correct_tree, 
							processing_time=7,
							local_holding_cost=220*0.2/365,
							demand_bound_constant=4,
#							original_label=1,
							demand_source=DemandSource(type='N', mean=22.0, standard_deviation=4.1),
							external_inbound_cst=0,
							external_outbound_cst=3,
							net_demand_mean=22.0,
						  	net_demand_standard_deviation=4.1,
#							larger_adjacent_node=3,
#							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=38))
		correct_tree.add_node(SupplyChainNode(2, network=correct_tree, 
							processing_time=7,
							local_holding_cost=140*0.2/365,
							demand_bound_constant=4,
#							original_label=2,
							demand_source=DemandSource(type='N', mean=15.3, standard_deviation=6.2),
							external_inbound_cst=0,
							external_outbound_cst=3,
							net_demand_mean=15.3,
						  	net_demand_standard_deviation=6.2,
#							larger_adjacent_node=3,
#							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=38))
		correct_tree.add_node(SupplyChainNode(4, network=correct_tree, 
							processing_time=3,
							local_holding_cost=5*0.2/365,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
#							original_label=4,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=math.sqrt(4.1**2+6.2**2),
#							larger_adjacent_node=3,
#							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=3))
		correct_tree.add_node(SupplyChainNode(3, network=correct_tree, 
							processing_time=21,
							local_holding_cost=90*0.2/365,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
#							original_label=3,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=math.sqrt(4.1**2+6.2**2),
#							larger_adjacent_node=4,
#							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=31))
		correct_tree.add_node(SupplyChainNode(5, network=correct_tree, 
							processing_time=8,
							local_holding_cost=20*0.2/365,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
#							original_label=5,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=math.sqrt(4.1**2+6.2**2),
#							larger_adjacent_node=5,
#							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=10))
		correct_tree.add_node(SupplyChainNode(6, network=correct_tree, 
							processing_time=2,
							local_holding_cost=7.5*0.2/365,
							demand_bound_constant=4,
							external_inbound_cst=0,
							external_outbound_cst=gsm_tree.BIG_INT,
#							original_label=6,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=math.sqrt(4.1**2+6.2**2),
							max_replenishment_time=2))
		correct_tree.add_edges_from_list([(6, 5), (4, 3), (5, 3), (3, 1), (3, 2)])

		self.assertTrue(new_tree.deep_equal_to(correct_tree))


class TestCalculateC(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCalculateC', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCalculateC', 'tear_down_class()')

	def test_example_6_5_k1(self):
		"""Test that calculate_c() works for network in Example 6.5 with k=1.
		"""

		print_status('TestCalculateC', 'test_example_6_5_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Test S = 0, SI = 1.
		c_1_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=1, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_1_0_1, math.sqrt(2) * math.sqrt(3))
		self.assertAlmostEqual(stage_cost, math.sqrt(2) * math.sqrt(3))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 1, SI = 1.
		c_1_1_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=1, SI=1, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_1_1_1, 2.0)
		self.assertAlmostEqual(stage_cost, 2.0)
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 2, SI = 1.
		c_1_2_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=2, SI=1, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_1_2_1, math.sqrt(2))
		self.assertAlmostEqual(stage_cost, math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 3, SI = 1.
		c_1_3_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=3, SI=1, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_1_3_1, 0.0)
		self.assertAlmostEqual(stage_cost, 0.0)
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

	def test_example_6_5_k2(self):
		"""Test that calculate_c() works for network in Example 6.5 with k=2.
		"""

		print_status('TestCalculateC', 'test_example_6_5_k2()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Test S = 0, SI = 0.
		c_2_0_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=0, SI=0, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_2_0_0, 3.0)
		self.assertAlmostEqual(stage_cost, 3.0)
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 1.
		c_2_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=0, SI=1, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_2_0_1, 3 * math.sqrt(2))
		self.assertAlmostEqual(stage_cost, 3 * math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 2.
		c_2_0_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=0, SI=2, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_2_0_2, 3 * math.sqrt(3))
		self.assertAlmostEqual(stage_cost, 3 * math.sqrt(3))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 3.
		c_2_0_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=0, SI=3, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_2_0_3, 6.0)
		self.assertAlmostEqual(stage_cost, 6.0)
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 4.
		c_2_0_4, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=0, SI=4, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_2_0_4, 3 * math.sqrt(5))
		self.assertAlmostEqual(stage_cost, 3 * math.sqrt(5))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

	def test_example_6_5_k3_S0(self):
		"""Test that calculate_c() works for network in Example 6.5 with k=3 and
		S=0.
		"""

		print_status('TestCalculateC', 'test_example_6_5_k3_S0()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {1: {0: math.sqrt(2) * math.sqrt(3),
								 1: 2.0,
								 2: math.sqrt(2),
								 3: 0.0}}
		theta_in_partial = {2: {0: 3.0,
								1: 3 * math.sqrt(2),
								2: 3 * math.sqrt(3),
								3: 6.0,
								4: 3 * math.sqrt(5),
								5: 3 * math.sqrt(6)}}

		# Test S = 0, SI = 0.
		c_3_0_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=0, SI=0,
								theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		correct_cost = 2 * math.sqrt(2) + math.sqrt(2) * math.sqrt(3) + 3.0
		self.assertAlmostEqual(c_3_0_0, correct_cost)
		self.assertAlmostEqual(stage_cost, 2 * math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {1: 0})
		self.assertDictEqual(best_downstream_SI, {2: 0})

		# Test S = 0, SI = 1.
		c_3_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=0, SI=1,
								theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		correct_cost = 4.0 + 2.0 + 3.0
		self.assertAlmostEqual(c_3_0_1, correct_cost)
		self.assertAlmostEqual(stage_cost, 4.0)
		self.assertDictEqual(best_upstream_S, {1: 1})
		self.assertDictEqual(best_downstream_SI, {2: 0})

		# Test S = 0, SI = 2.
		c_3_0_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=0, SI=2,
								theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		correct_cost = 2 * math.sqrt(2) * math.sqrt(3) + math.sqrt(2) + 3.0
		self.assertAlmostEqual(c_3_0_2, correct_cost)
		self.assertAlmostEqual(stage_cost, 2 * math.sqrt(2) * math.sqrt(3))
		self.assertDictEqual(best_upstream_S, {1: 2})
		self.assertDictEqual(best_downstream_SI, {2: 0})

		# Test S = 0, SI = 3.
		c_3_0_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=0, SI=3,
								theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		correct_cost = 4 * math.sqrt(2) + 0.0 + 3.0
		self.assertAlmostEqual(c_3_0_3, correct_cost)
		self.assertAlmostEqual(stage_cost, 4 * math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {1: 3})
		self.assertDictEqual(best_downstream_SI, {2: 0})

	def test_example_6_5_k3_S2(self):
		"""Test that calculate_c() works for network in Example 6.5 with k=3 and
		S=2.
		"""

		print_status('TestCalculateC', 'test_example_6_5_k3_S2()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {1: {0: math.sqrt(2) * math.sqrt(3),
								 1: 2.0,
								 2: math.sqrt(2),
								 3: 0.0}}
		theta_in_partial = {2: {0: 3.0,
								1: 3 * math.sqrt(2),
								2: 3 * math.sqrt(3),
								3: 6.0,
								4: 3 * math.sqrt(5),
								5: 3 * math.sqrt(6)}}

		# Test S = 2, SI = 1.
		c_3_2_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=2, SI=1,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 0.0 + 2.0 + 3 * math.sqrt(3)
		self.assertAlmostEqual(c_3_2_1, correct_cost)
		self.assertAlmostEqual(stage_cost, 0.0)
		self.assertDictEqual(best_upstream_S, {1: 1})
		self.assertDictEqual(best_downstream_SI, {2: 2})

		# Test S = 2, SI = 2.
		c_3_2_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=2, SI=2,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 2 * math.sqrt(2) + math.sqrt(2) + 3 * math.sqrt(3)
		self.assertAlmostEqual(c_3_2_2, correct_cost)
		self.assertAlmostEqual(stage_cost, 2 * math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {1: 2})
		self.assertDictEqual(best_downstream_SI, {2: 2})

		# Test S = 2, SI = 3.
		c_3_2_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=2, SI=3,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 4.0 + 0.0 + 3 * math.sqrt(3)
		self.assertAlmostEqual(c_3_2_3, correct_cost)
		self.assertAlmostEqual(stage_cost, 4.0)
		self.assertDictEqual(best_upstream_S, {1: 3})
		self.assertDictEqual(best_downstream_SI, {2: 2})

	def test_example_6_5_k4(self):
		"""Test that calculate_c() works for network in Example 6.5 with k=4.
		"""

		print_status('TestCalculateC', 'test_example_6_5_k4()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {1: {0: math.sqrt(2) * math.sqrt(3),
								 1: 2.0,
								 2: math.sqrt(2),
								 3: 0.0},
							 3: {0: 2 * math.sqrt(2) + math.sqrt(2) * math.sqrt(3) + 3.0,
								 1: math.sqrt(2) * math.sqrt(3) + 3 * math.sqrt(2),
								 2: 2 + 3 * math.sqrt(3),
								 3: math.sqrt(2) + 6,
								 4: 3 * math.sqrt(5)}}
		theta_in_partial = {2: {0: 3.0,
								1: 3 * math.sqrt(2),
								2: 3 * math.sqrt(3),
								3: 6.0,
								4: 3 * math.sqrt(5),
								5: 3 * math.sqrt(6)}}

		# Test S = 1, SI = 0.
		c_4_1_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=4, S=1, SI=0,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 0.0 + 2 * math.sqrt(2) + math.sqrt(2) * math.sqrt(3) + 3.0
		self.assertAlmostEqual(c_4_1_0, correct_cost)
		self.assertAlmostEqual(stage_cost, 0.0)
		self.assertDictEqual(best_upstream_S, {3: 0})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 1, SI = 1.
		c_4_1_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=4, S=1, SI=1,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 3.0 + (math.sqrt(2) * math.sqrt(3) + 3 * math.sqrt(2))
		self.assertAlmostEqual(c_4_1_1, correct_cost)
		self.assertAlmostEqual(stage_cost, 3.0)
		self.assertDictEqual(best_upstream_S, {3: 1})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 1, SI = 2.
		c_4_1_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=4, S=1, SI=2,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 3 * math.sqrt(2) + (math.sqrt(2) * math.sqrt(3) + 3 * math.sqrt(2))
		self.assertAlmostEqual(c_4_1_2, correct_cost)
		self.assertAlmostEqual(stage_cost, 3 * math.sqrt(2))
		self.assertDictEqual(best_upstream_S, {3: 1})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 1, SI = 3.
		c_4_1_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=4, S=1, SI=3,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 3 * math.sqrt(3) + (math.sqrt(2) * math.sqrt(3) + 3 * math.sqrt(2))
		self.assertAlmostEqual(c_4_1_3, correct_cost)
		self.assertAlmostEqual(stage_cost, 3 * math.sqrt(3))
		self.assertDictEqual(best_upstream_S, {3: 1})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 1, SI = 4.
		c_4_1_4, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=4, S=1, SI=4,
								 theta_in_partial=theta_in_partial,
								 theta_out_partial=theta_out_partial)
		correct_cost = 6.0 + (math.sqrt(2) * math.sqrt(3) + 3 * math.sqrt(2))
		self.assertAlmostEqual(c_4_1_4, correct_cost)
		self.assertAlmostEqual(stage_cost, 6.0)
		self.assertDictEqual(best_upstream_S, {3: 1})
		self.assertDictEqual(best_downstream_SI, {})

	def test_problem_6_7_k1(self):
		"""Test that calculate_c() works for network in Problem 6.7 with k=1.
		"""

		print_status('TestCalculateC', 'test_problem_6_7_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Test S = 0, SI = 0.
		SI = 0
		c_1_0_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								theta_out_partial={})
		self.assertAlmostEqual(c_1_0_0, 4 * 4 * 10 * math.sqrt(SI+2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI+2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 1.
		SI = 1
		c_1_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								 theta_out_partial={})
		self.assertAlmostEqual(c_1_0_1, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 2.
		SI = 2
		c_1_0_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								 theta_out_partial={})
		self.assertAlmostEqual(c_1_0_2, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 3.
		SI = 3
		c_1_0_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								 theta_out_partial={})
		self.assertAlmostEqual(c_1_0_3, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 4.
		SI = 4
		c_1_0_4, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								 theta_out_partial={})
		self.assertAlmostEqual(c_1_0_4, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

		# Test S = 0, SI = 5.
		SI = 5
		c_1_0_5, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=1, S=0, SI=SI, theta_in_partial={},
								 theta_out_partial={})
		self.assertAlmostEqual(c_1_0_5, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertAlmostEqual(stage_cost, 4 * 4 * 10 * math.sqrt(SI + 2))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {})

	def test_problem_6_7_k2_SI0(self):
		"""Test that calculate_c() works for network in Problem 6.7 with k=2 and
		SI=0.
		"""

		print_status('TestCalculateC', 'test_problem_6_7_k2_SI0()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {}
		theta_in_partial = {1: {SI: 4 * 4 * 10 * math.sqrt(SI+2) for SI in range(6)}}

		# Test S = 0, SI = 0.
		S = 0
		SI = 0
		c_2_0_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_0_0, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 1, SI = 0.
		S = 1
		SI = 0
		c_2_1_0, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_1_0, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

	def test_problem_6_7_k2_SI1(self):
		"""Test that calculate_c() works for network in Problem 6.7 with k=2 and
		SI=1.
		"""

		print_status('TestCalculateC', 'test_problem_6_7_k2_SI1()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {}
		theta_in_partial = {1: {SI: 4 * 4 * 10 * math.sqrt(SI+2) for SI in range(6)}}

		# Test S = 0, SI = 1.
		S = 0
		SI = 1
		c_2_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_0_1, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 1, SI = 1.
		S = 1
		SI = 1
		c_2_1_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_1_1, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 2, SI = 1.
		S = 2
		SI = 1
		c_2_2_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_2_1, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

	def test_problem_6_7_k2_SI2(self):
		"""Test that calculate_c() works for network in Problem 6.7 with k=2 and
		SI=2.
		"""

		print_status('TestCalculateC', 'test_problem_6_7_k2_SI2()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {}
		theta_in_partial = {1: {SI: 4 * 4 * 10 * math.sqrt(SI+2) for SI in range(6)}}

		# Test S = 0, SI = 2.
		S = 0
		SI = 2
		c_2_0_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_0_2, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 1, SI = 2.
		S = 1
		SI = 2
		c_2_1_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_1_2, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 2, SI = 2.
		S = 2
		SI = 2
		c_2_2_2, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_2_2, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

		# Test S = 2, SI = 3.
		S = 2
		SI = 3
		c_2_2_3, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=2, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_2_2_3, 3 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   4 * 4 * 10 * math.sqrt(S+2))
		self.assertAlmostEqual(stage_cost, 3 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {1: S})

	def test_problem_6_7_k3(self):
		"""Test that calculate_c() works for network in Problem 6.7 with k=3.
		"""

		print_status('TestCalculateC', 'test_problem_6_7_k3()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		# Build theta_in_partial and theta_out_partial.
		theta_out_partial = {}
		theta_in_partial = {1: {SI: 4 * 4 * 10 * math.sqrt(SI+2) for SI in range(6)},
							2: {SI: 160 * math.sqrt(SI+3) for SI in range(6)}}

		# Test S = 0, SI = 1.
		S = 0
		SI = 1
		c_3_0_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_3_0_1, 2 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   theta_in_partial[2][S])
		self.assertAlmostEqual(stage_cost, 2 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {2: S})

		# Test S = 1, SI = 1.
		S = 1
		SI = 1
		c_3_1_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_3_1_1, 2 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   theta_in_partial[2][S])
		self.assertAlmostEqual(stage_cost, 2 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {2: S})

		# Test S = 2, SI = 1.
		S = 2
		SI = 1
		c_3_2_1, stage_cost, best_upstream_S, best_downstream_SI = \
			gsm_tree._calculate_c(tree, k_index=3, S=S, SI=SI, theta_in_partial=theta_in_partial,
								theta_out_partial=theta_out_partial)
		self.assertAlmostEqual(c_3_2_1, 2 * 4 * 10 * math.sqrt(SI + 1 - S) +
							   theta_in_partial[2][S])
		self.assertAlmostEqual(stage_cost, 2 * 4 * 10 * math.sqrt(SI + 1 - S))
		self.assertDictEqual(best_upstream_S, {})
		self.assertDictEqual(best_downstream_SI, {2: S})


class TestCalculateThetaOut(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCalculateThetaOut', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCalculateThetaOut', 'tear_down_class()')

	def test_example_6_5_k1(self):
		"""Test that calculate_theta_out() works for network in Example 6.5 with k=1.
		"""

		print_status('TestCalculateThetaOut', 'test_example_6_5_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 1
		SI = 1
		theta_in_partial = {}
		theta_out_partial = {}

		for S in range(4):
			theta_out, best_cst_adjacent = \
				gsm_tree._calculate_theta_out(tree, k, S, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_out, math.sqrt(2) * math.sqrt(3 - S))
			self.assertDictEqual(best_cst_adjacent, {1: SI})

	def test_example_6_5_k3(self):
		"""Test that calculate_theta_out() works for network in Example 6.5 with k=3.
		"""

		print_status('TestCalculateThetaOut', 'test_example_6_5_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 3
		theta_in_partial = {2: {SI: 3 * math.sqrt(SI + 1) for SI in range(6)}}
		theta_out_partial = {1: {S: math.sqrt(2) * math.sqrt(3 - S) for S in range(4)}}

		# Test all S = 0,...,4. (Optimal SI values are stored in opt_SI dict.)
		opt_SI = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3}
		for S in range(5):
			theta_out, best_cst_adjacent = \
				gsm_tree._calculate_theta_out(tree, k, S, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_out, 2 * math.sqrt(2) * math.sqrt(opt_SI[S] + 1 - S)
								   + theta_out_partial[1][opt_SI[S]]
								   + theta_in_partial[2][S])
			self.assertDictEqual(best_cst_adjacent, {1: opt_SI[S], 2: S, 3: opt_SI[S]})

	def test_problem_6_7_k3(self):
		"""Test that calculate_theta_out() works for network in Problem 6.7 with k=3.
		"""

		print_status('TestCalculateThetaOut', 'test_problem_6_7_k3()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 3
		theta_in_partial = {1: {SI: 160 * math.sqrt(SI + 2) for SI in range(6)},
							2: {SI: 160 * math.sqrt(SI + 3) for SI in range(6)}}
		theta_out_partial = {}

		SI = 1
		S = 2
		theta_in, best_cst_adjacent = \
			gsm_tree._calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial)
		self.assertAlmostEqual(theta_in, 80 * math.sqrt(SI + 1 - S)
							   + theta_in_partial[2][S])
		self.assertDictEqual(best_cst_adjacent, {2: S,
												 3: S})

class TestCalculateThetaIn(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCalculateThetaIn', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCalculateThetaIn', 'tear_down_class()')

	def test_example_6_5_k2(self):
		"""Test that calculate_theta_in() works for network in Example 6.5 with k=2.
		"""

		print_status('TestCalculateThetaIn', 'test_example_6_5_k2()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 2
		S = 0
		theta_in_partial = {}
		theta_out_partial = {1: {S: math.sqrt(2) * math.sqrt(3 - S) for S in range(4)}}

		for SI in range(5):
			theta_in, best_cst_adjacent = \
				gsm_tree._calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_in, 3 * math.sqrt(SI + 1 - S))
			self.assertDictEqual(best_cst_adjacent, {2: S})

	def test_example_6_5_k4(self):
		"""Test that calculate_theta_in() works for network in Example 6.5 with k=4.
		"""

		print_status('TestCalculateThetaIn', 'test_example_6_5_k4()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 4
		theta_in_partial = {2: {SI: 3 * math.sqrt(SI + 1) for SI in range(6)}}
		theta_out_partial = {1: {S: math.sqrt(2) * math.sqrt(3 - S) for S in range(4)},
							 3: {0: 2 * math.sqrt(2) + math.sqrt(2) * math.sqrt(3) + theta_in_partial[2][0],
								 1: 0.0 + math.sqrt(2) * math.sqrt(3) + theta_in_partial[2][1],
								 2: 0.0 + 2.0 + theta_in_partial[2][2],
								 3: 0.0 + math.sqrt(2) + theta_in_partial[2][3],
								 4: 0.0 + 0.0 + theta_in_partial[2][4]}}


		# Test all SI = 0,..., 4. (Optimal S values are stored in opt_S dict.)
		opt_S = {0: 0, 1: 1, 2: 1, 3: 1, 4: 1}
		for SI in range(5):
			theta_in, best_cst_adjacent = \
				gsm_tree._calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_in, 3 * math.sqrt(SI) + theta_out_partial[3][opt_S[SI]])
			self.assertDictEqual(best_cst_adjacent, {3: opt_S[SI], 4: 1})

	def test_problem_6_7_k1(self):
		"""Test that calculate_theta_in() works for network in Problem 6.7 with k=1.
		"""

		print_status('TestCalculateThetaIn', 'test_problem_6_7_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 1
		S = 0
		theta_in_partial = {}
		theta_out_partial = {}

		for SI in range(6):
			theta_in, best_cst_adjacent = \
				gsm_tree._calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_in, 160 * math.sqrt(SI + 2))
			self.assertDictEqual(best_cst_adjacent, {1: S})

	def test_problem_6_7_k2(self):
		"""Test that calculate_theta_in() works for network in Problem 6.7 with k=2.
		"""

		print_status('TestCalculateThetaIn', 'test_problem_6_7_k1()')

		tree = gsm_tree.preprocess_tree(load_instance("problem_6_7"))
		tree = gsm_tree.relabel_nodes(tree, start_index=1)

		k = 2
		theta_in_partial = {1: {SI: 160 * math.sqrt(SI + 2) for SI in range(6)}}
		theta_out_partial = {}

		opt_S = {0: 1, 1: 2, 2: 3}
		for SI in range(3):
			theta_in, best_cst_adjacent = \
				gsm_tree._calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial)
			self.assertAlmostEqual(theta_in, 120 * math.sqrt(SI + 1 - opt_S[SI])
								   + theta_in_partial[1][opt_S[SI]])
			self.assertDictEqual(best_cst_adjacent, {1: opt_S[SI],
													 2: opt_S[SI]})


class TestOptimizeCommittedServiceTimes(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestOptimizeCommittedServiceTimes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestOptimizeCommittedServiceTimes', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that optimize_committed_service_times() works for network in
		Example 6.5.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_example_6_5')

		tree = load_instance("example_6_5")

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertEqual(opt_cost, 2 * math.sqrt(2) + math.sqrt(6) + 3.0)
		self.assertDictEqual(opt_cst, {1: 0, 2: 0, 3: 0, 4: 1})

	def test_figure_6_14(self):
		"""Test that optimize_committed_service_times() works for network in
		Figure 6.14.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_figure_6_14')

		tree = load_instance("figure_6_14")

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 18.8240044725922)
		self.assertDictEqual(opt_cst, {1: 0,
									   2: 3,
									   3: 5,
									   4: 4,
									   5: 7,
									   7: 0,
									   6: 0,
									   8: 0,
									   9: 0,
									  10: 2})

	def test_figure_6_14_s5(self):
		"""Test that optimize_committed_service_times() works for network in
		Figure 6.14 with CST to external customer = 5.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_figure_6_14_s5')

		tree = copy.deepcopy(load_instance("figure_6_14"))
		tree.nodes_by_index[10].external_outbound_cst = 5

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 12.4686888061037)
		self.assertDictEqual(opt_cst, {1: 0,
									   2: 3,
									   3: 5,
									   4: 4,
									   5: 0,
									   7: 3,
									   6: 3,
									   8: 3,
									   9: 3,
									   10: 5})

	def test_figure_6_14_s8(self):
		"""Test that optimize_committed_service_times() works for network in
		Figure 6.14 with CST to external customer = 8.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_figure_6_14_s8')

		tree = copy.deepcopy(load_instance("figure_6_14"))
		tree.nodes_by_index[10].external_outbound_cst = 8

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 3.25788236403285)
		self.assertDictEqual(opt_cst, {1: 0,
									   2: 3,
									   3: 1,
									   4: 1,
									   5: 3,
									   7: 6,
									   6: 6,
									   8: 4,
									   9: 3,
									   10: 8})

	def test_figure_6_14_s12(self):
		"""Test that optimize_committed_service_times() works for network in
		Figure 6.14 with CST to external customer = 12.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_figure_6_14_s12')

		tree = copy.deepcopy(load_instance("figure_6_14"))
		tree.nodes_by_index[10].external_outbound_cst = 12

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 0.232617430735335)
		self.assertDictEqual(opt_cst, {1: 0,
									   2: 3,
									   3: 5,
									   4: 4,
									   5: 7,
									   7: 6,
									   6: 10,
									   8: 4,
									   9: 3,
									   10: 12})

	def test_problem_6_7(self):
		"""Test that optimize_committed_service_times() works for network in
		Problem 6.7.
		"""

		print_status('TestOptimizeCommittedServiceTimes', 'test_problem_6_7')

		tree = load_instance("problem_6_7")

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 160 * math.sqrt(5))
		self.assertDictEqual(opt_cst, {1: 0, 2: 3, 3: 2})

	def test_problem_6_9(self):
		"""Test that optimize_committed_service_times() works for network in
		Problem 6.9."""

		print_status('TestOptimizeCommittedServiceTimes', 'test_problem_6_9')

		tree = load_instance("problem_6_9")

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 15.649530249501)
		self.assertDictEqual(opt_cst, {1: 3, 2: 3, 3: 0, 4: 0, 5: 0, 6: 2})

	def test_problem_6_9_s1_0_s2_7(self):
		"""Test that optimize_committed_service_times() works for network in
		Problem 6.9 with s_1 = 0 and s_2 = 7."""

		print_status('TestOptimizeCommittedServiceTimes', 'test_problem_6_9_s1_0_s2_7')

		tree = copy.deepcopy(load_instance("problem_6_9"))
		tree.nodes_by_index[1].external_outbound_cst = 0
		tree.nodes_by_index[2].external_outbound_cst = 7

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 13.121240238718)
		self.assertDictEqual(opt_cst, {1: 0, 2: 7, 3: 0, 4: 0, 5: 0, 6: 2})

	def test_problem_6_9_s1_21_s2_5(self):
		"""Test that optimize_committed_service_times() works for network in
		Problem 6.9 with s_1 = 21 and s_2 = 5."""

		print_status('TestOptimizeCommittedServiceTimes', 'test_problem_6_9_s1_21_s2_5')

		tree = copy.deepcopy(load_instance("problem_6_9"))
		tree.nodes_by_index[1].external_outbound_cst = 21
		tree.nodes_by_index[2].external_outbound_cst = 5

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 10.5811190103555)
		self.assertDictEqual(opt_cst, {1: 7, 2: 5, 3: 0, 4: 0, 5: 0, 6: 2})

	def test_single_stage_instance(self):
		"""Test that optimize_committed_service_times() works for a
		single-stage instance."""

		print_status('TestOptimizeCommittedServiceTimes', 'test_single_stage_instance')

		tree = SupplyChainNetwork()
		tree.add_node(SupplyChainNode(1, processing_time=1,
			external_inbound_cst=0,
			external_outbound_cst=0,
			local_holding_cost=1,
			demand_bound_constant=2,
			demand_source=DemandSource(type='N', mean=0, standard_deviation=1)
		))

		opt_cst, opt_cost = \
			gsm_tree.optimize_committed_service_times(tree)

		self.assertAlmostEqual(opt_cost, 2)
		self.assertDictEqual(opt_cst, {1: 0})

	def test_bad_params(self):
		"""Test that optimize_committed_service_times() correctly raises errors on bad parameters."""

		print_status('TestOptimizeCommittedServiceTimes', 'test_bad_params')

		tree = load_instance("problem_6_9")
		tree.nodes_by_index[1].demand_source.mean = None
		with self.assertRaises(ValueError):
			gsm_tree.optimize_committed_service_times(tree)

		tree = load_instance("problem_6_9")
		tree.nodes_by_index[2].demand_source.standard_deviation = None
		with self.assertRaises(ValueError):
			gsm_tree.optimize_committed_service_times(tree)
