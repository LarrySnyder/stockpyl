# ===============================================================================
# stockpyl - instances Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: GPLv3
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




.. csv-table:: Built-In Instances
   :file: aux_files/named_instances.csv
   :widths: 30, 70
   :header-rows: 1

API Reference
-------------

"""


#import copy
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

#: Default path to JSON file containing built-in instances. Relative to 'src' directory.
#DEFAULT_JSON_FILEPATH = '../datasets/stockpyl_instances.json'

def load_instance(instance_name, filepath=None, initialize_missing_attributes=True,
	ignore_state_vars=True):
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
	initialize_missing_attributes : bool, optional
		If ``True``, function will ensure that all attributes are present in the instance loaded,
		initializing any missing attributes to their default values. (Typically this is only set
		to ``False`` for debugging purposes.)
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

		# Delete the state variables and replace with initialized version, 
		# if ignore_state_variables = True.
		if ignore_state_vars:
			for n in instance.nodes:
				n.state_vars = []

		return instance
	except TypeError as e:
		# If the instance contains any dicts with integer keys, they will have
		# been saved as strings when the JSON was saved. Convert them back to integers here.
		# Currently, only demand_pmf has this issue.
		if 'demand_pmf' in instance.keys():
			instance['demand_pmf'] = {int(k): v for k, v in instance['demand_pmf'].items()}

		return instance


def save_instance_new(instance_name, instance_data, instance_description='', filepath=None, 
	replace=True, create_if_none=True, omit_state_vars=True):
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
	omit_state_vars : bool, optional
		If ``True``, the function will not save state variables as part of the nodes,
		even if they are present in the instance.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_json_path()

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

	# Make local copy of network.
	local_copy = deepcopy(instance_data)

	# Was data provided as dict or SupplyChainNetwork?
	if isinstance(local_copy, dict):
		data = local_copy
	else:
		# Assume SupplyChainNetwork.
		# Omit state variables, if requested.
		if omit_state_vars:
			for n in local_copy.nodes:
				n.state_vars = None
		data = json.encode(local_copy)

	# Create dictionary with instance metadata and data.
	instance_dict = {
		"name": instance_name,
		"description": instance_description,
		"data": data
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
		json.dump(json_contents, f)

	# Close file.
	f.close()


def save_instance(instance_name, instance_data, instance_description='', filepath=None, 
	replace=True, create_if_none=True, omit_state_vars=True):
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
	omit_state_vars : bool, optional
		If ``True``, the function will not save state variables as part of the nodes,
		even if they are present in the instance.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_json_path()

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

	# Make local copy of network.
	local_copy = deepcopy(instance_data)

	# Was data provided as dict or SupplyChainNetwork?
	if isinstance(local_copy, dict):
		data = local_copy
	else:
		# Assume SupplyChainNetwork.
		# Omit state variables, if requested.
		if omit_state_vars:
			for n in local_copy.nodes:
				n.state_vars = None
		data = jsonpickle.encode(local_copy)

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

	# Make sure path exists; if not, create it.
	os.makedirs(os.path.dirname(filepath), exist_ok=True)
	
	# Write all instances to JSON.
	with open(filepath, 'w') as f:
		json.dump(json_contents, f)

	# Close file.
	f.close()


def _save_instance_metadata_to_rst(instance_name, instance_description='', instance_title=None, code_to_build=None, 
	filepath=None, create_if_none=True):
	"""Save an instance metadata to an RST file. 

	Does not check whether the instance already exists in the file; simply appends it to the end.
	
	Parameters
	----------
	instance_name : str
		The name of the instance. 
	instance_description : str, optional
		A longer descrtiption of the instance.
	instance_title : str, optional
		The title to use for the section of the documentation that describes this instance.
		Typically a little longer and more descriptive than the name, e.g., "Example 6.1 (EOQ)".
		If ``None``, ``instance_description`` is used as the title.
	code_to_build : str, optional
		A string containing the code the user could use to build the instance manually.
	filepath : str, optional
		Path to the RST file. If ``None``, the function determines the path to 
		``aux_files/stockpyl_instances_metadata.rst``.
	create_if_none : bool, optional
		If the file does not already exist, the function will create a new file if ``True``; 
		otherwise, it will not do anything and issue a warning.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_metadata_path()

	# Make sure path exists; if not, create it.
	os.makedirs(os.path.dirname(filepath), exist_ok=True)

	# Does RST file exist?
	if not os.path.exists(filepath):
		# Should we create it?
		if not create_if_none:
			warnings.warn('filepath does not exist and create_if_none is False; no action was taken')
			return

	# Open RST file.
	with open(filepath, 'a') as rstfile:

		# Build lines to write to RST.
		lines_to_write = []
		lines_to_write.append(f".. collapse:: {instance_title or instance_description}\n")
		lines_to_write.append("\n")
		lines_to_write.append(f"\t| \n")
		lines_to_write.append(f"\t| **Name:** ``{instance_name}``\n")
		lines_to_write.append(f"\t| **Description:** {instance_description}\n")
		lines_to_write.append(f"\t| **Code to Load Instance:**\n\n\t.. code-block:: python\n\n\t\tinstance = load_instance('{instance_name}')\n\n")
		lines_to_write.append(f"\t| **Code to Build Manually:**\n\n\t.. code-block:: python\n\n{code_to_build}\n")
		lines_to_write.append("\n")
		
		# Write lines.
		rstfile.writelines(lines_to_write)

	# Close file.
	rstfile.close()


def _save_section_label_to_rst(label, filepath=None, create_if_none=True):
	"""Save a section label to an RST file. 

	Parameters
	----------
	label : str
		The text of the label.
	filepath : str, optional
		Path to the RST file. If ``None``, the function determines the path to 
		``aux_files/stockpyl_instances_metadata.rst``.
	create_if_none : bool, optional
		If the file does not already exist, the function will create a new file if ``True``; 
		otherwise, it will not do anything and issue a warning.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_metadata_path()

	# Make sure path exists; if not, create it.
	os.makedirs(os.path.dirname(filepath), exist_ok=True)

	# Does RST file exist?
	if not os.path.exists(filepath):
		# Should we create it?
		if not create_if_none:
			warnings.warn('filepath does not exist and create_if_none is False; no action was taken')
			return

	# Open RST file.
	with open(filepath, 'a') as rstfile:

		# Build lines to write to RST.
		lines_to_write = []
		lines_to_write.append("\n")
		lines_to_write.append("|\n") # force blank line
		lines_to_write.append("\n")
		lines_to_write.append(f"**{label}**")
		lines_to_write.append("\n\n")
		
		# Write lines.
		rstfile.writelines(lines_to_write)

	# Close file.
	rstfile.close()
	
	
def _save_summary_to_csv(save_filepath, json_filepath=None):
	"""Save a CSV file with a summary of the instances in a JSON file.

	Main purpose of this function is to build the CSV file that populates the table
	at the top of this page.

	Parameters
	----------
	save_filepath : str
		Path to the CSV file to create.
	json_filepath : str, optional
		Path to the JSON file. If ``None``, the function determines the path to 
		``datasets/stockpyl_instances.json``.
	"""

	# Determine filepath.
	if filepath is None:
		filepath = _stockpyl_instances_json_path()

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


def _save_instances_to_rst(save_filepath, json_filepath=None):
	"""Save a RST file with the instances found in ``json_filepath``.

	Main purpose of this function is to build the RST file that populates the list of
	instances at the top of this page.

	Parameters
	----------
	save_filepath : str
		Path to the CSV file to create.
	json_filepath : str, optional
		Path to the JSON file. If ``None``, the function determines the path to 
		``datasets/stockpyl_instances.json``.
	"""
	
	# Determine filepath.
	if json_filepath is None:
		json_filepath = _stockpyl_instances_json_path()

	# Does JSON file exist?
	if os.path.exists(json_filepath):
		# Use this path.
		new_path = json_filepath
	else:
		# Try changing working directory to project root (stockpyl/). This is mainly a workaround for
		# when this function is called from doctests.
		one_level_up = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		new_path = os.path.join(one_level_up, json_filepath)
		if not os.path.exists(new_path):
			raise FileNotFoundError(f"The JSON file {os.path.abspath(json_filepath)} was not found")

	# Load data from JSON.
	with open(new_path) as f:
		json_contents = json.load(f)

	# Open RST file.
	with open(save_filepath, 'w') as rstfile:
		
		# Loop through instances.
		for instance_record in list(json_contents["instances"]):
			
			# Get the instance itself. If instance is of type "network_dict", convert it to a network.
			if instance_record['type'] == "network_dict":
				instance = instance_record['data'].from_dict()
			else:
				instance = instance_record['data']

			# Build lines to write to RST.
			lines_to_write = []
			lines_to_write.append(f".. collapse:: {instance_record['title']}\n")
			lines_to_write.append("\n")
			lines_to_write.append(f"\t| ")
			lines_to_write.append(f"\t| **Name:** ``{instance_record['name']}``\n")
			lines_to_write.append(f"\t| **Description:** {instance_record['description']}\n")
			lines_to_write.append(f"\t| **Code to Load Instance:**\n\n\t.. code-block:: python\n\n\t\tinstance = load_instance('{instance_record['name']}')\n\n")
			lines_to_write.append(f"\t| **Code to Build Manually:**\n\n\t.. code-block:: python\n\n{instance_record['code_to_build']}\n")
			lines_to_write.append("\n")
			
			# Write lines.
			rstfile.writelines(lines_to_write)

	rstfile.close()


	# # Look for instance. (https://stackoverflow.com/a/8653568/3453768)
	# instance_index = next((i for i, item in enumerate(json_contents["instances"]) \
	# 	if item["name"] == instance_name), None)
	# # Was instance found?
	# if instance_index is None:
	# 	raise KeyError("The speficied instance name was not found")

	# # Get instance (in case it was jsonpickled).
	# instance = json_contents["instances"][instance_index]["data"]

	# # Try to decode instance using jsonpickle. This will fail if the
	# # instance is a regular dict, in which case we'll just return the dict.
	# try:
	# 	instance = jsonpickle.decode(instance)

	# 	# Replace the instance with a deep copy of it. This is important because if there are 
	# 	# missing attributes in the saved instance (which can happen if the instance was 
	# 	# saved under an earlier version of the code and a new field was introduced subsequently),
	# 	# the deep copy will contain default values for those attributes.
	# 	if initialize_missing_attributes:
	# 		instance.initialize(overwrite=False)

	# 	# Delete the state variables and replace with initialized version, 
	# 	# if ignore_state_variables = True.
	# 	if ignore_state_vars:
	# 		for n in instance.nodes:
	# 			n.state_vars = []

	# 	return instance
	# except TypeError as e:
	# 	# If the instance contains any dicts with integer keys, they will have
	# 	# been saved as strings when the JSON was saved. Convert them back to integers here.
	# 	# Currently, only demand_pmf has this issue.
	# 	if 'demand_pmf' in instance.keys():
	# 		instance['demand_pmf'] = {int(k): v for k, v in instance['demand_pmf'].items()}

	# 	return instance



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

def _stockpyl_instances_metadata_path():
	"""Determine the path to the RST file containing the instance metadata. 

	Returns
	-------
	str
		The absolute path, including the filename itself.
	"""
	code_file = os.path.abspath(inspect.getsourcefile(_stockpyl_instances_metadata_path))
	rtn = os.path.join(os.path.dirname(code_file), "aux_files", "stockpyl_instances_metadata.rst")
	assert os.path.exists(rtn) and os.path.isfile(rtn)
	return rtn
