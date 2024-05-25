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
	* The node number is indicated in the first column in the group (i.e., i=1).
	* (node, product) pairs are indicated by a vertical line, so '2|20' means node 2, product 20.
	* The columns for each node are as follows:

		- ``i=<node index>``: label for the column group
		- ``DISR``: was the node disrupted in the period? (True/False)
		- ``IO:s|prod``: inbound order for product ``prod`` received from successor ``s``
		- ``IOPL:s|prod``: inbound order pipeline for product ``prod`` from successor ``s``: a list of order
		  quantities arriving from succesor ``s`` in ``r`` periods from the
		  period, for ``r`` = 1, ..., ``order_lead_time``
		- ``OQ:p|prod``: order quantity placed to predecessor ``p`` for product ``prod``
		- ``OQFG:prod``: order quantity of finished good ``prod`` (this "order" is never actually placed—only
		   the raw material orders in ``OQ`` are placed; but ``OQFG`` can be useful for debugging)
		- ``OO:p:prod``: on-order quantity (items of product ``prod`` that have been ordered from successor
		  ``p`` but not yet received) 
		- ``IS:p|prod``: inbound shipment of product ``prod`` received from predecessor ``p`` 
		- ``ISPL:p|prod``: inbound shipment pipeline for product ``prod`` from predecessor ``p``: a list of
		  shipment quantities arriving from predecessor ``p`` in ``r`` periods from
		  the period, for ``r`` = 1, ..., ``shipment_lead_time``
		- ``IDI:p|prod``: inbound disrupted items: number of items of product ``prod`` from predecessor ``p``
		  that cannot be received due to a type-RP disruption at the node
		- ``RM:prod``: number of items of product ``prod`` in raw-material inventory at node
		- ``PFG:prod``: number of items of product ``prod`` that are pending, waiting to be
		  processed from raw materials
		- ``OS:s|prod``: outbound shipment of product ``prod`` to successor ``s``
		- ``DMFS|prod``: demand of product ``prod`` met from stock at the node in the current period
		- ``FR|prod``: fill rate of product ``prod``; cumulative from start of simulation to the current period
		- ``IL|prod``: inventory level of product ``prod`` (positive, negative, or zero) at node
		- ``BO:s|prod``: backorders of product ``prod`` owed to successor ``s``
		- ``ODI:s|prod``: outbound disrupted items of product ``prod``: number of items held for successor ``s`` due to
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
	* Negative product indices are "dummy products"

.. seealso::

	For an overview of simulation in |sp|,
	see the :ref:`tutorial page for simulation<tutorial_sim_page>`.



API Reference
-------------

"""

from tabulate import tabulate
import csv
from copy import deepcopy

#from stockpyl.sim import simulation
from stockpyl.helpers import sort_dict_by_keys, sort_nested_dict_by_keys, is_list
from stockpyl.instances import save_instance, load_instance
from stockpyl.demand_source import DemandSource
from stockpyl.disruption_process import DisruptionProcess


def write_results(network, num_periods, periods_to_print=None, columns_to_print=None, suppress_dummy_products=True,
					write_txt=False, txt_filename=None, write_csv=False, csv_filename=None):
	"""Write the results of a simulation to the console, as well as to a TXT and/or CSV file if requested.

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
	suppress_dummy_products : bool, optional
		``True`` (default) to omit dummy product indices in column headers, ``False`` to display them. 
		If dummy product indices are suppressed, 
		raw material inventories are indicated by their predecessor node indices rather than product indices.
	write_txt : bool, optional
		``True`` to write the output that is printed to the terminal to TXT file also, ``False`` otherwise. 
		Optional; default = ``False``.
	txt_filename : str, optional
		Filename to use for TXT file. Required if ``write_txt`` = ``True``; ignored otherwise.
	write_csv : bool, optional
		``True`` to write to CSV file, ``False`` otherwise. Optional; default = ``False``.
	csv_filename : str, optional
		Filename to use for CSV file. Required if ``write_csv`` = ``True``; ignored otherwise.


	Returns
	-------

	"""

	# Build lists of results strings.
	results = []

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
		cols_to_print = ['DISR', 'IO', 'IOPL', 'OQ', 'OQFG', 'OO', 'IS', 'ISPL', 'IDI', 'RM', 'PFG', 'OS', 'DMFS', 'FR', 'IL', 'BO', 'ODI', 'HC', 'SC', 'ITHC', 'REV', 'TC']
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
		# Loop through nodes.
		for ind in sorted_nodes:
			node = network.nodes_by_index[ind]

			# Remove 0th element of pipelines because these will always be 0 at the end of the period.
			IOPL_temp = sort_nested_dict_by_keys(node.state_vars[t].inbound_order_pipeline)
			IOPL = [x[1:] for x in IOPL_temp]
			ISPL_temp = sort_nested_dict_by_keys(node.state_vars[t].inbound_shipment_pipeline)
			ISPL = [x[1:] for x in ISPL_temp]
			# Build row.
			temp += ['|']
			if 'DISR'	in cols_to_print: temp += [node.state_vars[t].disrupted]
			if 'IO'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].inbound_order) 
			if 'IOPL'	in cols_to_print: temp += IOPL
			if 'OQ'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].order_quantity) 
			if 'OQFG'	in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].order_quantity_fg) 
			if 'OO'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].on_order_by_predecessor) 
			if 'IS'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].inbound_shipment) 
			if 'ISPL'	in cols_to_print: temp += ISPL
			if 'IDI'	in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].inbound_disrupted_items) 
			if 'RM'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].raw_material_inventory) 
			if 'PFG'	in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].pending_finished_goods) 
			if 'OS'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].outbound_shipment) 
			if 'DMFS'	in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].demand_met_from_stock)
			if 'FR'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].fill_rate)
			if 'IL'		in cols_to_print: temp += sort_dict_by_keys(node.state_vars[t].inventory_level)
			if 'BO'		in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].backorders_by_successor) 
			if 'ODI'	in cols_to_print: temp += sort_nested_dict_by_keys(node.state_vars[t].outbound_disrupted_items) 
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
		node = network.nodes_by_index[ind]
		headers = headers + [f"| i={ind:d}"] 
		if 'DISR'	in cols_to_print: headers += ['DISR']
		if 'IO'		in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].inbound_order, "IO", omit_negative_keys=suppress_dummy_products)
		if 'IOPL'	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].inbound_order_pipeline, "IOPL", omit_negative_keys=suppress_dummy_products)
		if 'OQ' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].order_quantity, "OQ", omit_negative_keys=suppress_dummy_products)
		if 'OQFG' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].order_quantity_fg, "OQFG", omit_negative_keys=suppress_dummy_products)
		if 'OO' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].on_order_by_predecessor, "OO", omit_negative_keys=suppress_dummy_products)
		if 'IS' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].inbound_shipment, "IS", omit_negative_keys=suppress_dummy_products)
		if 'ISPL' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].inbound_shipment_pipeline, "ISPL", omit_negative_keys=suppress_dummy_products)
		if 'IDI' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].inbound_disrupted_items, "IDI", omit_negative_keys=suppress_dummy_products)
		if 'RM' 	in cols_to_print: 
			# If suppress_dummy_products, use predecessor indices instead of product indices.
			if suppress_dummy_products:
				temp_dict = {}
				for k, v in node.state_vars[0].raw_material_inventory.items():
					if network.products_by_index[k].is_dummy: 
						temp_dict[node.raw_material_suppliers_by_raw_material(raw_material=k, return_indices=True)[0]] = v
					else:
						temp_dict[k] = v
				# temp_dict = {node.raw_material_suppliers_by_raw_material(raw_material=k, return_indices=True)[0]: v for k, v in node.state_vars[0].raw_material_inventory.items()}
			else:
				temp_dict = node.state_vars[0].raw_material_inventory
			headers += _dict_to_header_list(temp_dict, "RM")
		if 'PFG' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].pending_finished_goods, "PFG", omit_negative_keys=suppress_dummy_products)
		if 'OS' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].outbound_shipment, "OS", omit_negative_keys=suppress_dummy_products)
		if 'DMFS' 	in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].demand_met_from_stock, "DMFS", omit_negative_keys=suppress_dummy_products)
		if 'FR'		in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].fill_rate, "FR", omit_negative_keys=suppress_dummy_products)
		if 'IL'		in cols_to_print: headers += _dict_to_header_list(node.state_vars[0].inventory_level, "IL", omit_negative_keys=suppress_dummy_products)
		if 'BO' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].backorders_by_successor, "BO", omit_negative_keys=suppress_dummy_products)
		if 'ODI' 	in cols_to_print: headers += _nested_dict_to_header_list(node.state_vars[0].outbound_disrupted_items , "ODI", omit_negative_keys=suppress_dummy_products)
		if 'HC'		in cols_to_print: headers += ["HC"]
		if 'SC'		in cols_to_print: headers += ["SC"]
		if 'ITHC'	in cols_to_print: headers += ["ITHC"]
		if 'REV'	in cols_to_print: headers += ["REV"]
		if 'TC'		in cols_to_print: headers += ["TC"]

	# Average row.
	averages = ["t"]

	# Write results to screen.
	print(tabulate(results, headers=headers))

	# Write results to TXT file, if requested.
	if write_txt:
		with open(txt_filename, 'w') as txtFile:
			txtFile.write(tabulate(results, headers=headers))

	# Write results to CSV file, if requested.
	if write_csv:
		# Remove vertical bars -- these look good in the txt but not the csv.
		for i in range(len(headers)):
			headers[i] = headers[i].replace('| ', '') # has no effect if '| ' is not in the entry
		for r in results:
			for i in range(len(r)):
				if r[i] == '|':
					r[i] = ''

		# Write file.
		with open(csv_filename, 'w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(headers)
			for r in results:
				writer.writerow(r)


def _dict_to_header_list(d, abbrev, omit_negative_keys=False):
	"""Return list of headers for the given abbreviation and the values of the
	dict ``d``.

	Parameters
	----------
	d : dict
		The dict whose values should be used.
	abbrev : str
		The abbreviation string to use.
	omit_negative_keys : bool, optional
		``True`` to omit ``:k`` (where ``k`` is the key from the dictionary) if 
		``k`` is negative, ``True`` (default) to include it.

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
		header = abbrev
		if i is None:
			header += ':EXT'
		elif i >= 0 or not omit_negative_keys:
			header += f':{i:d}'
		header_list.append(header)

	return header_list


def _nested_dict_to_header_list(d, abbrev, omit_negative_keys=False):
	"""Return list of headers for the given abbreviation and the values of the
	nested dict ``d``.

	Parameters
	----------
	d : dict
		The dict whose values should be used.
	abbrev : str
		The abbreviation string to use.
	omit_negative_keys : bool, optional
		``True`` to omit ``|k`` (where ``k`` is the key from the inner dictionary) if 
		``k`` is negative, ``True`` (default) to include it.

	Returns
	-------
	header_list : list
		List of header strings.
	"""
	# Get list of dict keys, sorted in ascending order.
	sorted_dict_keys = sort_nested_dict_by_keys(d, return_values=False)
	# Build header list.
	header_list = []
	for i in sorted_dict_keys:
		if i[0] is None:
			header = f'{abbrev}:EXT'
		else:
			header = f'{abbrev}:{i[0]:d}'
		if i[1] >= 0 or not omit_negative_keys:
			header += f'|{i[1]:d}'
		header_list.append(header)

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

	