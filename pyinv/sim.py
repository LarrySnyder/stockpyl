"""Code for simulating multi-echelon inventory systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the ``SupplyChainNetwork`` and the ``SupplyChainNode``s
that it contains, which contains all of the data for the simulation instance.

The following parameters are used to specify input data:
	* Node-level parameters
		- local_holding_cost [h'] TODO: allow echelon h.c.
		- stockout_cost [p]
		- lead_time [L] TODO: create "alias" shipment_lead_time
		- order_lead_time
		- demand_source
		- inventory_policy
	* Edge-level parameters
		(None.)

The following attributes are used to store outputs and intermediate values:
	* Graph-level parameters
		- total_cost
	* Node-level parameters
		- IS
		- IO
		- OS
		- OO
		- IL
		- BO
		- EIL
		- HC
		- SC
		- ITHC
		- TC
		- DMFS
		- FR
		- OQ

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
import math
from scipy import stats
from tqdm import tqdm				# progress bar
import cProfile

from pyinv.datatypes import *
from pyinv.supply_chain_network import *
from pyinv.supply_chain_node import *
from pyinv.sim_io import *
from pyinv.helpers import *
#from tests.instances_ssm_serial import *
from pyinv.instances import *


# -------------------

# SIMULATION

def simulation(network, num_periods, rand_seed=None, progress_bar=True):
	"""Perform the simulation for ``num_periods`` periods. Fills performance
	measures directly into ``network``.

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	num_periods : int
		Number of periods to simulate.
	rand_seed : int, optional
		Random number generator seed.
	progress_bar : bool, optional
		Display a progress bar?

	Returns
	-------
	float
		Total cost over all nodes and periods.
	"""

	# TODO: check for directed loops
	# TODO: simulation seems to get slower as iterations progress -- why? (test T = 10000)

	# CONSTANTS

	# Number of extra periods to allow for calculations past the last period.
	extra_periods = int(round(np.max([n.order_lead_time for n in network.nodes]) \
					+ np.max([n.shipment_lead_time for n in network.nodes]))) + 2

	# INITIALIZATION

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
	initialize_state_vars(network)

	# MAIN LOOP

	for t in range(num_periods):

		# Update period counter for network.
		network.period = t

		# Update progress bar.
		pbar.update()

		# GENERATE DEMANDS AND ORDERS

		# Initialize visited dict.
		visited = {n.index: False for n in network.nodes}

		# Generate demands and place orders. Use depth-first search, starting
		# at nodes with no predecessors, and propagating orders upstream.
		for n in network.source_nodes:
			generate_downstream_orders(n.index, network, t, visited)

		# GENERATE SHIPMENTS

		# Reset visited dict.
		visited = {n.index: False for n in network.nodes}

		# Generate shipments. Use depth-first search, starting at nodes with
		# no predecessors, and propagating shipments downstream.
		for n in network.source_nodes:
			generate_downstream_shipments(n.index, network, t, visited)

		# UPDATE COSTS, PIPELINES, ETC.

		# Set initial values for period t+1 state variables.
		initialize_next_period_state_vars(network, t)

		# Calculate costs.
		calculate_period_costs(network, t)

	# Close progress bar.
	pbar.close()

	# Return total cost.
	return np.sum([n.state_vars[t].total_cost_incurred for n in network.nodes
			for t in range(num_periods)])


# -------------------

# HELPER FUNCTIONS

def generate_downstream_orders(node_index, network, period, visited):
	"""Generate demands and orders for all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : SupplyChainNetwork
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
	if node.demand_source.type != DemandType.NONE:
		# Generate demand and fill it in inbound_order_pipeline.
		node.state_vars_current.inbound_order_pipeline[None][0] = \
			node.demand_source.generate_demand(period)

	# Call generate_downstream_orders() for all non-visited successors.
	for s in node.successors():
		if not visited[s.index]:
			generate_downstream_orders(s.index, network, period, visited)

	# Receive inbound orders.
	for s_index in node.successor_indices(include_external=True):
		# Set inbound_order from pipeline.
		node.state_vars_current.inbound_order[s_index] = \
			node.state_vars_current.inbound_order_pipeline[s_index][0]
		# Remove order from pipeline.
		node.state_vars_current.inbound_order_pipeline[s_index][0] = 0

	# Calculate order quantity.
	order_quantity = get_order_quantity(node, period)
	node.state_vars_current.order_quantity = order_quantity

	# Get lead times (for convenience).
	order_lead_time = node.order_lead_time
	shipment_lead_time = node.shipment_lead_time

	# Place orders to all predecessors.
	for p in node.predecessors(include_external=True):
		if p is not None:
			p.state_vars_current.inbound_order_pipeline[node_index][order_lead_time] = \
				order_quantity
			p_index = p.index
		else:
			p_index = None
		node.state_vars_current.on_order_by_predecessor[p_index] += order_quantity
		# node.state_vars[period + 1].on_order_by_predecessor[p_index] = \
		# 	node.state_vars[period].on_order_by_predecessor[p_index] + order_quantity

	# Does node have external supply?
	if node.supply_type != SupplyType.NONE:
		# Place order to external supplier.
		# (For now, this just means adding to inbound shipment pipeline.)
		# TODO: Handle other types of supply functions
		node.state_vars_current.inbound_shipment_pipeline[None][order_lead_time+shipment_lead_time] = \
			order_quantity


def generate_downstream_shipments(node_index, network, period, visited):
	"""Generate shipments to all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : SupplyChainNetwork
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

	# Shortcuts.
	node = network.get_node_from_index(node_index)

	# Remember starting IL.
	starting_inventory_level = node.state_vars_current.inventory_level

	# Receive inbound shipments. (Set inbound_shipment, remove from shipment
	# pipeline, update IL and OO.)
	inbound_shipment = receive_inbound_shipment(node)

	# Process outbound shipments.
	process_outbound_shipments(node, starting_inventory_level, inbound_shipment)

	# Calculate fill rate (cumulative in periods 0,...,t).
	calculate_fill_rate(node, period)

	# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
	propagate_shipment_downstream(node)

	# Call generate_downstream_shipments() for all non-visited successors.
	for s in list(node.successors()):
		if not visited[s.index]:
			generate_downstream_shipments(s.index, network, period, visited)


def initialize_state_vars(network):
	"""Initialize the state variables for each node:
		* inventory_level = to initial_inventory_level
		* inbound_shipment_pipeline = initial_shipments
		* on_order = initial_shipments * shipment_lead_time + initial_orders * order_lead_time
		* inbound_order_pipeline = initial_orders

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	"""

	# Initialize inventory levels and other quantities.
	for n in network.nodes:
		# Initialize inventory_level to initial_inventory_level (or 0 if None).
		# TODO: handle what happens if initial IL < 0 (or prohibit it)
		n.state_vars[0].inventory_level = n.initial_inventory_level or 0

		# Initialize inbound shipment pipeline and on-order quantities.
		# TODO: allow different initial shipment/order quantities for different pred/succ.
		for p_index in n.predecessor_indices(include_external=True):
			for l in range(n.shipment_lead_time):
				n.state_vars[0].inbound_shipment_pipeline[p_index][l] = n.initial_shipments
			n.state_vars[0].on_order_by_predecessor[p_index] = \
				n.initial_shipments * n.shipment_lead_time + n.initial_orders * n.order_lead_time

		# Initialize inbound order pipeline. (Exclude external demand.)
		for s in n.successors():
			for l in range(s.order_lead_time):
				n.state_vars[0].inbound_order_pipeline[l] = s.initial_orders


def initialize_next_period_state_vars(network, period):
	"""Set initial values for state variables in period ``period``+1.
		* Update shipment and order pipelines by "advancing" them by 1 period
	and adding a 0 in the last element.
		* Set IL, BO, and OO next period = ending values this period.

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	period : int
		The current time period.
	"""

	for n in network.nodes:
		# Update pipelines.
		for p in n.predecessor_indices(include_external=True):
			n.state_vars[period+1].inbound_shipment_pipeline[p] = \
				n.state_vars[period].inbound_shipment_pipeline[p][1:] + [0]
		for s in n.successor_indices(include_external=True):
			n.state_vars[period+1].inbound_order_pipeline[s] = \
				n.state_vars[period].inbound_order_pipeline[s][1:] + [0]

		# Set next period's starting IL, BO, and OO.
		n.state_vars[period+1].inventory_level = n.state_vars[period].inventory_level
		for s_index in n.successor_indices(include_external=True):
			n.state_vars[period+1].backorders_by_successor[s_index] = \
				n.state_vars[period].backorders_by_successor[s_index]
		for p_index in n.predecessor_indices(include_external=True):
			n.state_vars[period+1].on_order_by_predecessor[p_index] = \
				n.state_vars[period].on_order_by_predecessor[p_index]


def calculate_period_costs(network, period):
	"""Calculate costs for one period.

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	period : int
		The time period.
	"""

	for n in network.nodes:
		try:
			n.state_vars[period].holding_cost_incurred = \
				n.local_holding_cost_function(n.state_vars[period].inventory_level)
		except TypeError:
			n.state_vars[period].holding_cost_incurred = \
				n.local_holding_cost * max(0, n.state_vars[period].inventory_level)
		try:
			n.state_vars[period].stockout_cost_incurred = \
				n.stockout_cost_function(n.state_vars[period].inventory_level)
		except TypeError:
			n.state_vars[period].stockout_cost_incurred = \
				n.stockout_cost * max(0, -n.state_vars[period].inventory_level)
		# TODO: add more flexible ways of calculating in-transit h.c.
		n.state_vars[period].in_transit_holding_cost_incurred = \
			n.local_holding_cost * np.sum([n.state_vars[period].in_transit_to(s) for s in n.successors()])

		n.state_vars[period].total_cost_incurred = \
			n.state_vars[period].holding_cost_incurred + \
			n.state_vars[period].stockout_cost_incurred + \
			n.state_vars[period].in_transit_holding_cost_incurred


def get_order_quantity(node, period):
	"""Calculate order quantity for the given node.

	Parameters
	----------
	node : SupplyChainNode
		The supply chain node.
	period : int
		Time period.

	Returns
	-------
	order_quantity : float
		The order quantity.

	"""
	# Calculate total demand (inbound orders), including successor nodes and
	# external demand.
	demand = node.get_attribute_total('inbound_order', period)

	if node.inventory_policy is None:
		order_quantity = 0
	elif node.inventory_policy.policy_type == InventoryPolicyType.ECHELON_BASE_STOCK:
		current_IP = node.state_vars_current.echelon_inventory_position - demand
		order_quantity = node.inventory_policy.get_order_quantity(echelon_inventory_position=current_IP)
	else:
		current_IP = node.state_vars_current.inventory_position - demand
		order_quantity = node.inventory_policy.get_order_quantity(inventory_position=current_IP)
	return order_quantity


def receive_inbound_shipment(node):
	"""Receive inbound shipment for the node:
		* Set inbound_shipment.
		* Remove from shipment pipeline.
		* Update IL and OO.

	Parameters
	----------
	node : SupplyChainNode
		The supply chain node.

	Returns
	-------
	inbound_shipment : float
		The inbound shipment quantity.

	"""
	# Receive inbound shipments (add it to IL). Subtract arriving shipment from
	# next period's starting OO.
	# TODO: handle what happens when AND-type supply nodes (assembly-type) -- now it assumes OR-type
	inbound_shipment = np.sum([node.state_vars_current.inbound_shipment_pipeline[
		p_index][0] for p_index in node.predecessor_indices(include_external=True)])
	for p_index in node.predecessor_indices(include_external=True):
		# Set inbound_shipments from pipeline.
		node.state_vars_current.inbound_shipment[p_index] = inbound_shipment
		# Remove shipment from pipeline.
		node.state_vars_current.inbound_shipment_pipeline[p_index][0] = 0
		# Update IL and OO.
		node.state_vars_current.inventory_level += inbound_shipment
		node.state_vars_current.on_order_by_predecessor[p_index] -= inbound_shipment

	return inbound_shipment


def process_outbound_shipments(node, starting_inventory_level, inbound_shipment):
	"""Process outbound shipments for the node:
		* Determine outbound shipments. Demands are satisfied in order of
		successor node index.
		* Update inventory level.
		* Calculate demand met from stock.

	Parameters
	----------
	node : SupplyChainNode
		The supply chain node.
	starting_inventory_level : float
		Starting inventory level for the period.
	inbound_shipment : float
		Inbound shipment for the period (already received).
	"""
	# Determine current on-hand and backorders (after shipment arrives but
	# before demand is subtracted).
	current_on_hand = max(0.0, starting_inventory_level) + inbound_shipment
	current_backorders = max(0.0, -starting_inventory_level)
	# Double-check BO calculations.
	current_backorders_check = node.get_attribute_total('backorders_by_successor', node.network.period)
	assert np.isclose(current_backorders, current_backorders_check), \
		"current_backorders = {:} <> current_backorders_check = {:}, node = {:d}, period = {:d}".format(
			current_backorders, current_backorders_check, node.index, node.network.period)

	# Determine outbound shipments. (Satisfy demand in order of successor node
	# index.) Also update EIL and BO, and calculate demand met from stock.
	# TODO: allow different allocation policies
	node.state_vars_current.demand_met_from_stock = 0.0
	for s_index in node.successor_indices(include_external=True):
		# Outbound shipment to s = min{OH, BO for s + new order from s}.
		node.state_vars_current.outbound_shipment[s_index] = \
			min(current_on_hand, node.state_vars_current.backorders_by_successor[s_index] +
				node.state_vars_current.inbound_order[s_index])

		# How much of outbound shipment was used to clear backorders?
		# (Assumes backorders are cleared before satisfying current period's
		# demands.)
		BO_OS = min(node.state_vars_current.outbound_shipment[s_index],
					node.state_vars_current.backorders_by_successor[s_index])
		non_BO_OS = node.state_vars_current.outbound_shipment[s_index] - BO_OS

		# Calculate demand met from stock. (Note: This assumes that if there
		# are backorders, they get priority over current period's demands.)
		# TODO: handle successor-level DMFS and FR.
		node.state_vars_current.demand_met_from_stock = \
			max(0, node.state_vars_current.outbound_shipment[s_index]
				- node.state_vars_current.backorders_by_successor[s_index])
		# Update IL and BO.
		node.state_vars_current.inventory_level -= node.state_vars_current.inbound_order[s_index]
		node.state_vars_current.backorders_by_successor[s_index] -= BO_OS

		# Calculate new backorders_by_successor.
		node.state_vars_current.backorders_by_successor[s_index] += max(0,
			node.state_vars_current.inbound_order[s_index] - non_BO_OS)


def calculate_fill_rate(node, period):
	"""Calculate fill rate for the node in the period.

	Parameters
	----------
	node : SupplyChainNode
		The supply chain node.
	period : int
		Time period.

	"""
	# Calculate fill rate (cumulative in periods 0,...,t).
	# TODO: is this where the time leak is??
	met_from_stock = np.sum([node.state_vars[t].demand_met_from_stock for t in range(period + 1)])
	total_demand = np.sum([node.get_attribute_total('inbound_order', t)
						   for t in range(period + 1)])
	if total_demand > 0:
		node.state_vars_current.fill_rate = met_from_stock / total_demand
	else:
		node.state_vars_current.fill_rate = 1.0


def propagate_shipment_downstream(node):
	"""Propagate shipment downstream, i.e., add it to successors' ``inbound_shipment_pipeline``.

	Parameters
	----------
	node : SupplyChainNode
		The supply chain node.

	Returns
	-------
	inbound_shipment : float
		The inbound shipment quantity.

	"""
	# Propagate shipment downstream (i.e., add to successors' inbound_shipment_pipeline).
	# TODO: handle end of horizon -- if period+s.shipment_lead_time > T
	for s in node.successors():
		s.state_vars_current.inbound_shipment_pipeline[node.index][s.shipment_lead_time] \
			= node.state_vars_current.outbound_shipment[s.index]


# -------------------

# SIMULATION STUFF

def run_multiple_trials(network, num_trials, num_periods, progress_bar=True):
	"""Run ``num_trials`` trials of the simulation, each with  ``num_periods``
	periods. Return mean and SEM of average cost.

	(To build alpha-confidence interval, use
	``mean_cost`` +/- z_{1-alpha/2} * ``sem_cost``.)

	Note: After trials, ``network`` will contain performance measures for the
	most recent trial.

	TODO: figure out how to handle randseed -- need to avoid setting it in simulation()

	Parameters
	----------
	network : SupplyChainNetwork
		The multi-echelon inventory network.
	num_trials : int
		Number of trials to simulate.
	num_periods : int
		Number of periods to simulate.

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
	pbar = tqdm(total=num_periods, disable=not progress_bar)

	# Initialize random number generator seed. The idea for now is to initialize
	# it with no seed; then, for each trial, initialize it by generating a
	# randint. This is because calling np.random.seed(None) is very slow
	# (it was the bottleneck of the simulation when running multiple trials)
	# so I'm generating seeds pseudo-randomly. Not sure this is the best approach.
	# TODO: figure this out

	# Run trials.
	for t in range(num_trials):
		# Update progress bar.
		pbar.update()

		total_cost = simulation(network, num_periods, rand_seed=np.random.randint(1, 1e5), progress_bar=False)
		average_costs.append(total_cost / num_periods)

	# Close progress bar.
	pbar.close()

	# Calculate mean and SEM of average cost.
	mean_cost = np.mean(average_costs)
	sem_cost = stats.sem(average_costs, ddof=0)

	return mean_cost, sem_cost


def main():
	T = 100

	network = get_named_instance("example_6_1")

	for i in network.nodes:
		i.initial_inventory_level = i.inventory_policy.base_stock_level

	# Set initial inventory levels to local BS levels (otherwise local and echelon policies
	# will differ in the first few periods).
#	for n in network.nodes:
#		n.initial_inventory_level = n.inventory_policy.base_stock_level

	# # Calculate echelon base-stock levels.
	# S_local = {n.index: n.inventory_policy.base_stock_level for n in network.nodes}
	# from pyinv.ssm_serial import local_to_echelon_base_stock_levels
	# S_echelon = local_to_echelon_base_stock_levels(network, S_local)
	#
	# # Create and fill echelon base-stock policies.
	# policy_factory = PolicyFactory()
	# for n in network.nodes:
	# 	n.inventory_policy = policy_factory.build_policy(InventoryPolicyType.ECHELON_BASE_STOCK,
	# 													 base_stock_level=S_echelon[n.index])

	# network = serial_system(
	# 	num_nodes=1,
	# 	demand_type=DemandType.NORMAL,
	# 	demand_mean=20,
	# 	demand_standard_deviation=4,
	# 	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	# 	local_base_stock_levels=[25],
	# 	shipment_lead_time=[1],
	# 	local_holding_cost=None,
	# 	stockout_cost=1,
	# 	initial_IL=60
	# )
	#
	# def holding_cost_function(x):
	# 	if x < 0:
	# 		return 0
	# 	elif x < 20 or x >= 80:
	# 		return 1.0 * x
	# 	else:
	# 		return 500.0
	#
	# network.nodes[0].holding_cost_function = holding_cost_function
	#
	#
	# mean_cost, sem_cost = run_multiple_trials(network, num_trials=1000, num_periods=3)
	# print("mean_cost = {}, sem_cost = {}".format(mean_cost, sem_cost))

	total_cost = simulation(network, T, rand_seed=17)
#	write_results(network, T, total_cost, write_csv=False)
	write_results(network, T, total_cost, write_csv=True, csv_filename='temp.csv')



if __name__ == "__main__":
#	cProfile.run('main()')
	main()