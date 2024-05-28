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
from stockpyl.helpers import compare_unhashable_lists

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


class TestHasExternalSupplierCustomer(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestHasExternalSupplierCustomer', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestHasExternalSupplierCustomer', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test external supplier/customer checks in Example 6.1.
		"""
		print_status('TestHasExternalSupplierCustomer', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		self.assertTrue(nodes[3].has_external_supplier)
		self.assertFalse(nodes[3].has_external_customer)
		self.assertFalse(nodes[2].has_external_supplier)
		self.assertFalse(nodes[2].has_external_customer)
		self.assertFalse(nodes[1].has_external_supplier)
		self.assertTrue(nodes[1].has_external_customer)

	def test_example_6_1(self):
		"""Test external supplier/customer checks in Example 6.1.
		"""
		print_status('TestHasExternalSupplierCustomer', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		self.assertTrue(nodes[3].has_external_supplier)
		self.assertFalse(nodes[3].has_external_customer)
		self.assertFalse(nodes[2].has_external_supplier)
		self.assertFalse(nodes[2].has_external_customer)
		self.assertFalse(nodes[1].has_external_supplier)
		self.assertTrue(nodes[1].has_external_customer)

	def test_assembly_3_stage(self):
		"""Test external supplier/customer checks in assembly 3 stage.
		"""
		print_status('TestHasExternalSupplierCustomer', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")
		nodes = {n.index: n for n in network.nodes}

		self.assertTrue(nodes[1].has_external_supplier)
		self.assertFalse(nodes[1].has_external_customer)
		self.assertTrue(nodes[2].has_external_supplier)
		self.assertFalse(nodes[2].has_external_customer)
		self.assertFalse(nodes[0].has_external_supplier)
		self.assertTrue(nodes[0].has_external_customer)

	def test_rosling_figure_1(self):
		"""Test external supplier/customer checks in Rosling Figure 1.
		"""
		print_status('TestHasExternalSupplierCustomer', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")
		nodes = {n.index: n for n in network.nodes}

		self.assertFalse(nodes[1].has_external_supplier)
		self.assertTrue(nodes[1].has_external_customer)
		self.assertFalse(nodes[2].has_external_supplier)
		self.assertFalse(nodes[2].has_external_customer)
		self.assertFalse(nodes[3].has_external_supplier)
		self.assertFalse(nodes[3].has_external_customer)
		self.assertFalse(nodes[4].has_external_supplier)
		self.assertFalse(nodes[4].has_external_customer)
		self.assertTrue(nodes[5].has_external_supplier)
		self.assertFalse(nodes[5].has_external_customer)
		self.assertTrue(nodes[6].has_external_supplier)
		self.assertFalse(nodes[6].has_external_customer)
		self.assertTrue(nodes[7].has_external_supplier)
		self.assertFalse(nodes[7].has_external_customer)

	def test_multiproduct_5_7(self):
		"""Test external supplier/customer checks in 5-node, 7-product system.
		"""
		print_status('TestHasExternalSupplierCustomer', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}

		self.assertFalse(nodes[0].has_external_supplier)
		self.assertTrue(nodes[0].has_external_customer)
		self.assertFalse(nodes[1].has_external_supplier)
		self.assertTrue(nodes[1].has_external_customer)
		self.assertFalse(nodes[2].has_external_supplier)
		self.assertFalse(nodes[2].has_external_customer)
		self.assertFalse(nodes[3].has_external_supplier)
		self.assertFalse(nodes[3].has_external_customer)
		self.assertTrue(nodes[4].has_external_supplier)
		self.assertFalse(nodes[4].has_external_customer)


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
			desc[n.index] = n.descendants

		self.assertEqual(desc[1], [])
		self.assertEqual(desc[2], [network.nodes_by_index[1]])
		self.assertEqual(desc[3], [network.nodes_by_index[1], network.nodes_by_index[2]])

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

		desc = {i: network.nodes_by_index[i].descendants for i in network.node_indices}

		self.assertEqual(desc[0], [])
		self.assertEqual(desc[1], [])
		self.assertEqual(desc[2], [network.nodes_by_index[0], network.nodes_by_index[1]])
		self.assertEqual(desc[3], [network.nodes_by_index[1]])
		self.assertEqual(desc[4], [network.nodes_by_index[0], network.nodes_by_index[1], network.nodes_by_index[2], network.nodes_by_index[3]])



class TestPredecessors(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPredecessors', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPredecessors', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test ancestors for 3-node serial system in Example 6.1.
		"""
		print_status('TestPredecessors', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		self.assertEqual(nodes[1].predecessor_indices(), [2])
		self.assertEqual(nodes[2].predecessor_indices(), [3])
		self.assertEqual(nodes[3].predecessor_indices(), [])
		self.assertEqual(nodes[1].predecessors(), [nodes[2]])
		self.assertEqual(nodes[2].predecessors(), [nodes[3]])
		self.assertEqual(nodes[3].predecessors(), [])

	def test_4_node_owmr(self):
		"""Test ancestors for 4-node OWMR system.
		"""
		print_status('TestPredecessors', 'test_4_node_owmr()')

		network = SupplyChainNetwork()

		nodes = []
		for i in range(4):
			nodes.append(SupplyChainNode(i))

		network.add_node(nodes[0])
		network.add_successor(nodes[0], nodes[1])
		network.add_successor(nodes[0], nodes[2])
		network.add_successor(nodes[0], nodes[3])

		nodes = {n.index: n for n in network.nodes}

		self.assertEqual(nodes[0].predecessor_indices(), [])
		self.assertEqual(nodes[1].predecessor_indices(), [0])
		self.assertEqual(nodes[2].predecessor_indices(), [0])
		self.assertEqual(nodes[3].predecessor_indices(), [0])
		self.assertEqual(nodes[0].predecessors(), [])
		self.assertEqual(nodes[1].predecessors(), [nodes[0]])
		self.assertEqual(nodes[2].predecessors(), [nodes[0]])
		self.assertEqual(nodes[3].predecessors(), [nodes[0]])

	def test_multiproduct_5_7(self):
		"""Test ancestors for 5-node, 7-product system.
		"""
		print_status('TestPredecessors', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}

		self.assertEqual(nodes[0].predecessor_indices(), [2])
		self.assertEqual(nodes[1].predecessor_indices(), [2, 3])
		self.assertEqual(nodes[2].predecessor_indices(), [4])
		self.assertEqual(nodes[3].predecessor_indices(), [4])
		self.assertEqual(nodes[4].predecessor_indices(), [])
		self.assertEqual(nodes[0].predecessors(), [nodes[2]])
		self.assertEqual(nodes[1].predecessors(), [nodes[2], nodes[3]])
		self.assertEqual(nodes[2].predecessors(), [nodes[4]])
		self.assertEqual(nodes[3].predecessors(), [nodes[4]])
		self.assertEqual(nodes[4].predecessors(), [])


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
			anc[n.index] = n.ancestors

		self.assertEqual(anc[1], [network.nodes_by_index[2], network.nodes_by_index[3]])
		self.assertEqual(anc[2], [network.nodes_by_index[3]])
		self.assertEqual(anc[3], [])

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

		anc = {i: network.nodes_by_index[i].ancestors for i in network.node_indices}

		self.assertEqual(anc[0], [network.nodes_by_index[2], network.nodes_by_index[4]])
		self.assertEqual(anc[1], [network.nodes_by_index[2], network.nodes_by_index[3], network.nodes_by_index[4]])
		self.assertEqual(anc[2], [network.nodes_by_index[4]])
		self.assertEqual(anc[3], [network.nodes_by_index[4]])
		self.assertEqual(anc[4], [])


class TestValidatePredecessor(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidatePredecessor', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidatePredecessor', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test validate_predecessor for 3-node serial system in Example 6.1.
		"""
		print_status('TestValidatePredecessor', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		pred_obj, pred_ind = nodes[1].validate_predecessor(2)
		self.assertEqual(pred_obj, nodes[2])
		self.assertEqual(pred_ind, 2)

		pred_obj, pred_ind = nodes[1].validate_predecessor(nodes[2])
		self.assertEqual(pred_obj, nodes[2])
		self.assertEqual(pred_ind, 2)

		pred_obj, pred_ind = nodes[1].validate_predecessor(None)
		self.assertEqual(pred_obj, nodes[2])
		self.assertEqual(pred_ind, 2)

		pred_obj, pred_ind = nodes[3].validate_predecessor(None)
		self.assertIsNone(pred_obj)
		self.assertIsNone(pred_ind)

	def test_bad_param(self):
		"""Test that validate_predecessor correctly raises exceptions on bad parameters.
		"""
		print_status('TestValidatePredecessor', 'test_bad_param()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		with self.assertRaises(TypeError):
			_, _ = nodes[1].validate_predecessor(5.6)
			_, _ = nodes[1].validate_predecessor(SupplyChainProduct(1))
		
		with self.assertRaises(ValueError):
			_, _ = nodes[1].validate_predecessor(nodes[3])
			_, _ = nodes[1].validate_predecessor(3)

		network.add_predecessor(nodes[2], SupplyChainNode(4))
		with self.assertRaises(ValueError):
			_, _ = nodes[2].validate_predecessor(None)


class TestValidateSuccessor(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateSuccessor', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateSuccessor', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test validate_successor for 3-node serial system in Example 6.1.
		"""
		print_status('TestValidateSuccessor', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		succ_obj, succ_ind = nodes[2].validate_successor(1)
		self.assertEqual(succ_obj, nodes[1])
		self.assertEqual(succ_ind, 1)

		succ_obj, succ_ind = nodes[2].validate_successor(nodes[1])
		self.assertEqual(succ_obj, nodes[1])
		self.assertEqual(succ_ind, 1)

		succ_obj, succ_ind = nodes[3].validate_successor(None)
		self.assertEqual(succ_obj, nodes[2])
		self.assertEqual(succ_ind, 2)

		succ_obj, succ_ind = nodes[1].validate_successor(None)
		self.assertIsNone(succ_obj)
		self.assertIsNone(succ_ind)

	def test_bad_param(self):
		"""Test that validate_successor correctly raises exceptions on bad parameters.
		"""
		print_status('TestValidateSuccessor', 'test_bad_param()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		with self.assertRaises(TypeError):
			_, _ = nodes[1].validate_successor(5.6)
			_, _ = nodes[1].validate_successor(SupplyChainProduct(1))
		
		with self.assertRaises(ValueError):
			_, _ = nodes[3].validate_successor(nodes[1])
			_, _ = nodes[3].validate_successor(1)

		network.add_successor(nodes[2], SupplyChainNode(4))
		with self.assertRaises(ValueError):
			_, _ = nodes[2].validate_successor(None)


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

		network.nodes_by_index[0].remove_product(network.nodes_by_index[0].products_by_index[0])
		network.nodes_by_index[1].remove_product(1)
		network.nodes_by_index[2].remove_product(network.nodes_by_index[2].products_by_index[2])

		self.assertEqual(network.nodes_by_index[0].product_indices, [-_INDEX_BUMP])
		self.assertEqual(network.nodes_by_index[1].product_indices, [0])
		self.assertEqual(network.nodes_by_index[2].product_indices, [3, 4])

	def test_product_does_not_exist(self):
		"""Test that remove_product() correctly does nothing if product doesn't exist.
		"""
		print_status('TestRemoveProduct', 'test_product_does_not_exist()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.nodes_by_index[0].remove_product(7)
		network.nodes_by_index[1].remove_product(7)

		self.assertEqual(network.nodes_by_index[0].product_indices, [0])
		self.assertEqual(network.nodes_by_index[1].product_indices, [0, 1])


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

		network.nodes_by_index[0].remove_products([network.nodes_by_index[0].products_by_index[0]])
		network.nodes_by_index[1].remove_products([1])
		network.nodes_by_index[2].remove_products([3, network.nodes_by_index[2].products_by_index[2]])

		self.assertEqual(network.nodes_by_index[0].product_indices, [-_INDEX_BUMP])
		self.assertEqual(network.nodes_by_index[1].product_indices, [0])
		self.assertEqual(network.nodes_by_index[2].product_indices, [4])

	def test_product_does_not_exist(self):
		"""Test that remove_product() correctly does nothing if product doesn't exist.
		"""
		print_status('TestRemoveProducts', 'test_product_does_not_exist()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		network.nodes_by_index[0].remove_products([7])
		network.nodes_by_index[2].remove_products([3, 7])

		self.assertEqual(network.nodes_by_index[0].product_indices, [0])
		self.assertEqual(network.nodes_by_index[2].product_indices, [2, 4])

		
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

		self.assertFalse(network.nodes_by_index[0].is_multiproduct)
		self.assertTrue(network.nodes_by_index[1].is_multiproduct)
		self.assertTrue(network.nodes_by_index[2].is_multiproduct)
		self.assertTrue(network.nodes_by_index[3].is_multiproduct)
		self.assertTrue(network.nodes_by_index[4].is_multiproduct)

		self.assertTrue(network.nodes_by_index[0].is_singleproduct)
		self.assertFalse(network.nodes_by_index[1].is_singleproduct)
		self.assertFalse(network.nodes_by_index[2].is_singleproduct)
		self.assertFalse(network.nodes_by_index[3].is_singleproduct)
		self.assertFalse(network.nodes_by_index[4].is_singleproduct)

		# Add a node with no product loaded.
		network.add_node(SupplyChainNode(20))
		self.assertFalse(network.nodes_by_index[20].is_multiproduct)
		self.assertTrue(network.nodes_by_index[20].is_singleproduct)


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
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=None), [nodes[1], nodes[2], nodes[3]]))
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=None, return_indices=True), [1, 2, 3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=77)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True)

	def test_mwor_one_product(self):
		"""Test that raw_material_suppliers and raw_material_supplier_indices work correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestRawMaterialSuppliers', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

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

		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=10), [nodes[1], nodes[2], nodes[3]]))
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=10, return_indices=True), [1, 2, 3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=None)
			_ = nodes[0].raw_material_suppliers_by_product(product=77)
			_ = nodes[0].raw_material_suppliers_by_product(product=None, return_indices=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True)

	def test_mwor_multiple_products(self):
		"""Test that raw_material_suppliers_by_product works correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestRawMaterialSuppliers', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=10), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=11), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=12), [nodes[3]]))
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=10, return_indices=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=11, return_indices=True), [2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=12, return_indices=True), [3])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=None)
			_ = nodes[0].raw_material_suppliers_by_product(product=77)
			_ = nodes[0].raw_material_suppliers_by_product(product=None, return_indices=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True)

	def test_multiproduct_5_7(self):
		"""Test that raw_material_suppliers_by_product works correctly on 5-node, 7-product network.
		"""
		print_status('TestRawMaterialSuppliers', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=0), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=0), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=1), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=2), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=3), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=4), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=2), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=4), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=5), [None]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=6), [None]))
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=0, return_indices=True), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=0, return_indices=True), [2, 3])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=1, return_indices=True), [2, 3])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=2, return_indices=True), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=3, return_indices=True), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=4, return_indices=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=2, return_indices=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=4, return_indices=True), [4])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=5, return_indices=True), [None])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=6, return_indices=True), [None])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=None)
			_ = nodes[0].raw_material_suppliers_by_product(product=77)
			_ = nodes[0].raw_material_suppliers_by_product(product=None, return_indices=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True)
		

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
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

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
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

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
		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[10].set_bill_of_materials(3, 3)
		prods[10].set_bill_of_materials(4, 15)
		prods[10].set_bill_of_materials(5, 6)

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
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

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
		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[11].set_bill_of_materials(3, 3)
		prods[11].set_bill_of_materials(4, 15)
		prods[12].set_bill_of_materials(5, 6)

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
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
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
		"""Test that raw_materials_by_product works correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])
		[node0prod0_ind] = nodes[0].product_indices

		# Raw materials by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=node0prod0_ind, return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(network_BOM=True), list(prods.values())))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=node0prod0_ind, network_BOM=True), list(prods.values())))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=True), list(prods.values())))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=False), [])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=node0prod0_ind, return_indices=True, network_BOM=False), [])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=node0prod0_ind, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=False), []))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=True), [1, 2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, return_indices=True, network_BOM=True), [1, 2, 3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[1], nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, network_BOM=True), [nodes[1], nodes[2], nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=False), [])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, return_indices=True, network_BOM=False), [])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, network_BOM=False), []))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=True), [1])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=True), [3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=True), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=True), [nodes[1]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=True), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=True), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=True), [nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=True), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=False)

	def test_mwor_one_product(self):
		"""Test that raw_materials_by_product works correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		nodes[0].add_product(SupplyChainProduct(10))
		prod10 = nodes[0].products[0]
		prod10.set_bill_of_materials(1, 5)
		prod10.set_bill_of_materials(2, 7)
		prod10.set_bill_of_materials(3, 3)
		prod10.set_bill_of_materials(4, 15)
		prod10.set_bill_of_materials(5, 6)

		[node0prod0_ind] = nodes[0].product_indices

		# Raw materials by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=node0prod0_ind, return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), list(prods.keys()))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(network_BOM=True), list(prods.values())))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=node0prod0_ind, network_BOM=True), list(prods.values())))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=True), list(prods.values())))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=False), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=node0prod0_ind, return_indices=True, network_BOM=False), list(prods.keys()))
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), list(prods.keys()))
		self.assertTrue((nodes[0].raw_materials_by_product(network_BOM=False), list(prods.values())))
		self.assertTrue((nodes[0].raw_materials_by_product(product=node0prod0_ind, network_BOM=False), list(prods.values())))
		self.assertTrue((nodes[0].raw_materials_by_product(product='all', network_BOM=False), list(prods.values())))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=True), [1, 2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, return_indices=True, network_BOM=True), [1, 2, 3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[1], nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, network_BOM=True), [nodes[1], nodes[2], nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=False), [1, 2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, return_indices=True, network_BOM=False), [1, 2, 3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=False), [nodes[1], nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=node0prod0_ind, network_BOM=False), [nodes[1], nodes[2], nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=True), [1])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=True), [3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=True), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=True), [nodes[1]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=True), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=True), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=True), [nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=True), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=False), [1])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=False), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=False), [3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=False), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=False), [nodes[1]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=False), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=False), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=False), [nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=False), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=False)

	def test_mwor_multiple_products(self):
		"""Test that raw_materials_by_product works correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestRawMaterials', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		# Raw materials by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=10, return_indices=True, network_BOM=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=11, return_indices=True, network_BOM=True), [3, 4])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=12, return_indices=True, network_BOM=True), [5])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [1, 2, 3, 4, 5])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=10, network_BOM=True), [prods[1], prods[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=11, network_BOM=True), [prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=12, network_BOM=True), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=True), [prods[1], prods[2], prods[3], prods[4], prods[5]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(return_indices=True, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=10, return_indices=True, network_BOM=False), [1, 2])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=11, return_indices=True, network_BOM=False), [3, 4])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=12, return_indices=True, network_BOM=False), [5])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [1, 2, 3, 4, 5])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=10, network_BOM=False), [prods[1], prods[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=11, network_BOM=False), [prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=12, network_BOM=False), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=False), [prods[1], prods[2], prods[3], prods[4], prods[5]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_materials_by_product(return_indices=True, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)
			_ = nodes[0].raw_materials_by_product(product=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=10, return_indices=True, network_BOM=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=11, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=12, return_indices=True, network_BOM=True), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=10, network_BOM=True), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=11, network_BOM=True), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=12, network_BOM=True), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=True)

		# Raw material suppliers by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=10, return_indices=True, network_BOM=False), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=11, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=12, return_indices=True, network_BOM=False), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=10, network_BOM=False), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=11, network_BOM=False), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=12, network_BOM=False), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_product(product=77, network_BOM=False)

		# Raw material suppliers by raw_material, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=True), [1])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=True), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=True), [3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=True), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=True), [nodes[1]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=True), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=True), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=True), [nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=True), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=True)

		# Raw material suppliers by raw_material, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, return_indices=True, network_BOM=False), [1])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=False), [1, 2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=False), [3])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=False), [3])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=1, network_BOM=False), [nodes[1]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, network_BOM=False), [nodes[1], nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, network_BOM=False), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, network_BOM=False), [nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_raw_material(raw_material=5, network_BOM=False), [nodes[3]]))
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=False)

	def test_multiproduct_5_7(self):
		"""Test that raw_materials_by_product works correctly on 5-node, 7-product network.
		"""
		print_status('TestRawMaterials', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		prods = network.products_by_index

		# Raw materials by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=0, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product=0, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product=1, return_indices=True, network_BOM=True), [3, 4])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [2, 3, 4])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=2, return_indices=True, network_BOM=True), [5])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=3, return_indices=True, network_BOM=True), [5])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=4, return_indices=True, network_BOM=True), [6])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [5, 6])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product=2, return_indices=True, network_BOM=True), [5])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product=4, return_indices=True, network_BOM=True), [6])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [5, 6])
		self.assertCountEqual(nodes[4].raw_materials_by_product(product=5, return_indices=True, network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertCountEqual(nodes[4].raw_materials_by_product(product=6, return_indices=True, network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertCountEqual(nodes[4].raw_materials_by_product(product='all', return_indices=True, network_BOM=True), [nodes[4]._external_supplier_dummy_product.index])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(network_BOM=True), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=0, network_BOM=True), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=True), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product=0, network_BOM=True), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product=1, network_BOM=True), [prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product='all', network_BOM=True), [prods[2], prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=2, network_BOM=True), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=3, network_BOM=True), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=4, network_BOM=True), [prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product='all', network_BOM=True), [prods[5], prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product=2, network_BOM=True), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product=4, network_BOM=True), [prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product='all', network_BOM=True), [prods[5], prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=5, network_BOM=True), [nodes[4]._external_supplier_dummy_product]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=6, network_BOM=True), [nodes[4]._external_supplier_dummy_product]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product='all', network_BOM=True), [nodes[4]._external_supplier_dummy_product]))
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_materials_by_product(return_indices=True, network_BOM=True)
			_ = nodes[1].raw_materials_by_product(network_BOM=True)
			_ = nodes[1].raw_materials_by_product(product=77, network_BOM=True)
			_ = nodes[1].raw_materials_by_product(product=77, network_BOM=True)

		# Raw materials by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_materials_by_product(return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product=0, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[0].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product=0, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product=1, return_indices=True, network_BOM=False), [3, 4])
		self.assertCountEqual(nodes[1].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [2, 3, 4])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=2, return_indices=True, network_BOM=False), [5])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=3, return_indices=True, network_BOM=False), [5])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product=4, return_indices=True, network_BOM=False), [6])
		self.assertCountEqual(nodes[2].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [5, 6])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product=2, return_indices=True, network_BOM=False), [5])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product=4, return_indices=True, network_BOM=False), [6])
		self.assertCountEqual(nodes[3].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), [5, 6])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(network_BOM=False), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=5, return_indices=True, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=6, return_indices=True, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product='all', return_indices=True, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product=0, network_BOM=False), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_materials_by_product(product='all', network_BOM=False), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product=0, network_BOM=False), [prods[2], prods[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product=1, network_BOM=False), [prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_materials_by_product(product='all', network_BOM=False), [prods[2], prods[3], prods[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=2, network_BOM=False), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=3, network_BOM=False), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product=4, network_BOM=False), [prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_materials_by_product(product='all', network_BOM=False), [prods[5], prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product=2, network_BOM=False), [prods[5]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product=4, network_BOM=False), [prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_materials_by_product(product='all', network_BOM=False), [prods[5], prods[6]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=5, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product=6, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_materials_by_product(product='all', network_BOM=False), []))
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_materials_by_product(return_indices=True, network_BOM=False)
			_ = nodes[1].raw_materials_by_product(network_BOM=False)
			_ = nodes[1].raw_materials_by_product(product=77, network_BOM=False)
			_ = nodes[1].raw_materials_by_product(product=77, network_BOM=False)

		# Raw material suppliers by product, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=0, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=0, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=1, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=2, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=3, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=4, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=2, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=4, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=5, return_indices=True, network_BOM=True), [None])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=6, return_indices=True, network_BOM=True), [None])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=True), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=0, network_BOM=True), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=0, network_BOM=True), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=1, network_BOM=True), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=2, network_BOM=True), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=3, network_BOM=True), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=4, network_BOM=True), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=2, network_BOM=True), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=4, network_BOM=True), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=5, network_BOM=True), [None]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=6, network_BOM=True), [None]))
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_suppliers_by_product(return_indices=True, network_BOM=True)
			_ = nodes[1].raw_material_suppliers_by_product(network_BOM=True)
			_ = nodes[1].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=True)
			_ = nodes[1].raw_material_suppliers_by_product(product=77, network_BOM=True)

		# # Raw material suppliers by product, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_product(product=0, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=0, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_product(product=1, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=2, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=3, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_product(product=4, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=2, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_product(product=4, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=5, return_indices=True, network_BOM=False), [])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_product(product=6, return_indices=True, network_BOM=False), [])
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(network_BOM=False), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[0].raw_material_suppliers_by_product(product=0, network_BOM=False), [nodes[2]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=0, network_BOM=False), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[1].raw_material_suppliers_by_product(product=1, network_BOM=False), [nodes[2], nodes[3]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=2, network_BOM=False), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=3, network_BOM=False), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[2].raw_material_suppliers_by_product(product=4, network_BOM=False), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=2, network_BOM=False), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[3].raw_material_suppliers_by_product(product=4, network_BOM=False), [nodes[4]]))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=5, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[4].raw_material_suppliers_by_product(product=6, network_BOM=False), []))
		with self.assertRaises(ValueError):
			_ = nodes[1].raw_material_suppliers_by_product(return_indices=True, network_BOM=False)
			_ = nodes[1].raw_material_suppliers_by_product(network_BOM=False)
			_ = nodes[1].raw_material_suppliers_by_product(product=77, return_indices=True, network_BOM=False)
			_ = nodes[1].raw_material_suppliers_by_product(product=77, network_BOM=False)

		# # Raw material suppliers by raw_material, network_BOM=True.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=True), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=True), [2, 3])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_raw_material(raw_material=6, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_raw_material(raw_material=6, return_indices=True, network_BOM=True), [4])
		self.assertCountEqual(nodes[4].raw_material_suppliers_by_raw_material(raw_material=nodes[4]._external_supplier_dummy_product.index, return_indices=True, network_BOM=True), [None])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=77, return_indices=True, network_BOM=True)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=77, network_BOM=True)

		# # Raw material suppliers by raw_material, network_BOM=False.
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[0].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=2, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=3, return_indices=True, network_BOM=False), [2])
		self.assertCountEqual(nodes[1].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=False), [2, 3])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[2].raw_material_suppliers_by_raw_material(raw_material=6, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_raw_material(raw_material=5, return_indices=True, network_BOM=False), [4])
		self.assertCountEqual(nodes[3].raw_material_suppliers_by_raw_material(raw_material=6, return_indices=True, network_BOM=False), [4])
		with self.assertRaises(ValueError):
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=4, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=None, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=77, return_indices=True, network_BOM=False)
			_ = nodes[0].raw_material_suppliers_by_raw_material(raw_material=77, network_BOM=False)
			_ = nodes[4].raw_material_suppliers_by_raw_material(raw_material=nodes[4]._external_supplier_dummy_product.index, return_indices=True, network_BOM=False)
		
		
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
		"""Test that products_by_raw_materials works correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1, return_indices=True), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2, return_indices=True), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3, return_indices=True), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4, return_indices=True), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5, return_indices=True), [nodes[0]._dummy_product.index])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index, return_indices=True), [1, 2])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None, return_indices=True), [1, 2])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index, return_indices=True), [2, 3])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None, return_indices=True), [2, 3])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index, return_indices=True), [4, 5])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None, return_indices=True), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5), [nodes[0]._dummy_product])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].products_by_raw_material(raw_material=77)
			_ = nodes[0].products_by_raw_material(raw_material=None)

	def test_mwor_one_product(self):
		"""Test that products_by_raw_materials works correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

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

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5, return_indices=True), [10])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index, return_indices=True), [1, 2])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None, return_indices=True), [1, 2])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index, return_indices=True), [2, 3])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None, return_indices=True), [2, 3])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index, return_indices=True), [4, 5])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None, return_indices=True), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4), [nodes[0].products[0]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5), [nodes[0].products[0]])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].products_by_raw_material(raw_material=77)
			_ = nodes[0].products_by_raw_material(raw_material=None)

	def test_mwor_multiple_products(self):
		"""Test that products_by_raw_materials works correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestProductsByRawMaterial', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

		nodes[0].add_products([SupplyChainProduct(10), SupplyChainProduct(11), SupplyChainProduct(12)])

		nodes[0].products_by_index[10].set_bill_of_materials(1, 5)
		nodes[0].products_by_index[10].set_bill_of_materials(2, 7)
		nodes[0].products_by_index[11].set_bill_of_materials(3, 3)
		nodes[0].products_by_index[11].set_bill_of_materials(4, 15)
		nodes[0].products_by_index[12].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2, return_indices=True), [10])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3, return_indices=True), [11])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4, return_indices=True), [11])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5, return_indices=True), [12])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index, return_indices=True), [1, 2])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None, return_indices=True), [1, 2])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index, return_indices=True), [2, 3])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None, return_indices=True), [2, 3])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index, return_indices=True), [4, 5])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None, return_indices=True), [4, 5])

		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=1), [nodes[0].products_by_index[10]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=2), [nodes[0].products_by_index[10]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=3), [nodes[0].products_by_index[11]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=4), [nodes[0].products_by_index[11]])
		self.assertListEqual(nodes[0].products_by_raw_material(raw_material=5), [nodes[0].products_by_index[12]])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=nodes[1]._external_supplier_dummy_product.index), [prods[1], prods[2]])
		self.assertListEqual(nodes[1].products_by_raw_material(raw_material=None), [prods[1], prods[2]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=nodes[2]._external_supplier_dummy_product.index), [prods[2], prods[3]])
		self.assertListEqual(nodes[2].products_by_raw_material(raw_material=None), [prods[2], prods[3]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=nodes[3]._external_supplier_dummy_product.index), [prods[4], prods[5]])
		self.assertListEqual(nodes[3].products_by_raw_material(raw_material=None), [prods[4], prods[5]])

		with self.assertRaises(ValueError):
			_ = nodes[0].products_by_raw_material(raw_material=77)
			_ = nodes[0].products_by_raw_material(raw_material=None)

	def test_multiproduct_5_7(self):
		"""Test that products_by_raw_materials works correctly on 5-node, 7-product network.
		"""
		print_status('TestProductsByRawMaterial', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		prods = network.products_by_index

		self.assertCountEqual(nodes[0].products_by_raw_material(raw_material=2, return_indices=True), [0])
		self.assertCountEqual(nodes[0].products_by_raw_material(raw_material=3, return_indices=True), [0])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=2, return_indices=True), [0])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=3, return_indices=True), [0, 1])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=4, return_indices=True), [1])
		self.assertCountEqual(nodes[2].products_by_raw_material(raw_material=5, return_indices=True), [2, 3])
		self.assertCountEqual(nodes[2].products_by_raw_material(raw_material=6, return_indices=True), [4])
		self.assertCountEqual(nodes[3].products_by_raw_material(raw_material=5, return_indices=True), [2])
		self.assertCountEqual(nodes[3].products_by_raw_material(raw_material=6, return_indices=True), [4])
		self.assertCountEqual(nodes[4].products_by_raw_material(raw_material=nodes[4]._external_supplier_dummy_product.index, return_indices=True), [5, 6])

		self.assertCountEqual(nodes[0].products_by_raw_material(raw_material=2), [prods[0]])
		self.assertCountEqual(nodes[0].products_by_raw_material(raw_material=3), [prods[0]])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=2), [prods[0]])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=3), [prods[0], prods[1]])
		self.assertCountEqual(nodes[1].products_by_raw_material(raw_material=4), [prods[1]])
		self.assertCountEqual(nodes[2].products_by_raw_material(raw_material=5), [prods[2], prods[3]])
		self.assertCountEqual(nodes[2].products_by_raw_material(raw_material=6), [prods[4]])
		self.assertCountEqual(nodes[3].products_by_raw_material(raw_material=5), [prods[2]])
		self.assertCountEqual(nodes[3].products_by_raw_material(raw_material=6), [prods[4]])
		self.assertCountEqual(nodes[4].products_by_raw_material(raw_material=nodes[4]._external_supplier_dummy_product.index), [prods[5], prods[6]])

		with self.assertRaises(ValueError):
			_ = nodes[0].products_by_raw_material(raw_material=77)
			_ = nodes[0].products_by_raw_material(raw_material=4)
			_ = nodes[0].products_by_raw_material(raw_material=5)
			_ = nodes[0].products_by_raw_material(raw_material=None)


class TestSupplierRawMaterialPairsByProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSupplierRawMaterialPairsByProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSupplierRawMaterialPairsByProduct', 'tear_down_class()')

	def test_mwor_one_product(self):
		"""Test that supplier_raw_material_pairs_by_product works correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestSupplierRawMaterialPairsByProduct', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		nodes[0].demand_source = DemandSource(type='P', mean=5)

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		prods[10] = SupplyChainProduct(10)
		nodes[0].add_product(prods[10])
		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[10].set_bill_of_materials(3, 3)
		prods[10].set_bill_of_materials(4, 15)
		prods[10].set_bill_of_materials(5, 6)

		self.assertTrue(compare_unhashable_lists(nodes[0].supplier_raw_material_pairs_by_product(product=prods[10], return_indices=False, network_BOM=True),
					   [(nodes[1], prods[1]), (nodes[1], prods[2]), (nodes[2], prods[2]), (nodes[2], prods[3]), (nodes[3], prods[4]), (nodes[3], prods[5])]))
		self.assertTrue(compare_unhashable_lists(nodes[0].supplier_raw_material_pairs_by_product(product=None, return_indices=False, network_BOM=True),
					   [(nodes[1], prods[1]), (nodes[1], prods[2]), (nodes[2], prods[2]), (nodes[2], prods[3]), (nodes[3], prods[4]), (nodes[3], prods[5])]))
		self.assertCountEqual(nodes[0].supplier_raw_material_pairs_by_product(product=None, return_indices=True, network_BOM=True),
					   [(1, 1), (1, 2), (2, 2), (2, 3), (3, 4), (3, 5)])
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=prods[1], return_indices=False, network_BOM=True),
					   [(None, nodes[1]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[1].supplier_raw_material_pairs_by_product(product=prods[1], return_indices=True, network_BOM=True), 
					   [(None, nodes[1]._external_supplier_dummy_product.index)])
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=2, return_indices=False, network_BOM=True), 
					   [(None, nodes[1]._external_supplier_dummy_product)]))
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[2].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=True),
					   [(None, nodes[2]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[2].supplier_raw_material_pairs_by_product(product=2, return_indices=True, network_BOM=True), 
					   [(None, nodes[2]._external_supplier_dummy_product.index)])
		self.assertTrue(compare_unhashable_lists(nodes[3].supplier_raw_material_pairs_by_product(product=4, return_indices=False, network_BOM=True),
					   [(None, nodes[3]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[3].supplier_raw_material_pairs_by_product(product=prods[5], return_indices=True, network_BOM=False), [])

		with self.assertRaises(ValueError):
			_ = nodes[1].supplier_raw_material_pairs_by_product(product=77)

	def test_mwor_multiple_products(self):
		"""Test that supplier_raw_material_pairs_by_product works correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestSupplierRawMaterialPairsByProduct', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		nodes[0].demand_source = DemandSource(type='P', mean=5)

		prods = {i: SupplyChainProduct(i) for i in [1, 2, 3, 4, 5, 10, 11, 12]}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

		nodes[0].add_products([prods[10], prods[11], prods[12]])

		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[11].set_bill_of_materials(3, 3)
		prods[11].set_bill_of_materials(4, 15)
		prods[12].set_bill_of_materials(5, 6)

		self.assertTrue(compare_unhashable_lists(nodes[0].supplier_raw_material_pairs_by_product(product=prods[10], return_indices=False, network_BOM=True),
					   [(nodes[1], prods[1]), (nodes[1], prods[2]), (nodes[2], prods[2])]))
		self.assertTrue(compare_unhashable_lists(nodes[0].supplier_raw_material_pairs_by_product(product=11, return_indices=False, network_BOM=True),
					   [(nodes[2], prods[3]), (nodes[3], prods[4])]))
		self.assertCountEqual(nodes[0].supplier_raw_material_pairs_by_product(product=12, return_indices=True, network_BOM=True),
						[(3, 5)])
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=prods[1], return_indices=False, network_BOM=True),
					   [(None, nodes[1]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[1].supplier_raw_material_pairs_by_product(product=prods[1], return_indices=True, network_BOM=True), 
					   [(None, nodes[1]._external_supplier_dummy_product.index)])
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=2, return_indices=False, network_BOM=True), 
					   [(None, nodes[1]._external_supplier_dummy_product)]))
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=False), []))
		self.assertTrue(compare_unhashable_lists(nodes[2].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=True),
					   [(None, nodes[2]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[2].supplier_raw_material_pairs_by_product(product=2, return_indices=True, network_BOM=True), 
					   [(None, nodes[2]._external_supplier_dummy_product.index)])
		self.assertTrue(compare_unhashable_lists(nodes[3].supplier_raw_material_pairs_by_product(product=4, return_indices=False, network_BOM=True),
					   [(None, nodes[3]._external_supplier_dummy_product)]))
		self.assertCountEqual(nodes[3].supplier_raw_material_pairs_by_product(product=prods[5], return_indices=True, network_BOM=False), [])

		with self.assertRaises(ValueError):
			_ = nodes[1].supplier_raw_material_pairs_by_product(product=77)
			_ = nodes[0].supplier_raw_material_pairs_by_product(product=None, return_indices=True, network_BOM=True), [None]

	def test_multiproduct_5_7(self):
		"""Test that supplier_raw_material_pairs_by_product works correctly on 5-node, 7-product network.
		"""
		print_status('TestSupplierRawMaterialPairsByProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		prods = {prod.index: prod for prod in network.products}

		self.assertTrue(compare_unhashable_lists(nodes[0].supplier_raw_material_pairs_by_product(product=prods[0], return_indices=False, network_BOM=True),
					   [(nodes[2], prods[2]), (nodes[2], prods[3])]))
		self.assertTrue(compare_unhashable_lists(nodes[1].supplier_raw_material_pairs_by_product(product=0, return_indices=False, network_BOM=True),
					   [(nodes[2], prods[2]), (nodes[2], prods[3]), (nodes[3], prods[2])]))
		self.assertCountEqual(nodes[1].supplier_raw_material_pairs_by_product(product=1, return_indices=True, network_BOM=True),
					   [(2, 3), (2, 4), (3, 4)])
		self.assertTrue(compare_unhashable_lists(nodes[2].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=True),
					   [(nodes[4], prods[5])]))
		self.assertCountEqual(nodes[2].supplier_raw_material_pairs_by_product(product=prods[3], return_indices=True, network_BOM=True), 
					   [(4, 5)])
		self.assertTrue(compare_unhashable_lists(nodes[2].supplier_raw_material_pairs_by_product(product=4, return_indices=False, network_BOM=True), 
					   [(nodes[4], prods[6])]))
		self.assertTrue(compare_unhashable_lists(nodes[3].supplier_raw_material_pairs_by_product(product=prods[2], return_indices=False, network_BOM=False), 
				   		[(nodes[4], prods[5])]))
		self.assertCountEqual(nodes[3].supplier_raw_material_pairs_by_product(product=4, return_indices=True, network_BOM=True),
					   [(4, 6)])
		self.assertCountEqual(nodes[4].supplier_raw_material_pairs_by_product(product=5, return_indices=True, network_BOM=True), 
					   [(None, nodes[4]._external_supplier_dummy_product.index)])
		self.assertTrue(compare_unhashable_lists(nodes[4].supplier_raw_material_pairs_by_product(product=prods[6], return_indices=False, network_BOM=False), []))

		with self.assertRaises(ValueError):
			_ = nodes[1].supplier_raw_material_pairs_by_product(product=77)
			_ = nodes[0].supplier_raw_material_pairs_by_product(product=None, return_indices=True, network_BOM=True), [None]
		

class TestCustomersByProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCustomersByProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCustomersByProduct', 'tear_down_class()')

	def test_mwor_no_product(self):
		"""Test that customers_by_product works correctly on MWOR network with no product added at retailer.
		"""
		print_status('TestCustomersByProduct', 'test_mwor_no_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		nodes[0].demand_source = DemandSource(type='P', mean=5)

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		self.assertCountEqual(nodes[0].customers_by_product(product=nodes[0]._dummy_product, return_indices=False, network_BOM=True), [None])
		self.assertCountEqual(nodes[0].customers_by_product(product=None, return_indices=False, network_BOM=True), [None])
		self.assertCountEqual(nodes[0].customers_by_product(product=None, return_indices=True, network_BOM=True), [None])
		self.assertCountEqual(nodes[1].customers_by_product(product=prods[1], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertCountEqual(nodes[1].customers_by_product(product=prods[1], return_indices=True, network_BOM=True), [0])
		self.assertCountEqual(nodes[1].customers_by_product(product=2, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertCountEqual(nodes[1].customers_by_product(product=prods[2], return_indices=False, network_BOM=False), [])
		self.assertCountEqual(nodes[2].customers_by_product(product=prods[2], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertCountEqual(nodes[2].customers_by_product(product=2, return_indices=True, network_BOM=True), [0])
		self.assertCountEqual(nodes[2].customers_by_product(product=3, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertCountEqual(nodes[2].customers_by_product(product=prods[3], return_indices=False, network_BOM=False), [])

		with self.assertRaises(ValueError):
			_ = nodes[1].customers_by_product(product=77)

	def test_mwor_one_product(self):
		"""Test that customers_by_product works correctly on MWOR network with one product added at retailer.
		"""
		print_status('TestCustomersByProduct', 'test_mwor_one_product()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		nodes[0].demand_source = DemandSource(type='P', mean=5)

		prods = {i: SupplyChainProduct(i) for i in range(1, 6)}
		nodes[1].add_products([prods[1], prods[2]])
		nodes[2].add_products([prods[2], prods[3]])
		nodes[3].add_products([prods[4], prods[5]])

		prods[10] = SupplyChainProduct(10)
		nodes[0].add_product(prods[10])
		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[10].set_bill_of_materials(3, 3)
		prods[10].set_bill_of_materials(4, 15)
		prods[10].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].customers_by_product(product=prods[10], return_indices=False, network_BOM=True), [None])
		self.assertListEqual(nodes[0].customers_by_product(product=None, return_indices=False, network_BOM=True), [None])
		self.assertListEqual(nodes[0].customers_by_product(product=None, return_indices=True, network_BOM=True), [None])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=True, network_BOM=True), [0])
		self.assertListEqual(nodes[1].customers_by_product(product=2, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[2], return_indices=False, network_BOM=False), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[2], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=2, return_indices=True, network_BOM=True), [0])
		self.assertListEqual(nodes[2].customers_by_product(product=3, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[3], return_indices=False, network_BOM=False), [nodes[0]])

		with self.assertRaises(ValueError):
			_ = nodes[1].customers_by_product(product=77)

	def test_mwor_multiple_products(self):
		"""Test that customers_by_product works correctly on MWOR network with multiple products added at retailer.
		"""
		print_status('TestCustomersByProduct', 'test_mwor_multiple_products()')

		network = mwor_system(3)
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		nodes[0].demand_source = DemandSource(type='P', mean=5)

		prods = {i: SupplyChainProduct(i) for i in [1, 2, 3, 4, 5, 10, 11, 12]}
		network.nodes_by_index[1].add_products([prods[1], prods[2]])
		network.nodes_by_index[2].add_products([prods[2], prods[3]])
		network.nodes_by_index[3].add_products([prods[4], prods[5]])

		nodes[0].add_products([prods[10], prods[11], prods[12]])

		prods[10].set_bill_of_materials(1, 5)
		prods[10].set_bill_of_materials(2, 7)
		prods[11].set_bill_of_materials(3, 3)
		prods[11].set_bill_of_materials(4, 15)
		prods[12].set_bill_of_materials(5, 6)

		self.assertListEqual(nodes[0].customers_by_product(product=prods[10], return_indices=False, network_BOM=True), [None])
		self.assertListEqual(nodes[0].customers_by_product(product=prods[11], return_indices=True, network_BOM=True), [None])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=True, network_BOM=True), [0])
		self.assertListEqual(nodes[1].customers_by_product(product=2, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[2], return_indices=False, network_BOM=False), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[2], return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=2, return_indices=True, network_BOM=True), [0])
		self.assertListEqual(nodes[2].customers_by_product(product=3, return_indices=False, network_BOM=True), [nodes[0]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[3], return_indices=False, network_BOM=False), [nodes[0]])

		with self.assertRaises(ValueError):
			_ = nodes[1].customers_by_product(product=77)
			_ = nodes[0].customers_by_product(product=None, return_indices=True, network_BOM=True), [None]

	def test_multiproduct_5_7(self):
		"""Test that customers_by_product works correctly on 5-node, 7-product network.
		"""
		print_status('TestCustomersByProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
		prods = {prod.index: prod for prod in network.products}

		self.assertListEqual(nodes[2].customers_by_product(product=prods[3], return_indices=False, network_BOM=False), [nodes[0], nodes[1]])



		self.assertListEqual(nodes[0].customers_by_product(product=prods[0], return_indices=False, network_BOM=True), [None])
		self.assertListEqual(nodes[0].customers_by_product(product=prods[0], return_indices=True, network_BOM=True), [None])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=False, network_BOM=True), [None])
		self.assertListEqual(nodes[1].customers_by_product(product=prods[1], return_indices=True, network_BOM=True), [None])
		self.assertListEqual(nodes[2].customers_by_product(product=2, return_indices=False, network_BOM=True), [nodes[0], nodes[1]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[3], return_indices=False, network_BOM=False), [nodes[0], nodes[1]])
		self.assertListEqual(nodes[2].customers_by_product(product=prods[4], return_indices=True, network_BOM=False), [1])
		self.assertListEqual(nodes[3].customers_by_product(product=prods[2], return_indices=False, network_BOM=True), [nodes[1]])
		self.assertListEqual(nodes[3].customers_by_product(product=4, return_indices=True, network_BOM=True), [1])
		self.assertListEqual(nodes[4].customers_by_product(product=5, return_indices=True, network_BOM=True), [2, 3])
		self.assertListEqual(nodes[4].customers_by_product(product=prods[6], return_indices=False, network_BOM=False), [nodes[2], nodes[3]])

		with self.assertRaises(ValueError):
			_ = nodes[1].customers_by_product(product=77)
			_ = nodes[0].customers_by_product(product=None, return_indices=True, network_BOM=True), [None]
		

class TestValidateProduct(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateProduct', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateProduct', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test validate_product for 3-node serial system in Example 6.1.
		"""
		print_status('TestValidateProduct', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		prod_obj, prod_ind = nodes[1].validate_product(nodes[1]._dummy_product)
		self.assertEqual(prod_obj, nodes[1]._dummy_product)
		self.assertEqual(prod_ind, nodes[1]._dummy_product.index)

		prod_obj, prod_ind = nodes[2].validate_product(nodes[2]._dummy_product.index)
		self.assertEqual(prod_obj, nodes[2]._dummy_product)
		self.assertEqual(prod_ind, nodes[2]._dummy_product.index)

		prod_obj, prod_ind = nodes[3].validate_product(None)
		self.assertEqual(prod_obj, nodes[3]._dummy_product)
		self.assertEqual(prod_ind, nodes[3]._dummy_product.index)

	def test_multiproduct_5_7(self):
		"""Test validate_product for 5-node, 7-product system.
		"""
		print_status('TestValidateProduct', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}
		products = {prod.index: prod for prod in network.products}

		prod_obj, prod_ind = nodes[2].validate_product(2)
		self.assertEqual(prod_obj, products[2])
		self.assertEqual(prod_ind, 2)

		prod_obj, prod_ind = nodes[2].validate_product(products[4])
		self.assertEqual(prod_obj, products[4])
		self.assertEqual(prod_ind, 4)

		prod_obj, prod_ind = nodes[0].validate_product(None)
		self.assertEqual(prod_obj, products[0])
		self.assertEqual(prod_ind, 0)

		# prod_obj, prod_ind = nodes[1].validate_product(None)
		# self.assertIsNone(prod_obj)
		# self.assertIsNone(prod_ind)

	def test_bad_param(self):
		"""Test that validate_product correctly raises exceptions on bad parameters.
		"""
		print_status('TestValidateProduct', 'test_bad_param()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}
		products = {prod.index: prod for prod in network.products}

		with self.assertRaises(TypeError):
			_, _ = nodes[2].validate_product(5.6)
			_, _ = nodes[2].validate_product(SupplyChainNode(10))
		
		with self.assertRaises(ValueError):
			_, _ = nodes[3].validate_product(products[5])
			_, _ = nodes[3].validate_product(5)
			_, _ = nodes[2].validate_product(None)

class TestValidateRawMaterial(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateRawMaterial', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateRawMaterial', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test validate_raw_material for 3-node serial system in Example 6.1.
		"""
		print_status('TestValidateRawMaterial', 'test_example_6_1()')

		network = load_instance("example_6_1")
		nodes = {n.index: n for n in network.nodes}

		rm_obj, rm_ind = nodes[1].validate_raw_material(nodes[2]._dummy_product)
		self.assertEqual(rm_obj, nodes[2]._dummy_product)
		self.assertEqual(rm_ind, nodes[2]._dummy_product.index)

		rm_obj, rm_ind = nodes[2].validate_raw_material(nodes[3]._dummy_product.index)
		self.assertEqual(rm_obj, nodes[3]._dummy_product)
		self.assertEqual(rm_ind, nodes[3]._dummy_product.index)

		rm_obj, rm_ind = nodes[2].validate_raw_material(nodes[3]._dummy_product.index, network_BOM=True)
		self.assertEqual(rm_obj, nodes[3]._dummy_product)
		self.assertEqual(rm_ind, nodes[3]._dummy_product.index)

		rm_obj, rm_ind = nodes[2].validate_raw_material(nodes[3]._dummy_product.index, predecessor=3)
		self.assertEqual(rm_obj, nodes[3]._dummy_product)
		self.assertEqual(rm_ind, nodes[3]._dummy_product.index)

		with self.assertRaises(ValueError):
			_, _ = nodes[2].validate_raw_material(nodes[3]._dummy_product.index, predecessor=1)
			_, _ = nodes[2].validate_raw_material(nodes[3]._dummy_product.index, network_BOM=False)

		rm_obj, rm_ind = nodes[2].validate_raw_material(None)
		self.assertEqual(rm_obj, nodes[3]._dummy_product)
		self.assertEqual(rm_ind, nodes[3]._dummy_product.index)

		rm_obj, rm_ind = nodes[3].validate_raw_material(nodes[3]._external_supplier_dummy_product.index)
		self.assertEqual(rm_obj, nodes[3]._external_supplier_dummy_product)
		self.assertEqual(rm_ind, nodes[3]._external_supplier_dummy_product.index)

		rm_obj, rm_ind = nodes[3].validate_raw_material(None)
		self.assertEqual(rm_obj, nodes[3]._external_supplier_dummy_product)
		self.assertEqual(rm_ind, nodes[3]._external_supplier_dummy_product.index)

		with self.assertRaises(ValueError):
			_, _ = nodes[3].validate_raw_material(nodes[3]._dummy_product.index, predecessor=2)

	def test_multiproduct_5_7(self):
		"""Test validate_raw_material for 5-node, 7-product system.
		"""
		print_status('TestValidateRawMaterial', 'test_multiproduct_5_7()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}
		products = {prod.index: prod for prod in network.products}

		rm_obj, rm_ind = nodes[1].validate_raw_material(products[4])
		self.assertEqual(rm_obj, products[4])
		self.assertEqual(rm_ind, 4)

		rm_obj, rm_ind = nodes[1].validate_raw_material(3)
		self.assertEqual(rm_obj, products[3])
		self.assertEqual(rm_ind, 3)

		rm_obj, rm_ind = nodes[1].validate_raw_material(3, predecessor=2)
		self.assertEqual(rm_obj, products[3])
		self.assertEqual(rm_ind, 3)

		with self.assertRaises(ValueError):
			_, _ = nodes[0].validate_raw_material(4)
			_, _ = nodes[1].validate_raw_material(3, predecessor=3)

		rm_obj, rm_ind = nodes[4].validate_raw_material(None)
		self.assertEqual(rm_obj, nodes[4]._external_supplier_dummy_product)
		self.assertEqual(rm_ind, nodes[4]._external_supplier_dummy_product.index)

		rm_obj, rm_ind = nodes[4].validate_raw_material(nodes[4]._external_supplier_dummy_product)
		self.assertEqual(rm_obj, nodes[4]._external_supplier_dummy_product)
		self.assertEqual(rm_ind, nodes[4]._external_supplier_dummy_product.index)

	def test_bad_param(self):
		"""Test that validate_raw_material correctly raises exceptions on bad parameters.
		"""
		print_status('TestValidateRawMaterial', 'test_bad_param()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")
		nodes = {n.index: n for n in network.nodes}
		products = {prod.index: prod for prod in network.products}

		with self.assertRaises(TypeError):
			_, _ = nodes[2].validate_raw_material(5.6)
			_, _ = nodes[2].validate_raw_material(SupplyChainNode(10))
		
		with self.assertRaises(ValueError):
			_, _ = nodes[3].validate_raw_material(products[0])
			_, _ = nodes[3].validate_raw_material(0)
			_, _ = nodes[2].validate_raw_material(None)

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

		self.assertEqual(network.nodes_by_index[1].forward_echelon_lead_time, 1)
		self.assertEqual(network.nodes_by_index[2].forward_echelon_lead_time, 2)
		self.assertEqual(network.nodes_by_index[3].forward_echelon_lead_time, 4)
		self.assertEqual(network.nodes_by_index[4].forward_echelon_lead_time, 6)
		self.assertEqual(network.nodes_by_index[5].forward_echelon_lead_time, 6)
		self.assertEqual(network.nodes_by_index[6].forward_echelon_lead_time, 7)
		self.assertEqual(network.nodes_by_index[7].forward_echelon_lead_time, 8)


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

		self.assertEqual(network.nodes_by_index[1].equivalent_lead_time, 1)
		self.assertEqual(network.nodes_by_index[2].equivalent_lead_time, 1)
		self.assertEqual(network.nodes_by_index[3].equivalent_lead_time, 2)
		self.assertEqual(network.nodes_by_index[4].equivalent_lead_time, 2)
		self.assertEqual(network.nodes_by_index[5].equivalent_lead_time, 0)
		self.assertEqual(network.nodes_by_index[6].equivalent_lead_time, 1)
		self.assertEqual(network.nodes_by_index[7].equivalent_lead_time, 1)


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

		self.assertEqual(network.nodes_by_index[1].derived_demand_mean, 5)
		self.assertEqual(network.nodes_by_index[2].derived_demand_mean, 5)
		self.assertEqual(network.nodes_by_index[3].derived_demand_mean, 5)

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
		network.nodes_by_index[1].demand_source = demand_source

		self.assertEqual(network.nodes_by_index[1].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[2].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[3].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[4].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[5].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[6].derived_demand_mean, 15)
		self.assertEqual(network.nodes_by_index[7].derived_demand_mean, 15)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(a).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		self.assertEqual(network.nodes_by_index[0].derived_demand_mean, 32)
		self.assertEqual(network.nodes_by_index[1].derived_demand_mean, 16)
		self.assertEqual(network.nodes_by_index[2].derived_demand_mean, 16)
		self.assertEqual(network.nodes_by_index[3].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[4].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[5].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[6].derived_demand_mean, 8)

	def test_rong_atan_snyder_figure_1b(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(b).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1b()')

		network = load_instance("rong_atan_snyder_figure_1b")

		self.assertEqual(network.nodes_by_index[0].derived_demand_mean, 64)
		self.assertEqual(network.nodes_by_index[1].derived_demand_mean, 40)
		self.assertEqual(network.nodes_by_index[2].derived_demand_mean, 24)
		self.assertEqual(network.nodes_by_index[3].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[4].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[5].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[6].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[7].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[8].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[9].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[10].derived_demand_mean, 8)

	def test_rong_atan_snyder_figure_1c(self):
		"""Test derived_demand_mean() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(c).
		"""
		print_status('TestDerivedDemandMean', 'test_rong_atan_snyder_figure_1c()')

		network = load_instance("rong_atan_snyder_figure_1c")

		self.assertEqual(network.nodes_by_index[0].derived_demand_mean, 32)
		self.assertEqual(network.nodes_by_index[1].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[2].derived_demand_mean, 24)
		self.assertEqual(network.nodes_by_index[3].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[4].derived_demand_mean, 8)
		self.assertEqual(network.nodes_by_index[5].derived_demand_mean, 8)


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

		self.assertEqual(network.nodes_by_index[1].derived_demand_standard_deviation, 1)
		self.assertEqual(network.nodes_by_index[2].derived_demand_standard_deviation, 1)
		self.assertEqual(network.nodes_by_index[3].derived_demand_standard_deviation, 1)

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
		network.nodes_by_index[1].demand_source = demand_source

		self.assertEqual(network.nodes_by_index[1].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[2].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[3].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[4].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[5].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[6].derived_demand_standard_deviation, 2)
		self.assertEqual(network.nodes_by_index[7].derived_demand_standard_deviation, 2)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(a).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		self.assertAlmostEqual(network.nodes_by_index[0].derived_demand_standard_deviation, math.sqrt(32))
		self.assertAlmostEqual(network.nodes_by_index[1].derived_demand_standard_deviation, math.sqrt(16))
		self.assertAlmostEqual(network.nodes_by_index[2].derived_demand_standard_deviation, math.sqrt(16))
		self.assertAlmostEqual(network.nodes_by_index[3].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[4].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[5].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[6].derived_demand_standard_deviation, math.sqrt(8))

	def test_rong_atan_snyder_figure_1b(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(b).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1b()')

		network = load_instance("rong_atan_snyder_figure_1b")

		self.assertAlmostEqual(network.nodes_by_index[0].derived_demand_standard_deviation, math.sqrt(64))
		self.assertAlmostEqual(network.nodes_by_index[1].derived_demand_standard_deviation, math.sqrt(40))
		self.assertAlmostEqual(network.nodes_by_index[2].derived_demand_standard_deviation, math.sqrt(24))
		self.assertAlmostEqual(network.nodes_by_index[3].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[4].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[5].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[6].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[7].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[8].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[9].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[10].derived_demand_standard_deviation, math.sqrt(8))

	def test_rong_atan_snyder_figure_1c(self):
		"""Test derived_demand_standard_deviation() for distribution system (Rong, Atan, and Snyder (2017),
		Figure 1(c).
		"""
		print_status('TestDerivedDemandStandardDeviation', 'test_rong_atan_snyder_figure_1c()')

		network = load_instance("rong_atan_snyder_figure_1c")

		self.assertAlmostEqual(network.nodes_by_index[0].derived_demand_standard_deviation, math.sqrt(32))
		self.assertAlmostEqual(network.nodes_by_index[1].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[2].derived_demand_standard_deviation, math.sqrt(24))
		self.assertAlmostEqual(network.nodes_by_index[3].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[4].derived_demand_standard_deviation, math.sqrt(8))
		self.assertAlmostEqual(network.nodes_by_index[5].derived_demand_standard_deviation, math.sqrt(8))



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

		node1 = network.nodes_by_index[1]
		node2 = network.nodes_by_index[2]
		node3 = network.nodes_by_index[3]

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

		node0 = network.nodes_by_index[0]
		node2 = network.nodes_by_index[2]
		node6 = network.nodes_by_index[6]

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

		# Replace network and product objects.
		for n in dict_nodes:
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

		# Replace network and product objects.
		for n in dict_nodes:
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

		# Replace network and product objects.
		for n in dict_nodes:
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

		# Replace network and product objects.
		for n in dict_nodes:
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
		n1 = network1.nodes_by_index[3]
		n2 = network2.nodes_by_index[3]
		n2.local_holding_cost = SupplyChainNode._DEFAULT_VALUES['local_holding_cost']
		self.assertTrue(n1.deep_equal_to(n2))

		# In this instance, node 1 is missing the ``demand_source`` attribute.
		network1 = load_instance("missing_demand_source_node_1", "tests/additional_files/test_supply_chain_node_TestNodeToFromDict_data.json")
		network2 = load_instance("example_6_1")
		n1 = network1.nodes_by_index[1]
		n2 = network2.nodes_by_index[1]
		n2.demand_source = DemandSource()
		self.assertTrue(n1.deep_equal_to(n2))

		# In this instance, the ``disruption_process`` attribute at node 1 is missing the ``recovery_probability`` attribute.
		network1 = load_instance("missing_recovery_probability_node_1", "tests/additional_files/test_supply_chain_node_TestNodeToFromDict_data.json")
		network2 = load_instance("example_6_1")
		n1 = network1.nodes_by_index[1]
		n2 = network2.nodes_by_index[1]
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

		# Replace network objects.
		# Fill products.
		for n in dict_nodes:
			n.network = network
			if n._dummy_product is not None:
				n._dummy_product = network.products_by_index[n._dummy_product]
			if n._external_supplier_dummy_product is not None:
				n._external_supplier_dummy_product = network.products_by_index[n._external_supplier_dummy_product]
			n._products_by_index = {k: network.products_by_index[k] for k in n._products_by_index.keys()}
			
			prods = copy.deepcopy(n.product_indices)
			n.remove_products('all')
			for prod in prods:
				n.add_product(network.products_by_index[prod])

		# Compare.
		for i in range(len(network.nodes)):
			self.assertTrue(network.nodes[i].deep_equal_to(dict_nodes[i]))


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

