import unittest

import numpy as np

from pyinv import supply_uncertainty
from pyinv.instances import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_supply_uncertainty   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestEconomicOrderQuantityWithDisruptions(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'tear_down_class()')

	def test_example_9_1_exact(self):
		"""Test that economic_order_quantity_with_disruptions() function correctly
		optimizes exact cost function for Example 9.1.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'test_example_9_1_exact()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("example_9_1")

		order_quantity, cost = supply_uncertainty.economic_order_quantity_with_disruptions(fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(order_quantity, 7.728110631910017e+02, places=4)
		self.assertAlmostEqual(cost, 1.739500025731971e+02, places=4)

		# Double-check cost.
		cost_check = supply_uncertainty.economic_order_quantity_with_disruptions_cost(order_quantity, fixed_cost,
											holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, cost_check)

	def test_problem_9_8_exact(self):
		"""Test that economic_order_quantity_with_disruptions() function correctly
		optimizes exact cost function for Problem 9.8.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'test_problem_9_8_exact()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("problem_9_8")

		order_quantity, cost = supply_uncertainty.economic_order_quantity_with_disruptions(fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(order_quantity, 24.066284024222202, places=4)
		self.assertAlmostEqual(cost, 96.266590901158000, places=4)

		# Double-check cost.
		cost_check = supply_uncertainty.economic_order_quantity_with_disruptions_cost(order_quantity, fixed_cost,
											holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, cost_check)

	def test_example_9_1_approx(self):
		"""Test that economic_order_quantity_with_disruptions() function correctly
		optimizes approximate cost function for Example 9.1.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'test_example_9_1_approx()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("example_9_1")

		order_quantity, cost = supply_uncertainty.economic_order_quantity_with_disruptions(fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(order_quantity, 7.731432417118889e+02)
		self.assertAlmostEqual(cost, 1.739572293851750e+02)

		# Double-check cost.
		cost_check = supply_uncertainty.economic_order_quantity_with_disruptions_cost(order_quantity, fixed_cost,
											holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate,
											approximate=True)
		self.assertAlmostEqual(cost, cost_check)

	def test_problem_9_8_approx(self):
		"""Test that economic_order_quantity_with_disruptions_cost() function correctly
		evaluates approximate cost for Problem 9.8.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptions', 'test_problem_9_8_approx()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("problem_9_8")

		order_quantity, cost = supply_uncertainty.economic_order_quantity_with_disruptions(fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(order_quantity, 24.066680759605532)
		self.assertAlmostEqual(cost, 96.266723038422130)

		# Double-check cost.
		cost_check = supply_uncertainty.economic_order_quantity_with_disruptions_cost(order_quantity, fixed_cost,
											holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate,
											approximate=True)
		self.assertAlmostEqual(cost, cost_check)


class TestEconomicOrderQuantityWithDisruptionsCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'tear_down_class()')

	def test_example_9_1_exact(self):
		"""Test that economic_order_quantity_with_disruptions_cost() function correctly
		evaluates exact cost for Example 9.1.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'test_example_9_1_exact()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("example_9_1")

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(800, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.740524722120417e02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(400, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 2.110841892589692e+02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(1100, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.847949312205155e+02)

	def test_problem_9_8_exact(self):
		"""Test that economic_order_quantity_with_disruptions_cost() function correctly
		evaluates exact cost for Problem 9.8.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'test_problem_9_8_exact()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("problem_9_8")

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(20, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 97.903839894383600)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(15, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.070780850066119e+02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(30, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 98.598718032153970)

	def test_example_9_1_approx(self):
		"""Test that economic_order_quantity_with_disruptions_cost() function correctly
		evaluates approximate cost for Example 9.1.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'test_example_9_1_approx()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("example_9_1")

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(800, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.740575334662489e+02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(400, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 2.122569014084507e+02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(1100, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.847950342821525e+02)

	def test_problem_9_8_approx(self):
		"""Test that economic_order_quantity_with_disruptions_cost() function correctly
		evaluates approximate cost for Problem 9.8.
		"""
		print_status('TestEconomicOrderQuantityWithDisruptionsCost', 'test_problem_9_8_approx()')

		holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate = \
			get_named_instance("problem_9_8")

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(20, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 97.904761904761900)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(15, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.070886075949367e+02)

		cost = supply_uncertainty.economic_order_quantity_with_disruptions_cost(30, fixed_cost,
											holding_cost, stockout_cost, demand_rate,
											disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 98.598726114649680)

