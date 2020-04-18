from pyinv.ssm_serial import *
#from pyinv.demand_source import *
from pyinv.supply_chain_network import *
from pyinv.sim import *
import copy

example_6_1_network_norm = serial_system(
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
example_6_1_network_norm.reindex_nodes({0: 1, 1: 2, 2: 3})

example_6_1_network_unif = serial_system(
    num_nodes=3,
    local_holding_cost=[7, 4, 2],
    echelon_holding_cost=[3, 2, 2],
    stockout_cost=[37.12, 0, 0],
    demand_type=DemandType.UNIFORM_CONTINUOUS,
    demand_lo=5-np.sqrt(12)/2,
    demand_hi=5+np.sqrt(12)/2,
    shipment_lead_time=[1, 1, 2],
    inventory_policy_type=InventoryPolicyType.BASE_STOCK,
    local_base_stock_levels=[6.49, 5.53, 10.69],
    downstream_0=True
)

example_6_1_network_unif.reindex_nodes({0: 1, 1: 2, 2: 3})

S_unif, C_unif = optimize_base_stock_levels(example_6_1_network_unif, x_num=100, d_num=10)
S_norm, C_norm = optimize_base_stock_levels(example_6_1_network_norm)

C_calc_unif = expected_cost(example_6_1_network_unif, S_unif)
C_calc_norm = expected_cost(example_6_1_network_norm, S_norm)

print("S_unif={:} C_unif={:12.2f} C_calc_unif={:12.2f}".format(S_unif, C_unif, C_calc_unif))
print("S_norm={:} C_norm={:12.2f} C_calc_unif={:12.2f}".format(S_norm, C_norm, C_calc_norm))

S_unif_local = echelon_to_local_base_stock_levels(example_6_1_network_unif, S_unif)
for n in example_6_1_network_unif.nodes:
    n.inventory_policy.base_stock_level = S_unif_local[n.index]

S_norm_local = echelon_to_local_base_stock_levels(example_6_1_network_norm, S_norm)
for n in example_6_1_network_norm.nodes:
    n.inventory_policy.base_stock_level = S_norm_local[n.index]

T = 1000

total_cost_unif = simulation(example_6_1_network_unif, T, rand_seed=None, progress_bar=True)
total_cost_norm = simulation(example_6_1_network_norm, T, rand_seed=None, progress_bar=True)

print("simulated cost unif = {:12.2f}".format(total_cost_unif / T))
print("simulated cost norm = {:12.2f}".format(total_cost_norm / T))