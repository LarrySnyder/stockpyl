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
		- ``RM:p``: number of items from predecessor ``p`` in raw-material inventory
		  at node
		- ``OS:s``: outbound shipment to successor ``s``
		- ``DMFS``: demand met from stock at the node in the current period
		- ``FR``: fill rate; cumulative from start of simulation to the current period
		- ``IL``: inventory level (positive, negative, or zero) at node
		- ``BO:s``: backorders owed to successor ``s``
		- ``DI:s``: disrupted items: number of items held for successor ``s`` due to
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


**Example:** Consider a 4-node system in which nodes 1 and 2 face external demand; node 3 has
an external supplier and serves nodes 1 and 2; and node 4 has an external customer and serves node 1.
Since node 1 has two predecessors (nodes 3 and 4), node 1 needs one unit from each predecessor in order
to make one unit of its own item.
Demands at nodes 1 and 2 have Poisson distributions with mean 10. The holding cost is 1 at nodes 3 and 4
and 2 at nodes 1 and 2. The stockout cost is 10 at nodes 1 and 2. Node 1 has no order lead time and a
shipment lead time of 2. Node 2 has an order lead time of 1 and a shipment lead time of 1. Nodes 3 and for
each have a shipment lead time of 1. Each stage follows a base-stock policy, with base-stock levels of
12, 12, 20, 12 at nodes 1, ..., 4, respectively. The code below builds this network, simulates it for 10 periods, and 
displays the results.

	.. code-block::
		
		>>> from stockpyl.supply_chain_network import network_from_edges
		>>> network = network_from_edges(
		...     edges=[(3, 2), (3, 1), (4, 1)],
		...     node_order_in_lists=[1, 2, 3, 4],
		...     local_holding_cost=[2, 2, 1, 1],
		...     stockout_cost=[10, 10, 0, 0],
		...     order_lead_time=[0, 1, 0, 0],   
		...     shipment_lead_time=[2, 1, 0, 1],
		...     demand_type=['P', 'P', None, None],
		...     mean=[10, 10, None, None],
		...     policy_type=['BS', 'BS', 'BS', 'BS'],
		...     base_stock_level=[30, 25, 10, 10]
		... )
		>>> simulation(network=network, num_periods=10)
		>>> write_results(network, num_periods=T)

The results are shown in the table below. In period 0:

	* Node 1 has a demand of 13 (``IO:EXT`` column),
	  places orders to nodes 3 and 4 of size 13 each (``OQ:3`` and ``OQ:4`` columns), ships 13 units
	  to its customer (``OS:EXT``), and ends the period with an inventory level of 17 (``IL``), incurring
	  a holding cost (``HC``) and a total cost (``TC``) of 34. (Each node begins the
	  simulation with its inventory level equal to its base-stock level.) 
	* Node 2 has a demand of 9, places an order of size 9 to node 3, ships 9 units to its customer, 
	  and ends the period with an inventory level of 16. 
	* Node 3 receives the order of 13 from node 1 (``IO:1`` = 13), but not the order from node 2 (``IO:2`` = 0)
	  since node 2 has an order lead time of 1. Node 2's order is in node 3's inbound order pipeline
	  (``IOPL:2``). Node 3 places an order of size 13 to its supplier (``OQ:EXT``) and receives it immediately
	  as an inbound shipment (``IS:EXT``) because its lead time is 0. It ships 13 units to node 1 (``OS:1``) but no units
	  to node 2 (``OS:2``) since it has not yet received an order from node 2. Its ending inventory level is 10.
	* Node 4 receives the order of size 13 from node 1 (``IO:1``), places an order of size 13 to its supplier (``OQ:EXT``).
	  It does not receive the shipment yet since its shipment lead time is 1, but the shipment appears in its
	  inbound shipment pipeline (``ISPL:EXT``). It began the period with 10 units in inventory, so it ships those
	  10 units to node 1 (``OS:1``), has 3 backorders for node 1 (``BO:1``), and ends with an inventory level of -3 (``IL``).

In period 1:

	* Node 1 receives a demand of 10, orders 10 units from nodes 3 and 4, so it now has 23 units on order from each
	  predecessor (``OO:3`` and ``OO:4``). Node 3 shipped 13 units in period 0 and will ship 10 in period 1, so node 1's
	  inbound shipment pipeline from node 3 (``ISPL:3``) shows 13 units arriving in one period and 10 units arriving in two periods.
	  Node 4 shipped only 10 units in period 0 (because of its insufficient inventory) and 13 in period 1, which
	  is reflected in ``ISPL:4``. Node 1 ships 10 units to its supplier and ends the period with an inventory level of 7.
	* Node 2 receives a demand of 9 again, places an order of size 9, ships 9 units to its customer, and ends
	  with an inventory level of 7.
	* Node 3 receives an order of size 10 from node 1 (``IO:1``), which node 1 placed in period 0, and an order of size
	  9 from node 2 (``IO:2``), which node 2 placed in period 1. It places an order of size 19, receives it immediately,
	  ships 10 units to node 1 and 9 to node 2, and ends with 10 units in inventory.
	* Node 4 receives the order of size 10 from node 1 and places an order of size 10. It receives the order of 13 that
	  it placed to its supplier in node 0 (``IS:EXT``), ships 13 units to node 1 (3 of which were backorders from period 0
	  and 10 of which are for the current demand), and ends with an inventory level of 0.

And so on. Also worth noting is that in period 2, node 1 receives 13 units from node 3 and 10 from node 4. It needs one 
unit from each predecessor to make one unit of its own finished product, so it can only make 10 such units, and
3 units of node 3's product remains in node 1's raw material inventory (``RM:3``). Node 1 began period 2 with an
inventory level of 7, received a demand of 9, and added 10 units to its finished goods inventory, so its ending
inventory level is 8 (``IL``). These 8 units incur a holding cost of 2 each; but the 3 units in raw material inventory
incur node 3's holding cost rate of 1 each. So, the total holding cost (``HC``) at node 1 is 19 in period 2.
	  


.. csv-table:: Simulation Results
   :file: ../../docs/aux_files/sim_io_example_instance.csv
   :widths: auto
   :header-rows: 1
   :stub-columns: 1


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
		Number of periods to print. The middle ``num_periods`` –
		``num_periods_to_print`` periods will be skipped. If omitted, will
		print all periods.
	write_csv : bool, optional
		True to write to CSV file, False otherwise. Optional; default = ``False``.
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
	if num_periods_to_print is None:
		periods_to_print = list(range(num_periods))
	else:
		periods_to_print = list(range(round(num_periods_to_print / 2))) + \
						   list(range(num_periods - round(num_periods_to_print / 2), num_periods))

	# Period-by-period rows.
	for t in periods_to_print:
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
			temp += [''] + [node.state_vars[t].disrupted] \
					+ sort_dict_by_keys(node.state_vars[t].inbound_order) \
					+ IOPL \
					+ sort_dict_by_keys(node.state_vars[t].order_quantity) \
					+ sort_dict_by_keys(node.state_vars[t].on_order_by_predecessor) \
					+ sort_dict_by_keys(node.state_vars[t].inbound_shipment) \
					+ ISPL \
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
	for ind in sorted_nodes:
		node = network.get_node_from_index(ind)
		headers = headers + ["i={:d}".format(node.index)] + ["DISR"]
		headers += _dict_to_header_list(node.state_vars[0].inbound_order, "IO")
		headers += _dict_to_header_list(node.state_vars[0].inbound_order_pipeline, "IOPL")
		headers += _dict_to_header_list(node.state_vars[0].order_quantity, "OQ")
		headers += _dict_to_header_list(node.state_vars[0].on_order_by_predecessor, "OO")
		headers += _dict_to_header_list(node.state_vars[0].inbound_shipment, "IS")
		headers += _dict_to_header_list(node.state_vars[0].inbound_shipment_pipeline, "ISPL")
		headers += _dict_to_header_list(node.state_vars[0].raw_material_inventory, "RM")
		headers += _dict_to_header_list(node.state_vars[0].outbound_shipment, "OS")
		headers += ["DMFS", "FR", "IL"]
		headers += _dict_to_header_list(node.state_vars[0].backorders_by_successor, "BO")
		headers += _dict_to_header_list(node.state_vars[0].disrupted_items_by_successor , "DI")
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

	