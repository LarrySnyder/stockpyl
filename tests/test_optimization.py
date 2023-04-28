import unittest
import copy

import stockpyl.optimization as optimization
from stockpyl.instances import *
from stockpyl.newsvendor import *
import stockpyl.ssm_serial as ssm_serial


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_meio   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestGoldenSectionSearch(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGoldenSectionSearch', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGoldenSectionSearch', 'tear_down_class()')

	def test_quadratic(self):
		"""Test that golden_section_search() correctly optimizes (x-2)^2.
		"""
		print_status('TestGoldenSectionSearch', 'test_quadratic()')

		f = lambda x: (x - 2) ** 2

		x_star, f_star = optimization.golden_section_search(f, 1, 5)

		self.assertAlmostEqual(x_star, 2, places=5)
		self.assertAlmostEqual(f_star, 0, places=5)

	def test_example_4_1(self):
		"""Test that golden_section_search() correctly optimizes newsvendor
		cost function for Example 4.1.
		"""
		print_status('TestGoldenSectionSearch', 'test_example_4_1()')

		instance = load_instance("example_4_1")
		h = instance['holding_cost']
		p = instance['stockout_cost']
		mu = instance['demand_mean']
		sigma = instance['demand_sd']

		f = lambda S: newsvendor_normal_cost(S, h, p, mu, sigma)

		S_star, f_star = optimization.golden_section_search(f, 40, 60)

		self.assertAlmostEqual(S_star, 56.60395592743389, places=5)
		self.assertAlmostEqual(f_star, 1.9976051931766445, places=5)

	def test_example_6_1_S1(self):
		"""Test that golden_section_search() correctly optimizes S_1 in SSM serial
		objective function with other base-stock levels are fixed.
		"""
		print_status('TestGoldenSectionSearch', 'test_example_6_1_S1()')

		instance = copy.deepcopy(load_instance("example_6_1"))
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		f = lambda S1: ssm_serial.expected_cost({1: S1, 2: 12.02, 3: 22.71}, network=instance, x_num=100, d_num=10)

		S1_star, C_star = optimization.golden_section_search(f, 0, 12)

		self.assertAlmostEqual(S1_star, 6.899491709061081, places=1)
		self.assertAlmostEqual(C_star, 47.82, places=1)
