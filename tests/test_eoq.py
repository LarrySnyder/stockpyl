import unittest

from inventory import eoq


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_eoq   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestEconomicOrderQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantity', 'tear_down_class()')

	def test_example_3_1(self):
		"""Test that EOQ function correctly solves Example 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_example_3_1()')

		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		order_quantity, cost = eoq.economic_order_quantity(fixed_cost, holding_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 304.0467800264368)
		self.assertAlmostEqual(cost, 68.410525505948272)

	def test_problem_3_1(self):
		"""Test that EOQ function correctly solves Problem 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_problem_3_1()')

		fixed_cost = 2250
		holding_cost = 275
		demand_rate = 500 * 365
		order_quantity, cost = eoq.economic_order_quantity(fixed_cost, holding_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 1728.109844993551)
		self.assertAlmostEqual(cost, 475230.2073732266)

	def test_bad_type(self):
		"""Test that EOQ function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantity', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		with self.assertRaises(TypeError):
			order_quantity, cost = eoq.economic_order_quantity(fixed_cost, holding_cost, demand_rate)

	def test_negative_parameter(self):
		"""Test that EOQ function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantity', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		with self.assertRaises(AssertionError):
			order_quantity, cost = eoq.economic_order_quantity(fixed_cost, holding_cost, demand_rate)


class TestEconomicOrderQuantityWithBackorders(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithBackorders', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithBackorders', 'tear_down_class()')

	def test_example_3_8(self):
		"""Test that EOQB function correctly solves Example 3.8.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_example_3_8()')

		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		order_quantity, stockout_fraction, cost = \
			eoq.economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 310.8125551589646)
		self.assertAlmostEqual(stockout_fraction, 0.043062200956938)
		self.assertAlmostEqual(cost, 66.921363550973254)

	def test_problem_3_2b(self):
		"""Test that EOQB function correctly solves Problem 3.2(b).
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_problem_3_2b()')

		fixed_cost = 40
		holding_cost = (165 * 0.17 + 12)
		stockout_cost = 60
		demand_rate = 40 * 52
		order_quantity, stockout_fraction, cost = \
			eoq.economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 83.235448128898042)
		self.assertAlmostEqual(stockout_fraction, 0.400299850074962)
		self.assertAlmostEqual(cost, 1999.148244415212)

	def test_bad_type(self):
		"""Test that EOQB function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		with self.assertRaises(TypeError):
			order_quantity, stockout_fraction, cost = \
				eoq.economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)

	def test_negative_parameter(self):
		"""Test that EOQB function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		with self.assertRaises(AssertionError):
			order_quantity, stockout_fraction, cost = \
				eoq.economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)


class TestEconomicProductionQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicProductionQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicProductionQuantity', 'tear_down_class()')

	def test_example_3_1(self):
		"""Test that EPQ function correctly solves Example 3.1, plus mu = 2000.
		"""
		print_status('TestEconomicProductionQuantity', 'test_example_3_1()')

		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		production_rate = 2000
		order_quantity, cost = eoq.economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)
		self.assertAlmostEqual(order_quantity, 513.9328595516969)
		self.assertAlmostEqual(cost, 40.472212689696120)

	def test_problem_3_22(self):
		"""Test that EPQ function correctly solves Problem 3.22.
		"""
		print_status('TestEconomicProductionQuantity', 'test_problem_3_22()')

		fixed_cost = 4
		holding_cost = 0.08
		demand_rate = 80
		production_rate = 110
		order_quantity, cost = eoq.economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)
		self.assertAlmostEqual(order_quantity, 171.2697677155351)
		self.assertAlmostEqual(cost, 3.736794931975310)

	def test_bad_type(self):
		"""Test that EPQ function raises exception on bad type.
		"""
		print_status('TestEconomicProductionQuantity', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		production_rate = 2000
		with self.assertRaises(TypeError):
			order_quantity, cost = eoq.economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)

	def test_negative_parameter(self):
		"""Test that EPQ function raises exception on negative parameter.
		"""
		print_status('TestEconomicProductionQuantity', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		production_rate = 2000
		with self.assertRaises(AssertionError):
			order_quantity, cost = eoq.economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)

