from stockpyl.supply_chain_network import single_stage_system, serial_system
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results
from stockpyl.instances import load_instance
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
# network = serial_system(
# 	num_nodes=3,
# 	node_order_in_system=[3, 2, 1],
# 	local_holding_cost={1: 7, 2: 4, 3: 2},		
# 	shipment_lead_time={1: 1, 2: 1, 3: 2},
# 	stockout_cost=37.12,
# 	demand_type='N',
# 	mean=5,
# 	standard_deviation=1,
# 	policy_type='EBS',	# echelon base-stock policy
# 	base_stock_level={1: 6.49, 2: 12.02, 3: 22.71}
# )
# #network = load_instance("example_6_1")
# total_cost = simulation(network=network, num_periods=1000, rand_seed=42, progress_bar=False)
# print(total_cost / 1000)

from stockpyl.disruption_process import DisruptionProcess
# network = single_stage_system(
# 	holding_cost=0.25,
# 	stockout_cost=3,
# 	demand_type='D',		# deterministic demand
# 	demand_list=2000,
# 	disruption_process=DisruptionProcess(random_process_type='M', disruption_probability=0.04, recovery_probability=0.25),
# 	policy_type='BS',		
# 	base_stock_level=8000
# )
# T = 10000
# total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
# print(f"Total cost per period = {total_cost / T}")
#write_results(network=network, num_periods=100, print_cost_summary=False)

# network = serial_system(
# 	num_nodes=2,
# 	node_order_in_system=[1, 2],
# 	shipment_lead_time=1,
# 	demand_type='P',
# 	mean=20,
# 	policy_type='BS',
# 	base_stock_level=[25, 25]
# )
network = load_instance("example_6_1")
network.get_node_from_index(2).disruption_process = DisruptionProcess(
	random_process_type='M',
	disruption_type='SP',
	disruption_probability=0.1,
	recovery_probability=0.4
)
T = 100
_ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
#write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'OS', 'IL', 'ISPL'], print_cost_summary=False)
write_results(network=network, num_periods=T, print_cost_summary=False, write_csv=True, csv_filename='tests/additional_files/test_sim_disruption_example_6_1_SP.csv')