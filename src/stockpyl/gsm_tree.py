# ===============================================================================
# stockpyl - gsm_tree Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_gsm_tree| module implements Graves and Willems's (2000, 2003) dynamic programming (DP)
algorithm for multi-echelon inventory systems with tree structures. 

.. note:: |node_stage|

The primary data object is the |class_network|, which contains all of the data
for the GSM instance.

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

import networkx as nx
import copy

from stockpyl.gsm_helpers import *
from stockpyl.helpers import *
from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.supply_chain_node import SupplyChainNode



### OPTIMIZATION ###

def optimize_committed_service_times(tree):
	"""Optimize committed service times using the dynamic programming (DP) algorithm of
	Graves and Willems (2000, 2003).

	``tree`` is the |class_network| containing the instance. The tree need not already have been
	pre-processed using :func:`preprocess_tree` or :func:`relabel_nodes`; this function will do so. 

	Output parameters are expressed using the original labeling of tree, even if the nodes
	are relabeled internally.

	Demands are assumed to be normally distributed. 

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Current node labels are ignored and may be anything.

	Returns
	-------
	opt_cst : dict
		Dict of optimal CSTs, with node indices as keys and CSTs as values.
	opt_cost : float
		Optimal expected cost of system.
	
	Raises
	------
	ValueError
		If any sink node (node with no successors) has no demand mean or standard devation provided.


	**Example** (Example 6.5):

	.. testsetup:: *

		from stockpyl.gsm_tree import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> tree = load_instance("example_6_5")
		>>> opt_cst, opt_cost = optimize_committed_service_times(tree)
		>>> opt_cst
		{1: 0, 3: 0, 2: 0, 4: 1}
		>>> opt_cost
		8.277916867529369


	References
	----------
	S. C. Graves and S. P. Willems. Optimizing strategic safety stock placement in supply chains. 
	*Manufacturing and Service Operations Management*, 2(1):68-83, 2000.

	S. C. Graves and S. P. Willems. Erratum: Optimizing strategic safety stock placement in supply chains. 
	*Manufacturing and Service Operations Management*, 5(2):176-177, 2003.
	"""
 
	# Validate parameters.
	for n in tree.sink_nodes:
		if n.demand_source.mean is None:
			raise ValueError(f'All sink nodes must have demand_source.mean (node {n.index} does not).')
		if n.demand_source.standard_deviation is None:
			raise ValueError(f'All sink nodes must have demand_source.standard_deviation (node {n.index} does not).')

	# Preprocess tree.
	tree = preprocess_tree(tree)

	# Relabel nodes.
	tree = relabel_nodes(tree)

	# Solve.
	opt_cst_relabeled, opt_cost = _cst_dp_tree(tree)

	# Prepare optimal solution in terms of original labels.
	opt_cst = {k.original_label: opt_cst_relabeled[k.index] for k in tree.nodes}

	return opt_cst, opt_cost


def _cst_dp_tree(tree):
	"""Optimize committed service times on pre-processed tree.

	Optimization is performed using the dynamic programming (DP) algorithm of
	Graves and Willems (2000).

	``tree`` is the |class_network| containing the instance. It must be pre-processed
	before calling this function.

	Assumes demand bound over tau periods is of the form
	:math:`z_\\alpha\\sigma\\sqrt{\\tau}`.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Current node labels are ignored and may be anything.

	Returns
	-------
	opt_cst : dict
		Dict of optimal CSTs, with node indices as keys and CSTs as values.
	opt_cost : float
		Optimal expected cost of system.

	"""

	# Initialize dicts to store values of theta_in(.) and theta_out(.) functions
	# (called f(.) and g(.) in Graves and Willems).
	theta_in = {k_index: {} for k_index in tree.node_indices}
	theta_out = {k_index: {} for k_index in tree.node_indices}

	# Get min and max node indices (for convenience).
	min_k_index = int(np.min(tree.node_indices))
	max_k_index = int(np.max(tree.node_indices))

	# Initialize best_cst_adjacent.
	# best_cst_adjacent[k_index][S][i] = CST chosen for stage i when calculating
	# theta_out(S) or theta_in(SI) for stage k.
	best_cst_adjacent = {k.index: {S: {} for S in
		range(k.max_replenishment_time+1)} for k in tree.nodes}

	# Loop through stages.
	for k_index in range(min_k_index, max_k_index + 1):

		# Get shortcuts to some parameters (for convenience).
		k = tree.nodes_by_index[k_index]
		max_replen_time = k.max_replenishment_time
		proc_time = k.processing_time

		# Evaluate theta_out(k_index, S) if p(k_index) is downstream from k_index and
		# and k_index < final k_index, evaluate theta_in(k_index, SI) otherwise.
		if k_index < max_k_index and k.larger_adjacent_node_is_downstream:

			# p(k_index) is downstream from k_index -- evaluate theta_out(k_index, S).
			for S in range(max_replen_time+1):
				# Calculate theta_out.
				theta_out[k_index][S], temp_best_cst_adjacent = \
					_calculate_theta_out(tree, k_index, S, theta_in, theta_out)
				# Copy temp_best_cst_adjacent to best_cst_adjacent.
				best_cst_adjacent[k_index][S] = {i: temp_best_cst_adjacent[i]
										   for i in temp_best_cst_adjacent}

			# Set values of theta_out and best_cst_adjacent for
			# max_replenishment_time+1 to max_max_replenishment_time to
			# theta_out(max_replenishment_time).
			# Needed so that stages with larger max_replenishment_time don't
			# encounter undefined values of theta_out.
			for S in range(max_replen_time+1,
						   tree.max_max_replenishment_time + 1):
				theta_out[k_index][S] = theta_out[k_index][max_replen_time]
				best_cst_adjacent[k_index][S] = best_cst_adjacent[k_index][max_replen_time]

		else:

			# p(k_index) is upstream from k_index -- evaluate theta_in(k_index, SI).
			for SI in range(max_replen_time - proc_time + 1):
				# Calculate theta_in.
				theta_in[k_index][SI], temp_best_cst_adjacent = \
					_calculate_theta_in(tree, k_index, SI, theta_in, theta_out)
				# Copy temp_best_cst_adjacent to best_cst_adjacent.
				best_cst_adjacent[k_index][SI] = {i: temp_best_cst_adjacent[i]
											for i in temp_best_cst_adjacent}

			# Set values of theta_in and best_cst_adjacent for
			# max_replenishment_time+1 to max_max_replenishment_time to
			# theta_in(max_replenishment_time - processing_time).
			# Needed so that stages with larger max_replenishment_time don't
			# encounter undefined values of theta_in.
			for SI in range(max_replen_time - proc_time + 1,
							tree.max_max_replenishment_time + 1):
				theta_in[k_index][SI] = theta_in[k_index][max_replen_time - proc_time]
				best_cst_adjacent[k_index][SI] = \
					best_cst_adjacent[k_index][max_replen_time - proc_time]

	# Determine best value of SI for final stage.
	max_k_node = tree.nodes_by_index[max_k_index]
	SI_dict = {SI: theta_in[max_k_index][SI] for SI in
			   range(max_k_node.max_replenishment_time -
					 max_k_node.processing_time + 1)} # smaller range of SI
	best_theta_in, best_SI = min_of_dict(SI_dict)

	# Initialize dict of optimal CSTs and optimal inbound CSTs.
	opt_cst = {}
	opt_in_cst = {}

	# Backtrack to find optimal CSTs: Loop backwards through stages k_index;
	# if p(k_index) is downstream from k_index, then set k_index's outbound CST to p(k_index)'s
	# optimal inbound CST (which we get from best_cst_adjacent[p(k_index)][CST(p(k_index))]);
	# if p(k_index) is upstream from k_index, then set k_index's inbound CST to p(k_index)'s optimal
	# outbound CST and set k_index's outbound CST to the optimal for that inbound
	# CST (from best_cst_adjacent[p(k_index)][CST(p(k_index))]).
	# For each stage, remember optimal outbound _and_ inbound CSTs.
	for k_index in range(max_k_index, min_k_index-1, -1):

		# Get node k.
		k = tree.nodes_by_index[k_index]

		# Get p(k_index), and determine whether p(k_index) and p(p(k_index)) are upstream or
		# downstream (for convenience).
		if k_index < max_k_index:
			pk = k.larger_adjacent_node
			pk_is_downstream = k.larger_adjacent_node_is_downstream
			if pk < max_k_index:
				ppk_is_downstream = tree.nodes_by_index[pk].larger_adjacent_node_is_downstream

		# Where is p(k_index)?
		if k_index == max_k_index:
			# This is final stage.
			opt_cst[k_index] = best_cst_adjacent[k_index][best_SI][k_index]
			opt_in_cst[k_index] = best_SI
		elif pk_is_downstream:
			# p(k_index) is downstream from k. Is p(p(k_index)) upstream or downstream from p(k_index)?
			if pk != max_k_index and ppk_is_downstream:
				# p(p(k_index)) is downstream from p(k_index) -- that means that optimal
				# CST values are stored in best_cst_adjacent[pk][opt_cst[pk]][.].
				opt_cst[k_index] = best_cst_adjacent[pk][opt_cst[pk]][k_index]
			else:
				# p(p(k_index)) is upstream from p(k_index) (or it's the final node) --
				# that means that optimal CST values are stored in
				# best_cst_adjacent[pk][opt_in_cst[ppk]][.].
				opt_cst[k_index] = best_cst_adjacent[pk][opt_in_cst[pk]][k_index]
			opt_in_cst[k_index] = best_cst_adjacent[k_index][opt_cst[k_index]][k_index]
		else:
			# p(k_index) is upstream from k. Is p(p(k_index)) upstream or downstream from p(k_index)?
			if pk != max_k_index and ppk_is_downstream:
				# p(p(k_index)) is downstream from p(k_index) -- that means that optimal
				# inbound CST values are stored in
				# best_cst_adjacent[pk][opt_cst[pk]][.].
				opt_in_cst[k_index] = best_cst_adjacent[pk][opt_cst[pk]][k_index]
			else:
				# p(p(k_index)) is upstream from p(k_index) (or it's the final node) --
				# that means that optimal inbound CST values are stored in
				# best_cst_adjacent[pk][opt_in_cst[pk]][.].
				opt_in_cst[k_index] = best_cst_adjacent[pk][opt_in_cst[pk]][k_index]
			opt_cst[k_index] = best_cst_adjacent[k_index][opt_in_cst[k_index]][k_index]

		# If outbound CST for k_index is greater than k_index's external outbound CST,
		# reset it.
		opt_cst[k_index] = min(opt_cst[k_index], k.external_outbound_cst)

	# Get optimal cost.
	opt_cost = best_theta_in

	return opt_cst, opt_cost


def _calculate_theta_out(tree, k_index, S, theta_in_partial, theta_out_partial):
	"""Calculate the function :math:`\\theta^o_k(S)` as described in Section 6.3.6.2 of
	|fosct| [function :math:`f_i(S)` in Section 5 of Graves and Willems
	(2003)].

	Original function is modified in the following ways:
	1. If :math:`S` is greater than the external outbound CST for stage :math:`k`,
	:math:`\\theta^o_k(S)` is calculated as though :math:`S` = external outbound CST. (If :math:`k` is a sink
	stage, :math:`\\theta^o_k(\\cdot)` will never be calculated [:math:`\\theta^i_k(\\cdot)` will be], but
	:math:`k` might have non-zero external outbound CST even if it is not a sink stage.)
	2. The range of values of :math:`SI` for which :math:`c_k(S,SI)` is evaluated begins at
	:math:`\\max\\{\\text{external_inbound_cst}, S - T_k\\}`, not :math:`\\max\\{0, S - T_k\\}`.
	3. The demand bound demand bound over :math:`\\tau` periods is assumed to be of the form
	:math:`z_\\alpha\\sigma\\sqrt{\\tau}`.
	4. When calculating :math:`c_k(S, SI)`, upstream nodes are allowed to use outbound
	CSTs greater than :math:`SI`, and downstream nodes are allowed to use inbound
	CSTs greater than :math:`S`. In effect, this allows multiple inbound/outbound
	CSTs for a single node.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Tree must be pre-processed already.
	k_index : int
		Index of node.
	S : int
		Outbound committed service time.
	theta_in_partial : dict
		Dict of values of theta_in function that have been calculated so far
		(i.e., for ``i`` < ``k_index``).
	theta_out_partial : dict
		Dict of values of theta_out function that have been calculated so far
		(i.e., for ``i`` < ``k_index``).

	Returns
	-------
	theta_out_k_S : float
		The value of :math:`\\theta^o_k(S)`.
	best_cst_adjacent : dict
		Dict indicating, for each adjacent stage :math:`i` with :math:`i \\le k`, the CST value
		that minimized :math:`\\theta^o_i(\\cdot)` for the optimal value of :math:`SI`.
		* If :math:`i` serves :math:`k`, then ``best_CST_adjacent[i]`` = the value of :math:`S_i` that
		minimizes :math:`\\theta^o_i(S_i)`.
		* If :math:`i` is served by :math:`k`, then ``best_CST_adjacent[i]`` = the value of :math:`SI_i`
		that minimizes :math:`\\theta^i_i(SI_i)`.
		* If :math:`i = k`, then ``best_CST_adjacent[i]`` = the best value of :math:`SI` chosen in
		minimization of :math:`\\theta^o_k(\\cdot)`.
	"""

	# Get node k_index, for convenience.
	k = tree.nodes_by_index[k_index]

	# Initialize min_c.
	min_c = float('inf')

	# Initialize output dict.
	best_cst_adjacent = {}

	# Initialize dict of c_k(S, SI) values (keys = SI values).
	c_SI = {}

	# Set local_S: If S > external_outbound_cst[k_index], must pretend
	# S = external_outbound_cst[k_index], otherwise stage thinks it can promise a
	# longer outbound CST than it really can.
	# Note: external outbound CST defaults to BIG_INT if not provided.
	local_S = min(S, k.external_outbound_cst)

	# Check whether S <= external outbound CST (otherwise this S is infeasible).
	# Note that external outbound CST defaults to BIG_INT if not provided.
	if S <= k.external_outbound_cst:

		# Loop through SI values between max(external inbound CST[k_index],
		# S - T_k) and M_k - T_k.
		# Note that external inbound CST defaults to 0 if not provided.
		lo_SI = max(k.external_inbound_cst, local_S - k.processing_time)
		hi_SI = k.max_replenishment_time - k.processing_time
		for SI in range(lo_SI, hi_SI+1):

			# Calculate c_k(S, SI).
			c_SI[SI], stage_cost, best_upstream_S, best_downstream_SI = \
				_calculate_c(tree, k_index, local_S, SI, theta_in_partial, theta_out_partial)

			# Compare to min.
			if c_SI[SI] < min_c:
				# Remember min cost and value of SI that attained it.
				min_c = c_SI[SI]
				best_cst_adjacent[k_index] = SI
				# Remember values of other CSTs that attained min cost.
				for i in range(np.min(tree.node_indices), k_index):
					if i in k.predecessor_indices():
						best_cst_adjacent[i] = best_upstream_S[i]
					elif i in k.successor_indices():
						best_cst_adjacent[i] = best_downstream_SI[i]

	# Capture theta_out_k_S.
	theta_out_k_S = min_c

	return theta_out_k_S, best_cst_adjacent


def _calculate_theta_in(tree, k_index, SI, theta_in_partial, theta_out_partial):
	"""Calculate the function :math:`\\theta^i_k(SI)` as described in Section 6.3.6.2 of
	|fosct| [function :math:`g_i(SI)` in Section 5 of Graves and Willems
	(2003)].

	Original function is modified in the following ways:
	1. If :math:`SI` is less than the external inbound CST for stage :math:`k`,
	:math:`\\theta^i_k(SI)` is calculated as though :math:`SI` = external inbound CST. (If :math:`k` is a
	source stage, :math:`\\theta^i_k(\\cdot)` will never be calculated [:math:`\\theta^o_k(\\cdot)` will be], but
	:math:`k` might have non-zero external inbound CST even if it is not a source stage.)
	2. The demand bound demand bound over :math:`\\tau` periods is assumed to be of the form
	:math:`z_\\alpha\\sigma\\sqrt{\\tau}`.
	3. When calculating :math:`c_k(S, SI)`, upstream nodes are allowed to use outbound
	CSTs greater than :math:`SI`, and downstream nodes are allowed to use inbound
	CSTs greater than :math:`S`. In effect, this allows multiple inbound/outbound
	CSTs for a single node.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Tree must be pre-processed already.
	k_index : int
		Index of node.
	SI : int
		Inbound committed service time.
	theta_in_partial : dict
		Dict of values of theta_in function that have been calculated so far
		(i.e., for :math:`i < k`).
	theta_out_partial : dict
		Dict of values of theta_out function that have been calculated so far
		(i.e., for :math:`i < k`).

	Returns
	-------
	theta_in_k_SI : float
		The value of :math:`\\theta^i_k(SI)`.
	best_cst_adjacent : dict
		Dict indicating, for each adjacent stage :math:`i` with :math:`i \\le k`, the CST value
		that minimized :math:`\\theta^i_i(\\cdot)` for the optimal value of S.
		* If :math:`i` serves :math:`k`, then ``best_CST_adjacent[i]`` = the value of :math:`S_i` that
		minimizes :math:`\\theta^o_i(S_i)`.
		* If :math:`i` is served by :math:`k`, then ``best_CST_adjacent[i]`` = the value of :math:`SI_i`
		that minimizes :math:`\\theta^i_i(SI_i)`.
		* If :math:`i = k`, then ``best_CST_adjacent[i]`` = the best value of :math:`S` chosen in
		minimization of :math:`theta^i(\\cdot)`.
	"""

	# Get node k_index, for convenience.
	k = tree.nodes_by_index[k_index]

	# Initialize min_c.
	min_c = float('inf')

	# Initialize output dict.
	best_cst_adjacent = {}

	# Initialize dict of c_k(S, SI) values (keys = S values).
	c_S = {}

	# Set local_SI: If SI < external_inbound_cst[k_index], must pretend
	# SI = external_inbound_cst[k_index], otherwise stage thinks it can get a
	# shorter inbound CST than it really can.
	# Note: external inbound CST defaults to 0 if not provided.
	local_SI = max(SI, k.external_inbound_cst)

	# Loop through S values between 0 and min(SI + T_k, external outbound CST[k_index]).
	# Note that external outbound CST defaults to BIG_INT if not provided.
	lo_S = 0
	hi_S = min(local_SI + k.processing_time, k.external_outbound_cst)
	for S in range(lo_S, hi_S+1):

		# Calculate c_k(S, SI).
		c_S[S], stage_cost, best_upstream_S, best_downstream_SI = \
			_calculate_c(tree, k_index, S, local_SI, theta_in_partial, theta_out_partial)

		# Compare to min.
		if c_S[S] < min_c:
			# Remember min cost and value of S that attained it.
			min_c = c_S[S]
			best_cst_adjacent[k_index] = S
			# Remember values of other CSTs that attained min cost.
			for i in range(np.min(tree.node_indices), k_index):
				if i in k.predecessor_indices():
					best_cst_adjacent[i] = best_upstream_S[i]
				elif i in k.successor_indices():
					best_cst_adjacent[i] = best_downstream_SI[i]

	# Capture theta_in_k_SI.
	theta_in_k_SI = min_c

	return theta_in_k_SI, best_cst_adjacent


def _calculate_c(tree, k_index, S, SI, theta_in_partial, theta_out_partial):
	"""Calculate :math:`c_k(S,SI)`, the expected holding cost for :math:`N_k` as function of
	inbound and outbound CSTs at node :math:`k`.

	Assumes demand bound over :math:`\\tau` periods is of the form
	:math:`z_\\alpha\\sigma\\sqrt{\\tau}`.

	Upstream nodes are allowed to use outbound CSTs greater than :math:`SI` and
	downstream nodes are allowed to use inbound CSTs greater than :math:`S`.
	In effect, this allows multiple inbound/outbound CSTs for a single :math:`k`.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Tree must be pre-processed already.
	k_index : int
		Index of node.
	S : int
		Outbound committed service time.
	SI : int
		Inbound committed service time.
	theta_in_partial : dict
		Dict of values of :math:`\\theta^i` function that have been calculated so far
		(i.e., for :math:`i < k`).
	theta_out_partial : dict
		Dict of values of :math:`\\theta^o` function that have been calculated so far
		(i.e., for :math:`i < k`).

	Returns
	-------
	cost : float
		Value of :math:`c_k(S,SI)`.
	stage_cost : float
		Cost to hold inventory at stage :math:`k` (only) given CSTs of :math:`SI` and :math:`S`.
	best_upstream_S : dict
		Dict indicating, for each :math:`i` that is immediately upstream from :math:`k`,
		the best outbound CST for :math:`i` given :math:`k`'s CSTs of :math:`SI` and :math:`S`.
	best_downstream_SI : dict
		Dict indicating, for each :math:`i` that is immediately downstream from :math:`k`,
		the best inbound CST for :math:`i` given :math:`k`'s CSTs of :math:`SI` and :math:`S`.
	"""

	# Get node k, for convenience.
	k = tree.nodes_by_index[k_index]

	# Initialize output dicts.
	best_upstream_S = {}
	best_downstream_SI = {}

	# Calculate safety stock.
	safety_stock = k.demand_bound_constant * \
					k.net_demand_standard_deviation * \
					math.sqrt(SI + k.processing_time - S)

	# Set stage_cost equal to holding cost at node k.
	stage_cost = k.holding_cost * safety_stock

	# Initialize cost to holding cost at node k.
	cost = stage_cost

	# Add theta_out_partial(i) for nodes i that are immediately upstream from k_index
	# and have smaller index. (At this point, theta_out_partial(i) has already been
	# calculated for i < k_index.)
	for i in k.predecessor_indices():
		if i < k_index:
			# Build dict of theta_out_partial(i, S2) values for S2 <= SI.
			theta_out_values = {S2: theta_out_partial[i][S2] for S2 in range(SI + 1)}
			# Find min value and argmin of theta_out_partial(i, S2) where S2 <= SI.
			min_theta_out, best_upstream_S[i] = min_of_dict(theta_out_values)
			# Add min value of theta_out_partial to cost.
			cost += min_theta_out

	# Add theta_in_partial(j) for nodes j that are immediately downstream from k_index
	# and have smaller index. (At this point, theta_in_partial(j) has already been
	# calculated for j < k_index.)
	for j in k.successor_indices():
		if j < k_index:
			# Build dict of theta_in_partial(j, SI2) values for SI2 >= S.
			theta_in_values = {SI2: theta_in_partial[j][SI2] for SI2 in
							   range(S, tree.max_max_replenishment_time + 1)}
			# Find min value and argmin of theta_in_partial(i, SI2) for SI2 >= S.
			min_theta_in, best_downstream_SI[j] = min_of_dict(theta_in_values)
			# Add min value of theta_in_partial to cost.
			cost += min_theta_in

	return cost, stage_cost, best_upstream_S, best_downstream_SI


### GRAPH MANIPULATION ###

def preprocess_tree(tree):
	"""Preprocess the GSM tree. Returns an independent copy.

	If tree is already correctly labeled, does not relabel it.

	Fill node-level attributes: ``net_demand_mean``,
	``net_demand_standard_deviation``, ``larger_adjacent_node``,
	``max_replenishment_time``.

	Fill missing data for ``demand_bound_constant``, ``external_inbound_cst``, and
	``external_outbound_cst attributes``.

	Fill ``max_max_replenishment_time`` network-level attribute.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network. Current node labels are ignored and may be anything.
	start_index : int, optional
		Integer to use as starting (smallest) node label.

	Returns
	-------
	new_tree : |class_network|
		Pre-processed multi-echelon tree network.

	"""

	new_tree = copy.deepcopy(tree)

	# Fill external inbound and outbound CST parameters, if not provided.
	# Default value of external outbound CST = BIG_INT.
	# Default value of external inbound CST = 0. (Not strictly necessary,
	# but cleaner.)
	for k in new_tree.nodes:
		if k.external_inbound_cst is None:
			k.external_inbound_cst = 0
		if k.external_outbound_cst is None:
			k.external_outbound_cst = BIG_INT

	# Fill demand bound constant parameters, if not provided.
	# Set equal to demand bound constant of sink node. If more than one sink node,
	# one is chosen arbitrarily. If no sink nodes have demand bound constant,
	# constant is set to 1.
	sinks_with_dbc = [k for k in new_tree.sink_nodes if k.demand_bound_constant is not None]
	for k in new_tree.nodes:
		if k.demand_bound_constant is None:
			if sinks_with_dbc == []:
				k.demand_bound_constant = 1
			else:
				k.demand_bound_constant = \
					sinks_with_dbc[0].demand_bound_constant

	# Calculate net demand parameters.
	net_demand_means, net_demand_standard_deviations = _net_demand(new_tree)
	for k in new_tree.nodes:
		k.net_demand_mean = net_demand_means[k.index]
		k.net_demand_standard_deviation = net_demand_standard_deviations[k.index]

	# Calculate max replenishment times.
	max_replenishment_times = _longest_paths(new_tree)
	for k in new_tree.nodes:
		k.max_replenishment_time = max_replenishment_times[k.index]

	# Calculate maximum value of max_replenishment_time.
	new_tree.max_max_replenishment_time = \
		np.max([k.max_replenishment_time for k in new_tree.nodes])

	return new_tree


def relabel_nodes(tree, start_index=0, force_relabel=False):
	"""Perform the node-labeling algorithm described in Section 5 of Graves and
	Willems (2000).

	If tree is already correctly labeled, returns the original tree,
	unless ``force_relabel`` is ``True``, in which case performs the relabeling.

	Does not modify the input tree. Fills ``original_label``,
	``larger_adjacent_node``, and ``larger_adjacent_node_is_downstream`` attributes
	of nodes in new tree, whether or not original tree was already
	correctly labeled.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.
		Current node labels are ignored (unless the tree is already correctly
		labeled) and may be anything.
	start_index : int, optional
		Integer to use as starting (smallest) node label.
	force_relabel : bool, optional
		If ``True``, function will relabel nodes even if original tree is correctly
		labeled.

	Returns
	-------
	relabeled_tree : |class_network|
		The relabeled tree network.

	"""

	# Check whether tree is already correctly labeled.
	is_correct = is_correctly_labeled(tree)

	# Do relabel?
	if is_correct and not force_relabel:
		relabeled_tree = copy.deepcopy(tree)
		new_labels = {k.index: k.index for k in tree.nodes}
	else:

		# Initialize all nodes to "unlabeled", and initialize list of new labels.
		labeled = {i.index: False for i in tree.nodes}
		new_labels = {}

		# Find nodes that are adjacent to at most 1 unlabeled node and label them.
		for k_index in range(start_index, start_index+len(tree.nodes)):

			# Find a node for labeling.
			for i in tree.nodes:

				# Make sure i is unlabeled.
				if not labeled[i.index]:
					# Count unlabeled nodes that are adjacent to node i.
					num_adj = len([j for j in i.neighbor_indices if not labeled[j]])

					# If i is adjacent to at most 1 unlabeled node, label it.
					if num_adj <= 1:
						# Change i's label to k_index.
						new_labels[i.index] = k_index
						# Mark i as labeled.
						labeled[i.index] = True
						# Break out of 'for i' loop
						break

		# Relabel the nodes
		relabeled_tree = copy.deepcopy(tree)
		relabeled_tree.reindex_nodes(new_labels)

	# Fill attributes of relabeled tree.
	larger_adjacent, downstream = _find_larger_adjacent_nodes(relabeled_tree)
	for k in tree.nodes:
		relabeled_node = relabeled_tree.nodes_by_index[new_labels[k.index]]
		relabeled_node.original_label = k.index
		if new_labels[k.index] < np.max(list(new_labels.values())):
			relabeled_node.larger_adjacent_node = larger_adjacent[relabeled_node.index]
			relabeled_node.larger_adjacent_node_is_downstream = downstream[relabeled_node.index]
		else:
			# Largest-indexed node has no larger adjacent node.
			relabeled_node.larger_adjacent_node = None
			relabeled_node.larger_adjacent_node_is_downstream = None

	return relabeled_tree


def is_correctly_labeled(tree):
	"""Determine whether tree is already correctly labeled.

	Tree is correctly labeled if all labels are consecutive integers and
	every stage (other than the highest-indexed one) has
	exactly one adjacent stage with a greater index.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.

	Returns
	-------
	``True`` if tree is already correctly labeled.
	"""

	# Get indices.
	ind = tree.node_indices

	# Check whether labels are consecutive integers starting at min_index.
	min_index = np.min(ind)
	try:
		if set(ind) != set(range(min_index, min_index + len(ind))):
			is_correct = False
		else:
			# Check whether every node has exactly one adjacent node with
			# greater index.
			is_correct = True
			for k in tree.nodes:
				if k.index < np.max(ind):
					greater_indexed_neighbors = \
						{i_ind for i_ind in k.predecessor_indices() if i_ind > k.index}.union(
							{i_ind for i_ind in k.successor_indices() if i_ind > k.index}
						)
					if len(greater_indexed_neighbors) != 1:
						is_correct = False
	except:
		is_correct = False

	return is_correct


def _find_larger_adjacent_nodes(tree):
	"""Find larger-indexed adjacent node, for each node in tree.

	After the nodes are relabeled by :func:`relabel_nodes`, each node (except the
	node with the largest index) is adjacent to exactly one node with a
	larger index. Node :math:`k`'s neighbor with larger index is denoted :math:`p(k)` in
	Graves and Willems (2000). This function finds :math:`p(k)` for all :math:`k` and also
	indicates whether :math:`p(k)` is upstream or downstream from :math:`k`.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.
		Nodes are assumed to have been relabeled using :func:`relabel_nodes`.

	Returns
	-------
	larger_adjacent: dict
		Dict containing index of each node's larger-indexed adjacent node,
		for all nodes except the largest-indexed node. Keys are node indices.
	downstream: dict
		Dict containing, for each node, ``True`` if the larger-indexed adjacent
		node is downstream from the node, ``False`` if it is upstream, for all
		nodes except the largest-indexed node. Keys are node indices.
	"""

	# Initialize dicts.
	larger_adjacent = {}
	downstream = {}

	# Loop through nodes.
	for k in tree.nodes:
		if k.index < np.max(tree.node_indices):
			# Get list of nodes that are adjacent to k and have a larger index,
			# but the list will only contain a single item; set larger_adjacent[k_index] to it.
			larger_adjacent_list = [i.index for i in k.neighbors if i.index > k.index]
			larger_adjacent[k.index] = larger_adjacent_list[0]

			# Set downstream flag.
			if larger_adjacent[k.index] in k.successor_indices():
				downstream[k.index] = True
			else:
				downstream[k.index] = False

	return larger_adjacent, downstream


def _longest_paths(tree):
	"""Determine the length of the longest path from any source node to to each
	node :math:`k`.

	Arc lengths are determined by processing times. External inbound CSTs are
	considered source nodes, so having an external inbound CST at node :math:`i` of 5 is
	like having another node that serves node :math:`i` with a processing time of 5.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.
		Nodes are assumed to have been relabeled using :func:`relabel_nodes`.

	Returns
	-------
	longest_lengths : dict
		Dict of longest paths to each node, with keys equal to node indices. [:math:`M_k`].

	"""

	# Build the tree as networkx DiGraph. Set the weight of each edge into a given node k to the processing
	# time of node k. If node k is a source node and/or it has an external inbound CST,
	# add a dummy node before node k and set weight of edge from dummy node to node k
	# equal to processing time of node k + external inbound CST for node k.
	temp_tree = tree.networkx_digraph()
	for k in tree.nodes:
		for p in k.predecessors():
			temp_tree[p.index][k.index]['weight'] = k.processing_time
		if temp_tree.in_degree(k.index) == 0 or (k.external_inbound_cst or 0) > 0:
			temp_tree.add_edge('dummy_' + str(k.index), k.index,
				weight=k.processing_time + (k.external_inbound_cst or 0))

	# Determine shortest path between every pair of nodes.
	# (Really there's only one path, but shortest path is the
	# most straightforward algorithm to use here.)
	path_lengths = dict(nx.shortest_path_length(temp_tree, weight='weight'))

	# Determine longest shortest path to each node k, among all
	# source nodes that are ancestors to k.
	longest_lengths = {}
	for k in tree.nodes:
		longest_lengths[k.index] = max([path_lengths[i][k.index] for i in
								  nx.ancestors(temp_tree, k.index)], default=0)

	return longest_lengths


def _net_demand(tree):
	"""Calculate net demand mean and standard deviation for all nodes in tree.

	Net demand is the demand stream consisting of the external demand for the
	node plus all downstream demand.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.

	Returns
	-------
	net_means : dict
		Dict of net mean for each node.

	net_standard_deviations : dict
		Dict of net standard deviation for each node.

	"""

	# Initialize net_mean and net_variances using each node's external demand.
	net_means = {k.index: k.demand_source.mean or 0 for k in tree.nodes}
	net_variances = {k.index: (k.demand_source.standard_deviation or 0)**2 for k in tree.nodes}

	# Make temp copy of tree.
	temp_tree = copy.deepcopy(tree)

# TODO: add check that the node list gets smaller each iteration -- otherwise there's a bug, but finding it can be hard because of the infinite loop

	# Loop through temp_tree. At each iteration, handle leaf nodes (nodes with
	# no _successors), adding their net_means and net_variances to those of their
	# _predecessors. Then remove the leaf nodes and iterate.
	while len(temp_tree.nodes) > 0:
		leaf_nodes = temp_tree.sink_nodes
		for k in leaf_nodes:
			for i in k.predecessor_indices():
				net_means[i] += net_means[k.index]
				net_variances[i] += net_variances[k.index]
			temp_tree.remove_node(k) 

	net_standard_deviations = {k.index: math.sqrt(net_variances[k.index]) for k in tree.nodes}
	return net_means, net_standard_deviations


def _connected_subgraph_nodes(tree):
	"""Determine nodes connected to :math:`k` in subgraph on :math:`\\{\\min_k,\\ldots,k\\}`, 
	for each :math:`k`, where :math:`\\min_k` is smallest index in graph. [:math:`N_k`]

	"Connected" does not necessarily mean "adjacent."

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.

	Returns
	-------
	connected_nodes : dict
		Dict of set of connected subgraph nodes for each node.

	"""

	# Intiailize output dict.
	connected_nodes = {}

	# Convert to networkx DiGraph so we can use subgraph().
	networkx_tree = tree.networkx_digraph()

	# Loop through nodes.
	for k in networkx_tree:
		# Build subgraph on {min_k,...,k}.
		subgraph = networkx_tree.to_undirected().subgraph(range(np.min(networkx_tree.nodes), k+1))
		# Build set of connected nodes.
		connected_nodes[k] = set(i for i in subgraph.nodes if
							  nx.has_path(subgraph, i, k))

	return connected_nodes


def gsm_to_ssm(tree, p=None):
	"""Convert GSM tree to SSM tree:
	
		- Convert local to echelon holding costs.
		- Convert processing times to lead times.
		- Include stockout cost at demand nodes (if provided).

	Tree must be pre-processed before calling.

	Parameters
	----------
	tree : |class_network|
		The multi-echelon tree network.
	p : float or dict, optional
		Stockout cost to use at demand nodes, or dict indicating stockout cost
		for each demand node. If ``None``, copies ``stockout_cost``
		field from tree for nodes that have it, and does not fill ``stockout_cost``
		for nodes that do not.

	Returns
	-------
	SSM_tree : |class_network|
		SSM representation of tree.
	"""

	# Build new graph.
	SSM_tree = SupplyChainNetwork()

	# Add nodes.
	for n in tree.nodes:
		upstream_h = np.sum([k.local_holding_cost for k in n.predecessors()])
		SSM_tree.add_node(SupplyChainNode(n.index, name=n.name, network=SSM_tree,
			shipment_lead_time=n.processing_time+n.external_inbound_cst,
			echelon_holding_cost=n.local_holding_cost-upstream_h))
		SSM_node = SSM_tree.nodes_by_index[n.index]
		SSM_node.demand_source = copy.deepcopy(n.demand_source)
		if p is not None:
			if n.demand_source is not None:
				if isinstance(p, dict):
					SSM_node.stockout_cost = p[SSM_node.index]
				else:
					SSM_node.stockout_cost = p
		else:
			if n.stockout_cost is not None:
				SSM_node.stockout_cost = n.stockout_cost

	# Add edges.
	edge_list = tree.edges
	SSM_tree.add_edges_from_list(edge_list)

	return SSM_tree


