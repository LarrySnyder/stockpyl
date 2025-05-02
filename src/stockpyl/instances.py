# ===============================================================================
# stockpyl - instances Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_instances| module contains code for loading and saving problem instances.

.. note:: |fosct_notation| 

	The abbreviation *SCMO* below refers to the textbook
	*Supply Chain Modeling and Optimization* by Snyder, Smilowitz, and Shen, forthcoming.

|sp| has a number of built-in instances, most (but not all) of which are taken from |fosct|.
These can be loaded using the :func:`~load_instance` function by providing the instance name. 
A list of the built-in instances is provided below.


.. include:: ../../../src/stockpyl/aux_files/stockpyl_instances_metadata.rst


|

API Reference
-------------

"""

import os
import json
import warnings
import datetime
import jsonpickle
import csv
from copy import deepcopy
import inspect

from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_node import *
from stockpyl.helpers import is_set, is_dict, serialize_set, deserialize_set


def load_instance(instance_name, filepath=None, ignore_state_vars=True):
	"""Load an instance from a JSON file. 

	If the instance was originally specified as a |class_network| object, returns the
	object; otherwise, returns the instance in a dictionary.

	Parameters
	----------
	instance_name : str
		The name of the instance.
	filepath : str, optional
		Path to the JSON file. If ``None``, the function determines the path to 
		``datasets/stockpyl_instances.json``.
	ignore_state_vars : bool, optional
		If ``True``, function will ignore any saved state variables in the nodes.

	Returns
	-------
	dict or |class_network|
		The loaded instance. If the instance was originally specified as a |class_network|
		object, returns the object; otherwise, returns the instance in a dictionary in which
		the keys equal the parameter names (e.g., "holding_cost") and the values equal the parameter
		values (e.g., 0.5).

	Raises
	------
	ValueError
		If the JSON file does not exist or the instance cannot be found in the JSON file.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_json_path()

	# Does JSON file exist?
	if os.path.exists(filepath):
		# Use this path.
		new_path = filepath
	else:
		# Try changing working directory to project root (stockpyl/). This is mainly a workaround for
		# when this function is called from doctests.
		one_level_up = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		new_path = os.path.join(one_level_up, filepath)
		if not os.path.exists(new_path):
			raise FileNotFoundError(f"The JSON file {os.path.abspath(filepath)} was not found")

	# Load data from JSON.
	with open(new_path) as f:
		json_contents = json.load(f, object_hook=deserialize_set)

	# Look for instance. (https://stackoverflow.com/a/8653568/3453768)
	instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
		if item["name"] == instance_name), None)
	# Was instance found?
	if instance_index is None:
		raise KeyError("The speficied instance name was not found")

	# Get instance.
	instance = json_contents["instances"][instance_index]["data"]
	instance_type = json_contents["instances"][instance_index]["type"]

	# Was instance saved as a dict or a network?
	if instance_type == "network":
		# As a network.
		instance = SupplyChainNetwork.from_dict(instance)

		# Delete the state variables and replace with initialized version, 
		# if ignore_state_variables = True.
		if ignore_state_vars:
			for n in instance.nodes:
				n.state_vars = []

		# Ensure that all nodes have dummy product fields set correctly. This is to maintain backward
		# compatitbility with earlier versions, which did not save product info (including dummy products).
		for n in instance.nodes:
			# Does node already have dummy product?
			if n._dummy_product is None:
				# Add a dummy product, whether or not it needs one (mainly to assign the index).
				n._add_dummy_product()
			# Assign external supplier dummy product.
			n._external_supplier_dummy_product = SupplyChainProduct(n._dummy_product.index - 1, is_dummy=True)
			# Does node have "real" products? (This will probably never happen, since products were introduced
			# in the same version as dummy products--so if a node has products, it probably has dummy products
			# correctly handled already.)
			if len(n.products_by_index) > 1:
				# Remove dummy product.
				n._remove_dummy_product()
	else:
		# As a dict. Leave in place. But:
		# If the instance contains any dicts with integer keys, they will have
		# been saved as strings when the JSON was saved. Convert them back to integers here.
		# Currently, only demand_pmf has this issue.
		if 'demand_pmf' in instance.keys():
			instance['demand_pmf'] = {int(k): v for k, v in instance['demand_pmf'].items()}
 
	return instance

def save_instance(instance_name, instance_data, instance_description='', filepath=None, 
	replace=True, create_if_none=True, delete_if_exists=False, omit_state_vars=True):
	"""Save an instance to a JSON file. 
	
	Parameters
	----------
	instance_name : str
		The name of the instance. This will be used later for retreving the instance.
	instance_data : dict or SupplyChainNetwork
		The instance data as a dictionary (with keys equal to parameter names (e.g., "holding_cost")
		and values equal to parameter values (e.g., 0.5)) or as a |class_network| object 
		(in which case the instance is serialized using :mod:`jsonpickle`).
	instance_description : str, optional
		A longer descrtiption of the instance.
	filepath : str, optional
		Path to the JSON file. If ``None``, the function determines the path to 
		``datasets/stockpyl_instances.json``.
	replace : bool, optional
		If an instance with the same ``instance_name`` is already in the file, the function
		will replace it if ``True`` and will ignore it (and write nothing) if ``False``.
	create_if_none : bool, optional
		If the file does not already exist, the function will create a new file if ``True``; 
		otherwise, it will not do anything and issue a warning.
	delete_if_exists : bool, optional
		If the file already exists, the function will delete it first if ``True``; 
		otherwise, it will modify the existing file.
	omit_state_vars : bool, optional
		If ``True``, the function will not save state variables as part of the nodes,
		even if they are present in the instance.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_json_path()

	# Does JSON file exist?
	if os.path.exists(filepath):
		if delete_if_exists:
			os.remove(filepath)
			json_contents = {
				"_id": "",
				"instances": [],
				"last_updated": ""
			}
		else:
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
	if instance_index is not None:
		if not replace:
			return

	# Make local copy of network.
	local_copy = deepcopy(instance_data)

	# Was data provided as dict or SupplyChainNetwork?
	if isinstance(local_copy, dict):
		data = local_copy
		instance_type = "dict"
	else:
		# Assume SupplyChainNetwork.
		# Omit state variables, if requested.
		if omit_state_vars:
			for n in local_copy.nodes:
				n.state_vars = None
		# Convert to dict and JSONify.
		data = local_copy.to_dict()
		instance_type = "network"

	# Create dictionary with instance metadata and data.
	instance_dict = {
		"name": instance_name,
		"description": instance_description,
		"data": data,
		"type": instance_type
	}

	# Add (or replace) instance.
	if instance_index is not None:
		# We already know replace is True, otherwise we would have exited already.
		json_contents["instances"][instance_index] = instance_dict
	else:
		json_contents["instances"].append(instance_dict)
	json_contents["last_updated"] = f"{datetime.datetime.now()}"

	# If the instance contains any dicts with integer keys, they will be
	# saved as strings when the JSON is saved. load_instance() converts them back to integers.
	# Currently, only demand_pmf has this issue.

	# Make sure path exists; if not, create it.
	os.makedirs(os.path.dirname(filepath), exist_ok=True)
	
	# Write all instances to JSON.
	with open(filepath, 'w') as f:
		json.dump(json_contents, f, default=serialize_set)

	# Close file.
	f.close()


def _stockpyl_instances_json_path():
	"""Determine the path to the JSON file containing the instances. 

	See discussion at https://github.com/LarrySnyder/stockpyl/issues/85.

	Returns
	-------
	str
		The absolute path, including the filename itself.
	"""
	code_file = os.path.abspath(inspect.getsourcefile(_stockpyl_instances_json_path))
	rtn = os.path.join(os.path.dirname(code_file), "datasets", "stockpyl_instances.json")
	assert os.path.exists(rtn) and os.path.isfile(rtn)
	return rtn

