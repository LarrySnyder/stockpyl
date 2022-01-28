import unittest
import numpy as np

import pyinv.gsm_tree as gsm_tree
import pyinv.gsm_tree_helpers as gsm_tree_helpers
from tests.instances_gsm_tree import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_tree   class : {:30s} function : {:30s}".format(class_name, function_name))

def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')



class TestSolutionCost(unittest.TestCase):
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

		tree = gsm_tree.preprocess_tree(instance_example_6_5)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		cost = gsm_tree.solution_cost_from_cst(tree, cst)
		self.assertAlmostEqual(cost, 2 * np.sqrt(2) + np.sqrt(6) + 3.0)

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		cost = gsm_tree.solution_cost_from_cst(tree, cst)
		self.assertAlmostEqual(cost, 13.6814337969452)


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

		tree = gsm_tree.preprocess_tree(instance_example_6_5)

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

		tree = gsm_tree.preprocess_tree(instance_figure_6_14)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {'Raw_Material': 0,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 5,
				'Imager_Base': 4,
				'Imager_Assembly': 7,
				'Camera': 0,
				'Ship_to_Final_Assembly': 0,
				'Circuit_Board': 0,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_SI = {'Raw_Material': 0,
						'Process_Wafers': 0,
						'Package_Test_Wafers': 3,
						'Imager_Base': 0,
						'Imager_Assembly': 5,
						'Camera': 0,
						'Ship_to_Final_Assembly': 7,
						'Circuit_Board': 0,
						'Other_Parts': 0,
						'Build_Test_Pack': 0}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
		self.assertDictEqual(SI, correct_SI)

		# Test a few singletons.
		SI = gsm_tree_helpers.inbound_cst(tree, 'Imager_Base', cst)
		self.assertEqual(SI, 0)
		SI = gsm_tree_helpers.inbound_cst(tree, 'Ship_to_Final_Assembly', cst)
		self.assertEqual(SI, 7)

		# Test a list.
		SI = gsm_tree_helpers.inbound_cst(tree, ['Process_Wafers', 'Package_Test_Wafers', 'Imager_Assembly'], cst)
		self.assertDictEqual(SI, {'Process_Wafers': 0, 'Package_Test_Wafers': 3, 'Imager_Assembly': 5})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {'Raw_Material': 2,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 3,
				'Imager_Base': 0,
				'Imager_Assembly': 3,
				'Camera': 1,
				'Ship_to_Final_Assembly': 5,
				'Circuit_Board': 1,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_SI = {'Raw_Material': 0,
						'Process_Wafers': 2,
						'Package_Test_Wafers': 3,
						'Imager_Base': 0,
						'Imager_Assembly': 3,
						'Camera': 0,
						'Ship_to_Final_Assembly': 3,
						'Circuit_Board': 0,
						'Other_Parts': 0,
						'Build_Test_Pack': 5}
		SI = gsm_tree_helpers.inbound_cst(tree, tree.nodes, cst)
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

		tree = gsm_tree.preprocess_tree(instance_example_6_5)

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

		tree = gsm_tree.preprocess_tree(instance_figure_6_14)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {'Raw_Material': 0,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 5,
				'Imager_Base': 4,
				'Imager_Assembly': 7,
				'Camera': 0,
				'Ship_to_Final_Assembly': 0,
				'Circuit_Board': 0,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_nlt = {'Raw_Material': 2,
						'Process_Wafers': 0,
						'Package_Test_Wafers': 0,
						'Imager_Base': 0,
						'Imager_Assembly': 0,
						'Camera': 6,
						'Ship_to_Final_Assembly': 10,
						'Circuit_Board': 4,
						'Other_Parts': 3,
						'Build_Test_Pack': 0}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
		self.assertDictEqual(nlt, correct_nlt)

		# Test a few singletons.
		nlt = gsm_tree_helpers.net_lead_time(tree, 'Raw_Material', cst)
		self.assertEqual(nlt, 2)
		nlt = gsm_tree_helpers.net_lead_time(tree, 'Package_Test_Wafers', cst)
		self.assertEqual(nlt, 0)

		# Test a list.
		nlt = gsm_tree_helpers.net_lead_time(tree, ['Process_Wafers', 'Package_Test_Wafers', 'Imager_Assembly'], cst)
		self.assertDictEqual(nlt, {'Process_Wafers': 0, 'Package_Test_Wafers': 0, 'Imager_Assembly': 0})

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {'Raw_Material': 2,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 3,
				'Imager_Base': 0,
				'Imager_Assembly': 3,
				'Camera': 1,
				'Ship_to_Final_Assembly': 5,
				'Circuit_Board': 1,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_nlt = {'Raw_Material': 0,
						'Process_Wafers': 2,
						'Package_Test_Wafers': 2,
						'Imager_Base': 4,
						'Imager_Assembly': 2,
						'Camera': 5,
						'Ship_to_Final_Assembly': 1,
						'Circuit_Board': 3,
						'Other_Parts': 3,
						'Build_Test_Pack': 5}
		nlt = gsm_tree_helpers.net_lead_time(tree, tree.nodes, cst)
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

		tree = gsm_tree.preprocess_tree(instance_example_6_5)

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

		tree = gsm_tree.preprocess_tree(instance_figure_6_14)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {'Raw_Material': 0,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 5,
				'Imager_Base': 4,
				'Imager_Assembly': 7,
				'Camera': 0,
				'Ship_to_Final_Assembly': 0,
				'Circuit_Board': 0,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_ss = {'Raw_Material': 23.2617430735335,
						'Process_Wafers': 0,
						'Package_Test_Wafers': 0,
						'Imager_Base': 0,
						'Imager_Assembly': 0,
						'Camera': 40.2905208759734,
						'Ship_to_Final_Assembly': 52.0148387875557,
						'Circuit_Board': 32.8970725390294,
						'Other_Parts': 28.4897005289389,
						'Build_Test_Pack': 0}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Test a few singletons.
		ss = gsm_tree_helpers.safety_stock_levels(tree, 'Raw_Material', cst)
		self.assertAlmostEqual(ss, correct_ss['Raw_Material'])
		ss = gsm_tree_helpers.safety_stock_levels(tree, 'Package_Test_Wafers', cst)
		self.assertAlmostEqual(ss, correct_ss['Package_Test_Wafers'])

		# Test a list.
		ss = gsm_tree_helpers.safety_stock_levels(tree,
			['Process_Wafers', 'Package_Test_Wafers', 'Imager_Assembly'], cst)
		for k in ss:
			self.assertAlmostEqual(ss[k], correct_ss[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {'Raw_Material': 2,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 3,
				'Imager_Base': 0,
				'Imager_Assembly': 3,
				'Camera': 1,
				'Ship_to_Final_Assembly': 5,
				'Circuit_Board': 1,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_ss = {'Raw_Material': 0,
						'Process_Wafers': 23.2617430735335,
						'Package_Test_Wafers': 23.2617430735335,
						'Imager_Base': 32.8970725390294,
						'Imager_Assembly': 23.2617430735335,
						'Camera': 36.7800452290057,
						'Ship_to_Final_Assembly': 16.4485362695147,
						'Circuit_Board': 28.4897005289389,
						'Other_Parts': 28.4897005289389,
						'Build_Test_Pack': 36.7800452290057}
		ss = gsm_tree_helpers.safety_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
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

		tree = instance_example_6_5.copy()
		tree.nodes[2]['external_demand_mean'] = 5
		tree.nodes[4]['external_demand_mean'] = 5
		tree = gsm_tree.preprocess_tree(tree)

		# Optimal solution: S = (0,0,0,1).
		cst = {1: 0, 2: 0, 3: 0, 4: 1}
		correct_bs = {1: 32.4494897427832, 2: 6, 3: 11.4142135623731, 4: 0}
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 3, cst)
		self.assertAlmostEqual(bs, correct_bs[3])

		# Sub-optimal solution: S = (2,0,2,1).
		cst = {1: 2, 2: 0, 3: 2, 4: 1}
		correct_bs = {1: 11.4142135623731, 2: 16.7320508075689, 3: 11.4142135623731, 4: 11.4142135623731}
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 1, cst)
		self.assertAlmostEqual(bs, correct_bs[1])
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 2, cst)
		self.assertAlmostEqual(bs, correct_bs[2])


	def test_figure_6_14(self):
		"""Test that cst_to_base_stock_levels() correctly reports base-stock levels for
		solutions for Figure 6.14.

		NOTE: Figure 6.14 does not contain data for mu. Here, we assume mu = 100.
		"""

		print_status('TestBaseStockLevels', 'test_figure_6_14()')

		tree = instance_figure_6_14.copy()
		tree.nodes['Build_Test_Pack']['external_demand_mean'] = 100
		tree = gsm_tree.preprocess_tree(tree)

		# Optimal solution: S = (0,3,5,4,7,0,0,0,0,2).
		cst = {'Raw_Material': 0,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 5,
				'Imager_Base': 4,
				'Imager_Assembly': 7,
				'Camera': 0,
				'Ship_to_Final_Assembly': 0,
				'Circuit_Board': 0,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_bs = {'Raw_Material': 223.261743073533,
						'Process_Wafers': 0,
						'Package_Test_Wafers': 0,
						'Imager_Base': 0,
						'Imager_Assembly': 0,
						'Camera': 640.290520875973,
						'Ship_to_Final_Assembly': 1052.01483878756,
						'Circuit_Board': 432.897072539029,
						'Other_Parts': 328.489700528939,
						'Build_Test_Pack': 0}
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Test a few singletons.
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 'Raw_Material', cst)
		self.assertAlmostEqual(bs, correct_bs['Raw_Material'])
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, 'Package_Test_Wafers', cst)
		self.assertAlmostEqual(bs, correct_bs['Package_Test_Wafers'])

		# Test a list.
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree,
													   ['Process_Wafers', 'Package_Test_Wafers', 'Imager_Assembly'], cst)
		for k in bs:
			self.assertAlmostEqual(bs[k], correct_bs[k])

		# Sub-optimal solution: S = (2,3,3,0,3,1,5,1,0,2).
		cst = {'Raw_Material': 2,
				'Process_Wafers': 3,
				'Package_Test_Wafers': 3,
				'Imager_Base': 0,
				'Imager_Assembly': 3,
				'Camera': 1,
				'Ship_to_Final_Assembly': 5,
				'Circuit_Board': 1,
				'Other_Parts': 0,
				'Build_Test_Pack': 2}
		correct_bs = {'Raw_Material': 0,
						'Process_Wafers': 223.261743073533,
						'Package_Test_Wafers': 223.261743073533,
						'Imager_Base': 432.897072539029,
						'Imager_Assembly': 223.261743073533,
						'Camera': 536.780045229006,
						'Ship_to_Final_Assembly': 116.448536269515,
						'Circuit_Board': 328.489700528939,
						'Other_Parts': 328.489700528939,
						'Build_Test_Pack': 536.780045229006}
		bs = gsm_tree_helpers.cst_to_base_stock_levels(tree, tree.nodes, cst)
		for k in tree.nodes:
			self.assertAlmostEqual(bs[k], correct_bs[k])
