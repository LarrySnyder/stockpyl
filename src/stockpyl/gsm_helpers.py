# ===============================================================================
# stockpyl - gsm_helpers Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_gsm_helpers| module contains helper code for the dynamic programming (DP) algorithm 
to solve the guaranteed-service model (GSM) for multi-echelon inventory systems with tree structures 
by Graves and Willems (2000, 2003), which is implemented in the |mod_gsm_tree| module.

.. note:: |node_stage|

.. note:: |fosct_notation|

.. seealso::

	For an overview of multi-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for multi-echelon inventory optimization<tutorial_meio_page>`.


References
----------
S. C. Graves and S. P. Willems. Optimizing strategic safety stock placement in supply chains. 
*Manufacturing and Service Operations Management*, 2(1):68-83, 2000.

S. C. Graves and S. P. Willems. Erratum: Optimizing strategic safety stock placement in supply chains. 
*Manufacturing and Service Operations Management*, 5(2):176-177, 2003.


API Reference
-------------

"""


import numpy as np

from stockpyl.helpers import *


### SOLUTION HANDLING ###

def solution_cost_from_cst(tree, cst):
	"""Calculate expected cost per period of given solution as specified by committed service times (CSTs).

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Network need not have been relabeled.
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree. [:math:`S`]

	Returns
	-------
	cost : float
		Expected cost of the solution. [:math:`g(S)`]


	**Example** (Example 6.5):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("example_6_5"))
		>>> solution_cost_from_cst(tree, {1: 0, 2: 0, 3: 0, 4: 1})
		8.277916867529369

	"""

	cost = 0
	for k in tree.nodes:

		# Calculate net lead time.
		nlt = net_lead_time(tree, tree.node_indices, cst)

		# Calculate safety stock and holding cost.
		safety_stock = k.demand_bound_constant * \
					   k.net_demand_standard_deviation * \
					   math.sqrt(nlt[k.index])
		holding_cost = k.holding_cost * safety_stock

		# Set stage_cost equal to holding cost at node_k k.
		cost += holding_cost

	return cost


def solution_cost_from_base_stock_levels(tree, local_bsl):
	"""Calculate expected cost per period of given solution as specified by base-stock
	levels. Cost is based on safety stock, which is calculated as base-stock
	level minus demand mean.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Graph need not have been relabeled.
	local_bsl : dict
		Dict of local base-stock levels for each node, using the same node
		labeling as tree. [:math:`y`]

	Returns
	-------
	cost : float
		Expected cost of the solution. [:math:`g(S)`]


	**Example** (Example 6.5):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("example_6_5"))
		>>> solution_cost_from_base_stock_levels(tree, {1: 2.45, 2: 1.00, 3: 1.41, 4: 0.00})
		8.27

	"""

	cost = 0
	for k in tree.nodes:
		# Calculate safety stock and holding cost.
		safety_stock = local_bsl[k.index] - k.net_demand_mean
		holding_cost = k.holding_cost * safety_stock

		# Set stage_cost equal to holding cost at node_k.
		cost += holding_cost

	return cost


def inbound_cst(tree, node_index, cst):
	"""Determine the inbound CST (:math:`SI`) for one or more stages, given all of the
	outbound CSTs. The inbound CST is calculated as the maximum of the outbound CST for 
	all predecessors, and the external inbound CST (if any).

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Network need not have been relabeled.
	node_index : node *or* iterable container
		A single node index *or* a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as ``tree``. [:math:`S`]

	Returns
	-------
	SI : int *or* dict
		Inbound CST of node ``node_index`` (if ``node_index`` is a single node); *or* a dictionary of
		inbound CST values keyed by node (if ``node_index`` is an iterable container) [:math:`SI`].


	**Example** (Problem 6.9):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("problem_6_9"))
		>>> inbound_cst(tree, 3, {1: 3, 2: 3, 3: 31, 4: 3, 5: 10, 6: 2})
		10

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(node_index):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		node_index = [node_index]
		n_is_iterable = False

	# Build dict of SI values.
	SI = {}
	for k in node_index:
		# Determine inbound CST (= max of CST for all predecessors, and external
		# inbound CST).
		k_node = tree.nodes_by_index[k]
		SI[k] = k_node.external_inbound_cst
		if len(k_node.predecessor_indices()) > 0:
			SI[k] = max(SI[k], np.max([cst[i] for i in k_node.predecessor_indices()]))

	if n_is_iterable:
		return SI
	else:
		return SI[node_index[0]]


def net_lead_time(tree, node_index, cst):
	"""Determine the net lead time (NLT) for one or more stages, given the
	outbound CSTs.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Network need not have been relabeled.
	node_index : node *or* iterable container
		A single node index *or* a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree. [:math:`S`]

	Returns
	-------
	nlt : int *or* dict
		NLT of node ``node_index`` (if ``node_index`` is a single node); *or* a dictionary of NLT values
		keyed by node (if ``node_index`` is an iterable container).


	**Example** (Problem 6.9):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("problem_6_9"))
		>>> net_lead_time(tree, tree.node_indices, {1: 3, 2: 3, 3: 31, 4: 3, 5: 10, 6: 2})
		{1: 35, 2: 35, 3: 0, 4: 0, 5: 0, 6: 0}

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(node_index):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		node_index = [node_index]
		n_is_iterable = False

	# Get inbound CSTs.
	SI = inbound_cst(tree, node_index, cst)

	# Determine NLTs.
	nlt = {}
	for k in node_index:
		# Determine NLT.
		nlt[k] = SI[k] + tree.nodes_by_index[k].processing_time - cst[k]

	if n_is_iterable:
		return nlt
	else:
		return nlt[node_index[0]]


def cst_to_base_stock_levels(tree, node_index, cst):
	"""Determine base-stock levels for one or more stages, for given committed
	service times (CST).

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Graph need not have been relabeled.
	node_index : node *or* iterable container
		A single node index *or* a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree. [:math:`S`]

	Returns
	-------
	base_stock_level : float *or* dict
		Base-stock level of node ``node_index`` (if ``node_index`` is a single node); *or* a dictionary of
		base-stock levels keyed by node (if ``node_index`` is an iterable container). [:math:`y`]


	**Example** (Problem 6.9):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("example_6_5"))
		>>> cst_to_base_stock_levels(tree, tree.node_indices, {1: 0, 2: 0, 3: 0, 4: 1})
		{1: 2.4494897427831783, 3: 1.4142135623730951, 2: 1.0, 4: 0.0}

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(node_index):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		node_index = [node_index]
		n_is_iterable = False

	# Calculate net lead times and safety stock levels.
	nlt = net_lead_time(tree, node_index, cst)
	ss = safety_stock_levels(tree, node_index, cst)

	base_stock_level = {}
	for k in node_index:
		base_stock_level[k] = tree.nodes_by_index[k].net_demand_mean * nlt[k] + ss[k]

	if n_is_iterable:
		return base_stock_level
	else:
		return base_stock_level[node_index[0]]


def safety_stock_levels(tree, node_index, cst):
	"""Determine safety stock levels for one or more nodes, for given committed
	service times (CST).
	
	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Graph need not have been relabeled.
	node_index : node *or* iterable container
		A single node index *or* a container of node indices (dict, list, set, etc.).
	cst : dict
		Dict of CSTs for each node, using the same node labeling as tree. [:math:`S`]

	Returns
	-------
	safety_stock_level : float *or* dict
		Safety stock of node ``node_index`` (if ``node_index`` is a single node); *or* a dictionary of
		safety stock values keyed by node (if ``node_index`` is an iterable container).


	**Example** (Problem 6.9):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = preprocess_tree(load_instance("example_6_5"))
		>>> safety_stock_levels(tree, tree.node_indices, {1: 0, 2: 0, 3: 0, 4: 1})
		{1: 2.4494897427831783, 3: 1.4142135623730951, 2: 1.0, 4: 0.0}

	"""

	# Determine whether n is singleton or iterable.
	if is_iterable(node_index):
		n_is_iterable = True
	else:
		# n is a singleton; replace it with a list.
		node_index = [node_index]
		n_is_iterable = False

	# Calculate net lead times.
	nlt = net_lead_time(tree, node_index, cst)

	safety_stock_level = {}
	for k in node_index:
		node_k = tree.nodes_by_index[k]
		safety_stock_level[k] = node_k.demand_bound_constant * \
						  node_k.net_demand_standard_deviation * \
						  math.sqrt(nlt[k])

	if n_is_iterable:
		return safety_stock_level
	else:
		return safety_stock_level[node_index[0]]
