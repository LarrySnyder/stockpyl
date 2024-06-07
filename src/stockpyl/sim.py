"""
.. include:: ../../globals.inc

Overview
--------

The |mod_sim| module contains code for simulating multi-echelon inventory systems.
The primary data object is the |class_network| object and the |class_node| and |class_product| objects
that it contains. These objects contain all of the data for the simulation instance.


.. note:: |node_stage|

.. seealso::

	For an overview of simulation in |sp|,
	see the :ref:`tutorial page for simulation<tutorial_sim_page>` and
	the :ref:`tutorial page for multi-product simulation<tutorial_multiproduct_sim_page>`.


API Reference
-------------


"""

import numpy as np
from scipy import stats
from tqdm import tqdm  # progress bar
import warnings
import datetime
import copy

#from stockpyl.datatypes import *
#from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import NodeStateVars
from stockpyl.sim_io import write_instance_and_states
from stockpyl.helpers import BIG_FLOAT
#from tests.instances_ssm_serial import *
from stockpyl.instances import load_instance

# -------------------

# GLOBAL VARIABLES

# Did we already issue a warning about backorder mismatches?
issued_backorder_warning = False


# -------------------

# SIMULATION

def simulation(network, num_periods, rand_seed=None, progress_bar=True, consistency_checks='W'):
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

	# Initialize the simulation:
	# 	* Check validity of the network
	# 	* Initialize state and decision variables at each node
	# 	* Set the numpy PRNG seed
	#	* Set network.period to None
	# NOTE: State variables are indexed up to num_periods+extra_periods; the
	# additional slots are to allow calculations past the last period.
	initialize(network=network, num_periods=num_periods, rand_seed=rand_seed)

	# Initialize progress bar. (If not requested, then this will disable it.)
	pbar = tqdm(total=num_periods, disable=not progress_bar)

	# MAIN LOOP

	for _ in range(num_periods):
		# Update progress bar.
		pbar.update()

		# Execute one time period:
		# 	* Update disruption states
		# 	* Generate demands and orders
		# 	* Generate shipments
		# 	* Update costs, pipelines, etc.
		# 	* Increment ``network.period`` by 1
		step(network=network, consistency_checks=consistency_checks)

	# Close progress bar.
	pbar.close()

	# Close down simulation:
	# 	* Calculate the total cost over all nodes and periods.
	total_cost = close(network=network)

	# Return total cost.
	return total_cost


def initialize(network, num_periods, rand_seed=None):
	"""Initialize the simulation:

		* Check validity of the network
		* Initialize state and decision variables at each node
		* Set the numpy PRNG seed
		* Set network.period to None (will be set to 0 in first call to :func:`stockpyl.sim.step`)

	.. note:: Calling :func:`~stockpyl.sim.initialize` function, then :func:`stockpyl.sim.step` function once per
		period, then :func:`~stockpyl.sim.close` function is equivalent to calling
		:func:`~stockpyl.sim.simulate` function (aside from progress bar, which :func:`~stockpyl.sim.simulate`
		displays but the individual functions do not).

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	num_periods : int
		Number of periods to simulate.
	rand_seed : int, optional
		Random number generator seed.

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

	# Check that all nodes have inventory policies with node attribute set correctly.
	for node in network.nodes:
		for prod_ind in node.product_indices:
			policy = node.get_attribute('inventory_policy', product=prod_ind)
			if policy is None or policy.type is None:
				if prod_ind:
					err_str = f'The inventory_policy attribute for node {node.index} and product {prod_ind} is None. You must provide a Policy object in one or both objects in order for the simulation to set order quantities.'
				else:
					err_str = f'The inventory_policy attribute for node {node.index} is None. You must provide a Policy object in order for the simulation to set order quantities.'
				raise AttributeError(err_str)

	# Initialize state and decision variables at each node.

	# NOTE: State variables are indexed up to num_periods+extra_periods; the
	# additional slots are to allow calculations past the last period.

	for n in network.nodes:
		# Initialize state variable objects for state-variable history list.
		n.state_vars = [NodeStateVars(n, t) for t in range(num_periods + extra_periods)]

	# Initialize random number generator.
	np.random.seed(rand_seed)

	# Initialize state variables.
	_initialize_state_vars(network)

	# Set network.period to None (will be set to 0 in first call to step()).
	network.period = None


def step(network, order_quantity_override=None, consistency_checks='W'):
	"""Execute one time period of the simulation:

		* Increment ``network.period`` by 1
		* Update disruption states
		* Generate demands and orders
		* Generate shipments
		* Update costs, pipelines, etc.

	.. note:: Calling :func:`~stockpyl.sim.initialize` function, then :func:`stockpyl.sim.step` function once per
		period, then :func:`~stockpyl.sim.close` function is equivalent to calling
		:func:`~stockpyl.sim.simulate` function (aside from progress bar, which :func:`~stockpyl.sim.simulate`
		displays but the individual functions do not).

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	consistency_checks : str, optional
		String indicating whether to run consistency checks (backorder calculations) and what to do
		if check fails. See docstring for :func:`~stockpyl.sim.simulation` for list of currently supported strings.
	order_quantity_override : dict, optional
		Nested dictionary such that order_quantity_override[node][pred][rm] is an order quantity (or ``None``)
		for each node in the network, each predecessor, and each raw material the node orders from that predecessor
		(each specified by its index, not the object). 
		If provided, these order quantities will override the order quantities that would otherwise be calculated for
		the nodes/products. If the node has a single predecessor and raw material, ``pred`` and ``rm`` may be set to ``None`` and
		they will be determined automatically.
	 	If ``order_quantity_override`` is provided but its value is ``None`` for a given
		node, an order quantity will be calculated for that node as usual. (This option is mostly used
		when running the simulation from outside the package, e.g., in a reinforcement learning environment;
		it is analogous to setting the action for the current time period.)
	"""

	# Update period counter for network.
	if network.period is None:
		network.period = 0
	else:
		network.period += 1

	# Get shortcut to current period.
	t = network.period

	# UPDATE DISRUPTION STATES

	_update_disruption_states(network, t)

	# GENERATE DEMANDS AND ORDERS

	# Initialize visited dict.
	visited = {n.index: False for n in network.nodes}

	# Generate demands and place orders. Use depth-first search, starting
	# at nodes with no successors, and propagating orders upstream.
	for n in network.source_nodes:
		_generate_downstream_orders(n.index, network, t, visited, order_quantity_override=order_quantity_override)

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


def close(network):
	"""Close down the simulation:

		* Calculate and return the total cost over all nodes and periods.

	.. note:: Calling :func:`~stockpyl.sim.initialize` function, then :func:`stockpyl.sim.step` function once per
		period, then :func:`~stockpyl.sim.close` function is equivalent to calling
		:func:`~stockpyl.sim.simulate` function (aside from progress bar, which :func:`~stockpyl.sim.simulate`
		displays but the individual functions do not).

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.

	Returns
	-------
	float
		Total cost over all nodes and periods.
	"""

	# Return total cost.
	return float(np.sum([n.state_vars[t].total_cost_incurred for n in network.nodes
						 for t in range(len(n.state_vars))]))


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


def _generate_downstream_orders(node_index, network, period, visited, order_quantity_override=None):
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
	order_quantity_override : dict, optional
		Nested dictionary such that order_quantity_override[node][pred][rm] is an order quantity (or ``None``)
		for each node in the network, each predecessor, and each raw material the node orders from that predecessor
		(each specified by its index, not the object). 
		If provided, these order quantities will override the order quantities that would otherwise be calculated for
		the nodes/products. If the node has a single predecessor and raw material, ``pred`` and ``rm`` may be set to ``None`` and
		they will be determined automatically.
	 	If ``order_quantity_override`` is provided but its value is ``None`` for a given
		node, an order quantity will be calculated for that node as usual. (This option is mostly used
		when running the simulation from outside the package, e.g., in a reinforcement learning environment;
		it is analogous to setting the action for the current time period.)
	"""
	# Did we already visit this node?
	if visited[node_index]:
		# We shouldn't even be here.
		return

	# Mark node as visited.
	visited[node_index] = True

	# Get the node.
	node = network.nodes_by_index[node_index]

	# Loop through products (including dummy product).
	for prod_index in node.product_indices:
		# Does node/product have external demand?
		dem_src = node.get_attribute('demand_source', prod_index)
		if dem_src is not None and dem_src.type is not None:
			# Generate demand and fill it in inbound_order_pipeline.
			node.state_vars_current.inbound_order_pipeline[None][prod_index][0] = \
				dem_src.generate_demand(period)

	# Call generate_downstream_orders() for all non-visited successors.
	for s in node.successors():
		if not visited[s.index]:
			_generate_downstream_orders(s.index, network, period, visited,
										order_quantity_override=order_quantity_override)

	# Receive inbound orders.
	_receive_inbound_orders(node)

	# Loop through products at this node (possibly including dummy).
	for prod_ind in node.product_indices:
		
		# Get lead times and product index (for convenience).
		order_lead_time = node.get_attribute('order_lead_time', prod_ind) or 0
		shipment_lead_time = node.get_attribute('shipment_lead_time', prod_ind) or 0
		
		# Determine order quantity, in FG units.
		# Is there an order-pausing disruption?
		if node.disrupted and node.disruption_process.disruption_type == 'OP':
			# Do nothing.
			pass
		else:
			# Shortcut to the policy.
			policy = node.get_attribute('inventory_policy', product=prod_ind)

			# Determine node/product's order capacity.
			order_capac = node.get_attribute('order_capacity', product=prod_ind) or BIG_FLOAT

			# Get order quantities for all raw materials (expressed in units of RM).
			# Dict returned also contains an order quantity for the FG, which will be used
			# below to set pending_finished_goods.
			order_quantity_dict = policy.get_order_quantity(product=prod_ind, order_capacity=order_capac, include_raw_materials=True)

			# Update FG order quantity and pending finished goods. (Convert to downstream units.)
			node.state_vars_current.order_quantity_fg[prod_ind] += order_quantity_dict[None][None]
			node.state_vars_current.pending_finished_goods[prod_ind] += order_quantity_dict[None][None]

			# Place orders for all raw materials.
			for rm in node.raw_materials_by_product(product=prod_ind, network_BOM=True):
				rm_index = rm.index
				for p in node.raw_material_suppliers_by_raw_material(raw_material=rm_index, network_BOM=True):
					p_index = p.index if p is not None else None
					
					# Was an override order quantity provided?
					try:
						if None in order_quantity_override[node.index] and None in order_quantity_override[node.index][None]:
							qty_override = order_quantity_override[node.index][None][None]
						else:
							qty_override = order_quantity_override[node.index][p_index][rm_index]
					except:
						qty_override = None
					
					if qty_override is not None:   
						rm_OQ = qty_override
					else:
						rm_OQ = order_quantity_dict[p_index][rm_index]

					# Place order in predecessor's order pipeline (converting first to raw material units via BOM).
	 				# (Add to any existing inbound order, because multiple products at the node can order the same RM.)
					if p is not None:
						p.state_vars_current.inbound_order_pipeline[node_index][rm_index][order_lead_time] += rm_OQ
					else:
						# Place order to external supplier. (For now, this just means adding to inbound shipment pipeline.)
						node.state_vars_current.inbound_shipment_pipeline[None][rm_index][order_lead_time + shipment_lead_time] += rm_OQ

					# Record order quantity. (Add to existing order quantity, since multiple products might order the same RM from
					# the same predecessor.)
					node.state_vars_current.order_quantity[p_index][rm_index] += rm_OQ
					# Add order to on_order_by_predecessor.
					node.state_vars_current.on_order_by_predecessor[p_index][rm_index] += rm_OQ

		
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
	node = network.nodes_by_index[node_index]

	# Remember starting IL (as dict by product).
	starting_inventory_level = copy.deepcopy(node.state_vars_current.inventory_level)

	# Receive inbound shipments. (Set inbound_shipment, remove from shipment
	# pipeline, update OO.)
	_receive_inbound_shipments(node)

	# Convert raw materials to finished goods. (Returns dict by)
	new_finished_goods = _raw_materials_to_finished_goods(node)

	# Process outbound shipments.
	_process_outbound_shipments(node, starting_inventory_level, new_finished_goods,
								consistency_checks=consistency_checks)

	# Calculate fill rate (cumulative in periods 0,...,t).
	_calculate_fill_rate(node, period)

	# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
	_propagate_shipment_downstream(node)

	# Call generate_downstream_shipments() for all successors for which all predecessors
	# have now been processed.
	for s in node.successors():
		if all([visited[p_ind] for p_ind in s.predecessor_indices()]):
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

		# State variables indexed by product at this node.
		for prod_ind in n.product_indices:
			
			# Initialize inventory_level to initial_inventory_level (or to BS level, etc., if None).
			init_IL = n.get_attribute('initial_inventory_level', prod_ind)
			if init_IL is None:
				# Choose a supplier and RM to use when getting an order quantity to set the initial IL.
				init_IL = n.get_attribute('inventory_policy', prod_ind).get_order_quantity(product=prod_ind, include_raw_materials=False, inventory_position=0)
			n.state_vars[0].inventory_level[prod_ind] = init_IL

			# Initialize inbound order pipeline. (Exclude external demand.)
			for s in n.successors():
				for l in range(s.get_attribute('order_lead_time', prod_ind) or 0):
					n.state_vars[0].inbound_order_pipeline[s.index][prod_ind][l] = s.get_attribute('initial_orders', prod_ind) or 0

		# State variables indexed by product at predecessor nodes.
		for rm_index in n.raw_materials_by_product('all', return_indices=True, network_BOM=True):
			for p_index in n.raw_material_suppliers_by_raw_material(raw_material=rm_index, return_indices=True, network_BOM=True):
				
				# Initialize inbound shipment pipeline and on-order quantities.
				for l in range(n.shipment_lead_time or 0):
					n.state_vars[0].inbound_shipment_pipeline[p_index][rm_index][l] = n.get_attribute('initial_shipments', prod_ind) or 0
				n.state_vars[0].on_order_by_predecessor[p_index][rm_index] = \
					(n.get_attribute('initial_shipments', prod_ind) or 0) * (n.get_attribute('shipment_lead_time', prod_ind) or 0) \
						+ (n.get_attribute('initial_orders', prod_ind) or 0) * (n.get_attribute('order_lead_time', prod_ind) or 0)

				# Initialize raw material inventory.
				for rm_index in n.raw_materials_by_product(product='all', return_indices=True, network_BOM=True):
					n.state_vars[0].raw_material_inventory[rm_index] = 0   


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
	# Loop through successor nodes.
	for s in node.successors(include_external=True):
		# Shortcut to successor node index.
		s_index = s.index if s is not None else None

		# Loop through products at this node.
		for prod_index in node.product_indices:
			# Set inbound_order from pipeline.
			node.state_vars_current.inbound_order[s_index][prod_index] = \
				node.state_vars_current.inbound_order_pipeline[s_index][prod_index][0]
			# Remove order from pipeline.
			node.state_vars_current.inbound_order_pipeline[s_index][prod_index][0] = 0
			# Update demand_cumul.
			node.state_vars_current.demand_cumul[prod_index] += node.state_vars_current.inbound_order[s_index][prod_index]


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

	# Loop through nodes.
	for n in network.nodes:
		# Loop through predecessors.
		for p in n.predecessors(include_external=True):
			# Shortcut to predecessor index.
			p_index = p.index if p is not None else None
			# Loop through raw materials at predecessor.
			for rm_index in (p.product_indices if p is not None else [n._external_supplier_dummy_product.index]):

				if rm_index in n.raw_materials_by_product('all', return_indices=True, network_BOM=True) and \
					p in n.raw_material_suppliers_by_raw_material(rm_index, network_BOM=True):
			
					# Is there a transit-pausing disruption?
					if n.disrupted and n.disruption_process.disruption_type == 'TP':
						# Yes; items in shipment pipeline stay where they are.
						n.state_vars[period + 1].inbound_shipment_pipeline[p_index][rm_index] = \
							n.state_vars[period].inbound_shipment_pipeline[p_index][rm_index].copy()
					else:
						# No; items in shipment pipeline advance by 1 slot.
						# Copy items from slot 0 in period t to t+1. (Normally, this will equal 0, but it can
						# be non-zero if there was a type-RP disruption.)
						n.state_vars[period + 1].inbound_shipment_pipeline[p_index][rm_index][0] = \
							n.state_vars[period].inbound_shipment_pipeline[p_index][rm_index][0]
						# Add items from slot s+1 in period t to slot s in period t+1.
						for s in range(len(n.state_vars[period].inbound_shipment_pipeline[p_index][rm_index]) - 1):
							n.state_vars[period + 1].inbound_shipment_pipeline[p_index][rm_index][s] += \
								n.state_vars[period].inbound_shipment_pipeline[p_index][rm_index][s + 1]
				
		# Loop through successors.
		for s in n.successor_indices(include_external=True):
			# Loop through products at this node.
			for prod_index in n.product_indices:
				n.state_vars[period + 1].inbound_order_pipeline[s][prod_index] = \
					n.state_vars[period].inbound_order_pipeline[s][prod_index][1:] + [0]

		# Set next period's starting IL, BO, IDI, ODI, RM, PFG, and OO.
		# Loop through products at node.
		for prod_index in n.product_indices:
			n.state_vars[period + 1].inventory_level[prod_index] = n.state_vars[period].inventory_level[prod_index]
			n.state_vars[period + 1].pending_finished_goods[prod_index] = n.state_vars[period].pending_finished_goods[prod_index]
			# Loop through successors.
			for s_index in n.successor_indices(include_external=True):
				n.state_vars[period + 1].backorders_by_successor[s_index][prod_index] = \
					n.state_vars[period].backorders_by_successor[s_index][prod_index]
			for s_index in n.successor_indices(include_external=False):
				n.state_vars[period + 1].outbound_disrupted_items[s_index][prod_index] = \
					n.state_vars[period].outbound_disrupted_items[s_index][prod_index]
		# Loop through predecessors.
		for p in n.predecessors(include_external=True):
			p_index = p.index if p is not None else None
			# Loop through raw materials at predecessor.
			for rm_index in (p.product_indices if p is not None else [n._external_supplier_dummy_product.index]):
				if rm_index in n.raw_materials_by_product('all', return_indices=True, network_BOM=True) and \
					p in n.raw_material_suppliers_by_raw_material(rm_index, network_BOM=True):
					n.state_vars[period + 1].on_order_by_predecessor[p_index][rm_index] = \
						n.state_vars[period].on_order_by_predecessor[p_index][rm_index]
					n.state_vars[period + 1].raw_material_inventory[rm_index] = \
						n.state_vars[period].raw_material_inventory[rm_index]
					n.state_vars[period + 1].inbound_disrupted_items[p_index][rm_index] = \
						n.state_vars[period].inbound_disrupted_items[p_index][rm_index]

		# Set demand_met_from_stock_cumul and demand_cumul.
		for prod_index in n.product_indices:
			n.state_vars[period + 1].demand_met_from_stock_cumul[prod_index] = \
				n.state_vars[period].demand_met_from_stock_cumul[prod_index]
			n.state_vars[period + 1].demand_cumul[prod_index] = \
				n.state_vars[period].demand_cumul[prod_index]


def _calculate_period_costs(network, period):
	"""Calculate costs and revenues for one period and store them in n.state_vars[period].

	Parameters
	----------
	network : |class_network|
		The multi-echelon inventory network.
	period : int
		The time period.
	"""

	# Loop through nodes.
	for n in network.nodes:
		# Initialize costs.
		n.state_vars[period].holding_cost_incurred = 0
		n.state_vars[period].stockout_cost_incurred = 0
		n.state_vars[period].in_transit_holding_cost_incurred = 0
		n.state_vars[period].revenue_earned = 0
			
		# Loop through products at node.
		for prod_index in n.product_indices:
			# Finished goods holding cost.
			items_held = max(0, n.state_vars[period].inventory_level[prod_index]) + \
							n._get_state_var_total('outbound_disrupted_items', period, product=prod_index)
			try:
				n.state_vars[period].holding_cost_incurred += n.get_attribute('local_holding_cost_function', prod_index)(items_held)
			except TypeError:
				n.state_vars[period].holding_cost_incurred += (n.get_attribute('local_holding_cost', prod_index) or 0) * items_held
			# Raw materials holding cost. Includes only products that come from an actual predecessor node, not external supplier.
			for rm_index in n.raw_materials_by_product(product=prod_index, return_indices=True, network_BOM=True):
				# Determine suppliers for this raw material, excluding external supplier.
				preds = n.raw_material_suppliers_by_raw_material(raw_material=rm_index, network_BOM=True)
				preds = [p for p in preds if p is not None]
				if len(preds) > 0:
					# Choose first supplier of this raw material arbitrarily and use its holding cost. This is a workaround
					# for now, since there cam be multiple RM suppliers but there's no way to specify which supplier's
					# holding cost to use (or some other holding cost). See https://github.com/LarrySnyder/stockpyl/issues/140.
					p = preds[0]
					# Calculate raw material holding cost.
					n.state_vars[period].holding_cost_incurred += \
						(p.get_attribute('local_holding_cost', rm_index) or 0) * \
						(n.state_vars[period].raw_material_inventory[rm_index] \
							+ n.state_vars[period].inbound_disrupted_items[p.index][rm_index])
			# Stockout cost.
			try:
				n.state_vars[period].stockout_cost_incurred += \
					n.get_attribute('stockout_cost_function', prod_index)(n.state_vars[period].inventory_level[prod_index])
			except TypeError:
				n.state_vars[period].stockout_cost_incurred += \
					(n.get_attribute('stockout_cost', prod_index) or 0) * max(0, -n.state_vars[period].inventory_level[prod_index])
			# In-transit holding cost.
			if n.get_attribute('in_transit_holding_cost', prod_index) is None:
				h = n.get_attribute('local_holding_cost', prod_index) or 0
			else:
				h = n.get_attribute('in_transit_holding_cost', prod_index) or 0
			n.state_vars[period].in_transit_holding_cost_incurred += \
				h * float(np.sum([n.state_vars[period].in_transit_to(s, prod_index) \
					  for s in n.customers_by_product(product=prod_index, network_BOM=True) if s is not None]))
			# Revenue.
			n.state_vars[period].revenue_earned = (n.get_attribute('revenue', prod_index) or 0) * \
												float(np.sum([n.state_vars[period].outbound_shipment[s_index][prod_index] \
																for s_index in n.successor_indices(include_external=True)]))

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

	If node is currently disrupted and disruption type = 'RP' (receipt-pausing), inbound
	items are moved to inbound_disrupted_items.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	"""
	# Loop through predecessors.
	for p in node.predecessors(include_external=True):
		# Shortcut to predecessor index.
		p_index = p.index if p is not None else None

		# Loop through raw materials at predecessor.
		for rm_index in (p.product_indices if p is not None else [node._external_supplier_dummy_product.index]):
			if rm_index in node.raw_materials_by_product('all', return_indices=True, network_BOM=True) and \
				p in node.raw_material_suppliers_by_raw_material(rm_index, network_BOM=True):

				# Determine number of items that will be received from p (if there is no disruption),
				# not including inbound disrupted items waiting to be received.
				ready_to_receive = node.state_vars_current.inbound_shipment_pipeline[p_index][rm_index][0]

				# Is there a receipt-pausing disruption?
				if node.disrupted and node.disruption_process.disruption_type == 'RP':
					# Yes: Don't receive anything.
					IS = 0
					# Increase inbound disrupted items by the items that would have been received, if
					# there were no disruption.
					IDI = ready_to_receive
				else:
					# No: Inbound shipment from p = ready_to_receive + IDI from p.
					IS = ready_to_receive + node.state_vars_current.inbound_disrupted_items[p_index][rm_index]
					# Decrease inbound disrupted items by its whole amount. (This will zero out
					# inbound_disrupted_items below.)
					IDI = -node.state_vars_current.inbound_disrupted_items[p_index][rm_index]

				# Set inbound_shipment attribute.
				node.state_vars_current.inbound_shipment[p_index][rm_index] = IS
				# Remove shipment from pipeline.
				node.state_vars_current.inbound_shipment_pipeline[p_index][rm_index][0] = 0
				# Add shipment to raw material inventory.
				node.state_vars_current.raw_material_inventory[rm_index] += IS
				# Update on-order inventory.
				node.state_vars_current.on_order_by_predecessor[p_index][rm_index] -= ready_to_receive
				# Update inbound_disrupted_items.
				node.state_vars_current.inbound_disrupted_items[p_index][rm_index] += IDI


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
	new_finished_goods : dict
		Dict whose keys are indices of products at ``node`` and whose values are 
		the corresponding number of new finished goods added to inventory this period.

	"""

	# Shortcut to period.
	period = node.network.period

	# Allocate available raw materials to products in proportion to each product's share of
	# the order for that raw material that was placed LT periods ago.
	share = {}
	for rm_index in node.raw_materials_by_product(product='all', return_indices=True, network_BOM=True):

		# Shortcut to lead times. Note: This assumes that all products that use this RM have the
		# same lead times. Currently no way to distinguish among products if they have different lead times.
		prod = node.products_by_raw_material(rm_index)[0]
		OLT = node.get_attribute('order_lead_time', prod) or 0
		SLT = node.get_attribute('shipment_lead_time', prod) or 0

		# Determine number of units of this raw material available (in units of the RM).
		avail_rm = node.state_vars_current.raw_material_inventory[rm_index]

		# Shortcut to list of product indices for this RM.
		prods_for_rm = node.products_by_raw_material(rm_index, return_indices=True)

		# If avail_rm > 0, then we know period >= OLT + SLT.
		if avail_rm > 0:
			# Determine total order placed for this raw material LT periods ago.
			units_ordered = sum([node.state_vars[period - OLT - SLT].order_quantity[pred_index][rm_index]
									for pred_index in node.raw_material_suppliers_by_raw_material(rm_index, return_indices=True, network_BOM=True)])
			
			# If units_ordered == 0, allocate into equal shares. (This can happen if the original
			# order was backordered, or if there is initial RM at the start of the simulation.)
			if units_ordered == 0:
				share_frac = {prod_index: 1 / len(prods_for_rm) for prod_index in prods_for_rm}
			else:
				share_frac = {prod_index: node.state_vars[period - OLT - SLT].order_quantity_fg[prod_index] \
											* node.NBOM(product=prod_index, predecessor=None, raw_material=rm_index) \
											/ units_ordered for prod_index in prods_for_rm}
			
			# Determine each product's share of this raw material.
			share[rm_index] = {prod_index: avail_rm * share_frac[prod_index] for prod_index in prods_for_rm}
		else:
			share[rm_index] = {prod_index: 0 for prod_index in prods_for_rm}
		
		# If share doesn't sum to 1, allocate the remaining units to an arbitrary product.
		# (I don't think this should ever happen, except maybe because of rounding.)
		extra = avail_rm - sum([share[rm_index][prod_index] for prod_index in prods_for_rm])
		if extra > 0:
			share[rm_index][prods_for_rm[0]] + extra

	# Determine number of units of each product that can be processed.
	new_finished_goods = {}
	for prod_index in node.product_indices:
		# Determine number of FGunits that can be produced; it equals the min, over all
		# RMs for the product, of the product's share of that RM, expressed in FG units.
		avail_rm = {rm_index: share[rm_index][prod_index] / node.NBOM(product=prod_index, predecessor=None, raw_material=rm_index)
					for rm_index in node.raw_materials_by_product(prod_index, return_indices=True, network_BOM=True)}
		num_to_make = min(avail_rm.values())
	
		# Number of finished goods = min of min RM available and pending FG.
		new_finished_goods[prod_index] = num_to_make

		# Process units: remove from raw material and add to finished goods.
		for rm_index in node.raw_materials_by_product(prod_index, return_indices=True, network_BOM=True):
			node.state_vars_current.raw_material_inventory[rm_index] \
				-= num_to_make * node.NBOM(product=prod_index, predecessor=None, raw_material=rm_index)
		node.state_vars_current.inventory_level[prod_index] += num_to_make

		# Subtract units from pending_finished_goods.
		node.state_vars_current.pending_finished_goods[prod_index] -= num_to_make

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
	starting_inventory_level : dict
		Dict whose keys are indices of products at ``node`` and whose values are the corresponding
		starting inventory level for the period.
	new_finished_goods : dict
		Dict whose keys are indices of products at ``node`` and whose values are 
		the corresponding number of new finished goods added to inventory this period.
	consistency_checks : str, optional
		String indicating whether to run consistency checks (backorder calculations) and what to do
		if check fails. For currently supported strings, see docstring for simulation().
	"""

	# Loop through products at this node.
	for prod_index in node.product_indices:

		# Determine current on-hand and backorders (after new finished goods are
		# added but before demand is subtracted).
		current_on_hand = max(0.0, starting_inventory_level[prod_index]) + new_finished_goods[prod_index]
		current_backorders = max(0.0, -starting_inventory_level[prod_index])

		global issued_backorder_warning
		if consistency_checks in ('W', 'WF', 'E', 'EF') and not issued_backorder_warning:
			# Double-check BO calculations.
			current_backorders_check = node._get_state_var_total('backorders_by_successor', node.network.period, product=prod_index)
			if not np.isclose(current_backorders, current_backorders_check):
				if consistency_checks in ('WF', 'EF'):
					# Write instance and simulation data to file.
					filename = 'failed_instance_' + str(datetime.datetime.now())
					filepath = 'aux_files/' + filename + '.json'
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
				warning_msg += "\x1b[0m"  # reset color
				if consistency_checks in ('W', 'WF'):
					warnings.warn(warning_msg)
					issued_backorder_warning = True
				if consistency_checks in ('E', 'EF'):
					raise ValueError(warning_msg)

		# Determine outbound shipments. (Satisfy demand in order of successor node
		# index.) Also update EIL and BO, and calculate demand met from stock.
		node.state_vars_current.demand_met_from_stock[prod_index] = 0.0
		for s in node.successors(include_external=True):
			# Get successor index (for convenience).
			s_index = None if s is None else s.index

			# Determine number of items that will ship out to s (if there is no disruption), not including
			# disrupted items waiting to ship. = min{OH, BO for s + new order from s}
			ready_to_ship = min(current_on_hand, node.state_vars_current.backorders_by_successor[s_index][prod_index] +
								node.state_vars_current.inbound_order[s_index][prod_index])

			# Is there a shipment-pausing disruption at s?
			if s is not None and s.disrupted and s.disruption_process.disruption_type == 'SP':
				# Yes: Don't ship anything out.
				OS = 0
				# New outbound disrupted items = the items that would have been shipped out, if
				# there were no disruption.
				ODI = ready_to_ship
				# Decompose ODI into new demands that are now disrupted items and previously backordered items
				# that are now disrupted items. Assumes backorders are handled first, then new demands.
				BO_to_DI = min(ready_to_ship, node.state_vars_current.backorders_by_successor[s_index][prod_index])
				ND_to_DI = ODI - BO_to_DI
			else:
				# No: Outbound shipment to s = ready_to_ship + ODI for s.
				OS = ready_to_ship + node.state_vars_current.outbound_disrupted_items[s_index][prod_index]
				# No new disrupted items.
				ODI = 0
				BO_to_DI = 0
				ND_to_DI = 0

			# How much of outbound shipment was used for previously disrupted items and to clear backorders?
			# (Assumes disrupted items are cleared first, then backorders, before satisfying current period's
			# demands.)
			DI_OS = min(OS, node.state_vars_current.outbound_disrupted_items[s_index][prod_index])
			BO_OS = min(OS - DI_OS, node.state_vars_current.backorders_by_successor[s_index][prod_index])
			non_BO_DI_OS = OS - BO_OS - DI_OS

			# Update outbound_shipment and current_on_hand. (Outbound items that were previously disrupted
			# do not get subtracted from current_on_hand because they were not included in it to begin with.)
			node.state_vars_current.outbound_shipment[s_index][prod_index] = OS
			current_on_hand -= (OS - DI_OS + ODI)

			# Calculate demand met from stock. (Note: This assumes that if there
			# are backorders, they get priority over current period's demands.)
			DMFS = max(0, OS - node.state_vars_current.backorders_by_successor[s_index][prod_index])
			node.state_vars_current.demand_met_from_stock[prod_index] += DMFS
			node.state_vars_current.demand_met_from_stock_cumul[prod_index] += DMFS

			# Update IL and BO.
			node.state_vars_current.inventory_level[prod_index] -= node.state_vars_current.inbound_order[s_index][prod_index]

			# Calculate new backorders_by_successor.
			node.state_vars_current.backorders_by_successor[s_index][prod_index] -= (BO_OS + BO_to_DI)
			node.state_vars_current.backorders_by_successor[s_index][prod_index] \
				+= max(0, node.state_vars_current.inbound_order[s_index][prod_index] - ND_to_DI - non_BO_DI_OS)

			# Update disrupted_items.
			if s is not None:
				node.state_vars_current.outbound_disrupted_items[s_index][prod_index] += ODI - DI_OS


def _calculate_fill_rate(node, period):
	"""Calculate fill rate for the node in the period.

	Parameters
	----------
	node : |class_node|
		The supply chain node.
	period : int
		Time period.

	"""
	# Loop through products at this node.
	for prod_index in node.product_indices:
		# Calculate fill rate (cumulative in periods 0,...,t).
		met_from_stock = node.state_vars[period].demand_met_from_stock_cumul[prod_index]
		total_demand = node.state_vars[period].demand_cumul[prod_index]

		if total_demand > 0:
			node.state_vars_current.fill_rate[prod_index] = met_from_stock / total_demand
		else:
			node.state_vars_current.fill_rate[prod_index] = 1.0


def _propagate_shipment_downstream(node):
	"""Propagate shipment downstream, i.e., add it to successors' ``inbound_shipment_pipeline``.

	Parameters
	----------
	node : |class_node|
		The supply chain node.

	Returns
	-------
	inbound_shipment : dict
		Dict whose keys are indices of products at ``node`` and whose values are the corresponding
		starting inbound shipment quantity.
	"""
	# Loop through products at this node.
	for prod_index in node.product_indices:
		# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
		# (Normally inbound_shipment_pipeline[node.index][s.shipment_lead_time] should equal 0,
		# unless there is a type-TP disruption, in which case outbound shipments
		# successor wait in slot s.shipment_lead_time until the disruption ends.)
		for s in node.successors():
			if prod_index in s.raw_materials_by_product('all', return_indices=True, network_BOM=True) and \
				node in s.raw_material_suppliers_by_raw_material(prod_index, network_BOM=True):
				# Find a product at successor node that uses prod_index from node as a raw material,
				# and use its lead time. If there is more than one such product, use the last one found.
				for FG_index in s.product_indices:
					if prod_index in s.raw_materials_by_product(product=FG_index, return_indices=True, network_BOM=True) and \
						node.index in s.raw_material_suppliers_by_raw_material(raw_material=prod_index, return_indices=True, network_BOM=True):
						# Get lead time for this product.
						shipment_lead_time = (s.get_attribute('shipment_lead_time', product=FG_index) or 0)

				s.state_vars_current.inbound_shipment_pipeline[node.index][prod_index][shipment_lead_time] \
					+= node.state_vars_current.outbound_shipment[s.index][prod_index]


# -------------------

# SIMULATION STUFF

def run_multiple_trials(network, num_trials, num_periods, rand_seed=None, progress_bar=True):
	"""Run ``num_trials`` trials of the simulation, each with  ``num_periods``
	periods. Return mean and SEM of average cost per period across all trials.

	(To build :math:`\\alpha`-confidence interval, use
	``mean_cost`` :math:`\\pm z_{1-(1-\\alpha)/2} \\times` ``sem_cost``.)

	Note: After trials, ``network`` will contain state variables for the
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
		Mean of average cost per period across all trials.
	sem_cost : float
		Standard error of average cost per period across all trials.
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
	mean_cost = float(np.mean(average_costs))
	sem_cost = float(stats.sem(average_costs, ddof=0))

	return mean_cost, sem_cost
