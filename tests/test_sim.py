import unittest

from inventory.instances import *
from inventory.sim import *


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

		network = example_6_1_network

		total_cost = simulation(network, 100, rand_seed=17, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 6620.352025, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 4.8883, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -1.08737, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 4.30582, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[2][95], 6.97664, places=4)
		self.assertAlmostEqual(network.nodes[2].backorders[1][31], 0.148957, places=4)
		self.assertAlmostEqual(network.nodes[2].inventory_level[90], 0.0443519, places=4)

	def test_problem_6_1(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.1.
		"""
		print_status('TestSimulation', 'test_problem_6_1()')

		network = problem_6_1_network

		total_cost = simulation(network, 100, rand_seed=531, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 35794.476254, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 140.6747130757738, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -21.4276, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 98.6768, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[None][95], 105.7364470997879, places=4)
		self.assertAlmostEqual(network.nodes[0].backorders[None][31], 18.9103, places=4)
		self.assertAlmostEqual(network.nodes[1].inventory_level[90], -28.4205, places=4)

	def test_problem_6_2a(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.2(a).
		"""
		print_status('TestSimulation', 'test_problem_6_2a()')

		network = problem_6_2a_network

		total_cost = simulation(network, 100, rand_seed=1340, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 38381.048422, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 34.7807, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], 5.60159, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 36.0213, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[2][96], 34.9884, places=4)
		self.assertAlmostEqual(network.nodes[2].backorders[1][32], 2.67911, places=4)
		self.assertAlmostEqual(network.nodes[2].inventory_level[90], -1.76791, places=4)
		self.assertAlmostEqual(network.nodes[3].outbound_shipment[2][67], 30.0597, places=4)
		self.assertAlmostEqual(network.nodes[3].fill_rate[84], 0.843055, places=4)
		self.assertAlmostEqual(network.nodes[4].on_order[None][58], 30.9224, places=4)
		self.assertAlmostEqual(network.nodes[4].holding_cost_incurred[81], 2.58384, places=4)

	def test_problem_6_16(self):
		"""Test that simulation() function correctly simulates model from
		Problem 6.16.
		"""
		print_status('TestSimulation', 'test_problem_6_16()')

		network = problem_6_16_network

		total_cost = simulation(network, 100, rand_seed=762, progress_bar=False)

		# Compare total cost.
		self.assertAlmostEqual(total_cost, 52386.309175, places=4)

		# Compare a few performance measures.
		self.assertAlmostEqual(network.nodes[0].order_quantity[6], 23.5517, places=4)
		self.assertAlmostEqual(network.nodes[0].ending_inventory_level[95], -4.72853, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_order[0][43], 11.0029, places=4)
		self.assertAlmostEqual(network.nodes[1].inbound_shipment[None][95], 19.9307, places=4)
		self.assertAlmostEqual(network.nodes[0].backorders[None][31], 26.9162, places=4)
		self.assertAlmostEqual(network.nodes[1].inventory_level[90], -12.6397, places=4)

