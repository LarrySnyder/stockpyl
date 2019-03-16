import unittest
import numpy as np
import networkx as nx

from inventory import gsm_tree


# Class-level data objects. (Data will be filled in setUp functions.)
instance_figure_6_12 = nx.DiGraph()
instance_example_6_5 = nx.DiGraph()
instance_figure_6_4 = nx.DiGraph()
instance_figure_6_14 = nx.DiGraph()
instance_problem_6_9 = nx.DiGraph()


# Utility functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_tree   class : {:30s} function : {:30s}".format(class_name, function_name))


def dict_match(d1, d2, require_presence=False):
	"""Check whether two dicts have equal keys and values.

	A missing key is treated as 0 if the key is present in the other dict,
	unless require_presence is True, in which case the dict must have the
	key to count as a match.

	Parameters
	----------
	d1 : node
		First dict for comparison.
	d2 : node
		Second dict for comparison.
	require_presence : bool, optional
		Set to True to require dicts to have the same keys, or False
		(default) to treat missing keys as 0s.
	"""

	match = True

	# Check d1 against d2.
	for key in d1.keys():
		if key in d2:
			if d1[key] != d2[key]:
				match = False
		else:
			if d1[key] != 0 or require_presence:
				match = False

	# Check d2 against d1.
	for key in d2.keys():
		if key in d2:
			# We already checked in this case.
			pass
		else:
			if d2[key] != 0 or require_presence:
				match = False

	return match


# Module-level functions.

def setUpModule():
	"""Called once, before anything else in this module."""
	print_status('---', 'setUpModule()')

	# Build instance corresponding to network in Figure 6.12.
	instance_figure_6_12.add_nodes_from(range(1, 8))
	instance_figure_6_12.add_edge(1, 2)
	instance_figure_6_12.add_edge(1, 3)
	instance_figure_6_12.add_edge(3, 5)
	instance_figure_6_12.add_edge(4, 5)
	instance_figure_6_12.add_edge(5, 6)
	instance_figure_6_12.add_edge(5, 7)

	# Build instance corresponding to Example 6.5.
	instance_example_6_5.add_node(1, processing_time=2,
								  external_lead_time=1,
								  holding_cost=1)
	instance_example_6_5.add_node(2, processing_time=1,
								  external_committed_service_time=0,
								  holding_cost=3,
								  external_demand_standard_deviation=1)
	instance_example_6_5.add_node(3, processing_time=1,
								  holding_cost=2)
	instance_example_6_5.add_node(4, processing_time=1,
								  external_committed_service_time=1,
								  holding_cost=3,
								  external_demand_standard_deviation=1)
	instance_example_6_5.add_edge(1, 3)
	instance_example_6_5.add_edge(3, 2)
	instance_example_6_5.add_edge(3, 4)

	# Build instance corresponding to Figure 6.14.
	# Must be relabeled before used.
	instance_figure_6_14.add_node('Raw_Material', processing_time=2, holding_cost=1)
	instance_figure_6_14.add_node('Process_Wafers', processing_time=3, holding_cost=3)
	instance_figure_6_14.add_node('Package_Test_Wafers', processing_time=2, holding_cost=4)
	instance_figure_6_14.add_node('Imager_Base', processing_time=4, holding_cost=6)
	instance_figure_6_14.add_node('Imager_Assembly', processing_time=2, holding_cost=12)
	instance_figure_6_14.add_node('Ship_to_Final_Assembly', processing_time=3, holding_cost=13)
	instance_figure_6_14.add_node('Camera', processing_time=6, holding_cost=20)
	instance_figure_6_14.add_node('Circuit_Board', processing_time=4, holding_cost=8)
	instance_figure_6_14.add_node('Other_Parts', processing_time=3, holding_cost=4)
	instance_figure_6_14.add_node('Build_Test_Pack', processing_time=2,
								  holding_cost=50,
								  external_committed_service_time=2,
								  external_demand_standard_deviation=10)
	instance_figure_6_14.add_edge('Raw_Material', 'Process_Wafers')
	instance_figure_6_14.add_edge('Process_Wafers', 'Package_Test_Wafers')
	instance_figure_6_14.add_edge('Package_Test_Wafers', 'Imager_Assembly')
	instance_figure_6_14.add_edge('Imager_Base', 'Imager_Assembly')
	instance_figure_6_14.add_edge('Imager_Assembly', 'Ship_to_Final_Assembly')
	instance_figure_6_14.add_edge('Camera', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Ship_to_Final_Assembly', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Circuit_Board', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Other_Parts', 'Build_Test_Pack')

	# Build instance corresponding to Problem 6.9.
	# Must be relabeled before used.
	instance_problem_6_9.add_node(1, processing_time=7,
								  holding_cost=220,
								  external_committed_service_time=3,
								  external_demand_mean=22.0,
								  external_demand_standard_deviation=4.1)
	instance_problem_6_9.add_node(2, processing_time=7,
								  holding_cost=140,
								  external_committed_service_time=3,
								  external_demand_mean=15.3,
								  external_demand_standard_deviation=6.2)
	instance_problem_6_9.add_node(3, processing_time=21, holding_cost=90)
	instance_problem_6_9.add_node(4, processing_time=3, holding_cost=5)
	instance_problem_6_9.add_node(5, processing_time=8, holding_cost=20)
	instance_problem_6_9.add_node(6, processing_time=2, holding_cost=7.5)
	instance_problem_6_9.add_edge(6, 5)
	instance_problem_6_9.add_edge(4, 3)
	instance_problem_6_9.add_edge(5, 3)
	instance_problem_6_9.add_edge(3, 1)
	instance_problem_6_9.add_edge(3, 2)


def tearDownModule():
	"""Called once, after everything else in this module."""
	print_status('---', 'tearDownModule()')


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

		eq_d1_d2 = dict_match(d1, d2)
		eq_d1_d3 = dict_match(d1, d3)

		self.assertEqual(eq_d1_d2, False)
		self.assertEqual(eq_d1_d3, True)

	def test_missing_key(self):
		"""Test that dict_match() returns correct results if a key is
		missing.
		"""
		print_status('TestNodeMatch', 'test_missing_key()')

		d1 = {'k1': 3, 'k2': 0}
		d2 = {'k1': 3}

		eq_require_presence_t = dict_match(d1, d2, True)
		eq_require_presence_f = dict_match(d1, d2, False)

		self.assertEqual(eq_require_presence_t, False)
		self.assertEqual(eq_require_presence_f, True)


class TestRelabelNodes(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestRelabelNodes', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestRelabelNodes', 'tearDownClass()')

	def test_figure_6_12(self):
		"""Test that relabel_nodes() correctly relabels network
		in Figure 6.12.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_12()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_12, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = nx.DiGraph()
		correct_G.add_nodes_from(range(1, 8))
		correct_original_labels = {2: 1, 1: 2, 3: 3, 4: 4, 6: 5, 5: 6, 7: 7}
		nx.set_node_attributes(correct_G, correct_original_labels,
							   'original_label')
		correct_G.add_edge(2, 1)
		correct_G.add_edge(2, 3)
		correct_G.add_edge(3, 6)
		correct_G.add_edge(4, 6)
		correct_G.add_edge(6, 5)
		correct_G.add_edge(6, 7)

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))

	def test_example_6_5(self):
		"""Test that relabel_nodes() correctly relabels network in Example 6.13.
		"""

		print_status('TestRelabelNodes', 'test_example_6_5()')

		new_G = gsm_tree.relabel_nodes(instance_example_6_5, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = nx.DiGraph()
		correct_G.add_nodes_from(range(1, 5))
		correct_original_labels = {1: 1, 2: 2, 3: 3, 4: 4}
		nx.set_node_attributes(correct_G, correct_original_labels,
							   'original_label')
		correct_G.add_edge(1, 3)
		correct_G.add_edge(3, 2)
		correct_G.add_edge(3, 4)

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))

	def test_figure_6_14(self):
		"""Test that relabel_nodes() correctly relabels network in Figure 6.14.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = instance_figure_6_14.copy()
		correct_labels = {'Raw_Material': 1, 'Process_Wafers': 2, 'Package_Test_Wafers': 3,
						  'Imager_Base': 4, 'Imager_Assembly': 5, 'Ship_to_Final_Assembly': 6,
						  'Camera': 7, 'Circuit_Board': 8, 'Other_Parts': 9,
						  'Build_Test_Pack': 10}
		correct_G = nx.relabel_nodes(correct_G, correct_labels)
		correct_original_labels = {correct_labels[k]: k for k in
								   instance_figure_6_14.nodes}
		nx.set_node_attributes(correct_G, correct_original_labels,
							   'original_label')

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))

	def test_problem_6_9(self):
		"""Test that relabel_nodes() correctly relabels network in Problem 6.9.
		"""

		print_status('TestRelabelNodes', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(instance_problem_6_9, start_index=0)

		# Build correct relabeled network, and list of correct labels.
		correct_G = instance_problem_6_9.copy()
		correct_labels = {1: 0, 2: 1, 3: 3, 4: 2, 5: 4, 6: 5}
		correct_G = nx.relabel_nodes(correct_G, correct_labels)
		correct_original_labels = {correct_labels[k]: k for k in
								   instance_problem_6_9.nodes}
		nx.set_node_attributes(correct_G, correct_original_labels,
							   'original_label')

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))


class TestFindLargerAdjacentNodes(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestFindLargerAdjacentNodes', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestFindLargerAdjacentNodes', 'tearDownClass()')

	def test_figure_6_12(self):
		"""Test that find_larger_adjacent_nodes() works for relabeled network
		in Figure 6.12.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_figure_6_12()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_12, start_index=1)
		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 2, 2: 3, 3: 6, 4: 6, 5: 6, 6: 7}
		correct_downstream = {1: False, 2: True, 3: True, 4: True, 5: False, 6: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_example_6_5(self):
		"""Test that find_larger_adjacent_nodes() works for network in Example 6.5.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_example_6_5()')

		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(instance_example_6_5)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 3, 2: 3, 3: 4}
		correct_downstream = {1: True, 2: False, 3: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_figure_6_14(self):
		"""Test that find_larger_adjacent_nodes() works for network in Figure 6.14.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)
		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 2, 2: 3, 3: 5, 4: 5, 5: 6, 6: 10, 7: 10, 8: 10, 9: 10}
		correct_downstream = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)

	def test_problem_6_9(self):
		"""Test that find_larger_adjacent_nodes() works for network in Problem 6.9.
		"""

		print_status('TestFindLargerAdjacentNodes', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(instance_problem_6_9)
		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {0: 3, 1: 3, 2: 3, 3: 4, 4: 5}
		correct_downstream = {0: False, 1: False, 2: True, 3: False, 4: False}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)


class TestLongestPath(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestLongestPath', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestLongestPath', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that find_larger_adjacent_nodes() works for network in Example 6.5.
		"""

		print_status('TestLongestPath', 'test_example_6_5()')

		longest_lengths = gsm_tree.longest_paths(instance_example_6_5)

		# Build correct dictionary.
		correct_longest_lengths = {1: 3, 2: 5, 3: 4, 4: 5}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)

	def test_figure_6_14(self):
		"""Test that find_larger_adjacent_nodes() works for network in Figure 6.14.
		"""

		print_status('TestLongestPath', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)
		longest_lengths = gsm_tree.longest_paths(new_G)

		# Build correct dictionary.
		correct_longest_lengths = {1: 2, 2: 5, 3: 7, 4: 4, 5: 9, 6: 12, 7: 6, 8: 4, 9: 3, 10: 14}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)

	def test_problem_6_9(self):
		"""Test that find_larger_adjacent_nodes() works for network in Problem 6.9.
		"""

		print_status('TestLongestPath', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(instance_problem_6_9)
		longest_lengths = gsm_tree.longest_paths(new_G)

		# Build correct dictionary.
		correct_longest_lengths = {0: 38, 1: 38, 2: 3, 3: 31, 4: 10, 5: 2}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)


class TestNetDemand(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestNetDemand', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestNetDemand', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that net_demand() works for network in Example 6.5.
		"""

		print_status('TestNetDemand', 'test_example_6_5()')

		net_means, net_standard_deviations = gsm_tree.net_demand(instance_example_6_5)

		# Build correct dictionaries.
		correct_net_means = {k: 0 for k in instance_example_6_5.nodes}
		correct_net_standard_deviations = {1: np.sqrt(2), 2: 1, 3: np.sqrt(2),
										   4: 1}

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)

	def test_figure_6_14(self):
		"""Test that net_demand() works for network in Figure 6.14.
		"""

		print_status('TestNetDemand', 'test_figure_6_14()')

		new_G = gsm_tree.relabel_nodes(instance_figure_6_14)
		net_means, net_standard_deviations = gsm_tree.net_demand(new_G)

		# Build correct dictionaries.
		correct_net_means = {k: 0 for k in new_G.nodes}
		correct_net_standard_deviations = {k: 10 for k in new_G.nodes}

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)

	def test_problem_6_9(self):
		"""Test that net_demand() works for network in Problem 6.9.
		"""

		print_status('TestNetDemand', 'test_problem_6_9()')

		new_G = gsm_tree.relabel_nodes(instance_problem_6_9)
		net_means, net_standard_deviations = gsm_tree.net_demand(new_G)

		# Build correct dictionaries.
		correct_net_means = {0: 22.0, 1: 15.3}
		correct_net_standard_deviations = {0: 4.1, 1: 6.2}
		for k in range(2, 6):
			correct_net_means[k] = 22.0 + 15.3
			correct_net_standard_deviations[k] = np.sqrt(4.1**2 + 6.2**2)

		self.assertDictEqual(net_means, correct_net_means)
		self.assertDictEqual(net_standard_deviations,
							 correct_net_standard_deviations)


class TestPreprocessTree(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		print_status('TestPreprocessTree', 'setUpClass()')

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		print_status('TestPreprocessTree', 'tearDownClass()')

	def test_example_6_5(self):
		"""Test that preprocess_tree() works for network in Example 6.5.
		"""

		print_status('TestPreprocessTree', 'test_example_6_5()')

		new_tree = gsm_tree.preprocess_tree(instance_example_6_5, start_index=1)

		# Build correct tree.
		correct_tree = nx.DiGraph()
		correct_tree.add_node(1, processing_time=2,
							external_lead_time=1,
							holding_cost=1,
							original_label=1,
						  	net_demand_standard_deviation=np.sqrt(2),
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=3)
		correct_tree.add_node(2, processing_time=1,
							external_committed_service_time=0,
							holding_cost=3,
							original_label=2,
							external_demand_standard_deviation=1,
							net_demand_standard_deviation=1,
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=5)
		correct_tree.add_node(3, processing_time=1,
							holding_cost=2,
							original_label=3,
							net_demand_standard_deviation=np.sqrt(2),
							larger_adjacent_node=4,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=4)
		correct_tree.add_node(4, processing_time=1,
							external_committed_service_time=1,
							holding_cost=3,
							original_label=4,
							external_demand_standard_deviation=1,
							net_demand_standard_deviation=1,
							max_replenishment_time=5)
		correct_tree.add_edge(1, 3)
		correct_tree.add_edge(3, 2)
		correct_tree.add_edge(3, 4)

		trees_equal = nx.is_isomorphic(new_tree, correct_tree, dict_match, dict_match)

		self.assertEqual(trees_equal, True)

	def test_figure_6_14(self):
		"""Test that preprocess_tree() works for network in Figure 6.14.
		"""

		print_status('TestPreprocessTree', 'test_figure_6_14()')

		new_tree = gsm_tree.preprocess_tree(instance_figure_6_14, start_index=1)

		# Build correct tree.
		correct_tree = nx.DiGraph()
		correct_tree.add_node(1, processing_time=2,
							  holding_cost=1,
							  original_label='Raw_Material',
							  net_demand_standard_deviation=10,
							  larger_adjacent_node=2,
							  larger_adjacent_node_is_downstream=True,
							  max_replenishment_time=2)
		correct_tree.add_node(2, processing_time=3,
							holding_cost=3,
							original_label='Process_Wafers',
							net_demand_standard_deviation=10,
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=5)
		correct_tree.add_node(3, processing_time=2,
							holding_cost=4,
							original_label='Package_Test_Wafers',
							net_demand_standard_deviation=10,
							larger_adjacent_node=5,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=7)
		correct_tree.add_node(4, processing_time=4,
							holding_cost=6,
							original_label='Imager_Base',
							net_demand_standard_deviation=10,
							larger_adjacent_node=5,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=4)
		correct_tree.add_node(5, processing_time=2,
							holding_cost=12,
							original_label='Imager_Assembly',
							net_demand_standard_deviation=10,
							larger_adjacent_node=6,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=9)
		correct_tree.add_node(6, processing_time=3,
							holding_cost=13,
							original_label='Ship_to_Final_Assembly',
							net_demand_standard_deviation=10,
							larger_adjacent_node=10,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=12)
		correct_tree.add_node(7, processing_time=6,
							holding_cost=20,
							original_label='Camera',
							net_demand_standard_deviation=10,
							larger_adjacent_node=10,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=6)
		correct_tree.add_node(8, processing_time=4,
							holding_cost=8,
							original_label='Circuit_Board',
							net_demand_standard_deviation=10,
							larger_adjacent_node=10,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=4)
		correct_tree.add_node(9, processing_time=3,
							holding_cost=4,
							original_label='Other_Parts',
							net_demand_standard_deviation=10,
							larger_adjacent_node=10,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=3)
		correct_tree.add_node(10, processing_time=2,
							holding_cost=50,
							original_label='Build_Test_Pack',
							external_committed_service_time=2,
							external_demand_standard_deviation=10,
							net_demand_standard_deviation=10,
							max_replenishment_time=14)
		correct_tree.add_edge(1, 2)
		correct_tree.add_edge(2, 3)
		correct_tree.add_edge(3, 5)
		correct_tree.add_edge(4, 5)
		correct_tree.add_edge(5, 6)
		correct_tree.add_edge(7, 10)
		correct_tree.add_edge(6, 10)
		correct_tree.add_edge(8, 10)
		correct_tree.add_edge(9, 10)

		trees_equal = nx.is_isomorphic(new_tree, correct_tree, dict_match, dict_match)

		self.assertEqual(trees_equal, True)

	def test_problem_6_9(self):
		"""Test that preprocess_tree() works for network in Problem 6.9.
		"""

		print_status('TestPreprocessTree', 'test_problem_6_9()')

		new_tree = gsm_tree.preprocess_tree(instance_problem_6_9)

		# Build correct tree.
		correct_tree = nx.DiGraph()
		correct_tree.add_node(0, processing_time=7,
							holding_cost=220,
							original_label=1,
							external_demand_mean=22.0,
							external_demand_standard_deviation=4.1,
							external_committed_service_time=3,
							net_demand_mean=22.0,
						  	net_demand_standard_deviation=4.1,
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=38)
		correct_tree.add_node(1, processing_time=7,
							holding_cost=140,
							original_label=2,
							external_demand_mean=15.3,
							external_demand_standard_deviation=6.2,
							external_committed_service_time=3,
							net_demand_mean=15.3,
							net_demand_standard_deviation=6.2,
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=38)
		correct_tree.add_node(2, processing_time=3,
							holding_cost=5,
							original_label=4,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=np.sqrt(4.1**2+6.2**2),
							larger_adjacent_node=3,
							larger_adjacent_node_is_downstream=True,
							max_replenishment_time=3)
		correct_tree.add_node(3, processing_time=21,
							holding_cost=90,
							original_label=3,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=np.sqrt(4.1**2+6.2**2),
							larger_adjacent_node=4,
							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=31)
		correct_tree.add_node(4, processing_time=8,
							holding_cost=20,
							original_label=5,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=np.sqrt(4.1**2+6.2**2),
							larger_adjacent_node=5,
							larger_adjacent_node_is_downstream=False,
							max_replenishment_time=10)
		correct_tree.add_node(5, processing_time=2,
							holding_cost=7.5,
							original_label=6,
							net_demand_mean=22.0+15.3,
							net_demand_standard_deviation=np.sqrt(4.1**2+6.2**2),
							max_replenishment_time=2)
		correct_tree.add_edge(5, 4)
		correct_tree.add_edge(2, 3)
		correct_tree.add_edge(4, 3)
		correct_tree.add_edge(3, 0)
		correct_tree.add_edge(3, 1)

		trees_equal = nx.is_isomorphic(new_tree, correct_tree, dict_match, dict_match)

		self.assertEqual(trees_equal, True)
