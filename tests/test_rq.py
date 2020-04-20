import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm

from pyinv import rq


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_rq   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestrQCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQCost', 'tear_down_class()')

	def test_example_5_1(self):
		"""Test that r_q_cost() function correctly evaluates cost in Example 5.1.
		"""
		print_status('TestNewsvendorNormal', 'test_example_5_1()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		cost = rq.r_q_cost(126.8, 328.5, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(cost, 78.071162509282942)

		cost = rq.r_q_cost(100, 250, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(cost, 87.346478028174985)

	def test_problem_5_1(self):
		"""Test that r_q_cost() function correctly evaluates cost in Problem 5.1.
		"""
		print_status('TestNewsvendorNormal', 'test_problem_5_1()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		cost = rq.r_q_cost(-1.9859, 166.95, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(cost, 4.842110418415538e+02)

		cost = rq.r_q_cost(100, 250, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(cost, 8.303219178082192e+02)


class TestrQOptimalrForQ(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQOptimalrForQ', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQOptimalrForQ', 'tear_down_class()')

	def test_example_5_2(self):
		"""Test that r_q_optimal_r_for_q() function correctly finds r(Q) for
		Example 5.2.
		"""
		print_status('TestrQOptimalrForQ', 'test_example_5_2()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		r = rq.r_q_optimal_r_for_q(318, holding_cost,
											stockout_cost,
											annual_demand_mean,
											annual_demand_standard_deviation,
											lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 1.277880348669655e+02)

		r = rq.r_q_optimal_r_for_q(150, holding_cost,
								   stockout_cost,
								   annual_demand_mean,
								   annual_demand_standard_deviation,
								   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 1.471949581740714e+02)

		r = rq.r_q_optimal_r_for_q(750, holding_cost,
											stockout_cost,
											annual_demand_mean,
											annual_demand_standard_deviation,
											lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 99.853773396165280)

	def test_problem_5_1(self):
		"""Test that r_q_optimal_r_for_q() function correctly finds r(Q) for
		Problem 5.1.
		"""
		print_status('TestrQEILApproximation', 'test_problem_5_1()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		r = rq.r_q_optimal_r_for_q(318, holding_cost,
											stockout_cost,
											annual_demand_mean,
											annual_demand_standard_deviation,
											lead_time, tol=1e-6)
		self.assertAlmostEqual(r, -11.727678833180178)

		r = rq.r_q_optimal_r_for_q(150, holding_cost,
								   stockout_cost,
								   annual_demand_mean,
								   annual_demand_standard_deviation,
								   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, -0.885130303271656)

		r = rq.r_q_optimal_r_for_q(750, holding_cost,
								   stockout_cost,
								   annual_demand_mean,
								   annual_demand_standard_deviation,
								   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, -39.569675038859785)

	def test_problem_5_3(self):
		"""Test that r_q_optimal_r_for_q() function correctly finds r(Q) for
		Problem 5.3.
		"""
		print_status('TestrQEILApproximation', 'test_problem_5_3()')

		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		annual_demand_mean = 192
		annual_demand_standard_deviation = 17.4
		lead_time = 3

		r = rq.r_q_optimal_r_for_q(318, holding_cost,
											stockout_cost,
											annual_demand_mean,
											annual_demand_standard_deviation,
											lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 6.121331312304716e+02)

		r = rq.r_q_optimal_r_for_q(150, holding_cost,
								   stockout_cost,
								   annual_demand_mean,
								   annual_demand_standard_deviation,
								   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 6.225171783526781e+02)

		r = rq.r_q_optimal_r_for_q(750, holding_cost,
								   stockout_cost,
								   annual_demand_mean,
								   annual_demand_standard_deviation,
								   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 5.984126476551643e+02)


class TestrQEILApproximation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQEILApproximation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQEILApproximation', 'tear_down_class()')

	def test_example_5_2(self):
		"""Test that r_q_eil_approximation() function correctly solves Example 5.2.
		"""
		print_status('TestrQEILApproximation', 'test_example_5_2()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		r, Q, cost = rq.r_q_eil_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 2.139704421358024e+02)
		self.assertAlmostEqual(Q, 3.185901810768729e+02)
		self.assertAlmostEqual(cost, 95.451140222851961)

	def test_problem_5_1a(self):
		"""Test that r_q_eil_approximation() function correctly solves Problem 5.1(a).
		"""
		print_status('TestrQEILApproximation', 'test_problem_5_1a()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		r, Q, cost = rq.r_q_eil_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 17.972649360167715)
		self.assertAlmostEqual(Q, 1.621231617283653e+02)
		self.assertAlmostEqual(cost, 5.311189321826714e+02)

	def test_problem_5_3a(self):
		"""Test that r_q_eil_approximation() function correctly solves Problem 5.3(a).
		"""
		print_status('TestrQEILApproximation', 'test_problem_5_3a()')

		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		annual_demand_mean = 192
		annual_demand_standard_deviation = 17.4
		lead_time = 3

		r, Q, cost = rq.r_q_eil_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time, tol=1e-6)
		self.assertAlmostEqual(r, 6.448385303830128e+02)
		self.assertAlmostEqual(Q, 4.007559793125993e+02)
		self.assertAlmostEqual(cost, 1.006273949347740e+02)


class TestrQEOQBApproximation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQEOQBApproximation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQEOQBApproximation', 'tear_down_class()')

	def test_example_5_4(self):
		"""Test that r_q_eoqb_approximation() function correctly solves Example 5.4.
		"""
		print_status('TestrQEOQBApproximation', 'test_example_5_4()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		r, Q = rq.r_q_eoqb_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 1.286378144242710e+02)
		self.assertAlmostEqual(Q, 3.085737801203754e+02)

	def test_problem_5_1b(self):
		"""Test that r_q_eoqb_approximation() function correctly solves Problem 5.1(b).
		"""
		print_status('TestrQEOQBApproximation', 'test_problem_5_1b()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		r, Q = rq.r_q_eoqb_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, -1.929822185100239)
		self.assertAlmostEqual(Q, 1.660850065197970e+02)

	def test_problem_5_3b(self):
		"""Test that r_q_eoqb_approximation() function correctly solves Problem 5.3(b).
		"""
		print_status('TestrQEOQBApproximation', 'test_problem_5_3b()')

		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		annual_demand_mean = 192
		annual_demand_standard_deviation = 17.4
		lead_time = 3

		r, Q = rq.r_q_eoqb_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 6.090252058220594e+02)
		self.assertAlmostEqual(Q, 3.913259510944808e+02)


class TestrQEOQSSApproximation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQEOQSSApproximation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQEOQSSApproximation', 'tear_down_class()')

	def test_example_5_5(self):
		"""Test that r_q_eoqss_approximation() function correctly solves Example 5.5.
		"""
		print_status('TestrQEOQSSApproximation', 'test_example_5_5()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		r, Q = rq.r_q_eoqss_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 1.903369965715624e+02)
		self.assertAlmostEqual(Q, 3.040467800264368e+02)

	def test_problem_5_1c(self):
		"""Test that r_q_eoqss_approximation() function correctly solves Problem 5.1(c).
		"""
		print_status('TestrQEOQSSApproximation', 'test_problem_5_1c()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		r, Q = rq.r_q_eoqss_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 15.125515371852014)
		self.assertAlmostEqual(Q, 1.606438657804998e+02)

	def test_problem_5_3c(self):
		"""Test that r_q_eoqb_approximation() function correctly solves Problem 5.3(c).
		"""
		print_status('TestrQEOQSSApproximation', 'test_problem_5_3c()')

		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		annual_demand_mean = 192
		annual_demand_standard_deviation = 17.4
		lead_time = 3

		r, Q = rq.r_q_eoqss_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 6.529638947041127e+02)
		self.assertAlmostEqual(Q, 3.902819493648150e+02)


class TestrQLossFunctionApproximation(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQLossFunctionApproximation', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQLossFunctionApproximation', 'tear_down_class()')

	def test_example_5_6(self):
		"""Test that r_q_loss_function_approximation() function correctly solves Example 5.6.
		"""
		print_status('TestrQLossFunctionApproximation', 'test_example_5_6()')

		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		annual_demand_mean = 1300
		annual_demand_standard_deviation = 150
		lead_time = 1/12

		r, Q = rq.r_q_loss_function_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 1.268670642878315e+02, places=5)
		self.assertAlmostEqual(Q, 3.284491413581765e+02, places=5)

	def test_problem_5_1d(self):
		"""Test that r_q_loss_function_approximation() function correctly solves Problem 5.1(d).
		"""
		print_status('TestrQLossFunctionApproximation', 'test_problem_5_1d()')

		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		annual_demand_mean = 800
		annual_demand_standard_deviation = 40
		lead_time = 4/365

		r, Q = rq.r_q_loss_function_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, -1.985868645048718, places=5)
		self.assertAlmostEqual(Q, 1.669501022040942e+02, places=5)

	def test_problem_5_3d(self):
		"""Test that r_q_loss_function_approximation() function correctly solves Problem 5.3(d).
		"""
		print_status('TestrQLossFunctionApproximation', 'test_problem_5_3d()')

		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		annual_demand_mean = 192
		annual_demand_standard_deviation = 17.4
		lead_time = 3

		r, Q = rq.r_q_loss_function_approximation(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, annual_demand_standard_deviation,
						   lead_time)
		self.assertAlmostEqual(r, 6.085445118000358e+02, places=4)
		self.assertAlmostEqual(Q, 4.038060023373138e+02, places=4)


class TestrQCostPoisson(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQCostPoisson', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQCostPoisson', 'tear_down_class()')

	def test_example_5_8(self):
		"""Test that r_q_cost_poisson() function correctly evaluates cost in
		Example 5.8.
		"""
		print_status('TestrQCostPoisson', 'test_example_5_8()')

		holding_cost = 20
		stockout_cost = 150
		fixed_cost = 100
		annual_demand_mean = 1.5
		lead_time = 2

		cost = rq.r_q_cost_poisson(3, 5, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertAlmostEqual(cost, 1.079235806331498e+02)

		cost = rq.r_q_cost_poisson(8, 12, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertAlmostEqual(cost, 2.425281637662021e+02)

	def test_problem_5_2(self):
		"""Test that r_q_cost_poisson() function correctly evaluates cost in Problem 5.2.
		"""
		print_status('TestrQCostPoisson', 'test_problem_5_2()')

		holding_cost = 4
		stockout_cost = 28
		fixed_cost = 4
		annual_demand_mean = 12
		lead_time = 0.5

		cost = rq.r_q_cost_poisson(6, 7, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertAlmostEqual(cost, 28.241312842169155)

		cost = rq.r_q_cost_poisson(3, 9, holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertAlmostEqual(cost, 34.264154469469503)


class TestrQPoissonExact(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestrQPoissonExact', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestrQPoissonExact', 'tear_down_class()')

	def test_example_5_8(self):
		"""Test that r_q_poisson_exact() function correctly solves Example 5.8.
		"""
		print_status('TestrQPoissonExact', 'test_example_5_8()')

		holding_cost = 20
		stockout_cost = 150
		fixed_cost = 100
		annual_demand_mean = 1.5
		lead_time = 2

		r, Q, cost = rq.r_q_poisson_exact(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertEqual(r, 3)
		self.assertEqual(Q, 5)
		self.assertAlmostEqual(cost, 1.079235806331498e+02)

	def test_problem_5_2(self):
		"""Test that r_q_cost_poisson() function correctly solves Problem 5.2.
		"""
		print_status('TestrQCostPoisson', 'test_problem_5_2()')

		holding_cost = 4
		stockout_cost = 28
		fixed_cost = 4
		annual_demand_mean = 12
		lead_time = 0.5

		r, Q, cost = rq.r_q_poisson_exact(holding_cost, stockout_cost, fixed_cost,
						   annual_demand_mean, lead_time)
		self.assertEqual(r, 6)
		self.assertEqual(Q, 7)
		self.assertAlmostEqual(cost, 28.241312842169155)

