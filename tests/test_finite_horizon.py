import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm
import scipy.io as sio

import stockpyl.finite_horizon as finite_horizon
from stockpyl.instances import *
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
		print_status('TestFiniteHorizon', 'compare_solution_vs_matlab()')

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

		instance = load_instance("problem_4_29")

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				instance['fixed_cost'], 
				instance['demand_mean'], 
				instance['demand_sd'], 
				None,
				instance['discount_factor'], 
				instance['initial_inventory_level']
			)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_29_with_T_arrays(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29
		when inputs are specified as T-length arrays.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29_with_T_arrays()')

		instance = load_instance("problem_4_29")

		num_periods = instance['num_periods']
		holding_cost = [instance['holding_cost']] * num_periods
		stockout_cost = [instance['stockout_cost']] * num_periods
		purchase_cost = [instance['purchase_cost']] * num_periods
		fixed_cost = [instance['fixed_cost']] * num_periods
		demand_mean = [instance['demand_mean']] * num_periods
		demand_sd = [instance['demand_sd']] * num_periods
		discount_factor = [instance['discount_factor']] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, instance['terminal_holding_cost'], instance['terminal_stockout_cost'],
			purchase_cost, fixed_cost, demand_mean, demand_sd, None, discount_factor,
			instance['initial_inventory_level'])

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_29_with_T1_arrays(self):
		"""Test that finite_horizon() function correctly solves Problem 4.29
		when inputs are specified as (T+1)-length arrays.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_29_with_T1_arrays()')

		instance = load_instance("problem_4_29")

		num_periods = instance['num_periods']
		holding_cost = [None] + [instance['holding_cost']] * num_periods
		stockout_cost = [None] + [instance['stockout_cost']] * num_periods
		purchase_cost = [None] + [instance['purchase_cost']] * num_periods
		fixed_cost = [None] + [instance['fixed_cost']] * num_periods
		demand_mean = [None] + [instance['demand_mean']] * num_periods
		demand_sd = [None] + [instance['demand_sd']] * num_periods
		discount_factor = [None] + [instance['discount_factor']] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, instance['terminal_holding_cost'], instance['terminal_stockout_cost'],
			purchase_cost, fixed_cost, demand_mean, demand_sd, None, discount_factor,
			instance['initial_inventory_level'])

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

		instance = load_instance("problem_4_29")

		num_periods = instance['num_periods']
		holding_cost = [None] + [instance['holding_cost']] * num_periods
		stockout_cost = [instance['stockout_cost']] * num_periods
		demand_mean = [None] + [instance['demand_mean']] * num_periods
		demand_sd = [instance['demand_sd']] * num_periods
		discount_factor = [None] + [instance['discount_factor']] * num_periods

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(num_periods, holding_cost,
			stockout_cost, instance['terminal_holding_cost'], instance['terminal_stockout_cost'],
			instance['purchase_cost'], instance['fixed_cost'], demand_mean, demand_sd, None, discount_factor,
			instance['initial_inventory_level'])

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_29')

	def test_problem_4_30(self):
		"""Test that finite_horizon() function correctly solves Problem 4.30.
		"""
		print_status('TestFiniteHorizon', 'test_problem_4_30()')

		instance = load_instance("problem_4_30")

		# Solve problem.
		reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
			x_range = finite_horizon.finite_horizon_dp(
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				instance['fixed_cost'], 
				instance['demand_mean'], 
				instance['demand_sd'], 
				None,
				instance['discount_factor'], 
				instance['initial_inventory_level']
			)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
			'tests/additional_files/problem_4_30')

	def test_bad_parameters(self):
		"""Test that finite_horizon() function correctly raises errors on bad parameters.
		"""
		print_status('TestFiniteHorizon', 'test_bad_parameters()')

		instance = load_instance("problem_4_30")

		with self.assertRaises(ValueError):
			reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
				x_range = finite_horizon.finite_horizon_dp(
					-3, 
					instance['holding_cost'], 
					instance['stockout_cost'], 
					instance['terminal_holding_cost'], 
					instance['terminal_stockout_cost'], 
					instance['purchase_cost'], 
					instance['fixed_cost'], 
					instance['demand_mean'], 
					instance['demand_sd'], 
					None,
					instance['discount_factor'], 
					instance['initial_inventory_level']
				)

		with self.assertRaises(ValueError):
			reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
				x_range = finite_horizon.finite_horizon_dp(
					5.7, 
					instance['holding_cost'], 
					instance['stockout_cost'], 
					instance['terminal_holding_cost'], 
					instance['terminal_stockout_cost'], 
					instance['purchase_cost'], 
					instance['fixed_cost'], 
					instance['demand_mean'], 
					instance['demand_sd'], 
					None,
					instance['discount_factor'], 
					instance['initial_inventory_level']
				)

		with self.assertRaises(ValueError):
			reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
				x_range = finite_horizon.finite_horizon_dp(
					instance['num_periods'], 
					instance['holding_cost'], 
					instance['stockout_cost'], 
					-5, 
					instance['terminal_stockout_cost'], 
					instance['purchase_cost'], 
					instance['fixed_cost'], 
					instance['demand_mean'], 
					instance['demand_sd'], 
					None,
					instance['discount_factor'], 
					instance['initial_inventory_level']
				)

		holding_cost = [1] * 10
		holding_cost[3] = -5
		with self.assertRaises(ValueError):
			reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
				x_range = finite_horizon.finite_horizon_dp(
					instance['num_periods'], 
					holding_cost, 
					instance['stockout_cost'], 
					instance['terminal_holding_cost'], 
					instance['terminal_stockout_cost'], 
					instance['purchase_cost'], 
					instance['fixed_cost'], 
					instance['demand_mean'], 
					instance['demand_sd'], 
					None,
					instance['discount_factor'], 
					instance['initial_inventory_level']
				)

		discount_factor = [0.98] * 10
		discount_factor[2] = 1.5
		with self.assertRaises(ValueError):
			reorder_points, order_up_to_levels, total_cost, cost_matrix, oul_matrix, \
				x_range = finite_horizon.finite_horizon_dp(
					instance['num_periods'], 
					instance['holding_cost'], 
					instance['stockout_cost'], 
					instance['terminal_holding_cost'], 
					instance['terminal_stockout_cost'], 
					instance['purchase_cost'], 
					instance['fixed_cost'], 
					instance['demand_mean'], 
					instance['demand_sd'], 
					None,
					discount_factor, 
					instance['initial_inventory_level']
				)

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
			purchase_cost, fixed_cost, demand_mean, demand_sd, None, discount_factor,
			initial_inventory_level)

		# Test against MATLAB solution.
		self.compare_solution_vs_matlab(reorder_points, order_up_to_levels,
										total_cost, cost_matrix, oul_matrix, x_range,
										'tests/additional_files/instance_1', sample_frac=None)


class TestMyopicBounds(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMyopicBounds', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMyopicBounds', 'tear_down_class()')

	def test_5_period_instance(self):
		"""Test that myopic_bounds() function correctly finds bounds for a 5-period instance.
		"""
		print_status('TestMyopicBounds', 'test_5_period_instance()')

		S_underbar, S_overbar, s_underbar, s_overbar = finite_horizon.myopic_bounds(5, 1, 20, 1, 20, 2, 50, 100, 20)

		np.testing.assert_allclose(S_underbar, [0., 133.36782388, 133.36782388, 133.36782388, 133.36782388, 126.18343434])
		np.testing.assert_allclose(S_overbar, [0., 191.66022943, 191.66022943, 191.66022943, 191.66022943, 126.18343434])
		np.testing.assert_allclose(s_underbar, [0., 110.26036849, 110.26036849, 110.26036849, 110.26036849, 111.66574177])
		np.testing.assert_allclose(s_overbar, [0., 133.36782388, 133.36782388, 133.36782388, 133.36782388, 111.66574177])

	def test_problem_4_29(self):
		"""Test that myopic_bounds() function correctly finds bounds for Problem 4.29.
		"""
		print_status('TestMyopicBounds', 'test_problem_4_29()')

		instance = load_instance("problem_4_29")

		S_underbar, S_overbar, s_underbar, s_overbar = finite_horizon.myopic_bounds(
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				instance['fixed_cost'], 
				instance['demand_mean'], 
				instance['demand_sd'], 
				instance['discount_factor']
			)

		np.testing.assert_allclose(S_underbar, [0., 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 22.7233349])
		np.testing.assert_allclose(S_overbar, [0., 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 22.7233349])
		np.testing.assert_allclose(s_underbar, [0., 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 22.7233349])
		np.testing.assert_allclose(s_overbar, [0., 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 22.7233349])

	def test_problem_4_29_with_K(self):
		"""Test that myopic_bounds() function correctly finds bounds for Problem 4.29 with K = 100.
		"""
		print_status('TestMyopicBounds', 'test_problem_4_29_with_K()')

		instance = load_instance("problem_4_29")
		fixed_cost = 100

		S_underbar, S_overbar, s_underbar, s_overbar = finite_horizon.myopic_bounds(
				instance['num_periods'], 
				instance['holding_cost'], 
				instance['stockout_cost'], 
				instance['terminal_holding_cost'], 
				instance['terminal_stockout_cost'], 
				instance['purchase_cost'], 
				fixed_cost, 
				instance['demand_mean'], 
				instance['demand_sd'], 
				instance['discount_factor']
			)
		np.testing.assert_allclose(S_underbar, [0., 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 23.27904955, 22.7233349])
		np.testing.assert_allclose(S_overbar, [0., 120.5649451, 120.5649451, 120.5649451, 120.5649451, 120.5649451, 120.5649451, 120.5649451, 120.5649451, 120.5649451, 22.7233349])
		np.testing.assert_allclose(s_underbar, [0., 13.85076661, 13.85076661, 13.85076661, 13.85076661, 13.85076661, 13.85076661, 13.85076661, 13.85076661, 13.85076661, 16.09987465])
		np.testing.assert_allclose(s_overbar, [0., 21.34135253, 21.34135253, 21.34135253, 21.34135253, 21.34135253, 21.34135253, 21.34135253, 21.34135253, 21.34135253, 16.09987465])
