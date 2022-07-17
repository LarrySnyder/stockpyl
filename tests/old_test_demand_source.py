import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from demand_source import *


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


class TestValidateParameters(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestValidateParameters', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestValidateParameters', 'tear_down_class()')

	def test_normal(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for normal distribution.
		"""
		print_status('TestValidateParameters', 'test_normal()')

		demand_source = DemandSource()
		demand_source.demand_type = 'N'
		demand_source.demand_mean = -100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'N'
		demand_source.demand_standard_deviation = -100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

	def test_uniform_discrete(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for uniform discrete distribution.
		"""
		print_status('TestValidateParameters', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.demand_type = 'UD'
		demand_source.demand_lo = -100
		demand_source.demand_hi = 100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UD'
		demand_source.demand_lo = 10
		demand_source.demand_hi = -100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UD'
		demand_source.demand_lo = 3.8
		demand_source.demand_hi = 100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UD'
		demand_source.demand_hi = 72.3
		demand_source.demand_lo = 50
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UD'
		demand_source.demand_lo = 50
		demand_source.demand_hi = 20
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

	def test_uniform_continuous(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for uniform continuous distribution.
		"""
		print_status('TestValidateParameters', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.demand_type = 'UC'
		demand_source.demand_lo = -100
		demand_source.demand_hi = 100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UC'
		demand_source.demand_lo = 10
		demand_source.demand_hi = -100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.demand_type = 'UC'
		demand_source.demand_lo = 50
		demand_source.demand_hi = 20
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

	def test_deterministic(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for deterministic distribution.
		"""
		print_status('TestValidateParameters', 'test_deterministic()')

		demand_source = DemandSource()
		demand_source.demand_type = 'D'
		demand_source.demand_lo = -100
		demand_source.demand_hi = 100
		with self.assertRaises(AssertionError):
			demand_source.validate_parameters()

	def test_init_discrete_explicit(self):
		"""Test that DemandSourceDiscreteExplicit correctly raises errors on invalid parameters.
		"""
		print_status('TestValidateParameters', 'TestDemandSourceParameters()')

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
		deterministic demand_list.
		"""
		print_status('TestDemandSourceRepr', 'test_deterministic()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = 5
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demand_list=5)")

		demand_source = demand_source_factory.build_demand_source(DemandType.DETERMINISTIC)
		demand_source.demands = [5, 4, 3]
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DETERMINISTIC: demand_list=[5, 4, 3])")

	def test_discrete_explicit(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string for
		discrete explicit demand_list.
		"""
		print_status('TestDemandSourceRepr', 'test_discrete_explicit()')

		demand_source_factory = DemandSourceFactory()

		demand_source = demand_source_factory.build_demand_source(DemandType.DISCRETE_EXPLICIT)
		demand_source.demands = [5, 4, 3]
		demand_source.probabilities = [0.2, 0.5, 0.3]
		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(DISCRETE_EXPLICIT: demand_list=[5, 4, 3], probabilities=[0.2, 0.5, 0.3])")


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
		"""Test that generate_demand() returns valid demand values for normal demand_list.
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
		"""Test that generate_demand() returns valid demand values for discrete uniform demand_list.
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
		"""Test that generate_demand() returns valid demand values for continuous uniform demand_list.
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
		"""Test that generate_demand() returns valid demand values for deterministic demand_list.
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
		"""Test that generate_demand() returns valid demand values for discrete explicit demand_list.
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


class TestDemandDistribution(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandDistribution', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandDistribution', 'tear_down_class()')

	def test_normal(self):
		"""Test demand_distribution() for normal demand_list.
		"""
		print_status('TestDemandDistribution', 'test_normal()')

		demand_source_factory = DemandSourceFactory()
		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		distribution = demand_source.demand_distribution()
#		a = distribution.a
#		b = distribution.b
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

#		self.assertEqual(a, float("-inf"))
#		self.assertEqual(b, float("inf"))
		self.assertEqual(mu, 50)
		self.assertEqual(sigma, 8)
		self.assertAlmostEqual(z, 58.291467115950319)

	def test_uniform_continuous(self):
		"""Test demand_distribution() for continuous uniform demand_list.
		"""
		print_status('TestDemandDistribution', 'test_uniform_continuous()')

		demand_source_factory = DemandSourceFactory()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 50
		demand_source.hi = 100

		distribution = demand_source.demand_distribution()
#		a = distribution.a
#		b = distribution.b
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

#		self.assertEqual(a, 50)
#		self.assertEqual(b, 100)
		self.assertEqual(mu, 75)
		self.assertAlmostEqual(sigma, 50 / math.sqrt(12))
		self.assertEqual(z, 92.5)


class TestCDF(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCDF', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCDF', 'tear_down_class()')

	def test_normal(self):
		"""Test that cdf() returns correct values normal demand_list.
		"""
		print_status('TestCDF', 'test_normal()')

		demand_source_factory = DemandSourceFactory()
		demand_source = demand_source_factory.build_demand_source(DemandType.NORMAL)
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		F = demand_source.cdf(55)
		self.assertAlmostEqual(F, 0.734014470951299)

		F = demand_source.cdf(40)
		self.assertAlmostEqual(F, 0.105649773666855)

	def test_uniform_continuous(self):
		"""Test that truncation_bounds() returns correct bounds for continuous
		uniform demand_list.
		"""
		print_status('TestCDF', 'test_uniform_continuous()')

		demand_source_factory = DemandSourceFactory()
		demand_source = demand_source_factory.build_demand_source(DemandType.UNIFORM_CONTINUOUS)
		demand_source.lo = 50
		demand_source.hi = 100

		F = demand_source.cdf(55)
		self.assertEqual(F, 0.100000000000000)

		F = demand_source.cdf(80)
		self.assertEqual(F, 0.600000000000000)


