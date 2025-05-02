import unittest

from stockpyl.wagner_whitin import *
from stockpyl.instances import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_wagner_whitin   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestWagnerWhitin(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestWagnerWhitin', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestWagnerWhitin', 'tear_down_class()')

	def test_example_3_9(self):
		"""Test that wagner_whitin function correctly solves Example 3.9.
		"""
		print_status('TestWagnerWhitin', 'test_example_3_9()')

		instance = load_instance("example_3_9")
		num_periods = instance['num_periods']
		holding_cost = instance['holding_cost']
		fixed_cost = instance['fixed_cost']
		demand = instance['demand']

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		self.assertEqual(order_quantities, [0, 210, 0, 150, 0])
		self.assertEqual(next_order_periods, [0, 3, 5, 5, 5])
		self.assertAlmostEqual(cost, 1380)

	def test_problem_3_27(self):
		"""Test that wagner_whitin function correctly solves Problem 3.27.
		"""
		print_status('TestWagnerWhitin', 'test_problem_3_27()')

		instance = load_instance("problem_3_27")
		num_periods = instance['num_periods']
		holding_cost = instance['holding_cost']
		fixed_cost = instance['fixed_cost']
		demand = instance['demand']

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		self.assertEqual(order_quantities, [0, 150, 180, 0, 200])
		self.assertEqual(next_order_periods, [0, 2, 4, 4, 5])
		self.assertAlmostEqual(cost, 424)

	def test_problem_3_29(self):
		"""Test that wagner_whitin function correctly solves Problem 3.29.
		"""
		print_status('TestWagnerWhitin', 'test_problem_3_29()')

		instance = load_instance("problem_3_29")
		num_periods = instance['num_periods']
		holding_cost = instance['holding_cost']
		fixed_cost = instance['fixed_cost']
		demand = instance['demand']

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		self.assertEqual(order_quantities, [0, 1310, 0, 1095, 0, 880])
		self.assertEqual(next_order_periods, [0, 3, 4, 5, 6, 6])
		self.assertAlmostEqual(cost, 423)

	def test_purchase_cost(self):
		"""Test that wagner_whitin function correctly solves SCMO HW problem with
		nonstationary purchase costs.
		"""
		print_status('TestWagnerWhitin', 'test_purchase_cost()')

		instance = load_instance("scmo_ww_hw_c")
		num_periods = instance['num_periods']
		holding_cost = instance['holding_cost']
		fixed_cost = instance['fixed_cost']
		demand = instance['demand']
		purchase_cost = instance['purchase_cost']

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand, purchase_cost)

		self.assertEqual(order_quantities, [0, 400, 3000, 0, 0, 0])
		self.assertEqual(next_order_periods, [0, 2, 6, 6, 6, 6])
		self.assertAlmostEqual(cost, 4940)

	def test_all_scalars(self):
		"""Test that wagner_whitin function works if all parameters are scalars.
		"""
		print_status('TestWagnerWhitin', 'test_all_scalars()')

		num_periods = 5
		holding_cost = 0.1
		fixed_cost = 100
		demand = 200

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		self.assertEqual(order_quantities, [0, 400, 0, 600, 0, 0])
		self.assertEqual(next_order_periods, [0, 3, 6, 6, 6, 6])
		self.assertAlmostEqual(cost, 280)

	def test_vector_lengths(self):
		"""Test that wagner_whitin function works with various lengths of input
		vectors.
		"""
		print_status('TestWagnerWhitin', 'test_long_vectors()')

		num_periods = 5
		holding_cost = [0.1, 0.1, 0.1, 0.1, 0.1]
		fixed_cost = [0, 100, 100, 100, 100, 100]
		demand = [0, 730, 580, 445, 650, 880]

		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		self.assertEqual(order_quantities, [0, 1310, 0, 1095, 0, 880])
		self.assertEqual(next_order_periods, [0, 3, 4, 5, 6, 6])
		self.assertAlmostEqual(cost, 423)

	def test_negative_parameter(self):
		"""Test that wagner_whitin function raises exception on negative parameter.
		"""
		print_status('TestWagnerWhitin', 'test_negative_parameter()')

		num_periods = 5
		holding_cost = -0.5
		fixed_cost = [0, 100, 100, 100, 100, 100]
		demand = [0, 730, 580, 445, 650, 880]
		with self.assertRaises(ValueError):
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)

		num_periods = 5
		holding_cost = [0.1, 0.1, -0.1, 0.1, 0.1]
		fixed_cost = [0, 100, 100, 100, 100, 100]
		demand = [0, 730, 580, 445, 650, 880]
		with self.assertRaises(ValueError):
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)


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

	def test_177(self):
		"""Test instance in PR #177 (handle zero-demand periods correctly).
		"""
		print_status('TestPreviousBugs', 'test_177()')

		num_periods = 6
		holding_cost = [1, 1, 1, 1, 1, 1]
		fixed_cost = [110, 108, 110, 120, 125, 134]
		demand = [0, 0, 0, 0, 0, 7]
		
		order_quantities, cost, costs_to_go, next_order_periods = \
			wagner_whitin(num_periods, holding_cost, fixed_cost, demand)
		
		self.assertListEqual(order_quantities, [0, 0, 0, 7, 0, 0, 0])
		self.assertEqual(cost, 131)