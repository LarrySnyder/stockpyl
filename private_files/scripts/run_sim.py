# This is necessary in order to make the import statements work.
# Change the path to your own configuration.
import sys
sys.path.append('/Users/larry/Documents/GitHub/stockpyl')

from stockpyl import sim
from stockpyl import sim_io
from stockpyl import supply_chain_network
from stockpyl import instances

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

