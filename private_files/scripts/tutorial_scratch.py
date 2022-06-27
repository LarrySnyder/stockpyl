from stockpyl.supply_chain_network import network_from_edges
from stockpyl.sim import simulation
from stockpyl.sim_io import write_results
network = network_from_edges(
	edges=[(3, 2), (3, 1), (4, 1)],
	node_order_in_lists=[1, 2, 3, 4],
	local_holding_cost=[2, 2, 1, 1],
	stockout_cost=[10, 10, 0, 0],
	order_lead_time=[0, 1, 0, 0],   
	shipment_lead_time=[2, 1, 0, 1],
	demand_type=['P', 'P', None, None],
	mean=[10, 10, None, None],
	policy_type=['BS', 'BS', 'BS', 'BS'],
	base_stock_level=[30, 25, 10, 10]
)
simulation(network=network, num_periods=10, rand_seed=40)

write_results(
	network=network, 
	num_periods=10,
	periods_to_print=list(range(3, 9)), 
	columns_to_print=['OQ', 'IL', 'costs'],
	print_cost_summary=False
	)