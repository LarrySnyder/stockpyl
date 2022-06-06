import unittest

import numpy as np

from stockpyl.supply_uncertainty import *
from stockpyl.instances import *


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


class TestEOQWithDisruptions(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEOQWithDisruptions', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEOQWithDisruptions', 'tear_down_class()')

	def test_example_9_1_exact(self):
		"""Test that eoq_with_disruptions() function correctly
		optimizes exact cost function for Example 9.1.
		"""
		print_status('TestEOQWithDisruptions', 'test_example_9_1_exact()')

		instance = load_instance("example_9_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		order_quantity, cost = eoq_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
																	   disruption_rate, recovery_rate)
		self.assertAlmostEqual(order_quantity, 7.728110631910017e+02, places=4)
		self.assertAlmostEqual(cost, 1.739500025731971e+02, places=4)

		# Double-check cost.
		cost_check = eoq_with_disruptions_cost(order_quantity, fixed_cost,
																  holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, cost_check)

	def test_problem_9_8_exact(self):
		"""Test that eoq_with_disruptions() function correctly
		optimizes exact cost function for Problem 9.8.
		"""
		print_status('TestEOQWithDisruptions', 'test_problem_9_8_exact()')

		instance = load_instance("problem_9_8")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		order_quantity, cost = eoq_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
																	   disruption_rate, recovery_rate)
		self.assertAlmostEqual(order_quantity, 24.066284024222202, places=4)
		self.assertAlmostEqual(cost, 96.266590901158000, places=4)

		# Double-check cost.
		cost_check = eoq_with_disruptions_cost(order_quantity, fixed_cost,
																  holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, cost_check)

	def test_example_9_1_approx(self):
		"""Test that eoq_with_disruptions() function correctly
		optimizes approximate cost function for Example 9.1.
		"""
		print_status('TestEOQWithDisruptions', 'test_example_9_1_approx()')

		instance = load_instance("example_9_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		order_quantity, cost = eoq_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
																	   disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(order_quantity, 7.731432417118889e+02)
		self.assertAlmostEqual(cost, 1.739572293851750e+02)

		# Double-check cost.
		cost_check = eoq_with_disruptions_cost(order_quantity, fixed_cost,
																  holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate,
																  approximate=True)
		self.assertAlmostEqual(cost, cost_check)

	def test_problem_9_8_approx(self):
		"""Test that eoq_with_disruptions_cost() function correctly
		evaluates approximate cost for Problem 9.8.
		"""
		print_status('TestEOQWithDisruptions', 'test_problem_9_8_approx()')

		instance = load_instance("problem_9_8")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		order_quantity, cost = eoq_with_disruptions(fixed_cost, holding_cost, stockout_cost, demand_rate,
																	   disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(order_quantity, 24.066680759605532)
		self.assertAlmostEqual(cost, 96.266723038422130)

		# Double-check cost.
		cost_check = eoq_with_disruptions_cost(order_quantity, fixed_cost,
																  holding_cost, stockout_cost, demand_rate, disruption_rate, recovery_rate,
																  approximate=True)
		self.assertAlmostEqual(cost, cost_check)


class TestEOQWithDisruptionsCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEOQWithDisruptionsCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEOQWithDisruptionsCost', 'tear_down_class()')

	def test_example_9_1_exact(self):
		"""Test that eoq_with_disruptions_cost() function correctly
		evaluates exact cost for Example 9.1.
		"""
		print_status('TestEOQWithDisruptionsCost', 'test_example_9_1_exact()')

		instance = load_instance("example_9_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		cost = eoq_with_disruptions_cost(800, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.740524722120417e02)

		cost = eoq_with_disruptions_cost(400, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 2.110841892589692e+02)

		cost = eoq_with_disruptions_cost(1100, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.847949312205155e+02)

	def test_problem_9_8_exact(self):
		"""Test that eoq_with_disruptions_cost() function correctly
		evaluates exact cost for Problem 9.8.
		"""
		print_status('TestEOQWithDisruptionsCost', 'test_problem_9_8_exact()')

		instance = load_instance("problem_9_8")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		cost = eoq_with_disruptions_cost(20, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 97.903839894383600)

		cost = eoq_with_disruptions_cost(15, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 1.070780850066119e+02)

		cost = eoq_with_disruptions_cost(30, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate)
		self.assertAlmostEqual(cost, 98.598718032153970)

	def test_example_9_1_approx(self):
		"""Test that eoq_with_disruptions_cost() function correctly
		evaluates approximate cost for Example 9.1.
		"""
		print_status('TestEOQWithDisruptionsCost', 'test_example_9_1_approx()')

		instance = load_instance("example_9_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		cost = eoq_with_disruptions_cost(800, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.740575334662489e+02)

		cost = eoq_with_disruptions_cost(400, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 2.122569014084507e+02)

		cost = eoq_with_disruptions_cost(1100, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.847950342821525e+02)

	def test_problem_9_8_approx(self):
		"""Test that eoq_with_disruptions_cost() function correctly
		evaluates approximate cost for Problem 9.8.
		"""
		print_status('TestEOQWithDisruptionsCost', 'test_problem_9_8_approx()')

		instance = load_instance("problem_9_8")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_rate = instance['demand_rate']
		disruption_rate = instance['disruption_rate']
		recovery_rate = instance['recovery_rate']

		cost = eoq_with_disruptions_cost(20, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 97.904761904761900)

		cost = eoq_with_disruptions_cost(15, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 1.070886075949367e+02)

		cost = eoq_with_disruptions_cost(30, fixed_cost, holding_cost, stockout_cost, demand_rate,
															disruption_rate, recovery_rate, approximate=True)
		self.assertAlmostEqual(cost, 98.598726114649680)


class TestNewsvendorWithDisruptions(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorWithDisruptions', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorWithDisruptions', 'tear_down_class()')

	def test_example_9_3(self):
		"""Test that newsvendor_with_disruptions() function correctly solves Example 9.3.
		"""
		print_status('TestNewsvendorWithDisruptions', 'test_example_9_3()')

		instance = load_instance("example_9_3")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand = instance['demand']
		disruption_prob = instance['disruption_prob']
		recovery_prob = instance['recovery_prob']

		base_stock_level, cost = newsvendor_with_disruptions(holding_cost, stockout_cost,
																				demand, disruption_prob, recovery_prob)
		self.assertEqual(base_stock_level, 8000)
		self.assertAlmostEqual(cost, 2.737068965490435e+03, places=4)

		base_stock_level, cost = newsvendor_with_disruptions(holding_cost, stockout_cost,
																				demand, disruption_prob, recovery_prob,
																				base_stock_level=2000)
		self.assertEqual(base_stock_level, 2000)
		self.assertAlmostEqual(cost, 3.310344827558603e+03, places=4)

		base_stock_level, cost = newsvendor_with_disruptions(holding_cost, stockout_cost,
																				demand, disruption_prob, recovery_prob,
																				base_stock_level=12000)
		self.assertEqual(base_stock_level, 12000)
		self.assertAlmostEqual(cost, 3.075161637904759e+03, places=4)


class TestEOQWithAdditiveYieldUncertainty(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEOQWithAdditiveYieldUncertainty', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEOQWithAdditiveYieldUncertainty', 'tear_down_class()')

	def test_example_9_4(self):
		"""Test that eoq_with_additive_yield_uncertainty() function correctly solves Example 9.4.
		"""
		print_status('TestNewsvendorWithDisruptions', 'test_example_9_4()')

		instance = load_instance("example_9_4")
		fixed_cost = instance['fixed_cost']
		holding_cost = instance['holding_cost']
		demand_rate = instance['demand_rate']
		yield_mean = instance['yield_mean']
		yield_sd = instance['yield_sd']

		order_quantity, cost = eoq_with_additive_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd)
		self.assertAlmostEqual(order_quantity, 2.302463704688188e+05)
		self.assertAlmostEqual(cost, 1.291478222812913e+04)

		order_quantity, cost = eoq_with_additive_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd,
																					  order_quantity=200000)
		self.assertEqual(order_quantity, 200000)
		self.assertAlmostEqual(cost, 1.306313513513514e+04)

		order_quantity, cost = eoq_with_additive_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd,
																					  order_quantity=350000)
		self.assertEqual(order_quantity, 350000)
		self.assertAlmostEqual(cost, 1.419904477611940e+04)

	def test_problem_9_4a(self):
		"""Test that eoq_with_additive_yield_uncertainty() function correctly solves Problem 9.4a.
		"""
		print_status('TestNewsvendorWithDisruptions', 'test_problem_9_4a()')

		instance = load_instance("problem_9_4a")
		fixed_cost = instance['fixed_cost']
		holding_cost = instance['holding_cost']
		demand_rate = instance['demand_rate']
		yield_mean = instance['yield_mean']
		yield_sd = instance['yield_sd']

		order_quantity, cost = eoq_with_additive_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd)
		self.assertAlmostEqual(order_quantity, 1.778109845109285e+03)
		self.assertAlmostEqual(cost, 4.752302074050533e+05)


class TestEOQWithMultiplicativeYieldUncertainty(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEOQWithMultiplicativeYieldUncertainty', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEOQWithMultiplicativeYieldUncertainty', 'tear_down_class()')

	def test_example_9_5(self):
		"""Test that eoq_with_multiplicative_yield_uncertainty() function correctly solves Example 9.5.
		"""
		print_status('TestEOQWithMultiplicativeYieldUncertainty', 'test_example_9_5()')

		instance = load_instance("example_9_5")
		fixed_cost = instance['fixed_cost']
		holding_cost = instance['holding_cost']
		demand_rate = instance['demand_rate']
		yield_mean = instance['yield_mean']
		yield_sd = instance['yield_sd']

		order_quantity, cost = eoq_with_multiplicative_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd)
		self.assertAlmostEqual(order_quantity, 2.544602129999894e+05)
		self.assertAlmostEqual(cost, 1.308652523999946e+04)

		order_quantity, cost = eoq_with_multiplicative_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd,
																					  order_quantity=200000)
		self.assertEqual(order_quantity, 200000)
		self.assertAlmostEqual(cost, 1.346785714285714e+04)

		order_quantity, cost = eoq_with_multiplicative_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd,
																					  order_quantity=350000)
		self.assertEqual(order_quantity, 350000)
		self.assertAlmostEqual(cost, 1.375714285714286e+04)

	def test_problem_9_4b(self):
		"""Test that eoq_with_multiplicative_yield_uncertainty() function correctly solves Problem 9.4b.
		"""
		print_status('TestEOQWithMultiplicativeYieldUncertainty', 'test_problem_9_4b()')

		instance = load_instance("problem_9_4b")
		fixed_cost = instance['fixed_cost']
		holding_cost = instance['holding_cost']
		demand_rate = instance['demand_rate']
		yield_mean = instance['yield_mean']
		yield_sd = instance['yield_sd']

		order_quantity, cost = eoq_with_multiplicative_yield_uncertainty(fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd)
		self.assertAlmostEqual(order_quantity, 1.916183333947864e+03)
		self.assertAlmostEqual(cost, 4.762070433625989e+05)


class TestNewsvendorWithAdditiveYieldUncertainty(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorWithAdditiveYieldUncertainty', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorWithAdditiveYieldUncertainty', 'tear_down_class()')

	def test_example_9_6(self):
		"""Test that newsvendor_with_additive_yield_uncertainty() function correctly solves Example 9.6.
		"""
		print_status('TestNewsvendorWithAdditiveYieldUncertainty', 'test_example_9_6()')

		instance = load_instance("example_9_6")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand = instance['demand']
		yield_lo = instance['yield_lo']
		yield_hi = instance['yield_hi']

		yield_distribution = uniform(yield_lo, yield_hi-yield_lo)

		# Don't provide loss_function.
		base_stock_level, cost = newsvendor_with_additive_yield_uncertainty(holding_cost, stockout_cost,
									demand, yield_distribution=yield_distribution)
		self.assertAlmostEqual(base_stock_level, 2 - 1.0/6)
		self.assertAlmostEqual(cost, 6249999.9975, places=4)

		# Do provide loss_function.
		loss_function = lambda x: uniform_loss(x, yield_lo, yield_hi)
		base_stock_level, cost = newsvendor_with_additive_yield_uncertainty(holding_cost, stockout_cost,
									demand, yield_distribution=yield_distribution, loss_function=loss_function)
		self.assertAlmostEqual(base_stock_level, 2 - 1.0/6)
		self.assertAlmostEqual(cost, 6250000, places=4)

	def test_problem_9_5(self):
		"""Test that newsvendor_with_additive_yield_uncertainty() function correctly solves Problem 9.5.
		"""
		print_status('TestNewsvendorWithAdditiveYieldUncertainty', 'test_problem_9_5()')

		instance = load_instance("problem_9_5")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand = instance['demand']
		yield_lo = instance['yield_lo']
		yield_hi = instance['yield_hi']

		yield_distribution = uniform(yield_lo, yield_hi-yield_lo)

		# Don't provide loss_function.
		base_stock_level, cost = newsvendor_with_additive_yield_uncertainty(holding_cost, stockout_cost,
									demand, yield_distribution=yield_distribution)
		self.assertAlmostEqual(base_stock_level, 29.45, places=1)
		self.assertAlmostEqual(cost, 333.34, places=1)

		# Do provide loss_function.
		loss_function = lambda x: uniform_loss(x, yield_lo, yield_hi)
		base_stock_level, cost = newsvendor_with_additive_yield_uncertainty(holding_cost, stockout_cost,
									demand, yield_distribution=yield_distribution, loss_function=loss_function)
		self.assertAlmostEqual(base_stock_level, 29.45, places=1)
		self.assertAlmostEqual(cost, 333.34, places=1)


