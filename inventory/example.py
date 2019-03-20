"""Examples to demonstrate the use of gsm_tree.py, which implements the
dynamic programming algorithm for the guaranteed-service model (GSM)
for multi-echelon inventory systems with tree structures by Graves and Willems (2000).

'node' and 'stage' are used interchangeably in the documentation.

The primary data object is the NetworkX DiGraph, which contains all of the data
for the GSM instance. The following attributes are used to specify input data:
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

When adding nodes using nx.DiGraph.add_node(), you can add attributes as
arguments to add_node(). Subsequently, to get or set node attributes, the node
is treated like a dict with the attributes as keys (as strings), so use
node['holding_cost'], etc.

(c) Lawrence V. Snyder
Lehigh University and Opex Analytics

"""

import time
import tabulate
import sys
#import networkx as nx

from inventory.gsm_tree import *


### Solve Yinan's instance. ###

# Create a new DiGraph object.
yinan_graph = nx.DiGraph()

# Add nodes, with the relevant attributes. Attributes are specified as
# arguments to add_node().
yinan_graph.add_node(1, processing_time=4,
					external_inbound_cst=0,
					holding_cost=1,
					demand_bound_constant=1)
yinan_graph.add_node(2, processing_time=0,
					holding_cost=1.1,
					demand_bound_constant=1,
					external_outbound_cst=0,
					external_demand_standard_deviation=1)
yinan_graph.add_node(3, processing_time=2,
					holding_cost=1,
					demand_bound_constant=1)
yinan_graph.add_node(4, processing_time=0,
					holding_cost=100000,
					demand_bound_constant=1,
					external_outbound_cst=0,
					external_demand_standard_deviation=1)

# Add edges. (units_required is the only edge attribute, but we don't need
# it here because it equals 1 for every edge.)
yinan_graph.add_edge(1, 2)
yinan_graph.add_edge(3, 2)
yinan_graph.add_edge(3, 4)

# We can add any arbitrary attributes we want to the graph, nodes, and edges.
# Here, we'll add a label to the graph.
yinan_graph.graph['problem_name'] = 'Yinan''s Counterexample'

# We have to preprocess the graph before we can solve the model or perform
# other functions. Preprocessing calculates some intermediate quantities, fills
# in some missing attributes, etc. Note that preprocess_tree() returns a new graph,
# it does not modify the original graph. In the line below, we just replace the
# old one with the new one.
yinan_graph = preprocess_tree(yinan_graph)

# Start the timer.
start_time = time.time()

# Solve the problem.
opt_cost, opt_cst = optimize_committed_service_times(yinan_graph)

# Stop the timer.
end_time = time.time()

# Get some other quantities based on the solution.
SI = inbound_cst(yinan_graph, yinan_graph.nodes, opt_cst)
nlt = net_lead_time(yinan_graph, yinan_graph.nodes, opt_cst)
safety_stock = safety_stock_levels(yinan_graph, yinan_graph.nodes, opt_cst)
base_stock = base_stock_levels(yinan_graph, yinan_graph.nodes, opt_cst)

# Display the results.
print('\nSolved {:s} in {:.4f} seconds.'.format(yinan_graph.graph['problem_name'],
											  end_time - start_time))
print('Optimal cost: {:.4f}'.format(opt_cost))
print('Optimal solution:\n')
results = []
for k in yinan_graph.nodes:
	results.append([k, opt_cst[k], SI[k], nlt[k], safety_stock[k], base_stock[k]])
print(tabulate.tabulate(results, headers=['Stage', 'S', 'SI', 'NLT', 'Safety Stock', 'Base-Stock Level']))



### Solve the instance in Example 6.5. ###

# Create a new DiGraph object.
ex65_graph = nx.DiGraph()

# Add nodes, with the relevant attributes. Attributes are specified as
# arguments to add_node().
ex65_graph.add_node(1, processing_time=2,
					external_inbound_cst=1,
					holding_cost=1,
					demand_bound_constant=1)
ex65_graph.add_node(2, processing_time=1,
					external_outbound_cst=0,
					holding_cost=3,
					demand_bound_constant=1,
					external_demand_standard_deviation=1)
ex65_graph.add_node(3, processing_time=1,
					holding_cost=2,
					demand_bound_constant=1)
ex65_graph.add_node(4, processing_time=1,
					external_outbound_cst=1,
					holding_cost=3,
					demand_bound_constant=1,
					external_demand_standard_deviation=1)

# Add edges. (units_required is the only edge attribute, but we don't need
# it here because it equals 1 for every edge.)
ex65_graph.add_edge(1, 3)
ex65_graph.add_edge(3, 2)
ex65_graph.add_edge(3, 4)

# We can add any arbitrary attributes we want to the graph, nodes, and edges.
# Here, we'll add a label to the graph.
ex65_graph.graph['problem_name'] = 'Example 6.5'

# We have to preprocess the graph before we can solve the model or perform
# other functions. Preprocessing calculates some intermediate quantities, fills
# in some missing attributes, etc. Note that preprocess_tree() returns a new graph,
# it does not modify the original graph. In the line below, we just replace the
# old one with the new one.
ex65_graph = preprocess_tree(ex65_graph)

# Start the timer.
start_time = time.time()

# Solve the problem.
opt_cost, opt_cst = optimize_committed_service_times(ex65_graph)

# Stop the timer.
end_time = time.time()

# Get some other quantities based on the solution.
SI = inbound_cst(ex65_graph, ex65_graph.nodes, opt_cst)
nlt = net_lead_time(ex65_graph, ex65_graph.nodes, opt_cst)
safety_stock = safety_stock_levels(ex65_graph, ex65_graph.nodes, opt_cst)
base_stock = base_stock_levels(ex65_graph, ex65_graph.nodes, opt_cst)

# Display the results.
print('\nSolved {:s} in {:.4f} seconds.'.format(ex65_graph.graph['problem_name'],
											  end_time - start_time))
print('Optimal cost: {:.4f}'.format(opt_cost))
print('Optimal solution:\n')
results = []
for k in ex65_graph.nodes:
	results.append([k, opt_cst[k], SI[k], nlt[k], safety_stock[k], base_stock[k]])
print(tabulate.tabulate(results, headers=['Stage', 'S', 'SI', 'NLT', 'Safety Stock', 'Base-Stock Level']))

