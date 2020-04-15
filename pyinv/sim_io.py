"""Input-output code for simulating multi-echelon pyinv systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the simulation instance.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
from tabulate import tabulate
import csv

from pyinv.sim import *


def write_results(network, num_periods, total_cost, num_periods_to_print=None,
				  write_csv=False, csv_filename=None):
	"""

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon pyinv network.
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

	# Build list of results strings
	results = []

	# Average row.
	temp = ["Avg"]
	for node in network.nodes:
		temp = temp + ["|", np.average(node.inventory_level[:]),
					   node.get_attribute_total('on_order', None) / num_periods,
					   node.get_attribute_total('inbound_shipment', None) / num_periods,
					   node.get_attribute_total('inbound_order', None) / num_periods,
					   np.average(node.order_quantity[:]),
					   node.get_attribute_total('outbound_shipment', None) / num_periods,
					   np.average(node.demand_met_from_stock[:]),
					   np.average(node.fill_rate[:]),
					   np.average(node.ending_inventory_level[:]),
					   node.get_attribute_total('backorders', None) / num_periods,
					   np.average(node.holding_cost_incurred[:]),
					   np.average(node.stockout_cost_incurred[:]),
					   np.average(node.in_transit_holding_cost_incurred[:]),
					   np.average(node.total_cost_incurred[:])]
	results.append(temp)
	results.append([""])

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
			temp = temp + ["|", node.inventory_level[t],
						   node.get_attribute_total('on_order', t),
						   node.get_attribute_total('inbound_shipment', t),
						   node.get_attribute_total('inbound_order', t),
						   node.order_quantity[t],
						   node.get_attribute_total('outbound_shipment', t),
						   node.demand_met_from_stock[t],
						   node.fill_rate[t],
						   node.ending_inventory_level[t],
						   node.get_attribute_total('backorders', t),
						   node.holding_cost_incurred[t],
						   node.stockout_cost_incurred[t],
						   node.in_transit_holding_cost_incurred[t],
						   node.total_cost_incurred[t]]
		results.append(temp)
		if t+1 not in periods_to_print and t < num_periods-1:
			results.append(["..."])
	# Header row
	headers = ["t"]
	for n in network.nodes:
		headers = headers + ["|i={:d}".format(n.index), "IL", "OO", "IS", "IO", "OQ",
							 "OS", "DMFS", "FR", #"BEI",
							 "EIL", "BO", "HC", "SC", "ITHC", "TC"]

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

