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
		"""Test that inbound_cst() correctly reports inbound CST for solutions
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
		"""Test that inbound_cst() correctly reports inbound CST for solutions
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


class TestNetLeadTime(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestNetLeadTime', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestNetLeadTime', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that net_lead_time() correctly reports NLT for solutions
		for Example_6_5.
		"""

		print_status('TestNetLeadTime', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(instance_example_6_5, force_relabel=False)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_nlt = {1: 3, 2: 1, 3: 1, 4: 0}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_tree_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 3)
		nlt = gsm_tree_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 1)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_nlt = {1: 1, 2: 3, 3: 1, 4: 2}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_tree_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 1)
		nlt = gsm_tree_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 1)

	def test_figure_6_14(self):
		"""Test that net_lead_time() correctly reports NLT for solutions
		for Figure 6.14.
		"""

		print_status('TestNetLeadTime', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(instance_figure_6_14, start_index=1)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0, 2: 3, 3: 5, 4: 4, 5: 7, 6: 0, 7: 0, 8: 0, 9: 0, 10: 2}
		correct_nlt = {1: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 10, 7: 6, 8: 4, 9: 3, 10: 0}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_tree_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 2)
		nlt = gsm_tree_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 0)

		# Test a list.
		nlt = gsm_tree_helpers.net_lead_time(tree, [2, 3, 5], cst)
		self.assertDictEqual(nlt, {2: 0, 3: 0, 5: 0})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2, 2: 3, 3: 3, 4: 0, 5: 3, 6: 5, 7: 1, 8: 1, 9: 0, 10: 2}
		correct_nlt = {1: 0, 2: 2, 3: 2, 4: 4, 5: 2, 6: 1, 7: 5, 8: 3, 9: 3, 10: 5}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
		self.assertDictEqual(nlt, correct_nlt)


class TestSafetyStockLevels(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestSafetyStockLevels', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestSafetyStockLevels', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that safety_stock_levels() correctly reports safety stock for
		solutions for Example_6_5.
		"""

		print_status('TestSafetyStockLevels', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(instance_example_6_5, force_relabel=False)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_ss = {1: 2.44948974278318, 2: 1, 3: 1.41421356237309, 4: 0}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_tree_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, 2.44948974278318)
		ss = gsm_tree_helpers.safety_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(ss, 1.41421356237309)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_ss = {1: 1.41421356237309, 2: 1.73205080756888, 3: 1.41421356237309, 4: 1.41421356237309}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_tree_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, 1.41421356237309)
		ss = gsm_tree_helpers.safety_stock_levels(tree, 2, cst)
		self.assertAlmostEqual(ss, 1.73205080756888)


	def test_figure_6_14(self):
		"""Test that safety_stock_levels() correctly reports safety stock for
		solutions for Figure 6.14.
		"""

		print_status('TestSafetyStockLevels', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(instance_figure_6_14, start_index=1)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0, 2: 3, 3: 5, 4: 4, 5: 7, 6: 0, 7: 0, 8: 0, 9: 0, 10: 2}
		correct_ss = {1: 23.2617430735335,
						2: 0,
						3: 0,
						4: 0,
						5: 0,
						6: 52.0148387875557,
						7: 40.2905208759734,
						8: 32.8970725390294,
						9: 28.4897005289389,
						10: 0}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_tree_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, correct_ss[1])
		ss = gsm_tree_helpers.safety_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(ss, correct_ss[3])

		# Test a list.
		ss = gsm_tree_helpers.safety_stock_levels(tree, [2, 3, 5], cst)
		for k in ss:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2, 2: 3, 3: 3, 4: 0, 5: 3, 6: 5, 7: 1, 8: 1, 9: 0, 10: 2}
		correct_ss = {1: 0,
						2: 23.2617430735335,
						3: 23.2617430735335,
						4: 32.8970725390294,
						5: 23.2617430735335,
						6: 16.4485362695147,
						7: 36.7800452290057,
						8: 28.4897005289389,
						9: 28.4897005289389,
						10: 36.7800452290057}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(ss[k], correct_ss[k])


class TestBaseStockLevels(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestBaseStockLevels', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestBaseStockLevels', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that base_stock_levels() correctly reports base-stock levels for
		solutions for Example 6.5.

		NOTE: Example 6.5 does not contain data for mu. Here, we assume mu = 5.
		"""

		print_status('TestBaseStockLevels', 'test_example_6_5()')

		tree = instance_example_6_5.copy()
		tree.nodes[2]['external_demand_mean'] = 5
		tree.nodes[4]['external_demand_mean'] = 5
		tree = gsm_tree.preprocess_tree(tree, force_relabel=False)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_bs = {1: 32.4494897427832, 2: 6, 3: 11.4142135623731, 4: 0}
		bs = gsm_tree_helpers.base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_tree_helpers.base_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(bs, correct_bs[3])

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_bs = {1: 11.4142135623731, 2: 16.7320508075689, 3: 11.4142135623731, 4: 11.4142135623731}
		bs = gsm_tree_helpers.base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_tree_helpers.base_stock_levels(tree, 2, cst)
		self.assertAlmostEqual(bs, correct_bs[2])


	def test_figure_6_14(self):
		"""Test that base_stock_levels() correctly reports base-stock levels for
		solutions for Figure 6.14.

		NOTE: Figure 6.14 does not contain data for mu. Here, we assume mu = 100.
		"""

		print_status('TestBaseStockLevels', 'test_figure_6_14()')

		tree = instance_figure_6_14.copy()
		tree.nodes['Build_Test_Pack']['external_demand_mean'] = 100
		tree = gsm_tree.preprocess_tree(tree, start_index=1)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0, 2: 3, 3: 5, 4: 4, 5: 7, 6: 0, 7: 0, 8: 0, 9: 0, 10: 2}
		correct_bs = {1: 223.261743073533,
						2: 0,
						3: 0,
						4: 0,
						5: 0,
						6: 1052.01483878756,
						7: 640.290520875973,
						8: 432.897072539029,
						9: 328.489700528939,
						10: 0}
		bs = gsm_tree_helpers.base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_tree_helpers.base_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(bs, correct_bs[3])

		# Test a list.
		bs = gsm_tree_helpers.base_stock_levels(tree, [2, 3, 5], cst)
		for k in bs:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2, 2: 3, 3: 3, 4: 0, 5: 3, 6: 5, 7: 1, 8: 1, 9: 0, 10: 2}
		correct_bs = {1: 0,
						2: 223.261743073533,
						3: 223.261743073533,
						4: 432.897072539029,
						5: 223.261743073533,
						6: 116.448536269515,
						7: 536.780045229006,
						8: 328.489700528939,
						9: 328.489700528939,
						10: 536.780045229006}
		bs = gsm_tree_helpers.base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])
