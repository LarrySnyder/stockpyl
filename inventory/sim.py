"""Code for simulating multi-echelon inventory systems.

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
		- demand_probabilities
		- demand_lo
		- demand_hi
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
		- EIL
		- HC
		- SC
		- TC
		- DMFS
		- FR
		- OQ

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np

from inventory.datatypes import *
from inventory.sim_io import *
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
		demand = np.random.choice(node['demands'], p=node['demand_probabilities'])
	else:
		raise ValueError('Valid demand_type not provided')

	return demand


def generate_downstream_orders(node_index, network, period, visited):
	"""Generate demands and orders for all downstream nodes using depth-first-search.
	Ignore nodes for which visited=True.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : DiGraph
		NetworkX directed graph representing the multi-echelon inventory network.
	period : int
		Time period. Required if node or downstream nodes have demand_type =
		DETERMINISTIC; ignored otherwise.
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

	# Call generate_downstream_orders() for all non-visited successors.
	for s in list(network.successors(node_index)):
		if not visited[s]:
			generate_downstream_orders(s, network, period, visited)

	# Calculate order quantity. # TODO: handle policies
	order_quantity = np.sum([network.nodes[node_index]['IO'][s][period] for s in
							 list(network.successors(node_index))+[None]])

	# Place orders to all predecessors.
	for p in list(network.predecessors(node_index)):
		network.nodes[p]['IO'][node_index][period] = order_quantity


def get_attribute_total(node_index, network, attribute, period):
	"""Return total of attribute for the period specified. Attribute should be
	an attribute that is indexed by successor or predecessor, i.e., IS, OO, IO,
	or OS. (If another attribute is specified, return the value of the attribute,
	without any summation.)

	Example: get_attribute_total(3, network, 'IS', 5) returns the total
	inbound shipment, from all predecessor nodes, in period 5.

	Parameters
	----------
	node_index : int
		Index of starting node for depth-first search.
	network : DiGraph
		NetworkX directed graph representing the multi-echelon inventory network.
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
	elif attribute in ('IO', 'OS'):
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
		NetworkX directed graph representing the multi-echelon inventory network.
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

		# Inventory Level: IL[t] = inventory level (positive or negative) at
		# stage at the beginning of period t.
		G.nodes[n]['IL'] = np.zeros(num_periods+EXTRA_PERIODS)

		# Ending Inventory Level: EIL[t] = inventory level (positive or
		# negative) at stage at the end of period t.
		# NOTE: this is just for convenience, since EIL[i,t] = IL[i,t+1]
		G.nodes[n]['EIL'] = np.zeros(num_periods)

		# Costs: HC[t], SC[t], TC[t] = holding, stockout, and total cost
		# incurred at stage in period t.
		G.nodes[n]['HC'] = np.zeros(num_periods)
		G.nodes[n]['SC'] = np.zeros(num_periods)
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

	# Initialize inventory levels and other quantities.
	for n in G.nodes():
		# Initialize inventory levels.
		G.nodes[n]['IL'][0] = G.nodes[n]['initial_IL']

		# Initialize inbound order quantities for all predecessors of n,
		# and update on-order quantity.
		for j in G.predecessors(n):
			for t in range(G.nodes[n]['order_LT']):
				G.nodes[j]['IO'][n][t] = G.nodes[n]['initial_orders']
				G.nodes[n]['OO'][j][0] += G.nodes[j]['IO'][n][t]

		# Initialize inbound shipment quantities from all predecessors of n,
		# and update on-order quantity.
		for j in G.predecessors(n):
			for t in range(G.nodes[n]['shipment_LT']):
				G.nodes[n]['IS'][j][t] = G.nodes[n]['initial_shipments']
				G.nodes[n]['OO'][j][0] += G.nodes[n]['IS'][j][t]

	# MAIN LOOP

	for t in range(num_periods):

		# GENERATE DEMANDS AND ORDERS

		# Build list of nodes with no predecessors. (These will be the starting
		# nodes for the dfs.)
		no_pred = {n for n in G.nodes() if G.in_degree(n) == 0}

		# Initialize visited dict.
		visited = {n: False for n in G.nodes}

		# Generate demands and place orders. Use depth-first search, starting
		# at nodes with no predecessors.
		for n in no_pred:
			generate_downstream_orders(n, G, t, visited)

	# Fill total cost as graph-level attribute.
	G.graph['total_cost'] = np.sum([G.nodes[n]['TC'][t] for n in G.nodes()
									for t in range(num_periods)])
	
	print("")

	return G



def main():
	T = 10
	G = simulation(instance_2_stage, T)
	write_results(G, T, False, None)



if __name__ == "__main__":
	main()
