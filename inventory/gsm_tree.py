"""Code to implement dynamic programming (DP) algorithm for guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2003).

'node' and 'stage' are used interchangeably in the documentation.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import numpy as np
import scipy as sp
import networkx as nx
import matplotlib.pyplot as plt


### GRAPH MANIPULATION ###

def relabel_nodes(tree, start_index=0):
	"""Perform the node-labeling algorithm described in Section 5 of Graves and Willems.

	Parameters
	----------
	adjacency_matrix : graph
		NetworkX directed graph indicating flows among nodes. Current node labels are
		ignored and may be anything.
	start_index : int
		Integer to use as starting (smallest) node label.

	Returns
	-------
	new_labels: dict
		Dict containing each node's new label; for example, if new_labels[3] = 8, then
		node 3 has been re-labeled as 8.

	"""

	# Determine number of nodes.
	num_nodes = nx.number_of_nodes(tree)

	# Initialize all nodes to "unlabeled", and initialize list of new labels.
	labeled = {i: False for i in tree.nodes()}
	new_labels = {}

	# Find nodes that are adjacent to at most 1 unlabeled node and label them.
	for k in range(start_index, start_index+num_nodes):

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

	return new_labels



# Network from Figure 6.12.
G = nx.DiGraph()
G.add_nodes_from(range(1, 8))
G.add_edge(1, 2)
G.add_edge(1, 3)
G.add_edge(3, 5)
G.add_edge(4, 5)
G.add_edge(5, 6)
G.add_edge(5, 7)
new_labels = relabel_nodes(G, start_index=71)
print(new_labels)

new_G = nx.relabel_nodes(G, new_labels)
nx.draw_networkx(new_G, with_labels=True)
plt.show()
# A = nx.adjacency_matrix(G)
# print(G)
# print(nx.to_numpy_matrix(G))