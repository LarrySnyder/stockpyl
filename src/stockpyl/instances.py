# ===============================================================================
# stockpyl - instances Module
# -------------------------------------------------------------------------------
# Updated: 02-03-2022
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""
.. include:: ../globals.inc

The :mod:`instances` module contains code for loading and saving problem instances.
Unless otherwise noted, instances are taken from Snyder and Shen, *Fundamentals of Supply Chain Theory*, 2nd edition
(2019).




.. csv-table:: Named Instances
   :file: ../docs/aux_files/named_instances.csv
   :widths: 30, 70
   :header-rows: 1
"""

#import copy
import os
import json
import warnings
import datetime
import jsonpickle
import csv

from stockpyl.supply_chain_network import *
from stockpyl.supply_chain_node import *

DEFAULT_JSON_FILEPATH = 'datasets/stockpyl_instances.json'

# TODO: function to sort instances in JSON by name, or even better, by chapter then name

def load_instance(instance_name, filepath=DEFAULT_JSON_FILEPATH, initialize_missing_attributes=True):
	"""Load an instance from a JSON file. 

	If the instance was originally specified as a ``SupplyChainNetwork`` object, returns the
	object; otherwise, returns the instance in a dictionary.

	Parameters
	----------
	instance_name : str
		The name of the instance.
	filepath : str, optional
		Path to the JSON file. If ``None``, ``../datasets/stockpyl_instances.json`` is used.
	initialize_missing_attributes : bool, optional
		If ``True``, method will ensure that all attributes are present in the instance loaded,
		initializing any missing attributes to their default values. (Typically this is only set
		to ``False`` for debugging purposes.)

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
		json_contents = json.load(f)

	# Look for instance. (https://stackoverflow.com/a/8653568/3453768)
	instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
		if item["name"] == instance_name), None)
	# Was instance found?
	if instance_index is None:
		raise KeyError("The speficied instance name was not found")

	# Get instance (in case it was jsonpickled).
	instance = json_contents["instances"][instance_index]["data"]

	# Try to decode instance using jsonpickle. This will fail if the
	# instance is a regular dict, in which case we'll just return the dict.
	try:
		instance = jsonpickle.decode(instance)

		# Replace the instance with a deep copy of it. This is important because if there are 
		# missing attributes in the saved instance (which can happen if the instance was 
		# saved under an earlier version of the code and a new field was introduced subsequently),
		# the deep copy will contain default values for those attributes.
		if initialize_missing_attributes:
			instance.initialize(overwrite=False)
		# TODO: this method of making sure that all attributes are present feels clunky and prone to error.
		# A better way might be to not use jsonpickle and instead create the relevant objects when loading, 
		# then fill them from the data in the file.

		return instance
	except TypeError as e:
		# If the instance contains any dicts with integer keys, they will have
		# been saved as strings when the JSON was saved. Convert them back to integers here.
		# Currently, only demand_pmf has this issue.
		# TODO: try to do this without a try...except. try...except makes it too hard to debug
		# if there is another (unplanned) exception
		if 'demand_pmf' in instance.keys():
			instance['demand_pmf'] = {int(k): v for k, v in instance['demand_pmf'].items()}

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
	if instance_index is not None:
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

	# If the instance contains any dicts with integer keys, they will be
	# saved as strings when the JSON is saved. load_instance() converts them back to integers.
	# Currently, only demand_pmf has this issue.

	# Write all instances to JSON.
	with open(filepath, 'w') as f:
		json.dump(json_contents, f)

	# Close file.
	f.close()


def save_summary_to_csv(save_filepath, json_filepath=DEFAULT_JSON_FILEPATH):
	"""Save a CSV file with a summary of the instances in a JSON file.

	Main purpose of this method is to build the CSV file that populates the table
	at the top of this page.

	Parameters
	----------
	save_filepath : str
		Path to the CSV file to create.
	json_filepath : str, optional
		Path to the JSON file. If ``None``, ``../datasets/stockpyl_instances.json`` is used.
	"""

	# Load JSON file.
	with open(json_filepath) as f:
		json_contents = json.load(f)

	# Write to CSV.
	with open(save_filepath, 'w', newline='') as csvfile:
		instance_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		instance_writer.writerow(['Name', 'Description'])
		for instance in json_contents['instances']:
			instance_writer.writerow([instance['name'], instance['description']])

	f.close()
	csvfile.close()

