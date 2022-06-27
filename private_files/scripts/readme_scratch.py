# from stockpyl.supply_chain_network import serial_system, echelon_to_local_base_stock_levels
# from stockpyl.sim import simulation
# from stockpyl.sim_io import write_results
# from stockpyl.ssm_serial import optimize_base_stock_levels
# from stockpyl.policy import Policy
# from stockpyl.disruption_process import DisruptionProcess
# from stockpyl.demand_source import DemandSource
# from stockpyl.instances import load_instance


from stockpyl.supply_chain_network import serial_system
from stockpyl.ssm_serial import optimize_base_stock_levels
network = serial_system(
	num_nodes=3,
	node_order_in_system=[3, 2, 1],
	echelon_holding_cost=[4, 3, 1],
	local_holding_cost=[4, 7, 8],
	shipment_lead_time=[1, 1, 2],
	stockout_cost=40,
	demand_type='N',
	mean=10,
	standard_deviation=2
)
S_star, C_star = optimize_base_stock_levels(network=network)
print(f"S_star = {S_star}, C_star = {C_star}")

from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels
from stockpyl.sim import simulation
from stockpyl.policy import Policy
S_star_local = echelon_to_local_base_stock_levels(network, S_star)
for n in network.nodes:
	n.inventory_policy = Policy(type='BS', base_stock_level=S_star_local[n.index], node=n)
T = 1000
total_cost = simulation(network=network, num_periods=T, rand_seed=42)
print(f"Average total cost per period = {total_cost/T}")

# network = load_instance("example_6_1")
# # # network.get_node_from_index(3).demand_source=DemandSource()
# # # network.get_node_from_index(2).demand_source=DemandSource()
# network2 = serial_system(
# 	num_nodes=3,
# 	node_order_in_system=[3, 2, 1],
# 	echelon_holding_cost={1: 3, 2: 2, 3: 2},
# 	local_holding_cost={1: 7, 2: 4, 3: 2},
# 	shipment_lead_time={1: 1, 2: 1, 3: 2},
# 	stockout_cost={1: 37.12, 2: 0, 3: 0},
# 	demand_type='N',
# 	mean=5,
# 	standard_deviation=1,
# 	policy_type='BS',
# 	base_stock_level=0,
# )

# # #S_star = {3: 22.700237234889784, 2: 12.012332294949644, 1: 6.5144388073261155}
# S_star, C_star = optimize_base_stock_levels(network=network2)
# print(f"{S_star}, {C_star}")

# S_star_local = echelon_to_local_base_stock_levels(network2, S_star)
# # for n in network.nodes:
# # 	n.inventory_policy = Policy(type='BS', base_stock_level=S_star_local[n.index], node=n)
# # 	#n.disruption_process = DisruptionProcess()

# for n in network2.nodes:
# 	n.inventory_policy = Policy(type='BS', base_stock_level=S_star_local[n.index], node=n)
# # 	#n.disruption_process = DisruptionProcess()
# # # eq = network.deep_equal_to(network2)


# T = 1000
# total_cost = simulation(network=network, num_periods=T)
# #write_results(network=network, num_periods=T, periods_to_print=10, columns_to_print=['basic', 'costs'])
# print(f"network: {total_cost/T}")

# total_cost = simulation(network=network2, num_periods=T)
# #write_results(network=network, num_periods=T, periods_to_print=10, columns_to_print=['basic', 'costs'])
# print(f"network2: {total_cost/T}")