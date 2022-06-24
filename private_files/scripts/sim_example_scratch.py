from stockpyl.supply_chain_network import single_stage_system, serial_system
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results
from stockpyl.instances import load_instance

import math

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

# def holding_cost(x):
# 	return 0.5 * max(x, 0)**2

# network = single_stage_system(
# 	local_holding_cost_function=holding_cost,
# 	stockout_cost_function=lambda x: 10 * math.sqrt(max(-x, 0)),
# 	demand_type='P',	
# 	mean=15,
# 	policy_type='BS',		
# 	base_stock_level=17,
# 	lead_time=1
# )
# T = 100
# total_cost = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
# #print(f"Total cost per period = {total_cost / T}")
# write_results(network=network, num_periods=T, periods_to_print=list(range(6)), columns_to_print='costs', print_cost_summary=False)

# network = serial_system(
# 	num_nodes=2,
# 	node_order_in_system=[1, 2],
# 	shipment_lead_time=1,
# 	demand_type='P',
# 	mean=20,
# 	policy_type='BS',
# 	base_stock_level=[25, 25]
# )
from stockpyl.ssm_serial import optimize_base_stock_levels, newsvendor_heuristic
from stockpyl.supply_chain_network import echelon_to_local_base_stock_levels
from stockpyl.sim import run_multiple_trials
# Load network.
network = load_instance("example_6_1")
# Set base-stock levels according to optimal solution.
S_opt, _ = optimize_base_stock_levels(network=network)
S_opt_local = echelon_to_local_base_stock_levels(network, S_opt)
for n in network.nodes:
	n.inventory_policy.base_stock_level = S_opt_local[n.index]
mean_opt, sem_opt = run_multiple_trials(network=network, num_trials=10, num_periods=1000, rand_seed=42, progress_bar=False)
print(f"Optimal solution has simulated average cost per period with mean {mean_opt} and SEM {sem_opt}")
# Set base-stock levels according to heuristic solution.
S_heur = newsvendor_heuristic(network=network)
S_heur_local = echelon_to_local_base_stock_levels(network, S_heur)
for n in network.nodes:
	n.inventory_policy.base_stock_level = S_heur_local[n.index]
mean_heur, sem_heur = run_multiple_trials(network=network, num_trials=10, num_periods=1000, rand_seed=42, progress_bar=False)
print(f"Heuristic solution has simulated average cost per period with mean {mean_heur} and SEM {sem_heur}")
# Calculate confidence intervals.
from scipy.stats import norm
z = norm.ppf(1 - (1 - 0.95)/2)
lo_opt, hi_opt = mean_opt - z * sem_opt, mean_opt + z * sem_opt
lo_heur, hi_heur = mean_heur - z * sem_heur, mean_heur + z * sem_heur
print(f"Optimal solution CI = [{lo_opt}, {hi_opt}], heuristic solution CI = [{lo_heur}, {hi_heur}]")



# network.get_node_from_index(2).disruption_process = DisruptionProcess(
# 	random_process_type='M',
# 	disruption_type='RP',
# 	disruption_probability=0.1,
# 	recovery_probability=0.4
# )
# T = 100
# _ = simulation(network=network, num_periods=T, rand_seed=42, progress_bar=False)
# write_results(network=network, num_periods=T, periods_to_print=list(range(7, 16)), columns_to_print=['DISR', 'IO', 'OQ', 'IS', 'OS', 'IL', 'ISPL', 'IDI'], print_cost_summary=False)
#write_results(network=network, num_periods=T, print_cost_summary=False, write_csv=True, csv_filename='tests/additional_files/test_sim_disruption_example_6_1_SP.csv')