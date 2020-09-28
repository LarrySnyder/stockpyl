import unittest

from pyinv.instances import *
from pyinv.sim import *
from pyinv.ssm_serial import local_to_echelon_base_stock_levels
from pyinv.policy import *


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


# TODO: add tests for non-normal demands

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

		network = get_named_instance("example_6_1")

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 6620.352025, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[1], 4.8883, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, -1.08737, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[43].inbound_order[0], 4.30582, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[95].inbound_shipment[2], 6.97664, places=4)
		self.assertAlmostEqual(network.nodes[2].state_vars[31].backorders_by_successor[1], 0.148957, places=4)
		self.assertAlmostEqual(network.nodes[2].state_vars[89].inventory_level, 0.0443519, places=4)

	def test_problem_6_1(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.1.
		"""
		print_status('TestSimulation', 'test_problem_6_1()')

		network = get_named_instance("problem_6_1")

		total_cost = simulation(network, 100, rand_seed=531, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 35794.476254, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[1], 140.6747130757738, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, -21.4276, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[43].inbound_order[0], 98.6768, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[95].inbound_shipment[None], 105.7364470997879, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[31].backorders_by_successor[None], 18.9103, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[89].inventory_level, -28.4205, places=4)

	def test_problem_6_2a(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.2(a).
		"""
		print_status('TestSimulation', 'test_problem_6_2a()')

		network = get_named_instance("problem_6_2a_adj")

		total_cost = simulation(network, 100, rand_seed=1340, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 38381.048422, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[1], 34.7807, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, 5.60159, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[43].inbound_order[0], 36.0213, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[96].inbound_shipment[2], 34.9884, places=4)
		self.assertAlmostEqual(network.nodes[2].state_vars[32].backorders_by_successor[1], 2.67911, places=4)
		self.assertAlmostEqual(network.nodes[2].state_vars[89].inventory_level, -1.76791, places=4)
		self.assertAlmostEqual(network.nodes[3].state_vars[67].outbound_shipment[2], 30.0597, places=4)
		self.assertAlmostEqual(network.nodes[3].state_vars[84].fill_rate, 0.843055, places=4)
		self.assertAlmostEqual(network.nodes[4].state_vars[58].on_order_by_predecessor[None], 26.8160166, places=4)
		self.assertAlmostEqual(network.nodes[4].state_vars[81].holding_cost_incurred, 2.58384, places=4)

	def test_problem_6_16(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.16.
		"""
		print_status('TestSimulation', 'test_problem_6_16()')

		network = get_named_instance("problem_6_16")

		total_cost = simulation(network, 100, rand_seed=762, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 52386.309175, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[1], 23.5517, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, -4.72853, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[43].inbound_order[0], 11.0029, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[95].inbound_shipment[None], 19.9307, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[31].backorders_by_successor[None], 26.9162, places=4)
		self.assertAlmostEqual(network.nodes[1].state_vars[89].inventory_level, -12.6397, places=4)

	def test_single_stage(self):
		"""Test that simulation() function correctly simulates single-stage
		model with base-stock policy.
		"""
		print_status('TestSimulation', 'test_single_stage()')

		network = get_named_instance("example_4_1_network")

		total_cost = simulation(network, num_periods=100, rand_seed=762, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 255.2472033, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].state_vars[6].order_quantity[None], 57.103320, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inventory_level, 9.9564105, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[43].inbound_order[None], 32.00584965, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[95].inbound_shipment[None], 52.9079333, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[19].backorders_by_successor[None], 6.7125153, places=4)
		self.assertAlmostEqual(network.nodes[0].state_vars[86].inventory_level, -2.09415258242449, places=4)


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

		network_local = get_named_instance("example_6_1")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_local.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Simulate with local BS policy.
		total_cost_local = simulation(network_local, 100, rand_seed=41, progress_bar=False)

		# Create the network for echelon policy test.
		network_ech = get_named_instance("example_6_1")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_ech.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Calculate echelon base-stock levels.
		S_local = {n.index: n.inventory_policy.base_stock_level for n in network_ech.nodes}
		S_echelon = local_to_echelon_base_stock_levels(network_ech, S_local)

		# Create and fill echelon base-stock policies.
		policy_factory = PolicyFactory()
		for n in network_ech.nodes:
			n.inventory_policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
												 base_stock_level=S_echelon[n.index])

		# Simulate with echelon BS policy.
		total_cost_ech = simulation(network_ech, 100, rand_seed=41, progress_bar=False)

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
		network_local = get_named_instance("problem_6_2a_adj")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_local.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Simulate with local BS policy.
		total_cost_local = simulation(network_local, 100, rand_seed=41, progress_bar=False)

		# Create the network for echelon policy test.
		network_ech = get_named_instance("problem_6_2a_adj")

		# Set initial inventory levels to local BS levels (otherwise local and echelon policies
		# will differ in the first few periods).
		for n in network_ech.nodes:
			n.initial_inventory_level = n.inventory_policy.base_stock_level

		# Calculate echelon base-stock levels.
		S_local = {n.index: n.inventory_policy.base_stock_level for n in network_ech.nodes}
		S_echelon = local_to_echelon_base_stock_levels(network_ech, S_local)

		# Create and fill echelon base-stock policies.
		policy_factory = PolicyFactory()
		for n in network_ech.nodes:
			n.inventory_policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
												 base_stock_level=S_echelon[n.index])

		# Simulate with echelon BS policy.
		total_cost_ech = simulation(network_ech, 100, rand_seed=41, progress_bar=False)

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
