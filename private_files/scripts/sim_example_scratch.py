from stockpyl.supply_chain_network import single_stage_system
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results
network = single_stage_system(
	demand_type='P',		# Poisson demand
	mean=10,
	policy_type='BS',		# base-stock policy
	base_stock_level=13,
	order_lead_time=0,
	shipment_lead_time=1
)
total_cost = simulation(network=network, num_periods=4, rand_seed=42, progress_bar=False)
write_results(network=network, num_periods=4, columns_to_print='minimal', print_cost_summary=False)
