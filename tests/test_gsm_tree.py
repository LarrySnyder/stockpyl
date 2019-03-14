import unittest
import inspect
import networkx as nx

from inventory import gsm_tree


# Class-level data objects. (Data will be filled in setUp functions.)
instance_figure_6_12 = nx.DiGraph()
instance_example_6_5 = nx.DiGraph()
instance_figure_6_4 = nx.DiGraph()


def setUpModule():
	"""Called once, before anything else in this module."""
	log_point('module %s' % __name__)

	# Build instance corresponding to network in Figure 6.12.
	instance_figure_6_12.add_nodes_from(range(1, 8))
	instance_figure_6_12.add_edge(1, 2)
	instance_figure_6_12.add_edge(1, 3)
	instance_figure_6_12.add_edge(3, 5)
	instance_figure_6_12.add_edge(4, 5)
	instance_figure_6_12.add_edge(5, 6)
	instance_figure_6_12.add_edge(5, 7)

	# Build instance corresponding to Example 6.5.
	instance_example_6_5.add_node(1, processing_time=2, external_lead_time=1)
	instance_example_6_5.add_node(2, processing_time=1, external_committed_service_time=0)
	instance_example_6_5.add_node(3, processing_time=1)
	instance_example_6_5.add_node(4, processing_time=1, external_committed_service_time=1)
	instance_example_6_5.add_edge(1, 3)
	instance_example_6_5.add_edge(3, 2)
	instance_example_6_5.add_edge(3, 4)


def tearDownModule():
	"""Called once, after everything else in this module."""
	log_point('module %s' % __name__)


def log_point(context):
	"""Utility function to trace control flow, for module functions and class methods.

	http://pythontesting.net/framework/unittest/unittest-fixtures/
	"""
	calling_function = inspect.stack()[1][3]
	print("in {:s} - {:s}()".format(context, calling_function))


class TestRelabelNodes(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		log_point("class {:s}".format(cls.__name__))

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		log_point("class {:s}".format(cls.__name__))

	def log_point(self):
		"""Utility method to trace control flow.

		http://pythontesting.net/framework/unittest/unittest-fixtures/
		"""
		calling_function = inspect.stack()[1][3]
		current_test = self.id().split('.')[-1]
		print("\nin {:s} - {:s}()".format(current_test, calling_function))

	def test_figure_6_12(self):
		"""Test that relabel_nodes()  correctly relabels network
		in Figure 6.12.
		"""

		self.log_point()

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

		self.log_point()

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


class TestFindLargerAdjacentNodes(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		log_point('class %s' % cls.__name__)

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		log_point('class %s' % cls.__name__)

	def log_point(self):
		"""Utility method to trace control flow.

		http://pythontesting.net/framework/unittest/unittest-fixtures/
		"""
		calling_function = inspect.stack()[1][3]
		current_test = self.id().split('.')[-1]
		print("\nin {:s} - {:s}()".format(current_test, calling_function))

	def test_figure_6_12(self):
		"""Test that find_larger_adjacent_nodes() works for relabeled network
		in Figure 6.12.
		"""

		self.log_point()

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

		self.log_point()

		larger_adjacent, downstream = gsm_tree.find_larger_adjacent_nodes(instance_example_6_5)

		# Build correct dictionaries.
		correct_larger_adjacent = {1: 3, 2: 3, 3: 4}
		correct_downstream = {1: True, 2: False, 3: True}

		self.assertDictEqual(larger_adjacent, correct_larger_adjacent)
		self.assertDictEqual(downstream, correct_downstream)


class TestLongestPath(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Called once, before any tests."""
		log_point('class %s' % cls.__name__)

	@classmethod
	def tearDownClass(cls):
		"""Called once, after all tests, if setUpClass successful."""
		log_point('class %s' % cls.__name__)

	def log_point(self):
		"""Utility method to trace control flow.

		http://pythontesting.net/framework/unittest/unittest-fixtures/
		"""
		calling_function = inspect.stack()[1][3]
		current_test = self.id().split('.')[-1]
		print("\nin {:s} - {:s}()".format(current_test, calling_function))

	def test_example_6_5(self):
		"""Test that find_larger_adjacent_nodes() works for network in Example 6.5.
		"""

		self.log_point()

		longest_lengths = gsm_tree.longest_path(instance_example_6_5)

		# Build correct dictionary.
		correct_longest_lengths = {1: 3, 2: 5, 3: 4, 4: 5}

		self.assertDictEqual(longest_lengths, correct_longest_lengths)
