"""
.. include:: ../../globals.inc

Overview 
--------

Code for simulating multi-echelon inventory systems.

.. note:: |node_stage|

The primary data object is the |class_network| and the |class_node| objects
that it contains, which contains all of the data for the simulation instance.

API Reference
-------------


"""

import numpy as np
from scipy import stats
from tqdm import tqdm				# progress bar
import warnings
import datetime

#from stockpyl.datatypes import *
#from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import NodeStateVars
from stockpyl.sim_io import write_instance_and_states
from stockpyl import helpers
#from tests.instances_ssm_serial import *
from stockpyl.instances import load_instance


# -------------------

# GLOBAL VARIABLES

# Did we already issue a warning about backorder mismatches?
issued_backorder_warning = False


# -------------------

# SIMULATION

def simulation(network, num_periods, rand_seed=None, progress_bar=True, consistency_checks='warn'):
	"""Perform the simulation for ``num_periods`` periods. Fills performance
	measures directly into ``network``.

	If ``initial_inventory_level`` is ``None`` for any node, its initial inventory level is set
	to its base-stock level (or similar for other inventory policy types).

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	num_periods : int
		Number of periods to simulate.
	rand_seed : int, optional
		Random number generator seed.
	progress_bar : bool, optional
		Display a progress bar?
	consistency_checks : str, optional
		String indicating whether to run consistency checks (backorder calculations) and what to do
		if check fails. Currently supported strings are:

		* 'N': No consistency checks
		* 'W': Issue warning if check fails but do not dump instance and simulation data to file (default)
		* 'WF': Issue warning if check fails and dump instance and simulation data to file
		* 'E': Raise exception if check fails but do not dump instance and simulation data to file
		* 'EF': Raise exception if check fails and dump instance and simulation data to file

	Returns
	-------
	float
		Total cost over all nodes and periods.

	Raises
	------
	ValueError
		If network contains a directed cycle.
	"""

	# CONSTANTS

	# Number of extra periods to allow for calculations past the last period.
	extra_periods = int(round(np.max([n.order_lead_time or 0 for n in network.nodes]) \
					+ np.max([n.shipment_lead_time or 0 for n in network.nodes]))) + 2

	# INITIALIZATION

	# Check that the network doesn't contain a directed cycle.
	if network.has_directed_cycle():
		raise ValueError("network may not contain a directed cycle")

	# Initialize state and decision variables at each node.

	# NOTE: State variables are indexed up to num_periods+extra_periods; the
	# additional slots are to allow calculations past the last period.

	for n in network.nodes:

		# Initialize state variable objects for state-variable history list.
		n.state_vars = [NodeStateVars(n, t) for t in range(num_periods+extra_periods)]

	# Initialize random number generator.
	np.random.seed(rand_seed)

	# Initialize progress bar. (If not requested, then this will disable it.)
	pbar = tqdm(total=num_periods, disable=not progress_bar)

	# Initialize state variables.
	_initialize_state_vars(network)

	# MAIN LOOP

	for t in range(num_periods):

		# Update period counter for network.
		network.period = t

		# Update progress bar.
		pbar.update()

		# UPDATE DISRUPTION STATES

		_update_disruption_states(network, t)

		# GENERATE DEMANDS AND ORDERS

		# Initialize visited dict.
		visited = {n.index: False for n in network.nodes}

		# Generate demand_list and place orders. Use depth-first search, starting
		# at nodes with no successors, and propagating orders upstream.
		for n in network.source_nodes:
			_generate_downstream_orders(n.index, network, t, visited)

		# GENERATE SHIPMENTS

		# Reset visited dict.
		visited = {n.index: False for n in network.nodes}

		# Generate shipments. Use depth-first search, starting at nodes with
		# no predecessors, and propagating shipments downstream.
		for n in network.source_nodes:
			_generate_downstream_shipments(n.index, network, t, visited, consistency_checks=consistency_checks)

		# UPDATE COSTS, PIPELINES, ETC.

		# Set initial values for period t+1 state variables.
		_initialize_next_period_state_vars(network, t)

		# Calculate costs.
		_calculate_period_costs(network, t)

	# Close progress bar.
	pbar.close()

	# Return total cost.
	return np.sum([n.state_vars[t].total_cost_incurred for n in network.nodes
			for t in range(num_periods)])


# -------------------

# HELPER FUNCTIONS

def _update_disruption_states(network, period):
	"""Update disruption states for all nodes in network.
	Record disruption states in ``state_vars``.

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		Time period.
	"""

	for n in network.nodes:
		# Is there a disruption process object at this node?
		if n.disruption_process is not None:
			n.disruption_process.update_disruption_state(period)

		# Record disruption state in state_vars.
		n.state_vars_current.disrupted = n.disrupted


def _generate_downstream_orders(node_index, network, period, visited):
	"""Generate demands and orders for all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	If node is currently disrupted and disruption type = 'OP' (order-pausing), order quantity
	is forced to 0.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		Time period.
	visited : dict
		Dictionary indicating whether each node in network has already been
		visited by the depth-first search.

	"""
	# Did we already visit this node?
	if visited[node_index]:
		# We shouldn't even be here.
		return

	# Mark node as visited.
	visited[node_index] = True

	# Get the node.
	node = network.get_node_from_index(node_index)

	# Does node have external demand?
	if node.demand_source is not None and node.demand_source.type is not None:
		# Generate demand and fill it in inbound_order_pipeline.
		node.state_vars_current.inbound_order_pipeline[None][0] = \
			node.demand_source.generate_demand(period)

	# Call generate_downstream_orders() for all non-visited successors.
	for s in node.successors():
		if not visited[s.index]:
			_generate_downstream_orders(s.index, network, period, visited)

	# Receive inbound orders.
	_receive_inbound_orders(node)

	# Get lead times (for convenience).
	order_lead_time = node.order_lead_time or 0
	shipment_lead_time = node.shipment_lead_time or 0

	# Place orders to all predecessors.
	for p in node.predecessors(include_external=True):
		if p is not None:
			# Is there an order-pausing disruption?
			if node.disrupted and node.disruption_process.disruption_type == 'OP':
				order_quantity = 0
			else:
				# Calculate order quantity.
				order_quantity = node.inventory_policy.get_order_quantity(predecessor_index=p.index)
			# Place order in predecessor's order pipeline.
			p.state_vars_current.inbound_order_pipeline[node_index][order_lead_time] = \
				order_quantity
			p_index = p.index
		else:
			# Is there an order-pausing disruption?
			if node.disrupted and node.disruption_process.disruption_type == 'OP':
				order_quantity = 0
			else:
				# Calculate order quantity.
				order_quantity = node.inventory_policy.get_order_quantity(predecessor_index=None)
			# Place order to external supplier.
			# (For now, this just means adding to inbound shipment pipeline.)
			node.state_vars_current.inbound_shipment_pipeline[None][order_lead_time + shipment_lead_time] += \
				order_quantity
			p_index = None

		# Record order quantity.
		node.state_vars_current.order_quantity[p_index] = order_quantity
		# Add order to on_order_by_predecessor.
		node.state_vars_current.on_order_by_predecessor[p_index] += order_quantity


def _generate_downstream_shipments(node_index, network, period, visited, consistency_checks='W'):
	"""Generate shipments to all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	If downstream node is currently disrupted and its disruption type = 'SP' (shipment-pausing),
	no items are shipped to that node. Those items are placed in disrupted-items inventory. 
	They are not included in either the node's IL or its BOs, but they are charged a holding
	cost as though they were included in IL.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		Time period.
	visited : dict
		Dictionary indicating whether each node in network has already been
		visited by the depth-first search.
	consistency_checks : str, optional
		String indicating whether to run consistency checks (backorder calculations) and what to do
		if check fails. For currently supported strings, see docstring for simulation().

	"""
	# Did we already visit this node?
	if visited[node_index]:
		# We shouldn't even be here.
		return

	# Mark node as visited.
	visited[node_index] = True

	# Shortcuts.
	node = network.get_node_from_index(node_index)

	# Remember starting IL.
	starting_inventory_level = node.state_vars_current.inventory_level

	# Receive inbound shipments. (Set inbound_shipment, remove from shipment
	# pipeline, update OO.)
	_receive_inbound_shipments(node)

	# Convert raw materials to finished goods.
	new_finished_goods = _raw_materials_to_finished_goods(node)

	# Process outbound shipments.
	_process_outbound_shipments(node, starting_inventory_level, new_finished_goods, consistency_checks=consistency_checks)

	# Calculate fill rate (cumulative in periods 0,...,t).
	_calculate_fill_rate(node, period)

	# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
	_propagate_shipment_downstream(node)

	# Call generate_downstream_shipments() for all non-visited successors.
	for s in list(node.successors()):
		if not visited[s.index]:
			_generate_downstream_shipments(s.index, network, period, visited, consistency_checks=consistency_checks)


def _initialize_state_vars(network):
	"""Initialize the state variables for each node:

		* inventory_level = to initial_inventory_level (or base-stock level, etc., if initial_inventory_level is None)
		* inbound_shipment_pipeline = initial_shipments
		* on_order = initial_shipments * shipment_lead_time + initial_orders * order_lead_time
		* inbound_order_pipeline = initial_orders

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	"""

	# Initialize inventory levels and other quantities.
	for n in network.nodes:
		# Initialize inventory_level to initial_inventory_level (or to BS level, etc., if None).
		if n.initial_inventory_level is not None:
			init_IL = n.initial_inventory_level
		else:
			init_IL = n.inventory_policy.get_order_quantity(inventory_position=0)
		n.state_vars[0].inventory_level = init_IL

		# Initialize inbound shipment pipeline and on-order quantities.
		for p_index in n.predecessor_indices(include_external=True):
			for l in range(n.shipment_lead_time or 0):
				n.state_vars[0].inbound_shipment_pipeline[p_index][l] = n.initial_shipments or 0
			n.state_vars[0].on_order_by_predecessor[p_index] = \
				(n.initial_shipments or 0) * (n.shipment_lead_time or 0) + (n.initial_orders or 0) * (n.order_lead_time or 0)

		# Initialize inbound order pipeline. (Exclude external demand.)
		for s in n.successors():
			for l in range(s.order_lead_time or 0):
				n.state_vars[0].inbound_order_pipeline[s.index][l] = s.initial_orders or 0

		# Initialize raw material inventory.
		for p in n.predecessor_indices(include_external=True):
			n.state_vars[0].raw_material_inventory[p_index] = 0


def _receive_inbound_orders(node):
	"""Receive inbound orders:

		* Set inbound order from pipeline.
		* Remove inbound order from pipeline.
		* Update cumulative demand.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	"""
	for s_index in node.successor_indices(include_external=True):
		# Set inbound_order from pipeline.
		node.state_vars_current.inbound_order[s_index] = \
			node.state_vars_current.inbound_order_pipeline[s_index][0]
		# Remove order from pipeline.
		node.state_vars_current.inbound_order_pipeline[s_index][0] = 0
		# Update demand_cumul.
		node.state_vars_current.demand_cumul += node.state_vars_current.inbound_order[s_index]


def _initialize_next_period_state_vars(network, period):
	"""Set initial values for state variables in period ``period`` + 1.

		* Update shipment and order pipelines by "advancing" them by 1 period \
		and adding a 0 in the last element.
		* Set IL, BO, RM, and OO next period = ending values this period.
		* Set _cumul attributes = ending values this period.
		* Do nothing for ``disrupted``; this is set in update_disruption_states().

	If node is currently disrupted and its disruption type = 'TP' (transit-pausing),
	items in its shipment pipelines are not advanced. 

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		The current time period.
	"""

	for n in network.nodes:
		# Update pipelines.
		for p in n.predecessor_indices(include_external=True):
			# Is there a transit-pausing disruption?
			if n.disrupted and n.disruption_process.disruption_type == 'TP':
				# Yes; items in shipment pipeline stay where they are.
				n.state_vars[period+1].inbound_shipment_pipeline[p] = \
					n.state_vars[period].inbound_shipment_pipeline[p]
			else:
				# No; items in shipment pipeline advance by 1 slot.
				# Copy items from slot 0 in period t to t+1. (Normally, this will equal 0, but it can 
				# be non-zero if there was a type-RP disruption.)
				n.state_vars[period+1].inbound_shipment_pipeline[p][0] = \
					n.state_vars[period].inbound_shipment_pipeline[p][0]
				# Add items from slot s+1 in period t to slot s in period t+1.
				for s in range(len(n.state_vars[period].inbound_shipment_pipeline[p])-1):
					n.state_vars[period+1].inbound_shipment_pipeline[p][s] += \
						n.state_vars[period].inbound_shipment_pipeline[p][s+1]

				# n.state_vars[period+1].inbound_shipment_pipeline[p] = \
				# 	n.state_vars[period].inbound_shipment_pipeline[p][1:] + [0]
		for s in n.successor_indices(include_external=True):
			n.state_vars[period+1].inbound_order_pipeline[s] = \
				n.state_vars[period].inbound_order_pipeline[s][1:] + [0]

		# Set next period's starting IL, BO, RM, and OO.
		n.state_vars[period+1].inventory_level = n.state_vars[period].inventory_level
		for s_index in n.successor_indices(include_external=True):
			n.state_vars[period+1].backorders_by_successor[s_index] = \
				n.state_vars[period].backorders_by_successor[s_index]
		for s_index in n.successor_indices(include_external=False):
			n.state_vars[period+1].disrupted_items_by_successor[s_index] = \
				n.state_vars[period].disrupted_items_by_successor[s_index]
		for p_index in n.predecessor_indices(include_external=True):
			n.state_vars[period+1].on_order_by_predecessor[p_index] = \
				n.state_vars[period].on_order_by_predecessor[p_index]
			n.state_vars[period+1].raw_material_inventory[p_index] = \
				n.state_vars[period].raw_material_inventory[p_index]

		# Set demand_met_from_stock_cumul and demand_cumul.
		n.state_vars[period+1].demand_met_from_stock_cumul = \
			n.state_vars[period].demand_met_from_stock_cumul
		n.state_vars[period+1].demand_cumul = \
			n.state_vars[period].demand_cumul


def _calculate_period_costs(network, period):
	"""Calculate costs and revenues for one period.

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		The time period.
	"""

	for n in network.nodes:
		# Finished goods holding cost.
		items_held = max(0, n.state_vars[period].inventory_level) + n._get_attribute_total('disrupted_items_by_successor', period)
		try:
			n.state_vars[period].holding_cost_incurred = n.local_holding_cost_function(items_held)
		except TypeError:
			n.state_vars[period].holding_cost_incurred = (n.local_holding_cost or 0) * items_held
		# Raw materials holding cost.
		for p in n.predecessors(include_external=False):
			n.state_vars[period].holding_cost_incurred += \
				(p.local_holding_cost or 0) * n.state_vars[period].raw_material_inventory[p.index]
		# Stockout cost.
		try:
			n.state_vars[period].stockout_cost_incurred = \
				n.stockout_cost_function(n.state_vars[period].inventory_level)
		except TypeError:
			n.state_vars[period].stockout_cost_incurred = \
				(n.stockout_cost or 0) * max(0, -n.state_vars[period].inventory_level)
		# In-transit holding cost.
		if n.in_transit_holding_cost is None:
			h = n.local_holding_cost or 0
		else:
			h = n.in_transit_holding_cost or 0
		n.state_vars[period].in_transit_holding_cost_incurred = \
			h * np.sum([n.state_vars[period].in_transit_to(s) for s in n.successors()])
		# Revenue.
		n.state_vars[period].revenue_earned = (n.revenue or 0) * \
			np.sum([n.state_vars[period].outbound_shipment[s_index] \
					for s_index in n.successor_indices(include_external=True)])

		# Total cost.
		n.state_vars[period].total_cost_incurred = \
			n.state_vars[period].holding_cost_incurred + \
			n.state_vars[period].stockout_cost_incurred + \
			n.state_vars[period].in_transit_holding_cost_incurred - \
			n.state_vars[period].revenue_earned


def _receive_inbound_shipments(node):
	"""Receive inbound shipment for the node:

		* Set inbound_shipment.
		* Remove from shipment pipeline and add to raw material inventory.
		* Process as many units as possible.
		* Update IL and OO.

	If node is currently disrupted and disruption type = 'RP' (receipt-pausing), quantity received
	is forced to 0.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	"""
	# Loop through predecessors.
	for p_index in node.predecessor_indices(include_external=True):
		# Is there a receipt-pausing disruption?
		if node.disrupted and node.disruption_process.disruption_type == 'RP':
			inbound_shipment = 0
		else:
			# Determine inbound shipment amount from p.
			inbound_shipment = node.state_vars_current.inbound_shipment_pipeline[p_index][0]
		# Set inbound_shipment attribute.
		node.state_vars_current.inbound_shipment[p_index] = inbound_shipment
		# Remove shipment from pipeline.
		node.state_vars_current.inbound_shipment_pipeline[p_index][0] -= inbound_shipment
		# Add shipment to raw material inventory.
		node.state_vars_current.raw_material_inventory[p_index] += inbound_shipment
		# Update on-order inventory.
		node.state_vars_current.on_order_by_predecessor[p_index] -= inbound_shipment


def _raw_materials_to_finished_goods(node):
	"""Process raw materials to convert them to finished goods:

		* Remove items from raw material inventory.
		* Update IL.

	Parameters
	----------
	node : |class_node|
		The supply chain node.

	Returns
	-------
	new_finished_goods : float
		Number of new finished goods added to inventory this period.

	"""
	# Determine number of units that can be processed.
	new_finished_goods = np.min([node.state_vars_current.raw_material_inventory[p_index]
						for p_index in node.predecessor_indices(include_external=True)])

	# Process units: remove from raw material inventory and add to finished goods.
	for p_index in node.predecessor_indices(include_external=True):
		node.state_vars_current.raw_material_inventory[p_index] -= new_finished_goods
	node.state_vars_current.inventory_level += new_finished_goods

	return new_finished_goods


def _process_outbound_shipments(node, starting_inventory_level, new_finished_goods, consistency_checks='W'):
	"""Process outbound shipments for the node:

		* Determine outbound shipments. Demands are satisfied in order of \
		successor node index.
		* Update inventory level.
		* Calculate demand met from stock.

	If downstream node is currently disrupted and its disruption type = 'SP' (shipment-pausing),
	no items are shipped to that node. Those items are placed in disrupted-items inventory. 
	They are not included in either the node's IL or its BOs, but they are charged a holding
	cost as though they were included in IL.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	starting_inventory_level : float
		Starting inventory level for the period.
	new_finished_goods : float
		Number of new finished goods added to inventory this period.
	consistency_checks : str, optional
		String indicating whether to run consistency checks (backorder calculations) and what to do
		if check fails. For currently supported strings, see docstring for simulation().
	"""
	# Determine current on-hand and backorders (after new finished goods are
	# added but before demand is subtracted).
	current_on_hand = max(0.0, starting_inventory_level) + new_finished_goods
	current_backorders = max(0.0, -starting_inventory_level)

	global issued_backorder_warning
	if consistency_checks in ('W', 'WF', 'E', 'EF') and not issued_backorder_warning:
		# Double-check BO calculations.
		current_backorders_check = node._get_attribute_total('backorders_by_successor', node.network.period) 
		if not np.isclose(current_backorders, current_backorders_check):
			if consistency_checks in ('WF', 'EF'):
				# Write instance and simulation data to file.
				filename = 'failed_instance_' + str(datetime.datetime.now())
				filepath = 'aux_files/'+filename+'.json'
				write_instance_and_states(
					network=node.network, 
					filepath=filepath,
					instance_name='failed_instance'
				)
			# Issue warning.
			# See https://stackoverflow.com/q/287871/3453768 for terminal text color.
			if consistency_checks in ('W', 'WF'):
				textcolor = '\033[93m'
			else:
				textcolor = '\033[91m'
			warning_msg = f"\n{textcolor}Backorder check failed! current_backorders = {current_backorders} <> current_backorders_check = {current_backorders_check}, node = {node.index}, period = {node.network.period}.\n"
			if consistency_checks in ('WF', 'EF'):
				warning_msg += f"The instance and simulation data have been written to {filepath}.\n"
			warning_msg += f"Please post an issue at https://github.com/LarrySnyder/stockpyl/issues or contact the developer directly.\n"
			if consistency_checks in ('W', 'WF'):
				warning_msg += f"Simulation will proceed, but results may be incorrect."
			warning_msg += "\x1b[0m" # reset color
			if consistency_checks in ('W', 'WF'):
				warnings.warn(warning_msg)
				issued_backorder_warning = True
			if consistency_checks in ('E', 'EF'):
				raise ValueError(warning_msg)
			# warnings.warn(f"Backorder check failed! current_backorders = {current_backorders} <> current_backorders_check = {current_backorders_check}, node = {node.index}, period = {node.network.period}.")
			# warnings.warn(f"The instance and simulation data have been written to {filepath}.")
			# warnings.warn(f"Please post an issue at https://github.com/LarrySnyder/stockpyl/issues or contact the developer directly.")
			# warnings.warn(f"Include the text of this error message as well as the file referenced above.")
			# warnings.warn(f"Simulation will proceed, but results may be incorrect.")

	# 		# print(f"{textcolor}Backorder check failed! current_backorders = {current_backorders} <> current_backorders_check = {current_backorders_check}, node = {node.index}, period = {node.network.period}.")
	# 		# print(f"{textcolor}The instance and simulation data have been written to {filepath}.")
	# 		# print(f"{textcolor}Please post an issue at https://github.com/LarrySnyder/stockpyl/issues or contact the developer directly.")
	# 		# print(f"{textcolor}Include the text of this error message as well as the file referenced above.")
	# 		# raise ValueError()

	# Determine outbound shipments. (Satisfy demand in order of successor node
	# index.) Also update EIL and BO, and calculate demand met from stock.
	node.state_vars_current.demand_met_from_stock = 0.0
	for s in node.successors(include_external=True):
#	for s_index in node.successor_indices(include_external=True):
		# Get successor index (for convenience).
		s_index = None if s is None else s.index

		# Determine number of items that will ship out to s (if there is no disruption), not including
		# disrupted items waiting to ship. = min{OH, BO for s + new order from s} 
		ready_to_ship = min(current_on_hand, node.state_vars_current.backorders_by_successor[s_index] +
			node.state_vars_current.inbound_order[s_index])

		# Is there a shipment-pausing disruption at s?
		if s is not None and s.disrupted and s.disruption_process.disruption_type == 'SP':
			# Yes: Don't ship anything out.
			OS = 0
			# New disrupted items = the items that would have been shipped out, if there were no disruption.
			DI = ready_to_ship
			# Decompose DI into new demands that are now disrupted items and previously backordered items 
			# that are now disrupted items. Assumes backorders are handled first, then new demands.
			BO_to_DI = min(ready_to_ship, node.state_vars_current.backorders_by_successor[s_index])
			ND_to_DI = DI - BO_to_DI
		else:
			# No: Outbound shipment to s = ready_to_ship + DI for s.
			OS = ready_to_ship + node.state_vars_current.disrupted_items_by_successor[s_index]
			# No new disrupted items.
			DI = 0
			BO_to_DI = 0
			ND_to_DI = 0

		# How much of outbound shipment was used for previously disrupted items and to clear backorders?
		# (Assumes disrupted items are cleared first, then backorders, before satisfying current period's
		# demands.)
		DI_OS = min(OS, node.state_vars_current.disrupted_items_by_successor[s_index])
		BO_OS = min(OS - DI_OS, node.state_vars_current.backorders_by_successor[s_index])
		non_BO_DI_OS = OS - BO_OS - DI_OS

		# Update outbound_shipment and current_on_hand. (Outbound items that were previously disrupted
		# do not get subtracted from current_on_hand because they were not included in it to begin with.)
		node.state_vars_current.outbound_shipment[s_index] = OS
		current_on_hand -= (OS - DI_OS + DI)

		# Calculate demand met from stock. (Note: This assumes that if there
		# are backorders, they get priority over current period's demand_list.)
		DMFS = max(0, OS - node.state_vars_current.backorders_by_successor[s_index])
		node.state_vars_current.demand_met_from_stock += DMFS
		node.state_vars_current.demand_met_from_stock_cumul += DMFS
		
		# Update IL and BO.
		node.state_vars_current.inventory_level -= node.state_vars_current.inbound_order[s_index]

		# Calculate new backorders_by_successor.
		node.state_vars_current.backorders_by_successor[s_index] -= (BO_OS + BO_to_DI)
		node.state_vars_current.backorders_by_successor[s_index] += max(0,
			node.state_vars_current.inbound_order[s_index] - ND_to_DI - non_BO_DI_OS)

		# Update disrupted_items.
		if s is not None:
			node.state_vars_current.disrupted_items_by_successor[s_index] += DI - DI_OS


def _calculate_fill_rate(node, period):
	"""Calculate fill rate for the node in the period.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	period : int
		Time period.

	"""
	# Calculate fill rate (cumulative in periods 0,...,t).
	met_from_stock = node.state_vars[period].demand_met_from_stock_cumul
	total_demand = node.state_vars[period].demand_cumul
	# met_from_stock = np.sum([node.state_vars[t].demand_met_from_stock for t in range(period + 1)])
	# total_demand = np.sum([node._get_attribute_total('inbound_order', t)
	# 					   for t in range(period + 1)])

	if total_demand > 0:
		node.state_vars_current.fill_rate = met_from_stock / total_demand
	else:
		node.state_vars_current.fill_rate = 1.0


def _propagate_shipment_downstream(node):
	"""Propagate shipment downstream, i.e., add it to successors' ``inbound_shipment_pipeline``.

	Parameters
	----------
	node : |class_node|
		The supply chain node.

	Returns
	-------
	inbound_shipment : float
		The inbound shipment quantity.

	"""
	# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
	# (Normally inbound_shipment_pipeline[node.index][s.shipment_lead_time] should equal 0,
	# unless there is a type-TP disruption, in which case outbound shipments
	# successor wait in slot s.shipment_lead_time until the disruption ends.)
	for s in node.successors():
		s.state_vars_current.inbound_shipment_pipeline[node.index][s.shipment_lead_time or 0] \
			+= node.state_vars_current.outbound_shipment[s.index]


# -------------------

# SIMULATION STUFF

def run_multiple_trials(network, num_trials, num_periods, rand_seed=None, progress_bar=True):
	"""Run ``num_trials`` trials of the simulation, each with  ``num_periods``
	periods. Return mean and SEM of average cost.

	(To build alpha-confidence interval, use
	``mean_cost`` +/- z_{1-alpha/2} * ``sem_cost``.)

	Note: After trials, ``network`` will contain performance measures for the
	most recent trial.

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	num_trials : int
		Number of trials to simulate.
	num_periods : int
		Number of periods to simulate.
	rand_seed : int, optional
		Random number generator seed.
	progress_bar : bool, optional
		Display a progress bar?

	Returns
	-------
	mean_cost : float
		Mean of average costs across all trials.
	sem_cost : float
		Standard error of average costs across all trials.
	"""

	# Initialize list of average costs.
	average_costs = []

	# Initialize progress bar. (If not requested, then this will disable it.)
	pbar = tqdm(total=num_trials, disable=not progress_bar)

	# Initialize random number generator seed. The idea for now is to initialize
	# it with rand_seed (which is possibly None); then, for each trial, initialize it by generating a
	# randint. This is because calling np.random.seed(None) is very slow
	# (it was the bottleneck of the simulation when running multiple trials)
	# so I'm generating seeds pseudo-randomly. Not sure this is the best approach.
	np.random.seed(rand_seed)

	# Run trials.
	for t in range(num_trials):
		# Update progress bar.
		pbar.update()

		total_cost = simulation(network, num_periods, rand_seed=np.random.randint(1, 10000), progress_bar=False)
		average_costs.append(total_cost / num_periods)

	# Close progress bar.
	pbar.close()

	# Calculate mean and SEM of average cost.
	mean_cost = np.mean(average_costs)
	sem_cost = stats.sem(average_costs, ddof=0)

	return mean_cost, sem_cost


