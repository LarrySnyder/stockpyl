import unittest
from scipy import stats
import numpy as np

import stockpyl.helpers as helpers


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_helpers   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestMinOfDict(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestMinOfDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestMinOfDict', 'tear_down_class()')

	def test_small_dict(self):
		"""Test that min_of_dict() returns correct result for a small dict.
		"""
		print_status('TestMinOfDict', 'test_small_dict()')

		d = {'a': 7.5, 'b': 6.1, 'c': 8.0}

		min_value, min_key = helpers.min_of_dict(d)

		self.assertEqual(min_value, 6.1)
		self.assertEqual(min_key, 'b')

	def test_nonnumeric(self):
		"""Test that min_of_dict() correctly raises TypeError if dict
		contains nonnumeric value."""
		print_status('TestMinOfDict', 'test_nonnumeric()')

		d = {'a': 7.5, 'b': 6.1, 'c': 'potato'}

		with self.assertRaises(TypeError):
			min_value, min_key = helpers.min_of_dict(d)


class TestDictMatch(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDictMatch', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDictMatch', 'tear_down_class()')

	def test_all_keys_present(self):
		"""Test that dict_match() returns correct results if all keys are
		present.
		"""
		print_status('TestDictMatch', 'test_all_keys_present()')

		d1 = {'k1': 3, 'k2': 7}
		d2 = {'k1': 3, 'k2': 6}
		d3 = {'k1': 3, 'k2': 7}

		eq_d1_d2 = helpers.dict_match(d1, d2)
		eq_d1_d3 = helpers.dict_match(d1, d3)

		self.assertEqual(eq_d1_d2, False)
		self.assertEqual(eq_d1_d3, True)

	def test_missing_key(self):
		"""Test that dict_match() returns correct results if a key is
		missing.
		"""
		print_status('TestNodeMatch', 'test_missing_key()')

		d1 = {'k1': 3, 'k2': 0}
		d2 = {'k1': 3}

		eq_require_presence_t = helpers.dict_match(d1, d2, True)
		eq_require_presence_f = helpers.dict_match(d1, d2, False)

		self.assertEqual(eq_require_presence_t, False)
		self.assertEqual(eq_require_presence_f, True)


class TestIsIterable(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsIterable', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsIterable', 'tear_down_class()')

	def test_list(self):
		"""Test that is_iterable() correctly returns True when input is a list.
		"""
		print_status('TestIsIterable', 'test_list()')

		a = [1, 2, 3]
		self.assertEqual(helpers.is_iterable(a), True)

	def test_set(self):
		"""Test that is_iterable() correctly returns True when input is a set.
		"""
		print_status('TestIsIterable', 'test_set()')

		a = {1, 2, 3}
		self.assertEqual(helpers.is_iterable(a), True)

	def test_dict(self):
		"""Test that is_iterable() correctly returns True when input is a dict.
		"""
		print_status('TestIsIterable', 'test_dict()')

		a = {1: 0, 2: 5, 3: 'potato'}
		self.assertEqual(helpers.is_iterable(a), True)

	def test_singleton(self):
		"""Test that is_iterable() correctly returns False when input is a
		singleton.
		"""
		print_status('TestIsIterable', 'test_singleton()')

		a = 3.14
		self.assertEqual(helpers.is_iterable(a), False)

	def test_iter(self):
		"""Test that is_iterable() correctly returns True when input is an
		iter.
		"""
		print_status('TestIsIterable', 'test_iter()')

		a = iter("foo")
		self.assertEqual(helpers.is_iterable(a), True)


class TestIsInteger(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsInteger', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsInteger', 'tear_down_class()')

	def test_int(self):
		"""Test that is_integer() returns correct result if x is an int.
		"""
		print_status('TestIsInteger', 'test_int()')

		x = 14
		is_int = helpers.is_integer(x)
		self.assertEqual(is_int, True)

	def test_int_float(self):
		"""Test that is_integer() returns correct result if x is an integer float.
		"""
		print_status('TestIsInteger', 'test_int_float()')

		x = 14.0
		is_int = helpers.is_integer(x)
		self.assertEqual(is_int, True)

	def test_nonint_float(self):
		"""Test that is_integer() returns correct result if x is a non-integer
		float.
		"""
		print_status('TestIsInteger', 'test_nonint_float()')

		x = 14.5
		is_int = helpers.is_integer(x)
		self.assertEqual(is_int, False)

	def test_nonfloat(self):
		"""Test that is_integer() returns correct result if x is a non-float.
		"""
		print_status('TestIsInteger', 'test_nonfloat()')

		x = "pudding"
		is_int = helpers.is_integer(x)
		self.assertEqual(is_int, False)


class TestIsDiscreteDistribution(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsDiscreteDistribution', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsDiscreteDistribution', 'tear_down_class()')

	def test_frozen_discrete(self):
		"""Test that is_discrete_distribution() returns correct result if
		passed a frozen discrete distribution.
		"""
		print_status('TestIsDiscreteDistribution', 'test_frozen_discrete()')

		dist = stats.poisson(10)
		is_discrete = helpers.is_discrete_distribution(dist)
		self.assertEqual(is_discrete, True)

	def test_frozen_continuous(self):
		"""Test that is_discrete_distribution() returns correct result if
		passed a frozen continuous distribution.
		"""
		print_status('TestIsDiscreteDistribution', 'test_frozen_continuous()')

		dist = stats.norm(10, 2)
		is_discrete = helpers.is_discrete_distribution(dist)
		self.assertEqual(is_discrete, False)

	def test_custom_discrete(self):
		"""Test that is_discrete_distribution() returns correct result if
		passed a custom discrete distribution.
		"""
		print_status('TestIsDiscreteDistribution', 'test_custom_discrete()')

		xk = list(range(7))
		pk = (0.1, 0.2, 0.3, 0.1, 0.1, 0.0, 0.2)
		dist = stats.rv_discrete(values=(xk, pk))

		is_discrete = helpers.is_discrete_distribution(dist)
		self.assertEqual(is_discrete, True)

	def test_custom_continuous(self):
		"""Test that is_discrete_distribution() returns correct result if
		passed a custom continuous distribution.
		"""
		print_status('TestIsDiscreteDistribution', 'test_custom_continuous()')

		class continuous_gen(stats.rv_continuous):
			def _pdf(self, x, *args):
				if 0 <= x <= 1:
					return 1
				else:
					return 0
		dist = continuous_gen()

		is_discrete = helpers.is_discrete_distribution(dist)
		self.assertEqual(is_discrete, False)


class TestIsContinuousDistribution(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestIsContinuousDistribution', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestIsContinuousDistribution', 'tear_down_class()')

	def test_frozen_discrete(self):
		"""Test that is_continuous_distribution() returns correct result if
		passed a frozen discrete distribution.
		"""
		print_status('TestIsContinuousDistribution', 'test_frozen_discrete()')

		dist = stats.poisson(10)
		is_discrete = helpers.is_continuous_distribution(dist)
		self.assertEqual(is_discrete, False)

	def test_frozen_continuous(self):
		"""Test that is_continuous_distribution() returns correct result if
		passed a frozen continuous distribution.
		"""
		print_status('TestIsContinuousDistribution', 'test_frozen_continuous()')

		dist = stats.norm(10, 2)
		is_discrete = helpers.is_continuous_distribution(dist)
		self.assertEqual(is_discrete, True)

	def test_custom_discrete(self):
		"""Test that is_continuous_distribution() returns correct result if
		passed a custom discrete distribution.
		"""
		print_status('TestIsContinuousDistribution', 'test_custom_discrete()')

		xk = list(range(7))
		pk = (0.1, 0.2, 0.3, 0.1, 0.1, 0.0, 0.2)
		dist = stats.rv_discrete(values=(xk, pk))

		is_discrete = helpers.is_continuous_distribution(dist)
		self.assertEqual(is_discrete, False)

	def test_custom_continuous(self):
		"""Test that is_continuous_distribution() returns correct result if
		passed a custom continuous distribution.
		"""
		print_status('TestIsContinuousDistribution', 'test_custom_continuous()')

		class continuous_gen(stats.rv_continuous):
			def _pdf(self, x, *args):
				if 0 <= x <= 1:
					return 1
				else:
					return 0
		dist = continuous_gen()

		is_discrete = helpers.is_continuous_distribution(dist)
		self.assertEqual(is_discrete, True)


class TestCheckIterableSizes(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestCheckIterableSizes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestCheckIterableSizes', 'tear_down_class()')

	def test_singletons(self):
		"""Test that check_iterable_sizes() returns correct result if given
		only singletons.
		"""
		print_status('TestCheckIterableSizes', 'test_singletons()')

		self.assertTrue(helpers.check_iterable_sizes([3.14, 5]))

	def test_list_of_equals(self):
		"""Test that check_iterable_sizes() returns correct result if given
		a list of equal-sized iterables.
		"""
		print_status('TestCheckIterableSizes', 'test_list_of_equals()')

		self.assertTrue(helpers.check_iterable_sizes([
			[3.14, 5], 
			('a', 'b'), 
			np.array([1, 2])
		]))

	def test_list_of_equals_and_singletons(self):
		"""Test that check_iterable_sizes() returns correct result if given
		a list of equal-sized iterables with some singletons too.
		"""
		print_status('TestCheckIterableSizes', 'test_list_of_equals_and_singletons()')

		self.assertTrue(helpers.check_iterable_sizes([
			[3.14, 5], 
			7,
			('a', 'b'), 
			np.array([1, 2]),
			42
		]))

	def test_list_of_unequals(self):
		"""Test that check_iterable_sizes() returns correct result if given
		a list of unequal-sized iterables.
		"""
		print_status('TestCheckIterableSizes', 'test_list_of_unequals()')

		self.assertFalse(helpers.check_iterable_sizes([
			[3.14, 5, 17], 
			('a', 'b'), 
			np.array([1, 2])
		]))

	def test_list_of_unequals_and_singletons(self):
		"""Test that check_iterable_sizes() returns correct result if given
		a list of unequal-sized iterables with some singletons too.
		"""
		print_status('TestCheckIterableSizes', 'test_list_of_unequals_and_singletons()')

		self.assertFalse(helpers.check_iterable_sizes([
			[3.14, 5, 17], 
			7,
			('a', 'b'), 
			np.array([1, 2]),
			42
		]))


class TestEnsureListForTimePeriods(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEnsureListForTimePeriods', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEnsureListForTimePeriods', 'tear_down_class()')

	def test_singleton(self):
		"""Test that ensure_list_for_time_periods() returns correct result if
		x is a singleton.
		"""
		print_status('TestEnsureListForTimePeriods', 'test_singleton()')

		x = helpers.ensure_list_for_time_periods(3.14, 5)
		self.assertEqual(x, [0, 3.14, 3.14, 3.14, 3.14, 3.14])

	def test_list_without_0(self):
		"""Test that ensure_list_of_length() returns correct result if x is
		a list of length num_periods.
		"""
		print_status('TestEnsureListForTimePeriods', 'test_list_without_0()')

		x = helpers.ensure_list_for_time_periods([3.14, 3.14, 3.14, 3.14, 3.14], 5)
		self.assertEqual(x, [0, 3.14, 3.14, 3.14, 3.14, 3.14])

	def test_list_with_0(self):
		"""Test that ensure_list_of_length() returns correct result if x is
		a list of length num_periods+1.
		"""
		print_status('TestEnsureListForTimePeriods', 'test_list_with_0()')

		x = helpers.ensure_list_for_time_periods([-1, 3.14, 3.14, 3.14, 3.14, 3.14], 5)
		self.assertEqual(x, [-1, 3.14, 3.14, 3.14, 3.14, 3.14])

	def test_bad_list(self):
		"""Test that ensure_list_of_length() returns correct result if x is
		a list of an incorrect length.
		"""
		print_status('TestEnsureListForTimePeriods', 'test_bad_list()')

		with self.assertRaises(ValueError):
			x = helpers.ensure_list_for_time_periods([3.14, 3.14, 3.14, 3.14, 3.14], 8)


class TestEnsureListForNodes(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEnsureListForNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEnsureListForNodes', 'tear_down_class()')

	def test_singleton(self):
		"""Test that ensure_list_for_nodes() returns correct result if
		x is a singleton.
		"""
		print_status('TestEnsureListForNodes', 'test_singleton()')

		x = helpers.ensure_list_for_nodes(3.14, 5)
		self.assertEqual(x, [3.14, 3.14, 3.14, 3.14, 3.14])

	def test_list(self):
		"""Test that ensure_list_for_nodes() returns correct result if x is
		a list of length num_nodes.
		"""
		print_status('TestEnsureListForNodes', 'test_list0()')

		x = helpers.ensure_list_for_nodes([3.14, 3.14, 3.14, 3.14, 3.14], 5)
		self.assertEqual(x, [3.14, 3.14, 3.14, 3.14, 3.14])

	def test_bad_list(self):
		"""Test that ensure_list_for_nodes() returns correct result if x is
		a list of an incorrect length.
		"""
		print_status('TestEnsureListForNodes', 'test_bad_list()')

		with self.assertRaises(ValueError):
			x = helpers.ensure_list_for_nodes([3.14, 3.14, 3.14, 3.14, 3.14], 8)


class TestBuildNodeDataDict(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestBuildNodeDataDict', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestBuildNodeDataDict', 'tear_down_class()')

	def test_various(self):
		"""Test that build_node_data_dict() returns correct result for various attribute_value types.
		"""
		print_status('TestBuildNodeDataDict', 'test_various()')

		attribute_names=['local_holding_cost', 'stockout_cost', 'demand_mean', 'lead_time', 'processing_time']
		attribute_values = {}
		attribute_values['local_holding_cost'] = 1
		attribute_values['stockout_cost'] = [10, 8, 0]
		attribute_values['demand_mean'] = {1: 0, 3: 50}
		attribute_values['lead_time'] = None
		attribute_values['processing_time'] = None
		node_indices = [3, 2, 1]
		default_values = {'lead_time': 0, 'demand_mean': 99}
		data_dict = helpers.build_node_data_dict(attribute_names, attribute_values, node_indices, default_values)

		self.assertDictEqual(data_dict[1], {'local_holding_cost': 1, 'stockout_cost': 0, 'demand_mean': 0, 'lead_time': 0, 'processing_time': None})
		self.assertDictEqual(data_dict[2], {'local_holding_cost': 1, 'stockout_cost': 8, 'demand_mean': 99, 'lead_time': 0, 'processing_time': None})
		self.assertDictEqual(data_dict[3], {'local_holding_cost': 1, 'stockout_cost': 10, 'demand_mean': 50, 'lead_time': 0, 'processing_time': None})

	def test_bad_attribute_value(self):
		"""Test that build_node_data_dict() correctly raises exception if attribute_values[a] is bad.
		"""		
		print_status('TestBuildNodeDataDict', 'test_bad_attribute_value()')

		attribute_names=['local_holding_cost', 'stockout_cost']
		attribute_values = {}
		attribute_values['local_holding_cost'] = 1
		attribute_values['stockout_cost'] = [10, 8, 0, 7]
		node_indices = [3, 2, 1]
		with self.assertRaises(ValueError):
			_ = helpers.build_node_data_dict(attribute_names, attribute_values, node_indices)


class TestEnsureDictForNodes(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEnsureDictForNodes', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEnsureDictForNodes', 'tear_down_class()')

	def test_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		x is a dict.
		"""
		print_status('TestEnsureDictForNodes', 'test_dict()')

		x = helpers.ensure_dict_for_nodes({1: 3.14, 2: 5}, None)
		self.assertEqual(x, {1: 3.14, 2: 5})

	def test_singleton(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		x is a singleton.
		"""
		print_status('TestEnsureDictForNodes', 'test_singleton()')

		x = helpers.ensure_dict_for_nodes(3.14, [1, 4, 7])
		self.assertEqual(x, {1: 3.14, 4: 3.14, 7: 3.14})

	def test_list(self):
		"""Test that ensure_dict_for_nodes() returns correct result if x is
		a list of the correct length.
		"""
		print_status('TestEnsureDictForNodes', 'test_list()')

		x = helpers.ensure_dict_for_nodes([3.14, 5, 0], [1, 4, 7])
		self.assertEqual(x, {1: 3.14, 4: 5, 7: 0})

	def test_bad_list(self):
		"""Test that ensure_dict_for_nodes() returns correct result if x is
		a list of an incorrect length.
		"""
		print_status('TestEnsureDictForNodes', 'test_bad_list()')

		with self.assertRaises(ValueError):
			x = helpers.ensure_dict_for_nodes([3.14, 5], [1, 4, 7])


class TestSortDictByKeys(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSortDictByKeys', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSortDictByKeys', 'tear_down_class()')

	def test_ascending_values(self):
		"""Test that sort_dict_by_keys() returns correct result when ascending
		is True and return_values is True.
		"""
		print_status('TestSortDictByKeys', 'test_ascending_values()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}
		b = {"c": -5, "a": 2, "d": None, "b": "foo"}
		c = {0: 5, 3: "hello", 2: -1, 9: None, None: "bar"}

		a_vals = helpers.sort_dict_by_keys(a)
		b_vals = helpers.sort_dict_by_keys(b)
		c_vals = helpers.sort_dict_by_keys(c)

		self.assertEqual(a_vals, [5, -1, "hello", None])
		self.assertEqual(b_vals, [2, "foo", -5, None])
		self.assertEqual(c_vals, ["bar", 5, -1, "hello", None])

	def test_decending_values(self):
		"""Test that sort_dict_by_keys() returns correct result when ascending
		is False and return_values is True.
		"""
		print_status('TestSortDictByKeys', 'test_decending_values()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}
		b = {"c": -5, "a": 2, "d": None, "b": "foo"}
		c = {0: 5, 3: "hello", 2: -1, 9: None, None: "bar"}

		a_vals = helpers.sort_dict_by_keys(a, ascending=False)
		b_vals = helpers.sort_dict_by_keys(b, ascending=False)
		c_vals = helpers.sort_dict_by_keys(c, ascending=False)

		self.assertEqual(a_vals, [None, "hello", -1, 5])
		self.assertEqual(b_vals, [None, -5, "foo", 2])
		self.assertEqual(c_vals, [None, "hello", -1, 5, "bar"])

	def test_ascending_keys(self):
		"""Test that sort_dict_by_keys() returns correct result when ascending
		is True and return_values is False.
		"""
		print_status('TestSortDictByKeys', 'test_ascending_keys()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}
		b = {"c": -5, "a": 2, "d": None, "b": "foo"}
		c = {0: 5, 3: "hello", 2: -1, 9: None, None: "bar"}

		a_vals = helpers.sort_dict_by_keys(a, return_values=False)
		b_vals = helpers.sort_dict_by_keys(b, return_values=False)
		c_vals = helpers.sort_dict_by_keys(c, return_values=False)

		self.assertEqual(a_vals, [0, 2, 3, 9])
		self.assertEqual(b_vals, ["a", "b", "c", "d"])
		self.assertEqual(c_vals, [None, 0, 2, 3, 9])

	def test_decending_keys(self):
		"""Test that sort_dict_by_keys() returns correct result when ascending
		is False and return_values is False.
		"""
		print_status('TestSortDictByKeys', 'test_decending_keys()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}
		b = {"c": -5, "a": 2, "d": None, "b": "foo"}
		c = {0: 5, 3: "hello", 2: -1, 9: None, None: "bar"}

		a_vals = helpers.sort_dict_by_keys(a, ascending=False, return_values=False)
		b_vals = helpers.sort_dict_by_keys(b, ascending=False, return_values=False)
		c_vals = helpers.sort_dict_by_keys(c, ascending=False, return_values=False)

		self.assertEqual(a_vals, [9, 3, 2, 0])
		self.assertEqual(b_vals, ["d", "c", "b", "a"])
		self.assertEqual(c_vals, [9, 3, 2, 0, None])


class TestChangeDictKey(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestChangeDictKey', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestChangeDictKey', 'tear_down_class()')

	def test_change_dict_key(self):
		"""Test that change_dict_key() returns correct result.
		"""
		print_status('TestChangeDictKey', 'test_change_dict_key()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}
		b = {"c": -5, "a": 2, "d": None, "b": "foo"}
		c = {0: 5, 3: "hello", 2: -1, 9: None, None: "bar"}

		helpers.change_dict_key(a, 0, 77)
		helpers.change_dict_key(b, "d", "bar")
		helpers.change_dict_key(c, None, "foo")

		self.assertDictEqual(a, {3: "hello", 2: -1, 9: None, 77: 5})
		self.assertDictEqual(b, {"c": -5, "a": 2, "b": "foo", "bar": None})
		self.assertDictEqual(c, {0: 5, 3: "hello", 2: -1, 9: None, "foo": "bar"})

	def test_bad_key(self):
		"""Test that change_dict_key() raises KeyError if key is not found.
		"""
		print_status('TestChangeDictKey', 'test_bad_key()')

		a = {0: 5, 3: "hello", 2: -1, 9: None}

		with self.assertRaises(KeyError):
			helpers.change_dict_key(a, 1, 77)


class TestConvolveMany(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestConvolveMany', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestConvolveMany', 'tear_down_class()')

	def test_convolve_many(self):
		"""Test that convolve_many() returns correct result.
		"""
		print_status('TestConvolveMany', 'test_convolve_many()')

		a1 = helpers.convolve_many([[0.6, 0.3, 0.1], [0.5, 0.4, 0.1], [0.3, 0.7], [1.0]])
		a2 = helpers.convolve_many([[0.1, 0.7, 0.2], [0.1, 0.7, 0.2], [0.1, 0.7, 0.2]])

		a1_correct = [0.09, 0.327, 0.342, 0.182, 0.052, 0.007]
		a2_correct = [0.001, 0.021, 0.153, 0.427, 0.306, 0.084, 0.008]

		for i in range(len(a1)):
			self.assertAlmostEqual(a1[i], a1_correct[i])

		for i in range(len(a2)):
			self.assertAlmostEqual(a2[i], a2_correct[i])


class TestSumOfDiscretesDistribution(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSumOfDiscretesDistribution', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSumOfDiscretesDistribution', 'tear_down_class()')

	def test_sum_of_discretes_distribution(self):
		"""Test that sum_of_discretes_distribution() returns correct result.
		"""
		print_status('TestSumOfDiscretesDistribution', 'test_sum_of_discretes_distribution()')

		dist1 = helpers.sum_of_discretes_distribution(3, 0, 2, [0.1, 0.7, 0.2])
		dist2 = helpers.sum_of_discretes_distribution(3, 4, 7, [0.25, 0.25, 0.25, 0.25])

		a1_xk = range(0, 7)
		a1_pk = [0.001, 0.021, 0.153, 0.427, 0.306, 0.084, 0.008]
		a2_xk = range(12, 22)
		a2_pk = [0.015625, 0.046875, 0.09375, 0.15625, 0.1875, 0.1875, 0.15625, 0.09375, 0.046875, 0.015625]

		for i in range(len(a1_pk)):
			self.assertAlmostEqual(dist1.pmf(a1_xk[i]), a1_pk[i])
		for i in range(len(a2_pk)):
			self.assertAlmostEqual(dist2.pmf(a2_xk[i]), a2_pk[i])

		with self.assertRaises(ValueError):
			helpers.sum_of_discretes_distribution(3.5, 0, 2, [0.1, 0.7, 0.2])
		with self.assertRaises(ValueError):
			helpers.sum_of_discretes_distribution(3, 0.5, 2.5, [0.1, 0.7, 0.2])
		with self.assertRaises(ValueError):
			helpers.sum_of_discretes_distribution(3, 0, 5, [0.1, 0.7, 0.2])

