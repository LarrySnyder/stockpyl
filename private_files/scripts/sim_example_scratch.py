from stockpyl.supply_chain_network import single_stage_system, serial_system
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results
# network = single_stage_system(
# 	demand_type='P',		# Poisson demand
# 	mean=10,
# 	policy_type='BS',		# base-stock policy
# 	base_stock_level=13,
# 	order_lead_time=0,
# 	shipment_lead_time=1
# )
# _ = simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
# write_results(network=network, num_periods=4, columns_to_print='minimal', print_cost_summary=False)
# network = single_stage_system(
# 	holding_cost=0.18,
# 	stockout_cost=0.70,
# 	demand_type='N',                # normal demand
# 	mean=50,
# 	standard_deviation=8,
# 	policy_type='BS',               # base-stock policy
# 	base_stock_level=264.8,
# 	shipment_lead_time=4,
# 	order_lead_time=1			# to account for difference in SoE
# )
# total_cost = simulation(network=network, num_periods=1000, rand_seed=42, progress_bar=False)
# print(total_cost / 1000)
network = serial_system(
	num_nodes=2,
	demand_type='P',
	mean=45,
	policy_type=['rQ', 'BS'],
	reorder_point=[10, None],
	order_quantity=[50, None],
	base_stock_level=[None, 50],
	shipment_lead_time=[1, 1]
)
simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
write_results(network=network, num_periods=5, columns_to_print='minimal', print_cost_summary=False)
