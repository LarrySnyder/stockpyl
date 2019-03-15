"""Code to implement dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2003).

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the GSM instance.

Problem data are specified by specifying the following node attributes:
	- processing_time [T]
	- external_lead_time [si]
	- external_committed_service_time [s]
	- holding_cost [h]
	- external_demand_standard_deviation [sigma]

The following node attributes are used internally to store intermediate values:
	- net_demand_standard_deviation (standard deviation of combined demand
	stream consisting of external demand and downstream demand)

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

def relabel_nodes(tree, start_index=0):
	"""Perform the node-labeling algorithm described in Section 5 of Graves and
	Willems (2003).

	Does not modify the input tree.

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
	new_labels : dict
		Dict containing each node's new label; for example, if
		new_labels[3] = 8, then node 3 has been re-labeled as 8.

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
	return relabeled_tree, new_labels


def find_larger_adjacent_nodes(tree):
	"""Find larger-indexed adjacent node, for each node in tree.

	After the nodes are relabeled by relabel_nodes(), each node (except the
	node with the largest index) is adjacent to exactly one node with a
	larger index. Node k's neighbor with larger index is denoted p(k) in
	Graves and Willems (2003). This function finds p(k) for all k and also
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


def longest_path(tree):
	"""Determine the length of the longest path from any source node to to each node k.

	Arc lengths are determined by processing times. External lead times are considered
	source nodes, so having an external LT at node i of 5 is like having another node
	that serves node i with a processing time of 5.

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




# Network from Figure 6.12.
# G = nx.DiGraph()
# G.add_nodes_from(range(1, 8))
# G.add_edge(1, 2)
# G.add_edge(1, 3)
# G.add_edge(3, 5)
# G.add_edge(4, 5)
# G.add_edge(5, 6)
# G.add_edge(5, 7)

# Network from Figure 6.13.
# G = nx.DiGraph()
# G.add_nodes_from(range(1, 4))
# G.add_edge(1, 3)
# G.add_edge(3, 2)
# G.add_edge(3, 4)
# proc_times = {1: 2, 2: 1, 3: 1, 4: 1}
# external_lead_times = {1: 1}
# new_G, new_labels = relabel_nodes(G, start_index=1)
#
# longest_paths = longest_path(new_G, proc_times, external_lead_times)

#print(new_labels)
#
# new_G = nx.relabel_nodes(G, new_labels)
# nx.draw_networkx(new_G, with_labels=True)
# plt.show()
# A = nx.adjacency_matrix(G)
# print(G)
# print(nx.to_numpy_matrix(G))