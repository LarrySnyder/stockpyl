import unittest

from inventory import helpers


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_helpers   class : {:30s} function : {:30s}".format(class_name, function_name))


def setUpModule():
	"""Called once, before anything else in this module."""
	print_status('---', 'setUpModule()')


def tearDownModule():
	"""Called once, after everything else in this module."""
	print_status('---', 'tearDownModule()')


class TestMinOfDict(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestMinOfDict', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestMinOfDict', 'tearDownClass()')

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
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestDictMatch', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestDictMatch', 'tearDownClass()')

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
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestIsIterable', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestIsIterable', 'tearDownClass()')

	def test_list(self):
		"""Test that is_iterable() correctly returns True when input is a list.
		"""
		a = [1, 2, 3]
		self.assertEqual(helpers.is_iterable(a), True)

	def test_set(self):
		"""Test that is_iterable() correctly returns True when input is a set.
		"""
		a = {1, 2, 3}
		self.assertEqual(helpers.is_iterable(a), True)

	def test_dict(self):
		"""Test that is_iterable() correctly returns True when input is a dict.
		"""
		a = {1: 0, 2: 5, 3: 'potato'}
		self.assertEqual(helpers.is_iterable(a), True)

	def test_singleton(self):
		"""Test that is_iterable() correctly returns False when input is a
		singleton.
		"""
		a = 3.14
		self.assertEqual(helpers.is_iterable(a), False)


class TestIsInteger(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestIsInteger', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestIsInteger', 'tearDownClass()')

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


class TestEnsureListForTimePeriods(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestEnsureListForTimePeriods', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestEnsureListForTimePeriods', 'tearDownClass()')

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
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestEnsureListForNodes', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestEnsureListForNodes', 'tearDownClass()')

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
