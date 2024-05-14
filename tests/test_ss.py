import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm

from stockpyl.ss import *
from stockpyl.instances import *
from tests.settings import *

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_ss   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestsSCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestsSCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestsSCost', 'tear_down_class()')

	def test_example_4_7(self):
		"""Test that s_s_cost() function correctly evaluates cost in Example 4.7.
		"""
		print_status('TestsSCost', 'test_example_4_7()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']

		cost = s_s_cost_discrete(4, 10, holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertAlmostEqual(cost, 8.034111561471644)

		cost = s_s_cost_discrete(6, 18, holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertAlmostEqual(cost, 10.193798671644046)

	def test_problem_4_31(self):
		"""Test that s_s_cost() function correctly evaluates cost in Problem 4.31.
		"""
		print_status('TestsSCost', 'test_problem_4_31()')

		instance = load_instance("problem_4_31")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']

		cost = s_s_cost_discrete(4, 10, holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertAlmostEqual(cost, 2.622755613772775e+02)

		cost = s_s_cost_discrete(2, 7, holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertAlmostEqual(cost, 2.235748295669688e+02)

	def test_fz_instances(self):
		"""Test Zheng and Federgruen (1991) instances.
		"""
		print_status('TestsSCost', 'test_fz_instances()')

		h = 1
		p = 9
		K = 64
		mu = list(range(10, 80, 5)) + [21, 22, 23, 24, 51, 52, 59, 61, 63, 64]
		s = [6, 10, 14, 19, 23, 28, 33, 37, 42, 47, 52, 56, 62, 67, 15, 16, 17, 18, 43, 44, 51, 52, 54, 55]
		S = [40, 49, 62, 56, 66, 77, 87, 97, 108, 118, 129, 75, 81, 86, 65, 68, 52, 54, 110, 112, 126, 131, 73, 74]
		c = [35.022, 42.698, 49.173, 54.262, 57.819, 61.215, 64.512, 67.776, 70.975, 74.149, 77.306, 78.518, 79.037,
			 79.554, 50.406, 51.632, 52.757, 53.518, 71.611, 72.246, 76.679, 77.929, 78.287, 78.402]

		# To run only every ``skip`` instances, set ``step`` below.
		if RUN_ALL_TESTS:
			step = 1
		else:
			step = 10

		for n in range(1, len(mu), step):
			cost = s_s_cost_discrete(s[n], S[n], h, p, K, True, mu[n], None, None)
			self.assertAlmostEqual(cost, c[n], places=3)


class TestsSOptimalsS(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestsSOptimalsS', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestsSOptimalsS', 'tear_down_class()')

	def test_example_4_7(self):
		"""Test that s_s_discrete_exact() function solves Example 4.7.
		"""
		print_status('TestsSOptimalsS', 'test_example_4_7()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']

		s, S, g = s_s_discrete_exact(holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertEqual(s, 4)
		self.assertEqual(S, 10)
		self.assertAlmostEqual(g, 8.034111561471644)

	def test_problem_4_31(self):
		"""Test that s_s_discrete_exact() function solves Problem 4.31.
		"""
		print_status('TestsSOptimalsS', 'test_problem_4_31()')

		instance = load_instance("problem_4_31")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']

		s, S, g = s_s_discrete_exact(holding_cost, stockout_cost,
									fixed_cost, True, demand_mean)
		self.assertEqual(s, 2)
		self.assertEqual(S, 7)
		self.assertAlmostEqual(g, 2.235748295669688e+02)

	def test_problem_4_31_custom_pmf(self):
		"""Test that s_s_discrete_exact() function solves Problem 4.31 when demand distribution
		is provided as a demand_pmf object. (There was a bug that made this break; see https://github.com/LarrySnyder/stockpyl/issues/132.)
		"""
		print_status('TestsSOptimalsS', 'test_problem_4_31_custom_pmf()')

		instance = load_instance("problem_4_31")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']

		# Build demand_pmf.
		demand_hi = 50
		demand_pmf = [poisson.pmf(n, demand_mean) for n in range(demand_hi+1)]
		s, S, g = s_s_discrete_exact(holding_cost, stockout_cost,
									fixed_cost, use_poisson=False, demand_hi=demand_hi, demand_pmf=demand_pmf)
		
		self.assertEqual(s, 2)
		self.assertEqual(S, 7)
		self.assertAlmostEqual(g, 2.235748295669688e+02)

#	@unittest.skipUnless(RUN_ALL_TESTS, "TestsSOptimaltest_fz_instances skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_fz_instances(self):
		"""Test Zheng and Federgruen (1991) instances.
		"""
		print_status('TestsSOptimalsS', 'test_fz_instances()')

		h = 1
		p = 9
		K = 64
		mu = list(range(10, 80, 5)) + [21, 22, 23, 24, 51, 52, 59, 61, 63, 64]
		s_opt = [6, 10, 14, 19, 23, 28, 33, 37, 42, 47, 52, 56, 62, 67, 15, 16, 17, 18, 43, 44, 51, 52, 54, 55]
		S_opt = [40, 49, 62, 56, 66, 77, 87, 97, 108, 118, 129, 75, 81, 86, 65, 68, 52, 54, 110, 112, 126, 131, 73, 74]
		c_opt = [35.022, 42.698, 49.173, 54.262, 57.819, 61.215, 64.512, 67.776, 70.975, 74.149, 77.306, 78.518, 79.037,
			 79.554, 50.406, 51.632, 52.757, 53.518, 71.611, 72.246, 76.679, 77.929, 78.287, 78.402]

		# To run only every ``skip`` instances, set ``step`` below.
		if RUN_ALL_TESTS:
			step = 1
		else:
			step = 10

		for n in range(1, len(mu), step):
			s, S, g = s_s_discrete_exact(h, p, K, True, mu[n])
			self.assertEqual(s, s_opt[n])
			self.assertEqual(S, S_opt[n])
			self.assertAlmostEqual(g, c_opt[n], places=3)


class TestsSPowerApproximation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestsSPowerApproximation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestsSPowerApproximation', 'tear_down_class()')

	def test_example_4_8(self):
		"""Test that s_s_power_approximation() function solves Example 4.8.
		"""
		print_status('TestsSPowerApproximation', 'test_example_4_8()')

		instance = load_instance("example_4_8")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		s, S = s_s_power_approximation(holding_cost, stockout_cost,
									fixed_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(s, 40.194616956474071)
		self.assertAlmostEqual(S, 74.290170109805786)

	def test_problem_4_32(self):
		"""Test that s_s_power_approximation() function solves Problem 4.32.
		"""
		print_status('TestsSPowerApproximation', 'test_problem_4_32()')

		instance = load_instance("problem_4_32")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		fixed_cost = instance['fixed_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		s, S = s_s_power_approximation(holding_cost, stockout_cost,
									fixed_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(s, 2.266137928222839e+02)
		self.assertAlmostEqual(S, 3.243797868133974e+02)

