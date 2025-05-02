# ===============================================================================
# stockpyl - gsm_serial Module
# -------------------------------------------------------------------------------
# Author: Larry Snyder
# License: MIT
# ===============================================================================

"""
.. include:: ../../globals.inc

Overview 
--------

The |mod_gsm_serial| module contains code to implement dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with serial structures by Inderfurth (1991)).

.. note:: |node_stage|

.. note:: |fosct_notation|

.. seealso::

	For an overview of multi-echelon inventory optimization in |sp|,
	see the :ref:`tutorial page for multi-echelon inventory optimization<tutorial_meio_page>`.


References
----------
K. Inderfurth. Safety stock optimization in multistage inventory systems. 
*International Journal of Production Economics*, 24:103-113, 1991.


API Reference
-------------

"""

import networkx as nx
import copy
from stockpyl.demand_source import DemandSource

from stockpyl.gsm_helpers import *
from stockpyl.helpers import *
from stockpyl.supply_chain_network import SupplyChainNetwork, serial_system
from stockpyl.supply_chain_node import SupplyChainNode


### OPTIMIZATION ###

def optimize_committed_service_times(num_nodes=None, local_holding_cost=None, processing_time=None,
								demand_bound_constant=None, external_outbound_cst=None, external_inbound_cst=None,
								demand_mean=None, demand_standard_deviation=None,
								demand_source=None, network=None):
	"""Optimize committed service times using the dynamic programming (DP) algorithm of
	Inderfurth (1991).

	Problem instance may either be provided in the individual parameters ``num_nodes``, ..., ``demand_source``,
	or in the ``network`` parameter.

	If the instance is specified in the individual parameters, the nodes must be indexed :math:`N, \\ldots, 1`. 
	(If the instance is specified in the ``network`` parameter, the nodes may be indexed in any way.) The node-specific
	parameters (``local_holding_cost``, ``processing_time``, and ``demand_bound_constant``) must be either 
	a dict, a list, or a singleton, with the following requirements:
	
	* If the parameter is a dict, its keys must equal 1,..., ``num_nodes``,
	  each corresponding to a node index.
	* If the parameter is a list, it must have length ``num_nodes``;
	  the ``n`` th entry in the list corresponds to node with index ``n`` + 1.
	* If the parameter is a singleton, all nodes will have that parameter set to the
	  singleton value.

	Either ``demand_mean`` and ``demand_standard_deviation`` must be
	provided (in which case the demand will be assumed to be normally distributed)
	or a ``demand_source`` must be provided.

	Parameters
	----------
	num_nodes : int, optional
		Number of nodes in serial system. [:math:`N`]
	local_holding_cost : float, list, or dict, optional
		Local holding cost at each node. [:math:`h`]
	processing_time : float, list, or dict, optional
		Processing time at each node. [:math:`T`]
	demand_bound_constant : float, optional
		The constant to use in setting the demand bound. [:math:`z_\\alpha`]
	external_outbound_cst : int, optional
		Outbound CST to external customer at node 1.
	external_inbound_cst : int, optional
		Inbound CST from external supplier at node N.
	demand_mean : float, optional
		Mean demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_standard_deviation : float, optional
		Standard deviation of demand per unit time at node 1. Ignored if ``demand_source`` is not ``None``. [:math:`\\mu`]
	demand_source : |class_demand_source|, optional
		A DemandSource object describing the demand distribution at node 1. Required if
		``demand_mean`` and ``demand_standard_deviation`` are ``None``.
	network : |class_network|, optional
		A SupplyChainNetwork object that provides all of the necessary data. If provided,
		``num_nodes``, ..., ``demand_source`` are ignored.

	Returns
	-------
	opt_cst : dict
		Dict of optimal CSTs, with node indices as keys and CSTs as values.
	opt_cost : float
		Optimal expected cost of system.


	**Example** (Example 6.3):

	.. testsetup:: *

		from stockpyl.gsm_serial import *

	.. doctest::

		>>> from stockpyl.instances import load_instance
		>>> network = load_instance("example_6_3")
		>>> opt_cst, opt_cost = optimize_committed_service_times(network=network)
		>>> opt_cst
		{3: 0, 2: 0, 1: 1}
		>>> opt_cost
		2.8284271247461903

	References
	----------
	K. Inderfurth. Safety stock optimization in multistage inventory systems. 
	*International Journal of Production Economics*, 24:103-113, 1991.
	"""

	# Check for presence of data.
	if network is None and (num_nodes is None or local_holding_cost is None or \
		processing_time is None or demand_bound_constant is None or external_outbound_cst is None or \
		external_inbound_cst is None or \
		((demand_mean is None or demand_standard_deviation is None) and demand_source is None)):
		raise ValueError("You must provide either network or num_nodes, ..., demand_bound_constant")

	# Convert parameters to network, if parameters provided.
	if network:
		network = copy.deepcopy(network)
	else:

		# Build network.
		network = SupplyChainNetwork()

		# Build nodes.
		for n in range(1, num_nodes + 1):
			node = SupplyChainNode(
				index=n,
				network=network,
				local_holding_cost=ensure_dict_for_nodes(local_holding_cost, node_indices=list(range(1, num_nodes+1)))[n],
				processing_time=ensure_dict_for_nodes(processing_time, node_indices=list(range(1, num_nodes+1)))[n],
				demand_bound_constant=ensure_dict_for_nodes(demand_bound_constant, node_indices=list(range(1, num_nodes+1)))[n]
			)
			if n == 1:
				# Add demand information.
				if demand_source is None:
					node.demand_source = DemandSource(
						type='N', 
						mean=demand_mean,
						standard_deviation=demand_standard_deviation
					)
				else:
					node.demand_source = demand_source
				# Add external outbound CST.
				node.external_outbound_cst = external_outbound_cst
			if n == num_nodes:
				# Add external inbound CST.
				node.external_inbound_cst = external_inbound_cst

			network.add_node(node)

		# Add edges.
		network.add_edges_from_list([(n + 1, n) for n in range(1, num_nodes)])
		
	# Solve.
	opt_cst, opt_cost = _cst_dp_serial(network)

	return opt_cst, opt_cost


def _cst_dp_serial(network):
	"""Optimize committed service times for serial system.

	Optimization is performed using the dynamic programming (DP) algorithm of
	Inderfurth (1991).

	Assumes demand bound over tau periods is of the form
	:math:`z_\\alpha\\sigma\\sqrt{\\tau}`.

	Parameters
	----------
	network : |class_network|
		The multi-echelon serial network. 

	Returns
	-------
	opt_cst : dict
		Dict of optimal CSTs, with node indices as keys and CSTs as values.
	opt_cost : float
		Optimal expected cost of system.

	"""

	# Initialize dicts to store values of theta(.) function. 
	theta = {k_index: {} for k_index in network.node_indices}

	# Get number of nodes (for convenience).
	num_nodes = len(network.nodes)

	# Calculate max replenishment times (max replenishment time for node k = SI_N + sum
	# of processing times at nodes k, ..., N).
	for k_index in range(num_nodes, 0, -1):
		k = network.nodes_by_index[k_index]
		if k_index == num_nodes:
			k.max_replenishment_time = k.external_inbound_cst + k.processing_time
		else:
			upstream = network.nodes_by_index[k_index + 1]
			k.max_replenishment_time = upstream.max_replenishment_time + k.processing_time

	# Initialize best_cst_adjacent.
	# best_cst_adjacent[k_index][S][i] = CST chosen for stage i when calculating
	# theta(SI) for stage k.
#	best_cst_adjacent = {k.index: {S: {} for S in
#		range(k.max_replenishment_time+1)} for k in network.nodes}

	# Initialize best_S.
	# best_S[k_index][SI] = S that minimizes (6.44) for node k and SI.
	best_S = {k_index: {} for k_index in network.node_indices}

	# Get shortcuts to some parameters (for conveience).
	sigma = network.nodes_by_index[1].demand_source.standard_deviation

	# Loop through stages.
	for k_index in range(1, num_nodes + 1):

		# Get shortcuts to node (for convenience).
		k = network.nodes_by_index[k_index]

		# Determine range of SI values to check. (For node N, it's only external_inbound_cst;
		# for all other nodes, it's 0, ..., max_replenishment_time - T.)
		if k_index == num_nodes:
			SI_range = [k.external_inbound_cst]
		else:
			SI_range = list(range(k.max_replenishment_time - k.processing_time + 1))

		# Evaluate theta(k_index, SI).
		for SI in SI_range:
			if k_index == 1:

				# Calculate theta(1, SI) using (6.43). Ensure argument to sqrt is non-negative
				# (could be negative if S > T, in which case just treat NLT as 0).
				theta[k_index][SI] = k.local_holding_cost * k.demand_bound_constant \
					* sigma * math.sqrt(max(0, SI + k.processing_time - k.external_outbound_cst))
				best_S[k_index][SI] = k.external_outbound_cst

			else:

				# Calculate theta(k, SI) using (6.43).
				min_cost = float('inf')
				for S in range(SI + k.processing_time + 1):
					# Calculate cost for this S.
					cost = k.local_holding_cost * k.demand_bound_constant \
						* sigma * math.sqrt(SI + k.processing_time - S) \
						+ theta[k_index-1][S]
					# Compare to best.
					if cost < min_cost:
						min_cost = cost
						min_S = S
				
				# Fill theta and best_cst_adjacent.
				theta[k_index][SI] = min_cost
				best_S[k_index][SI] = min_S

			# Set values of theta_in and best_cst_adjacent for
			# max_replenishment_time+1 to max_max_replenishment_time to
			# theta_in(max_replenishment_time - processing_time).
			# Needed so that stages with larger max_replenishment_time don't
			# encounter undefined values of theta_in.
			# for SI in range(max_replen_time - proc_time + 1,
			# 				tree.max_max_replenishment_time + 1):
			# 	theta_in[k_index][SI] = theta_in[k_index][max_replen_time - proc_time]
			# 	best_cst_adjacent[k_index][SI] = \
			# 		best_cst_adjacent[k_index][max_replen_time - proc_time]

	# Initialize dict of optimal CSTs.
	opt_cst = {}

	# Backtrack to find optimal CSTs.
	for k_index in range(num_nodes, 0, -1):

		# Get node k.
		k = network.nodes_by_index[k_index]

		# Determine SI.
		if k_index == num_nodes:
			SI = k.external_inbound_cst
		else:
			SI = opt_cst[k_index+1]

		# Get best S for this SI.
		opt_cst[k_index] = best_S[k_index][SI]

	# Get optimal cost.
	opt_cost = theta[num_nodes][network.nodes_by_index[num_nodes].external_inbound_cst]

	return opt_cst, opt_cost

