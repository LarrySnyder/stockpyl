"""Input-output code for simulating multi-echelon inventory systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the simulation instance.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
from tabulate import tabulate
import csv

from inventory.sim import *


def write_results(network, num_periods, write_csv=False, csv_filename=None):
	"""

	Parameters
	----------
	network : DiGraph
		NetworkX directed graph representing the multi-echelon inventory network,
		with performance measures filled.
	num_periods : int
		Number of periods in simulation.
	write_csv : bool, optional
		True to write to csv file, False otherwise. Optional; default=False.
	csv_filename : str
		Filename to use for csv. Required if write_csv=True; ignored otherwise.


	Returns
	-------

	"""

	# Build list of results strings
	results = []
	for t in range(num_periods):
		temp = [t]
		for n in network.nodes():
			node = network.nodes[n]
			temp = temp + ["|", node['IL'][t],
						   get_attribute_total(n, network, 'OO', t),
						   get_attribute_total(n, network, 'IS', t),
						   get_attribute_total(n, network, 'IO', t),
						   node['OQ'][t],
						   get_attribute_total(n, network, 'OS', t),
						   node['DMFS'][t], node['FR'][t], #node['BEI'][t],
						   node['EIL'][t], node['HC'][t], node['SC'][t],
						   node['TC'][t]]

#		temp = temp + ["|", ".", ".", ".", sim_results["AO"][NUM_STAGES][t], ".", sim_results["OS"][NUM_STAGES][t], ".", ".", ".", ".", ".", ".", "."]
		results.append(temp)

	# Header row
	headers = ["t"]
	for n in network.nodes():
		headers = headers + ["|i={:d}".format(n), "IL", "OO", "AS", "AO", "OQ",
							 "OS", "DMFS", "FR", #"BEI",
							 "EIL", "HC", "SC", "TC"]

	# Write results to screen
	print(tabulate(results, headers=headers))

	# Average and total cost
	print("Total avg. cost per period = {:f}".format(1.0 * np.sum(network.graph['total_cost']) / num_periods))
	print("Total horizon cost = {:f}".format(1.0 * np.sum(network.graph['total_cost'])))

	# CSV output
	if write_csv:
		csvFile = open(csv_filename, 'w')
		with csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(headers)
			for r in results:
				writer.writerow(r)

