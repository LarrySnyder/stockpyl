import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

#from supply_chain_node import *
from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_product import *
from stockpyl.demand_source import DemandSource
from stockpyl.policy import Policy
from stockpyl.instances import *
from stockpyl.sim import *

from stockpyl.supply_chain_node import _INDEX_BUMP

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


class TestIndex(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIndex', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIndex', 'tear_down_class()')

	def test_update_dummy(self):
		"""Test that changing index also changes the dummy product.
		"""
		print_status('TestIndex', 'test_bad_index()')

		node = SupplyChainNode(index=5)
		self.assertEqual(node._dummy_product.index, -10)

		node.index = 10
		self.assertEqual(node._dummy_product.index, -20)

	def test_bad_index(self):
		"""Test that index property correctly raises error when appropriate.
		"""
		print_status('TestIndex', 'test_bad_index()')

		with self.assertRaises(ValueError):
			_ = SupplyChainNode(index=5.5)
			_ = SupplyChainProduct(index=-10)	
	

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


class TestGetAttribute(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetAttribute', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetAttribute', 'tear_down_class()')

	def test_singleproduct_node(self):
		"""Test get_attribute() for single node with single product.
		"""
		print_status('TestGetAttribute', 'test_singleproduct_node()')

		node = SupplyChainNode(index=0, local_holding_cost=2, lead_time=1, revenue=100)

		self.assertEqual(node.get_attribute('local_holding_cost'), 2)
		self.assertEqual(node.get_attribute('holding_cost', None), 2)
		self.assertEqual(node.get_attribute('lead_time'), 1)
		self.assertEqual(node.get_attribute('revenue'), 100)
		self.assertEqual(node.get_attribute('stockout_cost', None), None)
		self.assertEqual(node.get_attribute('stockout_cost'), None)
		
	def test_multiproduct_node(self):
		"""Test get_attribute() for single node with multiple products.
		"""
		print_status('TestGetAttribute', 'test_multiproduct_node()')

		node = SupplyChainNode(index=0, local_holding_cost=2)
		prod0 = SupplyChainProduct(index=0, lead_time=1, revenue=100)
		prod1 = SupplyChainProduct(index=1, lead_time=2, order_lead_time=4)
		prod2 = SupplyChainProduct(index=2, lead_time=3, initial_orders=33)
		node.add_products([prod0, prod1, prod2])
		node.initial_inventory_level = {0: 50, 1: 70, 2: 90}
		node.revenue = {1: 200, 2: 300}
		node.order_lead_time = {0: 5}

		self.assertEqual(node.get_attribute('local_holding_cost', 0), 2)
		self.assertEqual(node.get_attribute('local_holding_cost', prod1), 2)
		self.assertEqual(node.get_attribute('local_holding_cost', prod2), 2)
		self.assertEqual(node.get_attribute('holding_cost', 0), 2)
		self.assertEqual(node.get_attribute('holding_cost', prod1), 2)
		self.assertEqual(node.get_attribute('holding_cost', prod2), 2)
		self.assertEqual(node.get_attribute('lead_time', 0), 1)
		self.assertEqual(node.get_attribute('lead_time', 1), 2)
		self.assertEqual(node.get_attribute('lead_time', prod2), 3)
		self.assertEqual(node.get_attribute('revenue', prod0), 100)
		self.assertEqual(node.get_attribute('revenue', 1), 200)
		self.assertEqual(node.get_attribute('revenue', 2), 300)
		self.assertEqual(node.get_attribute('order_lead_time', prod0), 5)
		self.assertEqual(node.get_attribute('order_lead_time', 1), 4)
		self.assertEqual(node.get_attribute('order_lead_time', prod2), None)
		self.assertEqual(node.get_attribute('initial_orders', 0), None)
		self.assertEqual(node.get_attribute('initial_orders', 1), None)
		self.assertEqual(node.get_attribute('initial_orders', 2), 33)
		self.assertEqual(node.get_attribute('initial_inventory_level', 0), 50)
		self.assertEqual(node.get_attribute('initial_inventory_level', prod1), 70)
		self.assertEqual(node.get_attribute('initial_inventory_level', 2), 90)
		self.assertEqual(node.get_attribute('stockout_cost', prod0), None)
		self.assertEqual(node.get_attribute('stockout_cost', 1), None)
		self.assertEqual(node.get_attribute('stockout_cost', prod2), None)

		with self.assertRaises(ValueError):
			node.get_attribute('local_holding_cost', None)


		
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

	def test_multiproduct_5_7(self):
		"""Test descendants for 7-node multi-product system.
		"""
		print_status('TestDescendants', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		desc = {i: network.get_node_from_index(i).descendants for i in network.node_indices}

		self.assertEqual(desc[0], [])
		self.assertEqual(desc[1], [])
		self.assertEqual(desc[2], [network.get_node_from_index(0), network.get_node_from_index(1)])
		self.assertEqual(desc[3], [network.get_node_from_index(1)])
		self.assertEqual(desc[4], [network.get_node_from_index(0), network.get_node_from_index(1), network.get_node_from_index(2), network.get_node_from_index(3)])



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

	def test_multiproduct_5_7(self):
		"""Test ancestors for 5-node, 7-product system.
		"""
		print_status('TestAncestors', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		anc = {i: network.get_node_from_index(i).ancestors for i in network.node_indices}

		self.assertEqual(anc[0], [network.get_node_from_index(2), network.get_node_from_index(4)])
		self.assertEqual(anc[1], [network.get_node_from_index(2), network.get_node_from_index(3), network.get_node_from_index(4)])
		self.assertEqual(anc[2], [network.get_node_from_index(4)])
		self.assertEqual(anc[3], [network.get_node_from_index(4)])
		self.assertEqual(anc[4], [])


class TestAddProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddProduct', 'tear_down_class()')

	def test_basic(self):
		"""Basic test.
		"""
		print_status('TestAddProduct', 'test_basic()')

		network = load_instance("example_6_1")

		network.nodes[0].add_product(SupplyChainProduct(0))
		network.nodes[1].add_product(SupplyChainProduct(1))
		network.nodes[2].add_product(SupplyChainProduct(2))
		network.nodes[2].add_product(SupplyChainProduct(3))

		self.assertEqual(network.nodes[0].product_indices, [0])
		self.assertEqual(network.nodes[1].product_indices, [1])
		self.assertEqual(network.nodes[2].product_indices, [2, 3])

		
class TestAddProducts(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddProducts', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddProducts', 'tear_down_class()')

	def test_basic(self):
		"""Basic test.
		"""
		print_status('TestAddProducts', 'test_basic()')

		network = load_instance("example_6_1")

		network.nodes[0].add_products([SupplyChainProduct(0)])
		network.nodes[1].add_products([SupplyChainProduct(1)])
		network.nodes[2].add_products([SupplyChainProduct(2)])
		network.nodes[2].add_products([SupplyChainProduct(3)])

		self.assertEqual(network.nodes[0].product_indices, [0])
		self.assertEqual(network.nodes[1].product_indices, [1])
		self.assertEqual(network.nodes[2].product_indices, [2, 3])


class TestRemoveProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRemoveProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRemoveProduct', 'tear_down_class()')

	def test_basic(self):
		"""Basic test.
		"""
		print_status('TestRemoveProduct', 'test_basic()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		nodes[1].add_product(SupplyChainProduct(0))
		nodes[2].add_product(SupplyChainProduct(1))
		nodes[3].add_product(SupplyChainProduct(2))
		nodes[3].add_product(SupplyChainProduct(3))

		nodes[1].remove_product(0)
		nodes[2].remove_product(1)
		nodes[3].remove_product(nodes[3].products_by_index[2])

		self.assertEqual(nodes[1].product_indices, [-2])
		self.assertEqual(nodes[2].product_indices, [-4])
		self.assertEqual(nodes[3].product_indices, [3])

	def test_multiproduct_5_7(self):
		"""Test remove_product() for 5-node 7-product instance.
		"""
		print_status('TestRemoveProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.get_node_from_index(0).remove_product(network.get_node_from_index(0).products_by_index[0])
		network.get_node_from_index(1).remove_product(1)
		network.get_node_from_index(2).remove_product(network.get_node_from_index(2).products_by_index[2])

		self.assertEqual(network.get_node_from_index(0).product_indices, [-_INDEX_BUMP])
		self.assertEqual(network.get_node_from_index(1).product_indices, [0])
		self.assertEqual(network.get_node_from_index(2).product_indices, [3, 4])

	def test_product_does_not_exist(self):
		"""Test that remove_product() correctly does nothing if product doesn't exist.
		"""
		print_status('TestRemoveProduct', 'test_product_does_not_exist()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.get_node_from_index(0).remove_product(7)
		network.get_node_from_index(1).remove_product(7)

		self.assertEqual(network.get_node_from_index(0).product_indices, [0])
		self.assertEqual(network.get_node_from_index(1).product_indices, [0, 1])


class TestAddRemoveDummyProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestAddRemoveDummyProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestAddRemoveDummyProduct', 'tear_down_class()')

	def test_basic(self):
		"""Basic test.
		"""
		print_status('TestAddRemoveDummyProduct', 'test_basic()')

		node = SupplyChainNode(4)
		self.assertEqual(node.product_indices, [-8])
		self.assertTrue(node.products[0].is_dummy)

	def test_add_remove(self):
		"""Basic test.
		"""
		print_status('TestAddRemoveDummyProduct', 'test_add_remove()')

		node = SupplyChainNode(4)
		self.assertEqual(node.product_indices, [-8])
		self.assertTrue(node.products[0].is_dummy)
		self.assertEqual(node._dummy_product, node.products[0])

		node.add_product(SupplyChainProduct(5))
		self.assertNotIn(-4, node.product_indices)
		self.assertFalse(node.products[0].is_dummy)
		self.assertIsNone(node._dummy_product)

		node.remove_product(5)
		self.assertEqual(node.product_indices, [-8])
		self.assertTrue(node.products[0].is_dummy)
		self.assertEqual(node._dummy_product, node.products[0])

class TestRemoveProducts(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRemoveProducts', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRemoveProducts', 'tear_down_class()')

	def test_basic(self):
		"""Basic test.
		"""
		print_status('TestRemoveProducts', 'test_basic()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		nodes[1].add_product(SupplyChainProduct(0))
		nodes[2].add_product(SupplyChainProduct(1))
		nodes[3].add_product(SupplyChainProduct(2))
		nodes[3].add_product(SupplyChainProduct(3))

		nodes[1].remove_products([0])
		nodes[2].remove_products([1])
		nodes[3].remove_products([nodes[3].products_by_index[2], 3])

		self.assertEqual(nodes[1].product_indices, [-2])
		self.assertEqual(nodes[2].product_indices, [-4])
		self.assertEqual(nodes[3].product_indices, [-6])

	def test_multiproduct_5_7(self):
		"""Test remove_product() for 5-node 7-product instance.
		"""
		print_status('TestRemoveProducts', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.get_node_from_index(0).remove_products([network.get_node_from_index(0).products_by_index[0]])
		network.get_node_from_index(1).remove_products([1])
		network.get_node_from_index(2).remove_products([3, network.get_node_from_index(2).products_by_index[2]])

		self.assertEqual(network.get_node_from_index(0).product_indices, [-_INDEX_BUMP])
		self.assertEqual(network.get_node_from_index(1).product_indices, [0])
		self.assertEqual(network.get_node_from_index(2).product_indices, [4])

	def test_product_does_not_exist(self):
		"""Test that remove_product() correctly does nothing if product doesn't exist.
		"""
		print_status('TestRemoveProducts', 'test_product_does_not_exist()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.get_node_from_index(0).remove_products([7])
		network.get_node_from_index(2).remove_products([3, 7])

		self.assertEqual(network.get_node_from_index(0).product_indices, [0])
		self.assertEqual(network.get_node_from_index(2).product_indices, [2, 4])

		
class TestIsSingleMultiProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsMultiProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsMultiProduct', 'tear_down_class()')

	def test_dummy(self):
		"""Test that is_multiproduct and is_singleproduct return correct results if node only has dummy product.
		"""
		print_status('TestIsMultiProduct', 'test_dummy()')

		network = load_instance("example_6_1")

		# Make sure node 0 has no products.
		network.nodes[0].remove_products('all')

		self.assertFalse(network.nodes[0].is_multiproduct)
		self.assertTrue(network.nodes[0].is_singleproduct)

	def test_singleton(self):
		"""Test that is_multiproduct and is_singleproduct return correct results if node has one real product.
		"""
		print_status('TestIsMultiProduct', 'test_singleton()')

		network = load_instance("example_6_1")

		network.nodes[0].add_product(SupplyChainProduct(0))

		self.assertFalse(network.nodes[0].is_multiproduct)
		self.assertTrue(network.nodes[0].is_singleproduct)

	def test_multi(self):
		"""Test that is_multiproduct and is_singleproduct return correct results if node has multiple products.
		"""
		print_status('TestIsMultiProduct', 'test_multi()')

		network = load_instance("example_6_1")

		network.nodes[0].add_products([SupplyChainProduct(0), SupplyChainProduct(1)])

		self.assertTrue(network.nodes[0].is_multiproduct)
		self.assertFalse(network.nodes[0].is_singleproduct)

	def test_multiproduct_5_7(self):
		"""Test that is_multiproduct and is_singleproduct work correctly for 5-node, 7-product instance.
		"""
		print_status('TestIsMultiProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		self.assertFalse(network.get_node_from_index(0).is_multiproduct)
		self.assertTrue(network.get_node_from_index(1).is_multiproduct)
		self.assertTrue(network.get_node_from_index(2).is_multiproduct)
		self.assertTrue(network.get_node_from_index(3).is_multiproduct)
		self.assertTrue(network.get_node_from_index(4).is_multiproduct)

		self.assertTrue(network.get_node_from_index(0).is_singleproduct)
		self.assertFalse(network.get_node_from_index(1).is_singleproduct)
		self.assertFalse(network.get_node_from_index(2).is_singleproduct)
		self.assertFalse(network.get_node_from_index(3).is_singleproduct)
		self.assertFalse(network.get_node_from_index(4).is_singleproduct)

		# Add a node with no product loaded.
		network.add_node(SupplyChainNode(20))
		self.assertFalse(network.get_node_from_index(20).is_multiproduct)
		self.assertTrue(network.get_node_from_index(20).is_singleproduct)



		
		
# class TestGetProductFromIndex(unittest.TestCase):
# 	@classmethod
# 	def set_up_class(cls):
# 		"""Called once, before any tests."""
# 		print_status('TestGetProductFromIndex', 'set_up_class()')

# 	@classmethod
# 	def tear_down_class(cls):
# 		"""Called once, after all tests, if set_up_class successful."""
# 		print_status('TestGetProductFromIndex', 'tear_down_class()')

# 	def test_basic(self):
# 		"""Basic test.
# 		"""
# 		print_status('TestGetProductFromIndex', 'test_basic()')

# 		prod1 = SupplyChainProduct(index=0, local_holding_cost=1, stockout_cost=10)
# 		prod2 = SupplyChainProduct(index=1, local_holding_cost=2, stockout_cost=50)
# 		node = SupplyChainNode(index=0, products=[prod1, prod2])

# 		self.assertEqual(node.products[0].index, 0)
# 		self.assertEqual(node.products[1].index, 1)

# 	def test_multi_product_network7(self):
# 		"""Test 7-node multiproduct instance.
# 		"""
# 		print_status('TestGetProductFromIndex', 'test_multi_product_network7()')

# 		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

# 		self.assertIsNone(network.get_node_from_index(0).products[None])
# 		self.assertIsNone(network.get_node_from_index(0).products[44])
# 		self.assertEqual(network.get_node_from_index(1).products[1].index, 1)
# 		self.assertEqual(network.get_node_from_index(2).products[2].index, 2)
# 		self.assertEqual(network.get_node_from_index(2).products[3].index, 3)
# 		self.assertIsNone(network.get_node_from_index(2).products[44])


# class TestSetGetBillOfMaterials(unittest.TestCase):
# 	@classmethod
# 	def set_up_class(cls):
# 		"""Called once, before any tests."""
# 		print_status('TestSetGetBillOfMaterials', 'set_up_class()')

# 	@classmethod
# 	def tear_down_class(cls):
# 		"""Called once, after all tests, if set_up_class successful."""
# 		print_status('TestSetGetBillOfMaterials', 'tear_down_class()')

# 	def test_single_product(self):
# 		"""Test that set_ and get_bill_of_materials() work correctly when the node is single-product.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_single_product()')

# 		network = mwor_system(3)

# 		network.nodes[1].add_products([SupplyChainProduct(1), SupplyChainProduct(2)])
# 		network.nodes[2].add_products([SupplyChainProduct(2), SupplyChainProduct(3)])
# 		network.nodes[3].add_products([SupplyChainProduct(4), SupplyChainProduct(5)])

# 		network.nodes[0].set_bill_of_materials( 5, None, 1, 1)
# 		network.nodes[0].set_bill_of_materials( 7, None, 1, 2)
# 		network.nodes[0].set_bill_of_materials( 3, None, 2, 2)
# 		network.nodes[0].set_bill_of_materials(15, None, 2, 3)
# 		network.nodes[0].set_bill_of_materials( 6, None, 3, 4)
# 		network.nodes[0].set_bill_of_materials(16, None, 3, 5)

# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 1, 1), 5)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 1, 2), 7)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 2, 2), 3)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 2, 3), 15)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 3, 4), 6)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(None, 3, 5), 16)

# 	def test_multi_product(self):
# 		"""Test that set_ and get_bill_of_materials() work correctly when the node is multi-product.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_multi_product()')

# 		network = mwor_system(3)

# 		network.nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11)])
# 		network.nodes[1].add_products([SupplyChainProduct(1), SupplyChainProduct(2)])
# 		network.nodes[2].add_products([SupplyChainProduct(2), SupplyChainProduct(3)])
# 		network.nodes[3].add_products([SupplyChainProduct(4), SupplyChainProduct(5)])

# 		network.nodes[0].set_bill_of_materials(5, 10, 1, 1)
# 		network.nodes[0].set_bill_of_materials(7, 10, 1, 2)
# 		network.nodes[0].set_bill_of_materials(3, 11, 2, 2)
# 		network.nodes[0].set_bill_of_materials(15, 10, 2, 3)
# 		network.nodes[0].set_bill_of_materials(6, 11, 3, 4)
# 		network.nodes[0].set_bill_of_materials(16, 11, 3, 5)

# 		self.assertEqual(network.nodes[0].get_bill_of_materials(10, 1, 1), 5)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(10, 1, 2), 7)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(11, 2, 2), 3)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(10, 2, 3), 15)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(11, 3, 4), 6)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(11, 3, 5), 16)

# 	def test_multi_product_network7(self):
# 		"""Test that set_ and get_bill_of_materials() work correctly on 7-node multi-product instance.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_multi_product_network7()')

# 		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(None, 3, None), 4)
# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(1, 4, None), 1)
# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(1, 5, 4), 2.6)
# 		self.assertEqual(network.get_node_from_index(2).get_bill_of_materials(3, 5, 5), 6)
# 		self.assertEqual(network.get_node_from_index(2).get_bill_of_materials(3, None, None), 5)
# 		self.assertEqual(network.get_node_from_index(6).get_bill_of_materials(None, None, None), 1)
		
# 		network.get_node_from_index(0).set_bill_of_materials(500, None, 6, None)
# 		network.get_node_from_index(0).set_bill_of_materials(600, None, 5, 4)
# 		network.get_node_from_index(1).set_bill_of_materials(700, 1, 6, None)
# 		network.get_node_from_index(1).set_bill_of_materials(800, 1, None, None)

# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(None, 6, None), 500)
# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(None, 5, 4), 600)
# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(1, 6, None), 700)
# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(1, None, None), 800)

# 	def test_default_value_1node(self):
# 		"""Test that get_bill_of_materials() works correctly in a single-node system
# 		with a single product, in which case the BOM number for the node and the external
# 		supplier defaults to 1.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_default_value()')

# 		network = single_stage_system()

# 		self.assertEqual(network.nodes[0].get_bill_of_materials(), 1)

# 		# Now set BOM number explicitly.
# 		network.nodes[0].set_bill_of_materials(num_needed=6.3)
# 		self.assertEqual(network.nodes[0].get_bill_of_materials(), 6.3)

# 	def test_default_value_2node(self):
# 		"""Test that get_bill_of_materials() works correctly in a 2-node system
# 		when both the node and its predecessor are single product, in which case the 
# 		BOM number defaults to 1.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_default_value()')

# 		network = serial_system(2)

# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(predecessor_index=0), 1)

# 		# Now set BOM number explicitly.
# 		network.get_node_from_index(1).set_bill_of_materials(predecessor_index=0, num_needed=6.3)
# 		self.assertEqual(network.get_node_from_index(1).get_bill_of_materials(predecessor_index=0), 6.3)

# 	def test_default_value_mwor(self):
# 		"""Test that get_bill_of_materials() works correctly in a MWOR system
# 		when both the downstream node and one of its predecessors are single product, in which case the 
# 		BOM number defaults to 1.
# 		"""
# 		print_status('TestSetGetBillOfMaterials', 'test_default_value()')

# 		network = mwor_system(3)

# 		network.get_node_from_index(1).add_products([SupplyChainProduct(1), SupplyChainProduct(2)])
# 		network.get_node_from_index(2).add_products([SupplyChainProduct(2)])

# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(predecessor_index=1), 0)
# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(predecessor_index=2), 1)
# 		self.assertEqual(network.get_node_from_index(0).get_bill_of_materials(predecessor_index=3), 1)


# class TestBillOfMaterialsList(unittest.TestCase):
# 	@classmethod
# 	def set_up_class(cls):
# 		"""Called once, before any tests."""
# 		print_status('TestBillOfMaterialsList', 'set_up_class()')

# 	@classmethod
# 	def tear_down_class(cls):
# 		"""Called once, after all tests, if set_up_class successful."""
# 		print_status('TestBillOfMaterialsList', 'tear_down_class()')

# 	def test_mwor(self):
# 		"""Test that bill_of_materials works correctly on MWOR network.
# 		"""
# 		print_status('TestBillOfMaterialsList', 'test_mwor()')

# 		network = mwor_system(3)

# 		network.get_node_from_index(1).add_products([SupplyChainProduct(1), SupplyChainProduct(2)])
# 		network.get_node_from_index(2).add_products([SupplyChainProduct(2), SupplyChainProduct(3)])
# 		network.get_node_from_index(3).add_products([SupplyChainProduct(4), SupplyChainProduct(5)])

# 		node0 = network.get_node_from_index(0)

# 		node0.set_bill_of_materials( 5, None, 1, 1)
# 		node0.set_bill_of_materials( 7, None, 1, 2)
# 		node0.set_bill_of_materials( 3, None, 2, 2)
# 		node0.set_bill_of_materials(15, None, 2, 3)
# 		node0.set_bill_of_materials( 6, None, 3, 4)
# 		node0.set_bill_of_materials(16, None, 3, 5)

# 		bom0 = node0.bill_of_materials
# 		self.assertListEqual(bom0, [(5, 0, None, 1, 1), (7, 0, None, 1, 2), (3, 0, None, 2, 2), (15, 0, None, 2, 3), (6, 0, None, 3, 4), (16, 0, None, 3, 5)])
# 		bom1 = network.get_node_from_index(1).bill_of_materials
# 		self.assertListEqual(bom1, [(1, 1, 1, None, None), (1, 1, 2, None, None)])
# 		bom2 = network.get_node_from_index(2).bill_of_materials
# 		self.assertListEqual(bom2, [(1, 2, 2, None, None), (1, 2, 3, None, None)])
# 		bom3 = network.get_node_from_index(3).bill_of_materials
# 		self.assertListEqual(bom3, [(1, 3, 4, None, None), (1, 3, 5, None, None)])

# 	def test_multi_product_network7(self):
# 		"""Test that bill_of_materials works correctly on 5-node, 7-product network.
# 		"""
# 		print_status('TestBillOfMaterialsList', 'test_multi_product()')

# 		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

# 		self.assertSetEqual(
# 			set(network.get_node_from_index(0).bill_of_materials),
# 			{(1, 0, None, 4, None), (4, 0, None, 3, None)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(1).bill_of_materials),
# 			{(1, 1, 1, 4, None), (2.6, 1, 1, 5, 4), (5.1, 1, 1, 5, 5)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(2).bill_of_materials),
# 			{(3.8, 2, 2, 5, 5), (6, 2, 3, 5, 5), (1, 2, 3, 6, None), (5, 2, 3, None, None)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(3).bill_of_materials),
# 			{(1, 3, None, None, None)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(4).bill_of_materials),
# 			{(3, 4, None, None, None)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(5).bill_of_materials),
# 			{(16, 5, 5, None, None), (1, 5, 4, None, None)}
# 		)
# 		self.assertSetEqual(
# 			set(network.get_node_from_index(6).bill_of_materials),
# 			{(1, 6, None, None, None)}
# 		)


class TestRawMaterialSuppliers(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRawMaterialSuppliers', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRawMaterialSuppliers', 'tear_down_class()')

	def test_mwor_no_product(self):
		"""Test that raw_material_suppliers and raw_material_supplier_indices work correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestRawMaterialSuppliers', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=None), [nodes[1], nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=None), [1, 2, 3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77)

	def test_mwor_one_product(self):
		"""Test that raw_material_suppliers and raw_material_supplier_indices work correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestRawMaterialSuppliers', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		nodes[0].add_product(SupplyChainProduct(10))
		nodes[0].products[0].set_bill_of_materials(1, 5)
		nodes[0].products[0].set_bill_of_materials(2, 7)
		nodes[0].products[0].set_bill_of_materials(3, 3)
		nodes[0].products[0].set_bill_of_materials(4, 15)
		nodes[0].products[0].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=10), [nodes[1], nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=10), [1, 2, 3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product_index=None)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=None)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77)

	def test_mwor_multiple_products(self):
		"""Test that raw_material_suppliers_by_product and raw_material_supplier_indices_by_product work correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestRawMaterialSuppliers', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.get_node_from_index(1).add_products([prods[1], prods[2]])
		network.get_node_from_index(2).add_products([prods[2], prods[3]])
		network.get_node_from_index(3).add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=10), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=11), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=12), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=10), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=11), [2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=12), [3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product_index=None)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=None)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77)

	def test_multiproduct_5_7(self):
		"""Test that raw_material_suppliers_by_product and raw_material_supplier_indices_by_product work correctly on 5-node, 7-product network.
		"""
		print_status('TestRawMaterialSuppliers', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=0), [nodes[2]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=0), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=1), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=2), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=3), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=4), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=2), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=4), [nodes[4]])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=5), [None])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=6), [None])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=0), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=0), [2, 3])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=1), [2, 3])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=2), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=3), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=4), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=2), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=4), [4])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=5), [None])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=6), [None])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product_index=None)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=None)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77)
		

class TestGetNetworkBillOfMaterials(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetNetworkBillOfMaterials', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetNetworkBillOfMaterials', 'tear_down_class()')

	def test_mwor_no_product(self):
		"""Test that get_network_bill_of_materials and NBOM work correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestGetNetworkBillOfMaterials', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertEqual(nodes[0].get_network_bill_of_materials(None, 1, 1), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(None, nodes[1], 2), 1)
		self.assertEqual(nodes[0].NBOM(None, nodes[2], prods[2]), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(None, 2, prods[3]), 1)
		self.assertEqual(nodes[0].NBOM(None, 3, 4), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(None, nodes[3], prods[5]), 1)

		self.assertEqual(nodes[1].get_network_bill_of_materials(1, None, None), 1)
		self.assertEqual(nodes[1].NBOM(prods[2], None, None), 1)
		self.assertEqual(nodes[2].NBOM(2, None, None), 1)
		self.assertEqual(nodes[2].get_network_bill_of_materials(prods[3], None, None), 1)
		self.assertEqual(nodes[3].get_network_bill_of_materials(4, None, None), 1)
		self.assertEqual(nodes[3].NBOM(prods[5], None, None), 1)

		with self.assertRaises(ValueError):
			_ = nodes[0].get_network_bill_of_materials(3, 1, 1)
			_ = nodes[0].get_network_bill_of_materials(None, 1, 7)
			_ = nodes[1].get_network_bill_of_materials(1, 0, None)
			_ = nodes[0].NBOM(None, 1, 7)
			_ = nodes[0].get_network_bill_of_materials(None, None, 1)

	def test_mwor_one_product(self):
		"""Test that get_network_bill_of_materials and NBOM work correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestGetNetworkBillOfMaterials', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		prods[10] = SupplyChainProduct(10)
		nodes[0].add_product(prods[10])

		# First test without BOM.
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], 1, 1), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], nodes[1], 2), 1)
		self.assertEqual(nodes[0].NBOM(prods[10], nodes[2], prods[2]), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(10, 2, prods[3]), 1)
		self.assertEqual(nodes[0].NBOM(10, 3, 4), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(10, nodes[3], prods[5]), 1)

		# Then test with product and BOM.
		nodes[0].products[0].set_bill_of_materials(1, 5)
		nodes[0].products[0].set_bill_of_materials(2, 7)
		nodes[0].products[0].set_bill_of_materials(3, 3)
		nodes[0].products[0].set_bill_of_materials(4, 15)
		nodes[0].products[0].set_bill_of_materials(5, 6)

		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], 1, 1), 5)
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], nodes[1], 2), 7)
		self.assertEqual(nodes[0].NBOM(prods[10], nodes[2], prods[2]), 7)
		self.assertEqual(nodes[0].get_network_bill_of_materials(10, 2, prods[3]), 3)
		self.assertEqual(nodes[0].NBOM(10, 3, 4), 15)
		self.assertEqual(nodes[0].get_network_bill_of_materials(10, nodes[3], prods[5]), 6)

		self.assertEqual(nodes[1].get_network_bill_of_materials(1, None, None), 1)
		self.assertEqual(nodes[1].NBOM(prods[2], None, None), 1)
		self.assertEqual(nodes[2].NBOM(2, None, None), 1)
		self.assertEqual(nodes[2].get_network_bill_of_materials(prods[3], None, None), 1)
		self.assertEqual(nodes[3].get_network_bill_of_materials(4, None, None), 1)
		self.assertEqual(nodes[3].NBOM(prods[5], None, None), 1)

		with self.assertRaises(ValueError):
			_ = nodes[0].get_network_bill_of_materials(3, 1, 1)
			_ = nodes[0].get_network_bill_of_materials(None, 1, 7)
			_ = nodes[1].get_network_bill_of_materials(1, 0, None)
			_ = nodes[0].NBOM(None, 1, 7)

	def test_mwor_multiple_products(self):
		"""Test that get_network_bill_of_materials and NBOM work correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestGetNetworkBillOfMaterials', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.get_node_from_index(1).add_products([prods[1], prods[2]])
		network.get_node_from_index(2).add_products([prods[2], prods[3]])
		network.get_node_from_index(3).add_products([prods[4], prods[5]])

		prods[10] = SupplyChainProduct(10)
		prods[11] = SupplyChainProduct(11)
		prods[12] = SupplyChainProduct(12)
		nodes[0].add_products([prods[10], prods[11], prods[12]])

		# First test without BOM.
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], 1, 1), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[11], nodes[1], 2), 1)
		self.assertEqual(nodes[0].NBOM(prods[10], nodes[2], prods[2]), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(12, 2, prods[3]), 1)
		self.assertEqual(nodes[0].NBOM(10, 3, 4), 1)
		self.assertEqual(nodes[0].get_network_bill_of_materials(12, nodes[3], prods[5]), 1)

		# Then test with products and BOM.
		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], 1, 1), 5)
		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[10], nodes[1], 2), 7)
		self.assertEqual(nodes[0].NBOM(prods[11], nodes[2], prods[3]), 3)
		self.assertEqual(nodes[0].get_network_bill_of_materials(11, 3, prods[4]), 15)
		self.assertEqual(nodes[0].NBOM(10, 2, 2), 7)
		self.assertEqual(nodes[0].get_network_bill_of_materials(12, nodes[3], prods[5]), 6)

		self.assertEqual(nodes[1].get_network_bill_of_materials(1, None, None), 1)
		self.assertEqual(nodes[1].NBOM(prods[2], None, None), 1)
		self.assertEqual(nodes[2].NBOM(2, None, None), 1)
		self.assertEqual(nodes[2].get_network_bill_of_materials(prods[3], None, None), 1)
		self.assertEqual(nodes[3].get_network_bill_of_materials(4, None, None), 1)
		self.assertEqual(nodes[3].NBOM(prods[5], None, None), 1)

		with self.assertRaises(ValueError):
			_ = nodes[0].get_network_bill_of_materials(3, 1, 1)
			_ = nodes[0].get_network_bill_of_materials(None, 1, 7)
			_ = nodes[1].get_network_bill_of_materials(1, 0, None)
			_ = nodes[0].NBOM(None, 1, 7)
			

	def test_multiproduct_5_7(self):
		"""Test that get_network_bill_of_materials and NBOM work correctly on 5-node, 7-product network.
		"""
		print_status('TestGetNetworkBillOfMaterials', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}
		prods = {i: network.products_by_index[i] for i in network.product_indices}

		self.assertEqual(nodes[0].get_network_bill_of_materials(prods[0], 2, 2), 2.5)
		self.assertEqual(nodes[0].get_network_bill_of_materials(0, nodes[2], prods[3]), 7)
		self.assertEqual(nodes[0].get_network_bill_of_materials(0, None, prods[3]), 7)
		self.assertEqual(nodes[1].get_network_bill_of_materials(prods[0], 2, 2), 2.5)
		self.assertEqual(nodes[1].get_network_bill_of_materials(0, nodes[2], prods[3]), 7)
		self.assertEqual(nodes[1].get_network_bill_of_materials(0, nodes[3], 4), 0)
		self.assertEqual(nodes[1].get_network_bill_of_materials(1, nodes[2], prods[3]), 10)
		self.assertEqual(nodes[1].get_network_bill_of_materials(1, 2, 4), 3.8)
		self.assertEqual(nodes[1].get_network_bill_of_materials(prods[1], nodes[3], prods[4]), 3.8)
		self.assertEqual(nodes[2].get_network_bill_of_materials(2, nodes[4], 5), 0.2)
		self.assertEqual(nodes[2].get_network_bill_of_materials(2, None, 5), 0.2)
		self.assertEqual(nodes[2].get_network_bill_of_materials(2, 4, prods[6]), 0)
		self.assertEqual(nodes[2].get_network_bill_of_materials(3, 4, prods[5]), 2)
		self.assertEqual(nodes[3].get_network_bill_of_materials(prods[2], 4, 5), 0.2)
		self.assertEqual(nodes[3].get_network_bill_of_materials(prods[2], 4, prods[6]), 0)
		self.assertEqual(nodes[3].get_network_bill_of_materials(4, nodes[4], 5), 0)
		self.assertEqual(nodes[3].get_network_bill_of_materials(4, nodes[4], 6), 50)

		self.assertEqual(nodes[4].get_network_bill_of_materials(5, None, None), 1)
		self.assertEqual(nodes[4].get_network_bill_of_materials(6, None, None), 1)
		
		with self.assertRaises(ValueError):
			_ = nodes[0].get_network_bill_of_materials(3, 1, 1)
			_ = nodes[0].get_network_bill_of_materials(0, 2, 77)
			_ = nodes[1].get_network_bill_of_materials(0, None, 4)
		
class TestRawMaterials(unittest.TestCase):
	"""This class tests all of the various raw material functions for SupplyChainNode.
	"""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestRawMaterials', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestRawMaterials', 'tear_down_class()')

	def test_mwor_no_product(self):
		"""Test that raw_materials_by_product and raw_material_indices_by_product work correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		# Raw materials by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=True), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=True), list(prods.values()))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=False), [])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=True), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[1], nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), [nodes[1], nodes[2], nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=True), [1])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=True), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=True), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=True), [nodes[1]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=True), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=True), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=True), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=True), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=False)
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=False), [])

	def test_mwor_one_product(self):
		"""Test that raw_materials_by_product and raw_material_indices_by_product work correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		nodes[0].add_product(SupplyChainProduct(10))
		nodes[0].products[0].set_bill_of_materials(1, 5)
		nodes[0].products[0].set_bill_of_materials(2, 7)
		nodes[0].products[0].set_bill_of_materials(3, 3)
		nodes[0].products[0].set_bill_of_materials(4, 15)
		nodes[0].products[0].set_bill_of_materials(5, 6)

		# Raw materials by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=True), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=True), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=True), list(prods.values()))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=False), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=False), list(prods.keys()))
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=False), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), list(prods.values()))
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=False), list(prods.values()))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=True), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[1], nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=nodes[0].product_indices[0], network_BOM=True), [nodes[1], nodes[2], nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=False), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [1, 2, 3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=False), [nodes[1], nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=nodes[0].product_indices[0], network_BOM=False), [nodes[1], nodes[2], nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=True), [1])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=True), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=True), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=True), [nodes[1]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=True), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=True), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=True), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=True), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=False), [1])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=False), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=False), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=False), [3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=False), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=False), [nodes[1]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=False), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=False), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=False), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=False), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=False)

	def test_mwor_multiple_products(self):
		"""Test that raw_materials_by_product and raw_material_indices_by_product work correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.get_node_from_index(1).add_products([prods[1], prods[2]])
		network.get_node_from_index(2).add_products([prods[2], prods[3]])
		network.get_node_from_index(3).add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		# Raw materials by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=10, network_BOM=True), [1, 2])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=11, network_BOM=True), [3, 4])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=12, network_BOM=True), [5])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=True), [1, 2, 3, 4, 5])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=10, network_BOM=True), [prods[1], prods[2]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=11, network_BOM=True), [prods[3], prods[4]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=12, network_BOM=True), [prods[5]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=True), [prods[1], prods[2], prods[3], prods[4], prods[5]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(network_BOM=True)
			_ = nodes[0].raw_materials_by_product(network_BOM=True)
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=10, network_BOM=False), [1, 2])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=11, network_BOM=False), [3, 4])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=12, network_BOM=False), [5])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=False), [1, 2, 3, 4, 5])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=10, network_BOM=False), [prods[1], prods[2]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=11, network_BOM=False), [prods[3], prods[4]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=12, network_BOM=False), [prods[5]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=False), [prods[1], prods[2], prods[3], prods[4], prods[5]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_indices_by_product(network_BOM=False)
			_ = nodes[0].raw_materials_by_product(network_BOM=False)
			_ = nodes[0].raw_material_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=10, network_BOM=True), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=11, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=12, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=10, network_BOM=True), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=11, network_BOM=True), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=12, network_BOM=True), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(network_BOM=True)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=10, network_BOM=False), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=11, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=12, network_BOM=False), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=10, network_BOM=False), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=11, network_BOM=False), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=12, network_BOM=False), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_product(network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=True), [1])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=True), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=True), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=True), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=True), [nodes[1]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=True), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=True), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=True), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=True), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=1, network_BOM=False), [1])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=False), [1, 2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=False), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=False), [3])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=False), [3])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=1, network_BOM=False), [nodes[1]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=2, network_BOM=False), [nodes[1], nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=3, network_BOM=False), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=4, network_BOM=False), [nodes[3]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_raw_material(rm_index=5, network_BOM=False), [nodes[3]])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=False)

	def test_multiproduct_5_7(self):
		"""Test that raw_materials_by_product and raw_material_indices_by_product work correctly on 5-node, 7-product network.
		"""
		print_status('TestRawMaterials', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}
		prods = network.products_by_index

		# Raw materials by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=True), [2, 3])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=0, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=True), [2, 3])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index=0, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index=1, network_BOM=True), [3, 4])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index='all', network_BOM=True), [2, 3, 4])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=2, network_BOM=True), [5])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=3, network_BOM=True), [5])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=4, network_BOM=True), [6])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index='all', network_BOM=True), [5, 6])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index=2, network_BOM=True), [5])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index=4, network_BOM=True), [6])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index='all', network_BOM=True), [5, 6])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index=5, network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index=6, network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index='all', network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=True), [prods[2], prods[3]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=0, network_BOM=True), [prods[2], prods[3]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=True), [prods[2], prods[3]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index=0, network_BOM=True), [prods[2], prods[3]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index=1, network_BOM=True), [prods[3], prods[4]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index='all', network_BOM=True), [prods[2], prods[3], prods[4]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=2, network_BOM=True), [prods[5]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=3, network_BOM=True), [prods[5]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=4, network_BOM=True), [prods[6]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index='all', network_BOM=True), [prods[5], prods[6]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index=2, network_BOM=True), [prods[5]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index=4, network_BOM=True), [prods[6]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index='all', network_BOM=True), [prods[5], prods[6]])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index=5, network_BOM=True), [nodes[4]._external_supplier_dummy_product])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index=6, network_BOM=True), [nodes[4]._external_supplier_dummy_product])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index='all', network_BOM=True), [nodes[4]._external_supplier_dummy_product])
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_indices_by_product(network_BOM=True)
			_ = nodes[1].raw_materials_by_product(network_BOM=True)
			_ = nodes[1].raw_material_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[1].raw_materials_by_product(product_index=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_indices_by_product(network_BOM=False), [2, 3])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index=0, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[0].raw_material_indices_by_product(product_index='all', network_BOM=False), [2, 3])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index=0, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index=1, network_BOM=False), [3, 4])
		self.assertListEqual(nodes[1].raw_material_indices_by_product(product_index='all', network_BOM=False), [2, 3, 4])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=2, network_BOM=False), [5])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=3, network_BOM=False), [5])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index=4, network_BOM=False), [6])
		self.assertListEqual(nodes[2].raw_material_indices_by_product(product_index='all', network_BOM=False), [5, 6])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index=2, network_BOM=False), [5])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index=4, network_BOM=False), [6])
		self.assertListEqual(nodes[3].raw_material_indices_by_product(product_index='all', network_BOM=False), [5, 6])
		self.assertListEqual(nodes[0].raw_materials_by_product(network_BOM=False), [prods[2], prods[3]])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index=5, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index=6, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_material_indices_by_product(product_index='all', network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index=0, network_BOM=False), [prods[2], prods[3]])
		self.assertListEqual(nodes[0].raw_materials_by_product(product_index='all', network_BOM=False), [prods[2], prods[3]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index=0, network_BOM=False), [prods[2], prods[3]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index=1, network_BOM=False), [prods[3], prods[4]])
		self.assertListEqual(nodes[1].raw_materials_by_product(product_index='all', network_BOM=False), [prods[2], prods[3], prods[4]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=2, network_BOM=False), [prods[5]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=3, network_BOM=False), [prods[5]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index=4, network_BOM=False), [prods[6]])
		self.assertListEqual(nodes[2].raw_materials_by_product(product_index='all', network_BOM=False), [prods[5], prods[6]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index=2, network_BOM=False), [prods[5]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index=4, network_BOM=False), [prods[6]])
		self.assertListEqual(nodes[3].raw_materials_by_product(product_index='all', network_BOM=False), [prods[5], prods[6]])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index=5, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index=6, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_materials_by_product(product_index='all', network_BOM=False), [])
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_indices_by_product(network_BOM=False)
			_ = nodes[1].raw_materials_by_product(network_BOM=False)
			_ = nodes[1].raw_material_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[1].raw_materials_by_product(product_index=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=True), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=0, network_BOM=True), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=0, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=1, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=2, network_BOM=True), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=3, network_BOM=True), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=4, network_BOM=True), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=2, network_BOM=True), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=4, network_BOM=True), [4])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=5, network_BOM=True), [None])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=6, network_BOM=True), [None])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=0, network_BOM=True), [nodes[2]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=0, network_BOM=True), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=1, network_BOM=True), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=2, network_BOM=True), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=3, network_BOM=True), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=4, network_BOM=True), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=2, network_BOM=True), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=4, network_BOM=True), [nodes[4]])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=5, network_BOM=True), [None])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=6, network_BOM=True), [None])
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_supplier_indices_by_product(network_BOM=True)
			_ = nodes[1].raw_material_suppliers_by_product(network_BOM=True)
			_ = nodes[1].raw_material_supplier_indices_by_product(product_index=77, network_BOM=True)
			_ = nodes[1].raw_material_suppliers_by_product(product_index=77, network_BOM=True)

		# # Raw material suppliers by product, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(network_BOM=False), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_product(product_index=0, network_BOM=False), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=0, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_product(product_index=1, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=2, network_BOM=False), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=3, network_BOM=False), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_product(product_index=4, network_BOM=False), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=2, network_BOM=False), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_product(product_index=4, network_BOM=False), [4])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=5, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_product(product_index=6, network_BOM=False), [])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(network_BOM=False), [nodes[2]])
		self.assertListEqual(nodes[0].raw_material_suppliers_by_product(product_index=0, network_BOM=False), [nodes[2]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=0, network_BOM=False), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[1].raw_material_suppliers_by_product(product_index=1, network_BOM=False), [nodes[2], nodes[3]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=2, network_BOM=False), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=3, network_BOM=False), [nodes[4]])
		self.assertListEqual(nodes[2].raw_material_suppliers_by_product(product_index=4, network_BOM=False), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=2, network_BOM=False), [nodes[4]])
		self.assertListEqual(nodes[3].raw_material_suppliers_by_product(product_index=4, network_BOM=False), [nodes[4]])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=5, network_BOM=False), [])
		self.assertListEqual(nodes[4].raw_material_suppliers_by_product(product_index=6, network_BOM=False), [])
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_supplier_indices_by_product(network_BOM=False)
			_ = nodes[1].raw_material_suppliers_by_product(network_BOM=False)
			_ = nodes[1].raw_material_supplier_indices_by_product(product_index=77, network_BOM=False)
			_ = nodes[1].raw_material_suppliers_by_product(product_index=77, network_BOM=False)

		# # Raw material suppliers by raw_material, network_BOM=True.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=True), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=True), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=True), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=True), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_raw_material(rm_index=6, network_BOM=True), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=True), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_raw_material(rm_index=6, network_BOM=True), [4])
		self.assertListEqual(nodes[4].raw_material_supplier_indices_by_raw_material(rm_index=nodes[4]._external_supplier_dummy_product.index, network_BOM=True), [None])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=True)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=True)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=77, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=77, network_BOM=True)

		# # Raw material suppliers by raw_material, network_BOM=False.
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=False), [2])
		self.assertListEqual(nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=False), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=2, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=3, network_BOM=False), [2])
		self.assertListEqual(nodes[1].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=False), [2, 3])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=False), [4])
		self.assertListEqual(nodes[2].raw_material_supplier_indices_by_raw_material(rm_index=6, network_BOM=False), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_raw_material(rm_index=5, network_BOM=False), [4])
		self.assertListEqual(nodes[3].raw_material_supplier_indices_by_raw_material(rm_index=6, network_BOM=False), [4])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=4, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=None, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=None, network_BOM=False)
			_ = nodes[0].raw_material_supplier_indices_by_raw_material(rm_index=77, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(rm_index=77, network_BOM=False)
			_ = nodes[4].raw_material_supplier_indices_by_raw_material(rm_index=nodes[4]._external_supplier_dummy_product.index, network_BOM=False)
		
		
class TestProductsByRawMaterial(unittest.TestCase):
	"""This class tests all of the various raw material functions for SupplyChainNode.
	"""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestProductsByRawMaterial', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestProductsByRawMaterial', 'tear_down_class()')

	def test_mwor_no_product(self):
		"""Test that products_by_raw_materials and product_indices_by_raw_materials work correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=1), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=2), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=3), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=4), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=5), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [1, 2])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=None), [1, 2])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [2, 3])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=None), [2, 3])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [4, 5])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=None), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=1), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=2), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=3), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=4), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=5), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].product_indices_by_raw_material(rm_index=77)
			_ = nodes[0].product_indices_by_raw_material(rm_index=None)

	def test_mwor_one_product(self):
		"""Test that products_by_raw_materials and product_indices_by_raw_materials work correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		nodes[0].add_product(SupplyChainProduct(10))
		nodes[0].products[0].set_bill_of_materials(1, 5)
		nodes[0].products[0].set_bill_of_materials(2, 7)
		nodes[0].products[0].set_bill_of_materials(3, 3)
		nodes[0].products[0].set_bill_of_materials(4, 15)
		nodes[0].products[0].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=1), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=2), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=3), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=4), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=5), [10])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [1, 2])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=None), [1, 2])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [2, 3])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=None), [2, 3])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [4, 5])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=None), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=1), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=2), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=3), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=4), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=5), [nodes[0].products[0]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].product_indices_by_raw_material(rm_index=77)
			_ = nodes[0].product_indices_by_raw_material(rm_index=None)

	def test_mwor_multiple_products(self):
		"""Test that products_by_raw_materials and product_indices_by_raw_materials work correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.get_node_from_index(1).add_products([prods[1], prods[2]])
		network.get_node_from_index(2).add_products([prods[2], prods[3]])
		network.get_node_from_index(3).add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=1), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=2), [10])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=3), [11])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=4), [11])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=5), [12])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [1, 2])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=None), [1, 2])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [2, 3])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=None), [2, 3])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [4, 5])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=None), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=1), [nodes[0].products_by_index[10]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=2), [nodes[0].products_by_index[10]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=3), [nodes[0].products_by_index[11]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=4), [nodes[0].products_by_index[11]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=5), [nodes[0].products_by_index[12]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].product_indices_by_raw_material(rm_index=77)
			_ = nodes[0].product_indices_by_raw_material(rm_index=None)

	def test_multiproduct_5_7(self):
		"""Test that products_by_raw_materials and product_indices_by_raw_materials work correctly on 5-node, 7-product network.
		"""
		print_status('TestProductsByRawMaterial', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.get_node_from_index(i) for i in network.node_indices}
		prods = network.products_by_index

		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=2), [0])
		self.assertListEqual(nodes[0].product_indices_by_raw_material(rm_index=3), [0])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=2), [0])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=3), [0, 1])
		self.assertListEqual(nodes[1].product_indices_by_raw_material(rm_index=4), [1])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=5), [2, 3])
		self.assertListEqual(nodes[2].product_indices_by_raw_material(rm_index=6), [4])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=5), [2])
		self.assertListEqual(nodes[3].product_indices_by_raw_material(rm_index=6), [4])
		self.assertListEqual(nodes[4].product_indices_by_raw_material(rm_index=nodes[4]._external_supplier_dummy_product.index), [5, 6])

		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=2), [prods[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(rm_index=3), [prods[0]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=2), [prods[0]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=3), [prods[0], prods[1]])
		self.assertListEqual(nodes[1].products_by_raw_material(rm_index=4), [prods[1]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=5), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(rm_index=6), [prods[4]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=5), [prods[2]])
		self.assertListEqual(nodes[3].products_by_raw_material(rm_index=6), [prods[4]])
		self.assertListEqual(nodes[4].products_by_raw_material(rm_index=nodes[4]._external_supplier_dummy_product.index), [prods[5], prods[6]])

		with self.assertRaises(ValueError):
			_ = nodes[0].product_indices_by_raw_material(rm_index=77)
			_ = nodes[0].product_indices_by_raw_material(rm_index=4)
			_ = nodes[0].product_indices_by_raw_material(rm_index=5)
			_ = nodes[0].product_indices_by_raw_material(rm_index=None)

		
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

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, math.sqrt(32))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, math.sqrt(16))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, math.sqrt(16))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(6).derived_demand_standard_deviation, math.sqrt(8))

	def test_rong_atan_snyder_figure_1b(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(b).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1b()')

		network = load_instance("rong_atan_snyder_figure_1b")

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, math.sqrt(64))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, math.sqrt(40))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, math.sqrt(24))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(6).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(7).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(8).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(9).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(10).derived_demand_standard_deviation, math.sqrt(8))

	def test_rong_atan_snyder_figure_1c(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(c).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1c()')

		network = load_instance("rong_atan_snyder_figure_1c")

		self.assertAlmostEqual(network.get_node_from_index(0).derived_demand_standard_deviation, math.sqrt(32))
		self.assertAlmostEqual(network.get_node_from_index(1).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(2).derived_demand_standard_deviation, math.sqrt(24))
		self.assertAlmostEqual(network.get_node_from_index(3).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(4).derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.get_node_from_index(5).derived_demand_standard_deviation, math.sqrt(8))



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
			
	def test_multiproduct_5_7(self):
		"""Test deep_equal_to() for nodes in 5-node, 7-product network.
		"""
		print_status('TestDeepEqualTo', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		node_copies = [copy.deepcopy(n) for n in network.nodes]

		# Equal nodes.
		for i in range(len(network.nodes)):
			self.assertTrue(node_copies[i].deep_equal_to(network.nodes[i]))
			self.assertTrue(network.nodes[i].deep_equal_to(node_copies[i]))

		# Unequal nodes due to parameters.
		network.nodes[0].local_holding_cost = 99
		self.assertFalse(node_copies[0].deep_equal_to(network.nodes[0]))
		self.assertFalse(network.nodes[0].deep_equal_to(node_copies[0]))
		network.nodes[2].demand_source.standard_deviation = 99
		self.assertFalse(node_copies[2].deep_equal_to(network.nodes[2]))
		self.assertFalse(network.nodes[2].deep_equal_to(node_copies[2]))

		# Unequal networks due to missing policy.
		node_copies[2].inventory_policy = None
		self.assertFalse(node_copies[2].deep_equal_to(network.nodes[2]))
		self.assertFalse(network.nodes[2].deep_equal_to(node_copies[2]))
			

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

		# Convert successors and predecessors back to node objects. Replace network and product objects.
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
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}

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

		# Convert successors and predecessors back to node objects. Replace network and product objects.
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
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}

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

		# Convert successors and predecessors back to node objects. Replace network and product objects.
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
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}

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

		# Convert successors and predecessors back to node objects. Replace network and product objects.
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
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}

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

	def test_multiproduct_5_7(self):
		"""Test that to_dict() and from_dict() correctly convert SupplyChainNode object to and from dict
		in 5-stage 7-product network.
		"""
		print_status('TestNodeToFromDict', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		# Convert nodes to dicts.
		node_dicts = [n.to_dict() for n in network.nodes]

		# Convert dicts back to nodes.
		dict_nodes = [SupplyChainNode.from_dict(d) for d in node_dicts]

		# Convert successors and predecessors back to node objects. Replace network objects.
		# Fill products.
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
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}
			
			prods = n.product_indices
			n.remove_products('all')
			for prod in prods:
				n.add_product(network.products_by_index[prod])

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))


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
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		self.assertAlmostEqual(nodes[1].state_vars[22].inventory_level[dps[1]], 0.497397132, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].inventory_level[dps[2]], 0.038666224, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].inventory_level[dps[3]], -0.832602868, places=6)
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
		self.assertAlmostEqual(nodes[1].state_vars[22].in_transit(), 5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].in_transit(), 4.658730908, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].in_transit(), 6.031269092479092+5.491333775514212, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].on_order(), 5.992602868, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].on_order(), 5.491333776, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].on_order(), 6.031269092479092+5.491333775514212, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[22].raw_material_aggregate(), 0, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[22].raw_material_aggregate(), 0, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[22].raw_material_aggregate(), 0, places=6)
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
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		self.assertAlmostEqual(nodes[1].state_vars[37].inventory_level[dps[1]], IL1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].inventory_level[dps[2]], IL2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].inventory_level[dps[3]], IL3, places=6)
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
		self.assertAlmostEqual(nodes[1].state_vars[37].in_transit(), IT1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].in_transit(), IT2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].in_transit(), IT3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].on_order(), OO1, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].on_order(), OO2, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].on_order(), OO3, places=6)
		self.assertAlmostEqual(nodes[1].state_vars[37].raw_material_aggregate(), 0, places=6)
		self.assertAlmostEqual(nodes[2].state_vars[37].raw_material_aggregate(), 0, places=6)
		self.assertAlmostEqual(nodes[3].state_vars[37].raw_material_aggregate(), 0, places=6)
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
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		self.assertEqual(nodes[0].state_vars[22].inventory_level[dps[0]], IL0)
		self.assertEqual(nodes[1].state_vars[22].inventory_level[dps[1]], IL1)
		self.assertEqual(nodes[2].state_vars[22].inventory_level[dps[2]], IL2)
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
		self.assertEqual(nodes[0].state_vars[22].in_transit(), IT0)
		self.assertEqual(nodes[1].state_vars[22].in_transit(), IT1)
		self.assertEqual(nodes[2].state_vars[22].in_transit(), IT2)
		self.assertEqual(nodes[0].state_vars[22].on_order_by_predecessor[1][dps[1]], OO01)
		self.assertEqual(nodes[0].state_vars[22].on_order_by_predecessor[2][dps[2]], OO02)
		self.assertEqual(nodes[0].state_vars[22].on_order(), OO0)
		self.assertEqual(nodes[1].state_vars[22].on_order(), OO1)
		self.assertEqual(nodes[2].state_vars[22].on_order(), OO2)
		self.assertEqual(nodes[0].state_vars[22].raw_material_inventory[dps[1]], RM01)
		self.assertEqual(nodes[0].state_vars[22].raw_material_inventory[dps[2]], RM02)
		self.assertEqual(nodes[0].state_vars[22].raw_material_aggregate(), RM0)
		self.assertEqual(nodes[1].state_vars[22].raw_material_aggregate(), RM1)
		self.assertEqual(nodes[2].state_vars[22].raw_material_aggregate(), RM2)
		# self.assertEqual(nodes[0].state_vars[22].inventory_position(predecessor_index=1), IL0+OO01+RM01)
		# self.assertEqual(nodes[0].state_vars[22].inventory_position(predecessor_index=2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[22].inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[22].inventory_position(), IL1+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[22].inventory_position(), IL2+OO2+RM2)
		self.assertEqual(nodes[0].state_vars[22].echelon_on_hand_inventory, OH0)
		self.assertEqual(nodes[1].state_vars[22].echelon_on_hand_inventory, OH0+IT10+OH1)
		self.assertEqual(nodes[2].state_vars[22].echelon_on_hand_inventory, OH0+IT20+OH2)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[22].echelon_inventory_level, OH0+IT10+OH1-BO0)
		self.assertEqual(nodes[2].state_vars[22].echelon_inventory_level, OH0+IT20+OH2-BO0)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(predecessor_index=1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(predecessor_index=2), IL0+OO02+RM02)
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
		dps = {n.index: n._dummy_product.index for n in network.nodes}

		self.assertEqual(nodes[0].state_vars[per].inventory_level[dps[0]], IL0)
		self.assertEqual(nodes[1].state_vars[per].inventory_level[dps[1]], IL1)
		self.assertEqual(nodes[2].state_vars[per].inventory_level[dps[2]], IL2)
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
		self.assertEqual(nodes[0].state_vars[per].in_transit(), IT0)
		self.assertEqual(nodes[1].state_vars[per].in_transit(), IT1)
		self.assertEqual(nodes[2].state_vars[per].in_transit(), IT2)
		self.assertEqual(nodes[0].state_vars[per].on_order_by_predecessor[1][dps[1]], OO01)
		self.assertEqual(nodes[0].state_vars[per].on_order_by_predecessor[2][dps[2]], OO02)
		self.assertEqual(nodes[0].state_vars[per].on_order(), OO0)
		self.assertEqual(nodes[1].state_vars[per].on_order(), OO1)
		self.assertEqual(nodes[2].state_vars[per].on_order(), OO2)
		self.assertEqual(nodes[0].state_vars[per].raw_material_inventory[dps[1]], RM01)
		self.assertEqual(nodes[0].state_vars[per].raw_material_inventory[dps[2]], RM02)
		self.assertEqual(nodes[0].state_vars[per].raw_material_aggregate(), RM0)
		self.assertEqual(nodes[1].state_vars[per].raw_material_aggregate(), RM1)
		self.assertEqual(nodes[2].state_vars[per].raw_material_aggregate(), RM2)
		# self.assertEqual(nodes[0].state_vars[per].inventory_position(predecessor_index=1), IL0+OO01+RM01)
		# self.assertEqual(nodes[0].state_vars[per].inventory_position(predecessor_index=2), IL0+OO02+RM02)
		self.assertEqual(nodes[0].state_vars[per].inventory_position(), IL0+OO0+RM0)
		self.assertEqual(nodes[1].state_vars[per].inventory_position(), IL1+OO1+RM1)
		self.assertEqual(nodes[2].state_vars[per].inventory_position(), IL2+OO2+RM2)
		self.assertEqual(nodes[0].state_vars[per].echelon_on_hand_inventory, OH0)
		self.assertEqual(nodes[1].state_vars[per].echelon_on_hand_inventory, OH0+IT01+OH1)
		self.assertEqual(nodes[2].state_vars[per].echelon_on_hand_inventory, OH0+IT02+OH2)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_level, IL0)
		self.assertEqual(nodes[1].state_vars[per].echelon_inventory_level, OH0+IT01+OH1-BO0)
		self.assertEqual(nodes[2].state_vars[per].echelon_inventory_level, OH0+IT02+OH2-BO0)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(predecessor_index=1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(predecessor_index=2), IL0+OO02+RM02)
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

		n1 = SupplyChainNode(index=1)
		n2 = SupplyChainNode(index=1)
		n1.initialize(index=None)
		self.assertTrue(n1.deep_equal_to(n2))
		self.assertEqual(n1.products, [n1._dummy_product])

		n1 = SupplyChainNode(index=1, local_holding_cost=2, stockout_cost=50, shipment_lead_time=3)
		n2 = SupplyChainNode(index=1)
		n1.initialize()
		self.assertTrue(n1.deep_equal_to(n2))
		self.assertEqual(n1.products, [n1._dummy_product])

		with self.assertRaises(ValueError):
			n1.initialize(index=-5)
			n1.index = None
			n1.initialize(index=None)


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
