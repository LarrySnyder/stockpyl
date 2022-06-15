import os
import sys

sys.path.append(os.getcwd())

from stockpyl.ssm_serial import *
from stockpyl.gsm_tree import *
from stockpyl.instances import load_instance
from stockpyl.supply_chain_network import *


# S_star, C_star = optimize_base_stock_levels(
# 	num_nodes=3, 
# 	echelon_holding_cost=[3, 2, 2], 
# 	lead_time=[1, 1, 2], 
# 	stockout_cost=37.12, 
# 	demand_mean=5, 
# 	demand_standard_deviation=1
# 	)

example_6_5_network = network_from_edges(
	[(1, 3), (3, 2), (3, 4)],
	node_order_in_lists=[1, 2, 3, 4],
	processing_times=[2, 1, 1, 1],
	external_inbound_csts=[1, None, None, None],
	local_holding_cost=[1, 3, 2, 3],
	demand_bound_constants=[1, 1, 1, 1],
	external_outbound_csts=[None, 0, None, 1],
	demand_type=[None, 'N', None, 'N'],
	demand_mean=0,
	demand_standard_deviation=[None, 1, None, 1]
)
optimize_committed_service_times(tree=example_6_5_network)