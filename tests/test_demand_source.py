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


class TestDemandSourceParameters(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandSourceParameters', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandSourceParameters', 'tear_down_class()')

	def test_normal(self):
		"""Test that DemandSourceNormal correctly raises errors on invalid parameters.
		"""
		print_status('TestDemandSourceParameters', 'test_normal()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		with self.assertRaises(AssertionError):
			demand_source.mean = -100

		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		with self.assertRaises(AssertionError):
			demand_source.standard_deviation = -100

	def test_init_uniform_discrete(self):
		"""Test that DemandSourceUniformDiscrete correctly raises errors on invalid parameters.
		"""
		print_status('TestDemandSourceParameters', 'test_init_uniform_discrete()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		with self.assertRaises(AssertionError):
			demand_source.lo = -100

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		with self.assertRaises(AssertionError):
			demand_source.hi = -100

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		with self.assertRaises(AssertionError):
			demand_source.lo = 3.8

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		with self.assertRaises(AssertionError):
			demand_source.hi = 7.9

	def test_init_uniform_continuous(self):
		"""Test that DemandSourceUniformContinuous correctly raises errors on invalid parameters.
		"""
		print_status('TestDemandSourceParameters', 'test_init_uniform_continuous()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		with self.assertRaises(AssertionError):
			demand_source.lo = -100

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		with self.assertRaises(AssertionError):
			demand_source.hi = -100

	def test_init_discrete_explicit(self):
		"""Test that DemandSourceDiscreteExplicit correctly raises errors on invalid parameters.
		"""
		print_status('TestDemandSourceInit', 'TestDemandSourceParameters()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		with self.assertRaises(AssertionError):
			demand_source.probabilities = [0.2, 0.5, 0.2]


class TestDemandSourceRepr(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandSourceRepr', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandSourceRepr', 'tear_down_class()')

	def test_none(self):
		"""Test that DemandSourceNone.__repr__() correctly returns demand source string.
		"""
		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.NONE)
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(NONE)")

	def test_normal(self):
		"""Test that DemandSourceNormal.__repr__() correctly returns demand source string.
		"""
		print_status('TestDemandSourceRepr', 'test_normal()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		demand_source.mean = 50
		demand_source.standard_deviation = 8
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(NORMAL: mean=50.00, standard_deviation=8.00)")

	def test_uniform_discrete(self):
		"""Test that DemandSourceUniformDiscrete.__repr__() correctly returns demand source string.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_discrete()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		demand_source.lo = 50
		demand_source.hi = 80
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UNIFORM_DISCRETE: lo=50.00, hi=80.00)")

	def test_uniform_continuous(self):
		"""Test that DemandSourceUniformContinuous.__repr__() correctly returns demand source string.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_continuous()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 50
		demand_source.hi = 80
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UNIFORM_CONTINUOUS: lo=50.00, hi=80.00)")

	def test_deterministic(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		deterministic demands.
		"""
		print_status('TestDemandSourceRepr', 'test_deterministic()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = 5
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demands=5)")

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = [5, 4, 3]
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demands=[5, 4, 3])")

	def test_discrete_explicit(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		discrete explicit demands.
		"""
		print_status('TestDemandSourceRepr', 'test_discrete_explicit()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		demand_source.demands = [5, 4, 3]
		demand_source.probabilities = [0.2, 0.5, 0.3]
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DISCRETE_EXPLICIT: demands=[5, 4, 3], probabilities=[0.2, 0.5, 0.3])")


class TestGenerateDemand(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGenerateDemand', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGenerateDemand', 'tear_down_class()')

	def test_normal(self):
		"""Test that generate_demand() returns valid demand values for normal demands.
		"""
		print_status('TestGenerateDemand', 'test_normal()')

		demand_source_factory = DemandSourceFactory()

		# Check for correct errors.
		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		demand_source.mean = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		demand_source.standard_deviation = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()

	def test_uniform_discrete(self):
		"""Test that generate_demand() returns valid demand values for discrete uniform demands.
		"""
		print_status('TestGenerateDemand', 'test_uniform_discrete()')

		demand_source_factory = DemandSourceFactory()

		# Check for correct errors.
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		demand_source.lo = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		demand_source.hi = 12
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		demand_source.lo = 12
		demand_source.hi = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()

		# Check for correct demand values.
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_DISCRETE)
		demand_source.lo = 4
		demand_source.hi = 12
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d >= 4, d <= 12)

	def test_uniform_continuous(self):
		"""Test that generate_demand() returns valid demand values for continuous uniform demands.
		"""
		print_status('TestGenerateDemand', 'test_uniform_continuous()')

		demand_source_factory = DemandSourceFactory()

		# Check for correct errors.
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.hi = 12
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 12
		demand_source.hi = 4
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()

		# Check for correct demand values.
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 4
		demand_source.hi = 12
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d >= 4, d <= 12)

	def test_deterministic(self):
		"""Test that generate_demand() returns valid demand values for deterministic demands.
		"""
		print_status('TestGenerateDemand', 'test_deterministic()')

		demand_source_factory = DemandSourceFactory()

		# Check for correct errors.
		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()

		# Check for correct demand values.
		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = 5
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = [5, 4, 3, 2]
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = [5, 4, 3, 2]
		d = demand_source.generate_demand(period=2)
		self.assertEqual(d, 3)

	def test_discrete_explicit(self):
		"""Test that generate_demand() returns valid demand values for discrete explicit demands.
		"""
		print_status('TestGenerateDemand', 'test_discrete_explicit()')

		demand_source_factory = DemandSourceFactory()

		# Check for correct errors.
		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		demand_source.demands = [5, 4, 3, 2]
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()
		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		demand_source.probabilities = [0.25, 0.25, 0.2, 0.3]
		with self.assertRaises(AssertionError):
			_ = demand_source.generate_demand()

		# Check for correct demand values.
		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		demand_source. demands = [5, 4, 3, 2]
		demand_source.probabilities = [0.25, 0.25, 0.2, 0.3]
		for _ in range(100):
			d = demand_source.generate_demand()
			self.assertTrue(d in (5, 4, 3, 2))


