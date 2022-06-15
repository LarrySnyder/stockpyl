from stockpyl.ssm_serial import optimize_base_stock_levels, newsvendor_heuristic
from stockpyl.supply_chain_network import serial_system

shang_song_network = serial_system(
	num_nodes=4,
	node_order_in_system=[4, 3, 2, 1],
	echelon_holding_cost=0.25,
	shipment_lead_time=0.25,
	stockout_cost={1: 9},
	demand_type='P',
	mean=16,
	policy_type='BS'
)

S_star, C_star = optimize_base_stock_levels(network=shang_song_network)
print(f"S_star = {S_star} C_star = {C_star}")

S_heur = newsvendor_heuristic(network=shang_song_network)
print(f"S_heur = {S_heur}")