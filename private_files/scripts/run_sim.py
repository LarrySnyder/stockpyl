# This is necessary in order to make the import statements work.
import sys

#sys.path.append('../stockpyl')

from stockpyl import sim
from stockpyl import sim_io
from stockpyl import supply_chain_network
from stockpyl import supply_chain_node
from stockpyl import instances
from stockpyl import policy
from stockpyl import demand_source

import numpy as np

# Number of periods.
T = 1000

# Build a serial system. The function serial_system() does it for you.
# It returns a SupplyChainNetwork object, which is what the simulation needs.
# The data below replicate Example 6.1 from Fundamentals of Supply Chain Theory 2e.
serial_3 = supply_chain_network.serial_system(
	num_nodes=3,
	local_holding_cost=[7, 4, 2],
	stockout_cost=[37.12, 0, 0],
	shipment_lead_time=[1, 1, 2],
	demand_type='N',
	demand_mean=5,
	demand_standard_deviation=1,
	inventory_policy_type='BS',
	base_stock_levels=[6.49, 12.02-6.49, 22.71-12.02],
	downstream_0=True
)

# Simulate the system.
total_cost = sim.simulation(
	network=serial_3,
	num_periods=T,
	rand_seed=42
)
print(f"avg. cost per period = {total_cost/T}")

# Write the results. You can write them to the console or to a file.
# Here, I'm writing them to the console.
sim_io.write_results(
	network=serial_3,
	num_periods=T,
	num_periods_to_print=100,
	write_csv=False
)

# You can also load named instances, most of which are from the book.
serial_3 = instances.load_instance("example_6_1")
# If we simulate it, we should get the same results.
total_cost = sim.simulation(network=serial_3, num_periods=T, rand_seed=42)
print(f"avg. cost per period using named instance = {total_cost/T:.6f}")

# Let's simulate the same system, but using echelon base-stock policies instead of local.
# Calculate echelon base-stock levels.
S_local = {n.index: n.inventory_policy.base_stock_level for n in serial_3.nodes}
S_echelon = supply_chain_network.local_to_echelon_base_stock_levels(serial_3, S_local)

# Create and fill echelon base-stock policies.
for n in serial_3.nodes:
	n.inventory_policy.type = 'EBS'
	n.inventory_policy.base_stock_level = S_echelon[n.index]

# Simulate with echelon BS policy.
total_cost_ech = sim.simulation(serial_3, T, rand_seed=42)
print(f"avg. cost per period using echelon BS policies = {total_cost/T:.6f}")


# Here we'll build an assembly system -- a "multiple warehouse, one retailer" system.
assembly_3_stage_network = supply_chain_network.mwor_system(
	num_warehouses=2,
	local_holding_cost=[2, 1, 1],
	stockout_cost=[20, 0, 0],
	demand_type='N',
	demand_mean=5,
	demand_standard_deviation=1,
	shipment_lead_time=[1, 2, 2],
	inventory_policy_type='BS',
	base_stock_levels=[7, 13, 11],
	initial_IL=[7, 13, 11],
	downstream_0=True
)
# Tell it to round the demands to integers.
assembly_3_stage_network.nodes[0].demand_source.round_to_int = True
# Simulate. 
total_cost = sim.simulation(network=assembly_3_stage_network, num_periods=T, rand_seed=17)
print(f"avg. cost per period for MWOR system = {total_cost/T:.6f}")


# If you want to build your own network from scratch, the easiest way is to specify
# the edges, and the data for each node, and call network_from_edges(). Here's
# an example that builds the distribution system in Figure 1(a) from Rong, Atan, and Snyder (2017),
# but using normal demand instead of Poisson (I haven't implemented Poisson demand yet).
rong_atan_snyder_figure_1a = supply_chain_network.network_from_edges(
	edges=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)],
	demand_type={0: None, 1: None, 2: None, 3: 'N', 4: 'N', 5: 'N', 6: 'N'},	
	demand_mean=8,
	demand_standard_deviation=np.sqrt(8),
	local_holding_cost={0: 1/3, 1: 2/3, 2: 2/3, 3: 1, 4: 1, 5: 1, 6: 1},
	stockout_cost=20,
	shipment_lead_time=1,
	inventory_policy_type='BS',
	base_stock_levels={i: 0 for i in range(0, 7)}	# need to provide a value here, but will overwrite below
)
# Replace the base-stock levels with mean + 3 * SD for "derived demand" distribution 
# (external demand plus demand from downstream nodes).
for n in rong_atan_snyder_figure_1a.nodes:
	n.inventory_policy.base_stock_level = n.derived_demand_mean + 3 * n.derived_demand_standard_deviation

# Simulate. 
total_cost = sim.simulation(network=rong_atan_snyder_figure_1a, num_periods=T, rand_seed=17)
print(f"avg. cost per period for distribution system = {total_cost/T:.6f}")


# You can also build the network node-by-node, but it's more tedious. Here's the same distribution system:
# Initialize network.
rong_atan_snyder_figure_1a_v2 = supply_chain_network.SupplyChainNetwork()
# Build nodes.
node0 = supply_chain_node.SupplyChainNode(index=0, local_holding_cost=1/3, stockout_cost=0, shipment_lead_time=1)
node1 = supply_chain_node.SupplyChainNode(index=1, local_holding_cost=2/3, stockout_cost=0, shipment_lead_time=1)
node2 = supply_chain_node.SupplyChainNode(index=2, local_holding_cost=2/3, stockout_cost=0, shipment_lead_time=1)
node3 = supply_chain_node.SupplyChainNode(index=3, local_holding_cost=1, stockout_cost=20, shipment_lead_time=1)
node4 = supply_chain_node.SupplyChainNode(index=4, local_holding_cost=1, stockout_cost=20, shipment_lead_time=1)
node5 = supply_chain_node.SupplyChainNode(index=5, local_holding_cost=1, stockout_cost=20, shipment_lead_time=1)
node6 = supply_chain_node.SupplyChainNode(index=6, local_holding_cost=1, stockout_cost=20, shipment_lead_time=1)
# Add nodes to network.
rong_atan_snyder_figure_1a_v2.add_node(node0)
rong_atan_snyder_figure_1a_v2.add_successor(node0, node1)
rong_atan_snyder_figure_1a_v2.add_successor(node0, node2)
rong_atan_snyder_figure_1a_v2.add_successor(node1, node3)
rong_atan_snyder_figure_1a_v2.add_successor(node1, node4)
rong_atan_snyder_figure_1a_v2.add_successor(node2, node5)
rong_atan_snyder_figure_1a_v2.add_successor(node2, node6)
# Add demand sources to leaf nodes.
for n in rong_atan_snyder_figure_1a_v2.sink_nodes:
	n.demand_source = demand_source.DemandSource(type='N', mean=8, standard_deviation=np.sqrt(8))
# Add inventory policy to each node.
for n in rong_atan_snyder_figure_1a_v2.nodes:
	inventory_policy = policy.Policy()
	inventory_policy.type = 'BS'
	inventory_policy.base_stock_level = n.derived_demand_mean + 3 * n.derived_demand_standard_deviation
	n.inventory_policy = inventory_policy

# Simulate. 
total_cost = sim.simulation(network=rong_atan_snyder_figure_1a, num_periods=T, rand_seed=17)
print(f"avg. cost per period for distribution system built node-by-node = {total_cost/T:.6f}")
