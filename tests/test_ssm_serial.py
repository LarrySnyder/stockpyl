import unittest
import numpy as np

from pyinv import ssm_serial
from tests.instances_ssm_serial import *
from pyinv.instances import *

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_ssm_serial   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestLocalToEchelonBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLocalToEchelonBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLocalToEchelonBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that local_to_echelon_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestLocalToEchelonBaseStockLevels', 'test_example_6_1()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_local = {1: 4, 2: 5, 3: 1}
		S_echelon = ssm_serial.local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 4, 2: 9, 3: 10})

		S_local = {1: 10, 2: 0, 3: 2}
		S_echelon = ssm_serial.local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 10, 2: 10, 3: 12})

		S_local = {1: 3, 2: -4, 3: 5}
		S_echelon = ssm_serial.local_to_echelon_base_stock_levels(instance, S_local)
		self.assertDictEqual(S_echelon, {1: 3, 2: -1, 3: 4})


class TestExpectedCost(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExpectedCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExpectedCost', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that expected_cost() correctly calculates cost for
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestExpectedCost', 'test_example_6_1()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_echelon = {1: 4, 2: 9, 3: 10}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 4.029913673114759e+02)

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 3.365063607909906e+02)

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 6.309060854797420e+02)

	def test_problem_6_1(self):
		"""Test that expected_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedCost', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 1.677772194726791e+02)

		S_echelon = {1: 50, 2: 125}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 1.238684758097710e+03)

		S_echelon = {1: 75, 2: 50}
		cost = ssm_serial.expected_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 2.326562153947784e+03)


class TestExpectedHoldingCost(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExpectedHoldingCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExpectedHoldingCost', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that expected_holding_cost() correctly calculates cost for
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestExpectedHoldingCost', 'test_example_6_1()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_echelon = {1: 4, 2: 9, 3: 10}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 30.290113004920954)

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 30.189019642459233)

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 30.134385552606360)

	def test_problem_6_1(self):
		"""Test that expected_holding_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedHoldingCost', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 1.507714604680893e+02)

		S_echelon = {1: 50, 2: 125}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 1.001438804274813e+02)

		S_echelon = {1: 75, 2: 50}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, 100, 10)
		self.assertAlmostEqual(cost, 99.955972907264330)


class TestOptimizeBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestOptimizeBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestOptimizeBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100,
			d_num=10)
		correct_S_star = [0, 6.52, 12.24, 22.8]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n])
		self.assertAlmostEqual(C_star, 47.835336250392820)

	def test_problem_6_1(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.1.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100,
			d_num=10)
		correct_S_star = [0, 1.242440692221066e+02, 2.287925107043527e+02]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n])
		self.assertAlmostEqual(C_star, 1.677772194726791e+02)

	def test_problem_6_2a(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.2a.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_2a()')

		instance = copy.deepcopy(problem_6_2a_network)
		instance.reindex_nodes({n: n+1 for n in instance.node_indices})

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100,
			d_num=10)
		correct_S_star = [0, 39.8225, 77.2372, 111.5340, 142.7129, 173.8919]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=4)
		self.assertAlmostEqual(C_star, 458.6306, places=4)

