import unittest
from scipy import stats

import stockpyl.meio_general as meio_general
from stockpyl.instances import *
from stockpyl.ssm_serial import *
from stockpyl.supply_chain_network import *
from stockpyl.newsvendor import newsvendor_normal_cost
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

		network = load_instance("example_6_1")
		values = {1: [0, 5, 10], 2: list(range(10)), 3: list(range(0, 30, 5))}

		td_dict = meio_general.truncate_and_discretize(network.node_indices, values)

		self.assertDictEqual(td_dict, {1: [0, 5, 10], 2: list(range(10)), 3: list(range(0, 30, 5))})

	def test_lo_hi_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are provided as dicts but not step or num.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_dict()')

		network = load_instance("example_6_1")
		lo = {1: 0, 2: 10, 3: 100}
		hi = {1: 10, 2: 12, 3: 200}

		td_dict = meio_general.truncate_and_discretize(network.node_indices, truncation_lo=lo, truncation_hi=hi)

		self.assertDictEqual(td_dict, {1: list(range(0, 11)), 2: list(range(10, 13)), 3: list(range(100, 201))})

	def test_lo_hi_as_float(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are provided as floats but not step or num.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_float()')

		network = load_instance("example_6_1")
		lo = 0
		hi = 10

		td_dict = meio_general.truncate_and_discretize(network.node_indices, truncation_lo=lo, truncation_hi=hi)

		self.assertDictEqual(td_dict, {1: list(range(0, 11)), 2: list(range(0, 11)), 3: list(range(0, 11))})

	def test_step_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and step is provided as a dict.
		"""
		print_status('TestTruncateAndDiscretize', 'test_lo_hi_as_float()')

		network = load_instance("example_6_1")
		step = {1: 1, 2: 5, 3: 10}

		td_dict = meio_general.truncate_and_discretize(network.node_indices, discretization_step=step)

		self.assertDictEqual(td_dict, {1: list(range(0, 101)), 2: list(range(0, 101, 5)), 3: list(range(0, 101, 10))})

	def test_num_as_dict(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and num is provided as a dict.
		"""
		print_status('TestTruncateAndDiscretize', 'test_num_as_dict()')

		network = load_instance("example_6_1")
		num = {1: 10, 2: 50, 3: 100}

		td_dict = meio_general.truncate_and_discretize(network.node_indices, discretization_num=num)

		self.assertDictEqual(td_dict, {1: list(range(0, 101, 10)), 2: list(range(0, 101, 2)), 3: list(range(0, 101))})

	def test_num_as_int(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		lo and hi are not provided and num is provided as an int.
		"""
		print_status('TestTruncateAndDiscretize', 'test_num_as_int()')

		network = load_instance("example_6_1")
		num = 25

		td_dict = meio_general.truncate_and_discretize(network.node_indices, discretization_num=num)

		self.assertDictEqual(td_dict, {1: list(range(0, 101, 4)), 2: list(range(0, 101, 4)), 3: list(range(0, 101, 4))})

	def test_dict_of_nones(self):
		"""Test that ensure_dict_for_nodes() returns correct result if
		values is provided as a dict in which every value is None. (ensure_dict_for_nodes()
		should treat this the same as if no value was passed for values.)
		"""
		print_status('TestTruncateAndDiscretize', 'test_dict_of_nones()')

		network = load_instance("example_6_1")
		num = 25
		values = {i: None for i in network.node_indices}

		td_dict = meio_general.truncate_and_discretize(network.node_indices, values=values, discretization_num=num)

		self.assertDictEqual(td_dict, {1: list(range(0, 101, 4)), 2: list(range(0, 101, 4)), 3: list(range(0, 101, 4))})

class TestBaseStockGroupAssignments(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestBaseStockGroupAssignments', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestBaseStockGroupAssignments', 'tear_down_class()')

	def test_groups(self):
		"""Test that base_stock_group_assignments() returns correct result for a few groupings.
		"""
		print_status('TestBaseStockGroupAssignments', 'test_groups()')

		node_indices = list(range(9))

		optimization_group, group_list = meio_general._base_stock_group_assignments(node_indices, [{0, 2, 3}, {1, 4, 5}, {6, 7}, {8}])
		self.assertDictEqual(optimization_group, {0: 0, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 6, 7: 6, 8: 8})
		self.assertListEqual(group_list, [[0, 2, 3], [1, 4, 5], [6, 7], [8]])

		optimization_group, group_list = meio_general._base_stock_group_assignments(node_indices, [{0, 2, 3}])
		self.assertDictEqual(optimization_group, {0: 0, 1: 1, 2: 0, 3: 0, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8})
		self.assertListEqual(group_list, [[0, 2, 3], [1], [4], [5], [6], [7], [8]])

		optimization_group, group_list = meio_general._base_stock_group_assignments(node_indices, [{4, 6, 7}, {1, 2}, {0, 5}])
		self.assertDictEqual(optimization_group, {0: 0, 1: 1, 2: 1, 3: 3, 4: 4, 5: 0, 6: 4, 7: 4, 8: 8})
		self.assertListEqual(group_list, [[0, 5], [1, 2], [3], [4, 6, 7], [8]])

		optimization_group, group_list = meio_general._base_stock_group_assignments(node_indices)
		self.assertDictEqual(optimization_group, {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8})
		self.assertListEqual(group_list, [[0], [1], [2], [3], [4], [5], [6], [7], [8]])


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

		network = load_instance("example_4_1_network")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_enumeration(network, truncation_lo=55, truncation_hi=58, discretization_step=0.1,
												sim_num_trials=5, sim_num_periods=500, sim_rand_seed=762,
												progress_bar=False, print_solutions=False)

		self.assertAlmostEqual(best_S[0], 56.5)
		self.assertAlmostEqual(best_cost, 2.0768858172778417)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByEnumeration.test_example_6_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_6_1(self):
		"""Test that meio_by_enumeration() correctly solves Example 6.1.
		"""
		print_status('TestMEIOByEnumeration', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_enumeration(network, truncation_lo={1: 5, 2: 4, 3: 10},
													 truncation_hi={1: 7, 2: 7, 3: 12}, sim_num_trials=5,
													 sim_num_periods=500, sim_rand_seed=762,
													 progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {3: 11, 2: 5, 1: 7})
		self.assertAlmostEqual(best_cost, 51.736651092915224)

	def test_example_6_1_obj_fcn(self):
		"""Test that meio_by_enumeration() correctly solves Example 6.1 when
		objective function is provided.
		"""
		print_status('TestMEIOByEnumeration', 'test_example_6_1_obj_fcn()')

		network = load_instance("example_6_1")

		# reindex nodes N, ..., 1 (ssm_serial.expected_cost() requires it)
#		network.reindex_nodes({0: 1, 1: 2, 2: 3})
		obj_fcn = lambda S: expected_cost(local_to_echelon_base_stock_levels(network, S), network=network, x_num=100, d_num=10)
		best_S, best_cost = meio_general.meio_by_enumeration(network, truncation_lo={1: 5, 2: 4, 3: 10},
												truncation_hi={1: 7, 2: 7, 3: 12}, objective_function=obj_fcn,
												progress_bar=False, print_solutions=False)

		self.assertDictEqual(best_S, {3: 11, 2: 5, 1: 7})
		self.assertAlmostEqual(best_cost, 48.39840066304044)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByEnumeration.test_rong_atan_snyder_figure_1a skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_rong_atan_snyder_figure_1a(self):
		"""Test that meio_by_enumeration() correctly solves distribution system in
		Rong, Atan, and Snyder (2017), Figure 1(a). Uses grouping to avoid optimizing
		base-stock levels of identical nodes independently.
		"""
		print_status('TestMEIOByEnumeration', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_enumeration(network, groups=[{0}, {1, 2}, {3, 4, 5, 6}],
												truncation_lo={0: 35, 1: 22, 3: 10},
												truncation_hi={0: 50, 1: 31, 3: 14},
												discretization_step={0: 5, 1: 3, 3: 1},
												sim_num_trials=5,
												sim_num_periods=100, sim_rand_seed=762, progress_bar=False,
												print_solutions=False)

		self.assertDictEqual(best_S, {0: 45, 1: 25, 2: 25, 3: 12, 4: 12, 5: 12, 6: 12})
		self.assertAlmostEqual(best_cost, 173.84266390165666)


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

		network = load_instance("example_4_1_network")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_coordinate_descent(network, initial_solution={0: 50},
															search_lo=40, search_hi=60,
															sim_num_trials=5, sim_num_periods=500, sim_rand_seed=762)

		self.assertAlmostEqual(best_S[0], 56.45760997389772)
		self.assertAlmostEqual(best_cost, 2.076877118816367)

	def test_example_4_1_obj_fcn(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 4.1
		when objective function is provided..
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_4_1_obj_fcn()')

		network = load_instance("example_4_1_network")
		n0 = network.nodes[0]

		f = lambda S: newsvendor_normal_cost(S[0], n0.holding_cost, n0.stockout_cost, n0.demand_source.mean, n0.demand_source.standard_deviation)

		best_S, best_cost = meio_general.meio_by_coordinate_descent(network, initial_solution={0: 50},
															search_lo=40, search_hi=60,
															objective_function=f)

		self.assertAlmostEqual(best_S[0], 56.6039708832618)
		self.assertAlmostEqual(best_cost, 1.9976051931801355)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByCoordinateDescent.test_example_6_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_6_1(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 6.1.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_6_1()')

		network = load_instance("example_6_1")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_coordinate_descent(network, search_lo={1: 5, 2: 4, 3: 10},
													 search_hi={1: 7, 2: 7, 3: 12}, sim_num_trials=5,
													 sim_num_periods=500, sim_rand_seed=762)

		self.assertAlmostEqual(best_S[1], 6.48114753085059)
		self.assertAlmostEqual(best_S[2], 5.733907579533881)
		self.assertAlmostEqual(best_S[3], 10.498834186884864)
		self.assertAlmostEqual(best_cost, 51.35469251096947)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByCoordinateDescent.test_example_6_1 skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_example_6_1_obj_fcn(self):
		"""Test that meio_by_coordinate_descent() correctly solves Example 6.1 when
		objective function is provided.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_example_6_1_obj_fcn()')

		network = load_instance("example_6_1")

		# reindex nodes N, ..., 1 (ssm_serial.expected_cost() requires it)
		obj_fcn = lambda S: expected_cost(local_to_echelon_base_stock_levels(network, S), network=network, x_num=100, d_num=10)
		best_S, best_cost = meio_general.meio_by_coordinate_descent(network, search_lo={1: 5, 2: 4, 3: 10},
													 search_hi={1: 7, 2: 7, 3: 12}, objective_function=obj_fcn)

		self.assertAlmostEqual(best_S[1], 6.696779017720067)
		self.assertAlmostEqual(best_S[2], 5.599667676934946)
		self.assertAlmostEqual(best_S[3], 10.793908944672346)
		self.assertAlmostEqual(best_cost, 47.77466134840843)

	@unittest.skipUnless(RUN_ALL_TESTS, "TestMEIOByCoordinateDescent.test_rong_atan_snyder_figure_1a skipped for speed; to un-skip, set RUN_ALL_TESTS to True in tests/settings.py")
	def test_rong_atan_snyder_figure_1a(self):
		"""Test that meio_by_coordinate_descent() correctly solves distribution system in
		Rong, Atan, and Snyder (2017), Figure 1(a). Uses grouping to avoid optimizing
		base-stock levels of identical nodes independently.
		"""
		print_status('TestMEIOByCoordinateDescent', 'test_rong_atan_snyder_figure_1a()')

		network = load_instance("rong_atan_snyder_figure_1a")

		# Set initial inventory levels to 0. (Tests below were built with this assumption, but subsequent
		# changes in code changed the default initial IL.)
		for node in network.nodes:
			node.initial_inventory_level = 0

		best_S, best_cost = meio_general.meio_by_coordinate_descent(network, groups=[{0}, {1, 2}, {3, 4, 5, 6}],
												search_lo={0: 35, 1: 22, 3: 10},
												search_hi={0: 50, 1: 31, 3: 14},
												sim_num_trials=1,
												sim_num_periods=50, sim_rand_seed=762,
												verbose=False)

		self.assertDictEqual(best_S, {0: 46.137514205286905, 1: 22.8116265434347, 2: 22.8116265434347, 3: 11.599007310905623, 4: 11.599007310905623, 5: 11.599007310905623, 6: 11.599007310905623})
		self.assertAlmostEqual(best_cost, 267.103456382861)
