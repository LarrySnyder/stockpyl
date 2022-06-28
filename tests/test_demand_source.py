from base64 import standard_b64decode
import unittest

# import numpy as np
# from scipy.stats import norm
# from scipy.stats import poisson
# from scipy.stats import lognorm

from stockpyl.demand_source import *
from stockpyl.instances import load_instance


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


class TestDemandSourceEq(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDemandSourceEq', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDemandSourceEq', 'tear_down_class()')

	def test_true(self):
		"""Test that DemandSource.__eq__() correctly returns True when objects are equal.
		"""
		print_status('TestDemandSourceEq', 'test_true()')

		ds1 = DemandSource(type='N', mean=10, standard_deviation=2)
		ds2 = DemandSource(type='N', mean=10, standard_deviation=2)
		eq = ds1 == ds2
		self.assertTrue(eq)

		ds1 = DemandSource(type='N', mean=10, standard_deviation=2, round_to_int=True)
		ds2 = DemandSource(type='N', mean=10, standard_deviation=2, round_to_int=True)
		eq = ds1 == ds2
		self.assertTrue(eq)

		ds1 = DemandSource(type='P', mean=10)
		ds2 = DemandSource(type='P', mean=10)
		eq = ds1 == ds2
		self.assertTrue(eq)

		ds1 = DemandSource(type='CD', demand_list=[0, 5, 10], probabilities=[0.2, 0.5, 0.3])
		ds2 = DemandSource(type='CD', demand_list=[0, 5, 10], probabilities=[0.2, 0.5, 0.3])
		eq = ds1 == ds2
		self.assertTrue(eq)

		ds1 = DemandSource(type='P', mean=50)
		ds2 = DemandSource(type='P', mean=50)
		eq = ds1 == ds2
		self.assertTrue(eq)

		ds1 = DemandSource(type='UC', lo=50, hi=75)
		ds2 = DemandSource(type='UC', lo=50, hi=75)
		eq = ds1 == ds2
		self.assertTrue(eq)

	def test_false(self):
		"""Test that DemandSource.__eq__() correctly returns False when objects are not equal.
		"""
		print_status('TestDemandSourceEq', 'test_false()')

		ds1 = DemandSource(type='N', mean=10, standard_deviation=2)
		ds2 = DemandSource(type='N', mean=10, standard_deviation=1)
		eq = ds1 == ds2
		self.assertFalse(eq)

		ds1 = DemandSource(type='N', mean=10, standard_deviation=2)
		ds2 = DemandSource(type='N', mean=10, standard_deviation=2, round_to_int=True)
		eq = ds1 == ds2
		self.assertFalse(eq)

		ds1 = DemandSource(type='P', mean=10)
		ds2 = DemandSource(type='P', mean=8)
		eq = ds1 == ds2
		self.assertFalse(eq)

		ds1 = DemandSource(type='CD', demand_list=[0, 5, 10], probabilities=[0.1, 0.5, 0.4])
		ds2 = DemandSource(type='CD', demand_list=[0, 5, 10], probabilities=[0.2, 0.5, 0.3])
		eq = ds1 == ds2
		self.assertFalse(eq)

		ds1 = DemandSource(type='P', mean=40)
		ds2 = DemandSource(type='P', mean=50)
		eq = ds1 == ds2
		self.assertFalse(eq)

		ds1 = DemandSource(type='UC', lo=50, hi=75)
		ds2 = DemandSource(type='UC', lo=50, hi=100)
		eq = ds1 == ds2
		self.assertFalse(eq)

class TestInitialize(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestInitialize', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestInitialize', 'tear_down_class()')

	def test_initialize(self):
		"""Test that initialize() correctly initializes.
		"""
		print_status('TestInitialize', 'test_copy()')

		ds1 = DemandSource()
		ds2 = DemandSource()
		ds2.initialize()
		self.assertEqual(ds1, ds2)

		ds1 = DemandSource(type='CD', demand_list=[1, 2, 3], probabilities=[0.2, 0.5, 0.3])
		ds2 = DemandSource()
		ds1.initialize()
		self.assertEqual(ds1, ds2)

		ds1 = DemandSource(type='CD', demand_list=[1, 2, 3], probabilities=[0.2, 0.5, 0.3])
		ds2 = DemandSource()
		ds1.initialize(overwrite=False)
		self.assertNotEqual(ds1, ds2)

	def test_missing_values(self):
		"""Test that initialize() correctly leaves attributes in place if object already contains
		those attributes.
		"""
		print_status('TestInitialize', 'test_missing_values()')

		# In this instance, demand_source at node 1 is missing the ``mean`` attribute.
		network = load_instance("missing_mean", "tests/additional_files/test_demand_source_TestInitialize_data.json", initialize_missing_attributes=False)
		ds1 = network.get_node_from_index(1).demand_source
		ds1.initialize(overwrite=False)
		ds2 = DemandSource(type='N', mean=None, standard_deviation=1, round_to_int=False)
		self.assertEqual(ds1, ds2)
		
		network = load_instance("missing_mean", "tests/additional_files/test_demand_source_TestInitialize_data.json", initialize_missing_attributes=False)
		ds1 = network.get_node_from_index(1).demand_source
		ds1.initialize(overwrite=True)
		ds2 = DemandSource()
		self.assertEqual(ds1, ds2)

		network = load_instance("missing_demand_list", "tests/additional_files/test_demand_source_TestInitialize_data.json", initialize_missing_attributes=False)
		ds1 = network.get_node_from_index(3).demand_source
		ds1.initialize(overwrite=False)
		ds2 = DemandSource() # ds1 is basically blank
		self.assertEqual(ds1, ds2)


class TestToDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestToDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestToDict', 'tear_down_class()')

	def test_normal(self):
		"""Test that to_dict() correctly converts a normal DemandSource object to dict.
		"""
		print_status('TestToDict', 'test_normal()')

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 100
		demand_source.standard_deviation = 20
		demand_source.round_to_int = True
		ds_dict = demand_source.to_dict()
		correct_dict = {
			'type': 'N',
			'round_to_int': True,
			'mean': 100,
			'standard_deviation': 20,
			'demand_list': None,
			'probabilities': None,
			'lo': None,
			'hi': None
		}
		self.assertDictEqual(ds_dict, correct_dict)

	def test_uniform(self):
		"""Test that to_dict() correctly converts a uniform DemandSource object to dict.
		"""
		print_status('TestToDict', 'test_uniform()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 100
		demand_source.hi = 200
		ds_dict = demand_source.to_dict()
		correct_dict = {
			'type': 'UC',
			'round_to_int': False,
			'mean': None,
			'standard_deviation': None,
			'demand_list': None,
			'probabilities': None,
			'lo': 100,
			'hi': 200
		}
		self.assertDictEqual(ds_dict, correct_dict)

	def test_custom_discrete(self):
		"""Test that to_dict() correctly converts a custom-discrete DemandSource object to dict.
		"""
		print_status('TestToDict', 'test_custom_discrete()')

		demand_list = [0, 1, 2, 3]
		probabilities = [0.25, 0.1, 0.5, 0.15]

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = demand_list
		demand_source.probabilities = probabilities
		ds_dict = demand_source.to_dict()
		correct_dict = {
			'type': 'CD',
			'round_to_int': False,
			'mean': None,
			'standard_deviation': None,
			'demand_list': [0, 1, 2, 3],
			'probabilities': [0.25, 0.1, 0.5, 0.15],
			'lo': None,
			'hi': None
		}
		self.assertDictEqual(ds_dict, correct_dict)

		# Modify original lists to make sure the dict doesn't change.
		demand_list = [5, 4, 3, 2]
		probabilities = [0.25] * 4
		self.assertDictEqual(ds_dict, correct_dict)


class TestFromDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestFromDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestFromDict', 'tear_down_class()')

	def test_normal(self):
		"""Test that from_dict() correctly converts a normal DemandSource object from a dict.
		"""
		print_status('TestFromDict', 'test_normal()')

		the_dict = {
			'type': 'N',
			'round_to_int': True,
			'mean': 100,
			'standard_deviation': 20,
			'demand_list': None,
			'probabilities': None,
			'lo': None,
			'hi': None
		}
		ds = DemandSource.from_dict(the_dict)

		correct_ds = DemandSource()
		correct_ds.type = 'N'
		correct_ds.mean = 100
		correct_ds.standard_deviation = 20
		correct_ds.round_to_int = True
		
		self.assertEqual(ds, correct_ds)

	def test_uniform(self):
		"""Test that from_dict() correctly converts a uniform DemandSource object from a dict.
		"""
		print_status('TestFromDict', 'test_uniform()')

		the_dict = {
			'type': 'UC',
			'round_to_int': False,
			'mean': None,
			'standard_deviation': None,
			'demand_list': None,
			'probabilities': None,
			'lo': 100,
			'hi': 200
		}
		ds = DemandSource.from_dict(the_dict)

		correct_ds = DemandSource()
		correct_ds.type = 'UC'
		correct_ds.lo = 100
		correct_ds.hi = 200

		self.assertEqual(ds, correct_ds)

	def test_custom_discrete(self):
		"""Test that from_dict() correctly converts a custom-discrete DemandSource object from a dict.
		"""
		print_status('TestFromDict', 'test_custom_discrete()')

		demand_list = [0, 1, 2, 3]
		probabilities = [0.25, 0.1, 0.5, 0.15]

		the_dict = {
			'type': 'CD',
			'round_to_int': False,
			'mean': None,
			'standard_deviation': None,
			'demand_list': demand_list,
			'probabilities': probabilities,
			'lo': None,
			'hi': None
		}
		ds = DemandSource.from_dict(the_dict)

		correct_ds = DemandSource()
		correct_ds.type = 'CD'
		correct_ds.demand_list = [0, 1, 2, 3]
		correct_ds.probabilities = [0.25, 0.1, 0.5, 0.15]

		self.assertEqual(ds, correct_ds)

		# Modify original lists to make sure the object doesn't change.
		demand_list = [5, 4, 3, 2]
		probabilities = [0.25] * 4
		self.assertEqual(ds, correct_ds)


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
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.standard_deviation = -100
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

	def test_poisson(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for Poisson distribution.
		"""
		print_status('TestValidateParameters', 'test_poisson()')

		demand_source = DemandSource()
		demand_source.type = 'P'
		demand_source.mean = -100
		with self.assertRaises(AttributeError):
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
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 10
		demand_source.hi = -100
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 3.8
		demand_source.hi = 100
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.hi = 72.3
		demand_source.lo = 50
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 20
		with self.assertRaises(AttributeError):
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
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 10
		demand_source.hi = -100
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 20
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

	def test_deterministic(self):
		"""Test that TestValidateParameters correctly raises errors on invalid parameters
		for deterministic distribution.
		"""
		print_status('TestValidateParameters', 'test_deterministic()')

		demand_source = DemandSource()
		demand_source.type = 'D'
		demand_source.demand_list = None
		with self.assertRaises(AttributeError):
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
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4]
		demand_source.probabilities = None
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4, 5]
		demand_source.probabilities = 4 * [0.25]
		with self.assertRaises(AttributeError):
			demand_source.validate_parameters()

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = [1, 2, 3, 4]
		demand_source.probabilities = 4 * [0.2]
		with self.assertRaises(AttributeError):
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

	def test_poisson(self):
		"""Test that DemandSource.__repr__() correctly returns demand source string
		when type is 'P'.
		"""
		print_status('TestDemandSourceRepr', 'test_poisson()')

		demand_source = DemandSource()
		demand_source.type = 'P'
		demand_source.mean = 50

		demand_source_str = demand_source.__repr__()
		self.assertEqual(demand_source_str, "DemandSource(P: mean=50.00)")

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
		"""Test that generate_demand() returns valid demand values for deterministic demands.
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
		"""Test that generate_demand() returns valid demand values for discrete explicit demands.
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
		"""Test demand_distribution() for normal demands.
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

	def test_poisson(self):
		"""Test demand_distribution() for Poisson demands.
		"""
		print_status('TestDemandDistribution', 'test_poisson()')

		demand_source = DemandSource()
		demand_source.type = 'P'
		demand_source.mean = 50

		distribution = demand_source.demand_distribution
		mu = distribution.mean()
		sigma = distribution.std()
		z = distribution.ppf(0.85)

		self.assertEqual(mu, 50)
		self.assertAlmostEqual(sigma, np.sqrt(50))
		self.assertEqual(z, 57)

	def test_uniform_discrete(self):
		"""Test demand_distribution() for discrete uniform demands.
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
		"""Test demand_distribution() for continuous uniform demands.
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
		"""Test demand_distribution() for custom discrete demands.
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
		"""Test that cdf() returns correct values for normal demands.
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

	def test_poisson(self):
		"""Test that cdf() returns correct values for Poisson demands.
		"""
		print_status('TestCDF', 'test_poisson()')

		demand_source = DemandSource()
		demand_source.type = 'P'
		demand_source.mean = 50

		F = demand_source.cdf(55)
		self.assertAlmostEqual(F, 0.784470400693950)

		F = demand_source.cdf(40)
		self.assertAlmostEqual(F, 0.086070000117961)

	def test_uniform_continuous(self):
		"""Test that cdf() returns correct values for continuous
		uniform demands.
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
		uniform demands.
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
		demands.
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


class TestLeadTimeDemandDistribution(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestLeadTimeDemandDistribution', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestLeadTimeDemandDistribution', 'tear_down_class()')

	def test_normal(self):
		"""Test lead_time_demand_distribution() for normal demands.
		"""
		print_status('TestLeadTimeDemandDistribution', 'test_normal()')

		demand_source = DemandSource()
		demand_source.type = 'N'
		demand_source.mean = 50
		demand_source.standard_deviation = 8

		ltd_dist = demand_source.lead_time_demand_distribution(4)
		self.assertEqual(ltd_dist.mean(), 200)
		self.assertEqual(ltd_dist.std(), 16)
		self.assertAlmostEqual(ltd_dist.ppf(0.85), 216.58293423190065)
		self.assertIsInstance(ltd_dist.dist, scipy.stats._continuous_distns.norm_gen)

		ltd_dist = demand_source.lead_time_demand_distribution(5.5)
		self.assertEqual(ltd_dist.mean(), 50 * 5.5)
		self.assertEqual(ltd_dist.std(), 8 * np.sqrt(5.5))
		self.assertAlmostEqual(ltd_dist.ppf(0.85), 294.44521401635552)
		self.assertIsInstance(ltd_dist.dist, scipy.stats._continuous_distns.norm_gen)

	def test_poisson(self):
		"""Test lead_time_demand_distribution() for Poisson demands.
		"""
		print_status('TestLeadTimeDemandDistribution', 'test_poisson()')

		demand_source = DemandSource()
		demand_source.type = 'P'
		demand_source.mean = 50

		ltd_dist = demand_source.lead_time_demand_distribution(4)
		self.assertEqual(ltd_dist.mean(), 200)
		self.assertAlmostEqual(ltd_dist.std(), np.sqrt(200))
		self.assertEqual(ltd_dist.ppf(0.85), 215)
		self.assertIsInstance(ltd_dist.dist, scipy.stats._discrete_distns.poisson_gen)

	def test_uniform_discrete(self):
		"""Test lead_time_demand_distribution() for discrete uniform demands.
		"""
		print_status('TestLeadTimeDemandDistribution', 'test_uniform_discrete()')

		demand_source = DemandSource()
		demand_source.type = 'UD'
		demand_source.lo = 50
		demand_source.hi = 100

		ltd_dist = demand_source.lead_time_demand_distribution(4)
		self.assertAlmostEqual(ltd_dist.mean(), 300)
		self.assertAlmostEqual(ltd_dist.std(), 29.439202887758583)
		self.assertEqual(ltd_dist.ppf(0.85), 331)
		self.assertEqual(ltd_dist.ppf(0.0000000001), 200) 
		self.assertEqual(ltd_dist.ppf(0.9999999999), 400) 

		with self.assertRaises(ValueError):
			ltd_dist = demand_source.lead_time_demand_distribution(5.5)

	def test_uniform_continuous(self):
		"""Test lead_time_demand_distribution() for continuous uniform demands.
		"""
		print_status('TestLeadTimeDemandDistribution', 'test_uniform_continuous()')

		demand_source = DemandSource()
		demand_source.type = 'UC'
		demand_source.lo = 50
		demand_source.hi = 100

		ltd_dist = demand_source.lead_time_demand_distribution(4)
		self.assertAlmostEqual(ltd_dist.mean(), 300)
		self.assertAlmostEqual(ltd_dist.std(), 28.86751307162136)
		self.assertAlmostEqual(ltd_dist.ppf(0.85), 330.70733093427583)
		self.assertAlmostEqual(ltd_dist.ppf(0.0000000000001), 200, places=0) # Not super accurate
		self.assertAlmostEqual(ltd_dist.ppf(0.9999999999999), 400, places=0) 

		with self.assertRaises(ValueError):
			ltd_dist = demand_source.lead_time_demand_distribution(5.5)

	def test_custom_discrete(self):
		"""Test lead_time_demand_distribution() for custom discrete demands.
		"""
		print_status('TestLeadTimeDemandDistribution', 'test_custom_discrete()')

		d = [1, 4, 7, 10]
		p = [0.1, 0.2, 0.3, 0.4]

		demand_source = DemandSource()
		demand_source.type = 'CD'
		demand_source.demand_list = d
		demand_source.probabilities = p

		ltd_dist = demand_source.lead_time_demand_distribution(4)
		self.assertAlmostEqual(ltd_dist.mean(), 4 * np.dot(d, p))
		self.assertAlmostEqual(ltd_dist.std(), 6)
		self.assertEqual(ltd_dist.ppf(0.85), 34)
		self.assertEqual(ltd_dist.ppf(0.0000000001), 4)
		self.assertEqual(ltd_dist.ppf(0.9999999999), 40)

		with self.assertRaises(ValueError):
			ltd_dist = demand_source.lead_time_demand_distribution(5.5)




