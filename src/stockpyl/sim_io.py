"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_sim_io| module contains functions for writing the results of simulations. The main
function is :func:`write_results`, which writes a table to stdout (as well as to a CSV file
if requested) that lists the state variables for all nodes in the network and all periods
in the simulation. All state variables refer to their values at the end of the period.

.. note:: |node_stage|

The table has the following format:

	* Each row corresponds to a period in the simulation.
	* Each node is represented by a group of columns. 
	* The columns for each node are as follows:

		- ``i=<node index>``: label for the column group
		- ``DISR``: was the node disrupted in the period? (True/False)
		- ``IO:s``: inbound order received from successor ``s``
		- ``IOPL:s``: inbound order pipeline from successor ``s``: a list of order
		  quantities arriving from succesor ``s`` in ``r`` periods from the
		  period, for ``r`` = 1, ..., ``order_lead_time``
		- ``OQ:p``: order quantity placed to predecessor ``p`` in the period
		- ``OO:p``: on-order quantity (items that have been ordered from successor
		  ``p`` but not yet received) 
		- ``IS:p``: inbound shipment received from predecessor ``p`` 
		- ``ISPL:p``: inbound shipment pipeline from predecessor ``p``: a list of
		  shipment quantities arriving from predecessor ``p`` in ``r`` periods from
		  the period, for ``r`` = 1, ..., ``shipment_lead_time``
		- ``IDI:p``: inbound disrupted items: number of items from predecessor ``p``
		  that cannot be received due to a type-RP disruption at the node
		- ``RM:p``: number of items from predecessor ``p`` in raw-material inventory
		  at node
		- ``OS:s``: outbound shipment to successor ``s``
		- ``DMFS``: demand met from stock at the node in the current period
		- ``FR``: fill rate; cumulative from start of simulation to the current period
		- ``IL``: inventory level (positive, negative, or zero) at node
		- ``BO:s``: backorders owed to successor ``s``
		- ``ODI:s``: outbound disrupted items: number of items held for successor ``s`` due to
		  a type-SP disruption at ``s``
		- ``HC``: holding cost incurred at the node in the period
		- ``SC``: stockout cost incurred at the node in the period
		- ``ITHC``: in-transit holding cost incurred for items in transit to all successors
		  of the node
		- ``REV``: revenue (**Note:** *not currently supported*)
		- ``TC``: total cost incurred at the node (holding, stockout, and in-transit holding)

	* For state variables that are indexed by successor, if ``s`` = ``EXT``, the column
	  refers to the node's external customer
	* For state variables that are indexed by predecessor, if ``p`` = ``EXT``, the column
	  refers to the node's external supplier


.. admonition:: See Also

	For an overview of simulation in |sp|,
	see the :ref:`tutorial page for simulation<tutorial_sim_page>`.



API Reference
-------------

"""

import numpy as np
from tabulate import tabulate
import csv
from copy import deepcopy
import pandas as pd

#from stockpyl.sim import simulation
from stockpyl.helpers import sort_dict_by_keys, is_list
from stockpyl.instances import save_instance, load_instance
from stockpyl.demand_source import DemandSource
from stockpyl.disruption_process import DisruptionProcess


def write_results(network, num_periods, periods_to_print=None, columns_to_print=None,
				  write_csv=False, csv_filename=None):
	"""Write the results of a simulation to the console, as well as to a CSV file if requested.

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	num_periods : int
		Number of periods in simulation.
	periods_to_print : list or int, optional
		A list of period numbers to print, or the number of periods to print. In the latter case,
		the middle ``num_periods`` – ``periods_to_print`` periods will be skipped. If omitted, will
		print all periods (the default).
	columns_to_print : list or str, optional
		A list of columns to include in the table of results, each indicated as a string using the
		abbreviations given in the list above. Alternately, a string or a list of strings, which are shortcuts to
		groups of columns; currently supported strings are:
		
			* ``'basic'``: ``'IO'``, ``'OQ'``, ``'IS'``, ``'OS'``, ``'IL'``
			* ``'costs'``: ``'HC'``, ``'SC'``, ``'TC'``
			* ``'all'``: prints all columns (equivalent to setting ``columns_to_print=None``)

		Unrecognized strings are ignored. If omitted, will print all columns (the default). 
	write_csv : bool, optional
		``True`` to write to CSV file, ``False`` otherwise. Optional; default = ``False``.
	csv_filename : str, optional
		Filename to use for CSV file. Required if ``write_csv`` = ``True``; ignored otherwise.


	Returns
	-------

	"""

	# Build list of results strings
	results = []

#	temp = ["Avg"]
# 	for node in network.nodes:
# 		temp = temp + ["|", #np.average([node.state_vars[t].inventory_level for t in range(num_periods)]),
# 					   node.get_attribute_total('inbound_order', None) / num_periods,
# 					   None,
# 					   None, 
# 					   node.get_attribute_total('on_order_by_predecessor', None) / num_periods,
# 					   None,
# 					   None, None,
# 					   node.get_attribute_total('outbound_shipment', None) / num_periods,
# 					   np.average([node.state_vars[t].demand_met_from_stock for t in range(num_periods)]),
# 					   np.average([node.state_vars[t].fill_rate for t in range(num_periods)]),
# 					   np.average([node.state_vars[t].inventory_level for t in range(num_periods)]),
# #					   node.get_attribute_total('backorders_by_successor', None) / num_periods,
# 					   np.average([node.state_vars[t].holding_cost_incurred for t in range(num_periods)]),
# 					   np.average([node.state_vars[t].stockout_cost_incurred for t in range(num_periods)]),
# 					   np.average([node.state_vars[t].in_transit_holding_cost_incurred for t in range(
# 						   num_periods)]),
# 					   np.average([node.state_vars[t].total_cost_incurred for t in range(num_periods)])]
#	results.append(temp)
#	results.append([""])

	# Determine periods to print.
	if periods_to_print is None:
		pers_to_print = list(range(num_periods))
		print_dots = False
	elif is_list(periods_to_print):
		pers_to_print = periods_to_print
		print_dots = False
	else:
		pers_to_print = list(range(round(periods_to_print / 2))) + \
						   list(range(num_periods - round(periods_to_print / 2), num_periods))
		print_dots = True

	# Determine columns to print.
	if columns_to_print is None or columns_to_print == 'all' or 'all' in columns_to_print:
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
	elif not is_list(columns_to_print) and isinstance(columns_to_print, str):
		# columns_to_print is a string; put it in a list.
		cols_to_print = [columns_to_print]
	else:
		cols_to_print = columns_to_print
	# Now expand any built-in strings in the cols_to_print list.
	if 'basic' in cols_to_print:
		cols_to_print.remove('basic')
		cols_to_print.extend(['IO', 'OQ', 'IS', 'OS', 'IL'])
	if 'costs' in cols_to_print:
		cols_to_print.remove('costs')
		cols_to_print.extend(['HC', 'SC', 'TC'])

	# Period-by-period rows.
	for t in pers_to_print:
		temp = [t]
		sorted_nodes = sorted(network.node_indices)
		for ind in sorted_nodes:
			node = network.get_node_from_index(ind)
			# Remove 0th element of pipelines because these will always be 0 at the end of the period.
			IOPL_temp = sort_dict_by_keys(node.state_vars[t].inbound_order_pipeline)
			IOPL = [x[1:] for x in IOPL_temp]
			ISPL_temp = sort_dict_by_keys(node.state_vars[t].inbound_shipment_pipeline)
			ISPL = [x[1:] for x in ISPL_temp]
			# Build row.
			temp += ['']
			if 'DISR'	in cols_to_print: temp += [node.state_vars[t].disrupted]
			if 'IO'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].inbound_order) 
			if 'IOPL'	in cols_to_print: temp += IOPL
			if 'OQ'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].order_quantity) 
			if 'OO'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].on_order_by_predecessor) 
			if 'IS'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].inbound_shipment) 
			if 'ISPL'	in cols_to_print: temp += ISPL
			if 'IDI'	in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].inbound_disrupted_items) 
			if 'RM'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].raw_material_inventory) 
			if 'OS'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].outbound_shipment) 
			if 'DMFS'	in cols_to_print: temp += [node.state_vars[t].demand_met_from_stock]
			if 'FR'		in cols_to_print: temp += [node.state_vars[t].fill_rate]
			if 'IL'		in cols_to_print: temp += [node.state_vars[t].inventory_level]
			if 'BO'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].backorders_by_successor) 
			if 'ODI'	in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].outbound_disrupted_items) 
			if 'HC'		in cols_to_print: temp += [node.state_vars[t].holding_cost_incurred]
			if 'SC'		in cols_to_print: temp += [node.state_vars[t].stockout_cost_incurred]
			if 'ITHC'	in cols_to_print: temp += [node.state_vars[t].in_transit_holding_cost_incurred]
			if 'REV'	in cols_to_print: temp += [node.state_vars[t].revenue_earned]
			if 'TC' 	in cols_to_print: temp += [node.state_vars[t].total_cost_incurred]
		results.append(temp)
		if print_dots and t+1 not in pers_to_print and t < num_periods-1:
			results.append(["..."])

	# Header row
	headers = ["t"]
	for ind in sorted_nodes:
		node = network.get_node_from_index(ind)
		headers = headers + ["i={:d}".format(node.index)] 
		if 'DISR'	in cols_to_print: headers += ['DISR']
		if 'IO'		in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inbound_order, "IO")
		if 'IOPL'	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inbound_order_pipeline, "IOPL")
		if 'OQ' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].order_quantity, "OQ")
		if 'OO' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].on_order_by_predecessor, "OO")
		if 'IS' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inbound_shipment, "IS")
		if 'ISPL' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inbound_shipment_pipeline, "ISPL")
		if 'IDI' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inbound_disrupted_items, "IDI")
		if 'RM' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].raw_material_inventory, "RM")
		if 'OS' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].outbound_shipment, "OS")
		if 'DMFS' 	in cols_to_print: headers += ["DMFS"]
		if 'FR'		in cols_to_print: headers += ["FR"]
		if 'IL'		in cols_to_print: headers += ["IL"]
		if 'BO' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].backorders_by_successor, "BO")
		if 'ODI' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].outbound_disrupted_items , "ODI")
		if 'HC'		in cols_to_print: headers += ["HC"]
		if 'SC'		in cols_to_print: headers += ["SC"]
		if 'ITHC'	in cols_to_print: headers += ["ITHC"]
		if 'REV'	in cols_to_print: headers += ["REV"]
		if 'TC'		in cols_to_print: headers += ["TC"]

	# Average row.
	averages = ["t"]

	# Write results to screen
	print(tabulate(results, headers=headers))

	# CSV output
	if write_csv:
		with open(csv_filename, 'w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(headers)
			for r in results:
				writer.writerow(r)


def _dict_to_header_list(d, abbrev):
	"""Return list of headers for the given abbreviation and the values of the
	dict ``d``.

	Parameters
	----------
	d : dict
		The dict whose values should be used.
	abbrev : str
		The abbreviation string to use.

	Returns
	-------
	header_list : list
		List of header strings.
	"""
	# Get list of dict keys, sorted in ascending order.
	sorted_dict_keys = sort_dict_by_keys(d, return_values=False)
	# Build header list.
	header_list = []
	for i in sorted_dict_keys:
		if i is None:
			header_list.append(abbrev + ":EXT")
		else:
			header_list.append(abbrev + ":{:d}".format(i))

	return header_list


def write_instance_and_states(network, filepath, instance_name=None, num_periods=None):
	"""Write a JSON file containing the instance and all of the history of the
	state variables. This is mostly used for debugging.

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	filepath : str
		The filename and path for the saved JSON file.
	instance_name : str, optional
		The name of the instance to use when saving.
	num_periods : int, optional
		Number of periods of state data to save. If ``None``, will save all
		periods in the simulation (even if some are all zeroes).
	"""

	# Make a copy of the network.
	new_network = deepcopy(network)

	# Determine how many periods to save.
	num_periods_to_save = num_periods or len(new_network.nodes[0].state_vars)

	for node in new_network.nodes:
	
		# Change network's demands to deterministic, with the demands given in the state history.
		if node.demand_source is not None and node.demand_source.type is not None:
			# Create new demand source.
			demand_list = [node.state_vars[t].inbound_order[None] for t in range(num_periods_to_save)]
			node.demand_source = DemandSource(
				type='D',
				demand_list=demand_list
			)

		# Change network's disruptions to deterministic, with the disruptions given in
		# the state history.
		if node.disruption_process is not None and node.disruption_process.random_process_type is not None:
			# Create new disruption process.
			disruption_list = [node.state_vars[t].disrupted for t in range(num_periods_to_save)]
			node.disruption_process = DisruptionProcess(
				random_process_type='E',
				disruption_type=node.disruption_process.disruption_type,
				disruption_state_list=disruption_list
			)

	# Save the instance, excluding state variables.
	save_instance(
		instance_name=instance_name,
		instance_data=new_network,
		filepath=filepath,
		replace=True,
		omit_state_vars=True
	)

	