"""Helper code for dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2000).

'node' and 'stage' are used interchangeably in the documentation.

(c) Lawrence V. Snyder
Lehigh University

"""

import numpy as np
import math

from stockpyl.helpers import *


### SOLUTION HANDLING ###

def solution_cost_from_cst(tree, cst):
	"""Calculate expected cost of given solution as specified by CST.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	cost : float
		Expected cost of the solution.

	"""

	cost = 0
	for k in tree.nodes:

		# Calculate net lead time.
		nlt = net_lead_time(tree, tree.nodes, cst)

		# Calculate safety stock and holding cost.
		safety_stock = tree.nodes[k]['demand_bound_constant'] * \
					   tree.nodes[k]['net_demand_standard_deviation'] * \
					   np.sqrt(nlt[k])
		holding_cost = tree.nodes[k]['holding_cost'] * safety_stock

		# Set stage_cost equal to holding cost at node_k k.
		cost += holding_cost

	return cost


def solution_cost_from_base_stock_levels(tree, local_bsl):
	"""Calculate expected cost of given solution as specified by base-stock
	levels. Cost is based on safety stock, which is calculated as base-stock
	level minus demand mean.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	local_bsl : dict
		Dict of local base-stock levels for each node, using the same node
		labeling as tree.

	Returns
	-------
	cost : float
		Expected cost of the solution.

	"""

	cost = 0
	for k in tree.nodes:
		# Calculate safety stock and holding cost.
		safety_stock = local_bsl[k] - tree.nodes[k]['net_demand_mean']
		holding_cost = tree.nodes[k]['holding_cost'] * safety_stock

		# Set stage_cost equal to holding cost at node_k.
		cost += holding_cost

	return cost


def inbound_cst(tree, n, cst):
	"""Determine the inbound CST (SI) for one or more stages, given the
	outbound CSTs.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	n : node OR iterable container
		A single node index OR a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	SI : int OR dict
		Inbound CST (SI) of node n (if n is a single node); OR a dictionary of
		inbound CST (SI) values keyed by node (if n is an iterable container).

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(n):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		n = [n]
		n_is_iterable = False

	# Build dict of SI values.
	SI = {}
	for k in n:
		# Determine inbound CST (= max of CST for all _predecessors, and external
		# inbound CST).
		SI[k] = tree.nodes[k]['external_inbound_cst']
		if tree.in_degree[k] > 0:
			SI[k] = max(SI[k], np.max([cst[i] for i in tree.predecessors(k)]))

	if n_is_iterable:
		return SI
	else:
		return SI[n[0]]


def net_lead_time(tree, n, cst):
	"""Determine the net lead time (NLT) for one or more stages, given the
	outbound CSTs.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	n : node OR iterable container
		A single node index OR a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	nlt : int OR dict
		NLT of node n (if n is a single node); OR a dictionary of NLT values
		keyed by node (if n is an iterable container).

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(n):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		n = [n]
		n_is_iterable = False

	# Get inbound CSTs.
	SI = inbound_cst(tree, n, cst)

	# Determine NLTs.
	nlt = {}
	for k in n:
		# Determine NLT.
		nlt[k] = SI[k] + tree.nodes[k]['processing_time'] - cst[k]

	if n_is_iterable:
		return nlt
	else:
		return nlt[n[0]]


def cst_to_base_stock_levels(tree, n, cst):
	"""Determine base-stock levels for one or more stages, for given committed
	service times (CST).

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	n : node OR iterable container
		A single node index OR a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	base_stock : float OR dict
		Base-stock level of node n (if n is a single node); OR a dictionary of
		base-stock levels keyed by node (if n is an iterable container).

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(n):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		n = [n]
		n_is_iterable = False

	# Calculate net lead times and safety stock levels.
	nlt = net_lead_time(tree, n, cst)
	ss = safety_stock_levels(tree, n, cst)

	base_stock = {}
	for k in n:
		base_stock[k] = tree.nodes[k]['net_demand_mean'] * nlt[k] + ss[k]

	if n_is_iterable:
		return base_stock
	else:
		return base_stock[n[0]]


def safety_stock_levels(tree, n, cst):
	"""Determine safety stock levels for one or more nodes, for given committed
	service times (CST).
	
	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	n : node OR iterable container
		A single node index OR a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	safety_stock : float OR dict
		Safety stock of node n (if n is a single node); OR a dictionary of
		safety stock values keyed by node (if n is an iterable container).

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(n):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		n = [n]
		n_is_iterable = False

	# Calculate net lead times.
	nlt = net_lead_time(tree, n, cst)

	safety_stock = {}
	for k in n:
		safety_stock[k] = tree.nodes[k]['demand_bound_constant'] * \
						  tree.nodes[k]['net_demand_standard_deviation'] * \
						  np.sqrt(nlt[k])

	if n_is_iterable:
		return safety_stock
	else:
		return safety_stock[n[0]]
