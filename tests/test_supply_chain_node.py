import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from pyinv.supply_chain_node import *
from pyinv.instances import *
from pyinv.sim import *


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

	# def test_init(self):
	# 	"""Test that SupplyChainNode.__init__() correctly raises errors on
	# 	incorrect parameters.
	# 	"""
	# 	print_status('TestPolicyInit', 'test_init()')


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

		network = get_named_instance("example_6_1")

		nodes = network.nodes

		desc = {}
		for i in range(len(nodes)):
			desc[i] = nodes[i].descendants

		self.assertEqual(desc[0], [])
		self.assertEqual(desc[1], [nodes[0]])
		self.assertEqual(desc[2], [nodes[0], nodes[1]])

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

		network = get_named_instance("example_6_1")

		nodes = network.nodes

		anc = {}
		for i in range(len(nodes)):
			anc[i] = nodes[i].ancestors

		self.assertEqual(anc[0], [nodes[1], nodes[2]])
		self.assertEqual(anc[1], [nodes[2]])
		self.assertEqual(anc[2], [])

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


class TestStateVariables(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestStateVariables', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestStateVariables', 'tear_down_class()')

	def test_example_6_1_per_23(self):
		"""Test state variables for simulation of 3-node serial system in
		Example 6.1 at end of period 23.
		"""
		print_status('TestStateVariables', 'test_example_6_1_per_23()')

		network = get_named_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables, (re)run for a few more and repeat.
		simulation(network, 24, rand_seed=17)

		# Note: .on_hand will look at starting IL
		self.assertAlmostEqual(network.nodes[0].on_hand, 0.497397132, places=6)
		self.assertAlmostEqual(network.nodes[1].on_hand, 0.038666224, places=6)
		self.assertAlmostEqual(network.nodes[2].on_hand, 0, places=6)
		self.assertAlmostEqual(network.nodes[0].backorders, 0, places=6)
		self.assertAlmostEqual(network.nodes[1].backorders, 0, places=6)
		self.assertAlmostEqual(network.nodes[2].backorders, 0.832602868, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit_to(network.nodes[0]), 4.553353396, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit_to(network.nodes[1]), 5.385956264, places=6)
		self.assertAlmostEqual(network.nodes[0].in_transit_from(network.nodes[1]), 4.553353396, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit_from(network.nodes[2]), 5.385956264, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit_from(None), 5.491333776+4.553353396, places=6)
		self.assertAlmostEqual(network.nodes[0].in_transit, 4.553353396, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit, 5.385956264, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit, 5.491333776+4.553353396, places=6)
		self.assertAlmostEqual(network.nodes[0].on_order, 5.992602868, places=6)
		self.assertAlmostEqual(network.nodes[1].on_order, 5.491333776, places=6)
		self.assertAlmostEqual(network.nodes[2].on_order, 11.52260287, places=6)
		self.assertAlmostEqual(network.nodes[0].inventory_position, 0.497397132+5.992602868, places=6)
		self.assertAlmostEqual(network.nodes[1].inventory_position, 0.038666224+5.491333776, places=6)
		self.assertAlmostEqual(network.nodes[2].inventory_position, -0.832602868+11.52260287, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_on_hand_inventory, 0.497397132, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_on_hand_inventory, 5.089416752, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_on_hand_inventory, 10.475373015999999, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_inventory_level, 0.497397132, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_inventory_level, 5.089416752, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_inventory_level, 10.475373015999999, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_inventory_position, 0.497397132+5.992602868, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_inventory_position, 5.089416752+5.491333776, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_inventory_position, 10.475373015999999+11.52260287, places=6)

	def test_example_6_1_per_38(self):
		"""Test state variables for simulation of 3-node serial system in
		Example 6.1 at end of period 38.
		"""
		print_status('TestStateVariables', 'test_example_6_1_per_38()')

		network = get_named_instance("example_6_1")

		# Set initial inventory levels to local BS levels.
		for n in network.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Strategy for these tests: run sim for a few periods, test state
		# variables, (re)run for a few more and repeat.
		simulation(network, 39, rand_seed=17)

		# Note: .on_hand will look at starting IL
		self.assertAlmostEqual(network.nodes[0].on_hand, 0, places=6)
		self.assertAlmostEqual(network.nodes[1].on_hand, 0, places=6)
		self.assertAlmostEqual(network.nodes[2].on_hand, 0, places=6)
		self.assertAlmostEqual(network.nodes[0].backorders, 0.16089457, places=6)
		self.assertAlmostEqual(network.nodes[1].backorders, 0.682689274, places=6)
		self.assertAlmostEqual(network.nodes[2].backorders, 0.343065432, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit_to(network.nodes[0]), 4.517316191, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit_to(network.nodes[1]), 4.177692349, places=6)
		self.assertAlmostEqual(network.nodes[0].in_transit_from(network.nodes[1]), 4.517316191, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit_from(network.nodes[2]), 4.177692349, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit_from(None), 5.465282344+3.834626917, places=6)
		self.assertAlmostEqual(network.nodes[0].in_transit, 4.517316191, places=6)
		self.assertAlmostEqual(network.nodes[1].in_transit, 4.177692349, places=6)
		self.assertAlmostEqual(network.nodes[2].in_transit, 5.465282344+3.834626917, places=6)
		self.assertAlmostEqual(network.nodes[0].on_order, 6.65089457, places=6)
		self.assertAlmostEqual(network.nodes[1].on_order, 6.212689274, places=6)
		self.assertAlmostEqual(network.nodes[2].on_order, 11.03306543, places=6)
		self.assertAlmostEqual(network.nodes[0].inventory_position, -0.16089457+6.65089457, places=6)
		self.assertAlmostEqual(network.nodes[1].inventory_position, -0.682689274+6.212689274, places=6)
		self.assertAlmostEqual(network.nodes[2].inventory_position, -0.343065432+11.03306543, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_on_hand_inventory, 0, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_on_hand_inventory, 4.517316191, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_on_hand_inventory, 8.69500854, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_inventory_level, -0.16089457, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_inventory_level, 4.356421621, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_inventory_level, 8.53411397, places=6)
		self.assertAlmostEqual(network.nodes[0].echelon_inventory_position, -0.16089457+6.65089457, places=6)
		self.assertAlmostEqual(network.nodes[1].echelon_inventory_position, 4.356421621+6.212689274, places=6)
		self.assertAlmostEqual(network.nodes[2].echelon_inventory_position, 8.53411397+11.03306543, places=6)

