# ===============================================================================
# stockpyl - gsm_tree Module
# -------------------------------------------------------------------------------
# Version: 0.0.0
# Updated: 01-30-2022
# Author: Larry Snyder
# License: GPLv3
# ===============================================================================

"""Code to implement dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2000).

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the GSM instance.

The following attributes are used to specify input data:
	* Node-level attributes
		- processing_time [T]
		- external_inbound_cst [si]
		- external_outbound_cst [s]
		- holding_cost [h]
		- demand_bound_constant [z_alpha]
		- external_demand_mean [mu]
		- external_demand_standard_deviation [sigma]
	* Edge-level attributes
		- units_required (e.g., on edge i->j, units_required units of item i are
	required to make 1 unit of item j)

The following attributes are used to store outputs and intermediate values:
	* Graph-level attributes
		- max_max_replenishment_time
	* Node-level attributes:
		- original_label
		- net_demand_standard_deviation (standard deviation of combined demand
		stream consisting of external demand and downstream demand)
		- larger_adjacent_node [p]
		- larger_adjacent_node_is_downstream
		- max_replenishment_time [M]

(c) Lawrence V. Snyder
Lehigh University

"""

import networkx as nx

from stockpyl.gsm_tree_helpers import *
from stockpyl.helpers import *

# TODO: add instances to instance JSON

### GRAPH MANIPULATION ###

def preprocess_tree(tree):
	"""Preprocess the GSM tree. Returns an independent copy.

	If tree is already correctly labeled, does not relabel it.

	Fill node-level attributes: original_label, net_demand_mean,
	net_demand_standard_deviation, larger_adjacent_node,
	max_replenishment_time.
	Fill missing data for demand_bound_constant, external_inbound_cst, and
	external_outbound_cst attributes.

	Fill max_max_replenishment_time graph-level attribute.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored and may be anything.
	start_index : int, optional
		Integer to use as starting (smallest) node label.

	Returns
	-------
	new_tree : graph
		Pre-processed multi-echelon tree network.

	"""

	new_tree = tree.copy()

	# Fill external inbound and outbound CST parameters, if not provided.
	# Default value of external outbound CST = BIG_INT.
	# Default value of external inbound CST = 0. (Not strictly necessary,
	# but cleaner.)
	for k in new_tree.nodes:
		if 'external_inbound_cst' not in new_tree.nodes[k]:
			new_tree.nodes[k]['external_inbound_cst'] = 0
		if 'external_outbound_cst' not in new_tree.nodes[k]:
			new_tree.nodes[k]['external_outbound_cst'] = BIG_INT

	# Fill demand bound constant parameters, if not provided.
	# Set equal to demand bound constant of sink node. If more than one sink node,
	# one is chosen arbitrarily. If no sink nodes have demand bound constant,
	# constant is set to 1.
	sinks_with_dbc = [k for k in new_tree.nodes if new_tree.out_degree(k) == 0
					  and 'demand_bound_constant' in new_tree.nodes[k]]
	for k in new_tree.nodes:
		if 'demand_bound_constant' not in new_tree.nodes[k]:
			if sinks_with_dbc == []:
				new_tree.nodes[k]['demand_bound_constant'] = 1
			else:
				new_tree.nodes[k]['demand_bound_constant'] = \
					new_tree.nodes[sinks_with_dbc[0]]['demand_bound_constant']

	# Calculate net demand parameters.
	net_demand_means, net_demand_standard_deviations = net_demand(new_tree)
	nx.set_node_attributes(new_tree, net_demand_means, 'net_demand_mean')
	nx.set_node_attributes(new_tree, net_demand_standard_deviations,
						   'net_demand_standard_deviation')

	# Calculate max replenishment times.
	max_replenishment_times = longest_paths(new_tree)
	nx.set_node_attributes(new_tree, max_replenishment_times, 'max_replenishment_time')

	# Calculate maximum value of max_replenishment_time.
	new_tree.graph['max_max_replenishment_time'] = \
		np.max(list(nx.get_node_attributes(new_tree,
										   'max_replenishment_time').values()))

	return new_tree


def relabel_nodes(tree, start_index=0, force_relabel=False):
	"""Perform the node-labeling algorithm described in Section 5 of Graves and
	Willems (2000).

	If tree is already correctly labeled, returns the original tree,
	unless force_relabel is True, in which case performs the relabeling.

	Does not modify the input tree. Fills 'original_label',
	'larger_adjacent_node', and 'larger_adjacent_node_is_downstream' attributes
	of nodes in new tree, whether or not original tree was already
	correctly labeled.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored (unless the tree is already correctly
		labeled) and may be anything.
	start_index : int, optional
		Integer to use as starting (smallest) node label.
	force_relabel : bool, optional
		If True, function will relabel nodes even if original tree is correctly
		labeled.

	Returns
	-------
	relabeled_tree : graph
		NetworkX directed graph representing the relabeled tree network.

	"""

	# Check whether tree is already correctly labeled.
	is_correct = is_correctly_labeled(tree)

	# Do relabel?
	if is_correct and not force_relabel:
		relabeled_tree = tree.copy()
		new_labels = {k: k for k in tree.nodes}
	else:

		# Initialize all nodes to "unlabeled", and initialize list of new labels.
		labeled = {i: False for i in tree.nodes()}
		new_labels = {}

		# Find nodes that are adjacent to at most 1 unlabeled node and label them.
		for k in range(start_index, start_index+nx.number_of_nodes(tree)):

			# Find a node for labeling.
			for i in tree.nodes():

				# Make sure i is unlabeled.
				if not labeled[i]:
					# Count unlabeled nodes that are adjacent to node i.
					num_adj = len([j for j in nx.all_neighbors(tree, i) if not labeled[j]])

					# If i is adjacent to at most 1 unlabeled node, label it.
					if num_adj <= 1:
						# Change i's label to k.
						new_labels[i] = k
						# Mark i as labeled.
						labeled[i] = True
						# Break out of 'for i' loop
						break

		# Relabel the nodes
		relabeled_tree = nx.relabel_nodes(tree, new_labels)

	# Fill original_label attribute of relabeled tree.
	original_labels = {new_labels[k]: k for k in tree.nodes}
	nx.set_node_attributes(relabeled_tree, original_labels, 'original_label')

	# Fill larger-adjacent-node attributes.
	larger_adjacent, downstream = find_larger_adjacent_nodes(relabeled_tree)
	nx.set_node_attributes(relabeled_tree, larger_adjacent, 'larger_adjacent_node')
	nx.set_node_attributes(relabeled_tree, downstream, 'larger_adjacent_node_is_downstream')

	return relabeled_tree


def is_correctly_labeled(tree):
	"""Determine whether tree is already correctly labeled.

	Tree is correctly labeled if all labels are integers, the integers are
	consecutive, and every stage (other than the highest-indexed one) has
	exactly one adjacent stage with a greater index.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.

	Returns
	-------
	True if tree is already correctly labeled.
	"""

	# Get indices.
	ind = list(tree.nodes)

	# Check whether every label is a non-negative integer.
	if not np.all([str(k).isdigit() for k in ind]):
		is_correct = False
	else:
		# Check whether labels are consecutive integers starting at min_index.
		min_index = np.min(ind)
		if set(ind) != set(range(min_index, min_index + len(ind))):
			is_correct = False
		else:
			# Check whether every node as exactly one adjacent stage with
			# greater index.
			is_correct = True
			for k in tree.nodes:
				if k < np.max(ind):
					greater_indexed_neighbors = \
						{i for i in tree.predecessors(k) if i > k}.union(
							{i for i in tree.successors(k) if i > k}
						)
					if len(greater_indexed_neighbors) != 1:
						is_correct = False

	return is_correct


def find_larger_adjacent_nodes(tree):
	"""Find larger-indexed adjacent node, for each node in tree.

	After the nodes are relabeled by relabel_nodes(), each node (except the
	node with the largest index) is adjacent to exactly one node with a
	larger index. Node k's neighbor with larger index is denoted p(k) in
	Graves and Willems (2000). This function finds p(k) for all k and also
	indicates whether p(k) is upstream or downstream from k.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Nodes are assumed to have been relabeled using relabel_nodes().

	Returns
	-------
	larger_adjacent: dict
		Dict containing index of each node's larger-indexed adjacent node,
		for all nodes except the largest-indexed node.
	downstream: dict
		Dict containing, for each node, True if the larger-indexed adjacent
		node is downstream from the node, False if it is upstream, for all
		nodes except the largest-indexed node.
	"""

	# Initialize dicts.
	larger_adjacent = {}
	downstream = {}

	# Loop through nodes.
	for k in tree.nodes:
		if k < np.max(list(tree.nodes)):
			# Get list of nodes that are adjacent to k and have a larger index,
			# but the list will only contain a single item; set larger_adjacent[k] to it.
			larger_adjacent_list = [i for i in nx.all_neighbors(tree, k) if i > k]
			larger_adjacent[k] = larger_adjacent_list[0]

			# Set downstream flag.
			if larger_adjacent[k] in tree.successors(k):
				downstream[k] = True
			else:
				downstream[k] = False

	return larger_adjacent, downstream


def longest_paths(tree):
	"""Determine the length of the longest path from any source node to to each
	node k.

	Arc lengths are determined by processing times. External inbound CSTs are
	considered source nodes, so having an external inbound CST at node i of 5 is
	like having another node that serves node i with a processing time of 5.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Nodes are assumed to have been relabeled using relabel_nodes().

	Returns
	-------
	longest_lengths : dict
		Dict of longest paths to each node (M_k).

	"""

	# Get dict of external inbound CSTs. (Some nodes may have no entry.)
	external_inbound_cst = nx.get_node_attributes(tree, 'external_inbound_cst')

	# Copy the tree. Set the weight of each edge into a given node k to the processing
	# time of node k. If node k is a source node and/or it has an external inbound CST,
	# add a dummy node before node k and set weight of edge from dummy node to node k
	# equal to processing time of node k + external inbound CST for node k.
	temp_tree = tree.copy()
	for k in tree.nodes:
		for p in tree.predecessors(k):
			temp_tree[p][k]['weight'] = tree.nodes[k]['processing_time']
		if tree.in_degree(k) == 0 or external_inbound_cst.get(k, 0) > 0:
			temp_tree.add_edge('dummy_' + str(k), k,
							   weight=tree.nodes[k]['processing_time'] + external_inbound_cst.get(k, 0))

	# Determine shortest path between every pair of nodes.
	# (Really there's only one path, but shortest path is the
	# most straightforward algorithm to use here.)
	path_lengths = dict(nx.shortest_path_length(temp_tree, weight='weight'))

	# Determine longest shortest path to each node k, among all
	# source nodes that are ancestors to k.
	longest_lengths = {}
	for k in tree.nodes:
		longest_lengths[k] = max([path_lengths[i][k] for i in
								  nx.ancestors(temp_tree, k)], default=0)

	return longest_lengths


def net_demand(tree):
	"""Calculate net demand mean and standard deviation for all nodes in tree.

	Net demand is the demand stream consisting of the external demand for the
	node plus all downstream demand.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.

	Returns
	-------
	net_means : dict
		Dict of net mean for each node.

	net_standard_deviations : dict
		Dict of net standard deviation for each node.

	"""

	# Initialize net_mean and net_variances using each node's external demand.
	net_means = {k: tree.nodes[k].get('external_demand_mean', 0) for k in
				tree.nodes}
	net_variances = {k: tree.nodes[k].get('external_demand_standard_deviation', 0)**2
				for k in tree.nodes}

	# Make temp copy of tree.
	temp_tree = tree.copy()

	# Loop through temp_tree. At each iteration, handle leaf nodes (nodes with
	# no _successors), adding their net_means and net_variances to those of their
	# _predecessors. Then remove the leaf nodes and iterate.
	while temp_tree.number_of_nodes() > 0:
		leaf_nodes = [k for k in temp_tree.nodes if temp_tree.out_degree(k) == 0]
		for k in leaf_nodes:
			for i in temp_tree.predecessors(k):
				net_means[i] += net_means[k]
				net_variances[i] += net_variances[k]
			temp_tree.remove_node(k)

	net_standard_deviations = {k: np.sqrt(net_variances[k]) for k in tree.nodes}
	return net_means, net_standard_deviations


def connected_subgraph_nodes(tree):
	"""Determine nodes connected to k in subgraph on {min_k,...,k}, for each k,
	where min_k is smallest index in graph. [N_k]

	Connected does not necessarily mean adjacent.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.

	Returns
	-------
	connected_nodes : dict
		Dict of set of connected subgraph nodes for each node.

	"""

	# Intiailize output dict.
	connected_nodes = {}

	# Loop through nodes.
	for k in tree.nodes:
		# Build subgraph on {min_k,...,k}.
		subgraph = tree.to_undirected().subgraph(range(np.min(tree.nodes), k+1))
		# Build set of connected nodes.
		connected_nodes[k] = set(i for i in subgraph.nodes if
							  nx.has_path(subgraph, i, k))

	return connected_nodes


def GSM_to_SSM(tree, p=None):
	"""Convert GSM tree to SSM tree:
		- Convert local to echelon holding costs.
		- Convert processing times to lead times.
		- Include stockout cost at demand nodes (if provided).

	Tree must be pre-processed before calling.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
	p : float, optional
		Stockout cost to use at demand nodes. If None, copies stockout_cost
		field from tree for nodes that have it, and does not fill stockout_cost
		for nodes that do not.
		# TODO: allow different p values at different demand nodes

	Returns
	-------
	SSM_tree : graph
		SSM representation of tree.
	"""

	# Build new graph.
	SSM_tree = nx.DiGraph()

	# Add nodes.
	for n in tree.nodes:
		upstream_h = np.sum([tree.nodes[k]['holding_cost'] for k in
							 tree.predecessors(n)])
		SSM_tree.add_node(n,
			lead_time=tree.nodes[n]['processing_time']+tree.nodes[n]['external_inbound_cst'],
			echelon_holding_cost=tree.nodes[n]['holding_cost'] - upstream_h)
		if 'external_demand_mean' in tree.nodes[n]:
			SSM_tree.nodes[n]['mean'] = \
				tree.nodes[n]['external_demand_mean']
		if 'external_demand_standard_deviation' in tree.nodes[n]:
			SSM_tree.nodes[n]['standard_deviation'] = \
				tree.nodes[n]['external_demand_standard_deviation']
		if p is not None:
			if tree.nodes[n]['external_demand_mean'] > 0 or \
				tree.nodes[n]['external_demand_standard_deviation'] > 0:
				SSM_tree.nodes[n]['stockout_cost'] = p
		else:
			if 'stockout_cost' in tree.nodes[n]:
				SSM_tree.nodes[n]['stockout_cost'] = tree.nodes[n]['stockout_cost']

	# Add edges.
	SSM_tree.add_edges_from(tree.edges)

	return SSM_tree


### OPTIMIZATION ###

def optimize_committed_service_times(tree):
	"""Optimize committed service times.

	Optimization is performed using the dynamic programming (DP) algorithm of
	Graves and Willems (2000).

	tree is the DiGraph containing the instance. The tree must already have been
	pre-processed using preprocess_tree(), but it need not have had its nodes
	relabeled using relabel_nodes().

	Output parameters are expressed using the original labeling of tree.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored and may be anything.

	Returns
	-------
	opt_cost : float
		Optimal expected cost of system.
	opt_cst : dict
		Dict of optimal CSTs.

	"""

	# Relabel nodes.
	tree = relabel_nodes(tree)

	# Solve.
	opt_cost, opt_cst_relabeled = cst_dp(tree)

	# Prepare optimal solution in terms of original labels.
	opt_cst = {tree.nodes[k]['original_label']: opt_cst_relabeled[k]
			   for k in tree.nodes}

	return opt_cost, opt_cst


def cst_dp(tree):
	"""Optimize committed service times on pre-processed tree.

	Optimization is performed using the dynamic programming (DP) algorithm of
	Graves and Willems (2000).

	tree is the DiGraph containing the instance. It must be pre-processed
	before calling this function.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored and may be anything.

	Returns
	-------
	opt_cost : float
		Optimal expected cost of system.
	opt_cst : dict
		Dict of optimal CSTs.

	"""


	# Initialize dicts to store values of theta_in(.) and theta_out(.) functions
	# (called f(.) and g(.) in Graves and Willems).
	theta_in = {k: {} for k in tree.nodes}
	theta_out = {k: {} for k in tree.nodes}

	# Get min and max node indices (for convenience).
	min_k = np.min(list(tree.nodes))
	max_k = np.max(list(tree.nodes))

	# Initialize best_cst_adjacent.
	# best_cst_adjacent[k][S][i] = CST chosen for stage i when calculating
	# theta_out(S) or theta_in(SI) for stage k.
	best_cst_adjacent = {k: {S: {} for S in
		range(tree.nodes[k]['max_replenishment_time']+1)} for k in tree.nodes}

	# Loop through stages.
	for k in range(min_k, max_k + 1):

		# Get shortcuts to some parameters (for convenience).
		max_replen_time = tree.nodes[k]['max_replenishment_time']
		proc_time = tree.nodes[k]['processing_time']

		# Evaluate theta_out(k, S) if p(k) is downstream from k and
		# and k < final k, evaluate theta_in(k, SI) otherwise.
		if k < max_k and tree.nodes[k]['larger_adjacent_node_is_downstream']:

			# p(k) is downstream from k -- evaluate theta_out(k, S).
			for S in range(max_replen_time+1):
				# Calculate theta_out.
				theta_out[k][S], temp_best_cst_adjacent = \
					calculate_theta_out(tree, k, S, theta_in, theta_out)
				# Copy temp_best_cst_adjacent to best_cst_adjacent.
				best_cst_adjacent[k][S] = {i: temp_best_cst_adjacent[i]
										   for i in temp_best_cst_adjacent}

			# Set values of theta_out and best_cst_adjacent for
			# max_replenishment_time+1 to max_max_replenishment_time to
			# theta_out(max_replenishment_time).
			# Needed so that stages with larger max_replenishment_time don't
			# encounter undefined values of theta_out.
			for S in range(max_replen_time+1,
						   tree.graph['max_max_replenishment_time'] + 1):
				theta_out[k][S] = theta_out[k][max_replen_time]
				best_cst_adjacent[k][S] = best_cst_adjacent[k][max_replen_time]

		else:

			# p(k) is upstream from k -- evaluate theta_in(k, SI).
			for SI in range(max_replen_time - proc_time + 1):
				# Calculate theta_in.
				theta_in[k][SI], temp_best_cst_adjacent = \
					calculate_theta_in(tree, k, SI, theta_in, theta_out)
				# Copy temp_best_cst_adjacent to best_cst_adjacent.
				best_cst_adjacent[k][SI] = {i: temp_best_cst_adjacent[i]
											for i in temp_best_cst_adjacent}

			# Set values of theta_in and best_cst_adjacent for
			# max_replenishment_time+1 to max_max_replenishment_time to
			# theta_in(max_replenishment_time - processing_time).
			# Needed so that stages with larger max_replenishment_time don't
			# encounter undefined values of theta_in.
			for SI in range(max_replen_time - proc_time + 1,
							tree.graph['max_max_replenishment_time'] + 1):
				theta_in[k][SI] = theta_in[k][max_replen_time - proc_time]
				best_cst_adjacent[k][SI] = \
					best_cst_adjacent[k][max_replen_time - proc_time]

	# Determine best value of SI for final stage.
	SI_dict = {SI: theta_in[max_k][SI] for SI in
			   range(tree.nodes[max_k]['max_replenishment_time'] -
					 tree.nodes[max_k]['processing_time'] + 1)} # smaller range of SI
	best_theta_in, best_SI = min_of_dict(SI_dict)

	# Initialize dict of optimal CSTs and optimal inbound CSTs.
	opt_cst = {}
	opt_in_cst = {}

	# Backtrack to find optimal CSTs: Loop backwards through stages k;
	# if p(k) is downstream from k, then set k's outbound CST to p(k)'s
	# optimal inbound CST (which we get from best_cst_adjacent[p(k)][CST(p(k))]);
	# if p(k) is upstream from k, then set k's inbound CST to p(k)'s optimal
	# outbound CST and set k's outbound CST to the optimal for that inbound
	# CST (from best_cst_adjacent[p(k)][CST(p(k))]).
	# For each stage, remember optimal outbound _and_ inbound CSTs.
	for k in range(max_k, min_k-1, -1):

		# Get p(k), and determine whether p(k) and p(p(k)) are upstream or
		# downstream (for convenience).
		if k < max_k:
			pk = tree.nodes[k]['larger_adjacent_node']
			pk_is_downstream = tree.nodes[k]['larger_adjacent_node_is_downstream']
			if pk < max_k:
				ppk_is_downstream = tree.nodes[pk]['larger_adjacent_node_is_downstream']

		# Where is p(k)?
		if k == max_k:
			# This is final stage.
			opt_cst[k] = best_cst_adjacent[k][best_SI][k]
			opt_in_cst[k] = best_SI
		elif pk_is_downstream:
			# p(k) is downstream from k. Is p(p(k)) upstream or downstream from p(k)?
			if pk != max_k and ppk_is_downstream:
				# p(p(k)) is downstream from p(k) -- that means that optimal
				# CST values are stored in best_cst_adjacent[pk][opt_cst[pk]][.].
				opt_cst[k] = best_cst_adjacent[pk][opt_cst[pk]][k]
			else:
				# p(p(k)) is upstream from p(k) (or it's the final node) --
				# that means that optimal CST values are stored in
				# best_cst_adjacent[pk][opt_in_cst[ppk]][.].
				# TODO: best_cst_adjacent[pk][opt_in_cst[pk]][.] ???
				opt_cst[k] = best_cst_adjacent[pk][opt_in_cst[pk]][k]
			opt_in_cst[k] = best_cst_adjacent[k][opt_cst[k]][k]
		else:
			# p(k) is upstream from k. Is p(p(k)) upstream or downstream from p(k)?
			if pk != max_k and ppk_is_downstream:
				# p(p(k)) is downstream from p(k) -- that means that optimal
				# inbound CST values are stored in
				# best_cst_adjacent[pk][opt_cst[pk]][.].
				opt_in_cst[k] = best_cst_adjacent[pk][opt_cst[pk]][k]
			else:
				# p(p(k)) is upstream from p(k) (or it's the final node) --
				# that means that optimal inbound CST values are stored in
				# best_cst_adjacent[pk][opt_in_cst[pk]][.].
				opt_in_cst[k] = best_cst_adjacent[pk][opt_in_cst[pk]][k]
			opt_cst[k] = best_cst_adjacent[k][opt_in_cst[k]][k]

		# If outbound CST for k is greater than k's external outbound CST,
		# reset it.
		opt_cst[k] = min(opt_cst[k], tree.nodes[k]['external_outbound_cst'])

	# Get optimal cost.
	opt_cost = best_theta_in

	return opt_cost, opt_cst


def calculate_theta_out(tree, k, S, theta_in_partial, theta_out_partial):
	"""Calculate the function theta_out(k, S) as described in Section 6.3.6.2 of
	Snyder and Shen (2019) [function f_i(S) in Section 5 of Graves and Willems
	(2003)].

	Original function is modified in the following ways:
	1. If S is greater than the external outbound CST for stage k,
	theta_out(k, S) is calculated as though S = external outbound CST. (If k is a sink
	stage, theta_out(k,.) will never be calculated [theta_in(k,.) will be], but
	k might have non-zero external outbound CST even if it is not a sink stage.)
	2. The range of values of SI for which c_k(S,SI) is evaluated begins at
	max(external_inbound_cst, S - T_k), not max(0, S - T_k).
	3. The demand bound demand bound over tau periods is assumed to be of the form
	z_alpha * sigma * sqrt(tau).
	4. When calculating c_k(S, SI), upstream nodes are allowed to use outbound
	CSTs greater than SI, and downstream nodes are allowed to use inbound
	CSTs greater than S. In effect, this allows multiple inbound/outbound
	CSTs for a single nodes.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Tree must be pre-processed already.
	k : int
		Index of node.
	S : int
		Outbound committed service time.
	theta_in_partial : dict
		Dict of values of theta_in function that have been calculated so far
		(i.e., for i < k).
	theta_out_partial : dict
		Dict of values of theta_out function that have been calculated so far
		(i.e., for i < k).

	Returns
	-------
	theta_out_k_S : float
		The value of theta_out(k, S).
	best_cst_adjacent : dict
		Dict indicating, for each adjacent stage i with i <= k, the CST value
		that minimized theta_out(.) for the optimal value of SI.
		* If i serves k, then best_CST_adjacent[i] = the value of S_i that
		minimizes theta_out(i, S_i).
		* If i is served by k, then best_CST_adjacent[i] = the value of SI_i
		that minimizes theta_in(i, SI_i).
		* If i = k, then best_CST_adjacent[i] = the best value of SI chosen in
		minimization of theta_out(.).
	"""

	# Get node k, for convenience.
	node_k = tree.nodes[k]

	# Initialize min_c.
	min_c = float('inf')

	# Initialize output dict.
	best_cst_adjacent = {}

	# Initialize dict of c_k(S, SI) values (keys = SI values).
	c_SI = {}

	# Set local_S: If S > external_outbound_cst[k], must pretend
	# S = external_outbound_cst[k], otherwise stage thinks it can promise a
	# longer outbound CST than it really can.
	# Note: external outbound CST defaults to BIG_INT if not provided.
	local_S = min(S, node_k['external_outbound_cst'])

	# Check whether S <= external outbound CST (otherwise this S is infeasible).
	# Note that external outbound CST defaults to BIG_INT if not provided.
	if S <= node_k['external_outbound_cst']:

		# Loop through SI values between max(external inbound CST[k],
		# S - T_k) and M_k - T_k.
		# Note that external inbound CST defaults to 0 if not provided.
		lo_SI = max(node_k['external_inbound_cst'],
					local_S - node_k['processing_time'])
		hi_SI = node_k['max_replenishment_time'] - node_k['processing_time']
		for SI in range(lo_SI, hi_SI+1):

			# Calculate c_k(S, SI).
			c_SI[SI], stage_cost, best_upstream_S, best_downstream_SI = \
				calculate_c(tree, k, local_S, SI, theta_in_partial, theta_out_partial)

			# Compare to min.
			if c_SI[SI] < min_c:
				# Remember min cost and value of SI that attained it.
				min_c = c_SI[SI]
				best_cst_adjacent[k] = SI
				# Remember values of other CSTs that attained min cost.
				for i in range(np.min(tree.nodes), k):
					if i in tree.predecessors(k):
						best_cst_adjacent[i] = best_upstream_S[i]
					elif i in tree.successors(k):
						best_cst_adjacent[i] = best_downstream_SI[i]

	# Capture theta_out_k_S.
	theta_out_k_S = min_c

	return theta_out_k_S, best_cst_adjacent


def calculate_theta_in(tree, k, SI, theta_in_partial, theta_out_partial):
	"""Calculate the function theta_in(k, SI) as described in Section 6.3.6.2 of
	Snyder and Shen (2019) [function g_i(SI) in Section 5 of Graves and Willems
	(2003)].

	Original function is modified in the following ways:
	1. If SI is less than the external inbound CST for stage k,
	theta_in(k, SI) is calculated as though SI = external inbound CST. (If k is a
	source stage, theta_in(k,.) will never be calculated [theta_out(k,.) will be], but
	k might have non-zero external inbound CST even if it is not a source stage.)
	2. The demand bound demand bound over tau periods is assumed to be of the form
	z_alpha * sigma * sqrt(tau).
	3. When calculating c_k(S, SI), upstream nodes are allowed to use outbound
	CSTs greater than SI, and downstream nodes are allowed to use inbound
	CSTs greater than S. In effect, this allows multiple inbound/outbound
	CSTs for a single nodes.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Tree must be pre-processed already.
	k : int
		Index of node.
	SI : int
		Inbound committed service time.
	theta_in_partial : dict
		Dict of values of theta_in function that have been calculated so far
		(i.e., for i < k).
	theta_out_partial : dict
		Dict of values of theta_out function that have been calculated so far
		(i.e., for i < k).

	Returns
	-------
	theta_in_k_SI : float
		The value of theta_in(k, SI).
	best_cst_adjacent : dict
		Dict indicating, for each adjacent stage i with i <= k, the CST value
		that minimized theta_in(.) for the optimal value of S.
		* If i serves k, then best_CST_adjacent[i] = the value of S_i that
		minimizes theta_out(i, S_i).
		* If i is served by k, then best_CST_adjacent[i] = the value of SI_i
		that minimizes theta_in(i, SI_i).
		* If i = k, then best_CST_adjacent[i] = the best value of S chosen in
		minimization of theta_in(.).
	"""

	# Get node k, for convenience.
	node_k = tree.nodes[k]

	# Initialize min_c.
	min_c = float('inf')

	# Initialize output dict.
	best_cst_adjacent = {}

	# Initialize dict of c_k(S, SI) values (keys = S values).
	c_S = {}

	# Set local_SI: If SI < external_inbound_cst[k], must pretend
	# SI = external_inbound_cst[k], otherwise stage thinks it can get a
	# shorter inbound CST than it really can.
	# Note: external inbound CST defaults to 0 if not provided.
	local_SI = max(SI, node_k['external_inbound_cst'])

	# Loop through S values between 0 and min(SI + T_k, external outbound CST[k]).
	# Note that external outbound CST defaults to BIG_INT if not provided.
	lo_S = 0
	hi_S = min(local_SI + node_k['processing_time'], node_k['external_outbound_cst'])
	for S in range(lo_S, hi_S+1):

		# Calculate c_k(S, SI).
		c_S[S], stage_cost, best_upstream_S, best_downstream_SI = \
			calculate_c(tree, k, S, local_SI, theta_in_partial, theta_out_partial)

		# Compare to min.
		if c_S[S] < min_c:
			# Remember min cost and value of S that attained it.
			min_c = c_S[S]
			best_cst_adjacent[k] = S
			# Remember values of other CSTs that attained min cost.
			for i in range(np.min(list(tree.nodes)), k):
				if i in tree.predecessors(k):
					best_cst_adjacent[i] = best_upstream_S[i]
				elif i in tree.successors(k):
					best_cst_adjacent[i] = best_downstream_SI[i]

	# Capture theta_in_k_SI.
	theta_in_k_SI = min_c

	return theta_in_k_SI, best_cst_adjacent


def calculate_c(tree, k, S, SI, theta_in_partial, theta_out_partial):
	"""Calculate c_k(S,SI), the expected holding cost for N_k as function of
	inbound and outbound CSTs at node_k k.

	Assumes demand bound over tau periods is of the form
	z_alpha * sigma * sqrt(tau).
	# TODO: allow more general demand bound.

	Upstream nodes are allowed to use outbound CSTs greater than SI and
	downstream nodes are allowed to use inbound CSTs greater than S.
	In effect, this allows multiple inbound/outbound CSTs for a single
	node_k.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Tree must be pre-processed already.
	k : int
		Index of node_k.
	S : int
		Outbound committed service time.
	SI : int
		Inbound committed service time.
	theta_in_partial : dict
		Dict of values of theta_in function that have been calculated so far
		(i.e., for i < k).
	theta_out_partial : dict
		Dict of values of theta_out function that have been calculated so far
		(i.e., for i < k).

	Returns
	-------
	cost : float
		Value of c_k(S,SI).
	stage_cost : float
		Cost to hold inventory at stage k (only) given CSTs of SI and S.
	best_upstream_S : dict
		Dict indicating, for each i that is immediately upstream from k,
		the best outbound CST for node_k i given k's CSTs of SI and S.
	best_downstream_SI : dict
		Dict indicating, for each i that is immediately downstream from k,
		the best inbound CST for node_k i given k's CSTs of SI and S.
	"""

	# Get node k, for convenience.
	node_k = tree.nodes[k]

	# Initialize output dicts.
	best_upstream_S = {}
	best_downstream_SI = {}

	# Calculate safety stock.
	safety_stock = node_k['demand_bound_constant'] * \
					node_k['net_demand_standard_deviation'] * \
					np.sqrt(SI + node_k['processing_time'] - S)

	# Set stage_cost equal to holding cost at node_k k.
	stage_cost = node_k['holding_cost'] * safety_stock

	# Initialize cost to holding cost at node_k k.
	cost = stage_cost

	# Add theta_out_partial(i) for nodes i that are immediately upstream from k
	# and have smaller index. (At this point, theta_out_partial(i) has already been
	# calculated for i < k.)
	for i in tree.predecessors(k):
		if i < k:
			# Build dict of theta_out_partial(i, S2) values for S2 <= SI.
			theta_out_values = {S2: theta_out_partial[i][S2] for S2 in range(SI + 1)}
			# Find min value and argmin of theta_out_partial(i, S2) where S2 <= SI.
			min_theta_out, best_upstream_S[i] = min_of_dict(theta_out_values)
			# Add min value of theta_out_partial to cost.
			cost += min_theta_out

	# Add theta_in_partial(j) for nodes j that are immediately downstream from k
	# and have smaller index. (At this point, theta_in_partial(j) has already been
	# calculated for j < k.)
	for j in tree.successors(k):
		if j < k:
			# Build dict of theta_in_partial(j, SI2) values for SI2 >= S.
			theta_in_values = {SI2: theta_in_partial[j][SI2] for SI2 in
							   range(S, tree.graph['max_max_replenishment_time'] + 1)}
			# Find min value and argmin of theta_in_partial(i, SI2) for SI2 >= S.
			min_theta_in, best_downstream_SI[j] = min_of_dict(theta_in_values)
			# Add min value of theta_in_partial to cost.
			cost += min_theta_in

	return cost, stage_cost, best_upstream_S, best_downstream_SI
