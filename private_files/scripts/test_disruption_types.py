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
import tqdm
import matplotlib.pyplot as plt

# Number of periods.
T = 10000

# Two-stage system with deterministic demand. 0 --> 1
two_stage_determ = supply_chain_network.serial_system(
	num_nodes=2,
	local_holding_cost=[1, 2],
	stockout_cost=[0, 10],
	shipment_lead_time=[1, 1],
	demand_type='D',
	demand_list=[0, 10],
	inventory_policy_type='BS',
	base_stock_levels=[10, 10],
	downstream_0=False
)
# Downstream stage (stage 1) is subject to disruptions.
two_stage_determ.get_node_from_index(1).disruption_process = disruption_process.DisruptionProcess(
	random_process_type='M',
	disruption_type='OP',
	disruption_probability=0.05,
	recovery_probability=0.3
)
# Set ITHC=0 to avoid artificial increase in cost when L increases.
for n in two_stage_determ.nodes:
	n.in_transit_holding_cost = 0

# Lists to iterate over.
dt_list = ('OP', 'SP', 'TP', 'RP')
lt_list = list(range(10))

# Progress bar.
pbar = tqdm.tqdm(total=len(dt_list)*len(lt_list))

# Rand seed.
np.random.seed(42)

# Results.
results = {}

# Loop through disruption types.
for dt in dt_list:
	results[dt] = []

	# Loop through lead times.
	for lt in lt_list:
		pbar.update()

		# Fill parameters.
		node1 = two_stage_determ.get_node_from_index(1)
		node1.shipment_lead_time = lt
		node1.disruption_process.disruption_type = dt
		node1.inventory_policy.base_stock_level = node1.demand_source.demand_list * (lt + 1)

		# Simulate.
		total_cost = sim.simulation(network=two_stage_determ, num_periods=T, rand_seed=None, progress_bar=False)

		# Store results.
		results[dt].append(total_cost/T)

# Plot results.
plt.figure()
#plt.plot(lt_list, results['OP'], lt_list, results['SP'], lt_list, results['TP'], lt_list, results['RP'])
plt.plot(lt_list, results['OP'], marker='o', label='OP')
plt.plot(lt_list, results['SP'], marker='o', label='SP')
plt.plot(lt_list, results['TP'], marker='o', label='TP')
plt.plot(lt_list, results['RP'], marker='o', label='RP')
plt.legend()
plt.xlabel('Lead Time')
plt.ylabel('Avg. Cost/Period')
plt.title('2-Stage System, Deterministic Demand, alpha=0.05, beta=0.3, S=10*(L+1)')
plt.show()