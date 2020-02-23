"""Helper functions for inventory package.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import math
import networkx as nx

from inventory.datatypes import *


### CONSTANTS ###

BIG_INT = 1e100
BIG_FLOAT = 1.0e100


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


def dict_match(d1, d2, require_presence=False, rel_tol=1e-9, abs_tol=0.0):
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
	rel_tol : float
		Relative tolerance.
	abs_tol : float
		Absolute tolerance.
	"""

	match = True

	# Check d1 against d2.
	for key in d1.keys():
		if key in d2:
			if not math.isclose(d1[key], d2[key], rel_tol=rel_tol, abs_tol=abs_tol):
				match = False
		else:
			if not math.isclose(d1[key], 0, rel_tol=rel_tol, abs_tol=abs_tol) \
					or require_presence:
				match = False

	# Check d2 against d1.
	for key in d2.keys():
		if key in d2:
			# We already checked in this case.
			pass
		else:
			if not math.isclose(d2[key], 0, rel_tol=rel_tol, abs_tol=abs_tol) \
					or require_presence:
				match = False

	return match


def is_iterable(x):
	"""Determine whether x is an iterable or a singleton.

	Parameters
	----------
	x
		Object to test for iterable vs. singleton.

	Returns
	-------
	True if x is iterable, False if it is a singleton.

	"""
	# First check whether x is a string (because strings act like iterables).
	if isinstance(x, str):
		return False
	else:
		try:
	#		_ = iter(x)
			_ = (y for y in x)
		except TypeError:
			return False
		else:
			return True


def is_integer(x):
	"""Determine whether x is an integer. Return False if x is not a float,
	or is a non-integer float, or is an int.

	Parameters
	----------
	x : float
		Number to check for integrality.

	Returns
	-------
	is_int : bool
		True if x is an integer, False otherwise.

	"""
	# Check whether x is an int.
	if isinstance(x, int):
		return True
	# Check whether x is a float.
	elif isinstance(x, float):
		# Check whether x is an integer.
		if x.is_integer():
			return True
		else:
			return False
	else:
		return False


def ensure_list_for_time_periods(x, num_periods):
	"""Ensure that x is a list suitable for time-period indexing; if not, create
	such a list and return it.

	"Suitable for time-period indexing" means that it has length num_periods+1,
	and element [0] is ignored.

	If x is a singleton, return a list consisting of `num_periods` copies of x.
	If x is a list of length `num_periods`, return x.
	If x is a list of length `num_periods`-1, shift elements to the right by 1 slot,
		fill [0] element with 0, and return new list.
	Otherwise, raise a ValueError.

	Examples:
		- ensure_list_for_time_periods(5, 3) returns [5, 5, 5]
		- ensure_list_for_time_periods([0, 5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_time_periods([5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_time_periods([0, 5, 2, 1], 3) raises a ValueError.

	Parameters
	----------
	x : float or list
		Object to time-period-ify.
	num_periods : int
		Number of time periods.

	Returns
	-------
	x_new : list
		Time-period-ified list.
	"""
	# Determine whether x is singleton or iterable.
	if is_iterable(x):
		if len(x) == num_periods+1:
			return x
		elif len(x) == num_periods:
			return [0] + x
		else:
			raise ValueError('x must be a singleton or a list of length num_periods or num_periods+1')
	else:
		return [0] + [x] * num_periods


def ensure_list_for_nodes(x, num_nodes, default=None):
	"""Ensure that x is a list suitable for node indexing; if not, create
	such a list and return it.

	"Suitable for node indexing" means that it has length num_nodes.

	If x is a singleton, return a list consisting of `num_nodes` copies of x.
	If x is a list of length `num_nodes`, return x.
	If x is None and `default` is provided, return a list consisting of
		`num_nodes` copies of `default`.
	If x is None and `default` is not provided, a list consisting of
	 	`num_nodes` copies of None.
	Otherwise, raise a ValueError.

	Examples:
		- ensure_list_for_nodes(5, 3) returns [5, 5, 5]
		- ensure_list_for_nodes([0, 5, 2, 1], 4) returns [0, 5, 2, 1]
		- ensure_list_for_nodes([0, 5, 2, 1], 3) raises a ValueError.

	Parameters
	----------
	x : float or list
		Object to node-ify.
	num_nodes : int
		Number of nodes.
	default : float, optional
		Value to use if x is None.

	Returns
	-------
	x_new : list
		Node-ified list.
	"""
	# Is x None?
	if x is None:
		return [default] * num_nodes
	else:
		# Determine whether x is singleton or iterable.
		if is_iterable(x):
			if len(x) == num_nodes:
				return x
			else:
				raise ValueError('x must be a singleton or a list of length num_nodes')
		else:
			return [x] * num_nodes


### GRAPH GENERATORS ###

def serial_system(num_nodes, node_labels=None, downstream_0=True,
				  local_holding_cost=None, echelon_holding_cost=None,
				  stockout_cost=None, order_lead_time=None,
				  shipment_lead_time=None, demand_type=None, demand_mean=None,
				  demand_standard_deviation=None, demand_lo=None, demand_hi=None,
				  demands=None, demand_probabilities=None, initial_IL=None,
				  initial_orders=None, initial_shipments=None, supply_type=None):
	"""Generate serial system with specified number of nodes. Other than
	`num_nodes`, all parameters are optional. If they are provided, they must
	be either a list or a singleton. In the case of a list, the downstream-most
	node must come first, regardless of the labels provided. In the case of a
	singleton, the value will be applied to all relevant nodes.

	Parameters
	----------
	num_nodes : int
		Number of nodes in serial system.
	node_labels : list, optional
		List of node labels, with downstream-most node listed first.
	downstream_0 : bool, optional
		If True, node 0 is downstream; if False, node 0 is upstream. Ignored if
		node_labels is provided.
	local_holding_cost
	echelon_holding_cost
	stockout_cost
	order_lead_time
	shipment_lead_time
	demand_type
	demand_mean
	demand_standard_deviation
	demand_lo
	demand_hi
	demands
	initial_IL
	initial_orders
	initial_shipments
	supply_type

	Returns
	-------
	network : DiGraph
		The serial system network, with parameters filled.

	"""

	# Build list of node labels.
	if node_labels is not None:
		labels = node_labels
	elif downstream_0:
		labels = range(num_nodes)
	else:
		labels = range(num_nodes-1, -1, -1)

	# Build digraph.
	network = nx.DiGraph()
	network.add_nodes_from(labels)
	for n in range(num_nodes-1):
		network.add_edge(labels[n], labels[n+1])

	# Build vectors of attributes.
	h_local = ensure_list_for_nodes(local_holding_cost, num_nodes, 0.0)
	h_echelon = ensure_list_for_nodes(echelon_holding_cost, num_nodes, 0.0)
	p = ensure_list_for_nodes(stockout_cost, num_nodes, 0.0)
	order_LT = ensure_list_for_nodes(order_lead_time, num_nodes, 0)
	shipment_LT = ensure_list_for_nodes(shipment_lead_time, num_nodes, 0)
	d_type = ensure_list_for_nodes(demand_type, num_nodes, None)
	d_mean = ensure_list_for_nodes(demand_mean, num_nodes, None)
	d_sd = ensure_list_for_nodes(demand_standard_deviation, num_nodes, None)
	d_lo = ensure_list_for_nodes(demand_lo, num_nodes, None)
	d_hi = ensure_list_for_nodes(demand_hi, num_nodes, None)
	d = ensure_list_for_nodes(demands, num_nodes, None)
	d_prob = ensure_list_for_nodes(demand_probabilities, num_nodes, None)
	init_IL = ensure_list_for_nodes(initial_IL, num_nodes, None)
	init_orders = ensure_list_for_nodes(initial_orders, num_nodes, None)
	init_shipments = ensure_list_for_nodes(initial_shipments, num_nodes, None)
	s_type = ensure_list_for_nodes(supply_type, num_nodes, None)

	# Add attributes.
	for n_index in range(num_nodes):
		n = labels[n_index]
		network.nodes[n]['local_holding_cost'] = h_local[n_index]
		network.nodes[n]['echelon_holding_cost'] = h_echelon[n_index]
		network.nodes[n]['stockout_cost'] = p[n_index]
		network.nodes[n]['order_LT'] = order_LT[n_index]
		network.nodes[n]['shipment_LT'] = shipment_LT[n_index]
		network.nodes[n]['demand_type'] = d_type[n_index]
		if network.nodes[n]['demand_type'] == DemandType.NORMAL:
			network.nodes[n]['demand_mean'] = d_mean[n_index]
			network.nodes[n]['demand_standard_deviation'] = d_sd[n_index]
		else:
			network.nodes[n]['demand_mean'] = None
			network.nodes[n]['demand_standard_deviation'] = None
		if network.nodes[n]['demand_type'] in (DemandType.UNIFORM_CONTINUOUS,
			DemandType.UNIFORM_DISCRETE):
			network.nodes[n]['demand_hi'] = d_hi[n_index]
			network.nodes[n]['demand_lo'] = d_lo[n_index]
		else:
			network.nodes[n]['demand_hi'] = None
			network.nodes[n]['demand_lo'] = None
		if network.nodes[n]['demand_type'] == DemandType.DETERMINISTIC:
			network.nodes[n]['demands'] = d[n_index]
		else:
			network.nodes[n]['demands'] = None
		if network.nodes[n]['demand_type'] == DemandType.DISCRETE_EXPLICIT:
			network.nodes[n]['demands'] = d[n_index]
			network.nodes[n]['demand_probabilities'] = d_prob[n_index]
		else:
			network.nodes[n]['demands'] = None
			network.nodes[n]['demand_probabilities'] = None
		network.nodes[n]['initial_IL'] = init_IL[n_index]
		network.nodes[n]['initial_orders'] = init_orders[n_index]
		network.nodes[n]['initial_shipments'] = init_shipments[n_index]
		network.nodes[n]['supply_type'] = s_type[n_index]

	return network






