"""Code for simulating multi-echelon inventory systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the ``SupplyChainNetwork`` and the ``SupplyChainNode``s
that it contains, which contains all of the data for the simulation instance.

The following parameters are used to specify input data:
	* Node-level attributes
		- local_holding_cost [h'] TODO: allow echelon h.c.
		- stockout_cost [p]
		- lead_time [L] TODO: create "alias" shipment_lead_time
		- order_lead_time
		- demand_type
		- demand_mean [mu]
		- demand_standard_deviation [sigma]
		- demands [d]
		- demand_probabilities
		- demand_lo
		- demand_hi
		- inventory_policy
	* Edge-level attributes
		(None.)

The following attributes are used to store outputs and intermediate values:
	* Graph-level attributes
		- total_cost
	* Node-level attributes:
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

from inventory.datatypes import *
from inventory.supply_chain_network import *
from inventory.supply_chain_node import *
from inventory.sim_io import *
from inventory.helpers import *
from tests.instances_ssm_serial import *


# -------------------

# HELPER FUNCTIONS

def generate_demand(node, period=None, round=False):
	"""Generate demand for node in period, based on node's DemandType.

	Parameters
	----------
	node : SupplyChainNode
		NetworkX node representing the node to generate demand for.
	period : int
		Time period. Required if ``node.demand_type`` = ``DETERMINISTIC``;
		ignored otherwise.
	round : bool, optional
		Round the demand to nearest integer?

	Returns
	-------
	demand : float
		Demand for the node in the period.

	"""

	# TODO: use factory method pattern

	if node.demand_type == DemandType.NONE:
		demand = None
	elif node.demand_type == DemandType.NORMAL:
		demand = np.random.normal(node.demand_mean, node.demand_standard_deviation)
	elif node.demand_type == DemandType.UNIFORM_DISCRETE:
		demand = np.random.randint(node.demand_lo, node.demand_hi + 1)
	elif node.demand_type == DemandType.UNIFORM_CONTINUOUS:
		demand = np.random.uniform(node.demand_lo, node.demand_hi)
	elif node.demand_type == DemandType.DETERMINISTIC:
		# Get demand for period mod (# periods in demands list), i.e.,
		# if we are past the end of the demands list, loop back to the beginning.
		demand = node.demands[period % len(node.demands)]
	elif node.demand_type == DemandType.DISCRETE_EXPLICIT:
		demand = np.random.choice(node.demands, p=node.demand_probabilities)
	else:
		raise ValueError('Valid demand_type not provided')

	if round:
		demand = np.round(demand)

	return demand


# def get_order_quantity(node_index, network, period):
# 	"""Determine order quantity based on policy type and values of state variables.
#
# 	Parameters
# 	----------
# 	node_index
# 	network
# 	period
#
# 	Returns
# 	-------
#
# 	"""
# 	pass


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
	if node.demand_type != DemandType.NONE:
		# Generate demand and fill it in inbound_order.
		node.inbound_order[None][period] = generate_demand(node, period, round=True)

	# Call generate_downstream_orders() for all non-visited successors.
	for s in node.successors:
		if not visited[s.index]:
			generate_downstream_orders(s.index, network, period, visited)

	# Calculate total demand (inbound orders), including successor nodes and
	# external demand.
	demand = node.get_attribute_total('inbound_order', period)

	# Calculate order quantity. # TODO: handle policies
	if node.inventory_policy is None:
		order_quantity = 0
	else:
		IP = node.get_attribute_total("inventory_level", period) + \
			node.get_attribute_total("on_order", period) - demand
		order_quantity = node.inventory_policy.get_order_quantity(inventory_position=IP)
	node.order_quantity[period] = order_quantity

	# Get lead times (for convenience).
	order_lead_time = node.order_lead_time
	shipment_lead_time = node.shipment_lead_time

	# Place orders to all predecessors.
	if node.supply_type != SupplyType.NONE:
		predecessors = node.predecessors + [None]
	else:
		predecessors = node.predecessors
	for p in predecessors:
		if p is not None:
			p.inbound_order[node_index][period+order_lead_time] = \
				order_quantity
			p_index = p.index
		else:
			p_index = None
		node.on_order[p_index][period+1] = \
			node.on_order[p_index][period] + order_quantity

	# Does node have external supply?
	if node.supply_type != SupplyType.NONE:
		# Place order to external supplier.
		# (For now, this just means setting inbound shipment in the future.)
		# TODO: Handle other types of supply functions
		node.inbound_shipment[None][period+order_lead_time+shipment_lead_time] = \
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
	IS = node.get_attribute_total('inbound_shipment', period)
	IO = node.get_attribute_total('inbound_order', period)
	if node.supply_type != SupplyType.NONE:
		predecessor_indices = node.predecessor_indices + [None]
	else:
		predecessor_indices = node.predecessor_indices
	if node.demand_type != DemandType.NONE:
		successor_indices = node.successor_indices + [None]
	else:
		successor_indices = node.successor_indices

	# Receive inbound shipment (add it to ending IL); will subtract outbound
	# shipment later. Subtract arriving shipment from next period's starting OO.
	# TODO: handle what happens when multiple supply nodes (assembly-type)
	node.ending_inventory_level[period] = node.inventory_level[period] + IS
	for p_index in predecessor_indices:
		node.on_order[p_index][period+1] -= node.inbound_shipment[p_index][period]

	# Determine current on-hand and backorders (after shipment arrives but
	# before demand is subtracted).
	current_on_hand = max(0, node.inventory_level[period]) + IS
	current_backorders = max(0, -node.inventory_level[period])
	# Double-check BO calculations.
	current_backorders_check = node.get_attribute_total('backorders', period)
	assert np.isclose(current_backorders, current_backorders_check), \
		"current_backorders = {:} <> current_backorders_check = {:}, node = {:d}, period = {:d}".format(current_backorders, current_backorders_check, node_index, period)

	# Determine outbound shipments. (Satisfy demand in order of successor node
	# index.) Also update EIL and BO, and calculate demand met from stock.
	# TODO: allow different allocation policies
	node.demand_met_from_stock[period] = 0.0
	for s_index in successor_indices:
		# Outbound shipment to s = min{OH, BO for s + new order from s}.
		node.outbound_shipment[s_index][period] = \
			min(current_on_hand, node.backorders[s_index][period] +
				node.inbound_order[s_index][period])

		# How much of outbound shipment was used to clear backorders?
		# (Assumes backorders are cleared before satisfying current period's
		# demands.)
		BO_OS = min(node.outbound_shipment[s_index][period],
					node.backorders[s_index][period])
		non_BO_OS = node.outbound_shipment[s_index][period] - BO_OS

		# Calculate demand met from stock. (Note: This assumes that if there
		# are backorders, they get priority over current period's demands.)
		# TODO: handle successor-level DMFS and FR.
		node.demand_met_from_stock[period] = \
			max(0, node.outbound_shipment[s_index][period]
				- node.backorders[s_index][period])
		# Update EIL and BO.
		node.ending_inventory_level[period] -= node.inbound_order[s_index][period]
		node.backorders[s_index][period] -= BO_OS

		# Calculate new backorders.
		node.backorders[s_index][period] += max(0,
			node.inbound_order[s_index][period] - non_BO_OS)
#			node.inbound_order[s_index][period] - node.outbound_shipment[s_index][period])

	# node['OS'][period] = min(current_on_hand, current_backorders + IO)
	#
	# # Determine number of current period's demands (inbound orders) that are
	# # met from stock. (Note: This assumes that if there are backorders, current
	# # period's demands get priority.)
	# node['DMFS'][period] = min(current_on_hand, IO)

	# Calculate fill rate (cumulative in periods 0,...,t).
	met_from_stock = np.sum(node.demand_met_from_stock[0:period+1])
	total_demand = np.sum([node.get_attribute_total('inbound_order', t)
						for t in range(period+1)])
	if total_demand > 0:
		node.fill_rate[period] = met_from_stock / total_demand
	else:
		node.fill_rate[period] = 1.0

	# Propagate shipment downstream (i.e., update IS).
	for s in node.successors:
		s.inbound_shipment[node_index][period+s.shipment_lead_time] \
			= node.outbound_shipment[s.index][period]

	# Subtract demand from ending inventory and calculate costs.
	# TODO: add more flexible ways of calculating in-transit h.c.
	node.holding_cost_incurred[period] = \
		node.local_holding_cost * max(0, node.ending_inventory_level[period])
	node.stockout_cost_incurred[period] = \
		node.stockout_cost * max(0, -node.ending_inventory_level[period])
	node.in_transit_holding_cost_incurred[period] = \
		node.local_holding_cost * np.sum([s.inbound_shipment[node_index][period+1+t]
			for s in node.successors for t in range(s.shipment_lead_time)])

	node.total_cost_incurred[period] = \
		node.holding_cost_incurred[period] + \
		node.stockout_cost_incurred[period] + \
		node.in_transit_holding_cost_incurred[period]

	# Set next period's starting IL and BO.
	node.inventory_level[period+1] = node.ending_inventory_level[period]
	for s_index in successor_indices:
		node.backorders[s_index][period+1] = node.backorders[s_index][period]

	# Call generate_downstream_shipments() for all non-visited successors.
	for s in list(node.successors):
		if not visited[s.index]:
			generate_downstream_shipments(s.index, network, period, visited)


# -------------------

# SIMULATION

def simulation(network, num_periods, rand_seed=None):
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

	Returns
	-------
	float
		Total cost over all nodes and periods.
	"""

	# TODO: check for directed loops
	# TODO: simulation seems to get slower as iterations progress -- why? (test T = 10000)

	# CONSTANTS

	# Number of extra periods to allow for calculations past the last period.
	extra_periods = np.max([n.order_lead_time for n in network.nodes]) \
					+ np.max([n.shipment_lead_time for n in network.nodes]) + 2

	# INITIALIZATION

	# Initialize state and decision variables at each node.

	# NOTE: Some variables are indexed up to num_periods+EXTRA_PERIODS; the
	# additional slots are to allow calculations past the last period.

	# Build lists of predecessor and successor indices, including external
	# supply and demand, if any.
	# TODO: build this feature into the node object.
	predecessor_indices = {}
	successor_indices = {}
	for n in network.nodes:
		if n.supply_type != SupplyType.NONE:
			predecessor_indices[n] = n.predecessor_indices + [None]
		else:
			predecessor_indices[n] = n.predecessor_indices
		if n.demand_type != DemandType.NONE:
			successor_indices[n] = n.successor_indices + [None]
		else:
			successor_indices[n] = n.successor_indices

	for n in network.nodes:

		# State variables.
		n.inbound_shipment = {p_index: np.zeros(num_periods+extra_periods)
							  for p_index in predecessor_indices[n]}
		n.inbound_order = {s_index: np.zeros(num_periods+extra_periods)
						   for s_index in successor_indices[n]}
		n.outbound_shipment = {s_index: np.zeros(num_periods)
							   for s_index in successor_indices[n]}
		n.on_order = {p_index: np.zeros(num_periods+extra_periods)
					  for p_index in predecessor_indices[n]}
		n.inventory_level = np.zeros(num_periods+extra_periods)
		n.backorders = {s_index: np.zeros(num_periods+extra_periods)
						for s_index in successor_indices[n]}
		n.ending_inventory_level = np.zeros(num_periods)

		# Costs.
		n.holding_cost_incurred = np.zeros(num_periods)
		n.stockout_cost_incurred = np.zeros(num_periods)
		n.in_transit_holding_cost_incurred = np.zeros(num_periods)
		n.total_cost_incurred = np.zeros(num_periods)

		# Fill rates.
		n.demand_met_from_stock = np.zeros(num_periods)
		n.fill_rate = np.zeros(num_periods)

		# Decision variables.
		n.order_quantity = np.zeros(num_periods)

	# Initialize random number generator.
	np.random.seed(rand_seed)

	# Initialize inventory levels and other quantities.
	for n in network.nodes:
		# Initialize inventory levels and backorders.
		# TODO: handle what happens if initial IL < 0 (or prohibit it)
		if n.initial_inventory_level is not None:
			n.inventory_level[0] = n.initial_inventory_level
		else:
			n.inventory_level[0] = 0.0

		# Initialize inbound order quantities for all successors of n,
		# and update their on-order quantities.
		for s in n.successors:
			for t in range(n.order_lead_time):
				s.inbound_order[n.index][t] = n.initial_orders
				s.on_order[n.index][0] += s.inbound_order[n.index][t]

		# Initialize inbound shipment quantities from all predecessors of n,
		# and update on-order quantity at n.
		for p_index in predecessor_indices[n]:
			for t in range(n.shipment_lead_time):
				n.inbound_shipment[p_index][t] = n.initial_shipments or 0
				n.on_order[p_index][0] += n.inbound_shipment[p_index][t]

	# MAIN LOOP

	for t in tqdm(range(num_periods)):

		#print(t)

		# GENERATE DEMANDS AND ORDERS

		# Build list of nodes with no predecessors. (These will be the starting
		# nodes for the dfs.)
		no_pred = [n for n in network.nodes if n.predecessors == []]

		# Initialize visited dict.
		visited = {n.index: False for n in network.nodes}

		# Generate demands and place orders. Use depth-first search, starting
		# at nodes with no predecessors, and propagating orders upstream.
		for n in no_pred:
			generate_downstream_orders(n.index, network, t, visited)

		# GENERATE SHIPMENTS

		# Reset visited dict.
		visited	= {n.index: False for n in network.nodes}

		# Generate shipments. Use depth-first search, starting at nodes with
		# no predecessors, and propagating shipments downstream.
		for n in no_pred:
			generate_downstream_shipments(n.index, network, t, visited)

	# Return total cost.
	return np.sum([n.total_cost_incurred[t] for n in network.nodes
			for t in range(num_periods)])


def run_multiple_trials(network, num_trials, num_periods):
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

	# Run trials.
	for t in range(num_trials):
		total_cost = simulation(network, num_periods, rand_seed=None)
		average_costs.append(total_cost / num_periods)

	# Calculate mean and SEM of average cost.
	mean_cost = np.mean(average_costs)
	sem_cost = stats.sem(average_costs, ddof=0)

	return mean_cost, sem_cost


def main():
	T = 1000

	# Example 6.1
	serial_3 = serial_system(3, local_holding_cost=[7, 4, 2],
							 stockout_cost=[37.12, 0, 0],
							 demand_type=DemandType.NORMAL,
							 demand_mean=5,
							 demand_standard_deviation=1,
							 shipment_lead_time=[1, 1, 2],
							 inventory_policy_type=InventoryPolicyType.BASE_STOCK,
							 local_base_stock_levels=[6.49, 5.53, 10.69],
							 downstream_0=True)
#	total_cost = simulation(serial_3, T, rand_seed=None)
#	write_results(serial_3, T, total_cost, num_periods_to_print=50, write_csv=False)
	mean_cost, sem_cost = run_multiple_trials(serial_3, 10, T)
	print("mean = {:} SEM = {:}".format(mean_cost, sem_cost))

# 	# Problem 6.16
# 	serial_2 = serial_system(2, local_holding_cost=[7, 2],
# 							 stockout_cost=[24, 0],
# 							 demand_type=DemandType.NORMAL,
# 							 demand_mean=20,
# 							 demand_standard_deviation=4,
# 							 shipment_lead_time=[8, 3],
# 							 inventory_policy_type=InventoryPolicyType.BASE_STOCK,
# 							 local_base_stock_levels=[170, 60],
# #							 local_base_stock_levels=[171.1912, 57.7257],
# 							 initial_IL=20,
# 							 initial_orders=20,
# 							 initial_shipments=20,
# 							 downstream_0=True)
# 	total_cost = simulation(serial_2, T, rand_seed=None)
# 	write_results(serial_2, T, total_cost, num_periods_to_print=50, write_csv=False)

# 	serial_2_temp = serial_system(2, local_holding_cost=[1, 1],
# 							 stockout_cost=[10, 0],
# 							 demand_type=DemandType.NORMAL,
# 							 demand_mean=20,
# 							 demand_standard_deviation=1,
# #							 demand_type=DemandType.DETERMINISTIC,
# #							 demands=20,
# 							 shipment_lead_time=[2, 2],
# 							 inventory_policy_type=InventoryPolicyType.BASE_STOCK,
# 							 local_base_stock_levels=[60, 30],
# 							 initial_IL=20,
# 							 initial_orders=20,
# 							 initial_shipments=20,
# 							 downstream_0=True)
# 	total_cost = simulation(serial_2_temp, T, rand_seed=15)
# 	write_results(serial_2_temp, T, total_cost, num_periods_to_print=50, write_csv=False)





if __name__ == "__main__":
	main()
