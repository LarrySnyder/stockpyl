import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm
import copy

#from supply_chain_node import *
from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_product import *
from stockpyl.supply_chain_node import SupplyChainNode
from stockpyl.demand_source import DemandSource
from stockpyl.instances import *
from stockpyl.sim import *
from tests.settings import *
#RUN_ALL_TESTS = False

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_supply_chain_network   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestSupplyChainNetworkInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNetworkInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNetworkInit', 'tear_down_class()')

	def test_kwargs(self):
		"""Test that SupplyChainNetwork.__init__() produces identical networks
		if parameters are passed as arguments vs. set later.
		"""
		print_status('TestSupplyChainNetworkInit', 'test_kwargs()')

		network1 = SupplyChainNetwork(period=10, max_max_replenishment_time=20)
		network2 = SupplyChainNetwork()
		network2.period = 10
		network2.max_max_replenishment_time = 20
		self.assertTrue(network1.deep_equal_to(network2))

	def test_bad_params(self):
		"""Test that SupplyChainNetwork.__init__() correctly raises errors on
		invalid parameters.
		"""
		print_status('TestSupplyChainNetworkInit', 'test_bad_params()')

		with self.assertRaises(AttributeError):
			_ = SupplyChainNetwork(period=4, foo=7)


class TestDeepEqualTo(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDeepEqualTo', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDeepEqualTo', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test deep_equal_to() on 3-node serial system.
		"""
		print_status('TestDeepEqualTo', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		prod0 = SupplyChainProduct(0)
		prod1 = SupplyChainProduct(1)

		network.add_node(node2)
		network.add_successor(node2, node1)
		network.add_successor(node1, node0)

		network.add_product(prod0)
		network.add_product(prod1)

		# Equal networks.
		network2 = copy.deepcopy(network)
		self.assertTrue(network.deep_equal_to(network2))
		self.assertTrue(network2.deep_equal_to(network))
		
		# Unequal networks due to parameter.
		network2.nodes_by_index[1].in_transit_holding_cost = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))
		network2 = copy.deepcopy(network)
		network2.max_max_replenishment_time = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))
		network2 = copy.deepcopy(network)
		network2.products[0].stockout_cost = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

		# Unequal networks due to missing node.
		network2 = copy.deepcopy(network)
		network2.remove_node(network2.nodes[0])
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

		# Unequal networks due to missing product.
		network2 = copy.deepcopy(network)
		network2.remove_product(network2._local_product_indices[0])
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

	def test_4_node_owmr(self):
		"""Test deep_equal_to() on 4-node OWMR system.
		"""
		print_status('TestDeepEqualTo', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_successor(node0, node1)
		network.add_successor(node0, node2)
		network.add_successor(node0, node3)

		# Equal networks.
		network2 = copy.deepcopy(network)
		self.assertTrue(network.deep_equal_to(network2))
		self.assertTrue(network2.deep_equal_to(network))
		
		# Unequal networks due to parameter.
		network2.nodes_by_index[1].in_transit_holding_cost = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))
		network2 = copy.deepcopy(network)
		network2.max_max_replenishment_time = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

		# Unequal networks due to missing node.
		network2 = copy.deepcopy(network)
		network2.remove_node(network2.nodes[2])
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

	def test_multiproduct_5_7(self):
		"""Test deep_equal_to() on 5-node, 7-product system.
		"""
		print_status('TestDeepEqualTo', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		# Equal networks.
		network2 = copy.deepcopy(network)
		self.assertTrue(network.deep_equal_to(network2))
		self.assertTrue(network2.deep_equal_to(network))
		
		# Unequal networks due to parameter.
		network2.nodes_by_index[1].in_transit_holding_cost = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))
		network2 = copy.deepcopy(network)
		network2.max_max_replenishment_time = 99
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

		# Unequal networks due to missing node.
		network2 = copy.deepcopy(network)
		network2.remove_node(network2.nodes[2])
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

		# Unequal networks due to missing product.
		network2 = copy.deepcopy(network)
		network2.nodes_by_index[0].remove_product(0)
		self.assertFalse(network.deep_equal_to(network2))
		self.assertFalse(network2.deep_equal_to(network))

class TestInitialize(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestInitialize', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestInitialize', 'tear_down_class()')

	def test_initialize(self):
		"""Test that initialize() correctly initializes.
		"""
		print_status('TestInitialize', 'test_copy()')

		network1 = SupplyChainNetwork()
		network2 = SupplyChainNetwork()
		network1.initialize()
		self.assertTrue(network1.deep_equal_to(network2))

		network1 = SupplyChainNetwork()
		network1.period = 17
		network1.max_max_replenishment_time = 80
		network1.initialize()
		network2 = SupplyChainNetwork()
		self.assertTrue(network1.deep_equal_to(network2))

class TestEdges(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEdges', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEdges', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test edges property for 3-node serial system.
		"""
		print_status('TestEdges', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_successor(node2, node1)
		network.add_successor(node1, node0)

		edges = network.edges

		self.assertListEqual(edges, [(2, 1), (1, 0)])

	def test_4_node_owmr(self):
		"""Test edges property for 4-node OWMR system.
		"""
		print_status('TestEdges', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_successor(node0, node1)
		network.add_successor(node0, node2)
		network.add_successor(node0, node3)

		edges = network.edges

		self.assertListEqual(edges, [(0, 1), (0, 2), (0, 3)])


class TestHasDirectedCycle(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestHasDirectedCycle', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestHasDirectedCycle', 'tear_down_class()')

	def test_named_instances(self):
		"""Test has_directed_cycle() for a few named instances.
		"""
		print_status('TestHasDirectedCycle', 'test_named_instances()')

		instance = load_instance("example_6_1")
		self.assertFalse(instance.has_directed_cycle())

		instance = load_instance("rosling_figure_1")
		self.assertFalse(instance.has_directed_cycle())

		instance = load_instance("rong_atan_snyder_figure_1a")
		self.assertFalse(instance.has_directed_cycle())

	def test_cyclic(self):
		"""Test has_directed_cycle() for a cyclic network.
		"""
		print_status('TestHasDirectedCycle', 'test_cyclic()')

		instance = load_instance("example_6_1")
		instance.add_edge(1, 3)
		self.assertTrue(instance.has_directed_cycle())

		instance = load_instance("example_6_1")
		instance.add_edge(1, 2)
		self.assertTrue(instance.has_directed_cycle())

		instance = load_instance("rosling_figure_1")
		instance.add_node(SupplyChainNode(index=8))
		instance.add_edges_from_list([(1, 8), (8, 6)])
		self.assertTrue(instance.has_directed_cycle())

		instance = load_instance("rosling_figure_1")
		instance.add_edge(1, 3)
		self.assertTrue(instance.has_directed_cycle())

	def test_single_node(self):
		"""Test has_directed_cycle() for a network consisting of a single node.
		"""
		print_status('TestHasDirectedCycle', 'test_single_node()')

		instance = SupplyChainNetwork()
		instance.add_node(SupplyChainNode(index=1))
		self.assertFalse(instance.has_directed_cycle())

class TestAddSuccessor(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddSuccessor', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddSuccessor', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test add_successor() to build 3-node serial system.
		"""
		print_status('TestAddSuccessor', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_successor(node2, node1)
		network.add_successor(node1, node0)

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()

		self.assertEqual(node0succ, [])
		self.assertEqual(node1succ, [0])
		self.assertEqual(node2succ, [1])

	def test_3_node_serial_dupe(self):
		"""Test add_successor() to build 3-node serial system when the nodes
		are already in the network.
		"""
		print_status('TestAddSuccessor', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_node(node1)
		network.add_node(node0)

		network.add_successor(node2, node1)
		network.add_successor(node1, node0)

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()

		self.assertEqual(node0succ, [])
		self.assertEqual(node1succ, [0])
		self.assertEqual(node2succ, [1])

	def test_4_node_owmr(self):
		"""Test add_successor() to build 4-node OWMR system.
		"""
		print_status('TestAddSuccessor', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_successor(node0, node1)
		network.add_successor(node0, node2)
		network.add_successor(node0, node3)

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()
		node3succ = node3.successor_indices()

		self.assertEqual(node0succ, [1, 2, 3])
		self.assertEqual(node1succ, [])
		self.assertEqual(node2succ, [])
		self.assertEqual(node3succ, [])


class TestAddEdge(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddEdge', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddEdge', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test add_edge() on 3-node serial system.
		"""
		print_status('TestAddEdge', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_node(node1)
		network.add_node(node0)

		network.add_edge(2, 1)
		network.add_edge(1, 0)

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()

		self.assertEqual(node0succ, [])
		self.assertEqual(node1succ, [0])
		self.assertEqual(node2succ, [1])

		# Check that edge is not added if it already exists.
		num_edges = len(network.edges)
		network.add_edge(2, 1)
		self.assertEqual(num_edges, len(network.edges))

		# Check that error is raised if nodes do not exist.
		with self.assertRaises(KeyError):
			network.add_edge(5, 1)

	def test_4_node_owmr(self):
		"""Test add_edge() on 4-node OWMR system.
		"""
		print_status('TestAddEdge', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_node(node1)
		network.add_node(node2)
		network.add_node(node3)

		network.add_edge(0, 1)
		network.add_edge(0, 2)
		network.add_edge(0, 3)

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()
		node3succ = node3.successor_indices()

		self.assertEqual(node0succ, [1, 2, 3])
		self.assertEqual(node1succ, [])
		self.assertEqual(node2succ, [])
		self.assertEqual(node3succ, [])

		# Check that edge is not added if it already exists.
		num_edges = len(network.edges)
		network.add_edge(0, 2)
		self.assertEqual(num_edges, len(network.edges))
		

class TestAddEdgesFromList(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddEdgesFromList', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddEdgesFromList', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test add_edges_from_list() on 3-node serial system.
		"""
		print_status('TestAddEdgesFromList', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_node(node1)
		network.add_node(node0)

		network.add_edges_from_list([(2, 1), (1, 0)])

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()

		self.assertEqual(node0succ, [])
		self.assertEqual(node1succ, [0])
		self.assertEqual(node2succ, [1])

		# Check that edge is not added if it already exists.
		num_edges = len(network.edges)
		network.add_edges_from_list([(2, 1)])
		self.assertEqual(num_edges, len(network.edges))
		
		# Check that error is raised if nodes do not exist.
		with self.assertRaises(KeyError):
			network.add_edges_from_list([(5, 1)])

	def test_4_node_owmr(self):
		"""Test add_edges_from_list() on 4-node OWMR system.
		"""
		print_status('TestAddEdgesFromList', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_node(node1)
		network.add_node(node2)
		network.add_node(node3)

		network.add_edges_from_list([(0, 1), (0, 2), (0, 3)])

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node2succ = node2.successor_indices()
		node3succ = node3.successor_indices()

		self.assertEqual(node0succ, [1, 2, 3])
		self.assertEqual(node1succ, [])
		self.assertEqual(node2succ, [])
		self.assertEqual(node3succ, [])

		# Check that edge is not added if it already exists.
		num_edges = len(network.edges)
		network.add_edges_from_list([(0, 1), (0, 3)])
		self.assertEqual(num_edges, len(network.edges))


class TestRemoveNode(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRemoveNode', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRemoveNode', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test remove_node() on 3-node serial system.
		"""
		print_status('TestRemoveNode', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_node(node1)
		network.add_node(node0)

		network.add_edges_from_list([(2, 1), (1, 0)])

		network.remove_node(network.nodes_by_index[1])

		node0succ = node0.successor_indices()
		node2succ = node2.successor_indices()

		self.assertEqual(node0succ, [])
		self.assertEqual(node2succ, [])

	def test_4_node_owmr(self):
		"""Test remove_node() on 4-node OWMR system.
		"""
		print_status('TestRemoveNode', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_node(node1)
		network.add_node(node2)
		network.add_node(node3)

		network.add_edges_from_list([(0, 1), (0, 2), (0, 3)])

		network.remove_node(network.nodes_by_index[2])

		node0succ = node0.successor_indices()
		node1succ = node1.successor_indices()
		node3succ = node3.successor_indices()

		self.assertEqual(node0succ, [1, 3])
		self.assertEqual(node1succ, [])
		self.assertEqual(node3succ, [])


class TestParseNode(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestParseNode', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestParseNode', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test parse_node() on 3-node serial system.
		"""
		print_status('TestParseNode', 'test_example_6_1()')

		network = load_instance("example_6_1") # 3 -> 2 -> 1
		nodes = {n.index: n for n in network.nodes}

		node_obj, node_ind = network.parse_node(nodes[1])
		self.assertEqual(node_obj, nodes[1])
		self.assertEqual(node_ind, 1)

		node_obj, node_ind = network.parse_node(nodes[3])
		self.assertEqual(node_obj, nodes[3])
		self.assertEqual(node_ind, 3)

		node_obj, node_ind = network.parse_node(1)
		self.assertEqual(node_obj, nodes[1])
		self.assertEqual(node_ind, 1)

		node_obj, node_ind = network.parse_node(3)
		self.assertEqual(node_obj, nodes[3])
		self.assertEqual(node_ind, 3)

		node_obj, node_ind = network.parse_node(None)
		self.assertIsNone(node_obj)
		self.assertIsNone(node_ind)

	def test_bad_param(self):
		"""Test that parse_node() raises errors correctly on bad parameters.
		"""
		print_status('TestParseNode', 'test_bad_param()')

		network = load_instance("example_6_1") # 3 -> 2 -> 1

		with self.assertRaises(TypeError):
			_, _ = network.parse_node(6.5)
			_, _ = network.parse_node(network.products[0])
			_, _ = network.parse_node(None, allow_none=False)

		with self.assertRaises(ValueError):
			_, _ = network.parse_node(5)
			_, _ = network.parse_node(SupplyChainNode(5))

		
class TestParseProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestParseProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestParseProduct', 'tear_down_class()')

	def test_multiproduct_5_7(self):
		"""Test parse_product() on 5-node, 7-product system.
		"""
		print_status('TestParseProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		products = {n.index: n for n in network.products}

		product_obj, product_ind = network.parse_product(products[1])
		self.assertEqual(product_obj, products[1])
		self.assertEqual(product_ind, 1)

		product_obj, product_ind = network.parse_product(products[3])
		self.assertEqual(product_obj, products[3])
		self.assertEqual(product_ind, 3)

		product_obj, product_ind = network.parse_product(1)
		self.assertEqual(product_obj, products[1])
		self.assertEqual(product_ind, 1)

		product_obj, product_ind = network.parse_product(3)
		self.assertEqual(product_obj, products[3])
		self.assertEqual(product_ind, 3)

		product_obj, product_ind = network.parse_product(None)
		self.assertIsNone(product_obj)
		self.assertIsNone(product_ind)

	def test_bad_param(self):
		"""Test that parse_product() raises errors correctly on bad parameters.
		"""
		print_status('TestParseProduct', 'test_bad_param()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		with self.assertRaises(TypeError):
			_, _ = network.parse_product(6.5)
			_, _ = network.parse_product(network.nodes[0])
			_, _ = network.parse_product(None, allow_none=False)

		with self.assertRaises(ValueError):
			_, _ = network.parse_product(55)
			_, _ = network.parse_product(SupplyChainProduct(55))
		
				
class TestAddRemoveProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddRemoveProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddRemoveProduct', 'tear_down_class()')

	def test_basic(self):
		"""Test remove_product() on product-only system.
		"""
		print_status('TestAddRemoveProduct', 'test_basic()')

		network = SupplyChainNetwork()

		prod0 = SupplyChainProduct(0)
		prod1 = SupplyChainProduct(1)

		network.add_product(prod0)
		network.add_product(prod1)

		network.remove_product(network.products_by_index[1])

		self.assertEqual(network.product_indices, [0])

	def test_multiproduct_5_7(self):
		"""Test remove_product() on 5-node, 7-product system.
		"""
		print_status('TestAddRemoveProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		network.add_product(SupplyChainProduct(10))
		network.add_product(SupplyChainProduct(11))

		network.remove_product(network.products_by_index[10])

		self.assertSetEqual(set(network.product_indices), set([0, 1, 2, 3, 4, 5, 6, 11, -1001, -9, -7, -5, -3]))


class TestProductLists(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestProductLists', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestProductLists', 'tear_down_class()')

	def test_basic(self):
		"""Test product-only system.
		"""
		print_status('TestProductLists', 'test_basic()')

		network = SupplyChainNetwork()

		prod0 = SupplyChainProduct(0)
		prod1 = SupplyChainProduct(1)

		network.add_product(prod0)
		network.add_product(prod1)

		self.assertListEqual(network.products, [prod0, prod1])
		self.assertListEqual(network.product_indices, [0, 1])
		self.assertDictEqual(network.products_by_index, {0: prod0, 1: prod1})

	def test_multiproduct_5_7(self):
		"""Test 5-node, 7-product system.
		"""
		print_status('TestProductLists', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		network.add_product(SupplyChainProduct(10))
		network.add_product(SupplyChainProduct(11))
		products = {prod.index: prod for prod in network.products}

		self.assertCountEqual(network.product_indices, [0, 1, 2, 3, 4, 5, 6, 10, 11, -1001, -9, -7, -5, -3])
		self.assertListEqual(network.products, list(products.values()))
		self.assertDictEqual(network.products_by_index, {i: products[i] for i in products.keys()})
	

class TestReindexNodes(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestReindexNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestReindexNodes', 'tear_down_class()')

	def test_rosling_figure_1(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1.
		"""
		print_status('TestReindexNodes', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})

		for i in range(7):
			self.assertEqual(network.nodes[i].index, i+11)

	def test_rosling_figure_1_with_names(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1.
		"""
		print_status('TestReindexNodes', 'test_rosling_figure_1_with_names()')

		network = load_instance("rosling_figure_1")
		# Name the nodes "a"-"g".
		for i in range(1, 8):
			network.nodes_by_index[i].name = chr(97)

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17},
							  new_names={1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G"})

		for i in range(7):
			self.assertEqual(network.nodes[i].index, i+11)
			self.assertEqual(network.nodes[i].name, chr(65+i))

	def test_rosling_figure_1_with_state_vars_pre(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1 using
		simulation to test state variable reindexing that occurs before simulation.
		"""
		print_status('TestReindexNodes', 'test_rosling_figure_1_with_state_vars()')

		network = load_instance("rosling_figure_1")

		# Make the BS levels a little smaller so there are some stockouts.
		network.nodes_by_index[1].inventory_policy.base_stock_level = 6
		network.nodes_by_index[2].inventory_policy.base_stock_level = 20
		network.nodes_by_index[3].inventory_policy.base_stock_level = 35
		network.nodes_by_index[4].inventory_policy.base_stock_level = 58
		network.nodes_by_index[5].inventory_policy.base_stock_level = 45
		network.nodes_by_index[6].inventory_policy.base_stock_level = 65
		network.nodes_by_index[7].inventory_policy.base_stock_level = 75

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})
		nodes = {n.index: n for n in network.nodes}
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

		# Compare a few performance measures.
		self.assertEqual(nodes[11].state_vars[6].order_quantity[12][dps[12]], 4)
		self.assertEqual(nodes[11].state_vars[6].order_quantity[13][dps[13]], 4)
		self.assertEqual(nodes[12].state_vars[6].order_quantity[15][dps[15]], 4)
		self.assertEqual(nodes[13].state_vars[6].order_quantity[14][dps[14]], 4)
		self.assertEqual(nodes[14].state_vars[6].order_quantity[16][dps[16]], 0)
		self.assertEqual(nodes[14].state_vars[6].order_quantity[17][dps[17]], 0)
		self.assertEqual(nodes[11].state_vars[16].inventory_level[dps[11]], 3)
		self.assertEqual(nodes[12].state_vars[16].inventory_level[dps[12]], 7)
		self.assertEqual(nodes[13].state_vars[16].inventory_level[dps[13]], 4)
		self.assertEqual(nodes[14].state_vars[16].inventory_level[dps[14]], 9)
		self.assertEqual(nodes[15].state_vars[16].inventory_level[dps[15]], 7)
		self.assertEqual(nodes[16].state_vars[16].inventory_level[dps[16]], 19)
		self.assertEqual(nodes[17].state_vars[16].inventory_level[dps[17]], 24)
		self.assertEqual(nodes[11].state_vars[44].inventory_level[dps[11]], -4)
		self.assertEqual(nodes[12].state_vars[44].inventory_level[dps[12]], -5)
		self.assertEqual(nodes[13].state_vars[44].inventory_level[dps[13]], 0)
		self.assertEqual(nodes[14].state_vars[44].inventory_level[dps[14]], -2)
		self.assertEqual(nodes[15].state_vars[44].inventory_level[dps[15]], -6)
		self.assertEqual(nodes[16].state_vars[44].inventory_level[dps[16]], 0)
		self.assertEqual(nodes[17].state_vars[44].inventory_level[dps[17]], 10)
		self.assertEqual(nodes[11].state_vars[16].inbound_shipment[12][dps[12]], 2)
		self.assertEqual(nodes[11].state_vars[16].inbound_shipment[13][dps[13]], 2)
		self.assertEqual(nodes[12].state_vars[16].inbound_shipment[15][dps[15]], 1)
		self.assertEqual(nodes[13].state_vars[16].inbound_shipment[14][dps[14]], 0)
		self.assertEqual(nodes[14].state_vars[16].inbound_shipment[16][dps[16]], 12)
		self.assertEqual(nodes[14].state_vars[16].inbound_shipment[17][dps[17]], 12)
		self.assertEqual(nodes[15].state_vars[16].inbound_shipment[None][nodes[15]._external_supplier_dummy_product.index], 9)
		self.assertEqual(nodes[16].state_vars[16].inbound_shipment[None][nodes[16]._external_supplier_dummy_product.index], 13)
		self.assertEqual(nodes[17].state_vars[16].inbound_shipment[None][nodes[17]._external_supplier_dummy_product.index], 12)
		self.assertEqual(nodes[11].state_vars[45].raw_material_inventory[dps[12]], 0)
		self.assertEqual(nodes[11].state_vars[45].raw_material_inventory[dps[13]], 5)
		self.assertEqual(nodes[12].state_vars[45].raw_material_inventory[dps[15]], 0)
		self.assertEqual(nodes[14].state_vars[45].raw_material_inventory[dps[16]], 0)

	def test_rosling_figure_1_with_state_vars_post(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1 using
		simulation to test state variable reindexing that occurs after simulation.
		"""
		print_status('TestReindexNodes', 'test_rosling_figure_1_with_state_vars()')

		network = load_instance("rosling_figure_1")
		# Make the BS levels a little smaller so there are some stockouts.
		network.nodes_by_index[1].inventory_policy.base_stock_level = 6
		network.nodes_by_index[2].inventory_policy.base_stock_level = 20
		network.nodes_by_index[3].inventory_policy.base_stock_level = 35
		network.nodes_by_index[4].inventory_policy.base_stock_level = 58
		network.nodes_by_index[5].inventory_policy.base_stock_level = 45
		network.nodes_by_index[6].inventory_policy.base_stock_level = 65
		network.nodes_by_index[7].inventory_policy.base_stock_level = 75

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})
		nodes = {n.index: n for n in network.nodes}
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		# Compare a few performance measures.
		self.assertEqual(nodes[11].state_vars[6].order_quantity[12][dps[12]], 4)
		self.assertEqual(nodes[11].state_vars[6].order_quantity[13][dps[13]], 4)
		self.assertEqual(nodes[12].state_vars[6].order_quantity[15][dps[15]], 4)
		self.assertEqual(nodes[13].state_vars[6].order_quantity[14][dps[14]], 4)
		self.assertEqual(nodes[14].state_vars[6].order_quantity[16][dps[16]], 0)
		self.assertEqual(nodes[14].state_vars[6].order_quantity[17][dps[17]], 0)
		self.assertEqual(nodes[11].state_vars[16].inventory_level[dps[11]], 3)
		self.assertEqual(nodes[12].state_vars[16].inventory_level[dps[12]], 7)
		self.assertEqual(nodes[13].state_vars[16].inventory_level[dps[13]], 4)
		self.assertEqual(nodes[14].state_vars[16].inventory_level[dps[14]], 9)
		self.assertEqual(nodes[15].state_vars[16].inventory_level[dps[15]], 7)
		self.assertEqual(nodes[16].state_vars[16].inventory_level[dps[16]], 19)
		self.assertEqual(nodes[17].state_vars[16].inventory_level[dps[17]], 24)
		self.assertEqual(nodes[11].state_vars[44].inventory_level[dps[11]], -4)
		self.assertEqual(nodes[12].state_vars[44].inventory_level[dps[12]], -5)
		self.assertEqual(nodes[13].state_vars[44].inventory_level[dps[13]], 0)
		self.assertEqual(nodes[14].state_vars[44].inventory_level[dps[14]], -2)
		self.assertEqual(nodes[15].state_vars[44].inventory_level[dps[15]], -6)
		self.assertEqual(nodes[16].state_vars[44].inventory_level[dps[16]], 0)
		self.assertEqual(nodes[17].state_vars[44].inventory_level[dps[17]], 10)
		self.assertEqual(nodes[11].state_vars[16].inbound_shipment[12][dps[12]], 2)
		self.assertEqual(nodes[11].state_vars[16].inbound_shipment[13][dps[13]], 2)
		self.assertEqual(nodes[12].state_vars[16].inbound_shipment[15][dps[15]], 1)
		self.assertEqual(nodes[13].state_vars[16].inbound_shipment[14][dps[14]], 0)
		self.assertEqual(nodes[14].state_vars[16].inbound_shipment[16][dps[16]], 12)
		self.assertEqual(nodes[14].state_vars[16].inbound_shipment[17][dps[17]], 12)
		self.assertEqual(nodes[15].state_vars[16].inbound_shipment[None][nodes[15]._external_supplier_dummy_product.index], 9)
		self.assertEqual(nodes[16].state_vars[16].inbound_shipment[None][nodes[16]._external_supplier_dummy_product.index], 13)
		self.assertEqual(nodes[17].state_vars[16].inbound_shipment[None][nodes[17]._external_supplier_dummy_product.index], 12)
		self.assertEqual(nodes[11].state_vars[45].raw_material_inventory[dps[12]], 0)
		self.assertEqual(nodes[11].state_vars[45].raw_material_inventory[dps[13]], 5)
		self.assertEqual(nodes[12].state_vars[45].raw_material_inventory[dps[15]], 0)
		self.assertEqual(nodes[14].state_vars[45].raw_material_inventory[dps[16]], 0)


class TestSingleStageNetwork(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSingleStageNetwork', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSingleStageNetwork', 'tear_down_class()')

	def test_example_4_1(self):
		"""Test single_stage_network() to build system in Example 4.1.
		"""
		print_status('TestSingleStageNetwork', 'test_example_4_1()')

		network = single_stage_system(holding_cost=0.18,
							    stockout_cost=0.70,
								demand_type='N',
								mean=50, standard_deviation=8,
								policy_type='BS',
								base_stock_level=56.6)

		node = network.nodes[0]
		self.assertEqual(node.holding_cost, 0.18)
		self.assertEqual(node.stockout_cost, 0.70)
		self.assertEqual(node.demand_source.mean, 50)
		self.assertEqual(node.demand_source.standard_deviation, 8)
		self.assertEqual(node.inventory_policy.base_stock_level, 56.6)


class TestSerialSystem(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSerialSystem', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSerialSystem', 'tear_down_class()')
		
	def test_3_node_serial_downstream_0(self):
		"""Test serial_system_new() to build 3-node serial system, indexed 0,...,2
		with downstream node = 0.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_downstream_0()')

		network = serial_system(
			3,
			node_order_in_system=[2, 1, 0],
			node_order_in_lists=[0, 1, 2],
			local_holding_cost=[7, 4, 2],
			demand_type='N',
			mean=10,
			standard_deviation=2,
			policy_type='BS',
			base_stock_level=5
		)

		# Get nodes, in order from upstream to downstream.
		source_node = network.source_nodes[0]
		middle_node = source_node.successors()[0]
		sink_node = middle_node.successors()[0]

		# Get successors and predecessors.
		source_node_succ = source_node.successor_indices()
		middle_node_succ = middle_node.successor_indices()
		sink_node_succ = sink_node.successor_indices()
		source_node_pred = source_node.predecessor_indices()
		middle_node_pred = middle_node.predecessor_indices()
		sink_node_pred = sink_node.predecessor_indices()

		self.assertEqual(source_node.index, 2)
		self.assertEqual(middle_node.index, 1)
		self.assertEqual(sink_node.index, 0)

		self.assertEqual(source_node_succ, [1])
		self.assertEqual(middle_node_succ, [0])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [2])
		self.assertEqual(sink_node_pred, [1])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

	def test_3_node_serial_node_order_in_system(self):
		"""Test serial_system() to build 3-node serial system, with node_order_in_system
		provided.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_node_order_in_system()')

		network = serial_system(
			3,
			node_order_in_system=[12, 14, 17],
			local_holding_cost=[2, 4, 7],
			demand_type='N',
			mean=10,
			standard_deviation=2,
			policy_type='BS',
			base_stock_level=5			
		)

		# Get nodes, in order from upstream to downstream.
		source_node = network.source_nodes[0]
		middle_node = source_node.successors()[0]
		sink_node = middle_node.successors()[0]

		# Get successors and predecessors.
		source_node_succ = source_node.successor_indices()
		middle_node_succ = middle_node.successor_indices()
		sink_node_succ = sink_node.successor_indices()
		source_node_pred = source_node.predecessor_indices()
		middle_node_pred = middle_node.predecessor_indices()
		sink_node_pred = sink_node.predecessor_indices()

		self.assertEqual(source_node.index, 12)
		self.assertEqual(middle_node.index, 14)
		self.assertEqual(sink_node.index, 17)

		self.assertEqual(source_node_succ, [14])
		self.assertEqual(middle_node_succ, [17])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [12])
		self.assertEqual(sink_node_pred, [14])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

	def test_3_node_serial_node_order_in_system_node_order_in_lists(self):
		"""Test serial_system() to build 3-node serial system, with node_order_in_system
		and node_order_in_lists provided.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_node_order_in_system_node_order_in_lists()')

		network = serial_system(
			3,
			node_order_in_system=[12, 14, 17],
			node_order_in_lists=[14, 12, 17],
			local_holding_cost=[4, 2, 7],
			demand_type='N',
			mean=10,
			standard_deviation=2,
			policy_type='BS',
			base_stock_level=5			
		)

		# Get nodes, in order from upstream to downstream.
		source_node = network.source_nodes[0]
		middle_node = source_node.successors()[0]
		sink_node = middle_node.successors()[0]

		# Get successors and predecessors.
		source_node_succ = source_node.successor_indices()
		middle_node_succ = middle_node.successor_indices()
		sink_node_succ = sink_node.successor_indices()
		source_node_pred = source_node.predecessor_indices()
		middle_node_pred = middle_node.predecessor_indices()
		sink_node_pred = sink_node.predecessor_indices()

		self.assertEqual(source_node.index, 12)
		self.assertEqual(middle_node.index, 14)
		self.assertEqual(sink_node.index, 17)

		self.assertEqual(source_node_succ, [14])
		self.assertEqual(middle_node_succ, [17])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [12])
		self.assertEqual(sink_node_pred, [14])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestNetworkFromEdges.test_3_node_serial_list_params skipped because test fails for now; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_3_node_serial_list_params(self):
		"""Test serial_system_new() to build 3-node serial system, indexed 0,...,2
		with downstream node = 0, with 'CD' demand (which requires parameters that are
		passed as lists).
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_list_params()')

		network = serial_system(
			3,
			node_order_in_system=[2, 1, 0],
			node_order_in_lists=[0, 1, 2],
			local_holding_cost=[7, 4, 2],
			demand_type='CD',
			demand_list=[0, 1, 2, 3],
			probabilities=[0.25, 0.25, 0.4, 0.1],
			policy_type='BS',
			base_stock_level=5
		)

		# Get nodes, in order from upstream to downstream.
		source_node = network.source_nodes[0]
		middle_node = source_node.successors()[0]
		sink_node = middle_node.successors()[0]

		# Get successors and predecessors.
		source_node_succ = source_node.successor_indices()
		middle_node_succ = middle_node.successor_indices()
		sink_node_succ = sink_node.successor_indices()
		source_node_pred = source_node.predecessor_indices()
		middle_node_pred = middle_node.predecessor_indices()
		sink_node_pred = sink_node.predecessor_indices()

		self.assertEqual(source_node.index, 2)
		self.assertEqual(middle_node.index, 1)
		self.assertEqual(sink_node.index, 0)

		self.assertEqual(source_node_succ, [1])
		self.assertEqual(middle_node_succ, [0])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [2])
		self.assertEqual(sink_node_pred, [1])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

		correct_ds = DemandSource(type='CD', demand_list=[0, 1, 2, 3], probabilities=[0.25, 0.25, 0.4, 0.1])
		self.assertEqual(sink_node.demand_source, correct_ds)



class TestNetworkFromEdges(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNetworkFromEdges', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNetworkFromEdges', 'tear_down_class()')

	def get_correct_network(self):
		# Correct network for tests.
		correct_network = SupplyChainNetwork()
		node3 = SupplyChainNode(
			index=3,
			local_holding_cost=2, 
			inventory_policy=Policy(type='BS', base_stock_level=100),
			shipment_lead_time=0,
			supply_type='U'
		)
		correct_network.add_node(node3)
		node1 = SupplyChainNode(
			index=1, 
			local_holding_cost=4, 
			stockout_cost=20, 
			demand_source=DemandSource(type='N', mean=50, standard_deviation=5),
			inventory_policy=Policy(type='BS', base_stock_level=70),
			shipment_lead_time=2
		)
		correct_network.add_successor(node3, node1)
		node2 = SupplyChainNode(
			index=2, 
			local_holding_cost=7, 
			stockout_cost=50, 
			demand_source=DemandSource(type='N', mean=20, standard_deviation=3),
			inventory_policy=Policy(type='BS', base_stock_level=25),
			shipment_lead_time=6
		)
		correct_network.add_successor(node3, node2)
		node4 = SupplyChainNode(
			index=4,
			local_holding_cost=1, 
			inventory_policy=Policy(type='rQ', reorder_point=20, order_quantity=60),
			shipment_lead_time=1,
			supply_type='U'
		)
		correct_network.add_predecessor(node1, node4)
		for n in correct_network.nodes:
			n.inventory_policy.node = n

		return correct_network

	def test_4_node_1(self):
		"""Test that network_from_edges() correctly builds the network defined in
		get_correct_network() when built using all lists.
		"""
		print_status('TestNetworkFromEdges', 'test_4_node_1()')

		# Correct network.
		correct_network = self.get_correct_network()

		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_source=[
				DemandSource(type='N', mean=50, standard_deviation=5),
				DemandSource(type='N', mean=20, standard_deviation=3),
				None, None
			],
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))

	def test_4_node_2(self):
		"""Similar to test 1, but no node_indices provided.
		"""
		print_status('TestNetworkFromEdges', 'test_4_node_2()')

		# Correct network.
		correct_network = self.get_correct_network()

		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_source=[
				DemandSource(type='N', mean=50, standard_deviation=5),
				DemandSource(type='N', mean=20, standard_deviation=3),
				None, None
			],
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))
		
	def test_4_node_3(self):
		"""Similar to test 1, but with out-of-order index list.
		"""
		print_status('TestNetworkFromEdges', 'test_4_node_3()')

		# Correct network.
		correct_network = self.get_correct_network()

		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[3, 1, 2, 4],
			local_holding_cost=[2, 4, 7, 1],
			stockout_cost=[None, 20, 50, None],
			demand_source=[
				None, 
				DemandSource(type='N', mean=50, standard_deviation=5),
				DemandSource(type='N', mean=20, standard_deviation=3),
				None
			],
			inventory_policy=[
				Policy(type='BS', base_stock_level=100),
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[0, 2, 6, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))

	def test_4_node_4(self):
		"""Similar to test 1, but with various ways of providing data. Also add
		a new attribute to test singleton.
		"""
		print_status('TestNetworkFromEdges', 'test_4_node_4()')

		# Correct network.
		correct_network = self.get_correct_network()
		for n in correct_network.nodes:
			n.order_lead_time = 5 # to test singleton below

		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[3, 1, 2, 4],
			local_holding_cost=[2, 4, 7, 1],
			stockout_cost={3: None, 1: 20, 2: 50, 4: None},
			demand_source={
				1: DemandSource(type='N', mean=50, standard_deviation=5),
				2: None,
				3: None, 
				4: None
			},
			demand_type={2: 'N'},
			mean={2: 20},
			standard_deviation={2: 3},
			inventory_policy=[
				Policy(type='BS', base_stock_level=100),
				Policy(type='BS', base_stock_level=70),
				None,
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			policy_type='BS', # superceded by Policy for nodes 1, 3, 4
			base_stock_level=25,
			shipment_lead_time=[0, 2, 6, 1],
			order_lead_time=5
		)
		# for n in network.nodes:
		# 	if n.inventory_policy is not None:
		# 		n.inventory_policy.node = n
		self.assertTrue(network.deep_equal_to(correct_network))

	def test_demand_source(self):
		"""Test different ways to specify demand_source.
		"""
		print_status('TestNetworkFromEdges', 'test_demand_source()')

		# Correct network.
		correct_network = self.get_correct_network()

		# Specify type as singleton, other attributes as list.
		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_type='N',
			mean=[50, 20, None, None],
			standard_deviation=[5, 3, None, None],
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))

		# Specify type as singleton, other attributes as dict.
		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_type='N',
			mean={1: 50, 2: 20},
			standard_deviation={1: 5, 2: 3},
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))

		# Specify type and other attributes as singleton.
		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_type='N',
			mean=50,
			standard_deviation=5,
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		# Change correct_network to account for same means/SDs.
		correct_network.nodes_by_index[2].demand_source.mean = 50
		correct_network.nodes_by_index[2].demand_source.standard_deviation = 5
		self.assertTrue(network.deep_equal_to(correct_network))

	def test_single_node(self):
		"""Test network_from_edges() for building a single-node network.
		"""
		print_status('TestNetworkFromEdges', 'test_single_node()')

		# Correct network.
		node = SupplyChainNode(
			index=0,
			local_holding_cost=2,
			stockout_cost=20,
			demand_source=DemandSource(type='N', mean=10, standard_deviation=1),
			supply_type='U'
		)
		correct_network = SupplyChainNetwork()
		correct_network.add_node(node)

		network = network_from_edges(
			edges=[],
			local_holding_cost=2,
			stockout_cost=20,
			demand_type='N',
			mean=10,
			standard_deviation=1
		)
		self.assertTrue(network.deep_equal_to(correct_network))

		# Change index.
		correct_network.nodes[0].index = 7
		network = network_from_edges(
			edges=[],
			node_order_in_lists=[7],
			local_holding_cost=2,
			stockout_cost=20,
			demand_type='N',
			mean=10,
			standard_deviation=1
		)
		self.assertTrue(network.deep_equal_to(correct_network))

	def test_list_params(self):
		"""Test that network_from_edges() correctly builds the network defined in
		get_correct_network() when built using all lists.
		"""
		# Correct network.
		correct_network = self.get_correct_network()
		correct_network.nodes_by_index[1].demand_source = DemandSource(
			type='CD',
			demand_list=[0, 1, 2, 3],
			probabilities=[0.25, 0.25, 0.4, 0.1]
		)
		correct_network.nodes_by_index[2].demand_source = DemandSource(
			type='CD',
			demand_list=[0, 1, 2, 3],
			probabilities=[0.25, 0.25, 0.4, 0.1]
		)
		correct_network.nodes_by_index[3].demand_source = DemandSource(type=None)
		correct_network.nodes_by_index[4].demand_source = DemandSource(type=None)

		network = network_from_edges(
			edges=[(3, 1), (3, 2), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[4, 7, 2, 1],
			stockout_cost=[20, 50, None, None],
			demand_type='CD',
			demand_list=[[0, 1, 2, 3], [0, 1, 2, 3], None, None],
			probabilities=[[0.25, 0.25, 0.4, 0.1], [0.25, 0.25, 0.4, 0.1], None, None],
			inventory_policy=[
				Policy(type='BS', base_stock_level=70),
				Policy(type='BS', base_stock_level=25),
				Policy(type='BS', base_stock_level=100),
				Policy(type='rQ', reorder_point=20, order_quantity=60),
			],
			shipment_lead_time=[2, 6, 0, 1]
		)
		self.assertTrue(network.deep_equal_to(correct_network))

class TestMWORSystem(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMWORSystem', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMWORSystem', 'tear_down_class()')

	def test_4_node_mwor_downstream_0(self):
		"""Test mwor_system() to build 4-node MWOR system, indexed
		with downstream node = 0.
		"""
		print_status('TestMWORSystem', 'test_4_node_mwor_downstream_0()')

		network = mwor_system(3, node_order_in_lists=[0, 1, 2, 3],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		wh1 = network.source_nodes[0]
		wh2 = network.source_nodes[1]
		wh3 = network.source_nodes[2]
		ret = network.sink_nodes[0]

		# Get successors and predecessors.
		ret_succ = ret.successor_indices()
		wh1_succ = wh1.successor_indices()
		wh2_succ = wh2.successor_indices()
		wh3_succ = wh3.successor_indices()
		ret_pred = ret.predecessor_indices()
		wh1_pred = wh1.predecessor_indices()
		wh2_pred = wh2.predecessor_indices()
		wh3_pred = wh3.predecessor_indices()

		self.assertEqual(ret.index, 0)
		self.assertEqual(wh1.index, 1)
		self.assertEqual(wh2.index, 2)
		self.assertEqual(wh3.index, 3)

		self.assertEqual(ret_succ, [])
		self.assertEqual(wh1_succ, [0])
		self.assertEqual(wh2_succ, [0])
		self.assertEqual(wh3_succ, [0])
		self.assertEqual(ret_pred, [1, 2, 3])
		self.assertEqual(wh1_pred, [])
		self.assertEqual(wh2_pred, [])
		self.assertEqual(wh3_pred, [])

		self.assertEqual(ret.local_holding_cost, 5)
		self.assertEqual(wh1.local_holding_cost, 1)
		self.assertEqual(wh2.local_holding_cost, 1)
		self.assertEqual(wh3.local_holding_cost, 2)

	def test_4_node_mwor_downstream_3(self):
		"""Test mwor_system() to build 4-node MWOR system, indexed
		with downstream node = 3.
		"""
		print_status('TestMWORSystem', 'test_4_node_mwor_downstream_3()')

		network = mwor_system(3, node_order_in_system=[0, 1, 2, 3],
								node_order_in_lists=[3, 2, 1, 0],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		wh1 = network.source_nodes[2]
		wh2 = network.source_nodes[1]
		wh3 = network.source_nodes[0]
		ret = network.sink_nodes[0]

		# Get successors and predecessors.
		ret_succ = ret.successor_indices()
		wh1_succ = wh1.successor_indices()
		wh2_succ = wh2.successor_indices()
		wh3_succ = wh3.successor_indices()
		ret_pred = ret.predecessor_indices()
		wh1_pred = wh1.predecessor_indices()
		wh2_pred = wh2.predecessor_indices()
		wh3_pred = wh3.predecessor_indices()

		self.assertEqual(ret.index, 3)
		self.assertEqual(wh1.index, 2)
		self.assertEqual(wh2.index, 1)
		self.assertEqual(wh3.index, 0)

		self.assertEqual(ret_succ, [])
		self.assertEqual(wh1_succ, [3])
		self.assertEqual(wh2_succ, [3])
		self.assertEqual(wh3_succ, [3])
		self.assertEqual(ret_pred, [0, 1, 2])
		self.assertEqual(wh1_pred, [])
		self.assertEqual(wh2_pred, [])
		self.assertEqual(wh3_pred, [])

		self.assertEqual(ret.local_holding_cost, 5)
		self.assertEqual(wh1.local_holding_cost, 1)
		self.assertEqual(wh2.local_holding_cost, 1)
		self.assertEqual(wh3.local_holding_cost, 2)

	def test_4_node_mwor_index_list(self):
		"""Test mwor_system() to build 4-node MWOR system, with index list
		given explicitly
		"""
		print_status('TestMWORSystem', 'test_4_node_mwor_index_list()')

		network = mwor_system(3, node_order_in_system=[5, 12, 14, 17],
								node_order_in_lists=[17, 5, 14, 12],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		wh1 = network.source_nodes[0]
		wh2 = network.source_nodes[1]
		wh3 = network.source_nodes[2]
		ret = network.sink_nodes[0]

		# Get successors and predecessors.
		ret_succ = ret.successor_indices()
		wh1_succ = wh1.successor_indices()
		wh2_succ = wh2.successor_indices()
		wh3_succ = wh3.successor_indices()
		ret_pred = ret.predecessor_indices()
		wh1_pred = wh1.predecessor_indices()
		wh2_pred = wh2.predecessor_indices()
		wh3_pred = wh3.predecessor_indices()

		self.assertEqual(ret.index, 17)
		self.assertEqual(wh1.index, 5)
		self.assertEqual(wh2.index, 12)
		self.assertEqual(wh3.index, 14)

		self.assertEqual(ret_succ, [])
		self.assertEqual(wh1_succ, [17])
		self.assertEqual(wh2_succ, [17])
		self.assertEqual(wh3_succ, [17])
		self.assertEqual(ret_pred, [5, 12, 14])
		self.assertEqual(wh1_pred, [])
		self.assertEqual(wh2_pred, [])
		self.assertEqual(wh3_pred, [])

		self.assertEqual(ret.local_holding_cost, 5)
		self.assertEqual(wh1.local_holding_cost, 1)
		self.assertEqual(wh2.local_holding_cost, 2)
		self.assertEqual(wh3.local_holding_cost, 1)

	def test_145(self):
		"""Test instance in issue #165 (mwor_system() fails when setting demand_source).
		"""
		print_status('TestReindexNodes', 'test_145()')

		network = mwor_system(3, demand_source=DemandSource(type='P', mean=5))

		self.assertIsInstance(network.nodes_by_index[0].demand_source, DemandSource)
		self.assertEqual(network.nodes_by_index[0].demand_source.type, 'P')
		self.assertEqual(network.nodes_by_index[0].demand_source.mean, 5)
		for n in range(1, 4):
			self.assertIsInstance(network.nodes_by_index[n].demand_source, DemandSource)
			self.assertIsNone(network.nodes_by_index[n].demand_source.type)


class TestOWMRSystem(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestOWMRSystem', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestOWMRSystem', 'tear_down_class()')

	def test_4_node_owmr_downstream_0(self):
		"""Test owmr_system() to build 4-node owmr system, indexed
		with warehouse node = 0.
		"""
		print_status('TestOWMRSystem', 'test_4_node_owmr_downstream_0()')

		network = owmr_system(3, local_holding_cost=[2, 1, 1, 5],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		ret1 = network.sink_nodes[0]
		ret2 = network.sink_nodes[1]
		ret3 = network.sink_nodes[2]
		wh = network.source_nodes[0]

		# Get successors and predecessors.
		wh_succ = wh.successor_indices()
		ret1_succ = ret1.successor_indices()
		ret2_succ = ret2.successor_indices()
		ret3_succ = ret3.successor_indices()
		wh_pred = wh.predecessor_indices()
		ret1_pred = ret1.predecessor_indices()
		ret2_pred = ret2.predecessor_indices()
		ret3_pred = ret3.predecessor_indices()

		self.assertEqual(wh.index, 0)
		self.assertEqual(ret1.index, 1)
		self.assertEqual(ret2.index, 2)
		self.assertEqual(ret3.index, 3)

		self.assertEqual(wh_succ, [1, 2, 3])
		self.assertEqual(ret1_succ, [])
		self.assertEqual(ret2_succ, [])
		self.assertEqual(ret3_succ, [])
		self.assertEqual(wh_pred, [])
		self.assertEqual(ret1_pred, [0])
		self.assertEqual(ret2_pred, [0])
		self.assertEqual(ret3_pred, [0])

		self.assertEqual(wh.local_holding_cost, 2)
		self.assertEqual(ret1.local_holding_cost, 1)
		self.assertEqual(ret2.local_holding_cost, 1)
		self.assertEqual(ret3.local_holding_cost, 5)

	def test_4_node_owmr_downstream_3(self):
		"""Test owmr_system() to build 4-node owmr system, indexed
		with warehouse node = 3.
		"""
		print_status('TestOWMRSystem', 'test_4_node_owmr_downstream_3()')

		network = owmr_system(3, node_order_in_system=[3, 0, 1, 2],
								local_holding_cost=[2, 1, 1, 5],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		ret1 = network.sink_nodes[0]
		ret2 = network.sink_nodes[1]
		ret3 = network.sink_nodes[2]
		wh = network.source_nodes[0]

		# Get successors and predecessors.
		wh_succ = wh.successor_indices()
		ret1_succ = ret1.successor_indices()
		ret2_succ = ret2.successor_indices()
		ret3_succ = ret3.successor_indices()
		wh_pred = wh.predecessor_indices()
		ret1_pred = ret1.predecessor_indices()
		ret2_pred = ret2.predecessor_indices()
		ret3_pred = ret3.predecessor_indices()

		self.assertEqual(wh.index, 3)
		self.assertEqual(ret1.index, 0)
		self.assertEqual(ret2.index, 1)
		self.assertEqual(ret3.index, 2)

		self.assertEqual(wh_succ, [0, 1, 2])
		self.assertEqual(ret1_succ, [])
		self.assertEqual(ret2_succ, [])
		self.assertEqual(ret3_succ, [])
		self.assertEqual(wh_pred, [])
		self.assertEqual(ret1_pred, [3])
		self.assertEqual(ret2_pred, [3])
		self.assertEqual(ret3_pred, [3])

		self.assertEqual(wh.local_holding_cost, 2)
		self.assertEqual(ret1.local_holding_cost, 1)
		self.assertEqual(ret2.local_holding_cost, 1)
		self.assertEqual(ret3.local_holding_cost, 5)

	def test_4_node_owmr_index_list(self):
		"""Test owmr_system() to build 4-node owmr system, with index list
		given explicitly
		"""
		print_status('TestOWMRSystem', 'test_4_node_owmr_index_list()')

		network = owmr_system(3, node_order_in_system=[5, 12, 14, 17],
								node_order_in_lists=[17, 5, 14, 12],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Get nodes.
		ret1 = network.sink_nodes[0]
		ret2 = network.sink_nodes[1]
		ret3 = network.sink_nodes[2]
		wh = network.source_nodes[0]

		# Get successors and predecessors.
		wh_succ = wh.successor_indices()
		ret1_succ = ret1.successor_indices()
		ret2_succ = ret2.successor_indices()
		ret3_succ = ret3.successor_indices()
		wh_pred = wh.predecessor_indices()
		ret1_pred = ret1.predecessor_indices()
		ret2_pred = ret2.predecessor_indices()
		ret3_pred = ret3.predecessor_indices()

		self.assertEqual(wh.index, 5)
		self.assertEqual(ret1.index, 12)
		self.assertEqual(ret2.index, 14)
		self.assertEqual(ret3.index, 17)

		self.assertEqual(wh_succ, [12, 14, 17])
		self.assertEqual(ret1_succ, [])
		self.assertEqual(ret2_succ, [])
		self.assertEqual(ret3_succ, [])
		self.assertEqual(wh_pred, [])
		self.assertEqual(ret1_pred, [5])
		self.assertEqual(ret2_pred, [5])
		self.assertEqual(ret3_pred, [5])

		self.assertEqual(wh.local_holding_cost, 1)
		self.assertEqual(ret1.local_holding_cost, 2)
		self.assertEqual(ret2.local_holding_cost, 1)
		self.assertEqual(ret3.local_holding_cost, 5)


class TestNetworkxDigraph(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNetworkxDigraph', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNetworkxDigraph', 'tear_down_class()')

	def test_3_node_serial(self):
		"""Test networkx_digraph() for 3-node serial system.
		"""
		print_status('TestNetworkxDigraph', 'test_3_node_serial()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)

		network.add_node(node2)
		network.add_successor(node2, node1)
		network.add_successor(node1, node0)

		digraph = network.networkx_digraph()

		self.assertEqual(list(digraph.nodes), [2, 1, 0])
		self.assertEqual(list(digraph.edges), [(2, 1), (1, 0)])

	def test_4_node_owmr(self):
		"""Test networkx_digraph() for 4-node OWMR system.
		"""
		print_status('TestNetworkxDigraph', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		node0 = SupplyChainNode(0)
		node1 = SupplyChainNode(1)
		node2 = SupplyChainNode(2)
		node3 = SupplyChainNode(3)

		network.add_node(node0)
		network.add_successor(node0, node1)
		network.add_successor(node0, node2)
		network.add_successor(node0, node3)

		digraph = network.networkx_digraph()

		self.assertEqual(set(digraph.nodes), {3, 2, 1, 0})
		self.assertEqual(set(digraph.edges), {(0, 3), (0, 2), (0, 1)})


class TestLocalToEchelonBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLocalToEchelonBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLocalToEchelonBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that local_to_echelon_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestLocalToEchelonBaseStockLevels', 'test_example_6_1()')

		instance = load_instance("example_6_1") # 3 -> 2 -> 1

		S_local = {3: 10, 2: 6, 1: 6}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {3: 22, 2: 12, 1: 6})

		S_local = {1: 4, 2: 5, 3: 1}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 4, 2: 9, 3: 10})

		S_local = {1: 10, 2: 0, 3: 2}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 10, 2: 10, 3: 12})

		S_local = {1: 3, 2: -4, 3: 5}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 3, 2: -1, 3: 4})

	def test_example_6_1_renumbered(self):
		"""Test that local_to_echelon_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1 with 
		renumbered nodes.
		"""

		print_status('TestLocalToEchelonBaseStockLevels', 'test_example_6_1_renumbered()')

		instance = load_instance("example_6_1")
		instance.reindex_nodes({3: 1, 2: 2, 1: 3}) # now 1 -> 2 -> 3

		S_local = {1: 10, 2: 6, 3: 6}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 22, 2: 12, 3: 6})

		S_local = {3: 4, 2: 5, 1: 1}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {3: 4, 2: 9, 1: 10})

		S_local = {3: 10, 2: 0, 1: 2}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {3: 10, 2: 10, 1: 12})

		S_local = {3: 3, 2: -4, 1: 5}
		S_echelon = local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {3: 3, 2: -1, 1: 4})


class TestEchelonToLocalBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEchelonToLocalBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEchelonToLocalBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that echelon_to_local_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestEchelonToLocalBaseStockLevels', 'test_example_6_1()')

		instance = load_instance("example_6_1") # 3 -> 2 -> 1

		S_echelon = {3: 22, 2: 12, 1: 6}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {3: 10, 2: 6, 1: 6})

		S_echelon = {1: 4, 2: 9, 3: 10}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 4, 2: 5, 3: 1})

		S_echelon = {1: 10, 2: 10, 3: 12}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 10, 2: 0, 3: 2})

		S_echelon = {1: 3, 2: -1, 3: 4}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: -1, 2: 0, 3: 5})

		S_echelon = {1: 10, 2: 15, 3: 5}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 5, 2: 0, 3: 0})

	def test_example_6_1_renumbered(self):
		"""Test that echelon_to_local_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1 with 
		renumbered nodes.
		"""

		print_status('TestEchelonToLocalBaseStockLevels', 'test_example_6_1_renumbered()')

		instance = load_instance("example_6_1")
		instance.reindex_nodes({3: 1, 2: 2, 1: 3}) # now 1 -> 2 -> 3

		S_echelon = {1: 22, 2: 12, 3: 6}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 10, 2: 6, 3: 6})

		S_echelon = {3: 4, 2: 9, 1: 10}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {3: 4, 2: 5, 1: 1})

		S_echelon = {3: 10, 2: 10, 1: 12}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {3: 10, 2: 0, 1: 2})

		S_echelon = {3: 3, 2: -1, 1: 4}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {3: -1, 2: 0, 1: 5})

		S_echelon = {3: 10, 2: 15, 1: 5}
		S_local = echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {3: 5, 2: 0, 1: 0})


class TestToFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestToFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestToFromDict', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNetwork object to and from dict
		in Example 6.1.
		"""
		print_status('TestToFromDict', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Convert network to dict.
		network_dict = network.to_dict()

		# Convert dict back to network.
		dict_network = SupplyChainNetwork.from_dict(network_dict)

		# Compare.
		self.assertTrue(network.deep_equal_to(dict_network))

	def test_assembly_3_stage(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNetwork object to and from dict
		in 3-stage assembly system.
		"""
		print_status('TestToFromDict', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")

		# Convert network to dict.
		network_dict = network.to_dict()

		# Convert dict back to network.
		dict_network = SupplyChainNetwork.from_dict(network_dict)

		# Compare.
		self.assertTrue(network.deep_equal_to(dict_network))

	def test_multiproduct_5_7(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNetwork object to and from dict
		in 5-node, 7-product system.
		"""
		print_status('TestToFromDict', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		# Convert network to dict.
		network_dict = network.to_dict()

		# Convert dict back to network.
		dict_network = SupplyChainNetwork.from_dict(network_dict)

		# Compare.
		self.assertTrue(network.deep_equal_to(dict_network))

	def test_example_6_1_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNetwork object to and from dict
		in Example 6.1 per 22.
		"""
		print_status('TestToFromDict', 'test_example_6_1_per_22()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, convert nodes
		# to dict and back, compare to original.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Convert network to dict.
		network_dict = network.to_dict()

		# Convert dict back to network.
		dict_network = SupplyChainNetwork.from_dict(network_dict)

		# Compare.
		self.assertTrue(network.deep_equal_to(dict_network))

	def test_assembly_3_stage_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNetwork object to and from dict
		in 3-stage assembly system.
		"""
		print_status('TestToFromDict', 'test_assembly_3_stage_per_22()')

		network = load_instance("assembly_3_stage")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, convert nodes
		# to dict and back, compare to original.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Convert network to dict.
		network_dict = network.to_dict()

		# Convert dict back to network.
		dict_network = SupplyChainNetwork.from_dict(network_dict)

		# Compare.
		self.assertTrue(network.deep_equal_to(dict_network))

	def test_missing_values(self):
		"""Test that from_dict() correctly fills attributes with defaults if missing.
		"""
		print_status('TestToFromDict', 'test_missing_values()')

		# This instance is missing the ``period`` attribute.
		network1 = load_instance("missing_period", "tests/additional_files/test_supply_chain_network_TestToFromDict_data.json")
		network2 = load_instance("example_6_1")
		network2.period = SupplyChainNetwork._DEFAULT_VALUES['_period']
		self.assertTrue(network1.deep_equal_to(network2))

		# This instance is missing the ``nodes`` attribute.
		network1 = load_instance("missing_nodes", "tests/additional_files/test_supply_chain_network_TestToFromDict_data.json")
		network2 = load_instance("example_6_1")
		while len(network2.nodes) > 0:
			network2.remove_node(network2.nodes[0])
		self.assertTrue(network1.deep_equal_to(network2))

		# In this instance, node 3 is missing the ``local_holding_cost`` attribute.
		network1 = load_instance("missing_local_holding_cost_node_3", "tests/additional_files/test_supply_chain_network_TestToFromDict_data.json")
		network2 = load_instance("example_6_1")
		network2.nodes_by_index[3].local_holding_cost = SupplyChainNode._DEFAULT_VALUES['local_holding_cost']
		self.assertTrue(network1.deep_equal_to(network2))

		# In this instance, node 1 is missing the ``demand_source`` attribute.
		network1 = load_instance("missing_demand_source_node_1", "tests/additional_files/test_supply_chain_network_TestToFromDict_data.json")
		network2 = load_instance("example_6_1")
		network2.nodes_by_index[1].demand_source = DemandSource()
		self.assertTrue(network1.deep_equal_to(network2))

		# In this instance, the ``disruption_process`` attribute at node 1 is missing the ``recovery_probability`` attribute.
		network1 = load_instance("missing_recovery_probability_node_1", "tests/additional_files/test_supply_chain_network_TestToFromDict_data.json")
		network2 = load_instance("example_6_1")
		network2.nodes_by_index[1].disruption_process.recovery_probability = DisruptionProcess._DEFAULT_VALUES['_recovery_probability']
		self.assertTrue(network1.deep_equal_to(network2))



