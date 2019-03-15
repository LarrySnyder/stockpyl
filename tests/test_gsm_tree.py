import unittest
import inspect
import networkx as nx

from inventory import gsm_tree


# Class-level data objects. (Data will be filled in setUp functions.)
instance_figure_6_12 = nx.DiGraph()
instance_example_6_5 = nx.DiGraph()
instance_figure_6_4 = nx.DiGraph()
instance_figure_6_14 = nx.DiGraph()


def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_gsm_tree   class : {:30s} function : {:30s}".format(class_name, function_name))


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
	instance_example_6_5.add_node(1, processing_time=2, external_lead_time=1, holding_cost=1)
	instance_example_6_5.add_node(2, processing_time=1, external_committed_service_time=0, holding_cost=3)
	instance_example_6_5.add_node(3, processing_time=1, holding_cost=2)
	instance_example_6_5.add_node(4, processing_time=1, external_committed_service_time=1, holding_cost=3)
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
	instance_figure_6_14.add_node('Build_Test_Pack', processing_time=2, holding_cost=50, external_committed_service_time=2)
	instance_figure_6_14.add_edge('Raw_Material', 'Process_Wafers')
	instance_figure_6_14.add_edge('Process_Wafers', 'Package_Test_Wafers')
	instance_figure_6_14.add_edge('Package_Test_Wafers', 'Imager_Assembly')
	instance_figure_6_14.add_edge('Imager_Base', 'Imager_Assembly')
	instance_figure_6_14.add_edge('Imager_Assembly', 'Ship_to_Final_Assembly')
	instance_figure_6_14.add_edge('Camera', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Ship_to_Final_Assembly', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Circuit_Board', 'Build_Test_Pack')
	instance_figure_6_14.add_edge('Other_Parts', 'Build_Test_Pack')


def tearDownModule():
	"""Called once, after everything else in this module."""
	print_status('---', 'tearDownModule()')


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
		"""Test that relabel_nodes()  correctly relabels network
		in Figure 6.12.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_12()')

		new_G, new_labels = gsm_tree.relabel_nodes(instance_figure_6_12, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = nx.DiGraph()
		correct_G.add_nodes_from(range(1, 8))
		correct_G.add_edge(2, 1)
		correct_G.add_edge(2, 3)
		correct_G.add_edge(3, 6)
		correct_G.add_edge(4, 6)
		correct_G.add_edge(6, 5)
		correct_G.add_edge(6, 7)
		correct_labels = {1: 2, 2: 1, 3: 3, 4: 4, 5: 6, 6: 5, 7: 7}

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))
		self.assertDictEqual(new_labels, correct_labels)

	def test_example_6_5(self):
		"""Test that relabel_nodes() correctly relabels network in Example 6.13.
		"""

		print_status('TestRelabelNodes', 'test_example_6_5()')

		new_G, new_labels = gsm_tree.relabel_nodes(instance_example_6_5, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = nx.DiGraph()
		correct_G.add_nodes_from(range(1, 5))
		correct_G.add_edge(1, 3)
		correct_G.add_edge(3, 2)
		correct_G.add_edge(3, 4)
		correct_labels = {1: 1, 2: 2, 3: 3, 4: 4}

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))
		self.assertDictEqual(new_labels, correct_labels)

	def test_figure_6_14(self):
		"""Test that relabel_nodes() correctly relabels network in Figure 6.14.
		"""

		print_status('TestRelabelNodes', 'test_figure_6_14()')

		new_G, new_labels = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)

		# Build correct relabeled network, and list of correct labels.
		correct_G = instance_figure_6_14.copy()
		correct_labels = {'Raw_Material': 1, 'Process_Wafers': 2, 'Package_Test_Wafers': 3,
						  'Imager_Base': 4, 'Imager_Assembly': 5, 'Ship_to_Final_Assembly': 6,
						  'Camera': 7, 'Circuit_Board': 8, 'Other_Parts': 9,
						  'Build_Test_Pack': 10}
		correct_G = nx.relabel_nodes(correct_G, correct_labels)

		self.assertSetEqual(set(new_G.edges), set(correct_G.edges))
		self.assertDictEqual(new_labels, correct_labels)


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

		new_G, _ = gsm_tree.relabel_nodes(instance_figure_6_12, start_index=1)
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

		new_G, _ = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)
		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(new_G)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 2, 2: 3, 3: 5, 4: 5, 5: 6, 6: 10, 7: 10, 8: 10, 9: 10}
		correct_downstream = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True}

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

		longest_lengths = gsm_tree.longest_path(instance_example_6_5)

		# Build correct dictionary.
		correct_longest_lengths = {1: 3, 2: 5, 3: 4, 4: 5}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)

	def test_figure_6_14(self):
		"""Test that find_larger_adjacent_nodes() works for network in Figure 6.14.
		"""

		print_status('TestLongestPath', 'test_figure_6_14()')

		new_G, _ = gsm_tree.relabel_nodes(instance_figure_6_14, start_index=1)
		longest_lengths = gsm_tree.longest_path(new_G)

		# Build correct dictionary.
		correct_longest_lengths = {1: 2, 2: 5, 3: 7, 4: 4, 5: 9, 6: 12, 7: 6, 8: 4, 9: 3, 10: 14}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)
