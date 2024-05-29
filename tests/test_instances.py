import unittest
import json
import os

import stockpyl.instances as instances
from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.sim import simulation
from stockpyl.helpers import deserialize_set


# Module-level functions.

def print_status(class_name, function_name):
	"""Print status message."""
	print("module : test_instances   class : {:30s} function : {:30s}".format(class_name, function_name))


def set_up_module():
	"""Called once, before anything else in this module."""
	print_status('---', 'set_up_module()')


def tear_down_module():
	"""Called once, after everything else in this module."""
	print_status('---', 'tear_down_module()')


class LoadInstance(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('LoadInstance', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('LoadInstance', 'tear_down_class()')

	def test_example_4_2(self):
		"""Test that load_instance() correctly loads Example 6.1.
		"""
		print_status('LoadInstance', 'test_example_6_1()')

		# Load.
		instance = instances.load_instance('example_4_2')

		# Build from scratch.
		correct_instance = {
			"revenue": 1,
			"purchase_cost": 0.3,
			"salvage_value": 0.12,
			"demand_mean": 50,
			"demand_sd": 8
		}

		# Compare.
		self.assertEqual(len(instance), len(correct_instance))
		for attr, value in instance.items():
			self.assertEqual(value, correct_instance[attr])

	def test_example_9_5(self):
		"""Test that load_instance() correctly loads Example 9.5.
		"""
		print_status('LoadInstance', 'test_example_9_5()')

		# Load.
		instance = instances.load_instance('example_9_5')

		# Build from scratch.
		correct_instance = {
			"holding_cost": 0.06,
			"fixed_cost": 18500,
			"demand_rate": 75000,
			"yield_mean": 0.8333333333333334,
			"yield_sd": 0.14085904245475275
		}

		# Compare.
		self.assertEqual(len(instance), len(correct_instance))
		for attr, value in instance.items():
			self.assertEqual(value, correct_instance[attr])

	def test_example_6_1(self):
		"""Test that load_instance() correctly loads Example 6.1.
		"""
		print_status('LoadInstance', 'test_example_6_1()')

		# Load.
		instance = instances.load_instance("example_6_1")

		# Build from scratch.
		from stockpyl.supply_chain_network import serial_system
		correct_instance = serial_system(
			num_nodes=3,
			node_order_in_system=[3, 2, 1],
			echelon_holding_cost={1: 3, 2: 2, 3: 2},
			local_holding_cost={1: 7, 2: 4, 3: 2},
			shipment_lead_time={1: 1, 2: 1, 3: 2},
			stockout_cost={1: 37.12, 2: 0, 3: 0},
			demand_type='N',
			mean=5,
			standard_deviation=1,
			policy_type='BS',
			base_stock_level={1: 6.49, 2: 5.53, 3: 10.69}
		)

		# Compare.
		self.assertTrue(instance.deep_equal_to(correct_instance))

	def test_figure_6_14(self):
		"""Test that load_instance() correctly loads Figure 6.14.
		"""
		print_status('LoadInstance', 'test_figure_6_14()')

		# Load.
		instance = instances.load_instance("figure_6_14")

		# Build from scratch.
		from stockpyl.supply_chain_network import SupplyChainNetwork
		from stockpyl.supply_chain_node import SupplyChainNode
		from stockpyl.demand_source import DemandSource
		from scipy import stats
		correct_instance = SupplyChainNetwork()
		correct_instance.add_node(SupplyChainNode(1, 'Raw_Material', correct_instance, processing_time=2, local_holding_cost=0.01))
		correct_instance.add_node(SupplyChainNode(2, 'Process_Wafers', correct_instance, processing_time=3, local_holding_cost=0.03))
		correct_instance.add_node(SupplyChainNode(3, 'Package_Test_Wafers', correct_instance, processing_time=2, local_holding_cost=0.04))
		correct_instance.add_node(SupplyChainNode(4, 'Imager_Base', correct_instance, processing_time=4, local_holding_cost=0.06))
		correct_instance.add_node(SupplyChainNode(5, 'Imager_Assembly', correct_instance, processing_time=2, local_holding_cost=0.12))
		correct_instance.add_node(SupplyChainNode(6, 'Ship_to_Final_Assembly', correct_instance, processing_time=3, local_holding_cost=0.13))
		correct_instance.add_node(SupplyChainNode(7, 'Camera', correct_instance, processing_time=6, local_holding_cost=0.20))
		correct_instance.add_node(SupplyChainNode(8, 'Circuit_Board', correct_instance, processing_time=4, local_holding_cost=0.08))
		correct_instance.add_node(SupplyChainNode(9, 'Other_Parts', correct_instance, processing_time=3, local_holding_cost=0.04))
		correct_instance.add_node(SupplyChainNode(10, 'Build_Test_Pack', correct_instance, processing_time=2, local_holding_cost=0.50, \
			external_outbound_cst=2, demand_source=DemandSource(type='N', mean=0, standard_deviation=10)))
		for n in correct_instance.nodes:
			n.demand_bound_constant = stats.norm.ppf(0.95)
		correct_instance.add_edges_from_list([(1, 2), (2, 3), (3, 5), (4, 5), (5, 6), (7, 10), (6, 10), (8, 10), (9, 10)])

		# Compare.
		self.assertTrue(instance.deep_equal_to(correct_instance))


class SaveInstance(unittest.TestCase):

	@classmethod
	def set_up_class(cls):
		"""Called once, before any tests."""
		print_status('SaveInstance', 'set_up_class()')

	@classmethod
	def tear_down_class(cls):
		"""Called once, after all tests, if set_up_class successful."""
		print_status('SaveInstance', 'tear_down_class()')

	def test_example_4_2(self):
		"""Test that save_instance() correctly saves Example 6.1.
		"""
		print_status('SaveInstance', 'test_example_6_1()')

		# Load.
		instance = instances.load_instance('example_4_2')

		# Save.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_example_4_2.json'
		instances.save_instance(
			instance_name='test_example_4_2',
			instance_data=instance,
			instance_description='this is test_example_4_2',
			filepath=temp_filename
		)

		# Load saved JSON and correct JSON.
		correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_example_4_2_correct.json'
		with open(temp_filename) as f:
			saved_json = json.load(f, object_hook=deserialize_set)
			os.remove(temp_filename)
		with open(correct_contents_filename) as f:
			correct_json = json.load(f, object_hook=deserialize_set)

		# Remove the timestamp entry.
		del saved_json['last_updated']
		del correct_json['last_updated']

		# Compare.
		self.assertDictEqual(saved_json, correct_json)

	def test_example_9_5(self):
		"""Test that save_instance() correctly saves Example 9.5.
		"""
		print_status('SaveInstance', 'test_example_9_5()')

		# Load.
		instance = instances.load_instance('example_9_5')

		# Save.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_example_9_5.json'
		instances.save_instance(
			instance_name='test_example_9_5',
			instance_data=instance,
			instance_description='this is test_example_9_5',
			filepath=temp_filename
		)

		# Load saved JSON and correct JSON.
		correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_example_9_5_correct.json'
		with open(temp_filename) as f:
			saved_json = json.load(f, object_hook=deserialize_set)
			os.remove(temp_filename)
		with open(correct_contents_filename) as f:
			correct_json = json.load(f, object_hook=deserialize_set)

		# Remove the timestamp entry.
		del saved_json['last_updated']
		del correct_json['last_updated']

		# Compare.
		self.assertDictEqual(saved_json, correct_json)

	def test_example_6_1(self):
		"""Test that save_instance() correctly saves Example 6.1.
		"""
		print_status('SaveInstance', 'test_example_6_1()')

		# Load.
		instance = instances.load_instance('example_6_1')

		# Save.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_example_6_1.json'
		try:
			instances.save_instance(
				instance_name='test_example_6_1',
				instance_data=instance,
				instance_description='this is test_example_6_1',
				filepath=temp_filename
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_example_6_1_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare.
			self.maxDiff = None
			self.assertDictEqual(saved_json, correct_json)
		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)


	def test_example_6_1_with_order_capacity(self):
		"""Test that save_instance() correctly saves Example 6.1 with a few order capacities.
		"""
		print_status('SaveInstance', 'test_example_6_1_with_order_capacity()')

		# Load.
		instance = instances.load_instance('example_6_1')
		instance.nodes_by_index[1].order_capacity = 40
		instance.nodes_by_index[3].order_capacity = 25

		# Save.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_example_6_1_with_order_capacity.json'
		try:
			instances.save_instance(
				instance_name='test_example_6_1_with_order_capacity',
				instance_data=instance,
				instance_description='this is test_example_6_1_with_order_capacity',
				filepath=temp_filename
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_example_6_1_with_order_capacity_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare.
			self.assertDictEqual(saved_json, correct_json)
		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)

	def test_figure_6_14(self):
		"""Test that save_instance() correctly saves Figure 6.14.
		"""
		print_status('SaveInstance', 'test_figure_6_14()')

		# Load.
		instance = instances.load_instance('figure_6_14')

		# Save.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_figure_6_14.json'
		try:
			instances.save_instance(
				instance_name='test_figure_6_14',
				instance_data=instance,
				instance_description='this is test_figure_6_14',
				filepath=temp_filename
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_figure_6_14_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare the networks separately from the rest of the dict.
			# (pred/succ lists may be in different orders which will make the dicts fail assertDictEqual.)
			saved_instance = SupplyChainNetwork.from_dict(saved_json['instances'][0]['data'])
			correct_instance = SupplyChainNetwork.from_dict(correct_json['instances'][0]['data'])
			self.assertTrue(saved_instance.deep_equal_to(correct_instance))

			# Remove the instances from the dicts.
			del saved_json['instances'][0]['data']
			del correct_json['instances'][0]['data']

			# Compare.
			self.assertDictEqual(saved_json, correct_json)

		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)

	def test_omit_state_vars_true(self):
		"""Test that save_instance() correctly saves problem_6_2b_adj with 
		omit_state_vars set to True.
		"""
		print_status('SaveInstance', 'test_omit_state_vars_true()')

		# Load.
		instance = instances.load_instance('problem_6_2b_adj')

		# Simulate for a bit.
		_ = simulation(instance, num_periods=25, rand_seed=42, progress_bar=False, consistency_checks='E')

		# Save with omit_state_vars=True.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_omit_state_vars_true.json'
		try:
			instances.save_instance(
				instance_name='test_omit_state_vars_true',
				instance_data=instance,
				instance_description='this is test_omit_state_vars_true',
				filepath=temp_filename,
				omit_state_vars=True
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_omit_state_vars_true_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare.
			self.assertDictEqual(saved_json, correct_json)

		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)

	def test_omit_state_vars_false(self):
		"""Test that save_instance() correctly saves problem_6_2b_adj with 
		omit_state_vars set to False.
		"""
		print_status('SaveInstance', 'test_omit_state_vars_false()')

		# Load.
		instance = instances.load_instance('problem_6_2b_adj')

		# Simulate for a bit.
		_ = simulation(instance, num_periods=25, rand_seed=42, progress_bar=False, consistency_checks='E')

		# Save with omit_state_vars=False.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_omit_state_vars_false.json'
		try:
			instances.save_instance(
				instance_name='test_omit_state_vars_false',
				instance_data=instance,
				instance_description='this is test_omit_state_vars_false',
				filepath=temp_filename,
				omit_state_vars=False
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_omit_state_vars_false_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare.
			self.maxDiff = None
			self.assertDictEqual(saved_json, correct_json)

		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)

	def test_omit_state_vars_false_rosling(self):
		"""Test that save_instance() correctly saves rosling_figure_1 with 
		omit_state_vars set to False.
		"""
		print_status('SaveInstance', 'test_omit_state_vars_false_rosling()')

		# Load.
		instance = instances.load_instance('rosling_figure_1')

		# Simulate for a bit.
		_ = simulation(instance, num_periods=25, rand_seed=42, progress_bar=False, consistency_checks='E')

		# Save with omit_state_vars=False.
		temp_filename = 'tests/additional_files/temp_TestSaveInstance_omit_state_vars_false_rosling.json'
		try:
			instances.save_instance(
				instance_name='test_omit_state_vars_false_rosling',
				instance_data=instance,
				instance_description='this is test_omit_state_vars_false_rosling',
				filepath=temp_filename,
				omit_state_vars=False
			)

			# Load saved JSON and correct JSON.
			correct_contents_filename = 'tests/additional_files/test_instances_TestSaveInstance_omit_state_vars_false_rosling_correct.json'
			with open(temp_filename) as f:
				saved_json = json.load(f, object_hook=deserialize_set)
			with open(correct_contents_filename) as f:
				correct_json = json.load(f, object_hook=deserialize_set)

			# Remove the timestamp entry.
			del saved_json['last_updated']
			del correct_json['last_updated']

			# Compare.
			self.maxDiff = None
			self.assertDictEqual(saved_json, correct_json)

		finally:
			if os.path.exists(temp_filename):
				os.remove(temp_filename)


