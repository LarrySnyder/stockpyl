import unittest
import numpy as np

from stockpyl.ssm_serial import *
from tests.instances_ssm_serial import *
from stockpyl.instances import *

# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_ssm_serial   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestOptimizeBaseStockLevels(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestOptimizeBaseStockLevels', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestOptimizeBaseStockLevels', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1()')

		instance = load_instance("example_6_1")
#		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_star, C_star = optimize_base_stock_levels(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = [0, 6.599662958019763, 11.99662958019757, 22.790562824553184]
#		correct_S_star = [0, 6.514438807325977, 12.232248034454390, 22.788203530691469]	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 47.77466134840843, places=5)
#		self.assertAlmostEqual(C_star, 47.820555075345887, places=5)

	def test_example_6_1_from_network(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 when provided as a network object.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_from_network()')

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_star, C_star = optimize_base_stock_levels(network=instance,
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = [0, 6.599662958019763, 11.99662958019757, 22.790562824553184]
#		correct_S_star = [0, 6.514438807325977, 12.232248034454390, 22.788203530691469]	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 47.77466134840843, places=5)
#		self.assertAlmostEqual(C_star, 47.820555075345887, places=5)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		
	def test_example_6_1_alternate_indexing(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 when different indices are provided.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_alternate_indexing()')

		instance = load_instance("example_6_1")
		node1 = instance.nodes_by_index[1]
		node2 = instance.nodes_by_index[2]
		node3 = instance.nodes_by_index[3]
		correct_S_star = [0, 6.599662958019763, 11.99662958019757, 22.790562824553184]
#		correct_S_star = [0, 6.514438807325977, 12.232248034454390, 22.788203530691469]	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		correct_C_star = 47.77466134840843
#		correct_C_star = 47.820555075345887

		S_star, C_star = optimize_base_stock_levels(num_nodes=3,
			node_order_in_system=[3, 2, 1],
			node_order_in_lists=[1, 2, 3],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source],
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, correct_C_star, places=5)

		S_star, C_star = optimize_base_stock_levels(num_nodes=3,
			node_order_in_lists=[1, 2, 3],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source],
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, correct_C_star, places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 3, 2: 2, 3: 1})
		S_star, C_star = optimize_base_stock_levels(num_nodes=3,
			node_order_in_system=[1, 2, 3],
			node_order_in_lists=[3, 2, 1],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source],
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[4-n], places=5)
		self.assertAlmostEqual(C_star, correct_C_star, places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 3, 2: 2, 3: 1})
		S_star, C_star = optimize_base_stock_levels(num_nodes=3,
			node_order_in_system=[1, 2, 3],
			echelon_holding_cost=[node3.echelon_holding_cost, node2.echelon_holding_cost, node1.echelon_holding_cost],
			lead_time=[node3.lead_time, node2.lead_time, node1.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node3.demand_source, node2.demand_source, node1.demand_source],
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[4-n], places=5)
		self.assertAlmostEqual(C_star, correct_C_star, places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 7, 2: 3, 3: 15})
		S_star, C_star = optimize_base_stock_levels(num_nodes=3,
			node_order_in_system=[15, 3, 7],
			node_order_in_lists=[7, 3, 15],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source],
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		self.assertAlmostEqual(S_star[7], correct_S_star[1], places=5)
		self.assertAlmostEqual(S_star[3], correct_S_star[2], places=5)
		self.assertAlmostEqual(S_star[15], correct_S_star[3], places=5)
		self.assertAlmostEqual(C_star, correct_C_star, places=5)

	def test_problem_6_1(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.1.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_1()')

		instance = load_instance("problem_6_1")

		S_star, C_star = optimize_base_stock_levels(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = [0, 126.20331711660617, 226.02837018976868]
#		correct_S_star = [0, 1.241618472110342e2, 2.286691776877441e2]	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 170.28476581233167, places=5)
#		self.assertAlmostEqual(C_star, 1.676947889401860e+02, places=5)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_problem_6_2a(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.2a.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_2a()')

		instance = load_instance("problem_6_2a")

		S_star, C_star = optimize_base_stock_levels(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None, S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = [0, 42.31870725619709, 75.34023115608014, 112.48944554344857, 145.51096944333162, 178.53249334321467]
#		correct_S_star = [0, 39.7915536774345, 77.1934831561084, 111.478585178226, 142.646859743788, 173.815134309349]	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=4)
		self.assertAlmostEqual(C_star, 457.58007479275113, places=4)
#		self.assertAlmostEqual(C_star, 4.584970628129348e+02, places=4)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_problem_6_2b(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.2b.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_2b()')

		instance = load_instance("problem_6_2b")
#		instance.reindex_nodes({n: n+1 for n in instance.node_indices})

		S_star, C_star = optimize_base_stock_levels(network=instance,
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = {5: 174, 4: 142, 3: 109, 2: 74, 1: 41}
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=4)
		self.assertAlmostEqual(C_star, 453.6855978910213, places=4)
#		self.assertAlmostEqual(C_star, 453.61978213342144, places=4)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_example_6_1_uniform(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 with uniform demands.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_uniform()')

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		for n in instance.nodes:
			if n.index == 1:
				demand_source = DemandSource()
				demand_source.type = 'UC'
				demand_source.lo = 5 - math.sqrt(12) / 2
				demand_source.hi = 5 + math.sqrt(12) / 2
			else:
				demand_source = None
			n.demand_source = demand_source

		S_star, C_star = optimize_base_stock_levels(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=None,
			demand_standard_deviation=None,
			demand_source=instance.nodes_by_index[1].demand_source, 
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = {3: 22.90669850224821, 2: 12.050534323695166, 1: 6.421412157038025}
#		correct_S_star = {1: 6.293580485578014, 2: 11.95126810804254, 3: 22.601033044446353}	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=5)
		self.assertAlmostEqual(C_star, 47.386226146435995, places=5)
#		self.assertAlmostEqual(C_star, 46.45421661501915, places=5)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_example_6_1_poisson(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 with Poisson demands.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_poisson()')

		instance = load_instance("example_6_1")

		for n in instance.nodes:
			if n.index == 1:
				demand_source = DemandSource()
				demand_source.type = 'P'
				demand_source.mean = 5 
			else:
				demand_source = None
			n.demand_source = demand_source

		S_star, C_star = optimize_base_stock_levels(network=instance,
			S=None, plots=False)
		correct_S_star = {1: 9, 2: 15, 3: 26}
		self.assertDictEqual(S_star, correct_S_star)
		self.assertAlmostEqual(C_star, 72.0435433050749, places=5)
#		self.assertAlmostEqual(C_star, 72.02506008691718, places=5)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_problem_6_16(self):
		"""Test that optimize_base_stock_levels() correctly optimizes network in
		Problem 6.16.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_problem_6_16()')

		instance = load_instance("problem_6_16")

		S_star, C_star = optimize_base_stock_levels(network=instance,
			S=None, plots=False, x=None, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(8))
		correct_S_star = {2: 233.84999028717206, 1: 170.78615635393973}
#		correct_S_star = {2: 235.03951973066145, 1: 170.59486475174154}	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()
		for n in instance.node_indices:
			self.assertAlmostEqual(S_star[n], correct_S_star[n], places=4)
		self.assertAlmostEqual(C_star, 451.6549665069653, places=4)
#		self.assertAlmostEqual(C_star, 442.21079081028773, places=4)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_shang_song_instances(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		Shang-Song instances.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_shang_song_instances()')

		instance = load_instance("shang_song_1")
		S_star, C_star = optimize_base_stock_levels(network=instance, S=None, plots=False)
		correct_S_star = {1: 8, 2: 13, 3: 18, 4: 22}
		self.assertDictEqual(S_star, correct_S_star)
		self.assertAlmostEqual(C_star, 12.688, places=1)

		instance = load_instance("shang_song_9")
		S_star, C_star = optimize_base_stock_levels(network=instance, S=None, plots=False)
		correct_S_star = {1: 9, 2: 10, 3: 13, 4: 19}
		self.assertDictEqual(S_star, correct_S_star)
		self.assertAlmostEqual(C_star, 53.008, places=1)

		instance = load_instance("shang_song_17")
		S_star, C_star = optimize_base_stock_levels(network=instance, S=None, plots=False)
		correct_S_star = {1: 11, 2: 17, 3: 22, 4: 27}
		self.assertDictEqual(S_star, correct_S_star)
		self.assertAlmostEqual(C_star, 16.206, places=1)

		instance = load_instance("shang_song_25")
		S_star, C_star = optimize_base_stock_levels(network=instance, S=None, plots=False)
		correct_S_star = {1: 11, 2: 14, 3: 18, 4: 26}
		self.assertDictEqual(S_star, correct_S_star)
		self.assertAlmostEqual(C_star, 74.564, places=1)

	def test_bad_parameters(self):
		"""Test that optimize_base_stock_levels() correctly raises exceptions if
		bad parameters are given.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_bad_parameters()')

		instance = load_instance("example_6_1")
		instance.nodes_by_index[2].shipment_lead_time = -20
		with self.assertRaises(ValueError):
			S_star, C_star = optimize_base_stock_levels(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				x_num=100, d_num=10)
		
		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].stockout_cost = None
		with self.assertRaises(ValueError):
			S_star, C_star = optimize_base_stock_levels(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				x_num=100, d_num=10)

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].stockout_cost = -2
		with self.assertRaises(ValueError):
			S_star, C_star = optimize_base_stock_levels(network=instance, x_num=100, d_num=10)

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[2].echelon_holding_cost = None
		with self.assertRaises(ValueError):
			S_star, C_star = optimize_base_stock_levels(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				x_num=100, d_num=10)

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].demand_source = None
		instance.nodes_by_index[1].demand_mean = None
		instance.nodes_by_index[1].demand_standard_deviation = 10
		with self.assertRaises(ValueError):
			S_star, C_star = optimize_base_stock_levels(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=None,
				demand_standard_deviation=10,
				demand_source=None,
				x_num=100, d_num=10
			)

	def test_zero_leadtime(self):
		"""Test that ssm_serial.optimize_base_stock_levels() works when LT = 0. 
		(Issue 173 reported that this produced an error.)
		"""
		print_status('TestIssue173', 'test_zero_leadtime()')

		# Build network.
		network = serial_system(
			num_nodes=2,
			node_order_in_system=[2, 1],
			echelon_holding_cost=[1, 1],
			local_holding_cost=[1, 2],
			shipment_lead_time=[0, 0],
			stockout_cost=2,
			demand_type='N',
			mean=50,
			standard_deviation=10
		)
		# Optimize echelon base-stock levels.
		S_star, C_star = optimize_base_stock_levels(network=network)

		self.assertDictEqual(S_star, {1: 0, 2:0})
		self.assertEqual(C_star, 0)

	def test_one_zero_leadtime(self):
		"""Test that ssm_serial.optimize_base_stock_levels() works when one LT = 0 and the
		other is non-zero.
		"""
		print_status('TestIssue173', 'test_one_zero_leadtime()')

		# Build network.
		network = serial_system(
			num_nodes=2,
			node_order_in_system=[2, 1],
			echelon_holding_cost=[1, 1],
			local_holding_cost=[1, 2],
			shipment_lead_time=[0, 1],
			stockout_cost=2,
			demand_type='N',
			mean=50,
			standard_deviation=10
		)
		# Optimize echelon base-stock levels. 
		# Just make sure no error raised.
		S_star, C_star = optimize_base_stock_levels(network=network)

class TestNewsvendorHeuristic(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestNewsvendorHeuristic', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestNewsvendorHeuristic', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that newsvendor_heuristic() correctly optimizes
		network in Example 6.1.
		"""

		print_status('TestNewsvendorHeuristic', 'test_example_6_1()')

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_heur = newsvendor_heuristic(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None)
		correct_S_heur = [0, 6.490880975286938, 12.027434723327854, 22.634032391786285]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

	def test_example_6_1_from_network(self):
		"""Test that newsvendor_heuristic() correctly optimizes
		network in Example 6.1 when provided as a network object.
		"""

		print_status('TestNewsvendorHeuristic', 'test_example_6_1()')

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_heur = newsvendor_heuristic(network=instance)
		correct_S_heur = [0, 6.490880975286938, 12.027434723327854, 22.634032391786285]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)
		
	def test_example_6_1_alternate_indexing(self):
		"""Test that optimize_base_stock_levels() correctly optimizes
		network in Example 6.1 when different indices are provided.
		"""

		print_status('TestOptimizeBaseStockLevels', 'test_example_6_1_alternate_indexing()')

		instance = load_instance("example_6_1")
		node1 = instance.nodes_by_index[1]
		node2 = instance.nodes_by_index[2]
		node3 = instance.nodes_by_index[3]
		correct_S_heur = [0, 6.490880975286938, 12.027434723327854, 22.634032391786285]

		S_heur = newsvendor_heuristic(num_nodes=3,
			node_order_in_system=[3, 2, 1],
			node_order_in_lists=[1, 2, 3],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source])
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

		S_heur = newsvendor_heuristic(num_nodes=3,
			node_order_in_lists=[1, 2, 3],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source])
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 3, 2: 2, 3: 1})
		S_heur = newsvendor_heuristic(num_nodes=3,
			node_order_in_system=[1, 2, 3],
			node_order_in_lists=[3, 2, 1],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source])
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[4-n], places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 3, 2: 2, 3: 1})
		S_heur = newsvendor_heuristic(num_nodes=3,
			node_order_in_system=[1, 2, 3],
			echelon_holding_cost=[node3.echelon_holding_cost, node2.echelon_holding_cost, node1.echelon_holding_cost],
			lead_time=[node3.lead_time, node2.lead_time, node1.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node3.demand_source, node2.demand_source, node1.demand_source])
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[4-n], places=5)

		temp_instance = copy.deepcopy(instance)
		temp_instance.reindex_nodes({1: 7, 2: 3, 3: 15})
		S_heur = newsvendor_heuristic(num_nodes=3,
			node_order_in_system=[15, 3, 7],
			node_order_in_lists=[7, 3, 15],
			echelon_holding_cost=[node1.echelon_holding_cost, node3.echelon_holding_cost, node3.echelon_holding_cost],
			lead_time=[node1.lead_time, node2.lead_time, node3.lead_time],
			stockout_cost=node1.stockout_cost,
			demand_source=[node1.demand_source, node2.demand_source, node3.demand_source])
		self.assertAlmostEqual(S_heur[7], correct_S_heur[1], places=5)
		self.assertAlmostEqual(S_heur[3], correct_S_heur[2], places=5)
		self.assertAlmostEqual(S_heur[15], correct_S_heur[3], places=5)
		
	def test_problem_6_1(self):
		"""Test that newsvendor_heuristic() correctly optimizes network in
		Problem 6.1.
		"""

		print_status('TestNewsvendorHeuristic', 'test_problem_6_1()')

		instance = load_instance("problem_6_1")

		S_heur = newsvendor_heuristic(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None)
		correct_S_heur = [0, 123.4708970704270, 228.8600539144440]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)


	def test_problem_6_2a(self):
		"""Test that newsvendor_heuristic() correctly optimizes network in
		Problem 6.2a.
		"""

		print_status('TestNewsvendorHeuristic', 'test_problem_6_2a()')

		instance = load_instance("problem_6_2a")

		S_heur = newsvendor_heuristic(
			num_nodes=len(instance.nodes),
			echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
			lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
			stockout_cost=instance.nodes_by_index[1].stockout_cost,
			demand_mean=instance.nodes_by_index[1].demand_source.mean,
			demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
			demand_source=None)
		correct_S_heur = [0, 40.5867040168793, 74.4580698705858, 109.5962562657559, 142.8985667640439, 175.8329858066735]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

	def test_problem_6_2b(self):
		"""Test that newsvendor_heuristic() correctly optimizes network in
		Problem 6.2b.
		"""

		print_status('TestNewsvendorHeuristic', 'test_problem_6_2b()')

		instance = load_instance("problem_6_2b")

		S_heur = newsvendor_heuristic(network=instance)
		correct_S_heur = [0, 41, 74.5, 110, 143, 175.5]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

	def test_rounding(self):
		"""Test that newsvendor_heuristic() handles rounding correctly.
		"""
		print_status('TestNewsvendorHeuristic', 'test_problem_6_2a()')

		instance = load_instance("example_6_1")

		S_heur_up = newsvendor_heuristic(network=instance, round_type='up')
		self.assertDictEqual(S_heur_up, {1: 7, 2: 13, 3: 23})

		S_heur_down = newsvendor_heuristic(network=instance, round_type='down')
		self.assertDictEqual(S_heur_down, {1: 6, 2: 12, 3: 22})

		S_heur_nearest = newsvendor_heuristic(network=instance, round_type='nearest')
		self.assertDictEqual(S_heur_nearest, {1: 6, 2: 12, 3: 23})

		S_heur_none = newsvendor_heuristic(network=instance, round_type=None)
		correct_S_heur = [0, 6.490880975286938, 12.027434723327854, 22.634032391786285]
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur_none[n], correct_S_heur[n], places=5)

	def test_example_6_1_uniform(self):
		"""Test that newsvendor_heuristic() correctly optimizes
		network in Example 6.1 with uniform demands.
		"""

		print_status('TestNewsvendorHeuristic', 'test_example_6_1_uniform()')

		instance = load_instance("example_6_1")
#		instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		for n in instance.nodes:
			if n.index == 1:
				demand_source = DemandSource()
				demand_source.type = 'UC'
				demand_source.lo = 5 - math.sqrt(12) / 2
				demand_source.hi = 5 + math.sqrt(12) / 2
			else:
				demand_source = None
			n.demand_source = demand_source

		S_heur = newsvendor_heuristic(network=instance)

		correct_S_heur = {1: 6.473020278022186, 2: 12.06630336694632, 3: 22.668511750026827}
		for n in instance.node_indices:
			self.assertAlmostEqual(S_heur[n], correct_S_heur[n], places=5)

	def test_shang_song_instances(self):
		"""Test that newsvendor_heuristic() correctly optimizes Shang-Song instances.
		"""

		print_status('TestNewsvendorHeuristic', 'test_shang_song_instances()')

		instance = load_instance("shang_song_1")
		S_heur = newsvendor_heuristic(network=instance, round_type='down')
		correct_S_heur = {1: 8, 2: 13, 3: 18, 4: 22}
		self.assertDictEqual(S_heur, correct_S_heur)
		C_heur = expected_cost(S_heur, network=instance)
		self.assertAlmostEqual(C_heur, 12.688, places=1)

		instance = load_instance("shang_song_9")
		S_heur = newsvendor_heuristic(network=instance, round_type='down')
		correct_S_heur = {1: 9, 2: 10, 3: 14, 4: 20}
		self.assertDictEqual(S_heur, correct_S_heur)
		C_heur = expected_cost(S_heur, network=instance)
		self.assertAlmostEqual(C_heur, 53.258, places=1)

		instance = load_instance("shang_song_17")
		S_heur = newsvendor_heuristic(network=instance, round_type='up')
		correct_S_heur = {1: 11, 2: 17, 3: 22, 4: 27}
		self.assertDictEqual(S_heur, correct_S_heur)
		C_heur = expected_cost(S_heur, network=instance)
		self.assertAlmostEqual(C_heur, 16.206, places=1)

		instance = load_instance("shang_song_25")
		S_heur = newsvendor_heuristic(network=instance, round_type='up')
		correct_S_heur = {1: 11, 2: 14, 3: 19, 4: 26}
		self.assertDictEqual(S_heur, correct_S_heur)
		C_heur = expected_cost(S_heur, network=instance)
		self.assertAlmostEqual(C_heur, 74.747, places=1)

	def test_bad_parameters(self):
		"""Test that newsvendor_heuristic() correctly raises exceptions if
		bad parameters are given.
		"""

		print_status('TestNewsvendorHeuristic', 'test_bad_parameters()')

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[2].shipment_lead_time = -20
		with self.assertRaises(ValueError):
			S_heur = newsvendor_heuristic(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				demand_source=None)
		
		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].stockout_cost = None
		with self.assertRaises(ValueError):
			S_heur = newsvendor_heuristic(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				demand_source=None)

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].stockout_cost = -2
		with self.assertRaises(ValueError):
			S_heur = newsvendor_heuristic(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				demand_source=None)

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[2].echelon_holding_cost = None
		with self.assertRaises(ValueError):
			S_heur = newsvendor_heuristic(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=instance.nodes_by_index[1].demand_source.mean,
				demand_standard_deviation=instance.nodes_by_index[1].demand_source.standard_deviation,
				demand_source=None)

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})
		instance.nodes_by_index[1].demand_source = None
		instance.nodes_by_index[1].demand_mean = None
		instance.nodes_by_index[1].demand_standard_deviation = 10
		with self.assertRaises(ValueError):
			S_heur = newsvendor_heuristic(
				num_nodes=len(instance.nodes),
				echelon_holding_cost={node.index: node.echelon_holding_cost for node in instance.nodes},
				lead_time={node.index: node.shipment_lead_time for node in instance.nodes},
				stockout_cost=instance.nodes_by_index[1].stockout_cost,
				demand_mean=None,
				demand_standard_deviation=10,
				demand_source=None)


class TestExpectedCost(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExpectedCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExpectedCost', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that expected_cost() correctly calculates cost for
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestExpectedCost', 'test_example_6_1()')

		instance = load_instance("example_6_1")
		#instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_echelon = {1: 4, 2: 9, 3: 10}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 402.3432419162113)
#		self.assertAlmostEqual(cost, 4.025320847013973e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 320.6804885397852)
#		self.assertAlmostEqual(cost, 3.227131745107600e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 631.0057613782569)
#		self.assertAlmostEqual(cost, 6.292579915269251e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_problem_6_1(self):
		"""Test that expected_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedCost', 'test_problem_6_1()')

		instance = load_instance("problem_6_1")

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 168.53138639129807)
#		self.assertAlmostEqual(cost, 1.693611203524711e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 50, 2: 125}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 1219.2749858854334)
#		self.assertAlmostEqual(cost, 1.218952430250280e+03)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 75, 2: 50}
		cost = expected_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 2372.8522046052517)
#		self.assertAlmostEqual(cost, 2.378816200366911e+03)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()


class TestExpectedHoldingCost(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestExpectedHoldingCost', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestExpectedHoldingCost', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that expected_holding_cost() correctly calculates cost for
		a few different sets of BS levels for network in Example 6.1.
		"""

		print_status('TestExpectedHoldingCost', 'test_example_6_1()')

		instance = load_instance("example_6_1")
	#	instance.reindex_nodes({0: 1, 1: 2, 2: 3})

		S_echelon = {1: 4, 2: 9, 3: 10}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 29.94926804079309)
#		self.assertAlmostEqual(cost, 29.979059977933002)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 10, 2: 10, 3: 12}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 29.94946588408094)
#		self.assertAlmostEqual(cost, 30.013403869820511)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 3, 2: -1, 3: 4}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 29.949464010124)
#		self.assertAlmostEqual(cost, 29.986925977144374)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

	def test_problem_6_1(self):
		"""Test that expected_holding_cost() correctly calculates cost for
		a few different sets of BS levels for network in Problem 6.1.
		"""

		print_status('TestExpectedHoldingCost', 'test_problem_6_1()')

		instance = load_instance("problem_6_1")

		S_echelon = {1: 1.242440692221066e+02, 2: 2.287925107043527e+02}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 153.53208747149978)
#		self.assertAlmostEqual(cost, 1.526476024969551e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 50, 2: 125}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 100.34966244137183)
#		self.assertAlmostEqual(cost, 1.002946042252444e+02)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()

		S_echelon = {1: 75, 2: 50}
		cost = expected_holding_cost(S_echelon, network=instance, x_num=100, d_num=10,
			ltd_lower_tail_prob=1-stats.norm.cdf(4),
			ltd_upper_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_lower_tail_prob=1-stats.norm.cdf(4),
			sum_ltd_upper_tail_prob=1-stats.norm.cdf(4))
		self.assertAlmostEqual(cost, 100.00285706997458)
#		self.assertAlmostEqual(cost, 99.997129696149514)	# before changing sum_ltd_dist.mean() to sum_ltd_hi in optimize_base_stock_levels()


