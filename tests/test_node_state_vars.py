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

		nodes = {i: network.nodes_by_index[i] for i in range(1, 4)}
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

		nodes = {i: network.nodes_by_index[i] for i in range(1, 4)}
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

		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
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
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(predecessor=1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[22].echelon_inventory_position(predecessor=2), IL0+OO02+RM02)
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

		nodes = {i: network.nodes_by_index[i] for i in network.node_indices}
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
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(predecessor=1), IL0+OO01+RM01)
		self.assertEqual(nodes[0].state_vars[per].echelon_inventory_position(predecessor=2), IL0+OO02+RM02)
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
	# 		node = network.nodes_by_index[n_ind]
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
	# 		node = network.nodes_by_index[n_ind]
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


class TestGetStateVariables(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGetStateVariables', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGetStateVariables', 'tear_down_class()')

	def test_example_6_1_per_22(self):
		"""Test state variables for simulation of 3-node serial system in
		Example 6.1 at end of period 22.
		"""
		print_status('TestGetStateVariables', 'test_example_6_1_per_22()')

		network = load_instance("example_6_1")

		# Strategy for these tests: run sim for a few periods, test state
		# variable shortcuts against dicts.
		simulation(network, 23, rand_seed=17, progress_bar=False)

		nodes = {i: network.nodes_by_index[i] for i in range(1, 4)}

		for n in nodes.values():
			# Indexed by predecessor and raw material.
			for rm in n.raw_materials_by_product('all', network_BOM=True):
				rm_ind = rm.index
				for pred_ind in n.raw_material_suppliers_by_raw_material(rm_ind, return_indices=True, network_BOM=True):
					self.assertEqual(n.state_vars[22].inbound_shipment[pred_ind][rm_ind],
						n.state_vars[22].get_inbound_shipment(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[22].on_order_by_predecessor[pred_ind][rm_ind],
						n.state_vars[22].get_on_order_by_predecessor(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[22].inbound_disrupted_items[pred_ind][rm_ind],
						n.state_vars[22].get_inbound_disrupted_items(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[22].order_quantity[pred_ind][rm_ind],
						n.state_vars[22].get_order_quantity(predecessor=pred_ind, raw_material=rm_ind))
					for r in range(len(n.state_vars[22].inbound_shipment_pipeline[pred_ind][rm_ind])):
						self.assertEqual(n.state_vars[22].inbound_shipment_pipeline[pred_ind][rm_ind][r],
							n.state_vars[22].get_inbound_shipment_pipeline(periods_from_now=r, predecessor=pred_ind, raw_material=rm_ind))

			# Indexed by successor and product.
			for product in n.products:
				prod_ind = product.index
				for succ_ind in n.successor_indices(include_external=True):
					self.assertEqual(n.state_vars[22].inbound_order[succ_ind][prod_ind],
						n.state_vars[22].get_inbound_order(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[22].outbound_shipment[succ_ind][prod_ind],
					  	n.state_vars[22].get_outbound_shipment(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[22].backorders_by_successor[succ_ind][prod_ind],
					  	n.state_vars[22].get_backorders_by_successor(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[22].outbound_disrupted_items[succ_ind][prod_ind],
					  	n.state_vars[22].get_outbound_disrupted_items(successor=succ_ind, product=prod_ind))
					for r in range(len(n.state_vars[22].inbound_order_pipeline[succ_ind][prod_ind])):
						self.assertEqual(n.state_vars[22].inbound_order_pipeline[succ_ind][prod_ind][r],
							n.state_vars[22].get_inbound_order_pipeline(periods_from_now=r, successor=succ_ind, product=prod_ind))
						
			# Indexed by product.
			for prod_ind in n.product_indices:
				self.assertEqual(n.state_vars[22].demand_cumul[prod_ind], n.state_vars[22].get_demand_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[22].inventory_level[prod_ind], n.state_vars[22].get_inventory_level(product=prod_ind))
				self.assertEqual(n.state_vars[22].pending_finished_goods[prod_ind], n.state_vars[22].get_pending_finished_goods(product=prod_ind))
				self.assertEqual(n.state_vars[22].demand_met_from_stock[prod_ind], n.state_vars[22].get_demand_met_from_stock(product=prod_ind))
				self.assertEqual(n.state_vars[22].demand_met_from_stock_cumul[prod_ind], n.state_vars[22].get_demand_met_from_stock_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[22].fill_rate[prod_ind], n.state_vars[22].get_fill_rate(product=prod_ind))
				self.assertEqual(n.state_vars[22].order_quantity_fg[prod_ind], n.state_vars[22].get_order_quantity_fg(product=prod_ind))

			# Indexed by raw material.
			for rm_ind in n.raw_materials_by_product('all', return_indices=True, network_BOM=True):
				self.assertEqual(n.state_vars[22].raw_material_inventory[rm_ind], n.state_vars[22].get_raw_material_inventory(raw_material=rm_ind))

	def test_assembly_3_stage_per_43(self):
		"""Test state variables for simulation of 3-node assembly system at end of period 43.
		"""
		print_status('TestGetStateVariables', 'test_assembly_3_stage_per_43()')

		network = load_instance("assembly_3_stage")

		# Strategy for these tests: run sim for a few periods, test state
		# variable shortcuts against dicts.
		simulation(network, 44, rand_seed=17, progress_bar=False)
		nodes = {n.index: n for n in network.nodes}

		for n in nodes.values():
			# Indexed by predecessor and raw material.
			for rm in n.raw_materials_by_product('all', network_BOM=True):
				rm_ind = rm.index
				for pred_ind in n.raw_material_suppliers_by_raw_material(rm_ind, return_indices=True, network_BOM=True):
					self.assertEqual(n.state_vars[43].inbound_shipment[pred_ind][rm_ind],
						n.state_vars[43].get_inbound_shipment(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].on_order_by_predecessor[pred_ind][rm_ind],
						n.state_vars[43].get_on_order_by_predecessor(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].inbound_disrupted_items[pred_ind][rm_ind],
						n.state_vars[43].get_inbound_disrupted_items(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].order_quantity[pred_ind][rm_ind],
						n.state_vars[43].get_order_quantity(predecessor=pred_ind, raw_material=rm_ind))
					for r in range(len(n.state_vars[43].inbound_shipment_pipeline[pred_ind][rm_ind])):
						self.assertEqual(n.state_vars[43].inbound_shipment_pipeline[pred_ind][rm_ind][r],
							n.state_vars[43].get_inbound_shipment_pipeline(periods_from_now=r, predecessor=pred_ind, raw_material=rm_ind))

			# Indexed by successor and product.
			for product in n.products:
				prod_ind = product.index
				for succ_ind in n.successor_indices(include_external=True):
					self.assertEqual(n.state_vars[43].inbound_order[succ_ind][prod_ind],
						n.state_vars[43].get_inbound_order(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].outbound_shipment[succ_ind][prod_ind],
					  	n.state_vars[43].get_outbound_shipment(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].backorders_by_successor[succ_ind][prod_ind],
					  	n.state_vars[43].get_backorders_by_successor(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].outbound_disrupted_items[succ_ind][prod_ind],
					  	n.state_vars[43].get_outbound_disrupted_items(successor=succ_ind, product=prod_ind))
					for r in range(len(n.state_vars[43].inbound_order_pipeline[succ_ind][prod_ind])):
						self.assertEqual(n.state_vars[43].inbound_order_pipeline[succ_ind][prod_ind][r],
							n.state_vars[43].get_inbound_order_pipeline(periods_from_now=r, successor=succ_ind, product=prod_ind))
						
			# Indexed by product.
			for prod_ind in n.product_indices:
				self.assertEqual(n.state_vars[43].demand_cumul[prod_ind], n.state_vars[43].get_demand_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[43].inventory_level[prod_ind], n.state_vars[43].get_inventory_level(product=prod_ind))
				self.assertEqual(n.state_vars[43].pending_finished_goods[prod_ind], n.state_vars[43].get_pending_finished_goods(product=prod_ind))
				self.assertEqual(n.state_vars[43].demand_met_from_stock[prod_ind], n.state_vars[43].get_demand_met_from_stock(product=prod_ind))
				self.assertEqual(n.state_vars[43].demand_met_from_stock_cumul[prod_ind], n.state_vars[43].get_demand_met_from_stock_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[43].fill_rate[prod_ind], n.state_vars[43].get_fill_rate(product=prod_ind))
				self.assertEqual(n.state_vars[43].order_quantity_fg[prod_ind], n.state_vars[43].get_order_quantity_fg(product=prod_ind))

			# Indexed by raw material.
			for rm_ind in n.raw_materials_by_product('all', return_indices=True, network_BOM=True):
				self.assertEqual(n.state_vars[43].raw_material_inventory[rm_ind], n.state_vars[43].get_raw_material_inventory(raw_material=rm_ind))

	def test_multiproduct_5_7_per_43(self):
		"""Test state variables for simulation of 5-node, 7-product system at end of period 43.
		"""
		print_status('TestGetStateVariables', 'test_multiproduct_5_7_per_43()')

		network = load_instance("bom_structure", "tests/additional_files/test_multiproduct_5_7.json")

		# Strategy for these tests: run sim for a few periods, test state
		# variable shortcuts against dicts.
		simulation(network, 44, rand_seed=17, progress_bar=False)
		nodes = {n.index: n for n in network.nodes}

		for n in nodes.values():
			# Indexed by predecessor and raw material.
			for rm in n.raw_materials_by_product('all', network_BOM=True):
				rm_ind = rm.index
				for pred_ind in n.raw_material_suppliers_by_raw_material(rm_ind, return_indices=True, network_BOM=True):
					self.assertEqual(n.state_vars[43].inbound_shipment[pred_ind][rm_ind],
						n.state_vars[43].get_inbound_shipment(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].on_order_by_predecessor[pred_ind][rm_ind],
						n.state_vars[43].get_on_order_by_predecessor(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].inbound_disrupted_items[pred_ind][rm_ind],
						n.state_vars[43].get_inbound_disrupted_items(predecessor=pred_ind, raw_material=rm_ind))
					self.assertEqual(n.state_vars[43].order_quantity[pred_ind][rm_ind],
						n.state_vars[43].get_order_quantity(predecessor=pred_ind, raw_material=rm_ind))
					for r in range(len(n.state_vars[43].inbound_shipment_pipeline[pred_ind][rm_ind])):
						self.assertEqual(n.state_vars[43].inbound_shipment_pipeline[pred_ind][rm_ind][r],
							n.state_vars[43].get_inbound_shipment_pipeline(periods_from_now=r, predecessor=pred_ind, raw_material=rm_ind))

			# Indexed by successor and product.
			for product in n.products:
				prod_ind = product.index
				for succ_ind in n.successor_indices(include_external=True):
					self.assertEqual(n.state_vars[43].inbound_order[succ_ind][prod_ind],
						n.state_vars[43].get_inbound_order(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].outbound_shipment[succ_ind][prod_ind],
					  	n.state_vars[43].get_outbound_shipment(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].backorders_by_successor[succ_ind][prod_ind],
					  	n.state_vars[43].get_backorders_by_successor(successor=succ_ind, product=prod_ind))
					self.assertEqual(n.state_vars[43].outbound_disrupted_items[succ_ind][prod_ind],
					  	n.state_vars[43].get_outbound_disrupted_items(successor=succ_ind, product=prod_ind))
					for r in range(len(n.state_vars[43].inbound_order_pipeline[succ_ind][prod_ind])):
						self.assertEqual(n.state_vars[43].inbound_order_pipeline[succ_ind][prod_ind][r],
							n.state_vars[43].get_inbound_order_pipeline(periods_from_now=r, successor=succ_ind, product=prod_ind))
						
			# Indexed by product.
			for prod_ind in n.product_indices:
				self.assertEqual(n.state_vars[43].demand_cumul[prod_ind], n.state_vars[43].get_demand_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[43].inventory_level[prod_ind], n.state_vars[43].get_inventory_level(product=prod_ind))
				self.assertEqual(n.state_vars[43].pending_finished_goods[prod_ind], n.state_vars[43].get_pending_finished_goods(product=prod_ind))
				self.assertEqual(n.state_vars[43].demand_met_from_stock[prod_ind], n.state_vars[43].get_demand_met_from_stock(product=prod_ind))
				self.assertEqual(n.state_vars[43].demand_met_from_stock_cumul[prod_ind], n.state_vars[43].get_demand_met_from_stock_cumul(product=prod_ind))
				self.assertEqual(n.state_vars[43].fill_rate[prod_ind], n.state_vars[43].get_fill_rate(product=prod_ind))
				self.assertEqual(n.state_vars[43].order_quantity_fg[prod_ind], n.state_vars[43].get_order_quantity_fg(product=prod_ind))

			# Indexed by raw material.
			for rm_ind in n.raw_materials_by_product('all', return_indices=True, network_BOM=True):
				self.assertEqual(n.state_vars[43].raw_material_inventory[rm_ind], n.state_vars[43].get_raw_material_inventory(raw_material=rm_ind))


		
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


class TestPreviousBugs(unittest.TestCase):
	"""Test issues that have previously failed due to bugs."""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestPreviousBugs', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestPreviousBugs', 'tear_down_class()')

	def test_165(self):
		"""Test instance in issue #165 (Bug in sim with order lead time).
		"""
		print_status('TestPreviousBugs', 'test_165()')

		# Just check to make sure no exceptions are raised.
		
		from stockpyl.supply_chain_network import network_from_edges
		from stockpyl.sim import simulation
		from stockpyl.sim_io import write_results
		network = network_from_edges(
			edges=[(3, 2), (3, 1), (4, 1)],
			node_order_in_lists=[1, 2, 3, 4],
			local_holding_cost=[2, 2, 1, 1],
			stockout_cost=[10, 10, 0, 0],
			order_lead_time=[0, 1, 0, 0],   
			shipment_lead_time=[2, 1, 0, 1],
			demand_type=['P', 'P', None, None],
			mean=[10, 10, None, None],
			policy_type=['BS', 'BS', 'BS', 'BS'],
			base_stock_level=[30, 25, 10, 10]
		)
		simulation(network=network, num_periods=10, rand_seed=40)