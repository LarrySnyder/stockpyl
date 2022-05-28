"""Code to read and solve instances from Willems (2007), which presents
38 GSM tree instances from real-world supply chains.

'stdDev stageTime' field in Willems's data sets is ignored; that is, processing
times are treated as deterministic.

Unfortunately the optimal solutions or costs are not available, so there is
no benchmark against which to compare the results.

PROBLEM! These networks are not trees; they have (undirected) cycles.
Many contain "clusters of commonality," so they can be reduced to trees following
Humair and Willems (2006), but this is a whole other can of worms.
TODO: handle clusters of commonality
For now, this approach is a dead end.

(c) Lawrence V. Snyder
Lehigh University

"""

import pandas as pd
#from scipy import stats
#import numpy as np
import time
import tabulate
import matplotlib.pyplot as plt

from gsm_tree import *


node_df = pd.read_excel('MSOM-06-038-R2 Data Set in Excel.xls', sheet_name='01_SD')
edge_df = pd.read_excel('MSOM-06-038-R2 Data Set in Excel.xls', sheet_name='01_LL')

#print(node_df)

# Create tree.
tree = nx.DiGraph()

# Add nodes.
tree.add_nodes_from(node_df['Stage Name'])
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['stageCost'])), 'holding_cost')
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['avgDemand'])), 'external_demand_mean')
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['stdDevDemand'])), 'external_demand_standard_deviation')
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['maxServiceTime'])), 'external_outbound_cst')
for r, _ in node_df.iterrows():
	if not np.isnan(node_df['serviceLevel'][r]):
		tree.nodes[node_df['Stage Name'][r]]['demand_bound_constant'] = node_df['serviceLevel'][r]
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['stageTime'])), 'processing_time')
nx.set_node_attributes(tree, dict(zip(node_df['Stage Name'], node_df['maxServiceTime'])), 'external_outbound_cst')

# Loop through all nodes and all attributes and remove NaNs.
for i in tree.nodes:
	for k, v in list(tree.nodes[i].items()):
		if np.isnan(v):
			del tree.nodes[i][k]

# Add edges.
tree.add_edges_from(zip(edge_df['sourceStage'], edge_df['destinationStage']))

# Add problem instance label.
tree.graph['problem_name'] = '01'

# Get layout information.
pos = {node_df['Stage Name'][r]: (node_df['xPosition'][r], node_df['yPosition'][r]) for r, _ in node_df.iterrows()}

#for i in tree.nodes:
#	print(i, tree.nodes[i])

nx.draw(tree, pos=pos)
plt.show()

#
# tree = preprocess_tree(tree)
# start_time = time.time()
#
# opt_cost, opt_cst = optimize_committed_service_times(tree)
#
# end_time = time.time()
#
# # Get some other quantities based on the solution.
# SI = inbound_cst(tree, tree.nodes, opt_cst)
# nlt = net_lead_time(tree, tree.nodes, opt_cst)
# safety_stock = safety_stock_levels(tree, tree.nodes, opt_cst)
# base_stock = cst_to_base_stock_levels(tree, tree.nodes, opt_cst)
#
# # Display the results.
# print('\nSolved {:s} in {:.4f} seconds.'.format(tree.graph['problem_name'],
# 											  end_time - start_time))
# print('Optimal cost: {:.4f}'.format(opt_cost))
# print('Optimal solution:\n')
# results = []
# for k in tree.nodes:
# 	results.append([k, opt_cst[k], SI[k], nlt[k], safety_stock[k], base_stock[k]])
# print(tabulate.tabulate(results, headers=['Stage', 'S', 'SI', 'NLT', 'Safety Stock', 'Base-Stock Level']))
