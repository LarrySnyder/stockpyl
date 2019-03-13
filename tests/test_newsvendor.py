import unittest

from inventory import newsvendor


class TestNewsvendor(unittest.TestCase):
	def test_example_4_3(self):
		"""Test that newsvendor function correctly solves Example 4.3.
		"""

		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8

		base_stock_level, cost = newsvendor.newsvendor(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 56.603955927433887)
		self.assertAlmostEqual(cost, 1.997605193176645)

	def test_problem_4_1(self):
		"""Test that newsvendor function correctly solves Problem 4.1.
		"""

		holding_cost = 65-22
		stockout_cost = 129-65+15
		demand_mean = 900
		demand_sd = 60

		base_stock_level, cost = newsvendor.newsvendor(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 9.227214038234755e+02)
		self.assertAlmostEqual(cost, 2.718196781782411e+03)

	def test_bad_type(self):
		"""Test that newsvendor function raises exception on bad type.
		"""

		holding_cost = "taco"
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(TypeError):
			base_stock_level, cost = newsvendor.newsvendor(holding_cost, stockout_cost, demand_mean, demand_sd)

	def test_negative_parameter(self):
		"""Test that newsvendor function raises exception on negative parameter.
		"""

		holding_cost = -2
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(AssertionError):
			base_stock_level, cost = newsvendor.newsvendor(holding_cost, stockout_cost, demand_mean, demand_sd)
