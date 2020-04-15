"""Code for simulating multi-echelon pyinv systems.

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the simulation instance.

The following attributes are used to specify input data:
	* Node-level attributes
		- local_holding_cost [h'] TODO: allow echelon h.c.
		- stockout_cost [p]
		- lead_time [L] TODO: create "alias" shipment_lead_time
		- order_lead_time
		- demand_type
		- demand_mean [mu]
		- demand_standard_deviation [sigma]
		- demands [d]
		- probabilities
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

from pyinv.datatypes import *
from pyinv.sim_io import *
from pyinv.helpers import *
from tests.instances_ssm_serial import *

# -------------------

# HELPER FUNCTIONS


def generate_demand(node, period=None):
	"""Generate demand for node in period, based on node's DemandType.

	Parameters
	----------
	node : node
		NetworkX node representing the node to generate demand for.
	period : int
		Time period. Required if demand_type = DETERMINISTIC; ignored otherwise.

	Returns
	-------
	demand : float
		Demand for the node in the period.

	"""

	if node['demand_type'] == DemandType.NONE:
		demand = None
	elif node['demand_type'] == DemandType.NORMAL:
		demand = np.random.normal(node['demand_mean'], node['demand_standard_deviation'])
	elif node['demand_type'] == DemandType.UNIFORM_DISCRETE:
		demand = np.random.randint(node['demand_lo'], node['demand_hi'] + 1)
	elif node['demand_type'] == DemandType.UNIFORM_CONTINUOUS:
		demand = np.random.uniform(node['demand_lo'], node['demand_hi'])
	elif node['demand_type'] == DemandType.DETERMINISTIC:
		# Get demand for period mod (# periods in demands list), i.e.,
		# if we are past the end of the demands list, loop back to the beginning.
		demand = node['demands'][period % len(node['demands'])]
	elif node['demand_type'] == DemandType.DISCRETE_EXPLICIT:
		demand = np.random.choice(node['demands'], p=node['probabilities'])
	else:
		raise ValueError('Valid demand_type not provided')

	return demand


def order_quantity(node_index, network, period):
	"""Determine order quantity based on policy type and values of state variables.

	Parameters
	----------
	node_index
	network
	period

	Returns
	-------

	"""


def generate_downstream_orders(node_index, network, period, visited):
	"""Generate demands and orders for all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : DiGraph
		NetworkX directed graph representing the multi-echelon pyinv network.
	period : int
		Time period.
	visited : dict
		Dictionary indicating whether each node in network has already been
		visted by the depth-first search.

	Returns
	-------

	"""
	# Did we already visit this node?
	if visited[node_index]:
		# We shouldn't even be here.
		return

	# Mark node as visited.
	visited[node_index] = True

	# Does node have external demand?
	if network.nodes[node_index]['demand_type'] != DemandType.NONE:
		# Generate demand and fill it in 'IO'.
		network.nodes[node_index]['IO'][None][period] = \
			generate_demand(network.nodes[node_index], period)

	# Call generate_downstream_orders() for all non-visited _successors.
	for s in list(network.successors(node_index)):
		if not visited[s]:
			generate_downstream_orders(s, network, period, visited)

	# Calculate order quantity. # TODO: handle policies
	order_quantity = np.sum([network.nodes[node_index]['IO'][s][period] for s in
							 list(network.successors(node_index))+[None]])
	network.nodes[node_index]['OQ'][period] = order_quantity

	# Get lead times (for convenience).
	order_LT = network.nodes[node_index]['order_lead_time']
	shipment_LT = network.nodes[node_index]['shipment_lead_time']

	# Place orders to all _predecessors.
	for p in list(network.predecessors(node_index)) + [None]:
		if p is not None:
			network.nodes[p]['IO'][node_index][period+order_LT] = order_quantity
		network.nodes[node_index]['OO'][p][period+1] = \
			network.nodes[node_index]['OO'][p][period] + order_quantity

	# Does node have external supply?
	if network.nodes[node_index]['supply_type'] != SupplyType.NONE:
		# Place order to external supplier.
		# (For now, this just means setting inbound shipment in the future.)
		# TODO: handle other types of supply functions
		network.nodes[node_index]['IS'][None][period+order_LT+shipment_LT] = \
			order_quantity


def generate_downstream_shipments(node_index, network, period, visited):
	"""Generate shipments to all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : DiGraph
		NetworkX directed graph representing the multi-echelon pyinv network.
	period : int
		Time period.
	visited : dict
		Dictionary indicating whether each node in network has already been
		visted by the depth-first search.

	Returns
	-------

	"""
	# Did we already visit this node?
	if visited[node_index]:
		# We shouldn't even be here.
		return

	# Mark node as visited.
	visited[node_index] = True

	# Shortcuts.
	node = network.nodes[node_index]
	IS = get_attribute_total(node_index, network, 'IS', period)
	IO = get_attribute_total(node_index, network, 'IO', period)

	# Receive inbound shipment (add it to ending IL); will subtract outbound
	# shipment later. Subtract arriving shipment from next period's starting OO.
	# TODO: handle what happens when multiple supply nodes (assembly-type)
	node['EIL'][period] = node['IL'][period] + IS
	for p in list(network.predecessors(node_index)) + [None]:
		node['OO'][p][period+1] -= node['IS'][p][period]

	# Determine current on-hand and backorders (after shipment arrives but
	# before demand is subtracted).
	current_on_hand = max(0, node['IL'][period]) + IS
	current_backorders = max(0, -node['IL'][period])
	# Double check BO calculations.
	current_backorders_check = get_attribute_total(node_index, network, 'BO', period)
	assert math.isclose(current_backorders, current_backorders_check)

	# Determine outbound shipments. (Satisfy demand in order of successor node
	# index.) Also update EIL and BO, and calculate demand met from stock.
	# TODO: allow different allocation policies
	node['DMFS'][period] = 0.0
	for s in list(network.successors(node_index)) + [None]:
		# Outbound shipment to s = min{OH, BO for s + new order from s}.
		node['OS'][s][period] = min(current_on_hand,
									node['BO'][s][period] +
									node['IO'][s][period])
		# Calculate demand met from stock. (Note: This assumes that if there
		# are backorders, they get priority of current period's demands.)
		# TODO: handle successor-level DMFS and FR.
		node['DMFS'][period] = max(0, node['OS'][s][period] - node['BO'][s][period])
		# Update EIL and BO.
		node['EIL'][period] -= node['IO'][s][period]
		node['BO'][s][period] -= min(node['BO'][s][period], node['OS'][s][period])

	# node['OS'][period] = min(current_on_hand, current_backorders + IO)
	#
	# # Determine number of current period's demands (inbound orders) that are
	# # met from stock. (Note: This assumes that if there are backorders, current
	# # period's demands get priority.)
	# node['DMFS'][period] = min(current_on_hand, IO)

	# Calculate fill rate (cumulative in periods 0,...,t).
	met_from_stock = np.sum(node['DMFS'][0:period+1])
	total_demand = np.sum([get_attribute_total(node_index, network, 'IO', t)
						   for t in range(period+1)])
	if total_demand > 0:
		node['FR'][period] = met_from_stock / total_demand
	else:
		node['FR'][period] = 1.0

	# Propagate shipment downstream (i.e., update IS).
	for s in network.successors(node_index):
		network.nodes[s]['IS'][node_index][period+network.nodes[s]['shipment_lead_time']] \
			= node['OS'][s][period]

	# Subtract demand from ending pyinv and calculate costs.
	# TODO: add more flexible ways of calculating in-transit h.c.
	node['HC'][period] = node['local_holding_cost'] * max(0, node['EIL'][period])
	node['SC'][period] = node['stockout_cost'] * max(0, -node['EIL'][period])
	node['ITHC'][period] = node['local_holding_cost'] * \
						   np.sum([network.nodes[p]['OO'][node_index][period]
								   for p in network.successors(node_index)])
	node['TC'][period] = node['HC'][period] + node['SC'][period] + \
							node['ITHC'][period]

	# Set next period's starting IL.
	node['IL'][period+1] = node['EIL'][period]

	# Call generate_downstream_shipments() for all non-visited _successors.
	for s in list(network.successors(node_index)):
		if not visited[s]:
			generate_downstream_shipments(s, network, period, visited)


def get_attribute_total(node_index, network, attribute, period):
	"""Return total of attribute for the period specified. Attribute should be
	an attribute that is indexed by successor or predecessor, i.e., IS, OO, IO,
	OS, or BO. (If another attribute is specified, return the value of the
	attribute, without any summation.)

	Example: get_attribute_total(3, network, 'IS', 5) returns the total
	inbound shipment, from all predecessor nodes, in period 5.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : DiGraph
		NetworkX directed graph representing the multi-echelon pyinv network.
	attribute : str
		Attribute to be totalled. Error occurs if attribute is not present.
	period : int
		Time period.

	Returns
	-------

	"""
	if attribute in ('IS', 'OO'):
		# These attributes are indexed by predecessor.
		return np.sum([network.nodes[node_index][attribute][p][period] for
					   p in list(network.predecessors(node_index))+[None]])
	elif attribute in ('IO', 'OS', 'BO'):
		# These attributes are indexed by successor.
		return np.sum([network.nodes[node_index][attribute][s][period] for
					   s in list(network.successors(node_index))+[None]])
	else:
		return network.nodes[node_index][attribute][period]


# -------------------

# SIMULATION

def simulation(network, num_periods, rand_seed=None):
	"""

	Parameters
	----------
	network : DiGraph
		NetworkX directed graph representing the multi-echelon pyinv network.
	num_periods : int
		Number of periods to simulate.
	rand_seed : int, optional
		Random number generator seed.

	Returns
	-------
	G : DiGraph
		Copy of network, containing performance measures.

	"""

	# TODO: check for directed loops
	# TODO: modify original network; don't make copy

	# CONSTANTS

	# Number of extra periods to allow for calculations past the last period.
	EXTRA_PERIODS = 10

	# INITIALIZATION

	# Make local (deep) copy of graph.
	G = network.copy() #(with_data=True)

	# Initialize state and decision variables at each node.

	# NOTE: Some variables are indexed up to num_periods+EXTRA_PERIODS; the
	# additional slots are to allow calculations past the last period.

	for n in G.nodes:
		# --- State Variables --- #

		# Inbound Shipment: IS[j][t] = shipment quantity arriving at stage from
		# stage j in period t. If j is None, refers to external supply.
		G.nodes[n]['IS'] = {j: np.zeros(num_periods+EXTRA_PERIODS)
							for j in list(G.predecessors(n))+[None]}

		# Inbound Order: IO[j][t] = order quantity arriving at stage from stage
		# j in period t. If j is None, refers to external demand.
		G.nodes[n]['IO'] = {j: np.zeros(num_periods+EXTRA_PERIODS)
							for j in list(G.successors(n))+[None]}

		# Outbound Shipment: OS[j][t] = outbound shipment to stage j in period t.
		# If j is None, refers to external demand.
		G.nodes[n]['OS'] = {j: np.zeros(num_periods)
							for j in list(G.successors(n))+[None]}

		# On-Order: OO[j][t] = on-order quantity (items that have been ordered
		# from j but not yet received) at stage at the beginning of period t.
		# If j is None, refers to external supply.
		G.nodes[n]['OO'] = {j: np.zeros(num_periods+EXTRA_PERIODS)
							for j in list(G.predecessors(n))+[None]}

		# Inventory Level: IL[t] = pyinv level (positive or negative) at
		# stage at the beginning of period t.
		G.nodes[n]['IL'] = np.zeros(num_periods+EXTRA_PERIODS)

		# Backorders: BO[j][t] = number of backorders for successor s at the
		# beginning of period t. If s is None, refers to external demand. Sum
		# over all _successors should always equal IL^-.
		G.nodes[n]['BO'] = {s: np.zeros(num_periods+EXTRA_PERIODS)
							for s in list(G.successors(n))+[None]}

		# Ending Inventory Level: EIL[t] = pyinv level (positive or
		# negative) at stage at the end of period t.
		# NOTE: this is just for convenience, since EIL[i,t] = IL[i,t+1]
		G.nodes[n]['EIL'] = np.zeros(num_periods)

		# Costs: HC[t], SC[t], ITHC[t], TC[t] = holding, stockout, in-transit
		# holding, and total cost incurred at stage in period t.
		G.nodes[n]['HC'] = np.zeros(num_periods)
		G.nodes[n]['SC'] = np.zeros(num_periods)
		G.nodes[n]['ITHC'] = np.zeros(num_periods)
		G.nodes[n]['TC'] = np.zeros(num_periods)

		# Fill Rates: DMFS[t] = demands met from stock at stage in period t;
		# FR[t] = cumulative fill rate in periods 0,...,t.
		G.nodes[n]['DMFS'] = np.zeros(num_periods)
		G.nodes[n]['FR'] = np.zeros(num_periods)

		# --- Decision Variables --- #

		# Order Quantity: OQ[j][t] = order quantity placed by stage to stage j
		# in period t. If j is None, refers to external supply.
		G.nodes[n]['OQ'] = np.zeros(num_periods)

	# Initialize system state.

	# Initialize random number generator.
	np.random.seed(rand_seed)

	# Initialize pyinv levels and other quantities.
	for n in G.nodes():
		# Initialize pyinv levels and backorders.
		# TODO: handle what happens if initial IL < 0 (or prohibit it)
		if G.nodes[n]['initial_inventory_level'] is not None:
			G.nodes[n]['IL'][0] = G.nodes[n]['initial_inventory_level']
		else:
			G.nodes[n]['IL'][0] = 0.0

		# Initialize inbound order quantities for all _predecessors of n,
		# and update on-order quantity.
		for j in G.predecessors(n):
			for t in range(G.nodes[n]['order_lead_time']):
				G.nodes[j]['IO'][n][t] = G.nodes[n]['initial_orders']
				G.nodes[n]['OO'][j][0] += G.nodes[j]['IO'][n][t]

		# Initialize inbound shipment quantities from all _predecessors of n,
		# and update on-order quantity.
		for j in G.predecessors(n):
			for t in range(G.nodes[n]['shipment_lead_time']):
				G.nodes[n]['IS'][j][t] = G.nodes[n]['initial_shipments']
				G.nodes[n]['OO'][j][0] += G.nodes[n]['IS'][j][t]

	# MAIN LOOP

	for t in range(num_periods):

		#print(t)

		# GENERATE DEMANDS AND ORDERS

		# Build list of nodes with no _predecessors. (These will be the starting
		# nodes for the dfs.)
		no_pred = {n for n in G.nodes() if G.in_degree(n) == 0}

		# Initialize visited dict.
		visited = {n: False for n in G.nodes}

		# Generate demands and place orders. Use depth-first search, starting
		# at nodes with no _predecessors, and propagating orders upstream.
		for n in no_pred:
			generate_downstream_orders(n, G, t, visited)

		# GENERATE SHIPMENTS

		# Reset visited dict.
		visited	= {n: False for n in G.nodes}

		# Generate shipments. Use depth-first search, starting at nodes with
		# no _predecessors, and propagating shipments downstream.
		for n in no_pred:
			generate_downstream_shipments(n, G, t, visited)

	# Fill total cost as graph-level attribute.
	G.graph['total_cost'] = np.sum([G.nodes[n]['TC'][t] for n in G.nodes()
									for t in range(num_periods)])
	
	print("")

	return G



def main():
	T = 10
	serial_3 = serial_system(3, local_holding_cost=[7, 4, 2],
							 stockout_cost=[37.12, 0, 0],
							 demand_type=DemandType.NORMAL,
							 demand_mean=5,
							 demand_standard_deviation=1,
							 downstream_0=False)
	G = simulation(serial_3, T, rand_seed=15)
	write_results(G, T, False, None)

	print("")



if __name__ == "__main__":
	main()
