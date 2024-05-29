import unittest
import csv
import os

import stockpyl.sim_io as sim_io
from stockpyl.sim import *
from stockpyl.instances import *
from stockpyl.disruption_process import DisruptionProcess


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_rq   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class TestWriteResults(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestWriteResults', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestWriteResults', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1.
		"""
		print_status('TestWriteResults', 'test_example_6_1()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_example_6_1'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_example_6_1'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=cols_to_print, 
				write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)
			
			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_example_6_1_suppress_dummy_false(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1.
		"""
		print_status('TestWriteResults', 'test_example_6_1_suppress_dummy_false()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_example_6_1_suppress_dummy_false'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_example_6_1_suppress_dummy_false'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=cols_to_print, 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)
			
			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_periods_to_print(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when periods_to_print is specified as a list.
		"""
		print_status('TestWriteResults', 'test_periods_to_print()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_periods_to_print'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_periods_to_print'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=[2, 7, 43], columns_to_print=cols_to_print, 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_all(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is 'all'.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_all()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_all'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		# Same correct file as for test_columns_to_print_none.
		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_none'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print='all', 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_none(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is None.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_none()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_none'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_none'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=None, 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_list(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_list()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_list'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_list'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['IO', 'OQ', 'IL', 'TC'], 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)
			
			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_string(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a string.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_string()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_string'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_string'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print='basic', 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_list_of_strings(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list of strings.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_list_of_strings()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_list_of_strings'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_list_of_strings'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['basic', 'costs'], 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_mixed(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list that contains
		some column names and some built-in strings.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_mixed()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_mixed'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_mixed'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['SC', 'basic', 'IDI'], 
				write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			# if os.path.exists(txt_filename):
			# 	os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

	def test_columns_to_print_mixed_suppress_dummy_false(self):
		"""Test that write_results() function correctly writes results from
		simulation of Example 6.1 when columns_to_print is specified as a list that contains
		some column names and some built-in strings.
		"""
		print_status('TestWriteResults', 'test_columns_to_print_mixed_suppress_dummy_false()')

		# Build network.
		network = load_instance("example_6_1")

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename_root = 'tests/additional_files/temp_TestWriteResults_test_columns_to_print_mixed_suppress_dummy_false'
		txt_filename = filename_root + '.txt'
		csv_filename = filename_root + '.csv'

		correct_filename_root = 'tests/additional_files/test_sim_io_TestWriteResults_test_columns_to_print_mixed_suppress_dummy_false'
		correct_txt_filename = correct_filename_root + '.txt'
		correct_csv_filename = correct_filename_root + '.csv'

		try:
			sim_io.write_results(network=network, num_periods=100, periods_to_print=10, columns_to_print=['SC', 'basic', 'IDI'], 
				suppress_dummy_products=False, write_txt=True, txt_filename=txt_filename, write_csv=True, csv_filename=csv_filename)

			# Load TXT results and check them.
			with open(txt_filename) as txtfile:
				lines = txtfile.read().splitlines()
			with open(correct_txt_filename) as correct_txtfile:
				correct_lines = correct_txtfile.read().splitlines()
			self.assertListEqual(lines, correct_lines)

			# Load CSV results and check them.
			with open(csv_filename) as csvfile:
				reader = csv.reader(csvfile)
				rows = list(reader)
			with open(correct_csv_filename) as correct_csvfile:
				correct_reader = csv.reader(correct_csvfile)
				correct_rows = list(correct_reader)
			self.assertListEqual(rows, correct_rows)

		finally:
			# Delete files.
			if os.path.exists(txt_filename):
				os.remove(txt_filename)
			if os.path.exists(csv_filename):
				os.remove(csv_filename)

class TestWriteInstanceAndStates(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestWriteInstanceAndStates', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestWriteInstanceAndStates', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Example 6.1.
		"""
		print_status('TestWriteInstanceAndStates', 'test_example_6_1()')

		T = 100

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_example_6_1.json'
		try:
			sim_io.write_instance_and_states(network, filename, 'temp')

			# Correct node 0 demands.
			node0 = network.nodes_by_index[0]
			demand_list = [node0.state_vars[t].inbound_order[None] for t in range(T)]

			# Load instance and check it.
			new_network = load_instance('temp', filename, ignore_state_vars=True)
			self.assertListEqual(new_network.nodes_by_index[0].demand_source.demand_list[0:T], demand_list[0:T])
			# Remove state variables and demand sources and make sure networks are equal otherwise.
			for node in network.nodes:
				node.demand_source = None
				node.state_vars = None
			for node in new_network.nodes:
				node.demand_source = None
				node.state_vars = None
			self.assertTrue(network.deep_equal_to(new_network))

		finally:
			# Delete file.
			if os.path.exists(filename):
				os.remove(filename)
	
	def test_example_6_1_with_disruptions(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Example 6.1 with disruptions.
		"""
		print_status('TestWriteInstanceAndStates', 'test_example_6_1_with_disruptions()')

		T = 100

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})
		# Add disruptions.
		network.nodes_by_index[1].disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_example_6_1_with_disruptions.json'
		try:
			sim_io.write_instance_and_states(network, filename, 'temp')

			# Correct node 0 demands and node 1 disruptions.
			node0 = network.nodes_by_index[0]
			demand_list = [node0.state_vars[t].inbound_order[None] for t in range(T)]
			node1 = network.nodes_by_index[1]
			disruption_list = [node1.state_vars[t].disrupted for t in range(T)]

			# Load instance and check it.
			new_network = load_instance('temp', filename, ignore_state_vars=True)
			self.assertListEqual(new_network.nodes_by_index[0].demand_source.demand_list[0:T], demand_list[0:T])
			self.assertListEqual(new_network.nodes_by_index[1].disruption_process.disruption_state_list[0:T], disruption_list[0:T])
			# Remove state variables, demand sources, and disruption processes and make sure networks are equal otherwise.
			for node in network.nodes:
				node.demand_source = None
				node.state_vars = None
				node.disruption_process = None
			for node in new_network.nodes:
				node.demand_source = None
				node.state_vars = None
				node.disruption_process = None
			self.assertTrue(network.deep_equal_to(new_network))

		finally:
			# Delete file.
			if os.path.exists(filename):
				os.remove(filename)

	def test_rong_atan_snyder_figure_1a(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Rong, Atan, and Snyder Figure 1.
		"""
		print_status('TestWriteInstanceAndStates', 'test_rong_atan_snyder_figure_1a()')

		T = 100

		# Build network.
		network = load_instance("rong_atan_snyder_figure_1a")

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_rong_atan_snyder_figure_1a.json'
		try:
			sim_io.write_instance_and_states(network, filename, 'temp')

			# Correct demands.
			demand_list = {}
			for node in network.nodes:
				if node in network.sink_nodes:
					demand_list[node.index] = [node.state_vars[t].inbound_order[None] for t in range(T)]

			# Load instance and check it.
			new_network = load_instance('temp', filename, ignore_state_vars=True)
			for node in new_network.nodes:
				if node in new_network.sink_nodes:
					self.assertListEqual(node.demand_source.demand_list[0:T], demand_list[node.index][0:T])
			# Remove state variables and demand sources and make sure networks are equal otherwise.
			for node in network.nodes:
				node.demand_source = None
				node.state_vars = None
			for node in new_network.nodes:
				node.demand_source = None
				node.state_vars = None
			self.assertTrue(network.deep_equal_to(new_network))

		finally:
			# Delete file.
			if os.path.exists(filename):
				os.remove(filename)

	def test_rong_atan_snyder_figure_1a_with_disruptions(self):
		"""Test that write_instance_and_states() function correctly writes results from
		simulation of Rong, Atan, and Snyder Figure 1, with disruptions.
		"""
		print_status('TestWriteInstanceAndStates', 'test_rong_atan_snyder_figure_1a_with_disruptions()')

		T = 100

		# Build network.
		network = load_instance("rong_atan_snyder_figure_1a")
		# Add disruptions.
		network.nodes_by_index[1].disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='OP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)
		network.nodes_by_index[3].disruption_process = DisruptionProcess(
			random_process_type='M',
			disruption_type='SP',
			disruption_probability=0.1,
			recovery_probability=0.3
		)

		# Simulate and write results.
		simulation(network, T, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteInstanceAndStates_test_rong_atan_snyder_figure_1a_with_disruptions.json'
		try:
			sim_io.write_instance_and_states(network, filename, 'temp')

			# Correct demands and disruption states.
			demand_list = {}
			disruption_state_list = {}
			for node in network.nodes:
				if node in network.sink_nodes:
					demand_list[node.index] = [node.state_vars[t].inbound_order[None] for t in range(T)]
				if node.disruption_process is not None and node.disruption_process.random_process_type is not None:
					disruption_state_list[node.index] = [node.state_vars[t].disrupted for t in range(T)]

			# Load instance and check it.
			new_network = load_instance('temp', filename, ignore_state_vars=True)
			for node in new_network.nodes:
				if node in new_network.sink_nodes:
					self.assertListEqual(node.demand_source.demand_list[0:T], demand_list[node.index][0:T])
				if node.disruption_process is not None and node.disruption_process.random_process_type is not None:
					self.assertListEqual(node.disruption_process.disruption_state_list[0:T], disruption_state_list[node.index][0:T])
			# Remove state variables, demand sources, and disruption processes and make sure networks are equal otherwise.
			for node in network.nodes:
				node.demand_source = None
				node.state_vars = None
				node.disruption_process = None
			for node in new_network.nodes:
				node.demand_source = None
				node.state_vars = None
				node.disruption_process = None
			self.assertTrue(network.deep_equal_to(new_network))

		finally:
			# Delete file.
			if os.path.exists(filename):
				os.remove(filename)


class TestDictToHeaderList(unittest.TestCase):
	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('TestDictToHeaderList', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('TestDictToHeaderList', 'tear_down_class()')

	def test_example_6_1(self):
		"""Test that dict_to_header_list() function works correctly for
		simulation of Example 6.1. 
		"""
		print_status('TestDictToHeaderList', 'test_example_6_1()')

		# Build network.
		network = load_instance("example_6_1")
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)

		# Node 1 IO.
		header_list = sim_io._dict_to_header_list(network.nodes_by_index[1].state_vars[0].inbound_order, "IO")
		self.assertListEqual(header_list, ['IO:0'])

		# Node 2 IS.
		header_list = sim_io._dict_to_header_list(network.nodes_by_index[2].state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

	def test_mwor(self):
		"""Test that dict_to_header_list() function works correctly for an MWOR system.
		"""
		print_status('TestDictToHeaderList', 'test_mwor()')

		# Build network.
		network = mwor_system(3, node_order_in_lists=[0, 1, 2, 3],
								local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								mean=10, standard_deviation=2,
								policy_type='BS',
								base_stock_level=[10, 10, 10, 10])

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)

		# Node 0 IS.
		header_list = sim_io._dict_to_header_list(network.nodes_by_index[0].state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:1', 'IS:2', 'IS:3'])

		# Node 2 IS.
		header_list = sim_io._dict_to_header_list(network.nodes_by_index[2].state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

		# Node 0 ISPL.
		header_list = sim_io._dict_to_header_list(network.nodes_by_index[0].state_vars[0].inbound_shipment_pipeline, "ISPL")
		self.assertListEqual(header_list, ['ISPL:1', 'ISPL:2', 'ISPL:3'])

