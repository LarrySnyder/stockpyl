import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from inventory.demand_source import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_demand_source   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestDemandSourceInit(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandSourceInit', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandSourceInit', 'tear_down_class()')

	def test_init_normal(self):
		"""Test that DemandSource.__init__() correctly raises errors on incorrect parameters for normal demands.
		"""
		print_status('TestDemandSourceInit', 'test_init_normal()')

		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.NORMAL, demand_mean=100)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.NORMAL, demand_standard_deviation=10)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.NORMAL, demand_mean=100, demand_standard_deviation=-10)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.NORMAL, demand_mean=-50, demand_standard_deviation=10)

	def test_init_uniform_discrete(self):
		"""Test that DemandSource.__init__() correctly raises errors on incorrect parameters for discrete uniform demands.
		"""
		print_status('TestDemandSourceInit', 'test_init_uniform_discrete()')

		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_hi=5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=5, demand_hi=-5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=-5, demand_hi=8)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=5.5, demand_hi=8)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=5, demand_hi=8.3)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=10, demand_hi=3)

	def test_init_uniform_continuous(self):
		"""Test that DemandSource.__init__() correctly raises errors on incorrect parameters for continuous uniform demands.
		"""
		print_status('TestDemandSourceInit', 'test_init_uniform_continuous()')

		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_hi=5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=5, demand_hi=-5)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=-5, demand_hi=8)
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=10, demand_hi=3)

	def test_init_deterministic(self):
		"""Test that DemandSource.__init__() correctly raises errors on incorrect parameters for deterministic demands.
		"""
		print_status('TestDemandSourceInit', 'test_init_deterministic()')

		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.DETERMINISTIC)

	def test_init_discrete_explicit(self):
		"""Test that DemandSource.__init__() correctly raises errors on incorrect parameters for discrete explicit demands.
		"""
		print_status('TestDemandSourceInit', 'test_init_discrete_explicit()')

		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demands=[5, 3, 2])
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demand_probabilities=[0.2, 0.5, 0.3])
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demands=[5, 3], demand_probabilities=[0.2, 0.5, 0.3])
		with self.assertRaises(AssertionError):
			_ = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demands=[5, 3, 2], demand_probabilities=[0.2, 0.5, 0.2])


class TestDemandSourceRepr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandSourceRepr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandSourceRepr', 'tear_down_class()')

	def test_normal(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		normal demands.
		"""
		print_status('TestDemandSourceRepr', 'test_normal()')

		demand_source = DemandSource(demand_type=DemandType.NORMAL, demand_mean=50, demand_standard_deviation=8)
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(NORMAL: demand_mean=50.00, demand_standard_deviation=8.00)")

	def test_uniform_discrete(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		discrete uniform demands.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_discrete()')

		demand_source = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=50, demand_hi=80)
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UNIFORM_DISCRETE: demand_lo=50.00, demand_hi=80.00)")

	def test_uniform_continuous(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		continuous uniform demands.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_continuous()')

		demand_source = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=50, demand_hi=80)
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UNIFORM_CONTINUOUS: demand_lo=50.00, demand_hi=80.00)")

	def test_deterministic(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		deterministic demands.
		"""
		print_status('TestDemandSourceRepr', 'test_deterministic()')

		demand_source = DemandSource(demand_type=DemandType.DETERMINISTIC, demands=5)
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demands=5)")

		demand_source = DemandSource(demand_type=DemandType.DETERMINISTIC, demands=[5, 4, 3])
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demands=[5, 4, 3])")

	def test_discrete_explicit(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		discrete explicit demands.
		"""
		print_status('TestDemandSourceRepr', 'test_discrete_explicit()')

		demand_source = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demands=[5, 4, 3], demand_probabilities=[0.2, 0.5, 0.3])
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DISCRETE_EXPLICIT: demands=[5, 4, 3], demand_probabilities=[0.2, 0.5, 0.3])")


class TestGenerateDemand(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGenerateDemand', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGenerateDemand', 'tear_down_class()')

	def test_uniform_discrete(self):
		"""Test that generate_demand() returns valid demand values for discrete uniform demands.
		"""
		print_status('TestGenerateDemand', 'test_uniform_discrete()')

		demand_source = DemandSource(demand_type=DemandType.UNIFORM_DISCRETE, demand_lo=4, demand_hi=12)
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d >= 4, d <= 12)

	def test_uniform_continuous(self):
		"""Test that generate_demand() returns valid demand values for continuous uniform demands.
		"""
		print_status('TestGenerateDemand', 'test_uniform_continuous()')

		demand_source = DemandSource(demand_type=DemandType.UNIFORM_CONTINUOUS, demand_lo=4, demand_hi=12)
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d >= 4, d <= 12)

	def test_deterministic(self):
		"""Test that generate_demand() returns valid demand values for deterministic demands.
		"""
		print_status('TestGenerateDemand', 'test_deterministic()')

		demand_source = DemandSource(demand_type=DemandType.DETERMINISTIC, demands=5)
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = DemandSource(demand_type=DemandType.DETERMINISTIC, demands=[5, 4, 3, 2])
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = DemandSource(demand_type=DemandType.DETERMINISTIC, demands=[5, 4, 3, 2])
		d = demand_source.generate_demand(period=2)
		self.assertEqual(d, 3)

	def test_discrete_explicit(self):
		"""Test that generate_demand() returns valid demand values for discrete explicit demands.
		"""
		print_status('TestGenerateDemand', 'test_discrete_explicit()')

		demand_source = DemandSource(demand_type=DemandType.DISCRETE_EXPLICIT, demands=[5, 4, 3, 2], demand_probabilities=[0.25, 0.25, 0.2, 0.3])
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d in (5, 4, 3, 2))


