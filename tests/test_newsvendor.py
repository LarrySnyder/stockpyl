import unittest

from inventory import newsvendor


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_newsvendor   class : {:30s} function : {:30s}".format(class_name, function_name))


def setUpModule():
	"""Called once, before anything else in this module."""
	print_status('---', 'setUpModule()')


def tearDownModule():
	"""Called once, after everything else in this module."""
	print_status('---', 'tearDownModule()')


class TestNewsvendorNormal(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorNormal', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestNewsvendorNormal', 'tearDownClass()')

	def test_example_4_3(self):
		"""Test that newsvendor_normal function correctly solves Example 4.3.
		"""
		print_status('TestNewsvendorNormal', 'test_example_4_3()')

		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 56.603955927433887)
		self.assertAlmostEqual(cost, 1.997605193176645)

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, 40)
		self.assertAlmostEqual(base_stock_level, 40)
		self.assertAlmostEqual(cost, 7.356131552870388)

	def test_problem_4_1(self):
		"""Test that newsvendor_normal function correctly solves Problem 4.1.
		"""
		print_status('TestNewsvendorNormal', 'test_problem_4_1()')

		holding_cost = 65-22
		stockout_cost = 129-65+15
		demand_mean = 900
		demand_sd = 60

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 9.227214038234755e+02)
		self.assertAlmostEqual(cost, 2.718196781782411e+03)

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, 1040)
		self.assertAlmostEqual(base_stock_level, 1040)
		self.assertAlmostEqual(cost, 6.044298415188692e+03)

	def test_bad_type(self):
		"""Test that newsvendor_normal function raises exception on bad type.
		"""
		print_status('TestNewsvendorNormal', 'test_bad_type()')

		holding_cost = "taco"
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(TypeError):
			base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)

	def test_negative_parameter(self):
		"""Test that newsvendor_normal function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorNormal', 'test_negative_parameter()')

		holding_cost = -2
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(AssertionError):
			base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)
