# This is necessary in order to make the import statements work.
import sys

sys.path.append('../stockpyl')

from stockpyl import sim
from stockpyl import sim_io
from stockpyl import supply_chain_network
from stockpyl import supply_chain_node
from stockpyl import instances
from stockpyl import policy
from stockpyl import demand_source
from stockpyl import disruption_process
from stockpyl import supply_uncertainty

import numpy as np
import datetime

# Number of periods.
T = 1000

# Single-stage system with deterministic demand (Example 9.3).
if False:
	single_stage = supply_chain_network.single_stage(
		holding_cost=0.25,
		stockout_cost=3,
		demand_type='D',
		demand_list=2000,
		inventory_policy_type='BS',
		base_stock_level=8000,
		shipment_lead_time=1
	)
	single_stage.nodes[0].disruption_process = disruption_process.DisruptionProcess(
		random_process_type='M',
		disruption_type='OP',
		disruption_probability=0.04,
		recovery_probability=0.25
	)
	total_cost = sim.simulation(
		network=single_stage,
		num_periods=T,
		rand_seed=None
	)
	sim_io.write_results(
		network=single_stage,
		num_periods=T,
		num_periods_to_print=100,
		write_csv=False
	#	csv_filename='private_files/debugging_files/ss_disr.csv'
	)
	print(f"avg. cost per period = {total_cost/T} (expected {supply_uncertainty.newsvendor_with_disruptions(0.25, 3, 2000, 0.04, 0.25, 8000)[1]})")
	print(f"avg. disrupted periods = {np.sum([single_stage.nodes[0].state_vars[t].disrupted for t in range(T)]) / T} (expected {single_stage.nodes[0].disruption_process.steady_state_probabilities()[1]})")


# Build two-stage system with deterministic demand. 1 --> 0
two_stage_determ = supply_chain_network.serial_system(
	num_nodes=2,
	local_holding_cost=[1, 2],
	stockout_cost=[0, 10],
	shipment_lead_time=[1, 4], 
	demand_type='D',
	demand_list=[0, 10],
	inventory_policy_type='BS',
	base_stock_levels=[10, 90], 
	downstream_0=False
)
# Downstream stage (stage 0) is subject to disruptions.
two_stage_determ.get_node_from_index(0).disruption_process = disruption_process.DisruptionProcess(
	random_process_type='M',
	disruption_type='SP', 
	disruption_probability=0.05,
	recovery_probability=0.3
)
# Set ITHC=0 to avoid artificial increase in cost when L increases.
for n in two_stage_determ.nodes:
	n.in_transit_holding_cost = 0

# Simulate.
total_cost = sim.simulation(network=two_stage_determ, num_periods=T, rand_seed=42)
sim_io.write_results(
	network=two_stage_determ,
	num_periods=T,
#	num_periods_to_print=100,
	write_csv=True,
	csv_filename='/Users/larry/Documents/GitHub/stockpyl/private_files/debugging_files/ss_disr.csv'
)
print(f"avg. cost per period = {total_cost/T} ")
print(f"avg. disrupted periods = {np.sum([two_stage_determ.get_node_from_index(1).state_vars[t].disrupted for t in range(T)]) / T} (expected {two_stage_determ.get_node_from_index(1).disruption_process.steady_state_probabilities()[1]})")


# filename = 'saved_instance_'+str(datetime.datetime.now())
# sim_io.write_instance_and_states(
# 	network=two_stage_determ, 
# 	filepath='/Users/larry/Documents/GitHub/stockpyl/private_files/debugging_files/'+filename+'.json',
# 	instance_name='temp'
# )
