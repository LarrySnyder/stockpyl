import unittest
from scipy import stats

from pyinv import meio
from pyinv.instances import *
from pyinv.ssm_serial import *
from pyinv.newsvendor import newsvendor_normal_cost
from tests.settings import *


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


class TestTruncateAndDiscretize(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestTruncateAndDiscretize', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestTruncateAndDiscretize', 'tear_down_class()')

	def test_dict(self):
		"""Test that truncate_and_discretize() returns correct result if
		values dict is provided.
		"""
		print_status('TestTruncateAndDiscretize', 'test_dict()')

		network = get_named_instance("example_6_1")
		values = {0: [0, 5, 10], 1: list(range(10)), 2: list(range(0, 30, 5))}

		td_dict = meio.truncate_and_discretize(network, values)

		self.assertDictEqual(td_dict, {0: [0, 5, 10], 1: list(range(10)), 2: list(range(0, 30, 5))})

	def test_lo_hi_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are provided as dicts but not step or num.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_dict()')

		network = get_named_instance("example_6_1")
		lo = {0: 0, 1: 10, 2: 100}
		hi = {0: 10, 1: 12, 2: 200}

		td_dict = meio.truncate_and_discretize(network, truncation_lo=lo, truncation_hi=hi)

		self.assertDictEqual(td_dict, {0: list(range(0, 11)), 1: list(range(10, 13)), 2: list(range(100, 201))})

	def test_lo_hi_as_float(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are provided as floats but not step or num.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_float()')

		network = get_named_instance("example_6_1")
		lo = 0
		hi = 10

		td_dict = meio.truncate_and_discretize(network, truncation_lo=lo, truncation_hi=hi)

		self.assertDictEqual(td_dict, {0: list(range(0, 11)), 1: list(range(0, 11)), 2: list(range(0, 11))})

	def test_step_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and step is provided as a dict.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_float()')

		network = get_named_instance("example_6_1")
		step = {0: 1, 1: 5, 2: 10}

		td_dict = meio.truncate_and_discretize(network, discretization_step=step)

		self.assertDictEqual(td_dict, {0: list(range(0, 101)), 1: list(range(0, 101, 5)), 2: list(range(0, 101, 10))})

	def test_num_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and num is provided as a dict.
		"""
		print_status('TestTruncateAndDiscretize', 'test_num_as_dict()')

		network = get_named_instance("example_6_1")
		num = {0: 11, 1: 51, 2: 101}

		td_dict = meio.truncate_and_discretize(network, discretization_num=num)

		self.assertDictEqual(td_dict, {0: list(range(0, 101, 10)), 1: list(range(0, 101, 2)), 2: list(range(0, 101))})

	def test_num_as_int(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and num is provided as an int.
		"""
		print_status('TestTruncateAndDiscretize', 'test_num_as_int()')

		network = get_named_instance("example_6_1")
		num = 26

		td_dict = meio.truncate_and_discretize(network, discretization_num=num)

		self.assertDictEqual(td_dict, {0: list(range(0, 101, 4)), 1: list(range(0, 101, 4)), 2: list(range(0, 101, 4))})


class TestMEIOByEnumeration(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMEIOByEnumeration', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMEIOByEnumeration', 'tear_down_class()')

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByEnumeration.test_example_4_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_4_1(self):
		"""Test that meio_by_enumeration() correctly solves Example 4.1.
		"""
		print_status('TestMEIOByEnumeration', 'test_example_4_1()')

		network = get_named_instance("example_4_1_network")

		best_S, best_cost = meio.meio_by_enumeration(network, truncation_lo=55, truncation_hi=58, discretization_step=0.1,
												sim_num_trials=5, sim_num_periods=500, sim_rand_seed=762,
												progress_bar=False, print_solutions=False)

		self.assertAlmostEqual(best_S[0], 56.5)
		self.assertAlmostEqual(best_cost, 2.0768858172778417)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByEnumeration.test_example_6_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_6_1(self):
		"""Test that meio_by_enumeration() correctly solves Example 6.1.
		"""
		print_status('TestMEIOByEnumeration', 'test_example_6_1()')

		network = get_named_instance("example_6_1")

		best_S, best_cost = meio.meio_by_enumeration(network, truncation_lo={0: 5, 1: 4, 2: 10},
													 truncation_hi={0: 7, 1: 7, 2: 12}, sim_num_trials=5,
													 sim_num_periods=500, sim_rand_seed=762,
													 progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {0: 7, 1: 5, 2: 11})
		self.assertAlmostEqual(best_cost, 51.736651092915224)

	def test_example_6_1_obj_fcn(self):
		"""Test that meio_by_enumeration() correctly solves Example 6.1 when
		objective function is provided.
		"""
		print_status('TestMEIOByEnumeration', 'test_example_6_1_obj_fcn()')

		network = get_named_instance("example_6_1")

		# reindex nodes N, ..., 1 (ssm_serial.expected_cost() requires it)
		network.reindex_nodes({0: 1, 1: 2, 2: 3})
		obj_fcn = lambda S: expected_cost(network, local_to_echelon_base_stock_levels(network, S), x_num=100, d_num=10)
		best_S, best_cost = meio.meio_by_enumeration(network, truncation_lo={1: 5, 2: 4, 3: 10},
												truncation_hi={1: 7, 2: 7, 3: 12}, objective_function=obj_fcn,
												progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {1: 7, 2: 5, 3: 11})
		self.assertAlmostEqual(best_cost, 48.214497895254894)


class TestMEIOByCoordinateDescent(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMEIOByCoordinateDescent', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMEIOByCoordinateDescent', 'tear_down_class()')

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByCoordinateDescent.test_example_4_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_4_1(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 4.1.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_4_1()')

		network = get_named_instance("example_4_1_network")

		best_S, best_cost = meio.meio_by_coordinate_descent(network, initial_solution={0: 50},
															search_lo=40, search_hi=60,
															sim_num_trials=5, sim_num_periods=500, sim_rand_seed=762)

		self.assertAlmostEqual(best_S[0], 56.45760997389772)
		self.assertAlmostEqual(best_cost, 2.076877118816367)

	def test_example_4_1_obj_fcn(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 4.1
		when objective function is provided..
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_4_1_obj_fcn()')

		network = get_named_instance("example_4_1_network")
		n0 = network.nodes[0]

		f = lambda S: newsvendor_normal_cost(S[0], n0.holding_cost, n0.stockout_cost, n0.demand_source.mean, n0.demand_source.standard_deviation)

		best_S, best_cost = meio.meio_by_coordinate_descent(network, initial_solution={0: 50},
															search_lo=40, search_hi=60,
															objective_function=f)

		self.assertAlmostEqual(best_S[0], 56.6039708832618)
		self.assertAlmostEqual(best_cost, 1.9976051931801355)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByCoordinateDescent.test_example_6_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_6_1(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 6.1.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_6_1()')

		network = get_named_instance("example_6_1")

		best_S, best_cost = meio.meio_by_enumeration(network, truncation_lo={0: 5, 1: 4, 2: 10},
													 truncation_hi={0: 7, 1: 7, 2: 12}, sim_num_trials=5,
													 sim_num_periods=500, sim_rand_seed=762,
													 progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {0: 7, 1: 5, 2: 11})
		self.assertAlmostEqual(best_cost, 51.736651092915224)

	def test_example_6_1_obj_fcn(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 6.1 when
		objective function is provided.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_6_1_obj_fcn()')

		network = get_named_instance("example_6_1")

		# reindex nodes N, ..., 1 (ssm_serial.expected_cost() requires it)
		network.reindex_nodes({0: 1, 1: 2, 2: 3})
		obj_fcn = lambda S: expected_cost(network, local_to_echelon_base_stock_levels(network, S), x_num=100, d_num=10)
		best_S, best_cost = meio.meio_by_enumeration(network, truncation_lo={1: 5, 2: 4, 3: 10},
												truncation_hi={1: 7, 2: 7, 3: 12}, objective_function=obj_fcn,
												progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {1: 7, 2: 5, 3: 11})
		self.assertAlmostEqual(best_cost, 48.214497895254894)

