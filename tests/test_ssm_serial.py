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


class TestEchelonToLocalBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEchelonToLocalBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEchelonToLocalBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that echelon_to_local_base_stock_levels() correctly converts
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestEchelonToLocalBaseStockLevels', 'test_example_6_1()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_echelon = {1: 4, 2: 9, 3: 10}
		S_local = ssm_serial.echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 4, 2: 5, 3: 1})

		S_echelon = {1: 10, 2: 10, 3: 12}
		S_local = ssm_serial.echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 10, 2: 0, 3: 2})

		S_echelon = {1: 3, 2: -1, 3: 4}
		S_local = ssm_serial.echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: -1, 2: 0, 3: 5})

		S_echelon = {1: 10, 2: 15, 3: 5}
		S_local = ssm_serial.echelon_to_local_base_stock_levels(instance, S_echelon)
		self.assertDictEqual(S_local, {1: 5, 2: 0, 3: 0})


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
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 4.025320847013973e+02)

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 3.227131745107600e+02)

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 6.292579915269251e+02)

	def test_problem_6_1(self):
		"""Test that expected_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedCost', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 1.693611203524711e+02)

		S_echelon = {1: 50, 2: 125}
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 1.218952430250280e+03)

		S_echelon = {1: 75, 2: 50}
		cost = ssm_serial.expected_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 2.378816200366911e+03)


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
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 29.979059977933002)

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 30.013403869820511)

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 29.986925977144374)

	def test_problem_6_1(self):
		"""Test that expected_holding_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedHoldingCost', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 1.526476024969551e+02)

		S_echelon = {1: 50, 2: 125}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 1.002946042252444e+02)

		S_echelon = {1: 75, 2: 50}
		cost = ssm_serial.expected_holding_cost(instance, S_echelon, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 99.997129696149514)


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
			instance, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = [0, 6.514438807325977, 12.232248034454390, 22.788203530691469]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 47.820555075345887, places=5)

	def test_problem_6_1(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.1.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_1()')

		instance = copy.deepcopy(problem_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2})

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1 - stats.norm.cdf(4),
			ltd_upper_tail_prob=1 - stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1 - stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1 - stats.norm.cdf(8))
		correct_S_star = [0, 1.241618472110342e2, 2.286691776877441e2]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 1.676947889401860e+02, places=5)

	def test_problem_6_2a(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.2a.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_2a()')

		instance = copy.deepcopy(problem_6_2a_network)
		instance.reindex_nodes({n: n+1 for n in instance.node_indices})

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1 - stats.norm.cdf(4),
			ltd_upper_tail_prob=1 - stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1 - stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1 - stats.norm.cdf(8))
		correct_S_star = [0, 39.7915536774345, 77.1934831561084, 111.478585178226, 142.646859743788, 173.815134309349]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=4)
		self.assertAlmostEqual(C_star, 4.584970628129348e+02, places=4)

	def test_example_6_1_uniform(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 with uniform demands.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_uniform()')

		instance = copy.deepcopy(example_6_1_network)
		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		demand_source_factory = DemandSourceFactory()
		for n in instance.nodes:
			if n.index == 1:
				demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
				demand_source.lo = 5 - np.sqrt(12) / 2
				demand_source.hi = 5 + np.sqrt(12) / 2
			else:
				demand_source = demand_source_factory.build_demand_source(DemandType.NONE)
			n.demand_source = demand_source

		S_star, C_star = ssm_serial.optimize_base_stock_levels(
			instance, S=None, plots=False, x=None, x_num=100, d_num=10)
		correct_S_star = {1: 6.293580485578014, 2: 11.95126810804254, 3: 22.601033044446353}
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 46.45421661501915, places=5)

