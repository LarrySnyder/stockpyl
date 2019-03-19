import unittest
import numpy as np

from inventory import gsm_tree
from inventory import gsm_tree_helpers
from tests.instances_gsm_tree import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_tree   class : {:30s} function : {:30s}".format(class_name, function_name))

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

		min_value, min_key = gsm_tree.min_of_dict(d)

		self.assertEqual(min_value, 6.1)
		self.assertEqual(min_key, 'b')

	def test_nonnumeric(self):
		"""Test that min_of_dict() correctly raises TypeError if dict
		contains nonnumeric value."""
		print_status('TestMinOfDict', 'test_nonnumeric()')

		d = {'a': 7.5, 'b': 6.1, 'c': 'potato'}

		with self.assertRaises(TypeError):
			min_value, min_key = gsm_tree.min_of_dict(d)


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

		eq_d1_d2 = gsm_tree_helpers.dict_match(d1, d2)
		eq_d1_d3 = gsm_tree_helpers.dict_match(d1, d3)

		self.assertEqual(eq_d1_d2, False)
		self.assertEqual(eq_d1_d3, True)

	def test_missing_key(self):
		"""Test that dict_match() returns correct results if a key is
		missing.
		"""
		print_status('TestNodeMatch', 'test_missing_key()')

		d1 = {'k1': 3, 'k2': 0}
		d2 = {'k1': 3}

		eq_require_presence_t = gsm_tree_helpers.dict_match(d1, d2, True)
		eq_require_presence_f = gsm_tree_helpers.dict_match(d1, d2, False)

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
		self.assertEqual(gsm_tree_helpers.is_iterable(a), True)

	def test_set(self):
		"""Test that is_iterable() correctly returns True when input is a set.
		"""
		a = {1, 2, 3}
		self.assertEqual(gsm_tree_helpers.is_iterable(a), True)

	def test_dict(self):
		"""Test that is_iterable() correctly returns True when input is a dict.
		"""
		a = {1: 0, 2: 5, 3: 'potato'}
		self.assertEqual(gsm_tree_helpers.is_iterable(a), True)

	def test_singleton(self):
		"""Test that is_iterable() correctly returns False when input is a
		singleton.
		"""
		a = 3.14
		self.assertEqual(gsm_tree_helpers.is_iterable(a), False)


class TestSolutionCost(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestSolutionCost', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestSolutionCost', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that solution_cost() correctly reports cost for solutions
		for Example_6_5.
		"""

		print_status('TestSolutionCost', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(instance_example_6_5, force_relabel=False)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		cost = gsm_tree.solution_cost(tree, cst)
		self.assertAlmostEqual(cost, 2 * np.sqrt(2) + np.sqrt(6) + 3.0)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		cost = gsm_tree.solution_cost(tree, cst)
		self.assertAlmostEqual(cost, 13.6814337969452)


class TestInboundCST(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestInboundCST', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestInboundCST', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that inbound_cst() correctly reports cost for solutions
		for Example_6_5.
		"""

		print_status('TestInboundCST', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(instance_example_6_5, force_relabel=False)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_SI = {1: 1, 2: 0, 3: 0, 4: 0}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_tree_helpers.inbound_cst(tree, 1, cst)
		self.assertEqual(SI, 1)
		SI = gsm_tree_helpers.inbound_cst(tree, 3, cst)
		self.assertEqual(SI, 0)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_SI = {1: 1, 2: 2, 3: 2, 4: 2}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_tree_helpers.inbound_cst(tree, 1, cst)
		self.assertEqual(SI, 1)
		SI = gsm_tree_helpers.inbound_cst(tree, 3, cst)
		self.assertEqual(SI, 2)

	def test_figure_6_14(self):
		"""Test that inbound_cst() correctly reports cost for solutions
		for Figure 6.14.
		"""

		print_status('TestInboundCST', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(instance_figure_6_14, start_index=1)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0, 2: 3, 3: 5, 4: 4, 5: 7, 6: 0, 7: 0, 8: 0, 9: 0, 10: 2}
		correct_SI = {1: 0, 2: 0, 3: 3, 4: 0, 5: 5, 6: 7, 7: 0, 8: 0, 9: 0, 10: 0}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_tree_helpers.inbound_cst(tree, 4, cst)
		self.assertEqual(SI, 0)
		SI = gsm_tree_helpers.inbound_cst(tree, 6, cst)
		self.assertEqual(SI, 7)

		# Test a list.
		SI = gsm_tree_helpers.inbound_cst(tree, [2, 3, 5], cst)
		self.assertDictEqual(SI, {2: 0, 3: 3, 5: 5})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2, 2: 3, 3: 3, 4: 0, 5: 3, 6: 5, 7: 1, 8: 1, 9: 0, 10: 2}
		correct_SI = {1: 0, 2: 2, 3: 3, 4: 0, 5: 3, 6: 3, 7: 0, 8: 0, 9: 0, 10: 5}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
		self.assertDictEqual(SI, correct_SI)
