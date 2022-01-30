#from math import *
from multiprocessing.sharedctypes import Value
import unittest

from numpy import ndarray

from pyinv.eoq import *
from pyinv.instances import *


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_eoq   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestEconomicOrderQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantity', 'tear_down_class()')

	def test_example_3_1(self):
		"""Test that EOQ function correctly solves Example 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_example_3_1()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("example_3_1")

		order_quantity, cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 304.0467800264368)
		self.assertAlmostEqual(cost, 68.410525505948272)

	def test_order_quantity(self):
		"""Test that EOQ function correctly evaluates cost of solutions for
		Example 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_order_quantity()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("example_3_1")

		_, cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate, 304.0467800264368)
		self.assertAlmostEqual(cost, 68.410525505948272)

		_,  cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate, 250)
		self.assertAlmostEqual(cost, 69.724999999999994)

	def test_problem_3_1(self):
		"""Test that EOQ function correctly solves Problem 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_problem_3_1()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("problem_3_1")

		order_quantity, cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 1728.109844993551)
		self.assertAlmostEqual(cost, 475230.2073732266)

	def test_bad_type(self):
		"""Test that EOQ function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantity', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		with self.assertRaises(TypeError):
			order_quantity, cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate)

	def test_negative_parameter(self):
		"""Test that EOQ function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantity', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		with self.assertRaises(ValueError):
			order_quantity, cost = economic_order_quantity(fixed_cost, holding_cost, demand_rate)


class TestEconomicOrderQuantityWithBackorders(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithBackorders', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithBackorders', 'tear_down_class()')

	def test_example_3_8(self):
		"""Test that EOQB function correctly solves Example 3.8.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_example_3_8()')

		fixed_cost, holding_cost, stockout_cost, demand_rate = \
			get_named_instance("example_3_8")

		order_quantity, stockout_fraction, cost = \
			economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 310.8125551589646)
		self.assertAlmostEqual(stockout_fraction, 0.043062200956938)
		self.assertAlmostEqual(cost, 66.921363550973254)

	def test_problem_3_2b(self):
		"""Test that EOQB function correctly solves Problem 3.2(b).
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_problem_3_2b()')

		fixed_cost, holding_cost, stockout_cost, demand_rate = \
			get_named_instance("problem_3_2b")

		order_quantity, stockout_fraction, cost = \
			economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)
		self.assertAlmostEqual(order_quantity, 83.235448128898042)
		self.assertAlmostEqual(stockout_fraction, 0.400299850074962)
		self.assertAlmostEqual(cost, 1999.148244415212)

	def test_order_quantity(self):
		"""Test that EOQB function correctly evaluates cost of solutions for
		Problem 3.2(b).
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_order_quantity()')

		fixed_cost, holding_cost, stockout_cost, demand_rate = \
			get_named_instance("problem_3_2b")

		_, _, cost = economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate, 83.235448128898042, 0.400299850074962)
		self.assertAlmostEqual(cost, 1999.148244415212)

		_, _, cost = economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate, 100, 0.3)
		self.assertAlmostEqual(cost, 2083.225000000000)

	def test_bad_type(self):
		"""Test that EOQB function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		with self.assertRaises(TypeError):
			order_quantity, stockout_fraction, cost = \
				economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)

	def test_negative_parameter(self):
		"""Test that EOQB function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		with self.assertRaises(ValueError):
			order_quantity, stockout_fraction, cost = \
				economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate)

	def test_bad_solution_parameters(self):
		"""Test that EOQB function raises exception when only one of Q or x is provided.
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_bad_solution_parameters()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		order_quantity = 300
		stockout_fraction = 0.4

		with self.assertRaises(ValueError):
			order_quantity, stockout_fraction, cost = \
				economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate, order_quantity, None)

		with self.assertRaises(ValueError):
			order_quantity, stockout_fraction, cost = \
				economic_order_quantity_with_backorders(fixed_cost, holding_cost, stockout_cost, demand_rate, None, stockout_fraction)


class TestEconomicProductionQuantity(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicProductionQuantity', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicProductionQuantity', 'tear_down_class()')

	def test_example_3_1(self):
		"""Test that EPQ function correctly solves Example 3.1, plus mu = 2000.
		"""
		print_status('TestEconomicProductionQuantity', 'test_example_3_1()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("example_3_1")
		production_rate = 2000

		order_quantity, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)
		self.assertAlmostEqual(order_quantity, 513.9328595516969)
		self.assertAlmostEqual(cost, 40.472212689696120)

	def test_order_quantity(self):
		"""Test that EPQ function correctly evaluates cost of solutions for
		Example 3.1, plus mu = 2000.
		"""
		print_status('TestEconomicProductionQuantity', 'test_order_quantity()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("example_3_1")
		production_rate = 2000

		_, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate, 513.9328595516969)
		self.assertAlmostEqual(cost, 40.472212689696120)

		_,  cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate, 350)
		self.assertAlmostEqual(cost, 43.495535714285715)

	def test_problem_3_22(self):
		"""Test that EPQ function correctly solves Problem 3.22.
		"""
		print_status('TestEconomicProductionQuantity', 'test_problem_3_22()')

		fixed_cost, holding_cost, demand_rate, production_rate = \
			get_named_instance("problem_3_22")

		order_quantity, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)
		self.assertAlmostEqual(order_quantity, 171.2697677155351)
		self.assertAlmostEqual(cost, 3.736794931975310)

	def test_bad_type(self):
		"""Test that EPQ function raises exception on bad type.
		"""
		print_status('TestEconomicProductionQuantity', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		production_rate = 2000
		with self.assertRaises(TypeError):
			order_quantity, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)

	def test_negative_parameter(self):
		"""Test that EPQ function raises exception on negative parameter.
		"""
		print_status('TestEconomicProductionQuantity', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		production_rate = 2000
		with self.assertRaises(ValueError):
			order_quantity, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)

	def test_bad_producition_rate(self):
		"""Test that EPQ function raises exception when mu < lambda.
		"""
		print_status('TestEconomicProductionQuantity', 'test_bad_producition_rate()')

		fixed_cost, holding_cost, demand_rate = get_named_instance("example_3_1")
		production_rate = 1000

		fixed_cost = fixed_cost
		holding_cost = holding_cost
		demand_rate = demand_rate
		production_rate = production_rate

		with self.assertRaises(ValueError):
			order_quantity, cost = economic_production_quantity(fixed_cost, holding_cost, demand_rate, production_rate)

class TestJointReplenishmentProblemSilverHeuristic(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'tear_down_class()')

	def test_example_scmo(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves the SCMO example.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_example_scmo()')

		shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates = get_named_instance("jrp_ex")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)

		self.assertListEqual(order_quantities, [3.103164454170876, 9.309493362512628, 3.103164454170876])
		self.assertEqual(base_cycle_time, 3.103164454170876)
		self.assertListEqual(order_multiples, [1, 3, 1])
		self.assertEqual(cost, 837.8544026261366)

	def test_hw_1_scmo(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves first JRP HW problem from SCMO.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_hw_1_scmo()')

		shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates = get_named_instance("jrp_hw_1")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)

		self.assertListEqual(order_quantities, [434.91461289169166, 217.45730644584583, 224.78732801143613, 128.2753773978304])
		self.assertEqual(base_cycle_time, 0.24433405218634363)
		self.assertListEqual(order_multiples, [1, 2, 1, 3])
		self.assertEqual(cost, 1028646.3597045067)

	def test_silver(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves Silver's (1976) example.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_silver()')

		shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates = get_named_instance("jrp_silver")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)

		self.assertListEqual(order_quantities, [488.4707307805676, 184.58340978804858, 157.00844917946816, 143.50234602424507, 119.8666655026047])
		self.assertEqual(base_cycle_time, 0.2813771490671472)
		self.assertListEqual(order_multiples, [1, 1, 1, 3, 3])
		self.assertEqual(cost, 218.68632025498687)

	def test_spp(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves Silver, Pyke, and Peterson's (1998) example.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_spp()')

		shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates = get_named_instance("jrp_spp")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates)

		self.assertListEqual(order_quantities, [6550.912625995079, 952.1675328481219, 426.57105471595867, 685.5606236506478])
		self.assertEqual(base_cycle_time, 0.07617340262784976)
		self.assertListEqual(order_multiples, [1, 1, 4, 3])
		self.assertEqual(cost, 2067.650840930354)

