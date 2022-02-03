import copy
import os
import json
import warnings
import datetime
import jsonpickle

from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_node import *

DEFAULT_JSON_FILEPATH = 'datasets/stockpyl_instances.json'


def load_instance(instance_name, filepath=DEFAULT_JSON_FILEPATH):
	"""Load an instance from a JSON file. 

	If the instance was originally specified as a ``SupplyChainNetwork`` object, returns the
	object; otherwise, returns the instance in a dictionary.

	Parameters
	----------
	instance_name : str
		The name of the instance.
	filepath : str, optional
		Path to the JSON file. If ``None``, ``../datasets/stockpyl_instances.json`` is used.

	Returns
	-------
	dict or SupplyChainNetwork
		The loaded instance. If the instance was originally specified as a ``SupplyChainNetwork``
		object, returns the object; otherwise, returns the instance in a dictionary in which
		the keys equal the parameter names (e.g., "holding_cost") and the values equal the parameter
		values (e.g., 0.5).

	Raises
	------
	ValueError
		If the JSON file does not exist or the instance cannot be found in the JSON file.
	"""
	# TODO: unit tests
	
	# Does JSON file exist?
	if os.path.exists(filepath):
		# Load data from JSON.
		with open(filepath) as f:
			json_contents = json.load(f)
	else:
		raise FileNotFoundError("The specified JSON file was not found")
	
	# Look for instance. (https://stackoverflow.com/a/8653568/3453768)
	instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
		if item["name"] == instance_name), None)
	# Was instance found?
	if not instance_index:
		raise KeyError("The speficied instance name was not found")

	# Get instance (in case it was jsonpickled).
	instance = json_contents["instances"][instance_index]["data"]

	# Try to decode instance using jsonpickle. This will fail if the
	# instance is a regular dict, in which case we'll just return the dict.
	try:
		return jsonpickle.decode(instance)
	except:
		return instance


def save_instance(instance_name, instance_data, instance_description='', filepath=DEFAULT_JSON_FILEPATH, replace=True, create_if_none=True):
	"""Save an instance to a JSON file. 
	
	Appends the instance; does not check to see whether the instance is already in the file. 
	(To update an existing instance, use :func:`update_instance`.)

	Parameters
	----------
	instance_name : str
		The name of the instance. This will be used later for retreving the instance.
	instance_data : dict or SupplyChainNetwork
		The instance data as a dictionary (with keys equal to parameter names (e.g., "holding_cost")
		and values equal to parameter values (e.g., 0.5)) or as a ``SupplyChainNetwork`` object 
		(in which case the instance is serialized using :mod:`jsonpickle`).
	instance_description : str, optional
		A longer descrtiption of the instance.
	filepath : str, optional
		Path to the JSON file. If ``None``, ``../datasets/stockpyl_instances.json`` is used.
	replace : bool, optional
		If an instance with the same ``instance_name`` is already in the file, the function
		will replace it if ``True`` and will ignore it (and write nothing) if ``False``.
	create_if_none : bool, optional
		If the file does not already exist, the function will create a new file if ``True``; 
		otherwise, it will not do anything and issue a warning.
	"""

	# TODO: unit tests
	
	# Does JSON file exist?
	if os.path.exists(filepath):
		# Load data from JSON.
		with open(filepath) as f:
			json_contents = json.load(f)
	else:
		# Should we create it?
		if create_if_none:
			json_contents = {
				"_id": "",
				"instances": [],
				"last_updated": ""
			}
		else:
			warnings.warn('filepath does not exist and create_if_none is False; no action was taken')
			return

	# Look for instance. (https://stackoverflow.com/a/8653568/3453768)
	instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
		if item["name"] == instance_name), None)
	# Was instance found?
	if instance_index:
		if not replace:
			return

	# Was data provided as dict or SupplyChainNetwork?
	if isinstance(instance_data, dict):
		data = instance_data
	else:
		# Assume SupplyChainNetwork.
		data = jsonpickle.encode(instance_data)

	# Create dictionary with instance metadata and data.
	instance_dict = {
		"name": instance_name,
		"description": instance_description,
		"data": data
	}

	# Add (or replace) instance.
	if instance_index:
		# We already know replace is True, otherwise we would have exited already.
		json_contents["instances"][instance_index] = instance_dict
	else:
		json_contents["instances"].append(instance_dict)
	json_contents["last_updated"] = f"{datetime.datetime.now()}"

	# Write all instances to JSON.
	with open(filepath, 'w') as f:
		json.dump(json_contents, f)

	# Close file.
	f.close()


def update_instance(instance_name, instance_data, instance_description=None, filepath=DEFAULT_JSON_FILEPATH):
	"""Modify an instance in a JSON file.

	Parameters
	----------
	instance_name : str
		The name of the instance, for retreival. (The instance name cannot be changed by this function.)
	instance_data : dict
		The new instance data as a dictionary, with keys equal to variable names (e.g., ``holding_cost``)
		and values equal to variable values (e.g., 0.5).
	instance_description : str, optional
		The new description. Set to ``None`` to leave the old description in place.
	filepath : str, optional
		Path to the JSON file. If ``None``, ``../datasets/stockpyl_instances.json`` is used.

	Raises
	------
	ValueError 
		If ``instance_name`` does not exist in the JSON file.
	"""

	# TODO: unit tests

	# Load data from JSON.
	with open(filepath) as f:
		json_contents = json.load(f)

	# Find instance. (https://stackoverflow.com/a/8653568/3453768)
	instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
		if item["name"] == instance_name), None)
	
	# Was instance found?
	if not instance_index:
		raise KeyError('Instance was not found in JSON file.')

	# Get old instance.
	old_instance = json_contents["instances"][instance_index]
	
	# Build new instance.
	if instance_description is None:
		new_description = old_instance["description"]
	else:
		new_description = instance_description
	new_instance = {
		"name": instance_name,
		"description": new_description,
		"data": instance_data
	}

	# Replace instance in list.
	json_contents["instances"][instance_index] = new_instance
	json_contents["last_updated"] = f"{datetime.datetime.now()}"

	# Write all instances to JSON.
	with open(filepath, 'w') as f:
		json.dump(json_contents, f)

	# Close file.
	f.close()


def get_named_instance(instance_name):
	"""Return the named instance specified by ``instance_name``. Return
	variables depend on the instance.

	Parameters
	----------
	instance_name : str
		The instance name. See method code for allowable strings.

	"""

	# CHAPTER 3
	if instance_name == "example_3_1":
		# Example 3.1.
		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		demand_rate = 1300
		return fixed_cost, holding_cost, demand_rate
	elif instance_name == "problem_3_1":
		# Problem 3.1.
		fixed_cost = 2250
		holding_cost = 275
		demand_rate = 500 * 365
		return fixed_cost, holding_cost, demand_rate
	elif instance_name == "example_3_8":
		# Example 3.8.
		fixed_cost = 8
		holding_cost = 0.75 * 0.3
		stockout_cost = 5
		demand_rate = 1300
		return fixed_cost, holding_cost, stockout_cost, demand_rate
	elif instance_name == "problem_3_2b":
		# Problem 3.2(b).
		fixed_cost = 40
		holding_cost = (165 * 0.17 + 12)
		stockout_cost = 60
		demand_rate = 40 * 52
		return fixed_cost, holding_cost, stockout_cost, demand_rate
	elif instance_name == "problem_3_22":
		# Problem 3.22.
		fixed_cost = 4
		holding_cost = 0.08
		demand_rate = 80
		production_rate = 110
		return fixed_cost, holding_cost, demand_rate, production_rate
	elif instance_name == "example_3_9":
		# Example 3.9 (Wagner-Whitin).
		num_periods = 4
		holding_cost = 2
		fixed_cost = 500
		demand = [90, 120, 80, 70]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "problem_3_27":
		# Problem 3.27.
		num_periods = 4
		holding_cost = 0.8
		fixed_cost = 120
		demand = [150, 100, 80, 200]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "problem_3_29":
		# Problem 3.29.
		num_periods = 5
		holding_cost = 0.1
		fixed_cost = 100
		demand = [730, 580, 445, 650, 880]
		return num_periods, holding_cost, fixed_cost, demand
	elif instance_name == "ww_hw_c":
		# SCMO HW problem for WW with nonstationary purchase cost.
		num_periods = 5
		holding_cost = 0.1
		fixed_cost = 100
		demand = [400, 500, 500, 1100, 900]
		purchase_cost = [3, 1, 4, 6, 6]
		return num_periods, holding_cost, fixed_cost, demand, purchase_cost
	elif instance_name == "jrp_ex":
		# JRP example in SCMO.
		shared_fixed_cost = 600
		individual_fixed_costs = [120, 840, 300]
		holding_costs = [160, 20, 50]
		demand_rates = [1, 1, 1]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_1":
		# JRP HW 1 (paper)
		shared_fixed_cost = 20000
		individual_fixed_costs = [36000, 46000, 34000, 38000]
		holding_costs = [1000, 900, 1200, 1000]
		demand_rates = [1780, 445, 920, 175]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_2":
		# JRP HW 2 (construction)
		shared_fixed_cost = 1500
		individual_fixed_costs = [4000, 1000, 2000]
		holding_costs = [300, 200, 200]
		demand_rates_week = [175, 1600, 400]
		demand_rates = (52 * np.array(demand_rates_week)).tolist()
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_hw_3":
		# JRP HW 3 (books)
		shared_fixed_cost = 180
		individual_fixed_costs = [60, 100, 180, 115, 135]
		purchase_costs = [19, 14, 17, 14, 12]
		holding_costs = (0.28 * np.array(purchase_costs)).tolist()
		demand_rates = [6200, 1300, 400, 4400, 1800]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_silver":
		# Numerical example in Silver (1976).
		shared_fixed_cost = 10
		individual_fixed_costs = [1.87, 5.27, 7.94, 8.19, 8.87]
		holding_costs = [0.2] * 5
		demand_rates = [1736, 656, 558, 170, 142]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates
	elif instance_name == "jrp_spp":
		# Example on p. 428 of Silver, Pyke, and Peterson (1998).
		shared_fixed_cost = 40
		individual_fixed_costs = [15, 15, 15, 15]
		holding_costs = [0.24] * 4
		demand_rates = [86000, 12500, 1400, 3000]
		return shared_fixed_cost, individual_fixed_costs, holding_costs, demand_rates



	# CHAPTER 4
	if instance_name == "example_4_1_network":
		# Example 4.1 (newsvendor), as SupplyChainNetwork object.
		example_4_1_network = serial_system(
			num_nodes=1,
			local_holding_cost=[0.18],
			stockout_cost=[0.70],
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=8,
			shipment_lead_time=[1],
			inventory_policy_type='BS',
			base_stock_levels=[56.6]
		)
		return example_4_1_network
	elif instance_name == "example_4_1":
		# Example 4.1 (newsvendor).
		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		return holding_cost, stockout_cost, demand_mean, demand_sd
	elif instance_name == "example_4_2":
		# Example 4.2 (newsvendor explicit).
		selling_revenue = 1
		purchase_cost = 0.3
		salvage_value = 0.12
		demand_mean = 50
		demand_sd = 8
		return selling_revenue, purchase_cost, salvage_value, demand_mean, demand_sd
	elif instance_name == "example_4_2_network":
		# Example 4.2 (newsvendo rexplicit), as SupplyChainNetwork object.
		example_4_2_network = serial_system(
			num_nodes=1,
			local_holding_cost=[0.18],
			stockout_cost=[0.70],
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=8,
			shipment_lead_time=[1],
			inventory_policy_type='BS',
			base_stock_levels=[56.6])
		return example_4_2_network
	elif instance_name == "example_4_3":
		# Example 4.3 (= Example 4.1).
		return get_named_instance("example_4_1")
	elif instance_name == "problem_4_1":
		# Problem 4.1.
		holding_cost = 65-22
		stockout_cost = 129-65+15
		demand_mean = 900
		demand_sd = 60
		return holding_cost, stockout_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_3b":
		# Problem 4.3(b) (newsvendor explicit -- In-Flight Meals).
		selling_revenue = 7
		purchase_cost = 2.5
		salvage_value = 1.5
		demand_mean = 50
		demand_sd = 10
		return selling_revenue, purchase_cost, salvage_value, demand_mean, demand_sd
	elif instance_name == "example_4_4":
		# Example 4.4.
		holding_cost = 0.18
		stockout_cost = 0.7
		demand_mean = 50
		demand_sd = 8
		lead_time = 4
		return holding_cost, stockout_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "example_4_7":
		# Example 4.7 (Poisson).
		holding_cost = 1
		stockout_cost = 4
		demand_mean = 6
		fixed_cost = 5
		return holding_cost, stockout_cost, fixed_cost, demand_mean
	elif instance_name == "problem_4_8a":
		# Problem 4.8(a).
		holding_cost = 200
		stockout_cost = 270
		demand_mean = 18
		return holding_cost, stockout_cost, demand_mean
	elif instance_name == "problem_4_7b":
		# Problem 4.7(b).
		holding_cost = 500000
		stockout_cost = 1000000
		demand_pmf = {1: 0.25, 2: 0.05, 3: 0.1, 4: 0.2, 5: 0.15, 6: 0.10, 7: 0.10, 8: 0.05}
		return holding_cost, stockout_cost, demand_pmf
	elif instance_name == "problem_4_8b":
		# Problem 4.8(b) -- lognormal newsvendor.
		holding_cost = 1
		stockout_cost = 0.1765
		mu = 6
		sigma = 0.3
		return holding_cost, stockout_cost, mu, sigma
	elif instance_name == "problem_4_31":
		# Problem 4.31.
		holding_cost = 40
		stockout_cost = 125
		fixed_cost = 150
		demand_mean = 4
		return holding_cost, stockout_cost, fixed_cost, demand_mean
	elif instance_name == "example_4_8":
		# Example 4.8 (= Example 4.4 + K = 2.5).
		holding_cost, stockout_cost, demand_mean, demand_sd, _ = \
			get_named_instance("example_4_4")
		fixed_cost = 2.5
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_32":
		# Problem 4.32.
		holding_cost = 2
		stockout_cost = 36
		fixed_cost = 60
		demand_mean = 190
		demand_sd = 48
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd
	elif instance_name == "problem_4_29":
		# Problem 4.29.
		num_periods = 10
		holding_cost = 1
		stockout_cost = 25
		terminal_holding_cost = holding_cost
		terminal_stockout_cost = stockout_cost
		purchase_cost = 1
		fixed_cost = 0
		demand_mean = 18
		demand_sd = 3
		discount_factor = 0.98
		initial_inventory_level = 0
		return num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level
	elif instance_name == "problem_4_30":
		# Problem 4.30 (= Problem 4.29 + fixed_cost = 40).
		num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, _, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level = \
			get_named_instance("problem_4_29")
		fixed_cost = 40
		return num_periods, holding_cost, stockout_cost, terminal_holding_cost, \
			terminal_stockout_cost, purchase_cost, fixed_cost, demand_mean, \
			demand_sd, discount_factor, initial_inventory_level

	# CHAPTER 5
	if instance_name == "example_5_1":
		# Example 5.1 (plus 5.2-5.6).
		holding_cost = 0.225
		stockout_cost = 7.5
		fixed_cost = 8
		demand_mean = 1300
		demand_sd = 150
		lead_time = 1/12
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "problem_5_1":
		# Problem 5.1.
		holding_cost = 3.1
		stockout_cost = 45
		fixed_cost = 50
		demand_mean = 800
		demand_sd = 40
		lead_time = 4/365
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "problem_5_3":
		# Problem 5.3.
		holding_cost = 1.5 / 7
		stockout_cost = 40
		fixed_cost = 85
		demand_mean = 192
		demand_sd = 17.4
		lead_time = 3
		return holding_cost, stockout_cost, fixed_cost, demand_mean, demand_sd, lead_time
	elif instance_name == "example_5_8":
		# Example 5.8 (Poisson).
		holding_cost = 20
		stockout_cost = 150
		fixed_cost = 100
		demand_mean = 1.5
		lead_time = 2
		return holding_cost, stockout_cost, fixed_cost, demand_mean, lead_time
	elif instance_name == "problem_5_2":
		# Problem 5.2.
		holding_cost = 4
		stockout_cost = 28
		fixed_cost = 4
		demand_mean = 12
		lead_time = 0.5
		return holding_cost, stockout_cost, fixed_cost, demand_mean, lead_time

	# CHAPTER 6
	if instance_name == "example_6_1":
		# Example 6.1.
		example_6_1_network = serial_system(
			num_nodes=3,
			local_holding_cost=[7, 4, 2],
			echelon_holding_cost=[3, 2, 2],
			stockout_cost=[37.12, 0, 0],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time=[1, 1, 2],
			inventory_policy_type='BS',
			base_stock_levels=[6.49, 5.53, 10.69],
			downstream_0=True
		)
		return example_6_1_network
	elif instance_name == "problem_6_1":
		# Problem 6.1.
		problem_6_1_network = serial_system(
			num_nodes=2,
			local_holding_cost=[2, 1],
			echelon_holding_cost=[1, 1],
			stockout_cost=[15, 0],
			demand_type='N',
			demand_mean=100,
			demand_standard_deviation=15,
			shipment_lead_time=[1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[100, 94],
			downstream_0=True
		)
		return problem_6_1_network
	elif instance_name == "problem_6_2a":
		# Problem 6.2a.
		problem_6_2a_network = serial_system(
			num_nodes=5,
			local_holding_cost=[1, 2, 3, 5, 7],
			echelon_holding_cost=[2, 2, 1, 1, 1],
			stockout_cost=[24, 0, 0, 0, 0],
			demand_type='N',
			demand_mean=64,
			demand_standard_deviation=8,
			shipment_lead_time=[0.5, 0.5, 0.5, 0.5, 0.5],
			inventory_policy_type='BS',
			base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
			downstream_0=True
		)
		return problem_6_2a_network
	elif instance_name == "problem_6_2a_adj":
		# Problem 6.2a, adjusted for periodic review.
		# (Since L=0.5 in that problem, here we treat each period as
		# having length 0.5 in the original problem.)
		problem_6_2a_network_adj = serial_system(
			num_nodes=5,
			local_holding_cost=list(np.array([1, 2, 3, 5, 7]) / 2),
			stockout_cost=list(np.array([24, 0, 0, 0, 0]) / 2),
			demand_type='N',
			demand_mean=64 / 2,
			demand_standard_deviation=8 / np.sqrt(2),
			shipment_lead_time=[1, 1, 1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
			downstream_0=True
		)
		return problem_6_2a_network_adj
	elif instance_name == "problem_6_2b_adj":
		# Problem 6.2b, adjusted for periodic review.
		# (Since L=0.5 in that problem, here we treat each period as
		# having length 0.5 in the original problem.)
		problem_6_2a_network_adj = get_named_instance('problem_6_2a_adj')
		problem_6_2b_network_adjusted = copy.deepcopy(problem_6_2a_network_adj)
		# TODO: build this instance - -need to add Poisson demand capability
		return problem_6_2b_network_adjusted
	elif instance_name == "problem_6_16":
		# Problem 6.16.
		problem_6_16_network = serial_system(
			num_nodes=2,
			local_holding_cost=[7, 2],
			stockout_cost=[24, 0],
			demand_type='N',
			demand_mean=20,
			demand_standard_deviation=4,
			shipment_lead_time=[8, 3],
			inventory_policy_type='BS',
			base_stock_levels=[171.1912, 57.7257],
			initial_IL=20,
			initial_orders=20,
			initial_shipments=20,
			downstream_0=True
		)
		return problem_6_16_network

	# CHAPTER 9
	if instance_name == "example_9_1":
		# Example 9.1.
		holding_cost = 0.225
		stockout_cost = 5
		fixed_cost = 8
		demand_rate = 1300
		disruption_rate = 1.5
		recovery_rate = 14
		return holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate
	elif instance_name == "problem_9_8":
		# Problem 9.8.
		holding_cost = 4
		stockout_cost = 22
		fixed_cost = 35
		demand_rate = 30
		disruption_rate = 1
		recovery_rate = 12
		return holding_cost, stockout_cost, fixed_cost, demand_rate, disruption_rate, recovery_rate
	elif instance_name == "example_9_3":
		# Example 9.3.
		holding_cost = 0.25
		stockout_cost = 3
		disruption_prob = 0.04
		recovery_prob = 0.25
		demand = 2000
		return holding_cost, stockout_cost, demand, disruption_prob, recovery_prob
	elif instance_name == "example_9_4":
		# Example 9.4.
		fixed_cost = 18500
		holding_cost = 0.06
		demand_rate = 75000
		yield_mean = -15000
		yield_sd = 9000
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "problem_9_4a":
		# Problem 9.4a.
		fixed_cost, holding_cost, demand_rate = get_named_instance("problem_3_1")
		yield_mean = -1/0.02
		yield_sd = 0.02
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "problem_9_4b":
		# Problem 9.4b.
		fixed_cost, holding_cost, demand_rate = get_named_instance("problem_3_1")
		yield_mean = 0.9
		yield_sd = 0.2 / np.sqrt(12)
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "example_9_5":
		# Example 9.5.
		fixed_cost = 18500
		holding_cost = 0.06
		demand_rate = 75000
		yield_mean = 5.0/6
		yield_sd = np.sqrt(5.0/(36*7))
		return fixed_cost, holding_cost, demand_rate, yield_mean, yield_sd
	elif instance_name == "example_9_6":
		# Example 9.6.
		holding_cost = 15000000
		stockout_cost = 75000000
		demand = 1.5
		yield_lo = -0.5
		yield_hi = 0.5
		return holding_cost, stockout_cost, demand, yield_lo, yield_hi
	elif instance_name == "problem_9_5":
		# Problem 9.5.
		holding_cost = 150
		stockout_cost = 1200
		demand = 25
		yield_lo = -5
		yield_hi = 0
		return holding_cost, stockout_cost, demand, yield_lo, yield_hi

	# INSTANCES NOT FROM TEXTBOOK
	if instance_name == "assembly_3_stage":
		assembly_3_stage_network = mwor_system(
			num_warehouses=2,
			local_holding_cost=[2, 1, 1],
			stockout_cost=[20, 0, 0],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=1,
			shipment_lead_time=[1, 2, 2],
			inventory_policy_type='BS',
			base_stock_levels=[7, 13, 11],
			initial_IL=[7, 13, 11],
			downstream_0=True
		)
		assembly_3_stage_network.nodes[0].demand_source.round_to_int = True
		return assembly_3_stage_network
	elif instance_name == "assembly_3_stage_2":
			assembly_3_stage_2_network = network_from_edges(
				edges=[(1, 3), (2, 3)],
				local_holding_cost={1: 1, 2: 1, 3: 2},
				stockout_cost={1: 0, 2: 0, 3: 20},
				demand_type={1: None, 2: None, 3: 'N'},
				demand_mean=20,
				demand_standard_deviation=5,
				shipment_lead_time={1: 2, 2: 2, 3: 1},
				inventory_policy_type='BS',
				base_stock_levels={1: 44, 2: 52, 3: 28},
				initial_IL={1: 44, 2: 52, 3: 28}
			)
			# assembly_3_stage_2_network = mwor_system(
			# 	num_warehouses=2,
			# 	local_holding_cost=[2, 1, 1],
			# 	stockout_cost=[20, 0, 0],
			# 	type='D',
			# 	mean=20,
			# 	standard_deviation=5,
			# 	shipment_lead_time=[1, 2, 2],
			# 	inventory_policy_type='BS',
			# 	base_stock_levels=[28, 52, 44],
			# 	initial_IL=[28, 52, 44],
			# 	downstream_0=True)
			assembly_3_stage_2_network.get_node_from_index(3).demand_source.round_to_int = True
			return assembly_3_stage_2_network
	elif instance_name == "rosling_figure_1":
		# Figure 1 from Rosling (1989).
		# Note: Other than the structure and lead times, none of the remaining parameters are from Rosling's paper.
		rosling_figure_1_network = SupplyChainNetwork()
		nodes = {i: SupplyChainNode(index=i) for i in range(1, 8)}
		# Inventory policies.
		for n in nodes.values():
			n.inventory_policy.type = 'BEBS'
			n.inventory_policy.base_stock_level = None
		# Node 1.
		nodes[1].shipment_lead_time = 1
		demand_source = DemandSource() # TODO: create this in the constructor (like policy)
		demand_source.type = 'UD'
		demand_source.lo = 0
		demand_source.hi = 10
		nodes[1].demand_source = demand_source
		nodes[1].supply_type = None
		nodes[1].inventory_policy.base_stock_level = 8
		nodes[1].initial_inventory_level = 8
		rosling_figure_1_network.add_node(nodes[1])
		# Node 2.
		nodes[2].shipment_lead_time = 1
		nodes[2].supply_type = None
		nodes[2].inventory_policy.base_stock_level = 24
		nodes[2].initial_inventory_level = 8
		rosling_figure_1_network.add_predecessor(nodes[1], nodes[2])
		# Node 3.
		nodes[3].shipment_lead_time = 3
		nodes[3].supply_type = None
		nodes[3].inventory_policy.base_stock_level = 40
		nodes[3].initial_inventory_level = 24
		rosling_figure_1_network.add_predecessor(nodes[1], nodes[3])
		# Node 4.
		nodes[4].shipment_lead_time = 2
		nodes[4].supply_type = None
		nodes[4].inventory_policy.base_stock_level = 76
		nodes[4].initial_inventory_level = 16
		rosling_figure_1_network.add_predecessor(nodes[3], nodes[4])
		# Node 5.
		nodes[5].shipment_lead_time = 4
		nodes[5].inventory_policy.base_stock_level = 62
		nodes[5].initial_inventory_level = 32
		nodes[5].supply_type = 'U'
		rosling_figure_1_network.add_predecessor(nodes[2], nodes[5])
		# Node 6.
		nodes[6].shipment_lead_time = 1
		nodes[6].supply_type = 'U'
		nodes[6].inventory_policy.base_stock_level = 84
		nodes[6].initial_inventory_level = 8
		rosling_figure_1_network.add_predecessor(nodes[4], nodes[6])
		# Node 7.
		nodes[7].shipment_lead_time = 2
		nodes[7].supply_type = 'U'
		nodes[7].inventory_policy.base_stock_level = 92
		nodes[7].initial_inventory_level = 16
		rosling_figure_1_network.add_predecessor(nodes[4], nodes[7])
		return rosling_figure_1_network
	elif instance_name == "kangye_4_stage":
		kangye_4_stage = mwor_system(
			num_warehouses=3,
			demand_type='N',
			demand_mean=20,
			demand_standard_deviation=4,
			shipment_lead_time=[1, 1, 2, 3],
			inventory_policy_type='BEBS',
			base_stock_levels=[30, 50, 70, 90],
			downstream_0=True
		)
		return kangye_4_stage
	elif instance_name == "kangye_3_stage_serial":
		kangye_3_stage_serial = serial_system(
			num_nodes=3,
			local_holding_cost=[1, 5, 10],
			stockout_cost=[0, 0, 100],
			demand_type='N',
			demand_mean=5,
			demand_standard_deviation=np.sqrt(5),
			shipment_lead_time=[1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[7, 7, 7],
			initial_IL=[7, 7, 7],
			downstream_0=False
		)
		for i in range(2):
			kangye_3_stage_serial.get_node_from_index(i).in_transit_holding_cost = 0
		kangye_3_stage_serial.get_node_from_index(2).demand_source.round_to_int = True
		return kangye_3_stage_serial
	elif instance_name == "michelle_sean_3_stage":
		michelle_sean_3_stage = mwor_system(
			num_warehouses=2,
			demand_type='N',
			demand_mean=50,
			demand_standard_deviation=10,
			local_holding_cost=[10, 10, 10],
			stockout_cost=[10, 10, 10],
			shipment_lead_time=[1, 1, 1],
			inventory_policy_type='BS',
			base_stock_levels=[60, 50, 60],
			downstream_0=True,
			initial_IL=[60, 50, 60]
		)
		return michelle_sean_3_stage
	elif instance_name == "rong_atan_snyder_figure_1a":
		# Uses normal demand instead of Poisson.
		# TODO: add costs and lead times
		rong_atan_snyder_figure_1a = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
			demand_type={0: None, 1: None, 2: None, 3: 'N', 4: 'N', 5: 'N', 6: 'N'},
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			local_holding_cost={0: 1/3, 1: 2/3, 2: 2/3, 3: 1, 4: 1, 5: 1, 6: 1},
			stockout_cost=20,
			shipment_lead_time=1,
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 7)}
		)
		return rong_atan_snyder_figure_1a
	elif instance_name == "rong_atan_snyder_figure_1b":
		# Uses normal demand instead of Poisson.
		# TODO: add costs and lead times
		demand_type = {i: 'N' if i >= 3 else None for i in range(11)}
		rong_atan_snyder_figure_1b = network_from_edges(
			edges=[(0, 1), (0, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (2, 8), (2, 9), (2, 10)],
			demand_type=demand_type,
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 11)}
		)
		return rong_atan_snyder_figure_1b
	elif instance_name == "rong_atan_snyder_figure_1c":
		# Uses normal demand instead of Poisson.
		# TODO: add costs and lead times
		rong_atan_snyder_figure_1c = network_from_edges(
			edges=[(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)],
			demand_type={0: None, 1: 'N', 2: None, 3: 'N', 4: 'N', 5: 'N'},
			demand_mean=8,
			demand_standard_deviation=np.sqrt(8),
			inventory_policy_type='BS',
			base_stock_levels={i: 0 for i in range(0, 6)}
		)
		return rong_atan_snyder_figure_1c
