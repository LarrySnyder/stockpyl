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
