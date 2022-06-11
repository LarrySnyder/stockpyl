"""
.. include:: ../../globals.inc

Overview 
--------

Input-output code for simulating multi-echelon stockpyl systems.

.. note:: |node_stage|


API Reference
-------------

"""

import numpy as np
from tabulate import tabulate
import csv
from copy import deepcopy

#from stockpyl.sim import simulation
from stockpyl.helpers import sort_dict_by_keys
from stockpyl.instances import save_instance, load_instance
from stockpyl.demand_source import DemandSource
from stockpyl.disruption_process import DisruptionProcess


def write_results(network, num_periods, num_periods_to_print=None,
				  write_csv=False, csv_filename=None):
	"""

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	num_periods : int
		Number of periods in simulation.
	num_periods_to_print : int, optional
		Number of periods to print. The middle ``num_periods`` -
		``num_periods_to_print`` periods will be skipped. If omitted, will
		print all periods.
	write_csv : bool, optional
		True to write to csv file, False otherwise. Optional; default=False.
	csv_filename : str
		Filename to use for csv. Required if write_csv=True; ignored otherwise.


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
	if num_periods_to_print is None:
		periods_to_print = list(range(num_periods))
	else:
		periods_to_print = list(range(round(num_periods_to_print / 2))) + \
						   list(range(num_periods - round(num_periods_to_print / 2), num_periods))

	# Period-by-period rows.
	for t in periods_to_print:
		temp = [t]
		for node in network.nodes:
			temp += ["|"] + [node.state_vars[t].disrupted] \
					+ sort_dict_by_keys(node.state_vars[t].inbound_order) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_order_pipeline) \
					+ sort_dict_by_keys(node.state_vars[t].order_quantity) \
					+ sort_dict_by_keys(node.state_vars[t].on_order_by_predecessor) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_shipment) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_shipment_pipeline) \
					+ sort_dict_by_keys(node.state_vars[t].raw_material_inventory) \
					+ sort_dict_by_keys(node.state_vars[t].outbound_shipment) \
					+ [node.state_vars[t].demand_met_from_stock,
					node.state_vars[t].fill_rate,
					node.state_vars[t].inventory_level] \
					+ sort_dict_by_keys(node.state_vars[t].backorders_by_successor) \
					+ sort_dict_by_keys(node.state_vars[t].disrupted_items_by_successor ) \
					+ [node.state_vars[t].holding_cost_incurred,
					node.state_vars[t].stockout_cost_incurred,
					node.state_vars[t].in_transit_holding_cost_incurred,
					node.state_vars[t].revenue_earned,
					node.state_vars[t].total_cost_incurred]
		results.append(temp)
		if t+1 not in periods_to_print and t < num_periods-1:
			results.append(["..."])

	# Header row
	headers = ["t"]
	for node in network.nodes:
		headers = headers + ["|i={:d}".format(node.index)] + ["DISR"]
		headers += dict_to_header_list(node.state_vars[0].inbound_order, "IO")
		headers += dict_to_header_list(node.state_vars[0].inbound_order_pipeline, "IOPL")
		headers += dict_to_header_list(node.state_vars[0].order_quantity, "OQ")
		headers += dict_to_header_list(node.state_vars[0].on_order_by_predecessor, "OO")
		headers += dict_to_header_list(node.state_vars[0].inbound_shipment, "IS")
		headers += dict_to_header_list(node.state_vars[0].inbound_shipment_pipeline, "ISPL")
		headers += dict_to_header_list(node.state_vars[0].raw_material_inventory, "RM")
		headers += dict_to_header_list(node.state_vars[0].outbound_shipment, "OS")
		headers += ["DMFS", "FR", "IL"]
		headers += dict_to_header_list(node.state_vars[0].backorders_by_successor, "BO")
		headers += dict_to_header_list(node.state_vars[0].disrupted_items_by_successor , "DI")
		headers += ["HC", "SC", "ITHC", "REV", "TC"]

	# Write results to screen
	print(tabulate(results, headers=headers))

	# Average and total cost
	total_cost = np.sum([n.state_vars[t].total_cost_incurred for n in network.nodes
			for t in range(num_periods)])
	print("\nTotal avg. cost per period = {:f}".format(1.0 * np.sum(total_cost) / num_periods))
	print("Total horizon cost = {:f}".format(1.0 * np.sum(total_cost)))

	# CSV output
	if write_csv:
		with open(csv_filename, 'w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(headers)
			for r in results:
				writer.writerow(r)


def dict_to_header_list(d, abbrev):
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

	