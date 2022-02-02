import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.demand_source import *


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
		demand_source.type = 'N'
		demand_source.mean = -100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.standard_deviation = -100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

	def test_uniform_discrete(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for uniform discrete distribution.
		"""
		print_status('TestValidateParameters', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = -100
		demand_source.hi = 100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 10
		demand_source.hi = -100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 3.8
		demand_source.hi = 100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.hi = 72.3
		demand_source.lo = 50
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 20
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

	def test_uniform_continuous(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for uniform continuous distribution.
		"""
		print_status('TestValidateParameters', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = -100
		demand_source.hi = 100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 10
		demand_source.hi = -100
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 20
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

	def test_deterministic(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for deterministic distribution.
		"""
		print_status('TestValidateParameters', 'test_deterministic()')

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = None
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

	def test_custom_discrete(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for custom discrete distribution.
		"""
		print_status('TestValidateParameters', 'test_custom_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = None
		demand_source.probabilities = 4 * [0.25]
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4]
		demand_source.probabilities = None
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4, 5]
		demand_source.probabilities = 4 * [0.25]
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4]
		demand_source.probabilities = 4 * [0.2]
		with self.assertRaises(ValueError):
			demand_source.validate_parameters()


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
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is None.
		"""
		print_status('TestDemandSourceRepr', 'test_none()')

		demand_source = DemandSource()
		demand_source.type = None

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(None)")

	def test_normal(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'N'.
		"""
		print_status('TestDemandSourceRepr', 'test_normal()')

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(N: mean=50.00, standard_deviation=8.00)")

	def test_uniform_discrete(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'UD'.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 80

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UD: lo=50.00, hi=80.00)")

	def test_uniform_continuous(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'UC'.
		"""
		print_status('TestDemandSourceRepr', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 80

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(UC: lo=50.00, hi=80.00)")

	def test_deterministic(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'D'.
		"""
		print_status('TestDemandSourceRepr', 'test_deterministic()')

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = 5

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(D: demand_list=5)")

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = [5, 10, 5, 10]

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(D: demand_list=[5, 10, 5, 10])")

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = 5 * [5, 10, 5, 10]

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(D: demand_list=[5, 10, 5, 10, 5, 10, 5, 10]...)")

	def test_custom_discrete(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'CD'.
		"""
		print_status('TestDemandSourceRepr', 'test_custom_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [5, 10, 15, 20]
		demand_source.probabilities = [0.1, 0.2, 0.3, 0.4]

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(CD: demand_list=[5, 10, 15, 20], probabilities=[0.1, 0.2, 0.3, 0.4])")


class TestGenerateDemand(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestGenerateDemand', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestGenerateDemand', 'tear_down_class()')

	def test_deterministic(self):
		"""Test that generate_demand() returns valid demand values for deterministic demand_list.
		"""
		print_status('TestGenerateDemand', 'test_deterministic()')

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = 5
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = [5, 4, 3, 2]
		d = demand_source.generate_demand()
		self.assertEqual(d, 5)

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = [5, 4, 3, 2]
		d = demand_source.generate_demand(period=2)
		self.assertEqual(d, 3)

	def test_discrete_explicit(self):
		"""Test that generate_demand() returns valid demand values for discrete explicit demand_list.
		"""
		print_status('TestGenerateDemand', 'test_discrete_explicit()')

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = [5, 4, 3, 2]
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

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		distribution = demand_source.demand_distribution
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

		self.assertEqual(mu, 50)
		self.assertEqual(sigma, 8)
		self.assertAlmostEqual(z, 58.291467115950319)

	def test_uniform_discrete(self):
		"""Test demand_distribution() for discrete uniform demand_list.
		"""
		print_status('TestDemandDistribution', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 100

		distribution = demand_source.demand_distribution
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

		self.assertEqual(mu, 75)
		self.assertAlmostEqual(sigma, np.sqrt((51**2 - 1) / 12))
		self.assertEqual(z, 93)

	def test_uniform_continuous(self):
		"""Test demand_distribution() for continuous uniform demand_list.
		"""
		print_status('TestDemandDistribution', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 100

		distribution = demand_source.demand_distribution
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

		self.assertEqual(mu, 75)
		self.assertAlmostEqual(sigma, 50 / np.sqrt(12))
		self.assertEqual(z, 92.5)

	def test_custom_discrete(self):
		"""Test demand_distribution() for custom discrete demand_list.
		"""
		print_status('TestDemandDistribution', 'test_custom_discrete()')

		d = [1, 4, 7, 10]
		p = [0.1, 0.2, 0.3, 0.4]

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = d
		demand_source.probabilities = p

		distribution = demand_source.demand_distribution
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

		self.assertEqual(mu, np.dot(d, p))
		self.assertAlmostEqual(sigma, np.sqrt(np.dot(np.square(d), p) - mu**2))
		self.assertEqual(z, 10)


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
		"""Test that cdf() returns correct values for normal demand_list.
		"""
		print_status('TestCDF', 'test_normal()')

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		F = demand_source.cdf(55)
		self.assertAlmostEqual(F, 0.734014470951299)

		F = demand_source.cdf(40)
		self.assertAlmostEqual(F, 0.105649773666855)

	def test_uniform_continuous(self):
		"""Test that cdf() returns correct values for continuous
		uniform demand_list.
		"""
		print_status('TestCDF', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 100

		F = demand_source.cdf(55)
		self.assertEqual(F, 0.1)

		F = demand_source.cdf(80)
		self.assertEqual(F, 0.6)

	def test_uniform_discrete(self):
		"""Test that cdf() returns correct values for discrete
		uniform demand_list.
		"""
		print_status('TestCDF', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 100

		F = demand_source.cdf(55)
		self.assertEqual(F, 0.11764705882352941)

		F = demand_source.cdf(80)
		self.assertEqual(F, 0.6078431372549019)

	def test_custom_discrete(self):
		"""Test that cdf() returns correct values for custom discrete
		demand_list.
		"""
		print_status('TestCDF', 'test_custom_discrete()')

		d = [10, 40, 70, 100]
		p = [0.1, 0.2, 0.3, 0.4]

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = d
		demand_source.probabilities = p

		F = demand_source.cdf(55)
		self.assertAlmostEqual(F, 0.3)

		F = demand_source.cdf(80)
		self.assertAlmostEqual(F, 0.6)






