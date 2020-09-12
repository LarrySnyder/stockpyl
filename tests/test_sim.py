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
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 4.8883, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -1.08737, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 4.30582, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[2][95], 6.97664, places=4)
		self.assertAlmostEqual(network.nodes[2].backorders_by_successor[1][31], 0.148957, places=4)
		self.assertAlmostEqual(network.nodes[2].inventory_level[90], 0.0443519, places=4)

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
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 140.6747130757738, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -21.4276, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 98.6768, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[None][95], 105.7364470997879, places=4)
		self.assertAlmostEqual(network.nodes[0].backorders_by_successor[None][31], 18.9103, places=4)
		self.assertAlmostEqual(network.nodes[1].inventory_level[90], -28.4205, places=4)

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
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 34.7807, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], 5.60159, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 36.0213, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[2][96], 34.9884, places=4)
		self.assertAlmostEqual(network.nodes[2].backorders_by_successor[1][32], 2.67911, places=4)
		self.assertAlmostEqual(network.nodes[2].inventory_level[90], -1.76791, places=4)
		self.assertAlmostEqual(network.nodes[3].outbound_shipment[2][67], 30.0597, places=4)
		self.assertAlmostEqual(network.nodes[3].fill_rate[84], 0.843055, places=4)
		self.assertAlmostEqual(network.nodes[4].on_order_by_predecessor[None][58], 30.9224, places=4)
		self.assertAlmostEqual(network.nodes[4].holding_cost_incurred[81], 2.58384, places=4)

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
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 23.5517, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -4.72853, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 11.0029, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[None][95], 19.9307, places=4)
		self.assertAlmostEqual(network.nodes[0].backorders_by_successor[None][31], 26.9162, places=4)
		self.assertAlmostEqual(network.nodes[1].inventory_level[90], -12.6397, places=4)

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
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 57.103320, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], 9.9564105, places=4)
		self.assertAlmostEqual(network.nodes[0].inbound_order[None][43], 32.00584965, places=4)
		self.assertAlmostEqual(network.nodes[0].inbound_shipment[None][95], 52.9079333, places=4)
		self.assertAlmostEqual(network.nodes[0].backorders_by_successor[None][19], 6.7125153, places=4)
		self.assertAlmostEqual(network.nodes[0].inventory_level[87], -2.09415258242449, places=4)


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
			np.testing.assert_allclose(network_local.nodes[i].order_quantity,
									   network_ech.nodes[i].order_quantity)
			np.testing.assert_allclose(network_local.nodes[i].ending_inventory_level,
									   network_ech.nodes[i].ending_inventory_level)
			for s in network_ech.nodes[i].successor_indices:
				np.testing.assert_allclose(network_local.nodes[i].inbound_order[s],
										   network_ech.nodes[i].inbound_order[s])
			for p in network_ech.nodes[i].predecessor_indices:
				np.testing.assert_allclose(network_local.nodes[i].inbound_shipment[p],
										   network_ech.nodes[i].inbound_shipment[p])
			np.testing.assert_allclose(network_local.nodes[i].backorders,
									   network_ech.nodes[i].backorders)


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
			np.testing.assert_allclose(network_local.nodes[i].order_quantity,
									   network_ech.nodes[i].order_quantity)
			np.testing.assert_allclose(network_local.nodes[i].ending_inventory_level,
									   network_ech.nodes[i].ending_inventory_level)
			for s in network_ech.nodes[i].successor_indices:
				np.testing.assert_allclose(network_local.nodes[i].inbound_order[s],
										   network_ech.nodes[i].inbound_order[s])
			for p in network_ech.nodes[i].predecessor_indices:
				np.testing.assert_allclose(network_local.nodes[i].inbound_shipment[p],
										   network_ech.nodes[i].inbound_shipment[p])
			np.testing.assert_allclose(network_local.nodes[i].backorders,
									   network_ech.nodes[i].backorders)
