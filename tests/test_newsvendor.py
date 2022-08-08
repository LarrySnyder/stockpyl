import unittest

import numpy as np
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import lognorm

import stockpyl.newsvendor as newsvendor
from stockpyl.instances import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_newsvendor   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestNewsvendorNormal(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorNormal', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorNormal', 'tear_down_class()')

	def test_example_4_3(self):
		"""Test that newsvendor_normal function correctly solves Example 4.3.
		"""
		print_status('TestNewsvendorNormal', 'test_example_4_3()')

		instance = load_instance("example_4_3")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 56.603955927433887)
		self.assertAlmostEqual(cost, 1.997605193176645)

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, base_stock_level=40)
		self.assertAlmostEqual(base_stock_level, 40)
		self.assertAlmostEqual(cost, 7.356131552870388)

	def test_problem_4_1(self):
		"""Test that newsvendor_normal function correctly solves Problem 4.1.
		"""
		print_status('TestNewsvendorNormal', 'test_problem_4_1()')

		instance = load_instance("problem_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(base_stock_level, 9.227214038234755e+02)
		self.assertAlmostEqual(cost, 2.718196781782411e+03)

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, base_stock_level=1040)
		self.assertAlmostEqual(base_stock_level, 1040)
		self.assertAlmostEqual(cost, 6.044298415188692e+03)

	def test_example_4_4(self):
		"""Test that newsvendor_normal function correctly solves the first
		part of Example 4.4 (L=4, R=1).
		"""
		print_status('TestNewsvendorNormal', 'test_example_4_4()')

		instance = load_instance("example_4_4")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		lead_time = instance['lead_time']

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, lead_time=lead_time)
		self.assertAlmostEqual(base_stock_level, 2.647668943741548e+02)
		self.assertAlmostEqual(cost, 4.466781004149578)

		base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd, lead_time=lead_time, base_stock_level=180)
		self.assertAlmostEqual(base_stock_level, 180)
		self.assertAlmostEqual(cost, 49.000164748034095)

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
		with self.assertRaises(ValueError):
			base_stock_level, cost = newsvendor.newsvendor_normal(holding_cost, stockout_cost, demand_mean, demand_sd)


class TestNewsvendorNormalCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorNormalCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorNormalCost', 'tear_down_class()')

	def test_example_4_3(self):
		"""Test that newsvendor_normal_cost function correctly evaluates cost for
		Example 4.3.
		"""
		print_status('TestNewsvendorNormalCost', 'test_example_4_3()')

		instance = load_instance("example_4_3")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		cost = newsvendor.newsvendor_normal_cost(40, holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(cost, 7.356131552870388)

		cost = newsvendor.newsvendor_normal_cost(60, holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(cost, 2.156131552870387)

		cost = newsvendor.newsvendor_normal_cost(120, holding_cost, stockout_cost, demand_mean, demand_sd, lead_time=3)
		self.assertAlmostEqual(cost, 56.000000752740092)

	def test_problem_4_1(self):
		"""Test that newsvendor_normal_cost function correctly evaluates cost for Problem 4.1.
		"""
		print_status('TestNewsvendorNormalCost', 'test_problem_4_1()')

		instance = load_instance("problem_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		cost = newsvendor.newsvendor_normal_cost(1100, holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(cost, 8.600820410122849e+03)

		cost = newsvendor.newsvendor_normal_cost(922, holding_cost, stockout_cost, demand_mean, demand_sd)
		self.assertAlmostEqual(cost, 2.718393552026199e+03)

		cost = newsvendor.newsvendor_normal_cost(4000, holding_cost, stockout_cost, demand_mean, demand_sd, lead_time=3)
		self.assertAlmostEqual(cost, 1.720164082024570e+04)


class TestNewsvendorPoisson(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorPoisson', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorPoisson', 'tear_down_class()')

	def test_example_4_7(self):
		"""Test that newsvendor_poisson function correctly solves Example 4.7
		(without fixed cost).
		"""
		print_status('TestNewsvendorPoisson', 'test_example_4_7()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean)
		self.assertEqual(base_stock_level, 8)
		self.assertAlmostEqual(cost, 3.570106945770946)

		base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean, base_stock_level=5)
		self.assertEqual(base_stock_level, 5)
		self.assertAlmostEqual(cost, 6.590296024616344)

	def test_problem_4_8a(self):
		"""Test that newsvendor_poisson function correctly solves Problem 4.8a.
		"""
		print_status('TestNewsvendorPoisson', 'test_problem_4_8a()')

		instance = load_instance("problem_4_8a")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean)
		self.assertEqual(base_stock_level, 19)
		self.assertAlmostEqual(cost, 7.860884409351115e+02)

		base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean, base_stock_level=13)
		self.assertAlmostEqual(base_stock_level, 13)
		self.assertAlmostEqual(cost, 1.445751062891969e+03)

	def test_bad_type(self):
		"""Test that newsvendor_poisson function raises exception on bad type.
		"""
		print_status('TestNewsvendorPoinsson', 'test_bad_type()')

		holding_cost = "taco"
		stockout_cost = 0.7
		demand_mean = 50
		with self.assertRaises(TypeError):
			base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean)

	def test_negative_parameter(self):
		"""Test that newsvendor_poisson function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorPoisson', 'test_negative_parameter()')

		holding_cost = -2
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(ValueError):
			base_stock_level, cost = newsvendor.newsvendor_poisson(holding_cost, stockout_cost, demand_mean)


class TestNewsvendorPoissonCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorPoissonCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorPoissonCost', 'tear_down_class()')

	def test_example_4_7(self):
		"""Test that newsvendor_poisson_cost function correctly evaluates cost for
		Example 4.7 (without fixed cost).
		"""
		print_status('TestNewsvendorPoissonCost', 'test_example_4_7()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		cost = newsvendor.newsvendor_poisson_cost(8, holding_cost, stockout_cost, demand_mean)
		self.assertAlmostEqual(cost, 3.570106945770946)

		cost = newsvendor.newsvendor_poisson_cost(5, holding_cost, stockout_cost, demand_mean)
		self.assertAlmostEqual(cost, 6.590296024616344)

	def test_problem_4_8a(self):
		"""Test that newsvendor_poisson_cost function correctly evaluates cost for
		Problem 4.8a.
		"""
		print_status('TestNewsvendorPoissonCost', 'test_problem_4_8a()')

		instance = load_instance("problem_4_8a")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		cost = newsvendor.newsvendor_poisson_cost(19, holding_cost, stockout_cost, demand_mean)
		self.assertAlmostEqual(cost, 7.860884409351115e+02)

		cost = newsvendor.newsvendor_poisson_cost(13, holding_cost, stockout_cost, demand_mean)
		self.assertAlmostEqual(cost, 1.445751062891969e+03)


class TestNewsvendorContinuous(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorContinuous', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorContinuous', 'tear_down_class()')

	def test_example_4_1_with_distrib(self):
		"""Test that newsvendor_continuous function correctly solves Example 4.1
		when provided with rv_continuous object.
		"""
		print_status('TestNewsvendorContinuous', 'test_example_4_1_with_distrib()')

		instance = load_instance("example_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		demand_distrib = norm(demand_mean, demand_sd)

		base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib)
		self.assertAlmostEqual(base_stock_level, 56.603955927433887)
		self.assertAlmostEqual(cost, 1.997605193176645, places=5)

		base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib, base_stock_level=40)
		self.assertAlmostEqual(base_stock_level, 40)
		self.assertAlmostEqual(cost, 7.356131552870388, places=5)

	def test_example_4_1_with_pdf(self):
		"""Test that newsvendor_continuous function correctly solves Example 4.1
		when provided with pdf function.
		"""
		print_status('TestNewsvendorContinuous', 'test_example_4_1_with_pdf()')

	def test_problem_4_8b(self):
		"""Test that newsvendor_continuous function correctly solves Problem
		4.8(b).
		"""
		print_status('TestNewsvendorContinuous', 'test_problem_4_8b()')

		instance = load_instance("problem_4_8b")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		mu = instance['mu']
		sigma = instance['sigma']

		demand_distrib = lognorm(sigma, 0, np.exp(mu))

		base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib)
		self.assertAlmostEqual(base_stock_level, 2.956266448071368e+02)
		self.assertAlmostEqual(cost, 29.442543582135290, places=5)

		base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib, base_stock_level=350)
		self.assertAlmostEqual(base_stock_level, 350)
		self.assertAlmostEqual(cost, 34.588836685654854, places=5)

	def test_bad_type(self):
		"""Test that newsvendor_continuous function raises exception on bad type.
		"""
		print_status('TestNewsvendorContinuous', 'test_bad_type()')

		holding_cost = "taco"
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8

		demand_distrib = norm(demand_mean, demand_sd)

		with self.assertRaises(TypeError):
			base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib)

	def test_negative_parameter(self):
		"""Test that newsvendor_continuous function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorContinuous', 'test_negative_parameter()')

		holding_cost = -2
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8

		demand_distrib = norm(demand_mean, demand_sd)

		with self.assertRaises(ValueError):
			base_stock_level, cost = newsvendor.newsvendor_continuous(holding_cost, stockout_cost, demand_distrib)


class TestNewsvendorDiscrete(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorDiscrete', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorDiscrete', 'tear_down_class()')

	def test_example_4_7_with_distrib(self):
		"""Test that newsvendor_discrete function correctly solves Example 4.7
		(without fixed cost) when provided with rv_discrete object.
		"""
		print_status('TestNewsvendorDiscrete', 'test_example_4_7_with_distrib()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		demand_distrib = poisson(demand_mean)

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_distrib)
		self.assertEqual(base_stock_level, 8)
		self.assertAlmostEqual(cost, 3.570106945770946)

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_distrib, base_stock_level=5)
		self.assertEqual(base_stock_level, 5)
		self.assertAlmostEqual(cost, 6.590296024616344)

	def test_example_4_7_with_pmf(self):
		"""Test that newsvendor_discrete function correctly solves Example 4.7
		(without fixed cost) when provided with pmf dict.
		"""
		print_status('TestNewsvendorDiscrete', 'test_example_4_7_with_pmf()')

		instance = load_instance("example_4_7")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']

		d = range(0, 41)
		f = [poisson.pmf(d_val, demand_mean) for d_val in d]
		demand_pmf = dict(zip(d, f))

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_pmf=demand_pmf)
		self.assertEqual(base_stock_level, 8)
		self.assertAlmostEqual(cost, 3.570106945770946)

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_pmf=demand_pmf, base_stock_level=5)
		self.assertEqual(base_stock_level, 5)
		self.assertAlmostEqual(cost, 6.590296024616344)

	def test_problem_4_7b(self):
		"""Test that newsvendor_discrete function correctly solves Problem 4.7(b).
		"""
		print_status('TestNewsvendorDiscrete', 'test_problem_4_7b()')

		instance = load_instance("problem_4_7b")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_pmf = instance['demand_pmf']

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_pmf=demand_pmf)
		self.assertEqual(base_stock_level, 5)
		self.assertAlmostEqual(cost, 1225000)

		base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_pmf=demand_pmf, base_stock_level=3)
		self.assertAlmostEqual(base_stock_level, 3)
		self.assertAlmostEqual(cost, 1.725000000000000e+06)

	def test_bad_type(self):
		"""Test that newsvendor_normal function raises exception on bad type.
		"""
		print_status('TestNewsvendorDiscrete', 'test_bad_type()')

		holding_cost = "taco"
		stockout_cost = 4
		demand_mean = 6

		demand_distrib = poisson(demand_mean)

		with self.assertRaises(TypeError):
			base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_mean, demand_distrib)

	def test_negative_parameter(self):
		"""Test that newsvendor_normal function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorDiscrete', 'test_negative_parameter()')

		holding_cost = -4
		stockout_cost = 4
		demand_mean = 6

		demand_distrib = poisson(demand_mean)

		with self.assertRaises(ValueError):
			base_stock_level, cost = newsvendor.newsvendor_discrete(holding_cost, stockout_cost, demand_mean, demand_distrib)


class TestMyopic(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMyopic', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMyopic', 'tear_down_class()')

	def test_example_4_1(self):
		"""Test that myopic function correctly solves Example 4.1 (plus other
		parameters).
		"""
		print_status('TestMyopic', 'test_example_4_1()')

		instance = load_instance("example_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 0.3
		purchase_cost_next_per = 0.35
		discount_factor = 0.98

		base_stock_level, cost = newsvendor.myopic(holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(base_stock_level, 58.09891883213067)
		self.assertAlmostEqual(cost, 16.682411764618777)

		base_stock_level, cost = newsvendor.myopic(holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor, base_stock_level=62)
		self.assertEqual(base_stock_level, 62)
		self.assertAlmostEqual(cost, 16.850319828088736)

	def test_problem_4_1(self):
		"""Test that myopic function correctly solves Problem 4.1 (plus
		other parameters).
		"""
		print_status('TestMyopicCost', 'test_problem_4_1()')

		instance = load_instance("problem_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 65
		purchase_cost_next_per = 55
		discount_factor = 0.9

		base_stock_level, cost = newsvendor.myopic(holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(base_stock_level, 903.0832764843523)
		self.assertAlmostEqual(cost, 61416.404244990816)

		base_stock_level, cost = newsvendor.myopic(holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor, base_stock_level=950)
		self.assertEqual(base_stock_level, 950)
		self.assertAlmostEqual(cost, 62254.39180412519)


class TestMyopicCost(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMyopicCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMyopicCost', 'tear_down_class()')

	def test_example_4_1(self):
		"""Test that myopic_cost function correctly evaluates cost for
		parameters in Example 4.1 (plus others).
		"""
		print_status('TestMyopicCost', 'test_example_4_1()')

		instance = load_instance("example_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 0.3
		purchase_cost_next_per = 0.4
		discount_factor = 0.98

		cost = newsvendor.myopic_cost(60, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 16.236131552870390)

		cost = newsvendor.myopic_cost(40, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 23.276131552870389)

		cost = newsvendor.myopic_cost(120, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 21.160000000000000)

		cost = newsvendor.myopic_cost(56.6, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 16.390405437438364)

	def test_problem_4_1(self):
		"""Test that myopic_cost function correctly evaluates cost for
		parameters in Problem 4.1 (plus others).
		"""
		print_status('TestMyopicCost', 'test_problem_4_1()')

		instance = load_instance("problem_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 65
		purchase_cost_next_per = 55
		discount_factor = 0.9

		cost = newsvendor.myopic_cost(900, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 6.142025749253849e+04)

		cost = newsvendor.myopic_cost(1150, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 7.312502466917748e+04)

		cost = newsvendor.myopic_cost(650, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 7.437502466917748e+04)

		cost = newsvendor.myopic_cost(2400, holding_cost, stockout_cost, purchase_cost,
									  purchase_cost_next_per, demand_mean, demand_sd,
									  discount_factor)
		self.assertAlmostEqual(cost, 146250)


class TestSetMyopicCostTo(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSetMyopicCostTo', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSetMyopicCostTo', 'tear_down_class()')

	def test_example_4_1(self):
		"""Test that set_myopic_cost_to function correctly calculates
		values for Example 4.1.
		"""
		print_status('TestSetMyopicCostTo', 'test_example_4_3()')

		instance = load_instance("example_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 0.3
		purchase_cost_next_per = 0.4
		discount_factor = 0.98

		c_plus = purchase_cost - discount_factor * purchase_cost_next_per
		critical_ratio = \
			(stockout_cost - c_plus) / (stockout_cost + holding_cost)
		S_underbar = norm.ppf(critical_ratio, demand_mean, demand_sd)

		base_stock_level = newsvendor.set_myopic_cost_to(17, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 True)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 17)
		self.assertLessEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(17, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 False)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 17)
		self.assertGreaterEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(22, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 True)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 22)
		self.assertLessEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(22, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 False)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 22)
		self.assertGreaterEqual(base_stock_level, S_underbar)

	def test_problem_4_1(self):
		"""Test that set_myopic_cost_to function correctly calculates
		values for Problem 4.1.
		"""
		print_status('TestSetMyopicCostTo', 'test_problem_4_1()')

		instance = load_instance("problem_4_1")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 65
		purchase_cost_next_per = 55
		discount_factor = 0.9

		c_plus = purchase_cost - discount_factor * purchase_cost_next_per
		critical_ratio = \
			(stockout_cost - c_plus) / (stockout_cost + holding_cost)
		S_underbar = norm.ppf(critical_ratio, demand_mean, demand_sd)

		base_stock_level = newsvendor.set_myopic_cost_to(72000, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 True)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 72000)
		self.assertLessEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(72000, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 False)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 72000)
		self.assertGreaterEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(120000, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 True)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 120000)
		self.assertLessEqual(base_stock_level, S_underbar)

		base_stock_level = newsvendor.set_myopic_cost_to(120000, holding_cost,
														 stockout_cost,
														 purchase_cost,
														 purchase_cost_next_per,
														 demand_mean,
														 demand_sd,
														 discount_factor,
														 False)
		self.assertAlmostEqual(newsvendor.myopic_cost(base_stock_level,
													  holding_cost,
													  stockout_cost,
													  purchase_cost,
													  purchase_cost_next_per,
													  demand_mean,
													  demand_sd,
													  discount_factor), 120000)
		self.assertGreaterEqual(base_stock_level, S_underbar)

	def test_cost_too_small(self):
		"""Test that set_myopic_cost_to function correctly raises an error
		when the desired cost is smaller than the optimal cost.
		"""
		print_status('TestSetMyopicCostTo', 'test_cost_too_small()')

		instance = load_instance("example_4_3")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 0.3
		purchase_cost_next_per = 0.4
		discount_factor = 0.98

		c_plus = purchase_cost - discount_factor * purchase_cost_next_per
		critical_ratio = \
			(stockout_cost - c_plus) / (stockout_cost + holding_cost)
		S_underbar = norm.ppf(critical_ratio, demand_mean, demand_sd)
		G_S_underbar = newsvendor.myopic_cost(S_underbar, holding_cost, stockout_cost,
											  purchase_cost, purchase_cost_next_per,
											  demand_mean, demand_sd, discount_factor)

		with self.assertRaises(ValueError):
			base_stock_level = newsvendor.set_myopic_cost_to(0.9 * G_S_underbar,
															 holding_cost,
															 stockout_cost,
															 purchase_cost,
															 purchase_cost_next_per,
															 demand_mean,
															 demand_sd,
															 discount_factor,
															 False)

	def test_bad_c_plus(self):
		"""Test that set_myopic_cost_to function correctly raises an error
		when c_plus is outside of its bounds.
		"""
		print_status('TestSetMyopicCostTo', 'test_bad_c_plus()')

		instance = load_instance("example_4_3")
		holding_cost = instance['holding_cost']
		stockout_cost = instance['stockout_cost']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']
		purchase_cost = 0.3
		purchase_cost_next_per = 0.8
		discount_factor = 0.95

		with self.assertRaises(ValueError):
			base_stock_level = newsvendor.set_myopic_cost_to(17,
															 holding_cost,
															 stockout_cost,
															 purchase_cost,
															 purchase_cost_next_per,
															 demand_mean,
															 demand_sd,
															 discount_factor,
															 False)

		purchase_cost = 2
		purchase_cost_next_per = 0.2

		with self.assertRaises(ValueError):
			base_stock_level = newsvendor.set_myopic_cost_to(17,
															 holding_cost,
															 stockout_cost,
															 purchase_cost,
															 purchase_cost_next_per,
															 demand_mean,
															 demand_sd,
															 discount_factor,
															 False)


class TestNewsvendorNormalExplicit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorNormalExplicit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorNormalExplicit', 'tear_down_class()')

	def test_example_4_2(self):
		"""Test that newsvendor_normal_explicit function correctly solves Example 4.2.
		"""
		print_status('TestNewsvendorNormalExplicit', 'test_example_4_2()')

		instance = load_instance("example_4_2")
		revenue = instance['revenue']
		purchase_cost = instance['purchase_cost']
		salvage_value = instance['salvage_value']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, 0, 0)
		self.assertAlmostEqual(base_stock_level, 56.603955927433887)
		self.assertAlmostEqual(profit, 33.002394806823354)

		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, 0, 0, \
									base_stock_level=40)
		self.assertAlmostEqual(base_stock_level, 40)
		self.assertAlmostEqual(profit, 27.643868447129613)

	def test_problem_4_3b(self):
		"""Test that newsvendor_normal_explicit function correctly solves Problem 4.3(b).
		"""
		print_status('TestNewsvendorNormalExplicit', 'test_problem_4_3b()')

		instance = load_instance("problem_4_3b")
		revenue = instance['revenue']
		purchase_cost = instance['purchase_cost']
		salvage_value = instance['salvage_value']
		demand_mean = instance['demand_mean']
		demand_sd = instance['demand_sd']

		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, 0, 0)
		self.assertAlmostEqual(base_stock_level, 59.084578685373856)
		self.assertAlmostEqual(profit, 2.104768082523147e+02)

		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, 0, 0, \
									base_stock_level=62)
		self.assertAlmostEqual(base_stock_level, 62)
		self.assertAlmostEqual(profit, 2.099143652105560e+02)

		# Add a holding and stockout cost, and test again.
		holding_cost = 1
		stockout_cost = 5
		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, holding_cost, stockout_cost)
		self.assertAlmostEqual(base_stock_level, 59.388143168769034)
		self.assertAlmostEqual(profit, 1.954729310431908e+02)

		base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, demand_sd, holding_cost, stockout_cost, \
									base_stock_level=62)
		self.assertAlmostEqual(base_stock_level, 62)
		self.assertAlmostEqual(profit, 1.945482181675262e+02)

	def test_bad_type(self):
		"""Test that newsvendor_normal_explicit function raises exception on bad type.
		"""
		print_status('TestNewsvendorNormalExplicit', 'test_bad_type()')

		revenue = "taco"
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(TypeError):
			base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, purchase_cost,
				salvage_value, demand_mean, demand_sd, 0, 0)

	def test_negative_parameter(self):
		"""Test that newsvendor_normal_explicit function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorNormalExplicit', 'test_negative_parameter()')

		revenue = -4
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(ValueError):
			base_stock_level, profit = newsvendor.newsvendor_normal_explicit(revenue, purchase_cost,
				salvage_value, demand_mean, demand_sd, 0, 0)


class TestNewsvendorPoissonExplicit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorPoissonExplicit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorPoissonExplicit', 'tear_down_class()')

	def test_example_4_2(self):
		"""Test that newsvendor_poisson_explicit function correctly solves Example 4.2
		with Poisson demand.
		"""
		print_status('TestNewsvendorPoissonExplicit', 'test_example_4_2()')

		instance = load_instance("example_4_2")
		revenue = instance['revenue']
		purchase_cost = instance['purchase_cost']
		salvage_value = instance['salvage_value']
		demand_mean = instance['demand_mean']

		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, 0, 0)
		self.assertEqual(base_stock_level, 56)
		self.assertAlmostEqual(profit, 33.20276478819082)

		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, 0, 0, \
									base_stock_level=40)
		self.assertEqual(base_stock_level, 40)
		self.assertAlmostEqual(profit, 27.811432228377633)

		

	def test_problem_4_3b(self):
		"""Test that newsvendor_poisson_explicit function correctly solves Problem 4.3(b) 
		with Poisson demand.
		"""
		print_status('TestNewsvendorPoissonExplicit', 'test_problem_4_3b()')

		instance = load_instance("problem_4_3b")
		revenue = instance['revenue']
		purchase_cost = instance['purchase_cost']
		salvage_value = instance['salvage_value']
		demand_mean = instance['demand_mean']

		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, 0, 0)
		self.assertEqual(base_stock_level, 56)
		self.assertAlmostEqual(profit, 214.51727992619263)

		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, 0, 0, \
									base_stock_level=62)
		self.assertEqual(base_stock_level, 62)
		self.assertAlmostEqual(profit, 212.1430953089244)

		# Add a holding and stockout cost, and test again.
		holding_cost = 1
		stockout_cost = 5
		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, holding_cost, stockout_cost)
		self.assertEqual(base_stock_level, 57)
		self.assertAlmostEqual(profit, 203.67269269293658)

		base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, \
									purchase_cost, salvage_value, demand_mean, holding_cost, stockout_cost, \
									base_stock_level=62)
		self.assertEqual(base_stock_level, 62)
		self.assertAlmostEqual(profit, 199.20829019138736)

	def test_bad_type(self):
		"""Test that newsvendor_poisson_explicit function raises exception on bad type.
		"""
		print_status('TestNewsvendorPoissonExplicit', 'test_bad_type()')

		revenue = "taco"
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		with self.assertRaises(TypeError):
			base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, purchase_cost,
				salvage_value, demand_mean, 0, 0)

	def test_negative_parameter(self):
		"""Test that newsvendor_poisson_explicit function raises exception on negative parameter.
		"""
		print_status('TestNewsvendorPoissonExplicit', 'test_negative_parameter()')

		revenue = -4
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		demand_sd = 8
		with self.assertRaises(ValueError):
			base_stock_level, profit = newsvendor.newsvendor_poisson_explicit(revenue, purchase_cost,
				salvage_value, demand_mean, 0, 0)
