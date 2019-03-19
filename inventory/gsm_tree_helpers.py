"""Helper code for dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2000).

'node' and 'stage' are used interchangeably in the documentation.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np

### CONSTANTS ###

BIG_INT = 1e100


### UTILITY FUNCTIONS ###

def min_of_dict(d):
	"""Determine min value of dict and return min and argmin (key).

	Values must be numeric.

	Parameters
	----------
	d : dict
		The dict.

	Returns
	-------
	min_value : float
		Minimum value in dict.
	min_key
		Key that attains minimum value.

	Raises
	------
	TypeError
		If dict contains a non-numeric value.
	"""
	min_key = min(d, key=d.get)
	min_value = d[min_key]

	return min_value, min_key


def dict_match(d1, d2, require_presence=False):
	"""Check whether two dicts have equal keys and values.

	A missing key is treated as 0 if the key is present in the other dict,
	unless require_presence is True, in which case the dict must have the
	key to count as a match.

	Parameters
	----------
	d1 : node
		First dict for comparison.
	d2 : node
		Second dict for comparison.
	require_presence : bool, optional
		Set to True to require dicts to have the same keys, or False
		(default) to treat missing keys as 0s.
	"""

	match = True

	# Check d1 against d2.
	for key in d1.keys():
		if key in d2:
			if d1[key] != d2[key]:
				match = False
		else:
			if d1[key] != 0 or require_presence:
				match = False

	# Check d2 against d1.
	for key in d2.keys():
		if key in d2:
			# We already checked in this case.
			pass
		else:
			if d2[key] != 0 or require_presence:
				match = False

	return match


### SOLUTION HANDLING ###

def solution_cost(tree, cst):
	"""Calculate expected cost of given solution.

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
		SI = inbound_cst(tree, k, cst)
		net_lead_time = SI + tree.nodes[k]['processing_time'] - cst[k]

		# Calculate safety stock and holding cost.
		safety_stock = tree.nodes[k]['demand_bound_constant'] * \
					   tree.nodes[k]['net_demand_standard_deviation'] * \
					   np.sqrt(net_lead_time)
		holding_cost = tree.nodes[k]['holding_cost'] * safety_stock

		# Set stage_cost equal to holding cost at node_k k.
		cost += holding_cost

	return cost


def inbound_cst(tree, k, cst):
	"""Determine the inbound CST (SI) for a stage, given the outbound CSTs.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	k
		Index of node_k.
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	SI : int
		Inbound CST (SI).

	"""

	# Determine inbound CST (= max of CST for all predecessors, and external
	# inbound CST).
	SI = tree.nodes[k]['external_inbound_cst']
	if tree.in_degree[k] > 0:
		SI = max(SI, np.max([cst[i] for i in tree.predecessors(k)]))

	return SI


def base_stock_levels(tree, cst):
	"""Determine base-stock levels for given committed service times (CST).

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	base_stock_levels : dict
		Dict of base-stock levels.

	"""

	safety_stock = node_k['demand_bound_constant'] * \
				   node_k['net_demand_standard_deviation'] * \
				   np.sqrt(SI + node_k['processing_time'] - S)


def safety_stock_levels(tree, cst):
	"""Determine safety stock levels for given committed service times (CST).
	
	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Graph need not have been relabeled.
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree.

	Returns
	-------
	safety_stock : dict
		Dict of safety stock levels.

	"""

	safety_stock = {}
	for k in tree.nodes:
		safety_stock[k] = tree.nodes[k]['demand_bound_constant'] * \
						  tree.nodes[k]['net_demand_standard_deviation'] * \
						  np.sqrt(SI + tree.nodes[k]['processing_time'] - S)
