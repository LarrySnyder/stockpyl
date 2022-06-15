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

filename='failed_instance_2022-06-10 08:45:49.372822'
network=sim_io.load_instance(
	instance_name='failed_instance', 
	filepath='/Users/larry/Documents/GitHub/stockpyl/private_files/debugging_files/'+filename+'.json',
	ignore_state_vars=True
)

# Simulate.
total_cost = sim.simulation(network=network, num_periods=T, rand_seed=42)
sim_io.write_results(
	network=network,
	num_periods=T,
#	num_periods_to_print=100,
	write_csv=True,
	csv_filename='/Users/larry/Documents/GitHub/stockpyl/private_files/debugging_files/ss_disr.csv'
)
print(f"avg. cost per period = {total_cost/T} ")
print(f"avg. disrupted periods = {np.sum([network.get_node_from_index(1).state_vars[t].disrupted for t in range(T)]) / T} (expected {network.get_node_from_index(1).disruption_process.steady_state_probabilities()[1]})")
