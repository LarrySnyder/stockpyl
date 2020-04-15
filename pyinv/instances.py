import copy

from pyinv.supply_chain_network import *

# TODO: do this as an InstanceFactory so you can get the same intsnace multiple times (e.g., if you want to change and then start over again)

# Example 6.1.
example_6_1_network = serial_system(
	num_nodes=3,
	local_holding_cost=[7, 4, 2],
	echelon_holding_cost=[3, 2, 2],
	stockout_cost=[37.12, 0, 0],
	demand_type=DemandType.NORMAL,
	demand_mean=5,
	demand_standard_deviation=1,
	shipment_lead_time=[1, 1, 2],
	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	local_base_stock_levels=[6.49, 5.53, 10.69],
	downstream_0=True
)

# Problem 6.1.
problem_6_1_network = serial_system(
	num_nodes=2,
	local_holding_cost=[2, 1],
	echelon_holding_cost=[1, 1],
	stockout_cost=[15, 0],
	demand_type=DemandType.NORMAL,
	demand_mean=100,
	demand_standard_deviation=15,
	shipment_lead_time=[1, 1],
	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	local_base_stock_levels=[100, 94],
	downstream_0=True
)

# Problem 6.2a.
problem_6_2a_network = serial_system(
	num_nodes=5,
	local_holding_cost=[1, 2, 3, 5, 7],
	echelon_holding_cost=[2, 2, 1, 1, 1],
	stockout_cost=[24, 0, 0, 0, 0],
	demand_type=DemandType.NORMAL,
	demand_mean=64,
	demand_standard_deviation=8,
	shipment_lead_time=[0.5, 0.5, 0.5, 0.5, 0.5],
	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	local_base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
	downstream_0=True
)

# Problem 6.2a, adjusted for periodic review.
# (Since L=0.5 in that problem, here we treat each period as
# having length 0.5 in the original problem.)
problem_6_2a_network_adjusted = serial_system(
	num_nodes=5,
	local_holding_cost=list(np.array([1, 2, 3, 5, 7]) / 2),
	stockout_cost=list(np.array([24, 0, 0, 0, 0]) / 2),
	demand_type=DemandType.NORMAL,
	demand_mean=64 / 2,
	demand_standard_deviation=8 / np.sqrt(2),
	shipment_lead_time=[1, 1, 1, 1, 1],
	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	local_base_stock_levels=[40.59, 33.87, 35.14, 33.30, 32.93],
	downstream_0=True
)

# Problem 6.2b, adjusted for periodic review.
# (Since L=0.5 in that problem, here we treat each period as
# having length 0.5 in the original problem.)
problem_6_2b_network_adjusted = copy.deepcopy(problem_6_2a_network_adjusted)
# TODO: build this instance - -need to add Poisson demand capability

# Problem 6.16.
problem_6_16_network = serial_system(
	num_nodes=2,
	local_holding_cost=[7, 2],
	stockout_cost=[24, 0],
	demand_type=DemandType.NORMAL,
	demand_mean=20,
	demand_standard_deviation=4,
	shipment_lead_time=[8, 3],
	inventory_policy_type=InventoryPolicyType.BASE_STOCK,
	local_base_stock_levels=[171.1912, 57.7257],
	initial_IL=20,
	initial_orders=20,
	initial_shipments=20,
	downstream_0=True
)

