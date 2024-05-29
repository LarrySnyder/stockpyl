import unittest
import numpy as np

import stockpyl.gsm_tree as gsm_tree
import stockpyl.gsm_helpers as gsm_helpers
from stockpyl.instances import *
from tests.instances_gsm_tree import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_helpers   class : {:30s} function : {:30s}".format(class_name, function_name))

def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')



class TestSolutionCostFromCST(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSolutionCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSolutionCost', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that solution_cost_from_cst() correctly reports cost for solutions
		for Example_6_5.
		"""

		print_status('TestSolutionCost', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		cost = gsm_tree.solution_cost_from_cst(tree, cst)
		self.assertAlmostEqual(cost, 2 * math.sqrt(2) + math.sqrt(6) + 3.0)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		cost = gsm_tree.solution_cost_from_cst(tree, cst)
		self.assertAlmostEqual(cost, 13.6814337969452)

	def test_figure_6_14(self):
		"""Test that solution_cost_from_cst() correctly reports cost for solutions
		for Figure 6.14.
		"""

		print_status('TestSolutionCost', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0, 2: 3, 3: 5, 4: 4, 5: 7, 6: 0, 7: 0, 8: 0, 9: 0, 10: 2}
		cost = gsm_helpers.solution_cost_from_cst(tree, cst)
		correct_cost = 1.6448536269514722 * 10 * (0.01 * math.sqrt(2) + 0.13 * math.sqrt(10) + 0.2 * math.sqrt(6) + 0.08 * math.sqrt(4) + 0.04 * math.sqrt(3))
		self.assertAlmostEqual(cost, correct_cost)

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2, 2: 3, 3: 3, 4: 0, 5: 3, 6: 5, 7: 1, 8: 1, 9: 0, 10: 2}
		cost = gsm_helpers.solution_cost_from_cst(tree, cst)
		correct_cost = 1.6448536269514722 * 10 * (
			0.03 * math.sqrt(2) + # 2
			0.04 * math.sqrt(2) + # 3
			0.06 * math.sqrt(4) + # 4
			0.12 * math.sqrt(2) + # 5
			0.13 * math.sqrt(1) + # 6
			0.20 * math.sqrt(5) + # 7
			0.08 * math.sqrt(3) + # 8
			0.04 * math.sqrt(3) + # 9
			0.50 * math.sqrt(5)	# 10
		)
		self.assertAlmostEqual(cost, correct_cost)


class TestSolutionCostFromBaseStockLevels(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSolutionCostFromBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSolutionCostFromBaseStockLevels', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that solution_cost_from_base_stock_levels() correctly reports cost for solutions
		for Example_6_5.
		"""

		print_status('TestSolutionCostFromBaseStockLevels', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		# Optimal solution.
		bsl = {1: math.sqrt(2) * math.sqrt(3), 2: 1.00, 3: math.sqrt(2), 4: 0.00}
		cost = gsm_tree.solution_cost_from_base_stock_levels(tree, bsl)
		self.assertAlmostEqual(cost, 2 * math.sqrt(2) + math.sqrt(6) + 3.0)

		# Sub-optimal solution.
		bsl = {1: 3, 2: 0, 3: 2, 4: 0}
		cost = gsm_tree.solution_cost_from_base_stock_levels(tree, bsl)
		self.assertAlmostEqual(cost, 3 + 2 * 2)

	def test_figure_6_14(self):
		"""Test that solution_cost_from_base_stock_levels() correctly reports cost for solutions
		for Figure 6.14.
		"""

		print_status('TestSolutionCostFromBaseStockLevels', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		bsl = {1: 23.2617430735335,
			2: 0,
			3: 0,
			4: 0,
			5: 0,
			6: 52.0148387875557,
			7: 40.2905208759734,
			8: 32.8970725390294,
			9: 28.4897005289389,
			10: 0}
		cost = gsm_helpers.solution_cost_from_base_stock_levels(tree, bsl)
		correct_cost = 0.01 * 23.2617430735335 + 0.13 * 52.0148387875557 + 0.20 * 40.2905208759734 + 0.08 * 32.8970725390294 + 0.04 * 28.4897005289389
		self.assertAlmostEqual(cost, correct_cost)

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		bsl = {1: 0,
			2: 23.2617430735335,
			3: 23.2617430735335,
			4: 32.8970725390294,
			5: 23.2617430735335,
			6: 16.4485362695147,
			7: 36.7800452290057,
			8: 28.4897005289389,
			9: 28.4897005289389,
			10: 36.7800452290057}
		cost = gsm_helpers.solution_cost_from_base_stock_levels(tree, bsl)
		correct_cost = 1.6448536269514722 * 10 * (
			0.03 * math.sqrt(2) + # 2
			0.04 * math.sqrt(2) + # 3
			0.06 * math.sqrt(4) + # 4
			0.12 * math.sqrt(2) + # 5
			0.13 * math.sqrt(1) + # 6
			0.20 * math.sqrt(5) + # 7
			0.08 * math.sqrt(3) + # 8
			0.04 * math.sqrt(3) + # 9
			0.50 * math.sqrt(5)	# 10
		)
		self.assertAlmostEqual(cost, correct_cost)


class TestInboundCST(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestInboundCST', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestInboundCST', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that inbound_cst() correctly reports inbound CST for solutions
		for Example_6_5.
		"""

		print_status('TestInboundCST', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_SI = {1: 1, 2: 0, 3: 0, 4: 0}
		SI = gsm_helpers.inbound_cst(tree, tree.node_indices, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_helpers.inbound_cst(tree, 1, cst)
		self.assertEqual(SI, 1)
		SI = gsm_helpers.inbound_cst(tree, 3, cst)
		self.assertEqual(SI, 0)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_SI = {1: 1, 2: 2, 3: 2, 4: 2}
		SI = gsm_helpers.inbound_cst(tree, tree.node_indices, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_helpers.inbound_cst(tree, 1, cst)
		self.assertEqual(SI, 1)
		SI = gsm_helpers.inbound_cst(tree, 3, cst)
		self.assertEqual(SI, 2)

	def test_figure_6_14(self):
		"""Test that inbound_cst() correctly reports inbound CST for solutions
		for Figure 6.14.
		"""

		print_status('TestInboundCST', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0,
				2: 3,
				3: 5,
				4: 4,
				5: 7,
				6: 0,
				7: 0,
				8: 0,
				9: 0,
				10: 2}
		correct_SI = {1: 0,
						2: 0,
						3: 3,
						4: 0,
						5: 5,
						7: 0,
						6: 7,
						8: 0,
						9: 0,
						10: 0}
		SI = gsm_helpers.inbound_cst(tree, tree.node_indices, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_helpers.inbound_cst(tree, 4, cst)
		self.assertEqual(SI, 0)
		SI = gsm_helpers.inbound_cst(tree, 6, cst)
		self.assertEqual(SI, 7)

		# Test a list.
		SI = gsm_helpers.inbound_cst(tree, [2, 3, 5], cst)
		self.assertDictEqual(SI, {2: 0, 3: 3, 5: 5})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2,
				2: 3,
				3: 3,
				4: 0,
				5: 3,
				6: 5,
				7: 1,
				8: 1,
				9: 0,
				10: 2}
		correct_SI = {1: 0,
						2: 2,
						3: 3,
						4: 0,
						5: 3,
						6: 3,
						7: 0,
						8: 0,
						9: 0,
						10: 5}
		SI = gsm_helpers.inbound_cst(tree, tree.node_indices, cst)
		self.assertDictEqual(SI, correct_SI)


class TestNetLeadTime(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNetLeadTime', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNetLeadTime', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that net_lead_time() correctly reports NLT for solutions
		for Example_6_5.
		"""

		print_status('TestNetLeadTime', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_nlt = {1: 3, 2: 1, 3: 1, 4: 0}
		nlt = gsm_helpers.net_lead_time(tree, tree.node_indices, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 3)
		nlt = gsm_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 1)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_nlt = {1: 1, 2: 3, 3: 1, 4: 2}
		nlt = gsm_helpers.net_lead_time(tree, tree.node_indices, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 1)
		nlt = gsm_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 1)

	def test_figure_6_14(self):
		"""Test that net_lead_time() correctly reports NLT for solutions
		for Figure 6.14.
		"""

		print_status('TestNetLeadTime', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0,
				2: 3,
				3: 5,
				4: 4,
				5: 7,
				6: 0,
				7: 0,
				8: 0,
				9: 0,
				10: 2}
		correct_nlt = {1: 2,
						2: 0,
						3: 0,
						4: 0,
						5: 0,
						6: 10,
						7: 6,
						8: 4,
						9: 3,
						10: 0}
		nlt = gsm_helpers.net_lead_time(tree, tree.node_indices, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_helpers.net_lead_time(tree, 1, cst)
		self.assertEqual(nlt, 2)
		nlt = gsm_helpers.net_lead_time(tree, 3, cst)
		self.assertEqual(nlt, 0)

		# Test a list.
		nlt = gsm_helpers.net_lead_time(tree, [2, 3, 5], cst)
		self.assertDictEqual(nlt, {2: 0, 3: 0, 5: 0})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2,
				2: 3,
				3: 3,
				4: 0,
				5: 3,
				6: 5,
				7: 1,
				8: 1,
				9: 0,
				10: 2}
		correct_nlt = {1: 0,
						2: 2,
						3: 2,
						4: 4,
						5: 2,
						6: 1,
						7: 5,
						8: 3,
						9: 3,
						10: 5}
		nlt = gsm_helpers.net_lead_time(tree, tree.node_indices, cst)
		self.assertDictEqual(nlt, correct_nlt)


class TestSafetyStockLevels(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestSafetyStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestSafetyStockLevels', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that safety_stock_levels() correctly reports safety stock for
		solutions for Example_6_5.
		"""

		print_status('TestSafetyStockLevels', 'test_example_6_5()')

		tree = gsm_tree.preprocess_tree(load_instance("example_6_5"))

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_ss = {1: 2.44948974278318, 2: 1, 3: 1.41421356237309, 4: 0}
		ss = gsm_helpers.safety_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, 2.44948974278318)
		ss = gsm_helpers.safety_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(ss, 1.41421356237309)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_ss = {1: 1.41421356237309, 2: 1.73205080756888, 3: 1.41421356237309, 4: 1.41421356237309}
		ss = gsm_helpers.safety_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, 1.41421356237309)
		ss = gsm_helpers.safety_stock_levels(tree, 2, cst)
		self.assertAlmostEqual(ss, 1.73205080756888)


	def test_figure_6_14(self):
		"""Test that safety_stock_levels() correctly reports safety stock for
		solutions for Figure 6.14.
		"""

		print_status('TestSafetyStockLevels', 'test_figure_6_14()')

		tree = gsm_tree.preprocess_tree(load_instance("figure_6_14"))

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0,
				2: 3,
				3: 5,
				4: 4,
				5: 7,
				6: 0,
				7: 0,
				8: 0,
				9: 0,
				10: 2}
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
		ss = gsm_helpers.safety_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_helpers.safety_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(ss, correct_ss[1])
		ss = gsm_helpers.safety_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(ss, correct_ss[3])

		# Test a list.
		ss = gsm_helpers.safety_stock_levels(tree, [2, 3, 5], cst)
		for k in ss:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2,
				2: 3,
				3: 3,
				4: 0,
				5: 3,
				6: 5,
				7: 1,
				8: 1,
				9: 0,
				10: 2}
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
		ss = gsm_helpers.safety_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(ss[k], correct_ss[k])


class TestBaseStockLevels(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestBaseStockLevels', 'tear_down_class()')

	def test_example_6_5(self):
		"""Test that cst_to_base_stock_levels() correctly reports base-stock levels for
		solutions for Example 6.5.

		NOTE: Example 6.5 does not contain data for mu. Here, we assume mu = 5.
		"""

		print_status('TestBaseStockLevels', 'test_example_6_5()')

		tree = load_instance("example_6_5")
		tree.nodes_by_index[2].demand_source.mean = 5
		tree.nodes_by_index[4].demand_source.mean = 5
		tree = gsm_tree.preprocess_tree(tree)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_bs = {1: 32.4494897427832, 2: 6, 3: 11.4142135623731, 4: 0}
		bs = gsm_helpers.cst_to_base_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(bs, correct_bs[3])

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_bs = {1: 11.4142135623731, 2: 16.7320508075689, 3: 11.4142135623731, 4: 11.4142135623731}
		bs = gsm_helpers.cst_to_base_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 2, cst)
		self.assertAlmostEqual(bs, correct_bs[2])


	def test_figure_6_14(self):
		"""Test that cst_to_base_stock_levels() correctly reports base-stock levels for
		solutions for Figure 6.14.

		NOTE: Figure 6.14 does not contain data for mu. Here, we assume mu = 100.
		"""

		print_status('TestBaseStockLevels', 'test_figure_6_14()')

		tree = load_instance("figure_6_14")
		tree.nodes_by_index[10].demand_source.mean = 100
		tree = gsm_tree.preprocess_tree(tree)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {1: 0,
				2: 3,
				3: 5,
				4: 4,
				5: 7,
				6: 0,
				7: 0,
				8: 0,
				9: 0,
				10: 2}
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
		bs = gsm_helpers.cst_to_base_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_helpers.cst_to_base_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(bs, correct_bs[3])

		# Test a list.
		bs = gsm_helpers.cst_to_base_stock_levels(tree, [2, 3, 5], cst)
		for k in bs:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {1: 2,
				2: 3,
				3: 3,
				4: 0,
				5: 3,
				6: 5,
				7: 1,
				8: 1,
				9: 0,
				10: 2}
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
		bs = gsm_helpers.cst_to_base_stock_levels(tree, tree.node_indices, cst)
		for k in tree.node_indices:
			self.assertAlmostEqual(bs[k], correct_bs[k])
