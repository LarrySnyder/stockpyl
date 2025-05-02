#from math import *
import unittest
# import sys

# sys.path.append('../src')

from numpy import ndarray

from stockpyl.eoq import *
from stockpyl.instances import *


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

		instance = load_instance("example_3_1")

		order_quantity, cost = economic_order_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'])
		self.assertAlmostEqual(order_quantity, 304.0467800264368)
		self.assertAlmostEqual(cost, 68.410525505948272)

	def test_order_quantity(self):
		"""Test that EOQ function correctly evaluates cost of solutions for
		Example 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_order_quantity()')

		instance = load_instance("example_3_1")

		_, cost = economic_order_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], 304.0467800264368)
		self.assertAlmostEqual(cost, 68.410525505948272)

		_,  cost = economic_order_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], 250)
		self.assertAlmostEqual(cost, 69.724999999999994)

	def test_problem_3_1(self):
		"""Test that EOQ function correctly solves Problem 3.1.
		"""
		print_status('TestEconomicOrderQuantity', 'test_problem_3_1()')

		instance = load_instance("problem_3_1")

		order_quantity, cost = economic_order_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'])
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


class TestEconomicOrderQuantityWithAllUnitsDiscounts(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'tear_down_class()')

	def test_example_3_6(self):
		"""Test that economic_order_quantity_with_all_units_discounts function correctly solves Example 3.6.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_example_3_6()')

		instance = load_instance("example_3_5")

		order_quantity, region, cost = \
			economic_order_quantity_with_all_units_discounts(instance['fixed_cost'], instance['holding_cost_rate'], instance['demand_rate'], instance['breakpoints'], instance['unit_costs'])
		self.assertEqual(order_quantity, 800)
		self.assertEqual(region, 2)
		self.assertAlmostEqual(cost, 978.60)

	def test_problem_3_12a(self):
		"""Test that economic_order_quantity_with_all_units_discounts function correctly solves Problem 3.12(a).
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_problem_3_12a()')

		instance = load_instance("problem_3_12")

		order_quantity, region, cost = \
			economic_order_quantity_with_all_units_discounts(instance['fixed_cost'], instance['holding_cost_rate'], instance['demand_rate'], instance['breakpoints'], instance['unit_costs'])
		self.assertEqual(order_quantity, 2400)
		self.assertEqual(region, 2)
		self.assertAlmostEqual(cost, 201251093.75)

	def test_docstring_example(self):
		"""Test that economic_order_quantity_with_all_units_discounts function correctly solves instance in the docstring.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_docstring_example()')

		fixed_cost = 200
		holding_cost_rate = 0.2
		demand_rate = 1000
		breakpoints = [0, 200, 500]
		unit_costs = [500, 475, 450]

		order_quantity, region, cost = \
			economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)
		self.assertEqual(order_quantity, 500)
		self.assertEqual(region, 2)
		self.assertAlmostEqual(cost, 472900.0)

	def test_bad_type(self):
		"""Test that economic_order_quantity_with_all_units_discounts function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800],
		unit_costs = [0.75, 0.72, 0.68]

		with self.assertRaises(TypeError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_negative_parameter(self):
		"""Test that economic_order_quantity_with_all_units_discounts function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800],
		unit_costs = [0.75, 0.72, 0.68]

		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_bad_breapoints(self):
		"""Test that economic_order_quantity_with_all_units_discounts function raises exception when breakpoint parameters
		are bad.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_bad_breapoints()')

		fixed_cost = 8
		holding_cost_rate = 0.3
		demand_rate = 1300
		unit_costs = [0.75, 0.72, 0.68]

		breakpoints = 500
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [500, 600, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, 600.5, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, -400, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, 800, 400],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_bad_unit_costs(self):
		"""Test that economic_order_quantity_with_all_units_discounts function raises exception when breakpoint parameters
		are bad.
		"""
		print_status('TestEconomicOrderQuantityWithAllUnitsDiscounts', 'test_bad_unit_costs()')

		fixed_cost = 8
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800]

		unit_costs = [0.75, 0.72]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		unit_costs = [0.75, 0.72, 0.68, 0.6]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		unit_costs = [0.75, 0.72, -0.68]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_all_units_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)


class TestEconomicOrderQuantityWithIncrementalDiscounts(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'tear_down_class()')

	def test_example_3_7(self):
		"""Test that economic_order_quantity_with_incremental_discounts function correctly solves Example 3.7.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_example_3_7()')

		instance = load_instance("example_3_5")

		order_quantity, region, cost = \
			economic_order_quantity_with_incremental_discounts(instance['fixed_cost'], instance['holding_cost_rate'], instance['demand_rate'], instance['breakpoints'], instance['unit_costs'])
		self.assertAlmostEqual(order_quantity, 304.04678003)
		self.assertEqual(region, 0)
		self.assertAlmostEqual(cost, 1043.41052551)

	def test_problem_3_12b(self):
		"""Test that economic_order_quantity_with_incremental_discounts function correctly solves Problem 3.12(b).
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_problem_3_12b()')

		instance = load_instance("problem_3_12")

		order_quantity, region, cost = \
			economic_order_quantity_with_incremental_discounts(instance['fixed_cost'], instance['holding_cost_rate'], instance['demand_rate'], instance['breakpoints'], instance['unit_costs'])
		self.assertAlmostEqual(order_quantity, 28553.06065428)
		self.assertEqual(region, 2)
		self.assertAlmostEqual(cost, 208678591.67992835)

	def test_docstring_example(self):
		"""Test that economic_order_quantity_with_incremental_discounts function correctly solves instance in the docstring.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_docstring_example()')

		fixed_cost = 150
		holding_cost_rate = 0.25
		demand_rate = 2400
		breakpoints = [0, 300, 600]
		unit_costs = [100, 90, 80]

		order_quantity, region, cost = \
			economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)
		self.assertEqual(order_quantity, 1481.8906842274164)
		self.assertEqual(region, 2)
		self.assertAlmostEqual(cost, 222762.8136845483)

	def test_bad_type(self):
		"""Test that economic_order_quantity_with_incremental_discounts function raises exception on bad type.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_bad_type()')

		fixed_cost = "banana"
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800],
		unit_costs = [0.75, 0.72, 0.68]

		with self.assertRaises(TypeError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_negative_parameter(self):
		"""Test that economic_order_quantity_with_incremental_discounts function raises exception on negative parameter.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_negative_parameter()')

		fixed_cost = -8
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800],
		unit_costs = [0.75, 0.72, 0.68]

		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_bad_breapoints(self):
		"""Test that economic_order_quantity_with_incremental_discounts function raises exception when breakpoint parameters
		are bad.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_bad_breapoints()')

		fixed_cost = 8
		holding_cost_rate = 0.3
		demand_rate = 1300
		unit_costs = [0.75, 0.72, 0.68]

		breakpoints = 500
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [500, 600, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, 600.5, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, -400, 700],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		breakpoints = [0, 800, 400],
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

	def test_bad_unit_costs(self):
		"""Test that economic_order_quantity_with_incremental_discounts function raises exception when breakpoint parameters
		are bad.
		"""
		print_status('TestEconomicOrderQuantityWithIncrementalDiscounts', 'test_bad_unit_costs()')

		fixed_cost = 8
		holding_cost_rate = 0.3
		demand_rate = 1300
		breakpoints = [0, 400, 800]

		unit_costs = [0.75, 0.72]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		unit_costs = [0.75, 0.72, 0.68, 0.6]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)

		unit_costs = [0.75, 0.72, -0.68]
		with self.assertRaises(ValueError):
			_ = economic_order_quantity_with_incremental_discounts(fixed_cost, holding_cost_rate, demand_rate, breakpoints, unit_costs)


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

		instance = load_instance("example_3_8")

		order_quantity, stockout_fraction, cost = \
			economic_order_quantity_with_backorders(instance['fixed_cost'], instance['holding_cost'], instance['stockout_cost'], instance['demand_rate'])
		self.assertAlmostEqual(order_quantity, 310.8125551589646)
		self.assertAlmostEqual(stockout_fraction, 0.043062200956938)
		self.assertAlmostEqual(cost, 66.921363550973254)

	def test_problem_3_2b(self):
		"""Test that EOQB function correctly solves Problem 3.2(b).
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_problem_3_2b()')

		instance = load_instance("problem_3_2b")

		order_quantity, stockout_fraction, cost = \
			economic_order_quantity_with_backorders(instance['fixed_cost'], instance['holding_cost'], instance['stockout_cost'], instance['demand_rate'])
		self.assertAlmostEqual(order_quantity, 83.235448128898042)
		self.assertAlmostEqual(stockout_fraction, 0.400299850074962)
		self.assertAlmostEqual(cost, 1999.148244415212)

	def test_order_quantity(self):
		"""Test that EOQB function correctly evaluates cost of solutions for
		Problem 3.2(b).
		"""
		print_status('TestEconomicOrderQuantityWithBackorders', 'test_order_quantity()')

		instance = load_instance("problem_3_2b")

		_, _, cost = economic_order_quantity_with_backorders(instance['fixed_cost'], instance['holding_cost'], instance['stockout_cost'], instance['demand_rate'], 83.235448128898042, 0.400299850074962)
		self.assertAlmostEqual(cost, 1999.148244415212)

		_, _, cost = economic_order_quantity_with_backorders(instance['fixed_cost'], instance['holding_cost'], instance['stockout_cost'], instance['demand_rate'], 100, 0.3)
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

		instance = load_instance("example_3_1")
		production_rate = 2000

		order_quantity, cost = economic_production_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], production_rate)
		self.assertAlmostEqual(order_quantity, 513.9328595516969)
		self.assertAlmostEqual(cost, 40.472212689696120)

	def test_order_quantity(self):
		"""Test that EPQ function correctly evaluates cost of solutions for
		Example 3.1, plus mu = 2000.
		"""
		print_status('TestEconomicProductionQuantity', 'test_order_quantity()')

		instance = load_instance("example_3_1")
		production_rate = 2000

		_, cost = economic_production_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], production_rate, 513.9328595516969)
		self.assertAlmostEqual(cost, 40.472212689696120)

		_,  cost = economic_production_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], production_rate, 350)
		self.assertAlmostEqual(cost, 43.495535714285715)

	def test_problem_3_22(self):
		"""Test that EPQ function correctly solves Problem 3.22.
		"""
		print_status('TestEconomicProductionQuantity', 'test_problem_3_22()')

		instance = load_instance("problem_3_22")

		order_quantity, cost = economic_production_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], instance['production_rate'])
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

		instance = load_instance("example_3_1")
		production_rate = 1000

		with self.assertRaises(ValueError):
			order_quantity, cost = economic_production_quantity(instance['fixed_cost'], instance['holding_cost'], instance['demand_rate'], production_rate)

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

		instance = load_instance("scmo_jrp_ex")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [3.103164454170876, 9.309493362512628, 3.103164454170876])
		self.assertEqual(base_cycle_time, 3.103164454170876)
		self.assertListEqual(order_multiples, [1, 3, 1])
		self.assertEqual(cost, 837.8544026261366)

	def test_hw_1_scmo(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves first JRP HW problem from SCMO.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_hw_1_scmo()')

		instance = load_instance("scmo_jrp_hw_1")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [434.91461289169166, 217.45730644584583, 224.78732801143613, 128.2753773978304])
		self.assertEqual(base_cycle_time, 0.24433405218634363)
		self.assertListEqual(order_multiples, [1, 2, 1, 3])
		self.assertEqual(cost, 1028646.3597045067)

	def test_hw_2_scmo(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves second JRP HW problem from SCMO.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_hw_2_scmo()')

		instance = load_instance("scmo_jrp_hw_2")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [466.18602699427385, 1420.7574156015964, 710.3787078007982])
		self.assertEqual(base_cycle_time, 0.017076411245211497)
		self.assertListEqual(order_multiples, [3, 1, 2])
		self.assertEqual(cost, 566083.0327787611)

	def test_hw_3_scmo(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves third JRP HW problem from SCMO.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_hw_3_scmo()')

		instance = load_instance("scmo_jrp_hw_3")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [704.6087531803736, 295.4810900433825, 181.83451694977384, 500.04492161187807, 409.12766313699115])
		self.assertEqual(base_cycle_time, 0.11364657309360865)
		self.assertListEqual(order_multiples, [1, 2, 4, 1, 2])
		self.assertEqual(cost, 9107.181781429423)

	def test_silver(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves Silver's (1976) example.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_silver()')

		instance = load_instance("silver_jrp")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [488.4707307805676, 184.58340978804858, 157.00844917946816, 143.50234602424507, 119.8666655026047])
		self.assertEqual(base_cycle_time, 0.2813771490671472)
		self.assertListEqual(order_multiples, [1, 1, 1, 3, 3])
		self.assertEqual(cost, 218.68632025498687)

	def test_spp(self):
		"""Test that joint_replenishment_problem_silver_heuristic() correctly
		solves Silver, Pyke, and Peterson's (1998) example.
		"""
		print_status('TestJointReplenishmentProblemSilverHeuristic', 'test_spp()')

		instance = load_instance("spp_jrp")

		order_quantities, base_cycle_time, order_multiples, cost = \
			joint_replenishment_problem_silver_heuristic(instance['shared_fixed_cost'], instance['individual_fixed_costs'], instance['holding_costs'], instance['demand_rates'])

		self.assertListEqual(order_quantities, [6550.912625995079, 952.1675328481219, 426.57105471595867, 685.5606236506478])
		self.assertEqual(base_cycle_time, 0.07617340262784976)
		self.assertListEqual(order_multiples, [1, 1, 4, 3])
		self.assertEqual(cost, 2067.650840930354)

