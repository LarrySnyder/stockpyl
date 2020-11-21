import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from pyinv.supply_chain_node import *
from pyinv.supply_chain_network import *
from pyinv.instances import *
from pyinv.sim import *


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
		node3succ = node2.successor_indices()

		self.assertEqual(node0succ, [1, 2, 3])
		self.assertEqual(node1succ, [])
		self.assertEqual(node2succ, [])
		self.assertEqual(node3succ, [])


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
		print_status('TestAddSuccessor', 'test_rosling_figure_1()')

		network = get_named_instance("rosling_figure_1")

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})

		for i in range(7):
			self.assertEqual(network.nodes[i].index, i+11)

	def test_rosling_figure_1_with_names(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1.
		"""
		print_status('TestAddSuccessor', 'test_rosling_figure_1_with_names()')

		network = get_named_instance("rosling_figure_1")
		# Name the nodes "a"-"g".
		for i in range(1, 8):
			network.get_node_from_index(i).name = chr(97)

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17},
							  new_names={1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "F", 7: "G"})

		for i in range(7):
			self.assertEqual(network.nodes[i].index, i+11)
			self.assertEqual(network.nodes[i].name, chr(65+i))

	def test_rosling_figure_1_with_state_vars_pre(self):
		"""Test reindex_nodes() on system from Rosling (1989) Figure 1 using
		simulation to test state variable reindexing that occurs before simulation.
		"""
		print_status('TestAddSuccessor', 'test_rosling_figure_1_with_state_vars()')

		network = get_named_instance("rosling_figure_1")
		# Make the BS levels a little smaller so there are some stockouts.
		network.get_node_from_index(1).inventory_policy.echelon_base_stock_level = 6
		network.get_node_from_index(2).inventory_policy.echelon_base_stock_level = 20
		network.get_node_from_index(3).inventory_policy.echelon_base_stock_level = 35
		network.get_node_from_index(4).inventory_policy.echelon_base_stock_level = 58
		network.get_node_from_index(5).inventory_policy.echelon_base_stock_level = 45
		network.get_node_from_index(6).inventory_policy.echelon_base_stock_level = 65
		network.get_node_from_index(7).inventory_policy.echelon_base_stock_level = 75

		network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

		# Compare a few performance measures.
		self.assertEqual(network.get_node_from_index(11).state_vars[6].order_quantity[12], 4)
		self.assertEqual(network.get_node_from_index(11).state_vars[6].order_quantity[13], 4)
		self.assertEqual(network.get_node_from_index(12).state_vars[6].order_quantity[15], 4)
		self.assertEqual(network.get_node_from_index(13).state_vars[6].order_quantity[14], 4)
		self.assertEqual(network.get_node_from_index(14).state_vars[6].order_quantity[16], 0)
		self.assertEqual(network.get_node_from_index(14).state_vars[6].order_quantity[17], 0)
		self.assertEqual(network.get_node_from_index(11).state_vars[16].inventory_level, 3)
		self.assertEqual(network.get_node_from_index(12).state_vars[16].inventory_level, 7)
		self.assertEqual(network.get_node_from_index(13).state_vars[16].inventory_level, 4)
		self.assertEqual(network.get_node_from_index(14).state_vars[16].inventory_level, 9)
		self.assertEqual(network.get_node_from_index(15).state_vars[16].inventory_level, 7)
		self.assertEqual(network.get_node_from_index(16).state_vars[16].inventory_level, 19)
		self.assertEqual(network.get_node_from_index(17).state_vars[16].inventory_level, 24)
		self.assertEqual(network.get_node_from_index(11).state_vars[44].inventory_level, -4)
		self.assertEqual(network.get_node_from_index(12).state_vars[44].inventory_level, -5)
		self.assertEqual(network.get_node_from_index(13).state_vars[44].inventory_level, 0)
		self.assertEqual(network.get_node_from_index(14).state_vars[44].inventory_level, -2)
		self.assertEqual(network.get_node_from_index(15).state_vars[44].inventory_level, -6)
		self.assertEqual(network.get_node_from_index(16).state_vars[44].inventory_level, 0)
		self.assertEqual(network.get_node_from_index(17).state_vars[44].inventory_level, 10)
		self.assertEqual(network.get_node_from_index(11).state_vars[16].inbound_shipment[12], 2)
		self.assertEqual(network.get_node_from_index(11).state_vars[16].inbound_shipment[13], 2)
		self.assertEqual(network.get_node_from_index(12).state_vars[16].inbound_shipment[15], 1)
		self.assertEqual(network.get_node_from_index(13).state_vars[16].inbound_shipment[14], 0)
		self.assertEqual(network.get_node_from_index(14).state_vars[16].inbound_shipment[16], 12)
		self.assertEqual(network.get_node_from_index(14).state_vars[16].inbound_shipment[17], 12)
		self.assertEqual(network.get_node_from_index(15).state_vars[16].inbound_shipment[None], 9)
		self.assertEqual(network.get_node_from_index(16).state_vars[16].inbound_shipment[None], 13)
		self.assertEqual(network.get_node_from_index(17).state_vars[16].inbound_shipment[None], 12)
		self.assertEqual(network.get_node_from_index(11).state_vars[45].raw_material_inventory[12], 0)
		self.assertEqual(network.get_node_from_index(11).state_vars[45].raw_material_inventory[13], 5)
		self.assertEqual(network.get_node_from_index(12).state_vars[45].raw_material_inventory[15], 0)
		self.assertEqual(network.get_node_from_index(14).state_vars[45].raw_material_inventory[16], 0)


def test_rosling_figure_1_with_state_vars_post(self):
	"""Test reindex_nodes() on system from Rosling (1989) Figure 1 using
	simulation to test state variable reindexing that occurs after simulation.
	"""
	print_status('TestAddSuccessor', 'test_rosling_figure_1_with_state_vars()')

	network = get_named_instance("rosling_figure_1")
	# Make the BS levels a little smaller so there are some stockouts.
	network.get_node_from_index(1).inventory_policy.echelon_base_stock_level = 6
	network.get_node_from_index(2).inventory_policy.echelon_base_stock_level = 20
	network.get_node_from_index(3).inventory_policy.echelon_base_stock_level = 35
	network.get_node_from_index(4).inventory_policy.echelon_base_stock_level = 58
	network.get_node_from_index(5).inventory_policy.echelon_base_stock_level = 45
	network.get_node_from_index(6).inventory_policy.echelon_base_stock_level = 65
	network.get_node_from_index(7).inventory_policy.echelon_base_stock_level = 75

	total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

	network.reindex_nodes({1: 11, 2: 12, 3: 13, 4: 14, 5: 15, 6: 16, 7: 17})

	# Compare a few performance measures.
	self.assertEqual(network.get_node_from_index(11).state_vars[6].order_quantity[12], 4)
	self.assertEqual(network.get_node_from_index(11).state_vars[6].order_quantity[13], 4)
	self.assertEqual(network.get_node_from_index(12).state_vars[6].order_quantity[15], 4)
	self.assertEqual(network.get_node_from_index(13).state_vars[6].order_quantity[14], 4)
	self.assertEqual(network.get_node_from_index(14).state_vars[6].order_quantity[16], 0)
	self.assertEqual(network.get_node_from_index(14).state_vars[6].order_quantity[17], 0)
	self.assertEqual(network.get_node_from_index(11).state_vars[16].inventory_level, 3)
	self.assertEqual(network.get_node_from_index(12).state_vars[16].inventory_level, 7)
	self.assertEqual(network.get_node_from_index(13).state_vars[16].inventory_level, 4)
	self.assertEqual(network.get_node_from_index(14).state_vars[16].inventory_level, 9)
	self.assertEqual(network.get_node_from_index(15).state_vars[16].inventory_level, 7)
	self.assertEqual(network.get_node_from_index(16).state_vars[16].inventory_level, 19)
	self.assertEqual(network.get_node_from_index(17).state_vars[16].inventory_level, 24)
	self.assertEqual(network.get_node_from_index(11).state_vars[44].inventory_level, -4)
	self.assertEqual(network.get_node_from_index(12).state_vars[44].inventory_level, -5)
	self.assertEqual(network.get_node_from_index(13).state_vars[44].inventory_level, 0)
	self.assertEqual(network.get_node_from_index(14).state_vars[44].inventory_level, -2)
	self.assertEqual(network.get_node_from_index(15).state_vars[44].inventory_level, -6)
	self.assertEqual(network.get_node_from_index(16).state_vars[44].inventory_level, 0)
	self.assertEqual(network.get_node_from_index(17).state_vars[44].inventory_level, 10)
	self.assertEqual(network.get_node_from_index(11).state_vars[16].inbound_shipment[12], 2)
	self.assertEqual(network.get_node_from_index(11).state_vars[16].inbound_shipment[13], 2)
	self.assertEqual(network.get_node_from_index(12).state_vars[16].inbound_shipment[15], 1)
	self.assertEqual(network.get_node_from_index(13).state_vars[16].inbound_shipment[14], 0)
	self.assertEqual(network.get_node_from_index(14).state_vars[16].inbound_shipment[16], 12)
	self.assertEqual(network.get_node_from_index(14).state_vars[16].inbound_shipment[17], 12)
	self.assertEqual(network.get_node_from_index(15).state_vars[16].inbound_shipment[None], 9)
	self.assertEqual(network.get_node_from_index(16).state_vars[16].inbound_shipment[None], 13)
	self.assertEqual(network.get_node_from_index(17).state_vars[16].inbound_shipment[None], 12)
	self.assertEqual(network.get_node_from_index(11).state_vars[45].raw_material_inventory[12], 0)
	self.assertEqual(network.get_node_from_index(11).state_vars[45].raw_material_inventory[13], 5)
	self.assertEqual(network.get_node_from_index(12).state_vars[45].raw_material_inventory[15], 0)
	self.assertEqual(network.get_node_from_index(14).state_vars[45].raw_material_inventory[16], 0)


class TestSingleStageSystem(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSingleStageSystem', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSingleStageSystem', 'tear_down_class()')

	def test_example_4_1(self):
		"""Test single_stage() to build system in Example 4.1.
		"""
		print_status('TestSingleStageSystem', 'test_example_4_1()')

		network = single_stage(holding_cost=0.18,
							    stockout_cost=0.70,
								demand_type=DemandType.NORMAL,
								demand_mean=50, demand_standard_deviation=8,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								base_stock_level=56.6)

		node = network.nodes[0]
		self.assertEqual(node.holding_cost, 0.18)
		self.assertEqual(node.stockout_cost, 0.70)
		self.assertEqual(node.demand_source.mean, 50)
		self.assertEqual(node.demand_source.standard_deviation, 8)
		self.assertEqual(node.inventory_policy.base_stock_level, 56.6)


	def test_3_node_serial_upstream_0(self):
		"""Test serial_system() to build 3-node serial system, indexed 0,...,2
		with upstream node = 0.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_upstream_0()')

		network = serial_system(3, downstream_0=False,
								local_holding_cost=[7, 4, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[5, 5, 5])

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

		self.assertEqual(source_node.index, 0)
		self.assertEqual(middle_node.index, 1)
		self.assertEqual(sink_node.index, 2)

		self.assertEqual(source_node_succ, [1])
		self.assertEqual(middle_node_succ, [2])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [0])
		self.assertEqual(sink_node_pred, [1])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

	def test_3_node_serial_index_list(self):
		"""Test serial_system() to build 3-node serial system, with index list
		given explicitly.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_index_list()')

		network = serial_system(3, node_indices=[17, 14, 12],
								local_holding_cost=[7, 4, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[5, 5, 5])

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
		"""Test serial_system() to build 3-node serial system, indexed 0,...,2
		with downstream node = 0.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_downstream_0()')

		network = serial_system(3, local_holding_cost=[7, 4, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[5, 5, 5])

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

	def test_3_node_serial_upstream_0(self):
		"""Test serial_system() to build 3-node serial system, indexed 0,...,2
		with upstream node = 0.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_upstream_0()')

		network = serial_system(3, downstream_0=False,
								local_holding_cost=[7, 4, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[5, 5, 5])

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

		self.assertEqual(source_node.index, 0)
		self.assertEqual(middle_node.index, 1)
		self.assertEqual(sink_node.index, 2)

		self.assertEqual(source_node_succ, [1])
		self.assertEqual(middle_node_succ, [2])
		self.assertEqual(sink_node_succ, [])
		self.assertEqual(source_node_pred, [])
		self.assertEqual(middle_node_pred, [0])
		self.assertEqual(sink_node_pred, [1])

		self.assertEqual(source_node.local_holding_cost, 2)
		self.assertEqual(middle_node.local_holding_cost, 4)
		self.assertEqual(sink_node.local_holding_cost, 7)

	def test_3_node_serial_index_list(self):
		"""Test serial_system() to build 3-node serial system, with index list
		given explicitly.
		"""
		print_status('TestSerialSystem', 'test_3_node_serial_index_list()')

		network = serial_system(3, node_indices=[17, 14, 12],
								local_holding_cost={17: 7, 14: 4, 12: 2},
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=5)

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


class TestMWORSystem(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMWORSystem', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMWORSystem', 'tear_down_class()')

	def test_4_node_mrow_downstream_0(self):
		"""Test mwor_system() to build 4-node MWOR system, indexed
		with downstream node = 0.
		"""
		print_status('TestMWORSystem', 'test_4_node_mwor_downstream_0()')

		network = mwor_system(3, local_holding_cost=[5, 1, 1, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[10, 10, 10, 10])

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

	def test_4_node_mrow_downstream_3(self):
		"""Test mwor_system() to build 4-node MWOR system, indexed
		with downstream node = 3.
		"""
		print_status('TestMWORSystem', 'test_4_node_mrow_downstream_3()')

		network = mwor_system(3, downstream_0=False,
								local_holding_cost=[5, 1, 1, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[10, 10, 10, 10])

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

		self.assertEqual(ret.index, 3)
		self.assertEqual(wh1.index, 2)
		self.assertEqual(wh2.index, 1)
		self.assertEqual(wh3.index, 0)

		self.assertEqual(ret_succ, [])
		self.assertEqual(wh1_succ, [3])
		self.assertEqual(wh2_succ, [3])
		self.assertEqual(wh3_succ, [3])
		self.assertEqual(ret_pred, [2, 1, 0])
		self.assertEqual(wh1_pred, [])
		self.assertEqual(wh2_pred, [])
		self.assertEqual(wh3_pred, [])

		self.assertEqual(ret.local_holding_cost, 5)
		self.assertEqual(wh1.local_holding_cost, 1)
		self.assertEqual(wh2.local_holding_cost, 1)
		self.assertEqual(wh3.local_holding_cost, 2)

	def test_4_node_mrow_index_list(self):
		"""Test mwor_system() to build 4-node MWOR system, with index list
		given explicitly
		"""
		print_status('TestMWORSystem', 'test_4_node_mrow_index_list()')

		network = mwor_system(3, node_indices=[17, 14, 12, 5],
								local_holding_cost=[5, 1, 1, 2],
								demand_type=DemandType.NORMAL,
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type=InventoryPolicyType.BASE_STOCK,
								local_base_stock_levels=[10, 10, 10, 10])

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
		self.assertEqual(wh1.index, 14)
		self.assertEqual(wh2.index, 12)
		self.assertEqual(wh3.index, 5)

		self.assertEqual(ret_succ, [])
		self.assertEqual(wh1_succ, [17])
		self.assertEqual(wh2_succ, [17])
		self.assertEqual(wh3_succ, [17])
		self.assertEqual(ret_pred, [14, 12, 5])
		self.assertEqual(wh1_pred, [])
		self.assertEqual(wh2_pred, [])
		self.assertEqual(wh3_pred, [])

		self.assertEqual(ret.local_holding_cost, 5)
		self.assertEqual(wh1.local_holding_cost, 1)
		self.assertEqual(wh2.local_holding_cost, 1)
		self.assertEqual(wh3.local_holding_cost, 2)


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


