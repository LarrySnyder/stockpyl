import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm
import scipy.io as sio

import pyinv.finite_horizon as finite_horizon
from pyinv.instances import *
from tests.settings import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_finite_horizon   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestFiniteHorizon(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestFiniteHorizon', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestFiniteHorizon', 'tear_down_class()')

	def compare_solution_vs_matlab(self, reorder_points, order_up_to_levels, \
								   total_cost, cost_matrix, oul_matrix, x_range, \
								   matlab_filename, sample_frac=None):
		"""Test solution to the finite-horizon problem against MATLAB solution.

		Set ``sample_frac`` to test only a fraction of the elements of the
		larger arrays, rather than all elements. Set to 1 or ``None`` to test all.

		MATLAB command to save results:
		>> save('filename.mat', 's_small', 'S_large', 'total_cost', 'costmatrix', 'OULmatrix', 'xrange')
		"""
		# Read and parse solution obtained using MATLAB.
		# MATLAB variables require some manipulation:
		#   * Take transpose (because MATLAB outputs are column vectors).
		# 	* Take 0th element (because values are parsed as lists of lists).
		# 	* Convert to list from ndarray.
		# (For some variables,
		# we take transpose because MATLAB outputs are column vectors. For some,
		# we take 0th element because values are parsed as lists of lists.)
		mat_contents = sio.loadmat(matlab_filename)
		reorder_points_mat = list(np.transpose(mat_contents["s_small"])[0])
		order_up_to_levels_mat = list(np.transpose(mat_contents["S_large"])[0])
		total_cost_mat = float(mat_contents["total_cost"])
		cost_matrix_mat = mat_contents["costmatrix"]
		oul_matrix_mat = mat_contents["OULmatrix"]
		x_range_mat = list(np.transpose(mat_contents["xrange"])[0])

		# Compare solutions. (For some, use np.testing.assert_allclose
		# since unittest does not have assertAlmostEqual for arrays.)
		self.assertEqual(reorder_points[1:], reorder_points_mat)
		self.assertEqual(order_up_to_levels[1:], order_up_to_levels_mat)
		self.assertAlmostEqual(total_cost, total_cost_mat)
		self.assertEqual(list(x_range), x_range_mat)
		if sample_frac == 1 or sample_frac is None:
			np.testing.assert_allclose(cost_matrix[1:], cost_matrix_mat)
			np.testing.assert_allclose(oul_matrix[1:], oul_matrix_mat)
		else:
			for t in range(cost_matrix.shape[0]-1):
				for n in range(cost_matrix.shape[1]):
					if np.random.rand() < sample_frac:
						self.assertAlmostEqual(cost_matrix[t+1, n], cost_matrix_mat[t, n])
			for t in range(oul_matrix.shape[0] - 1):
				for n in range(oul_matrix.shape[1]):
					if np.random.rand() < sample_frac:
						self.assertAlmostEqual(oul_matrix[t+1, n], oul_matrix_mat[t, n])

	def test_problem_4_29(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29()')

		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_29_with_T_arrays(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29
		when inputs are specified as T-length arrays.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29_with_T_arrays()')

		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")
		holding_cost = [holding_cost] * num_periods
		stockout_cost = [stockout_cost] * num_periods
		purchase_cost = [purchase_cost] * num_periods
		fixed_cost = [fixed_cost] * num_periods
		demand_mean = [demand_mean] * num_periods
		demand_sd = [demand_sd] * num_periods
		discount_factor = [discount_factor] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_29_with_T1_arrays(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29
		when inputs are specified as (T+1)-length arrays.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29_with_T1_arrays()')

		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")
		holding_cost = [None] + [holding_cost] * num_periods
		stockout_cost = [None] + [stockout_cost] * num_periods
		purchase_cost = [None] + [purchase_cost] * num_periods
		fixed_cost = [None] + [fixed_cost] * num_periods
		demand_mean = [None] + [demand_mean] * num_periods
		demand_sd = [None] + [demand_sd] * num_periods
		discount_factor = [None] + [discount_factor] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_29_with_mixed_inputs(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29
		when some inputs are specified as singletons, some as T-length arrays,
		and some as (T+1)-length arrays.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29_with_mixed_inputs()')

		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")
		holding_cost = [None] + [holding_cost] * num_periods
		stockout_cost = [stockout_cost] * num_periods
		demand_mean = [None] + [demand_mean] * num_periods
		demand_sd = [demand_sd] * num_periods
		discount_factor = [None] + [discount_factor] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_30(self):
		"""Test that finite_horizon() function correctly solves Problem 4.30.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_30()')

		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_30")

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_30')

	@unittest.skipUnless(RUN_ALL_TESTS, "TestFiniteHorizon.test_instance_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_instance_1(self):
		"""Test that finite_horizon() function correctly solves instance
		specified below..
		"""
		print_status('TestFiniteHorizon', 'test_instance_1()')

		num_periods = 12
		holding_cost = [1, 1, 1, 1, 2, 2, 0.5, 0.5, 1, 1, 2, 2]
		stockout_cost = [20, 20, 10, 15, 10, 10, 20, 20, 15, 25, 20, 10]
		terminal_holding_cost = 4
		terminal_stockout_cost = 50
		purchase_cost = [0.5, 0.5, 0.5, 0.5, 0.2, 0.8, 0.2, 0.8, 0.5, 0.5, 0.5, 0.5]
		fixed_cost = 0
		demand_mean = [20, 60, 110, 200, 200, 40, 200, 200, 100, 170, 30, 90]
		demand_sd = [4.6000, 11.9000, 26.4000, 32.8000, 1.8000, 8.5000, 46.7000, 33.9000, 18.9000, 31.6000, 2.9000,
					 14.8000]
		discount_factor = 0.98
		initial_inventory_level = 0

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, terminal_holding_cost, terminal_stockout_cost,
			purchase_cost, fixed_cost, demand_mean, demand_sd, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
										'tests/additional_files/instance_1', sample_frac=None)



