"""Input-output code for simulating multi-echelon stockpyl systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the simulation instance.

(c) Lawrence V. Snyder
Lehigh University

"""

import numpy as np
from tabulate import tabulate
import csv

from stockpyl.sim import *


def write_results(network, num_periods, total_cost, num_periods_to_print=None,
				  write_csv=False, csv_filename=None):
	"""

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	num_periods : int
		Number of periods in simulation.
	total_cost : float
		Total cost in the simulation.
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

	# TODO: sort nodes in order of index before printing

	# Build list of results strings
	results = []

	# Average row. # TODO: handle averages
#	temp = ["Avg"]
# 	for node in network.nodes:
# 		temp = temp + ["|", #np.average([node.state_vars[t].inventory_level for t in range(num_periods)]),
# 					   node.get_attribute_total('inbound_order', None) / num_periods,
# 					   None,
# 					   None, # TODO: handle average Q by predecessor
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
			temp += ["|"] + sort_dict_by_keys(node.state_vars[t].inbound_order) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_order_pipeline) \
					+ sort_dict_by_keys(node.state_vars[t].order_quantity) \
					+ sort_dict_by_keys(node.state_vars[t].on_order_by_predecessor) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_shipment) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_shipment_pipeline) \
					+ sort_dict_by_keys(node.state_vars[t].raw_material_inventory) \
					+ sort_dict_by_keys(node.state_vars[t].outbound_shipment) \
					+ [node.state_vars[t].demand_met_from_stock,
					node.state_vars[t].fill_rate,
					node.state_vars[t].inventory_level,
					node.state_vars[t].holding_cost_incurred,
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
		headers = headers + ["|i={:d}".format(node.index)]
		headers += dict_to_header_list(node.state_vars[0].inbound_order, "IO")
		headers += dict_to_header_list(node.state_vars[0].inbound_order_pipeline, "IOPL")
		headers += dict_to_header_list(node.state_vars[0].order_quantity, "OQ")
		headers += dict_to_header_list(node.state_vars[0].on_order_by_predecessor, "OO")
		headers += dict_to_header_list(node.state_vars[0].inbound_shipment, "IS")
		headers += dict_to_header_list(node.state_vars[0].inbound_shipment_pipeline, "ISPL")
		headers += dict_to_header_list(node.state_vars[0].raw_material_inventory, "RM")
		headers += dict_to_header_list(node.state_vars[0].outbound_shipment, "OS")
		headers += ["DMFS", "FR", "IL", "HC", "SC", "ITHC", "REV", "TC"]

	# Write results to screen
	print(tabulate(results, headers=headers))

	# Average and total cost
	print("\nTotal avg. cost per period = {:f}".format(1.0 * np.sum(total_cost) / num_periods))
	print("Total horizon cost = {:f}".format(1.0 * np.sum(total_cost)))

	# CSV output
	if write_csv:
		csvFile = open(csv_filename, 'w')
		with csvFile:
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
