import unittest
import csv
import os

import stockpyl.sim_io as sim_io
from stockpyl.sim import *
from stockpyl.instances import *


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
		# reindex nodes to 2 -> 1 -> 0
		network.reindex_nodes({1: 0, 2: 1, 3: 2})

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)
		filename = 'tests/additional_files/temp_TestWriteResults_test_example_6_1.csv'
		sim_io.write_results(network, 100, 10, True, filename)

		row0 = 't,|i=0,DISR,IO:EXT,IOPL:EXT,OQ:1,OO:1,IS:1,ISPL:1,RM:1,OS:EXT,DMFS,FR,IL,BO:EXT,DI:EXT,HC,SC,ITHC,REV,TC,|i=1,DISR,IO:0,IOPL:EXT,IOPL:0,OQ:2,OO:2,IS:2,ISPL:2,RM:2,OS:0,DMFS,FR,IL,BO:0,DI:0,HC,SC,ITHC,REV,TC,|i=2,DISR,IO:1,IOPL:EXT,IOPL:1,OQ:EXT,OO:EXT,IS:EXT,ISPL:EXT,RM:EXT,OS:1,DMFS,FR,IL,BO:1,DI:1,HC,SC,ITHC,REV,TC'
		row5 = '4,|,False,6.037190468227883,[0],6.037190468227885,6.652501757799978,26.06553892254117,[0.0, 5.066098888673643],0.0,26.06553892254117,5.8746887104279075,0.22398503883788762,-0.16250175779997544,0.16250175779997544,0,0.0,6.032065249535088,0.0,0.0,6.032065249535088,|,False,6.037190468227885,[0],[0],6.037190468227887,7.116402869126333,5.066098888673643,[0.0, 5.623901111326357],0.0,5.066098888673643,4.450787599101552,0.3050545629127044,-1.5864028691263323,1.5864028691263323,0.0,0.0,0.0,20.264395554694573,0.0,20.264395554694573,|,False,6.037190468227887,[0],[0],6.037190468227889,12.18250175779998,5.623901111326357,[0.0, 6.145311289572089, 6.037190468227889],0.0,5.623901111326357,4.544688710427908,0.39831291850351647,-1.4925017577999782,1.492501757799979,0.0,0.0,0.0,11.247802222652714,0.0,11.247802222652714'
		row10 = '98,|,False,4.775201280806586,[0],4.775201280806585,4.775201280806586,5.855972018122079,[0.0, 4.775201280806585],0.0,4.775201280806586,4.775201280806586,0.9274469545198983,1.7147987191934133,0.0,0,12.003591034353892,0.0,0.0,0.0,12.003591034353892,|,False,4.775201280806585,[0],[0],4.775201280806586,4.77520128080658,5.3823688379681025,[0.0, 4.775201280806586],0.0,4.775201280806585,4.775201280806585,0.8746030168684653,0.7547987191934205,0.0,0.0,3.019194876773682,0,19.10080512322634,0.0,22.120000000000022,|,False,4.775201280806586,[0],[0],4.775201280806584,9.156803980142493,5.560039692192106,[0.0, 4.381602699335919, 4.775201280806584],0.0,4.775201280806586,4.775201280806586,0.888642036779627,1.5331960198575052,0.0,0.0,3.0663920397150104,0,9.550402561613172,0.0,12.616794601328182'
		
		# Load results and check them.
		with open(filename) as csvfile:
			reader = csv.reader(csvfile)
			rows = list(reader)

			self.assertEqual(','.join(rows[0]), row0)
			self.assertEqual(','.join(rows[5]), row5)
			self.assertEqual(','.join(rows[10]), row10)

			# Delete file.
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
		header_list = sim_io.dict_to_header_list(network.get_node_from_index(1).state_vars[0].inbound_order, "IO")
		self.assertListEqual(header_list, ['IO:0'])

		# Node 2 IS.
		header_list = sim_io.dict_to_header_list(network.get_node_from_index(2).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

	def test_mwor(self):
		"""Test that dict_to_header_list() function works correctly for an MWOR system.
		"""
		print_status('TestDictToHeaderList', 'test_mwor()')

		# Build network.
		network = mwor_system(3, local_holding_cost=[5, 1, 1, 2],
								demand_type='N',
								demand_mean=10, demand_standard_deviation=2,
								inventory_policy_type='BS',
								base_stock_levels=[10, 10, 10, 10])

		# Simulate and write results.
		simulation(network, 100, rand_seed=17, progress_bar=False)

		# Node 0 IS.
		header_list = sim_io.dict_to_header_list(network.get_node_from_index(0).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:1', 'IS:2', 'IS:3'])

		# Node 2 IS.
		header_list = sim_io.dict_to_header_list(network.get_node_from_index(2).state_vars[0].inbound_shipment, "IS")
		self.assertListEqual(header_list, ['IS:EXT'])

		# Node 0 ISPL.
		header_list = sim_io.dict_to_header_list(network.get_node_from_index(0).state_vars[0].inbound_shipment_pipeline, "ISPL")
		self.assertListEqual(header_list, ['ISPL:1', 'ISPL:2', 'ISPL:3'])
