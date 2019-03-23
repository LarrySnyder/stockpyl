import pandas as pd
import numpy as np
import networkx as nx

node_df = pd.read_csv('mwe.csv')

graph = nx.DiGraph()
graph.add_nodes_from(node_df['Name'])
nx.set_node_attributes(graph, dict(zip(node_df['Name'], node_df['Cost'])), 'nodeCost')
nx.set_node_attributes(graph, dict(zip(node_df['Name'], node_df['Mean'])), 'avgDemand')
nx.set_node_attributes(graph, dict(zip(node_df['Name'], node_df['SD'])), 'sdDemand')
nx.set_node_attributes(graph, dict(zip(node_df['Name'], node_df['CST'])), 'servTime')
nx.set_node_attributes(graph, dict(zip(node_df['Name'], node_df['SL'])), 'servLevel')

# # Idea #1: Only add rows for which attribute is not NaN.
# for r, _ in node_df.iterrows():
# 	if not np.isnan(node_df['serviceLevel'][r]):
# 		graph.nodes[node_df['Stage Name'][r]]['demand_bound_constant'] = node_df['serviceLevel'][r]
#
# # Idea #2: Delete NaN attributes.
# nx.set_node_attributes(graph, dict(zip(node_df['Stage Name'], node_df['avgDemand'])), 'external_demand_mean')
# for r, row in node_df.iterrows():
# 	if np.isnan(node_df['avgDemand'][r]):
# 		del graph.nodes[row['Stage Name']]['external_demand_mean']

# Loop through all nodes and all attributes and remove NaNs.
for i in graph.nodes:
	for k, v in list(graph.nodes[i].items()):
		if np.isnan(v):
			del graph.nodes[i][k]

for i in graph.nodes:
	print(graph.nodes[i])
