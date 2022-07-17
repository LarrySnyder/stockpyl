import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

#from supply_chain_node import *
from stockpyl.supply_chain_network import *
from stockpyl.demand_source import DemandSource
from stockpyl.policy import Policy
from stockpyl.instances import *
from stockpyl.sim import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_supply_chain_node   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestSupplyChainNodeInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNodeInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNodeInit', 'tear_down_class()')

	def test_kwargs(self):
		"""Test that SupplyChainNode.__init__() produces identical nodes
		if parameters are passed as arguments vs. set later.
		"""
		print_status('TestSupplyChainNodeInit', 'test_kwargs()')

		node1 = SupplyChainNode(index=1, name='foo', local_holding_cost=5, order_lead_time=2)
		node2 = SupplyChainNode(index=1)
		node2.name = 'foo'
		node2.local_holding_cost = 5
		node2.order_lead_time = 2
		self.assertTrue(node1.deep_equal_to(node2))

		node1 = SupplyChainNode(index=3, name='bar', local_holding_cost=2,
			demand_source=DemandSource(type='N', mean=20, standard_deviation=4), 
			inventory_policy=Policy(type='BS', base_stock_level=30)
		)
		node2 = SupplyChainNode(index=3)
		node2.name = 'bar'
		node2.local_holding_cost = 2
		node2.demand_source = DemandSource()
		node2.demand_source.type = 'N'
		node2.demand_source.mean = 20
		node2.demand_source.standard_deviation = 4
		node2.inventory_policy = Policy()
		node2.inventory_policy.type = 'BS'
		node2.inventory_policy.base_stock_level = 30
		self.assertTrue(node1.deep_equal_to(node2))

	def test_bad_params(self):
		"""Test that SupplyChainNode.__init__() correctly raises errors on
		invalid parameters.
		"""
		print_status('TestSupplyChainNodeInit', 'test_bad_params()')

		with self.assertRaises(AttributeError):
			_ = SupplyChainNode(index=4, foo=7)


class TestSupplyChainNodeEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplyChainNodeEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplyChainNodeEq', 'tear_down_class()')

	def test_eq(self):
		"""Test SupplyChainNode.__eq__().
		"""
		print_status('TestSupplyChainNodeEq', 'test_eq()')

		node1 = SupplyChainNode(index=3, name="foo")
		node2 = SupplyChainNode(index=3, name="bar")
		node3 = SupplyChainNode(index=5, name=None)
		node4 = SupplyChainNode(index=5, name="taco")
		node5 = SupplyChainNode(index=3, name="foo")

		eq11 = node1 == node1
		eq12 = node1 == node2
		eq13 = node1 == node3
		eq14 = node1 == node4
		eq15 = node1 == node5
		eq21 = node2 == node1
		eq22 = node2 == node2
		eq23 = node2 == node3
		eq24 = node2 == node4
		eq25 = node2 == node5
		eq31 = node3 == node1
		eq32 = node3 == node2
		eq34 = node3 == node4
		eq35 = node3 == node5

		self.assertEqual(eq11, True)
		self.assertEqual(eq12, True)
		self.assertEqual(eq13, False)
		self.assertEqual(eq14, False)
		self.assertEqual(eq15, True)
		self.assertEqual(eq21, True)
		self.assertEqual(eq22, True)
		self.assertEqual(eq23, False)
		self.assertEqual(eq24, False)
		self.assertEqual(eq25, True)
		self.assertEqual(eq31, False)
		self.assertEqual(eq32, False)
		self.assertEqual(eq34, True)
		self.assertEqual(eq35, False)

	def test_list_contains(self):
		"""Test that a list can correctly determine whether a SupplyChainNode is
		contained in it. This depends on SupplyChainNode.__eq__() working
		properly.
		"""
		print_status('TestSupplyChainNodeEq', 'test_list_contains()')

		node1 = SupplyChainNode(index=3, name="foo")
		node2 = SupplyChainNode(index=3, name="bar")
		node3 = SupplyChainNode(index=5, name=None)
		node4 = SupplyChainNode(index=6, name="taco")
		node5 = SupplyChainNode(index=3, name="foo")

		mylist = [node1, node2, node3]

		contains1 = node1 in mylist
		contains2 = node2 in mylist
		contains3 = node3 in mylist
		contains4 = node4 in mylist
		contains5 = node5 in mylist

		self.assertEqual(contains1, True)
		self.assertEqual(contains2, True)
		self.assertEqual(contains3, True)
		self.assertEqual(contains4, False)
		self.assertEqual(contains5, True)


class TestDescendants(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDescendants', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDescendants', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test descendants for 3-node serial system in Example 6.1.
		"""
		print_status('TestDescendants', 'test_example_6_1()')

		network = load_instance("example_6_1")

		nodes = network.nodes

		desc = {}
		for n in network.nodes:
			desc[n.index] = set(n.descendants)

		self.assertEqual(desc[1], set([]))
		self.assertEqual(desc[2], set([network.get_node_from_index(1)]))
		self.assertEqual(desc[3], set([network.get_node_from_index(1), network.get_node_from_index(2)]))

	def test_4_node_owmr(self):
		"""Test descendants for 4-node OWMR system.
		"""
		print_status('TestDescendants', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		nodes = []
		for i in range(4):
			nodes.append(SupplyChainNode(i))

		network.add_node(nodes[0])
		network.add_successor(nodes[0], nodes[1])
		network.add_successor(nodes[0], nodes[2])
		network.add_successor(nodes[0], nodes[3])

		desc = {}
		for i in range(len(nodes)):
			desc[i] = nodes[i].descendants

		self.assertEqual(desc[0], [nodes[1], nodes[2], nodes[3]])
		self.assertEqual(desc[1], [])
		self.assertEqual(desc[2], [])
		self.assertEqual(desc[3], [])


class TestAncestors(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAncestors', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAncestors', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test ancestors for 3-node serial system in Example 6.1.
		"""
		print_status('TestAncestors', 'test_example_6_1()')

		network = load_instance("example_6_1")

		anc = {}
		for n in network.nodes:
			anc[n.index] = set(n.ancestors)

		self.assertEqual(anc[1], set([network.get_node_from_index(2), network.get_node_from_index(3)]))
		self.assertEqual(anc[2], set([network.get_node_from_index(3)]))
		self.assertEqual(anc[3], set([]))

	def test_4_node_owmr(self):
		"""Test ancestors for 4-node OWMR system.
		"""
		print_status('TestAncestors', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		nodes = []
		for i in range(4):
			nodes.append(SupplyChainNode(i))

		network.add_node(nodes[0])
		network.add_successor(nodes[0], nodes[1])
		network.add_successor(nodes[0], nodes[2])
		network.add_successor(nodes[0], nodes[3])

		anc = {}
		for i in range(len(nodes)):
			anc[i] = nodes[i].ancestors

		self.assertEqual(anc[0], [])
		self.assertEqual(anc[1], [nodes[0]])
		self.assertEqual(anc[2], [nodes[0]])
		self.assertEqual(anc[3], [nodes[0]])


class TestLeadTime(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLeadTime', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLeadTime', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test lead_time property for 3-node serial system in Example 6.1.
		"""
		print_status('TestLeadTime', 'test_example_6_1()')

		network = load_instance("example_6_1")

		nodes = network.nodes

		self.assertEqual(nodes[0].lead_time, nodes[0].shipment_lead_time)
		self.assertEqual(nodes[2].lead_time, nodes[2].shipment_lead_time)

		nodes[1].lead_time = 7
		self.assertEqual(nodes[1].shipment_lead_time, 7)


class TestForwardEchelonLeadTime(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestForwardEchelonLeadTime', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestForwardEchelonLeadTime', 'tear_down_class()')

	def test_rosling_figure_1(self):
		"""Test forward_echelon_lead_time() for assembly system in Rosling (1989)
		Figure 1.
		"""
		print_status('TestForwardEchelonLeadTime', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")

		self.assertEqual(network.get_node_from_index(1).forward_echelon_lead_time, 1)
		self.assertEqual(network.get_node_from_index(2).forward_echelon_lead_time, 2)
		self.assertEqual(network.get_node_from_index(3).forward_echelon_lead_time, 4)
		self.assertEqual(network.get_node_from_index(4).forward_echelon_lead_time, 6)
		self.assertEqual(network.get_node_from_index(5).forward_echelon_lead_time, 6)
		self.assertEqual(network.get_node_from_index(6).forward_echelon_lead_time, 7)
		self.assertEqual(network.get_node_from_index(7).forward_echelon_lead_time, 8)


class TestEquivalentLeadTime(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEquivalentLeadTime', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEquivalentLeadTime', 'tear_down_class()')

	def test_rosling_figure_1(self):
		"""Test equivalent_lead_time() for assembly system in Rosling (1989)
		Figure 1.
		"""
		print_status('TestEquivalentLeadTime', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")

		self.assertEqual(network.get_node_from_index(1).equivalent_lead_time, 1)
		self.assertEqual(network.get_node_from_index(2).equivalent_lead_time, 1)
		self.assertEqual(network.get_node_from_index(3).equivalent_lead_time, 2)
		self.assertEqual(network.get_node_from_index(4).equivalent_lead_time, 2)
		self.assertEqual(network.get_node_from_index(5).equivalent_lead_time, 0)
		self.assertEqual(network.get_node_from_index(6).equivalent_lead_time, 1)
		self.assertEqual(network.get_node_from_index(7).equivalent_lead_time, 1)


class TestDerivedDemandMean(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDerivedDemandMean', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDerivedDemandMean', 'tear_down_class()')

	def test_serial(self):
		"""Test derived_demand_mean() for serial system (Example 6.1).
		"""
		print_status('TestDerivedDemandMean', 'test_serial()')

		network = load_instance("example_6_1")

		self.assertEqual(network.get_node_from_index(1).derived_demand_mean, 5)
		self.assertEqual(network.get_node_from_index(2).derived_demand_mean, 5)
		self.assertEqual(network.get_node_from_index(3).derived_demand_mean, 5)

	def test_assembly(self):
		"""Test derived_demand_mean() for assembly system (Rosling (1989) Figure 1,
		with demand for node 1 set to N(15, 2^2)).
		"""
		print_status('TestDerivedDemandMean', 'test_assembly()')

		network = load_instance("rosling_figure_1")
		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 15
		demand_source.standard_deviation = 2
		network.get_node_from_index(1).demand_source = demand_source

		self.assertEqual(network.get_node_from_index(1).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(2).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(3).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(4).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(5).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(6).derived_demand_mean, 15)
		self.assertEqual(network.get_node_from_index(7).derived_demand_mean, 15)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(a).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		self.assertEqual(network.get_node_from_index(0).derived_demand_mean, 32)
		self.assertEqual(network.get_node_from_index(1).derived_demand_mean, 16)
		self.assertEqual(network.get_node_from_index(2).derived_demand_mean, 16)
		self.assertEqual(network.get_node_from_index(3).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(4).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(5).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(6).derived_demand_mean, 8)

	def test_rong_atan_snyder_figure_1b(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(b).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1b()')

		network = load_instance("rong_atan_snyder_figure_1b")

		self.assertEqual(network.get_node_from_index(0).derived_demand_mean, 64)
		self.assertEqual(network.get_node_from_index(1).derived_demand_mean, 40)
		self.assertEqual(network.get_node_from_index(2).derived_demand_mean, 24)
		self.assertEqual(network.get_node_from_index(3).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(4).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(5).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(6).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(7).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(8).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(9).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(10).derived_demand_mean, 8)

	def test_rong_atan_snyder_figure_1c(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(c).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1c()')

		network = load_instance("rong_atan_snyder_figure_1c")

		self.assertEqual(network.get_node_from_index(0).derived_demand_mean, 32)
		self.assertEqual(network.get_node_from_index(1).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(2).derived_demand_mean, 24)
		self.assertEqual(network.get_node_from_index(3).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(4).derived_demand_mean, 8)
		self.assertEqual(network.get_node_from_index(5).derived_demand_mean, 8)


class TestDerivedDemandStandardDeviation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDerivedDemandStandardDeviation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDerivedDemandStandardDeviation', 'tear_down_class()')

	def test_serial(self):
		"""Test derived_demand_standard_deviation() for serial system (Example 6.1).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_serial()')

		network = load_instance("example_6_1")

		self.assertEqual(network.get_node_from_index(1).derived_demand_standard_deviation, 1)
		self.assertEqual(network.get_node_from_index(2).derived_demand_standard_deviation, 1)
		self.assertEqual(network.get_node_from_index(3).derived_demand_standard_deviation, 1)

	def test_assembly(self):
		"""Test derived_demand_standard_deviation() for assembly system (Rosling (1989) Figure 1,
		with demand for node 1 set to N(15, 2^2)).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_assembly()')

		network = load_instance("rosling_figure_1")
		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 15
		demand_source.standard_deviation = 2
		network.get_node_from_index(1).demand_source = demand_source

		self.assertEqual(network.get_node_from_index(1).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(2).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(3).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(4).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(5).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(6).derived_demand_standard_deviation, 2)
		self.assertEqual(network.get_node_from_index(7).derived_demand_standard_deviation, 2)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(a).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, np.sqrt(32))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, np.sqrt(16))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, np.sqrt(16))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(6).derived_demand_standard_deviation, np.sqrt(8))

	def test_rong_atan_snyder_figure_1b(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(b).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1b()')

		network = load_instance("rong_atan_snyder_figure_1b")

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, np.sqrt(64))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, np.sqrt(40))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, np.sqrt(24))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(6).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(7).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(8).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(9).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(10).derived_demand_standard_deviation, np.sqrt(8))

	def test_rong_atan_snyder_figure_1c(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(c).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1c()')

		network = load_instance("rong_atan_snyder_figure_1c")

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, np.sqrt(32))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, np.sqrt(24))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, np.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, np.sqrt(8))



class TestDeepEqualTo(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDeepEqualTo', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDeepEqualTo', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test deep_equal_to() for nodes in in Example 6.1.
		"""
		print_status('TestDeepEqualTo', 'test_example_6_1()')

		network = load_instance("example_6_1")

		node1 = network.get_node_from_index(1)
		node2 = network.get_node_from_index(2)
		node3 = network.get_node_from_index(3)

		# Equal nodes.
		node1copy = copy.deepcopy(node1)
		self.assertTrue(node1copy.deep_equal_to(node1))
		self.assertTrue(node1.deep_equal_to(node1copy))
		node2copy = copy.deepcopy(node2)
		self.assertTrue(node2copy.deep_equal_to(node2))
		self.assertTrue(node2.deep_equal_to(node2copy))
		node3copy = copy.deepcopy(node3)
		self.assertTrue(node3copy.deep_equal_to(node3))
		self.assertTrue(node3.deep_equal_to(node3copy))

		# Unequal nodes due to parameters.
		node1copy.local_holding_cost = 99
		self.assertFalse(node1copy.deep_equal_to(node1))
		self.assertFalse(node1.deep_equal_to(node1copy))
		node2copy.demand_source.standard_deviation = 99
		self.assertFalse(node2copy.deep_equal_to(node2))
		self.assertFalse(node2.deep_equal_to(node2copy))

		# Unequal networks due to missing policy.
		node3copy.inventory_policy = None
		self.assertFalse(node3copy.deep_equal_to(node3))
		self.assertFalse(node3.deep_equal_to(node3copy))

	def test_rong_atan_snyder_figure_1a(self):
		"""Test deep_equal_to() for nodes in in rong_atan_snyder_figure_1a.
		"""
		print_status('TestDeepEqualTo', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		node0 = network.get_node_from_index(0)
		node2 = network.get_node_from_index(2)
		node6 = network.get_node_from_index(6)

		# Equal nodes.
		node0copy = copy.deepcopy(node0)
		self.assertTrue(node0copy.deep_equal_to(node0))
		self.assertTrue(node0.deep_equal_to(node0copy))
		node2copy = copy.deepcopy(node2)
		self.assertTrue(node2copy.deep_equal_to(node2))
		self.assertTrue(node2.deep_equal_to(node2copy))
		node6copy = copy.deepcopy(node6)
		self.assertTrue(node6copy.deep_equal_to(node6))
		self.assertTrue(node6.deep_equal_to(node6copy))

		# Unequal nodes due to parameters.
		node0copy.local_holding_cost = 99
		self.assertFalse(node0copy.deep_equal_to(node0))
		self.assertFalse(node0.deep_equal_to(node0copy))
		node2copy.demand_source.standard_deviation = 99
		self.assertFalse(node2copy.deep_equal_to(node2))
		self.assertFalse(node2.deep_equal_to(node2copy))

		# Unequal networks due to missing policy.
		node6copy.inventory_policy = None
		self.assertFalse(node6copy.deep_equal_to(node6))
		self.assertFalse(node6.deep_equal_to(node6copy))
			
class TestNodeToFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNodeToFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNodeToFromDict', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNode object to and from dict
		in Example 6.1.
		"""
		print_status('TestNodeToFromDict', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Convert nodes to dicts.
		node_dicts = [n.to_dict() for n in network.nodes]

		# Convert dicts back to nodes.
		dict_nodes = [SupplyChainNode.from_dict(d) for d in node_dicts]

		# Convert successors and predecessors back to node objects. Replace network objects.
		for n in dict_nodes:
			preds = []
			succs = []
			for m in dict_nodes:
				if m.index in n.predecessors():
					preds.append(m)
				if m.index in n.successors():
					succs.append(m)
			n._predecessors = preds
			n._successors = succs
			n.network = network

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))

	def test_assembly_3_stage(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNode object to and from dict
		in 3-stage assembly system.
		"""
		print_status('TestNodeToFromDict', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")

		# Convert nodes to dicts.
		node_dicts = [n.to_dict() for n in network.nodes]

		# Convert dicts back to nodes.
		dict_nodes = [SupplyChainNode.from_dict(d) for d in node_dicts]

		# Convert successors and predecessors back to node objects. Replace network objects.
		for n in dict_nodes:
			preds = []
			succs = []
			for m in dict_nodes:
				if m.index in n.predecessors():
					preds.append(m)
				if m.index in n.successors():
					succs.append(m)
			n._predecessors = preds
			n._successors = succs
			n.network = network

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))

	def test_example_6_1_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNode object to and from dict
		in Example 6.1 per 22.
		"""
		print_status('TestNodeToFromDict', 'test_example_6_1_per_22()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, convert nodes
		# to dict and back, compare to original.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Convert nodes to dicts.
		node_dicts = [n.to_dict() for n in network.nodes]

		# Convert dicts back to nodes.
		dict_nodes = [SupplyChainNode.from_dict(d) for d in node_dicts]

		# Convert successors and predecessors back to node objects. Replace network objects.
		for n in dict_nodes:
			preds = []
			succs = []
			for m in dict_nodes:
				if m.index in n.predecessors():
					preds.append(m)
				if m.index in n.successors():
					succs.append(m)
			n._predecessors = preds
			n._successors = succs
			n.network = network

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))

	def test_assembly_3_stage_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNode object to and from dict
		in 3-stage assembly system.
		"""
		print_status('TestNodeToFromDict', 'test_assembly_3_stage_per_22()')

		network = load_instance("assembly_3_stage")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, convert nodes
		# to dict and back, compare to original.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Convert nodes to dicts.
		node_dicts = [n.to_dict() for n in network.nodes]

		# Convert dicts back to nodes.
		dict_nodes = [SupplyChainNode.from_dict(d) for d in node_dicts]

		# Convert successors and predecessors back to node objects. Replace network objects.
		for n in dict_nodes:
			preds = []
			succs = []
			for m in dict_nodes:
				if m.index in n.predecessors():
					preds.append(m)
				if m.index in n.successors():
					succs.append(m)
			n._predecessors = preds
			n._successors = succs
			n.network = network

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))

	def test_missing_values(self):
		"""Test that from_dict() correctly fills attributes with defaults if missing.
		"""
		print_status('TestNodeToFromDict', 'test_missing_values()')

		# In this instance, node 3 is missing the ``local_holding_cost`` attribute.
		network1 = load_instance("missing_local_holding_cost_node_3", "tests/additional_files/test_supply_chain_node_TestNodeToFromDict_data.json")
		network2 = load_instance("example_6_1")
		n1 = network1.get_node_from_index(3)
		n2 = network2.get_node_from_index(3)
		n2.local_holding_cost = SupplyChainNode._DEFAULT_VALUES['local_holding_cost']
		self.assertTrue(n1.deep_equal_to(n2))

		# In this instance, node 1 is missing the ``demand_source`` attribute.
		network1 = load_instance("missing_demand_source_node_1", "tests/additional_files/test_supply_chain_node_TestNodeToFromDict_data.json")
		network2 = load_instance("example_6_1")
		n1 = network1.get_node_from_index(1)
		n2 = network2.get_node_from_index(1)
		n2.demand_source = DemandSource()
		self.assertTrue(n1.deep_equal_to(n2))

		# In this instance, the ``disruption_process`` attribute at node 1 is missing the ``recovery_probability`` attribute.
		network1 = load_instance("missing_recovery_probability_node_1", "tests/additional_files/test_supply_chain_node_TestNodeToFromDict_data.json")
		network2 = load_instance("example_6_1")
		n1 = network1.get_node_from_index(1)
		n2 = network2.get_node_from_index(1)
		n2.disruption_process.recovery_probability = DisruptionProcess._DEFAULT_VALUES['_recovery_probability']
		self.assertTrue(n1.deep_equal_to(n2))

			
class TestStateVariables(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestStateVariables', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestStateVariables', 'tear_down_class()')

	def test_example_6_1_per_22(self):
		"""Test state variables for simulation of 3-node serial system in
		Example 6.1 at end of period 22.
		"""
		print_status('TestStateVariables', 'test_example_6_1_per_22()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		nodes = {i: network.get_node_from_index(i) for i in range(1, 4)}

		self.assertAlmostEqual(nodes[1].state_vars[22].inventory_level, 0.497397132, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].inventory_level, 0.038666224, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].inventory_level, -0.832602868, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].on_hand, 0.497397132, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].on_hand, 0.038666224, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].on_hand, 0, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].backorders, 0, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].backorders, 0, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].backorders, 0.832602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].in_transit_to(nodes[1]), 5.992602868, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].in_transit_to(nodes[2]), 4.658730908, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].in_transit_from(nodes[2]), 5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].in_transit_from(nodes[3]), 4.658730908, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].in_transit_from(None), 6.031269092479092+5.491333775514212, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].in_transit, 5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].in_transit, 4.658730908, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].in_transit, 6.031269092479092+5.491333775514212, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].on_order, 5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].on_order, 5.491333776, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].on_order, 6.031269092479092+5.491333775514212, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].inventory_position(), 6.49, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].inventory_position(), 5.53, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].inventory_position(), 10.69, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].echelon_on_hand_inventory, 0.497397132, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].echelon_on_hand_inventory, 0.497397132+5.992602868+0.038666224, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].echelon_on_hand_inventory, 0.497397132+5.992602868+0.038666224+4.658730908, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].echelon_inventory_level, 0.497397132, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].echelon_inventory_level, 0.497397132+5.992602868+0.038666224, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].echelon_inventory_level, 0.497397132+5.992602868+0.038666224+4.658730908, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].echelon_inventory_position(), 0.497397132+5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].echelon_inventory_position(), 0.497397132+5.992602868+0.038666224+5.491333776, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].echelon_inventory_position(), 0.497397132+5.992602868+0.038666224+4.658730908+6.031269092479092+5.491333775514212, places=6)

	def test_example_6_1_per_37(self):
		"""Test state variables for simulation of 3-node serial system in
		Example 6.1 at end of period 37.
		"""
		print_status('TestStateVariables', 'test_example_6_1_per_37()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables.
		simulation(network, 38, rand_seed=17, progress_bar=False)

		# Shortcuts to correct values.
		[IL1, IL2, IL3] = [-0.16089457,-0.682689274,-0.343065432]
		[OH1, OH2, OH3] = np.maximum([IL1, IL2, IL3], 0)
		[BO1, BO2, BO3] = np.maximum([-IL1, -IL2, -IL3], 0)
		[IT1, IT2, IT3] = [5.968205296, 5.869623842, 5.567783088742498+5.465282343506053]
		[OO1, OO2, OO3] = [6.65089457, 6.212689274, 11.03306543]

		nodes = {i: network.get_node_from_index(i) for i in range(1, 4)}

		self.assertAlmostEqual(nodes[1].state_vars[37].inventory_level, IL1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].inventory_level, IL2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].inventory_level, IL3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].on_hand, OH1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].on_hand, OH2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].on_hand, OH3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].backorders, BO1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].backorders, BO2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].backorders, BO3, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].in_transit_to(nodes[1]), IT1, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].in_transit_to(nodes[2]), IT2, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].in_transit_from(nodes[2]), IT1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].in_transit_from(nodes[3]), IT2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].in_transit_from(None), IT3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].in_transit, IT1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].in_transit, IT2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].in_transit, IT3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].on_order, OO1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].on_order, OO2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].on_order, OO3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].raw_material_aggregate, 0, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].inventory_position(), IL1+OO1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].inventory_position(), IL2+OO2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].inventory_position(), IL3+OO3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].echelon_on_hand_inventory, OH1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].echelon_on_hand_inventory, OH1+IT1+OH2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].echelon_on_hand_inventory, OH1+IT1+OH2+IT2+OH3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].echelon_inventory_level, IL1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].echelon_inventory_level, OH1+IT1+OH2-BO1, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].echelon_inventory_level, OH1+IT1+OH2+IT2+OH3-BO1, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].echelon_inventory_position(), IL1+OO1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].echelon_inventory_position(), OH1+IT1+OH2-BO1+OO2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].echelon_inventory_position(), OH1+IT1+OH2+IT2+OH3-BO1+OO3, places=6)

	def test_assembly_3_stage_per_22(self):
		"""Test state variables for simulation of 3-node assembly system at end of period 22.
		"""
		print_status('TestStateVariables', 'test_assembly_3_stage_per_22()')

		network = load_instance("assembly_3_stage")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Shortcuts to correct values.
		[IL0, IL1, IL2] = [2, 2, 0]
		[OH0, OH1, OH2] = np.maximum([IL0, IL1, IL2], 0)
		[BO0, BO1, BO2] = np.maximum([-IL0, -IL1, -IL2], 0)
		[IT10, IT20, IT0, IT1, IT2] = [5, 5, 5, 11, 11]
		[OO01, OO02, OO0, OO1, OO2] = [5, 5, 5, 11, 11]
		[RM01, RM02, RM0, RM1, RM2] = [0, 0, 0, 0, 0]

		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		self.assertEqual(nodes[0].state_vars[22].inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[22].inventory_level, IL1)
		self.assertEqual(nodes[2].state_vars[22].inventory_level, IL2)
		self.assertEqual(nodes[0].state_vars[22].on_hand, OH0)
		self.assertEqual(nodes[1].state_vars[22].on_hand, OH1)
		self.assertEqual(nodes[2].state_vars[22].on_hand, OH2)
		self.assertEqual(nodes[0].state_vars[22].backorders, BO0)
		self.assertEqual(nodes[1].state_vars[22].backorders, BO1)
		self.assertEqual(nodes[2].state_vars[22].backorders, BO2)
		self.assertEqual(nodes[1].state_vars[22].in_transit_to(nodes[0]), IT10)
		self.assertEqual(nodes[2].state_vars[22].in_transit_to(nodes[0]), IT20)
		self.assertEqual(nodes[0].state_vars[22].in_transit_from(nodes[1]), IT10)
		self.assertEqual(nodes[0].state_vars[22].in_transit_from(nodes[2]), IT20)
		self.assertEqual(nodes[1].state_vars[22].in_transit_from(None), IT1)
		self.assertEqual(nodes[2].state_vars[22].in_transit_from(None), IT2)
		self.assertEqual(nodes[0].state_vars[22].in_transit, IT0)
		self.assertEqual(nodes[1].state_vars[22].in_transit, IT1)
		self.assertEqual(nodes[2].state_vars[22].in_transit, IT2)
		self.assertEqual(nodes[0].state_vars[22].on_order_by_predecessor[1], OO01)
		self.assertEqual(nodes[0].state_vars[22].on_order_by_predecessor[2], OO02)
		self.assertEqual(nodes[0].state_vars[22].on_order, OO0)
		self.assertEqual(nodes[1].state_vars[22].on_order, OO1)
		self.assertEqual(nodes[2].state_vars[22].on_order, OO2)
		self.assertEqual(nodes[0].state_vars[22].raw_material_inventory[1], RM01)
		self.assertEqual(nodes[0].state_vars[22].raw_material_inventory[2], RM02)
		self.assertEqual(nodes[0].state_vars[22].raw_material_aggregate, RM0)
		self.assertEqual(nodes[1].state_vars[22].raw_material_aggregate, RM1)
		self.assertEqual(nodes[2].state_vars[22].raw_material_aggregate, RM2)
		self.assertEqual(nodes[0].state_vars[22].inventory_position(1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[22].inventory_position(2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[22].inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[22].inventory_position(), IL1+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[22].inventory_position(), IL2+OO2+RM2)
		self.assertEqual(nodes[0].state_vars[22].echelon_on_hand_inventory, OH0)
		self.assertEqual(nodes[1].state_vars[22].echelon_on_hand_inventory, OH0+IT10+OH1)
		self.assertEqual(nodes[2].state_vars[22].echelon_on_hand_inventory, OH0+IT20+OH2)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[22].echelon_inventory_level, OH0+IT10+OH1-BO0)
		self.assertEqual(nodes[2].state_vars[22].echelon_inventory_level, OH0+IT20+OH2-BO0)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[22].echelon_inventory_position(), OH0+IT10+OH1-BO0+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[22].echelon_inventory_position(), OH0+IT20+OH2-BO0+OO2+RM2)

	def test_assembly_3_stage_per_43(self):
		"""Test state variables for simulation of 3-node assembly system at end of period 43.
		"""
		print_status('TestStateVariables', 'test_assembly_3_stage_per_43()')

		network = load_instance("assembly_3_stage")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables.
		simulation(network, 44, rand_seed=17, progress_bar=False)

		# Shortcuts to correct values.
		per = 43
		[IL0, IL1, IL2] = [1, 4, 2]
		[OH0, OH1, OH2] = np.maximum([IL0, IL1, IL2], 0)
		[BO0, BO1, BO2] = np.maximum([-IL0, -IL1, -IL2], 0)
		[IT01, IT02, IT0, IT1, IT2] = [4, 6, 5, 9, 9]
		[OO01, OO02, OO0, OO1, OO2] = [4, 6, 5, 9, 9]
		[RM01, RM02, RM0, RM1, RM2] = [2, 0, 1, 0, 0]

		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		self.assertEqual(nodes[0].state_vars[per].inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[per].inventory_level, IL1)
		self.assertEqual(nodes[2].state_vars[per].inventory_level, IL2)
		self.assertEqual(nodes[0].state_vars[per].on_hand, OH0)
		self.assertEqual(nodes[1].state_vars[per].on_hand, OH1)
		self.assertEqual(nodes[2].state_vars[per].on_hand, OH2)
		self.assertEqual(nodes[0].state_vars[per].backorders, BO0)
		self.assertEqual(nodes[1].state_vars[per].backorders, BO1)
		self.assertEqual(nodes[2].state_vars[per].backorders, BO2)
		self.assertEqual(nodes[1].state_vars[per].in_transit_to(nodes[0]), IT01)
		self.assertEqual(nodes[2].state_vars[per].in_transit_to(nodes[0]), IT02)
		self.assertEqual(nodes[0].state_vars[per].in_transit_from(nodes[1]), IT01)
		self.assertEqual(nodes[0].state_vars[per].in_transit_from(nodes[2]), IT02)
		self.assertEqual(nodes[1].state_vars[per].in_transit_from(None), IT1)
		self.assertEqual(nodes[2].state_vars[per].in_transit_from(None), IT2)
		self.assertEqual(nodes[0].state_vars[per].in_transit, IT0)
		self.assertEqual(nodes[1].state_vars[per].in_transit, IT1)
		self.assertEqual(nodes[2].state_vars[per].in_transit, IT2)
		self.assertEqual(nodes[0].state_vars[per].on_order_by_predecessor[1], OO01)
		self.assertEqual(nodes[0].state_vars[per].on_order_by_predecessor[2], OO02)
		self.assertEqual(nodes[0].state_vars[per].on_order, OO0)
		self.assertEqual(nodes[1].state_vars[per].on_order, OO1)
		self.assertEqual(nodes[2].state_vars[per].on_order, OO2)
		self.assertEqual(nodes[0].state_vars[per].raw_material_inventory[1], RM01)
		self.assertEqual(nodes[0].state_vars[per].raw_material_inventory[2], RM02)
		self.assertEqual(nodes[0].state_vars[per].raw_material_aggregate, RM0)
		self.assertEqual(nodes[1].state_vars[per].raw_material_aggregate, RM1)
		self.assertEqual(nodes[2].state_vars[per].raw_material_aggregate, RM2)
		self.assertEqual(nodes[0].state_vars[per].inventory_position(1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[per].inventory_position(2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[per].inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[per].inventory_position(), IL1+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[per].inventory_position(), IL2+OO2+RM2)
		self.assertEqual(nodes[0].state_vars[per].echelon_on_hand_inventory, OH0)
		self.assertEqual(nodes[1].state_vars[per].echelon_on_hand_inventory, OH0+IT01+OH1)
		self.assertEqual(nodes[2].state_vars[per].echelon_on_hand_inventory, OH0+IT02+OH2)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[per].echelon_inventory_level, OH0+IT01+OH1-BO0)
		self.assertEqual(nodes[2].state_vars[per].echelon_inventory_level, OH0+IT02+OH2-BO0)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[per].echelon_inventory_position(), OH0+IT01+OH1-BO0+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[per].echelon_inventory_position(), OH0+IT02+OH2-BO0+OO2+RM2)

	# def test_rosling_figure_1_per_22(self):
	# 	"""Test state variables for simulation of system in Rosling (1989), Figure 1,
	# 	at end of period 22.
	# 	"""
	# 	print_status('TestStateVariables', 'test_rosling_figure_1_per_22()')
	#
	# 	network = load_instance("rosling_figure_1")
	#
	# 	# Strategy for these tests: run sim for a few periods, test state
	# 	# variables.
	# 	simulation(network, 23, rand_seed=17, progress_bar=False)
	#
	# 	# Shortcuts to correct values.
	# 	per = 22
	# 	IL = {1: -33, 2: -25, 3: -39, 4: -24, 5: -60, 6: 7, 7: -6}
	# 	OH = {i: max(IL[i], 0) for i in range(1, 8)}
	# 	BO = {i: max(-IL[i], 0) for i in range(1, 8)}
	# 	IT = {(1, 2): 2, (1, 3): 2, (2, 5): 0, (3, 4): 15, (4, 6): 10, (4, 7): 18, (5, None): 84, (6, None): 8, (7, None): 6}
	# 	OO = {(1, 2): 27, (1, 3): 41, (2, 5): 60, (3, 4): 39, (4, 6): 10, (4, 7): 24, (5, None): 84, (6, None): 8, (7, None): 6}
	# 	RM = {(1, 2): 14, (1, 3): 0, (2, 5): 0, (3, 4): 0, (4, 6): 14, (4, 7): 0, (5, None): 0, (6, None): 0, (7, None): 0}
	#
	# 	IT_agg = {}
	# 	OO_agg = {}
	# 	RM_agg = {}
	# 	ech_OH = {}
	# 	for n_ind in range(1, 8):
	# 		node = network.get_node_from_index(n_ind)
	# 		IT_agg[n_ind] = np.sum([IT[(n_ind, p_ind)] for (m_ind, p_ind) in IT if m_ind == n_ind]) / \
	# 						 	len(node.predecessors(include_external=True))
	# 		OO_agg[n_ind] = np.sum([OO[(n_ind, p_ind)] for (m_ind, p_ind) in OO if m_ind == n_ind]) / \
	# 						 	len(node.predecessors(include_external=True))
	# 		RM_agg[n_ind] = np.sum([RM[(n_ind, p_ind)] for (m_ind, p_ind) in RM if m_ind == n_ind]) / \
	# 						 	len(node.predecessors(include_external=True))
	# 		ech_OH[n_ind] = OH[n_ind] + np.sum([IT[(s_ind, n_ind)] + ech_OH[s_ind] for s_ind in node.successor_indices()])
	# 	EIPA = {(1, 2): ech_OH[1] - BO[1] + 0,
	# 			(1, 3): ech_OH[1] - BO[1] + 0,
	# 			(2, 5): ech_OH[2] - BO[1] + 0,
	# 			(3, 4): ech_OH[3] - BO[1] + 9,
	# 			(4, 6): ech_OH[4] - BO[1] + 0,
	# 			(4, 7): ech_OH[4] - BO[1] + 0,
	# 			(5, None): ech_OH[5] - BO[1] + 84,
	# 			(6, None): ech_OH[6] - BO[1] + 0,
	# 			(7, None): ech_OH[7] - BO[1] + 1}
	#
	# 	for n_ind in range(1, 8):
	# 		node = network.get_node_from_index(n_ind)
	# 		self.assertEqual(node.state_vars[per].inventory_level, IL[n_ind])
	# 		self.assertEqual(node.state_vars[per].on_hand, OH[n_ind])
	# 		self.assertEqual(node.state_vars[per].backorders, BO[n_ind])
	# 		for s in node.successors(include_external=False):
	# 			self.assertEqual(node.state_vars[per].in_transit_to(s), IT[(s.index, n_ind)])
	# 		for p in node.predecessors(include_external=True):
	# 			p_ind = None if p is None else p.index
	# 			self.assertEqual(node.state_vars[per].in_transit_from(p), IT[(n_ind, p_ind)])
	# 			self.assertEqual(node.state_vars[per].on_order_by_predecessor[p_ind], OO[(n_ind, p_ind)])
	# 			self.assertEqual(node.state_vars[per].raw_material_inventory[p_ind], RM[(n_ind, p_ind)])
	# 			self.assertEqual(node.state_vars[per].inventory_position(p_ind),
	# 							 IL[n_ind] + OO[(n_ind, p_ind)] + RM[(n_ind, p_ind)])
	# 			self.assertEqual(node.state_vars[per].echelon_inventory_position(p_ind),
	# 							 ech_OH[n_ind] - BO[1] + OO[(n_ind, p_ind)] + RM[(n_ind, p_ind)])
	# 			self.assertEqual(node.state_vars[per].echelon_inventory_position_adjusted(p_ind), EIPA[(n_ind, p_ind)])
	# 		self.assertEqual(node.state_vars[per].in_transit, IT_agg[n_ind])
	# 		self.assertEqual(node.state_vars[per].on_order, OO_agg[n_ind])
	# 		self.assertEqual(node.state_vars[per].raw_material_aggregate, RM_agg[n_ind])
	# 		self.assertEqual(node.state_vars[per].inventory_position(), IL[n_ind] + OO_agg[n_ind] + RM_agg[n_ind])
	# 		self.assertEqual(node.state_vars[per].echelon_on_hand_inventory, ech_OH[n_ind])
	# 		self.assertEqual(node.state_vars[per].echelon_inventory_level, ech_OH[n_ind] - BO[1])
	# 		self.assertEqual(node.state_vars[per].echelon_inventory_position(), ech_OH[n_ind] - BO[1] + OO_agg[n_ind] + RM_agg[n_ind])
	#


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

		n1 = SupplyChainNode(index=None)
		n2 = SupplyChainNode(index=None)
		n1.initialize()
		self.assertTrue(n1.deep_equal_to(n2))

		n1 = SupplyChainNode(index=None, local_holding_cost=2, stockout_cost=50, shipment_lead_time=3)
		n2 = SupplyChainNode(index=None)
		n1.initialize()
		self.assertTrue(n1.deep_equal_to(n2))


class TestNodeStateVarsToFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNodeStateVarsToFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNodeStateVarsToFromDict', 'tear_down_class()')

	def test_example_6_1_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert NodeStateVars object to and from dict
		in Example 6.1 per 22.
		"""
		print_status('TestNodeStateVarsToFromDict', 'test_example_6_1_per_22()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, convert state vars
		# to dict and back, compare to original.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Convert to dicts.
		nsv_dict_lists = {}
		for ind, nsv_list in original_nsv_lists.items():
			nsv_dict_lists[ind] = [nsv.to_dict() for nsv in nsv_list]

		# Convert back.
		nsv_lists_converted = {}
		for ind, nsv_dict_list in nsv_dict_lists.items():
			nsv_lists_converted[ind] = [NodeStateVars.from_dict(nsv_dict) for nsv_dict in nsv_dict_list]

		# Set node attributes to in original_nsv_lists to the node's indices 
		# (otherwise deep_equal_to() will get confused since from_dict() will only
		# set node to the node's index).
		for ind, nsv_list in original_nsv_lists.items():
			for t in range(len(nsv_list)):
				nsv_list[t].node = nsv_list[t].node.index

		# Check for equality.
		for ind, nsv_list in original_nsv_lists.items():
			self.assertListEqual(nsv_list, nsv_lists_converted[ind])

	def test_assembly_3_stage_per_22(self):
		"""Test that to_dict() and from_dict() correctly convert NodeStateVars object to and from dict
		in Example 6.1 per 22.
		"""
		print_status('TestNodeStateVarsToFromDict', 'test_assembly_3_stage_per_22()')

		network = load_instance("assembly_3_stage")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Convert to dicts.
		nsv_dict_lists = {}
		for ind, nsv_list in original_nsv_lists.items():
			nsv_dict_lists[ind] = [nsv.to_dict() for nsv in nsv_list]

		# Convert back.
		nsv_lists_converted = {}
		for ind, nsv_dict_list in nsv_dict_lists.items():
			nsv_lists_converted[ind] = [NodeStateVars.from_dict(nsv_dict) for nsv_dict in nsv_dict_list]

		# Set node attributes to in original_nsv_lists to the node's indices 
		# (otherwise deep_equal_to() will get confused since from_dict() will only
		# set node to the node's index).
		for ind, nsv_list in original_nsv_lists.items():
			for t in range(len(nsv_list)):
				nsv_list[t].node = nsv_list[t].node.index

		# Check for equality.
		for ind, nsv_list in original_nsv_lists.items():
			self.assertListEqual(nsv_list, nsv_lists_converted[ind])


class TestNodeStateVarsEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNodeStateVarsEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNodeStateVarsEq', 'tear_down_class()')

	def test_equal(self):
		"""Test that __eq__() and __ne__() work when state variables are equal.
		"""
		print_status('TestNodeStateVarsEq', 'test_equal()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, make copies of
		# state vars, check that they are equal.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Copies
		copy_nsv_lists = {ind: copy.deepcopy(nsv_list) for ind, nsv_list in original_nsv_lists.items()}

		# Check equality.
		for ind, nsv_list in original_nsv_lists.items():
			for t in range(len(nsv_list)):
				self.assertTrue(copy_nsv_lists[ind][t] == nsv_list[t])
				self.assertFalse(copy_nsv_lists[ind][t] != nsv_list[t])

	def test_not_equal(self):
		"""Test that __eq__() and __ne()__ work when state variables are not equal.
		"""
		print_status('TestNodeStateVarsEq', 'test_not_equal()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, make copies of
		# state vars, check that they are equal.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Copies
		copy_nsv_lists = {ind: copy.deepcopy(nsv_list) for ind, nsv_list in original_nsv_lists.items()}

		# Modify one object.
		copy_nsv_lists[1][12].inventory_level = 77

		# Check inequality.
		self.assertTrue(copy_nsv_lists[1][12] != original_nsv_lists[1][12])
		self.assertFalse(copy_nsv_lists[1][12] == original_nsv_lists[1][12])
		

class TestNodeStateVarsDeepEqualTo(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNodeStateVarsDeepEqualTo', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNodeStateVarsDeepEqualTo', 'tear_down_class()')

	def test_equal(self):
		"""Test that deep_equal_to() works when state variables are equal.
		"""
		print_status('TestNodeStateVarsDeepEqualTo', 'test_equal()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, make copies of
		# state vars, check that they are equal.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Copies
		copy_nsv_lists = {ind: copy.deepcopy(nsv_list) for ind, nsv_list in original_nsv_lists.items()}

		# Check equality.
		for ind, nsv_list in original_nsv_lists.items():
			for t in range(len(nsv_list)):
				self.assertTrue(copy_nsv_lists[ind][t].deep_equal_to(nsv_list[t]))

	def test_not_equal(self):
		"""Test that deep_equal_to() works when state variables are not equal.
		"""
		print_status('TestNodeStateVarsDeepEqualTo', 'test_not_equal()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, make copies of
		# state vars, check that they are equal.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		# Original NodeStateVars.
		original_nsv_lists = {n.index: n.state_vars for n in network.nodes}

		# Copies
		copy_nsv_lists = {ind: copy.deepcopy(nsv_list) for ind, nsv_list in original_nsv_lists.items()}

		# Modify one object.
		copy_nsv_lists[1][12].inventory_level = 77

		# Check inequality.
		self.assertFalse(copy_nsv_lists[1][12].deep_equal_to(original_nsv_lists[1][12]))
