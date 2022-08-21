import unittest
import random
import filecmp

from stockpyl.instances import *
from stockpyl.sim import *
from stockpyl.sim_io import write_results
from stockpyl.supply_chain_network import local_to_echelon_base_stock_levels
from stockpyl.policy import *
from stockpyl.disruption_process import DisruptionProcess


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_sim   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestSimulation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSimulation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSimulation', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that simulation() function correctly simulates model from
		Example 6.1.
		"""
		print_status('TestSimulation', 'test_example_6_1()')

		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 6620.352025, places=4)

		nodes = {n.index: n for n in network.nodes}

		# Compare a few performance measures.
		self.assertAlmostEqual(nodes[0].state_vars[6].order_quantity[1], 4.8883, places=4)
		self.assertAlmostEqual(nodes[0].state_vars[95].inventory_level, -1.08737, places=4)
		self.assertAlmostEqual(nodes[1].state_vars[43].inbound_order[0], 4.30582, places=4)
		self.assertAlmostEqual(nodes[1].state_vars[95].inbound_shipment[2], 6.97664, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[31].backorders_by_successor[1], 0.148957, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[89].inventory_level, 0.0443519, places=4)

	def test_problem_6_1(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.1.
		"""
		print_status('TestSimulation', 'test_problem_6_1()')

		network = load_instance("problem_6_1")
		
		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		total_cost = simulation(network, 100, rand_seed=531, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 35794.476254, places=4)

		nodes = {n.index: n for n in network.nodes}

		# Compare a few performance measures.
		self.assertAlmostEqual(nodes[1].state_vars[6].order_quantity[2], 140.6747130757738, places=4)
		self.assertAlmostEqual(nodes[1].state_vars[95].inventory_level, -21.4276, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[43].inbound_order[1], 98.6768, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[95].inbound_shipment[None], 105.7364470997879, places=4)
		self.assertAlmostEqual(nodes[1].state_vars[31].backorders_by_successor[None], 18.9103, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[89].inventory_level, -28.4205, places=4)

	def test_problem_6_2a(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.2(a).
		"""
		print_status('TestSimulation', 'test_problem_6_2a()')

		network = load_instance("problem_6_2a_adj")
		
		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		total_cost = simulation(network, 100, rand_seed=1340, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 38381.048422, places=4)

		nodes = {n.index: n for n in network.nodes}

		# Compare a few performance measures.
		self.assertAlmostEqual(nodes[1].state_vars[6].order_quantity[2], 34.7807, places=4)
		self.assertAlmostEqual(nodes[1].state_vars[95].inventory_level, 5.60159, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[43].inbound_order[1], 36.0213, places=4)
		self.assertAlmostEqual(nodes[2].state_vars[96].inbound_shipment[3], 34.9884, places=4)
		self.assertAlmostEqual(nodes[3].state_vars[32].backorders_by_successor[2], 2.67911, places=4)
		self.assertAlmostEqual(nodes[3].state_vars[89].inventory_level, -1.76791, places=4)
		self.assertAlmostEqual(nodes[4].state_vars[67].outbound_shipment[3], 30.0597, places=4)
		self.assertAlmostEqual(nodes[4].state_vars[84].fill_rate, 0.843055, places=4)
		self.assertAlmostEqual(nodes[5].state_vars[58].on_order_by_predecessor[None], 26.8160166, places=4)
		self.assertAlmostEqual(nodes[5].state_vars[81].holding_cost_incurred, 2.58384, places=4)

	def test_problem_6_16(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.16.
		"""
		print_status('TestSimulation', 'test_problem_6_16()')

		network = load_instance("problem_6_16")

		total_cost = simulation(network, 100, rand_seed=762, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 52386.309175, places=4)

		# Compare a few performance measures.
		node1 = network.get_node_from_index(1)
		node2 = network.get_node_from_index(2)
		self.assertAlmostEqual(node1.state_vars[6].order_quantity[2], 23.5517, places=4)
		self.assertAlmostEqual(node1.state_vars[95].inventory_level, -4.72853, places=4)
		self.assertAlmostEqual(node2.state_vars[43].inbound_order[1], 11.0029, places=4)
		self.assertAlmostEqual(node2.state_vars[95].inbound_shipment[None], 19.9307, places=4)
		self.assertAlmostEqual(node1.state_vars[31].backorders_by_successor[None], 26.9162, places=4)
		self.assertAlmostEqual(node2.state_vars[89].inventory_level, -12.6397, places=4)

	def test_single_stage(self):
		"""Test that simulation() function correctly simulates single-stage
		model with base-stock policy.
		"""
		print_status('TestSimulation', 'test_single_stage()')

		network = load_instance("example_4_1_network")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		total_cost = simulation(network, num_periods=100, rand_seed=762, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 255.2472033, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[None], 57.103320, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, 9.9564105, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[43].inbound_order[None], 32.00584965, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inbound_shipment[None], 52.9079333, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[19].backorders_by_successor[None], 6.7125153, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[86].inventory_level, -2.09415258242449, places=4)

	def test_no_policy_node(self):
		"""Test that simulation still works if we don't set the node attribute of the inventory policy.
		(node should be set by the property setter.)
		"""
		print_status('TestGetOrderQuantity', 'test_no_policy_node()')

		network = load_instance("example_4_1_network")

		# Replace inventory policy with a new one.
		pol = Policy()
		pol.type = 'BS'
		pol.base_stock_level = network.nodes[0].inventory_policy.base_stock_level
		network.nodes[0].inventory_policy = pol

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		total_cost = simulation(network, num_periods=100, rand_seed=762, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 255.2472033, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[None], 57.103320, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, 9.9564105, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[43].inbound_order[None], 32.00584965, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inbound_shipment[None], 52.9079333, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[19].backorders_by_successor[None], 6.7125153, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[86].inventory_level, -2.09415258242449, places=4)

	def test_assembly_3_stage(self):
		"""Test that simulation() function correctly simulates 3-stage assembly model.
		"""
		print_status('TestSimulation', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")
		#network = load_instance_old("assembly_3_stage", "/Users/larry/Documents/GitHub/stockpyl/src/stockpyl/datasets/stockpyl_instances_old.json")

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertEqual(total_cost, 1884)

		nodes = {n.index: n for n in network.nodes}

		# Compare a few performance measures.
		self.assertEqual(nodes[0].state_vars[6].order_quantity[1], 5)
		self.assertEqual(nodes[0].state_vars[6].order_quantity[2], 5)
		self.assertEqual(nodes[0].state_vars[26].inventory_level, 3)
		self.assertEqual(nodes[1].state_vars[26].inventory_level, 4)
		self.assertEqual(nodes[2].state_vars[26].inventory_level, 2)
		self.assertEqual(nodes[0].state_vars[41].inventory_level, -1)
		self.assertEqual(nodes[1].state_vars[41].inventory_level, 1)
		self.assertEqual(nodes[2].state_vars[41].inventory_level, -1)
		self.assertEqual(nodes[1].state_vars[43].inbound_order[0], 4)
		self.assertEqual(nodes[2].state_vars[43].inbound_order[0], 4)
		self.assertEqual(nodes[0].state_vars[95].inbound_shipment[1], 6)
		self.assertEqual(nodes[0].state_vars[95].inbound_shipment[2], 7)
		self.assertEqual(nodes[1].state_vars[95].inbound_shipment[None], 4)
		self.assertEqual(nodes[2].state_vars[95].inbound_shipment[None], 4)
		self.assertEqual(nodes[2].state_vars[78].backorders_by_successor[0], 2)

	def test_rosling_figure_1(self):
		"""Test that simulation() function correctly simulates model in Rosling (1989),
		Figure 1.
		"""
		print_status('TestSimulation', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")
		# Make the BS levels a little smaller so there are some stockouts.
		network.get_node_from_index(1).inventory_policy.base_stock_level = 6
		network.get_node_from_index(2).inventory_policy.base_stock_level = 20
		network.get_node_from_index(3).inventory_policy.base_stock_level = 35
		network.get_node_from_index(4).inventory_policy.base_stock_level = 58
		network.get_node_from_index(5).inventory_policy.base_stock_level = 45
		network.get_node_from_index(6).inventory_policy.base_stock_level = 65
		network.get_node_from_index(7).inventory_policy.base_stock_level = 75

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Compare total cost.
		self.assertEqual(total_cost, 0)

		# Compare a few performance measures.
		self.assertEqual(network.get_node_from_index(1).state_vars[6].order_quantity[2], 4)
		self.assertEqual(network.get_node_from_index(1).state_vars[6].order_quantity[3], 4)
		self.assertEqual(network.get_node_from_index(2).state_vars[6].order_quantity[5], 4)
		self.assertEqual(network.get_node_from_index(3).state_vars[6].order_quantity[4], 4)
		self.assertEqual(network.get_node_from_index(4).state_vars[6].order_quantity[6], 0)
		self.assertEqual(network.get_node_from_index(4).state_vars[6].order_quantity[7], 0)
		self.assertEqual(network.get_node_from_index(1).state_vars[16].inventory_level, 3)
		self.assertEqual(network.get_node_from_index(2).state_vars[16].inventory_level, 7)
		self.assertEqual(network.get_node_from_index(3).state_vars[16].inventory_level, 4)
		self.assertEqual(network.get_node_from_index(4).state_vars[16].inventory_level, 9)
		self.assertEqual(network.get_node_from_index(5).state_vars[16].inventory_level, 7)
		self.assertEqual(network.get_node_from_index(6).state_vars[16].inventory_level, 19)
		self.assertEqual(network.get_node_from_index(7).state_vars[16].inventory_level, 24)
		self.assertEqual(network.get_node_from_index(1).state_vars[44].inventory_level, -4)
		self.assertEqual(network.get_node_from_index(2).state_vars[44].inventory_level, -5)
		self.assertEqual(network.get_node_from_index(3).state_vars[44].inventory_level, 0)
		self.assertEqual(network.get_node_from_index(4).state_vars[44].inventory_level, -2)
		self.assertEqual(network.get_node_from_index(5).state_vars[44].inventory_level, -6)
		self.assertEqual(network.get_node_from_index(6).state_vars[44].inventory_level, 0)
		self.assertEqual(network.get_node_from_index(7).state_vars[44].inventory_level, 10)
		self.assertEqual(network.get_node_from_index(1).state_vars[16].inbound_shipment[2], 2)
		self.assertEqual(network.get_node_from_index(1).state_vars[16].inbound_shipment[3], 2)
		self.assertEqual(network.get_node_from_index(2).state_vars[16].inbound_shipment[5], 1)
		self.assertEqual(network.get_node_from_index(3).state_vars[16].inbound_shipment[4], 0)
		self.assertEqual(network.get_node_from_index(4).state_vars[16].inbound_shipment[6], 12)
		self.assertEqual(network.get_node_from_index(4).state_vars[16].inbound_shipment[7], 12)
		self.assertEqual(network.get_node_from_index(5).state_vars[16].inbound_shipment[None], 9)
		self.assertEqual(network.get_node_from_index(6).state_vars[16].inbound_shipment[None], 13)
		self.assertEqual(network.get_node_from_index(7).state_vars[16].inbound_shipment[None], 12)
		self.assertEqual(network.get_node_from_index(1).state_vars[45].raw_material_inventory[2], 0)
		self.assertEqual(network.get_node_from_index(1).state_vars[45].raw_material_inventory[3], 5)
		self.assertEqual(network.get_node_from_index(2).state_vars[45].raw_material_inventory[5], 0)
		self.assertEqual(network.get_node_from_index(4).state_vars[45].raw_material_inventory[6], 0)

	def test_directed_cycle(self):
		"""Test that simulation() function correctly raises a ValueError if network contains a 
		directed cycle.
		"""
		print_status('TestSimulation', 'test_directed_cycle()')

		instance = load_instance("example_6_1")
		instance.add_edge(1, 3)

		with self.assertRaises(ValueError):
			simulation(instance, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

	def test_no_policy(self):
		"""Test that simulation() function correctly raises an exception if a node has no inventory_policy.
		"""
		print_status('TestSimulation', 'test_example_6_1()')

		network = load_instance("example_6_1")
		network.nodes[1].inventory_policy = None

		with self.assertRaises(AttributeError):
			total_cost = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

	def test_node_not_set(self):
		"""Test that policy correctly raises an exception if a node's inventory_policy has no node attribute.
		"""
		print_status('TestSimulation', 'test_example_6_1()')

		network = load_instance("example_6_1")
		network.nodes[1].inventory_policy.node = None

		with self.assertRaises(AttributeError):
			total_cost = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')


class TestStepByStepSimulation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestStepByStepSimulation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestStepByStepSimulation', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that initialize() + step() + close() match the results from simulation()
		for Example 6.1.
		"""
		print_status('TestStepByStepSimulation', 'test_example_6_1()')

		network1 = load_instance("example_6_1")
		network2 = load_instance("example_6_1")
		T = 100

		# Via simulation().
		total_cost1 = simulation(network1, num_periods=T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Via initialize() + step() + close().
		initialize(network2, num_periods=T, rand_seed=17)
		for _ in range(T):
			step(network2, consistency_checks='E')
		total_cost2 = close(network2)

		# Compare total cost.
		self.assertAlmostEqual(total_cost1, total_cost2)

		# Compare networks (in particular, state variables).
		self.assertTrue(network1.deep_equal_to(network2))

	def test_example_6_1_order_quantity_override(self):
		"""Test that initialize() + step() + close() match the results from simulation()
		for Example 6.1 with an order quantity override.
		"""
		print_status('TestStepByStepSimulation', 'test_example_6_1()')

		network1 = load_instance("example_6_1")
		network2 = load_instance("example_6_1")
		T = 100

		# Via simulation().
		total_cost1 = simulation(network1, num_periods=T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Via initialize() + step() + close().
		initialize(network2, num_periods=T, rand_seed=17)
		for t in range(T):
			if t == 40:
				step(network2, consistency_checks='E', order_quantity_override={
					network2.get_node_from_index(2): 33,
					network2.get_node_from_index(3): 77,
				})
			else:
				step(network2, consistency_checks='E')
		total_cost2 = close(network2)

		# Compare order quantities in period 40.
		self.assertEqual(network2.get_node_from_index(2).state_vars[40].order_quantity[3], 33.0)
		self.assertEqual(network2.get_node_from_index(3).state_vars[40].order_quantity[None], 77.0)
		self.assertAlmostEqual(network2.get_node_from_index(1).state_vars[40].order_quantity[2], 
			network1.get_node_from_index(1).state_vars[40].order_quantity[2])

	def test_problem_6_2a(self):
		"""Test that initialize() + step() + close() match the results from simulation() for
		Problem 6.2(a).
		"""
		print_status('TestStepByStepSimulation', 'test_problem_6_2a()')

		network1 = load_instance("problem_6_2a_adj")
		network2 = load_instance("problem_6_2a_adj")
		T = 100

		# Via simulation().
		total_cost1 = simulation(network1, num_periods=T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Via initialize() + step() + close().
		initialize(network2, num_periods=T, rand_seed=17)
		for _ in range(T):
			step(network2, consistency_checks='E')
		total_cost2 = close(network2)

		# Compare total cost.
		self.assertAlmostEqual(total_cost1, total_cost2)

		# Compare networks (in particular, state variables).
		self.assertTrue(network1.deep_equal_to(network2))

	def test_assembly_3_stage(self):
		"""Test that initialize() + step() + close() match the results from simulation() for
		3-stage assembly model.
		"""
		print_status('TestStepByStepSimulation', 'test_assembly_3_stage()')

		network1 = load_instance("assembly_3_stage")
		network2 = load_instance("assembly_3_stage")
		T = 100

		# Via simulation().
		total_cost1 = simulation(network1, num_periods=T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Via initialize() + step() + close().
		initialize(network2, num_periods=T, rand_seed=17)
		for _ in range(T):
			step(network2, consistency_checks='E')
		total_cost2 = close(network2)

		# Compare total cost.
		self.assertAlmostEqual(total_cost1, total_cost2)

		# Compare networks (in particular, state variables).
		self.assertTrue(network1.deep_equal_to(network2))

	def test_rosling_figure_1(self):
		"""Test that initialize() + step() + close() match the results from simulation() for Rosling (1989),
		Figure 1.
		"""
		print_status('TestStepByStepSimulation', 'test_rosling_figure_1()')

		network1 = load_instance("rosling_figure_1")
		network2 = load_instance("rosling_figure_1")
		T = 100

		# Via simulation().
		total_cost1 = simulation(network1, num_periods=T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Via initialize() + step() + close().
		initialize(network2, num_periods=T, rand_seed=17)
		for _ in range(T):
			step(network2, consistency_checks='E')
		total_cost2 = close(network2)

		# Compare total cost.
		self.assertAlmostEqual(total_cost1, total_cost2)

		# Compare networks (in particular, state variables).
		self.assertTrue(network1.deep_equal_to(network2))

	def test_directed_cycle(self):
		"""Test that initialize() function correctly raises a ValueError if network contains a 
		directed cycle.
		"""
		print_status('TestStepByStepSimulation', 'test_directed_cycle()')

		instance = load_instance("example_6_1")
		instance.add_edge(1, 3)

		with self.assertRaises(ValueError):
			initialize(instance, 100, rand_seed=17)


class TestSimulationWithDisruptions(unittest.TestCase):
	"""Test simulation results for simulation with disruptions.
	"""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSimulationWithDisruptions', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSimulationWithDisruptions', 'tear_down_class()')

	def test_example_6_1_OP(self):
		"""Test that simulation() function correctly simulates model from
		Example 6.1 with type-OP disruptions.
		"""
		print_status('TestSimulationWithDisruptions', 'test_example_6_1_OP()')

		network = load_instance("example_6_1")

		network.get_node_from_index(2).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.4
		)

		_ = simulation(network, 100, rand_seed=42, progress_bar=False, consistency_checks='E')

		test_filename = 'tests/additional_files/temp_TestSimulationWithDisruptions_test_example_6_1_OP.csv'
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		write_results(network=network, num_periods=100, columns_to_print=cols_to_print, write_csv=True, csv_filename=test_filename)

		cmp_filename = 'tests/additional_files/test_sim_disruption_example_6_1_OP.csv'

		with open(test_filename) as test_csv:
			with open(cmp_filename) as cmp_csv:
				test_reader = csv.reader(test_csv)
				test_rows = list(test_reader)
				cmp_reader = csv.reader(cmp_csv)
				cmp_rows = list(cmp_reader)

				self.assertEqual(len(test_rows), len(cmp_rows))
				for r in range(len(test_rows)):
					for c in range(len(test_rows[r])):
						try:
							# Everything in the CSV is a string, so convert what we can to floats.
							test_val = float(test_rows[r][c])
						except ValueError:
							test_val = test_rows[r][c]
						try:
							cmp_val = float(cmp_rows[r][c])
							self.assertAlmostEqual(test_val, cmp_val)
						except ValueError:
							cmp_val = cmp_rows[r][c]
							self.assertEqual(test_val, cmp_val)

				os.remove(test_filename)

	def test_example_6_1_SP(self):
		"""Test that simulation() function correctly simulates model from
		Example 6.1 with type-SP disruptions.
		"""
		print_status('TestSimulationWithDisruptions', 'test_example_6_1_SP()')

		network = load_instance("example_6_1")

		network.get_node_from_index(2).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='SP',
			disruption_probability=0.1,
			recovery_probability=0.4
		)

		_ = simulation(network, 100, rand_seed=42, progress_bar=False, consistency_checks='E')

		test_filename = 'tests/additional_files/temp_TestSimulationWithDisruptions_test_example_6_1_SP.csv'
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		write_results(network=network, num_periods=100, columns_to_print=cols_to_print, write_csv=True, csv_filename=test_filename)

		cmp_filename = 'tests/additional_files/test_sim_disruption_example_6_1_SP.csv'

		with open(test_filename) as test_csv:
			with open(cmp_filename) as cmp_csv:
				test_reader = csv.reader(test_csv)
				test_rows = list(test_reader)
				cmp_reader = csv.reader(cmp_csv)
				cmp_rows = list(cmp_reader)

				self.assertEqual(len(test_rows), len(cmp_rows))
				for r in range(len(test_rows)):
					for c in range(len(test_rows[r])):
						try:
							# Everything in the CSV is a string, so convert what we can to floats.
							test_val = float(test_rows[r][c])
						except ValueError:
							test_val = test_rows[r][c]
						try:
							cmp_val = float(cmp_rows[r][c])
							self.assertAlmostEqual(test_val, cmp_val)
						except ValueError:
							cmp_val = cmp_rows[r][c]
							self.assertEqual(test_val, cmp_val)

				os.remove(test_filename)

	def test_example_6_1_TP(self):
		"""Test that simulation() function correctly simulates model from
		Example 6.1 with type-TP disruptions.
		"""
		print_status('TestSimulationWithDisruptions', 'test_example_6_1_TP()')

		network = load_instance("example_6_1")

		network.get_node_from_index(2).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='TP',
			disruption_probability=0.1,
			recovery_probability=0.4
		)

		_ = simulation(network, 100, rand_seed=42, progress_bar=False, consistency_checks='E')

		test_filename = 'tests/additional_files/temp_TestSimulationWithDisruptions_test_example_6_1_TP.csv'
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		write_results(network=network, num_periods=100, columns_to_print=cols_to_print, write_csv=True, csv_filename=test_filename)

		cmp_filename = 'tests/additional_files/test_sim_disruption_example_6_1_TP.csv'

		with open(test_filename) as test_csv:
			with open(cmp_filename) as cmp_csv:
				test_reader = csv.reader(test_csv)
				test_rows = list(test_reader)
				cmp_reader = csv.reader(cmp_csv)
				cmp_rows = list(cmp_reader)

				self.assertEqual(len(test_rows), len(cmp_rows))
				for r in range(len(test_rows)):
					for c in range(len(test_rows[r])):
						try:
							# Everything in the CSV is a string, so convert what we can to floats.
							test_val = float(test_rows[r][c])
						except ValueError:
							test_val = test_rows[r][c]
						try:
							cmp_val = float(cmp_rows[r][c])
							self.assertAlmostEqual(test_val, cmp_val)
						except ValueError:
							cmp_val = cmp_rows[r][c]
							self.assertEqual(test_val, cmp_val)

				os.remove(test_filename)

	def test_example_6_1_RP(self):
		"""Test that simulation() function correctly simulates model from
		Example 6.1 with type-RP disruptions.
		"""
		print_status('TestSimulationWithDisruptions', 'test_example_6_1_RP()')

		network = load_instance("example_6_1")

		network.get_node_from_index(2).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='RP',
			disruption_probability=0.1,
			recovery_probability=0.4
		)

		_ = simulation(network, 100, rand_seed=42, progress_bar=False, consistency_checks='E')

		test_filename = 'tests/additional_files/temp_TestSimulationWithDisruptions_test_example_6_1_RP.csv'
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
		write_results(network=network, num_periods=100, columns_to_print=cols_to_print, write_csv=True, csv_filename=test_filename)

		cmp_filename = 'tests/additional_files/test_sim_disruption_example_6_1_RP.csv'

		with open(test_filename) as test_csv:
			with open(cmp_filename) as cmp_csv:
				test_reader = csv.reader(test_csv)
				test_rows = list(test_reader)
				cmp_reader = csv.reader(cmp_csv)
				cmp_rows = list(cmp_reader)

				self.assertEqual(len(test_rows), len(cmp_rows))
				for r in range(len(test_rows)):
					for c in range(len(test_rows[r])):
						try:
							# Everything in the CSV is a string, so convert what we can to floats.
							test_val = float(test_rows[r][c])
						except ValueError:
							test_val = test_rows[r][c]
						try:
							cmp_val = float(cmp_rows[r][c])
							self.assertAlmostEqual(test_val, cmp_val)
						except ValueError:
							cmp_val = cmp_rows[r][c]
							self.assertEqual(test_val, cmp_val)

				os.remove(test_filename)


class TestSerialEchelonVsLocal(unittest.TestCase):
	"""Test that simulation results agree for a serial system when run using
	echelon vs. local base-stock policies.
	"""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSerialEchelonVsLocal', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSerialEchelonVsLocal', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that echelon policy results agree with local policy results
		for model from Example 6.1.
		"""
		print_status('TestSerialEchelonVsLocal', 'test_example_6_1()')

		network_local = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_local.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Simulate with local BS policy.
		total_cost_local = simulation(network_local, 100, rand_seed=41, progress_bar=False, consistency_checks='E')

		# Create the network for echelon policy test.
		network_ech = load_instance("example_6_1")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_ech.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Calculate echelon base-stock levels.
		S_local = {n.index: n.inventory_policy.base_stock_level for n in network_ech.nodes}
		S_echelon = local_to_echelon_base_stock_levels(network_ech, S_local)

		# Create and fill echelon base-stock policies.
		for n in network_ech.nodes:
			n.inventory_policy.type = 'EBS'
			n.inventory_policy.base_stock_level = S_echelon[n.index]

		# Simulate with echelon BS policy.
		total_cost_ech = simulation(network_ech, 100, rand_seed=41, progress_bar=False, consistency_checks='E')

		# Compare total costs.
		self.assertAlmostEqual(total_cost_local, total_cost_ech, places=4)

		# Compare a few performance measures.
		for i in range(len(network_ech.nodes)):
			np.testing.assert_allclose([network_local.nodes[i].state_vars[99].order_quantity[p_ind] for p_ind in
										network_local.nodes[i].predecessor_indices(include_external=True)],
									   [network_ech.nodes[i].state_vars[99].order_quantity[p_ind] for p_ind in
									    network_local.nodes[i].predecessor_indices(include_external=True)])
			np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inventory_level,
									   network_ech.nodes[i].state_vars[99].inventory_level)
			for s in network_ech.nodes[i].successor_indices():
				np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inbound_order[s],
										   network_ech.nodes[i].state_vars[99].inbound_order[s])
			for p in network_ech.nodes[i].predecessor_indices():
				np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inbound_shipment[p],
										   network_ech.nodes[i].state_vars[99].inbound_shipment[p])
			np.testing.assert_allclose(network_local.nodes[i].state_vars[99].backorders,
									   network_ech.nodes[i].state_vars[99].backorders)

	def test_problem_6_2a(self):
		"""Test that echelon policy results agree with local policy results
		for model from Problem 6.2a.
		"""
		print_status('TestSerialEchelonVsLocal', 'test_problem_6_2a()')

		# Create the network for local policy test.
		network_local = load_instance("problem_6_2a_adj")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_local.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Simulate with local BS policy.
		total_cost_local = simulation(network_local, 100, rand_seed=41, progress_bar=False, consistency_checks='E')

		# Create the network for echelon policy test.
		network_ech = load_instance("problem_6_2a_adj")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_ech.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Calculate echelon base-stock levels.
		S_local = {n.index: n.inventory_policy.base_stock_level for n in network_ech.nodes}
		S_echelon = local_to_echelon_base_stock_levels(network_ech, S_local)

		# Create and fill echelon base-stock policies.
		for n in network_ech.nodes:
			n.inventory_policy.type = 'EBS'
			n.inventory_policy.base_stock_level = S_echelon[n.index]

		# Simulate with echelon BS policy.
		total_cost_ech = simulation(network_ech, 100, rand_seed=41, progress_bar=False, consistency_checks='E')

		# Compare total costs.
		self.assertAlmostEqual(total_cost_local, total_cost_ech, places=4)

		# Compare a few performance measures.
		for i in range(len(network_ech.nodes)):
			np.testing.assert_allclose([network_local.nodes[i].state_vars[99].order_quantity[p_ind] for p_ind in
										network_local.nodes[i].predecessor_indices(include_external=True)],
									   [network_ech.nodes[i].state_vars[99].order_quantity[p_ind] for p_ind in
									    network_local.nodes[i].predecessor_indices(include_external=True)])
			np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inventory_level,
									   network_ech.nodes[i].state_vars[99].inventory_level)
			for s in network_ech.nodes[i].successor_indices():
				np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inbound_order[s],
										   network_ech.nodes[i].state_vars[99].inbound_order[s])
			for p in network_ech.nodes[i].predecessor_indices():
				np.testing.assert_allclose(network_local.nodes[i].state_vars[99].inbound_shipment[p],
										   network_ech.nodes[i].state_vars[99].inbound_shipment[p])
			np.testing.assert_allclose(network_local.nodes[i].state_vars[99].backorders,
									   network_ech.nodes[i].state_vars[99].backorders)


class TestBadBackorders(unittest.TestCase):
	"""This tests instances that have in the past caused failures of the backorder check during the simulation."""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSimulation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSimulation', 'tear_down_class()')

	def test_rong_atan_snyder_figure_1a_with_disruptions(self):
		"""Test that simulation() function correctly simulates model from
		Rong, Atan, and Snyder Figure 1, with disruptions.
		"""
		print_status('TestBadBackorders', 'test_rong_atan_snyder_figure_1a_with_disruptions()')

		T = 100

		# Build network.
		network = load_instance("rong_atan_snyder_figure_1a")
		# Add disruptions.
		network.get_node_from_index(1).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)
		network.get_node_from_index(3).disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='SP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)

		# Simulate.
		simulation(network, T, rand_seed=17, progress_bar=False, consistency_checks='E')

		# (Nothing to check, other than that a ValueError error wasn't raised during the simulation.)


class TestConsistencyChecks(unittest.TestCase):
	"""This tests a bunch of instances with randomly generated disruption processes to make sure their
	consistency checks are OK."""
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSimulation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSimulation', 'tear_down_class()')

	def try_multiple_disruption_processes(self, instance_name):
		"""Run multiple trials of simulation on instance, generating different random disruption
		processes each time, and checking that consistency checks are OK.
		"""
		T = 100
		num_trials = 10
		random.seed(42)

		for _ in range(num_trials):
			# Build network.
			network = load_instance(instance_name)
			# Add disruptions.
			num_disrupted_nodes = random.randint(1, len(network.nodes))
			disrupted_nodes = random.sample(network.nodes, num_disrupted_nodes)
			for n in disrupted_nodes:
				n.disruption_process = DisruptionProcess(
					random_process_type='M',
					disruption_type=random.choice(['OP', 'SP', 'RP', 'TP']),
					disruption_probability=random.random() * 0.5,
					recovery_probability=random.random()
				)

			# Simulate.
			simulation(network, T, rand_seed=17, progress_bar=False, consistency_checks='E')
			# (Nothing to check, except to make sure no ValueErrors were raised.)
			
	def test_example_6_1_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Example 6.1, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_example_6_1_with_disruptions()')

		self.try_multiple_disruption_processes("example_6_1")

	def test_problem_6_1_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Problem 6.1, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_problem_6_1_with_disruptions()')

		self.try_multiple_disruption_processes("problem_6_1")

	def test_problem_6_2a_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Problem 6.2a, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_problem_6_2a_with_disruptions()')

		self.try_multiple_disruption_processes("problem_6_2a_adj")

	def test_problem_6_16_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Problem 6.16, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_problem_6_16_with_disruptions()')

		self.try_multiple_disruption_processes("problem_6_16")

	def test_example_4_1_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Example 4.1, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_example_4_1_with_disruptions()')

		self.try_multiple_disruption_processes("example_4_1_network")

	def test_assembly_3_stage_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of 3-stage assembly system, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_assembly_3_stage_with_disruptions()')

		self.try_multiple_disruption_processes("assembly_3_stage")

	def test_rosling_figure_1_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of model in Rosling (1989), Figure 1, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_rosling_figure_1_with_disruptions()')

		self.try_multiple_disruption_processes("rosling_figure_1")

	def test_rong_atan_snyder_figure_1a_with_disruptions(self):
		"""Test that consistency checks are OK for simulation of Figure 1 in Rong, Atan, and Snyder, with disruptions.
		"""
		print_status('TestConsistencyChecks', 'test_rong_atan_snyder_figure_1a_with_disruptions()')

		self.try_multiple_disruption_processes("rong_atan_snyder_figure_1a")


class TestCalculatePeriodCosts(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCalculatePeriodCosts', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCalculatePeriodCosts', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of model from
		Example 6.1.
		"""
		print_status('TestCalculatePeriodCosts', 'test_example_6_1()')

		network = load_instance("example_6_1")

		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_problem_6_1(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of model from
		Problem 6.1.
		"""
		print_status('TestCalculatePeriodCosts', 'test_problem_6_1()')

		network = load_instance("problem_6_1")
		
		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_problem_6_2a(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of model from
		Problem 6.2(a).
		"""
		print_status('TestCalculatePeriodCosts', 'test_problem_6_2a()')

		network = load_instance("problem_6_2a_adj")
		
		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_problem_6_16(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of model from
		Problem 6.16.
		"""
		print_status('TestCalculatePeriodCosts', 'test_problem_6_16()')

		network = load_instance("problem_6_16")

		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_single_stage(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of single-stage
		model with base-stock policy.
		"""
		print_status('TestCalculatePeriodCosts', 'test_single_stage()')

		network = load_instance("example_4_1_network")

		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_assembly_3_stage(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of 3-stage assembly model.
		"""
		print_status('TestCalculatePeriodCosts', 'test_assembly_3_stage()')

		network = load_instance("assembly_3_stage")
		
		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)

	def test_rosling_figure_1(self):
		"""Test that _calculate_period_costs() correct calculates cost for simulation of model in Rosling (1989),
		Figure 1.
		"""
		print_status('TestCalculatePeriodCosts', 'test_rosling_figure_1()')

		network = load_instance("rosling_figure_1")
		
		_ = simulation(network, 100, rand_seed=17, progress_bar=False, consistency_checks='E')

		# Check costs in a few periods.
		for t in [0, 2, 17, 52, 80]:
			for n in network.nodes:
				self.assertEqual(
					n.state_vars[t].holding_cost_incurred + n.state_vars[t].stockout_cost_incurred \
						+ n.state_vars[t].in_transit_holding_cost_incurred - n.state_vars[t].revenue_earned,
					n.state_vars[t].total_cost_incurred
				)