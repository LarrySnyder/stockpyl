"""Code to implement dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2000).

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the GSM instance.

Problem data are specified by specifying the following node attributes:
	- processing_time [T]
	- external_lead_time [si]
	- external_committed_service_time [s]
	- holding_cost [h]
	- external_demand_mean [mu]
	- external_demand_standard_deviation [sigma]

The following node attributes are used internally to store outputs and
intermediate values:
	- original_label
	- net_demand_standard_deviation (standard deviation of combined demand
	stream consisting of external demand and downstream demand)
	- larger_adjacent_node [p]
	- larger_adjacent_node_is_downstream
	- max_replenishment_time [M]

The following edge attributes are supported:
	- units_required (e.g., on edge i->j, units_required units of item i are
	required to make 1 unit of item j)

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt
import pprint


### GRAPH MANIPULATION ###

def preprocess_tree(tree, start_index=0):
	"""Preprocess the GSM tree. Returns an independent copy.

	Relabel the nodes; fill original_label, net_demand_mean,
	net_demand_standard_deviation, larger_adjacent_node,
	max_replenishment_time attributes.

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

	# Relabel nodes.
	new_tree = relabel_nodes(tree, start_index)

	# Calculate net demand parameters.
	net_demand_means, net_demand_standard_deviations = net_demand(new_tree)
	nx.set_node_attributes(new_tree, net_demand_means, 'net_demand_mean')
	nx.set_node_attributes(new_tree, net_demand_standard_deviations,
						   'net_demand_standard_deviation')

	# Determine larger adjacent nodes.
	larger_adjacent, downstream = find_larger_adjacent_nodes(new_tree)
	nx.set_node_attributes(new_tree, larger_adjacent, 'larger_adjacent_node')
	nx.set_node_attributes(new_tree, downstream, 'larger_adjacent_node_is_downstream')

	# Calculate max replenishment times.
	max_replenishment_times = longest_paths(new_tree)
	nx.set_node_attributes(new_tree, max_replenishment_times, 'max_replenishment_time')

	return new_tree


def relabel_nodes(tree, start_index=0):
	"""Perform the node-labeling algorithm described in Section 5 of Graves and
	Willems (2000).

	Does not modify the input tree. Fills 'original_label' attribute of nodes
	in new tree with old node labels.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored and may be anything.
	start_index : int, optional
		Integer to use as starting (smallest) node label.

	Returns
	-------
	relabeled_tree : graph
		NetworkX directed graph representing the relabeled tree network.

	"""

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

	return relabeled_tree


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
		if k < np.max(tree.nodes):
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

	Arc lengths are determined by processing times. External lead times are
	considered source nodes, so having an external LT at node i of 5 is like
	having another node that serves node i with a processing time of 5.

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

	# Get dict of external lead times. (Some nodes may have no entry.)
	external_lead_time = nx.get_node_attributes(tree, 'external_lead_time')

	# Copy the tree. Set the weight of each edge into a given node k to the processing
	# time of node k. If node k is a source node and/or it has an external lead time,
	# add a dummy node before node k and set weight of edge from dummy node to node k
	# equal to processing time of node k + external lead time for node k.
	temp_tree = tree.copy()
	for k in tree.nodes:
		for p in tree.predecessors(k):
			temp_tree[p][k]['weight'] = tree.nodes[k]['processing_time']
		if tree.in_degree(k) == 0 or external_lead_time.get(k, 0) > 0:
			temp_tree.add_edge('dummy_' + str(k), k,
							   weight=tree.nodes[k]['processing_time'] + external_lead_time.get(k, 0))

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

	Does not modify the input tree.

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.

	Returns
	-------
	net_means : dict
		Dict of net mean for each node.

	net_demand : dict
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
	# no successors), adding their net_means and net_variances to those of their
	# predecessors. Then remove the leaf nodes and iterate.
	while temp_tree.number_of_nodes() > 0:
		leaf_nodes = [k for k in temp_tree.nodes if temp_tree.out_degree(k) == 0]
		for k in leaf_nodes:
			for i in temp_tree.predecessors(k):
				net_means[i] += net_means[k]
				net_variances[i] += net_variances[k]
			temp_tree.remove_node(k)

	net_standard_deviations = {k: np.sqrt(net_variances[k]) for k in tree.nodes}
	return net_means, net_standard_deviations


### OPTIMIZATION ###

def optimize_committed_service_times(raw_tree):
	"""Optimize committed service times.

	Optimization is performed using the dynamic programming (DP) algorithm of
	Graves and Willems (2000).

	raw_tree is the DiGraph containing the instance. It need not be
	pre-processed (nodes relabeled, etc.); this function will do the
	pre-processing.

	Parameters
	----------
	raw_tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Current node labels are ignored and may be anything.

	Returns
	-------

	"""

	# Preprocess tree.
	tree = preprocess_tree(raw_tree)

	# Solve.


def CST_DP(tree):
	"""Find optimal committed service times by dynamic programming (DP)
	algorithm by Graves and Willems (2000).

	Parameters
	----------
	tree : graph
		NetworkX directed graph representing the multi-echelon tree network.
		Tree must be pre-processed already.

	Returns
	-------

	"""

	# Calculate maximum value of max_replenishment_time.
	max_max_replenishment_time = np.max(nx.get_node_attributes(tree,
									'max_replenishment_time'))

